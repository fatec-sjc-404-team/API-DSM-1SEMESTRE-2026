from pathlib import Path

import pandas as pd

from Tratamento_Dados.csv_pipeline import filtrar_arquivos_csv

PASTA_DADOS = Path(__file__).parent

# Todos os CSVs mensais colocados nesta pasta entram no primeiro recorte.
PASTA_ENTRADA = PASTA_DADOS / "entrada"
ARQUIVO_SAIDA = PASTA_DADOS / "saida" / "scrdata_norte_nordeste.csv"

# Siglas das UFs mantidas no primeiro recorte.
ESTADOS_NORTE_NORDESTE = frozenset(
    {
        "AC",
        "AL",
        "AP",
        "AM",
        "BA",
        "CE",
        "MA",
        "PA",
        "PB",
        "PE",
        "PI",
        "RN",
        "RO",
        "RR",
        "SE",
        "TO",
    }
)


def filtrar_norte_nordeste(dados: pd.DataFrame) -> pd.DataFrame:
    """Mantém todas as colunas e apenas registros com UF do Norte ou Nordeste."""
    if "uf" not in dados.columns:
        raise ValueError("O CSV precisa conter uma coluna chamada 'uf'.")

    # Normaliza espaços e caixa para aceitar siglas como " ac " e "Ac".
    uf = dados["uf"].astype("string").str.strip().str.upper()
    return dados.loc[uf.isin(ESTADOS_NORTE_NORDESTE)].copy()


def main() -> None:
    arquivos_entrada = sorted(PASTA_ENTRADA.glob("*.csv"))
    if not arquivos_entrada:
        raise FileNotFoundError(
            f"Nenhum CSV encontrado em {PASTA_ENTRADA}. "
            "Coloque os arquivos mensais nessa pasta."
        )

    # Processa os arquivos em lotes e grava uma saída combinada.
    total_linhas = filtrar_arquivos_csv(
        arquivos_entrada, ARQUIVO_SAIDA, filtrar_norte_nordeste
    )
    print(
        f"{len(arquivos_entrada)} arquivos processados; "
        f"{total_linhas} linhas salvas em: {ARQUIVO_SAIDA}"
    )


if __name__ == "__main__":
    main()
