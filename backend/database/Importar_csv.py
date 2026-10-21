import csv
import getpass
import re
from datetime import date
from decimal import Decimal
from pathlib import Path

BATCH_SIZE = 500
ARQUIVO_CSV = (
    Path(__file__).resolve().parents[1]
    / "Tratamento_Dados"
    / "saida"
    / "scrdata_norte_nordeste_pessoa_fisica_baixa_renda.csv"
)
PREFIXOS_DECIMAIS = ("a_vencer_", "carteira_", "vencido_", "ativo_")


def converter_linha(
    linha: dict[str, str | None],
    colunas: list[str],
    colunas_decimais: set[str],
) -> tuple[date | Decimal | int | str, ...]:
    valores = []

    for coluna in colunas:
        valor = linha[coluna]
        if valor is None:
            raise ValueError(f"Valor ausente na coluna '{coluna}'.")

        valor = valor.strip()
        if coluna == "data_base":
            valores.append(date.fromisoformat(valor))
        elif coluna == "numero_de_operacoes":
            valores.append(int(valor))
        elif coluna in colunas_decimais:
            valores.append(Decimal(valor.replace(",", ".")))
        else:
            valores.append(valor)

    return tuple(valores)


def importar_csv(conexao, arquivo_csv: Path = ARQUIVO_CSV) -> int:
    with arquivo_csv.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")
        colunas = leitor.fieldnames

        if not colunas or "id" in colunas or len(set(colunas)) != len(colunas):
            raise ValueError("Cabeçalho do CSV inválido.")
        if any(
            re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", coluna) is None
            for coluna in colunas
        ):
            raise ValueError("O CSV contém um nome de coluna inválido.")

        colunas_sql = ", ".join(f"`{coluna}`" for coluna in colunas)
        marcadores = ", ".join(["%s"] * len(colunas))
        comando = f"INSERT INTO BCB ({colunas_sql}) VALUES ({marcadores})"
        colunas_decimais = {
            coluna for coluna in colunas if coluna.startswith(PREFIXOS_DECIMAIS)
        }
        total = 0
        lote = []

        try:
            with conexao.cursor() as cursor:
                cursor.execute("DELETE FROM BCB")

                for linha in leitor:
                    lote.append(converter_linha(linha, colunas, colunas_decimais))

                    if len(lote) == BATCH_SIZE:
                        cursor.executemany(comando, lote)
                        total += len(lote)
                        print(f"{total:,} linhas processadas")
                        lote.clear()

                if lote:
                    cursor.executemany(comando, lote)
                    total += len(lote)

            conexao.commit()
        except Exception:
            conexao.rollback()
            raise

    return total


def main() -> None:
    import pymysql

    usuario = input("Usuário do MySQL: ")
    senha = getpass.getpass("Senha do MySQL: ")
    conexao = pymysql.connect(
        host="localhost",
        user=usuario,
        password=senha,
        database="AvoCredit",
        charset="utf8mb4",
        autocommit=False,
    )

    try:
        total = importar_csv(conexao)
        print(f"Importação concluída: {total:,} linhas inseridas.")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()
