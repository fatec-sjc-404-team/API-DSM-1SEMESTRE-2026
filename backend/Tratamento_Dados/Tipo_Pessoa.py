from pathlib import Path

import pandas as pd

PASTA_DADOS = Path(__file__).parent

#Aqui são os caminhos dos para as bases de dados

#Ele esta pegando o resultado do tratamento anterior
ARQUIVO_ENTRADA = PASTA_DADOS / "saida" / "scrdata_202601_norte_nordeste.csv"

#E gerando o novo resultado
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

# Teste manual
#
# Para conferir se o código está funcionando, abra o terminal na pasta backend
# e execute:
# .\.venv\Scripts\python.exe -c "import pandas as pd; df=pd.read_csv('Tratamento_Dados/saida/scrdata_202601_norte_nordeste_pessoa_fisica.csv', sep=';'); clientes=df['cliente'].astype('string').str.strip().str.upper(); print('Linhas:', len(df)); print('Colunas:', len(df.columns)); print('Todas as linhas são de pessoas físicas:', clientes.eq('PF').all())"
#
# Resultado esperado:
# Linhas: 89029
# Colunas: 24
# Todas as linhas são de pessoas físicas: True
#
# O resultado será salvo em Tratamento_Dados/saida/.
