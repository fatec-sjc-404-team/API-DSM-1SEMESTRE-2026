import argparse
import logging
import os
from datetime import date

from database.Importar_csv import importar_csv
from Tratamento_Dados.atualizacao_semanal import (
    BACKUP,
    atualizar_fonte,
    hoje_e_dia_da_atualizacao,
    montar_fontes,
    rodar_modulo,
)

# Logger próprio deste arquivo (o Ruff exige isso)
logger = logging.getLogger(__name__)

# Ordem do pipeline de tratamento
ETAPAS_TRATAMENTO = [
    "Tratamento_Dados.Estados",
    "Tratamento_Dados.Tipo_Pessoa",
    "Tratamento_Dados.Renda",
]


def importar_no_banco():
    """Importa o CSV tratado para o MySQL.

    O importar_csv já apaga os dados antigos e, se der erro no meio,
    desfaz tudo (rollback). Então o banco nunca fica pela metade.
    """
    import pymysql

    # Usuário e senha vêm de variáveis de ambiente (nunca escrever no código)
    usuario = os.getenv("DB_USER")
    senha = os.getenv("DB_PASSWORD")
    if not usuario or senha is None:
        raise RuntimeError("Defina as variáveis de ambiente DB_USER e DB_PASSWORD.")

    conexao = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=usuario,
        password=senha,
        database="AvoCredit",
        charset="utf8mb4",
        autocommit=False,
    )
    try:
        return importar_csv(conexao)
    finally:
        conexao.close()


def automatizar(forcar=False, hoje=None, pasta_backup=BACKUP):
    """Roda tudo na ordem. Retorna True só se o processo inteiro deu certo."""
    if not forcar and not hoje_e_dia_da_atualizacao(hoje):
        logger.info("Hoje não é o dia da atualização.")
        return False
    ano = (hoje or date.today()).year

    # 1) Coleta: se falhar, o backup já foi restaurado e o banco não é tocado
    for nome, fonte in montar_fontes(ano).items():
        if not atualizar_fonte(nome, fonte, pasta_backup):
            logger.error("Coleta falhou. Banco mantido com os dados anteriores.")
            return False

    # 2) Tratamento: qualquer erro para tudo antes de chegar no banco
    for modulo in ETAPAS_TRATAMENTO:
        try:
            rodar_modulo(modulo)
        except Exception as erro:  # noqa: BLE001 (nunca pode travar)
            logger.error("Falha em %s: %s. Banco não foi alterado.", modulo, erro)
            return False

    # 3) Importação: sobrescreve os dados do banco com os novos
    try:
        total = importar_no_banco()
    except Exception as erro:  # noqa: BLE001 (nunca pode travar)
        logger.error("Falha na importação: %s. Banco mantido como estava.", erro)
        return False

    logger.info("Processo completo concluído: %s linhas importadas.", total)
    return True


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    parser = argparse.ArgumentParser(
        description="Automatiza coleta, tratamento e importação"
    )
    parser.add_argument(
        "--forcar", action="store_true", help="roda mesmo fora do dia fixo"
    )
    args = parser.parse_args()
    automatizar(forcar=args.forcar)


if __name__ == "__main__":
    main()
