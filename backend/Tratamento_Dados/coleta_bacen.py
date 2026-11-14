from datetime import date, timedelta

import requests

from Tratamento_Dados.salvar_dados import PASTA_SAIDA, salvar_csv

# API do SGS (Sistema Gerenciador de Séries Temporais) do Banco Central.
URL_SGS = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"

# Séries mensais de inadimplência de pessoa física (código SGS: nome no CSV).
SERIES = {
    21084: "inadimplencia_pf_total",
    21114: "inadimplencia_pf_credito_pessoal_nao_consignado",
}

ANO_INICIAL = 2012  # mesmo início dos dados do SCR.data (BCB)
JANELA_ANOS = 9  # a API recusa consultas de mais de 10 anos
TIMEOUT = (10, 60)  # (conexão, leitura) em segundos

COLUNAS = ["data_base", "codigo_serie", "serie", "valor_percentual"]
ARQUIVO_SAIDA = PASTA_SAIDA / "bacen_inadimplencia_pf.csv"


def gerar_janelas(inicio: date, fim: date) -> list[tuple[date, date]]:
    """Divide o período em janelas que a API aceita (sem passar de 10 anos)."""
    janelas = []
    while inicio <= fim:
        fim_janela = min(date(inicio.year + JANELA_ANOS, 12, 31), fim)
        janelas.append((inicio, fim_janela))
        inicio = fim_janela + timedelta(days=1)
    return janelas


def baixar_serie(codigo: int, inicio: date, fim: date) -> list[dict[str, str]]:
    """Baixa uma série do SGS, janela por janela, e junta os registros."""
    registros: list[dict[str, str]] = []

    for ini, fi in gerar_janelas(inicio, fim):
        resposta = requests.get(
            URL_SGS.format(codigo=codigo),
            params={
                "formato": "json",
                "dataInicial": ini.strftime("%d/%m/%Y"),
                "dataFinal": fi.strftime("%d/%m/%Y"),
            },
            timeout=TIMEOUT,
        )
        resposta.raise_for_status()

        dados = resposta.json()
        if not isinstance(dados, list):
            raise TypeError(f"Resposta inesperada do BACEN na série {codigo}.")
        registros.extend(dados)

    return registros


def converter(
    codigo: int, nome: str, registros: list[dict[str, str]]
) -> list[dict[str, str]]:
    """Converte para o padrão do projeto: data ISO (aaaa-mm-dd) e decimal com vírgula."""
    linhas = []
    for item in registros:
        if not item["valor"]:
            continue
        dia, mes, ano = item["data"].split("/")
        linhas.append(
            {
                "data_base": f"{ano}-{mes}-{dia}",
                "codigo_serie": str(codigo),
                "serie": nome,
                "valor_percentual": item["valor"].replace(".", ","),
            }
        )
    return linhas


def coletar_bacen(fim: date | None = None) -> list[dict[str, str]]:
    """Coleta todas as séries e retorna as linhas prontas para salvar."""
    fim = fim or date.today()
    linhas: list[dict[str, str]] = []

    for codigo, nome in SERIES.items():
        registros = baixar_serie(codigo, date(ANO_INICIAL, 1, 1), fim)
        if not registros:
            raise ValueError(f"A série {codigo} voltou vazia.")
        linhas.extend(converter(codigo, nome, registros))

    return linhas


def main() -> None:
    try:
        print("Coletando séries de inadimplência no BACEN ...")
        linhas = coletar_bacen()
        total = salvar_csv(linhas, COLUNAS, ARQUIVO_SAIDA)
    except (requests.RequestException, ValueError, TypeError) as erro:
        print(f"Erro: {erro}")
        return

    print(f"{total} linhas salvas em {ARQUIVO_SAIDA}")
    # Para conferir: compare estes valores com o site do BCB.
    for codigo, nome in SERIES.items():
        ultima = [linha for linha in linhas if linha["codigo_serie"] == str(codigo)][-1]
        print(f"  {nome}: {ultima['data_base']} = {ultima['valor_percentual']}%")


if __name__ == "__main__":
    main()
