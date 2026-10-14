from pathlib import Path

import pandas as pd

PASTA_DADOS = Path(__file__).parent

# Define o caminho do arquivo que será tratado.
# Coloque o CSV na pasta entrada; o caminho pode ser ajustado, se necessário.
ARQUIVO_ENTRADA = PASTA_DADOS / "entrada" / "scrdata_202601.csv"

# Estados que pertencem às regiões Norte e Nordeste.
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

    uf = dados["uf"].astype("string").str.strip().str.upper()
    return dados.loc[uf.isin(ESTADOS_NORTE_NORDESTE)].copy()


def main() -> None:
    if not ARQUIVO_ENTRADA.is_file():
        raise FileNotFoundError(
            f"CSV não encontrado: {ARQUIVO_ENTRADA}. "
            "Coloque scrdata_202601.csv na pasta Tratamento_Dados/entrada/."
        )

    arquivo_saida = PASTA_DADOS / "saida" / f"{ARQUIVO_ENTRADA.stem}_norte_nordeste.csv"
    dados = pd.read_csv(ARQUIVO_ENTRADA, sep=";")
    filtrados = filtrar_norte_nordeste(dados)

    arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
    filtrados.to_csv(arquivo_saida, sep=";", index=False)
    print(f"{len(filtrados)} linhas salvas em: {arquivo_saida}")


if __name__ == "__main__":
    main()
