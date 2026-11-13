import shutil  # copiar dados de um arquivo para outro (usado na extração)
import zipfile  # abrir e ler arquivos .zip
from pathlib import Path  # trabalhar com caminhos de pastas/arquivos

import requests  # fazer a requisição HTTP para baixar o arquivo

# URL do BCB com um "buraco" {ano} que será preenchido depois.
URL_BASE = "https://www.bcb.gov.br/pda/desig/scrdata_{ano}.zip"

# Pasta onde tudo será salvo: backend/Tratamento_Dados/entrada
# __file__ é este arquivo; .parent é a pasta dele (Tratamento_Dados).
PASTA_ENTRADA = Path(__file__).parent / "entrada"

# O ZIP é baixado em pedaços de 1 MB, para não carregar o arquivo
# inteiro na memória
TAMANHO_BLOCO = 1024 * 1024

# Tempo máximo de espera, em segundos: (para conectar, para receber dados).
TIMEOUT = (10, 120)


def validar_ano(ano: int | str) -> str:
    """Retorna o ano como texto de 4 dígitos ou levanta ValueError."""
    # str() aceita tanto 2026 (número) quanto "2026" (texto);
    # strip() remove espaços sobrando, como em " 2026 ".
    ano_texto = str(ano).strip()

    # Só aceitamos exatamente 4 dígitos. Isso também impede que alguém
    # digite algo estranho (como "../x") e bagunce a URL.
    if not (ano_texto.isdigit() and len(ano_texto) == 4):
        raise ValueError("Ano inválido. Use 4 dígitos, por exemplo 2026.")
    return ano_texto


def montar_url(ano: int | str) -> str:
    """Monta a URL do ZIP do BCB para o ano informado."""
    # Troca o {ano} da URL_BASE pelo ano já validado.
    return URL_BASE.format(ano=validar_ano(ano))


def baixar_zip(ano: int | str, pasta_destino: Path = PASTA_ENTRADA) -> Path:
    """Baixa o ZIP do BCB do ano informado e retorna o caminho do arquivo salvo."""
    ano_texto = validar_ano(ano)
    url = montar_url(ano_texto)

    # (parents=True cria as pastas "pai" também; exist_ok=True não dá
    # erro se a pasta já existir).
    pasta_destino.mkdir(parents=True, exist_ok=True)

    # Caminho final do ZIP. Ex: .../entrada/scrdata_2026.zip
    arquivo_zip = pasta_destino / f"scrdata_{ano_texto}.zip"

    # Baixamos primeiro para um arquivo temporário (começa com ponto e
    # termina com .tmp). Assim, se a conexão cair no meio, não fica um
    # ZIP pela metade com cara de arquivo completo.
    arquivo_temporario = arquivo_zip.with_name(f".{arquivo_zip.name}.tmp")

    try:
        # stream=True: baixa aos poucos, e não tudo de uma vez.
        with requests.get(
            url,
            stream=True,
            timeout=TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0"},
        ) as resposta:
            # 404 = "não encontrado": o BCB não tem arquivo desse ano.
            if resposta.status_code == 404:
                raise FileNotFoundError(
                    f"O BCB não tem arquivo para o ano {ano_texto}."
                )

            resposta.raise_for_status()

            # Grava no arquivo temporário, um bloco de 1 MB por vez.
            # "wb" = escrever em modo binário (ZIP não é texto).
            with arquivo_temporario.open("wb") as destino:
                for bloco in resposta.iter_content(chunk_size=TAMANHO_BLOCO):
                    destino.write(bloco)

        # Download completo: troca o nome do temporário pelo nome final.
        arquivo_temporario.replace(arquivo_zip)
    finally:
        # Roda sempre, com erro ou sem erro. Se o temporário ainda
        # existir (porque algo falhou), ele é apagado.
        # missing_ok=True evita erro quando ele já foi renomeado acima.
        arquivo_temporario.unlink(missing_ok=True)

    return arquivo_zip


def extrair_csvs(arquivo_zip: Path, pasta_destino: Path = PASTA_ENTRADA) -> list[Path]:
    """Extrai só os CSVs do ZIP para a pasta de destino e retorna os caminhos."""
    pasta_destino.mkdir(parents=True, exist_ok=True)

    # Lista onde guardamos o caminho de cada CSV extraído.
    extraidos: list[Path] = []

    with zipfile.ZipFile(arquivo_zip) as pacote:
        # infolist() devolve a lista de tudo que existe dentro do ZIP.
        for membro in pacote.infolist():
            # Pegamos só o NOME do arquivo, descartando pastas internas.
            # Isso evita que um ZIP malicioso escreva fora da pasta de
            # destino (ex: um item chamado "../../algo.csv").
            nome = Path(membro.filename).name

            # Pula pastas e qualquer arquivo que não seja .csv
            if membro.is_dir() or not nome.lower().endswith(".csv"):
                continue

            destino = pasta_destino / nome

            # Abre o item dentro do ZIP e o arquivo de destino, e copia o
            # conteúdo aos poucos
            with pacote.open(membro) as origem, destino.open("wb") as saida:
                shutil.copyfileobj(origem, saida)

            extraidos.append(destino)

    # Se o ZIP não tinha nenhum CSV, avisamos
    if not extraidos:
        raise ValueError(f"O ZIP {arquivo_zip.name} não contém arquivos CSV.")

    # Devolve a lista em ordem de mes
    return sorted(extraidos)


def main() -> None:
    """Pergunta o ano, baixa o ZIP, extrai os CSVs e mostra o resultado."""
    ano = input("Digite o ano que deseja baixar (ex: 2026): ")

    # try/except: tenta executar e, se algo der errado, mostra uma mensagem
    try:
        print(f"Baixando {montar_url(ano)} ...")
        arquivo_zip = baixar_zip(ano)
        csvs = extrair_csvs(arquivo_zip)
    except (ValueError, FileNotFoundError, zipfile.BadZipFile) as erro:
        # ValueError: ano inválido, ou ZIP sem CSVs.
        # FileNotFoundError: o BCB não tem esse ano.
        # BadZipFile: o arquivo baixado não é um ZIP válido.
        print(f"Erro: {erro}")
        return
    except requests.RequestException as erro:
        # Qualquer problema de rede: sem internet, timeout, erro do site...
        print(f"Erro de conexão ao baixar: {erro}")
        return

    arquivo_zip.unlink()

    # Mostra o que foi salvo: nome e tamanho (em MB) de cada CSV.
    print(f"{len(csvs)} CSVs salvos em {PASTA_ENTRADA}:")
    for csv in csvs:
        print(f"  - {csv.name} ({csv.stat().st_size / 1_048_576:.1f} MB)")


if __name__ == "__main__":
    main()
