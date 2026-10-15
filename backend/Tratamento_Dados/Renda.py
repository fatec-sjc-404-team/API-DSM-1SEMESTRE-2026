from pathlib import Path

import pandas as pd
from Tratamento_Dados.csv_pipeline import filtrar_arquivos_csv

PASTA_DADOS = Path(__file__).parent
# Continua a partir da saída que já contém somente clientes PF.
ARQUIVO_ENTRADA = PASTA_DADOS / "saida" / "scrdata_norte_nordeste_pessoa_fisica.csv"
ARQUIVO_SAIDA = (
    PASTA_DADOS / "saida" / "scrdata_norte_nordeste_pessoa_fisica_baixa_renda.csv"
)

# As categorias são comparadas sem diferenciar maiúsculas/minúsculas.
FAIXAS_BAIXA_RENDA = frozenset(
    {
        "sem rendimento",
        "até 1 salário mínimo",
        "mais de 1 a 2 salários mínimos",
    }
)


def filtrar_baixa_renda(dados: pd.DataFrame) -> pd.DataFrame:
    """Mantém todas as colunas e as três faixas de baixa renda definidas."""
    if "porte" not in dados.columns:
        raise ValueError("O CSV precisa conter uma coluna chamada 'porte'.")

    # strip/casefold toleram diferenças de espaços e capitalização no CSV.
    porte = dados["porte"].astype("string").str.strip().str.casefold()
    return dados.loc[porte.isin(FAIXAS_BAIXA_RENDA)].copy()


def main() -> None:
    if not ARQUIVO_ENTRADA.is_file():
        raise FileNotFoundError(
            f"Arquivo da etapa anterior não encontrado: {ARQUIVO_ENTRADA}. "
            "Execute Estados.py e Tipo_Pessoa.py primeiro."
        )

    # Cada etapa escreve um novo resultado e deixa sua entrada preservada.
    total_linhas = filtrar_arquivos_csv(
        [ARQUIVO_ENTRADA], ARQUIVO_SAIDA, filtrar_baixa_renda
    )
    print(f"{total_linhas} linhas salvas em: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
