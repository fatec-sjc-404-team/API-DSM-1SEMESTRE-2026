from pathlib import Path

import pandas as pd

PASTA_DADOS = Path(__file__).parent

# Aqui são os caminhos dos para as bases de dados

# Ele esta pegando o resultado do tratamento anterior
ARQUIVO_ENTRADA = PASTA_DADOS / "saida" / "scrdata_202601_norte_nordeste.csv"

# E gerando o novo resultado
ARQUIVO_SAIDA = (
    PASTA_DADOS / "saida" / "scrdata_202601_norte_nordeste_pessoa_fisica.csv"
)


def filtrar_pessoas_fisicas(dados: pd.DataFrame) -> pd.DataFrame:
    """Mantém todas as colunas e apenas clientes classificados como PF."""
    if "cliente" not in dados.columns:
        raise ValueError("O CSV precisa conter uma coluna chamada 'cliente'.")

    cliente = dados["cliente"].astype("string").str.strip().str.upper()
    return dados.loc[cliente == "PF"].copy()


def main() -> None:
    if not ARQUIVO_ENTRADA.is_file():
        raise FileNotFoundError(
            f"Arquivo da etapa anterior não encontrado: {ARQUIVO_ENTRADA}. "
            "Execute primeiro Estados.py."
        )

    dados = pd.read_csv(ARQUIVO_ENTRADA, sep=";")
    filtrados = filtrar_pessoas_fisicas(dados)

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    filtrados.to_csv(ARQUIVO_SAIDA, sep=";", index=False)
    print(f"{len(filtrados)} linhas salvas em: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
