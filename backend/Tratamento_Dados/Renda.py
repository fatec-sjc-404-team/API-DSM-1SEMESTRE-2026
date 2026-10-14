from pathlib import Path

import pandas as pd

PASTA_DADOS = Path(__file__).parent
ARQUIVO_ENTRADA = (
    PASTA_DADOS / "saida" / "scrdata_202601_norte_nordeste_pessoa_fisica.csv"
)
ARQUIVO_SAIDA = (
    PASTA_DADOS
    / "saida"
    / "scrdata_202601_norte_nordeste_pessoa_fisica_baixa_renda.csv"
)

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

    porte = dados["porte"].astype("string").str.strip().str.casefold()
    return dados.loc[porte.isin(FAIXAS_BAIXA_RENDA)].copy()


def main() -> None:
    if not ARQUIVO_ENTRADA.is_file():
        raise FileNotFoundError(
            f"Arquivo da etapa anterior não encontrado: {ARQUIVO_ENTRADA}. "
            "Execute Estados.py e Tipo_Pessoa.py primeiro."
        )

    dados = pd.read_csv(ARQUIVO_ENTRADA, sep=";")
    filtrados = filtrar_baixa_renda(dados)

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    filtrados.to_csv(ARQUIVO_SAIDA, sep=";", index=False)
    print(f"{len(filtrados)} linhas salvas em: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
