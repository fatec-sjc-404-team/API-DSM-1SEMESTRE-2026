from pathlib import Path

import pandas as pd
from Tratamento_Dados.csv_pipeline import filtrar_arquivos_csv

PASTA_DADOS = Path(__file__).parent

ARQUIVO_ENTRADA = PASTA_DADOS / "saida" / "scrdata_norte_nordeste.csv"

# Gera outro arquivo para preservar a saída da etapa anterior.
ARQUIVO_SAIDA = PASTA_DADOS / "saida" / "scrdata_norte_nordeste_pessoa_fisica.csv"


def filtrar_pessoas_fisicas(dados: pd.DataFrame) -> pd.DataFrame:
    """Mantém todas as colunas e apenas clientes classificados como PF."""
    if "cliente" not in dados.columns:
        raise ValueError("O CSV precisa conter uma coluna chamada 'cliente'.")

    # Normaliza espaços e caixa antes de comparar com a sigla PF.
    cliente = dados["cliente"].astype("string").str.strip().str.upper()
    return dados.loc[cliente == "PF"].copy()


def main() -> None:
    if not ARQUIVO_ENTRADA.is_file():
        raise FileNotFoundError(
            f"Arquivo da etapa anterior não encontrado: {ARQUIVO_ENTRADA}. "
            "Execute primeiro Estados.py."
        )

    total_linhas = filtrar_arquivos_csv(
        [ARQUIVO_ENTRADA], ARQUIVO_SAIDA, filtrar_pessoas_fisicas
    )
    print(f"{total_linhas} linhas salvas em: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
