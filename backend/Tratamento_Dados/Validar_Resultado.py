from pathlib import Path

import pandas as pd
from Estados import ESTADOS_NORTE_NORDESTE
from Renda import FAIXAS_BAIXA_RENDA

PASTA_DADOS = Path(__file__).parent
ARQUIVOS_ETAPAS = (
    (
        "Etapa 1 - Região Norte e Nordeste",
        PASTA_DADOS / "saida" / "scrdata_202601_norte_nordeste.csv",
        False,
        False,
    ),
    (
        "Etapa 2 - Pessoas físicas",
        PASTA_DADOS / "saida" / "scrdata_202601_norte_nordeste_pessoa_fisica.csv",
        True,
        False,
    ),
    (
        "Etapa 3 - Faixas de baixa renda",
        PASTA_DADOS
        / "saida"
        / "scrdata_202601_norte_nordeste_pessoa_fisica_baixa_renda.csv",
        True,
        True,
    ),
)


def validar_etapa(
    nome: str,
    caminho: Path,
    validar_pessoa: bool,
    validar_renda: bool,
) -> bool:
    if not caminho.is_file():
        raise FileNotFoundError(
            f"Resultado da etapa não encontrado: {caminho}. "
            "Execute as etapas de tratamento na ordem indicada no README."
        )

    dados = pd.read_csv(caminho, sep=";")
    colunas_necessarias = {"uf"}
    if validar_pessoa:
        colunas_necessarias.add("cliente")
    if validar_renda:
        colunas_necessarias.add("porte")

    colunas_ausentes = colunas_necessarias.difference(dados.columns)
    if colunas_ausentes:
        raise ValueError(
            f"Colunas necessárias ausentes em {caminho}: {sorted(colunas_ausentes)}"
        )

    uf = dados["uf"].astype("string").str.strip().str.upper()
    ufs_validas = not dados.empty and uf.isin(ESTADOS_NORTE_NORDESTE).all()

    resultados = [ufs_validas]
    print(f"\n{nome}")
    print(f"Arquivo: {caminho}")
    print(f"Linhas: {len(dados)}")
    print(f"Colunas: {len(dados.columns)}")
    print(f"Todas as UFs são do Norte/Nordeste: {'OK' if ufs_validas else 'FALHOU'}")

    if validar_pessoa:
        cliente = dados["cliente"].astype("string").str.strip().str.upper()
        clientes_pf = not dados.empty and cliente.eq("PF").all()
        resultados.append(clientes_pf)
        print(
            f"Todas as linhas são de pessoas físicas: "
            f"{'OK' if clientes_pf else 'FALHOU'}"
        )

    if validar_renda:
        porte = dados["porte"].astype("string").str.strip().str.casefold()
        rendas_validas = not dados.empty and porte.isin(FAIXAS_BAIXA_RENDA).all()
        resultados.append(rendas_validas)
        print(
            f"Todas as faixas de renda são permitidas: "
            f"{'OK' if rendas_validas else 'FALHOU'}"
        )

    return all(resultados)


def main() -> None:
    etapas_validas = [
        validar_etapa(nome, caminho, validar_pessoa, validar_renda)
        for nome, caminho, validar_pessoa, validar_renda in ARQUIVOS_ETAPAS
    ]

    if not all(etapas_validas):
        raise SystemExit("\nUma ou mais etapas não passaram nas verificações.")

    print("\nTodas as etapas passaram nas verificações.")


if __name__ == "__main__":
    main()
