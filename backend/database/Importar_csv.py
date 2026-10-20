import csv
import getpass
from datetime import date
from decimal import Decimal
from pathlib import Path

import pymysql


arquivo_csv = Path(
    "Tratamento_Dados/saida/"
    "scrdata_norte_nordeste_pessoa_fisica_baixa_renda.csv"
)

usuario = input("Usuário do MySQL: ")
senha = getpass.getpass("Senha do MySQL: ")

conexao = pymysql.connect(
    host="localhost",
    user=usuario,
    password=senha,
    database="AvoCredit",
    charset="utf8mb4",
)

try:
    with arquivo_csv.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")
        colunas = leitor.fieldnames

        if not colunas or "id" in colunas:
            raise ValueError("Cabeçalho do CSV inválido.")

        colunas_sql = ", ".join(f"`{coluna}`" for coluna in colunas)
        marcadores = ", ".join(["%s"] * len(colunas))
        comando = f"INSERT INTO BCB ({colunas_sql}) VALUES ({marcadores})"

        colunas_decimais = {
            coluna
            for coluna in colunas
            if coluna.startswith(
                ("a_vencer_", "carteira_", "vencido_", "ativo_")
            )
        }

        lote = []
        total = 0

        with conexao.cursor() as cursor:
            for linha in leitor:
                valores = []

                for coluna in colunas:
                    valor = linha[coluna].strip()

                    if coluna == "data_base":
                        valores.append(date.fromisoformat(valor))
                    elif coluna == "numero_de_operacoes":
                        valores.append(int(valor))
                    elif coluna in colunas_decimais:
                        valores.append(Decimal(valor.replace(",", ".")))
                    else:
                        valores.append(valor)

                lote.append(tuple(valores))

                if len(lote) == 500:
                    cursor.executemany(comando, lote)
                    conexao.commit()
                    total += len(lote)
                    print(f"{total:,} linhas importadas")
                    lote.clear()

            if lote:
                cursor.executemany(comando, lote)
                conexao.commit()
                total += len(lote)

    print(f"Importação concluída: {total:,} linhas inseridas.")

finally:
    conexao.close()