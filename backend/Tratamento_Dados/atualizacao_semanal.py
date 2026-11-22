"""Atualização semanal dos dados do BCB (FC404-112).

Baixa os CSVs, roda as etapas do tratamento, confere o resultado e, se houver
MySQL configurado (DB_USER), importa para a tabela BCB. Se qualquer passo
falhar, o site continua com os dados da semana anterior.
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# dia fixo da atualização (0 = segunda ... 6 = domingo)
DIA_ATUALIZACAO = 0
NOMES_DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
# Se a atualização do dia fixo falhar ou for perdida, tenta de novo nos dias
# seguintes até passar.
DIAS_ENTRE_ATUALIZACOES = 7

# Pastas do projeto (entrada e saida são ignoradas pelo Git)
PASTA_TRATAMENTO = Path(__file__).resolve().parent
PASTA_BACKEND = PASTA_TRATAMENTO.parent
ENTRADA = PASTA_TRATAMENTO / "entrada"
SAIDA = PASTA_TRATAMENTO / "saida"
# CSV final que o site lê (quando não há MySQL) e que é importado no MySQL
ARQUIVO_FINAL = SAIDA / "scrdata_norte_nordeste_pessoa_fisica_baixa_renda.csv"
# Cópia dos dados da semana anterior (fica dentro de saida, não vai para o Git)
BACKUP = SAIDA / "backup_semana_anterior"
# Data e hora da última atualização que deu certo (mostrada no site)
MARCADOR = SAIDA / "ultima_atualizacao.txt"

MODULO_COLETA = "Tratamento_Dados.coleta_bcb"
# Mesmo código de coleta_bcb.SAIDA_ANO_SEM_ARQUIVO (o BCB não tem o ano)
CODIGO_ANO_SEM_ARQUIVO = 2
# Etapas do tratamento, na ordem do README
ETAPAS_TRATAMENTO = [
    "Tratamento_Dados.Estados",
    "Tratamento_Dados.Tipo_Pessoa",
    "Tratamento_Dados.Renda",
    "Tratamento_Dados.Validar_Resultado",
]
MODULO_IMPORTACAO = "database.Importar_csv"


def rodar_modulo(modulo, argumentos=()):
    """Roda um módulo como se fosse na mão (python3 -m ...)."""
    subprocess.run(
        [sys.executable, "-m", modulo, *argumentos],
        cwd=PASTA_BACKEND,  # precisa rodar de dentro de backend/
        stdin=subprocess.DEVNULL,  # nada pode ficar esperando alguém digitar
        check=True,  # erro no módulo vira exceção
        timeout=3600,  # não fica preso se a fonte ou o banco travarem
    )


def coletar_bcb(ano):
    """Baixa o ano atual; se o BCB ainda não publicou (janeiro), baixa o anterior."""
    try:
        rodar_modulo(MODULO_COLETA, ["--ano", str(ano)])
    except subprocess.CalledProcessError as erro:
        if erro.returncode != CODIGO_ANO_SEM_ARQUIVO:
            raise
        logger.warning("O BCB ainda não tem %s; baixando %s.", ano, ano - 1)
        rodar_modulo(MODULO_COLETA, ["--ano", str(ano - 1)])


def atualizar_bcb(ano):
    """Coleta, trata, valida e importa os dados do BCB."""
    coletar_bcb(ano)
    for modulo in ETAPAS_TRATAMENTO:
        rodar_modulo(modulo)
    if os.environ.get("DB_USER"):
        rodar_modulo(MODULO_IMPORTACAO)
    else:
        logger.info("DB_USER não definido: o site vai ler o CSV tratado.")


def montar_fontes(ano):
    """Lista as fontes: como atualizar e quais arquivos guardar se der erro."""
    return {
        "bcb": {
            "atualizar": lambda: atualizar_bcb(ano),
            "dados": [ARQUIVO_FINAL],
        },
    }


def ler_ultima_atualizacao(marcador=MARCADOR):
    """Data e hora da última atualização que deu certo, ou None."""
    try:
        return datetime.fromisoformat(marcador.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def gravar_ultima_atualizacao(marcador=MARCADOR, agora=None):
    marcador.parent.mkdir(parents=True, exist_ok=True)
    agora = agora or datetime.now()
    marcador.write_text(agora.isoformat(timespec="seconds"), encoding="utf-8")


def deve_atualizar(hoje=None, ultima=None):
    """Diz se já é hora de atualizar.

    Atualiza no dia fixo, mas uma vez só por dia; se nunca atualizou ou se a
    última foi há uma semana ou mais (falha, servidor desligado), atualiza já.
    """
    hoje = hoje or date.today()
    if ultima is None:
        return True
    dias = (hoje - ultima).days
    if dias <= 0:
        return False
    return hoje.weekday() == DIA_ATUALIZACAO or dias >= DIAS_ENTRE_ATUALIZACOES


def guardar_backup(origem, backup):
    """Copia os dados atuais para a pasta de backup."""
    # Apaga o backup antigo para não misturar semanas
    if backup.is_dir():
        shutil.rmtree(backup)
    elif backup.exists():
        backup.unlink()
    backup.parent.mkdir(parents=True, exist_ok=True)
    # Copia pasta ou arquivo, se existir
    if origem.is_dir():
        shutil.copytree(origem, backup)
    elif origem.exists():
        shutil.copy2(origem, backup)


def restaurar_backup(origem, backup):
    """Volta os dados da semana anterior. Retorna False se não houver backup."""
    if not backup.exists():
        return False
    if origem.is_dir():
        shutil.rmtree(origem)
    if backup.is_dir():
        shutil.copytree(backup, origem)
    else:
        shutil.copy2(backup, origem)
    return True


def atualizar_fonte(nome, fonte, pasta_backup=BACKUP):
    """atualiza uma fonte; se falhar, mantém os dados anteriores."""
    backups = [(dados, pasta_backup / nome / dados.name) for dados in fonte["dados"]]
    for dados, backup in backups:
        guardar_backup(dados, backup)
    try:
        fonte["atualizar"]()
    except Exception as erro:  # qualquer falha não pode derrubar a aplicação  # noqa: BLE001
        logger.error("Falha na fonte %s: %s", nome, erro)
        restaurados = [restaurar_backup(dados, backup) for dados, backup in backups]
        if all(restaurados):
            logger.warning("Usando os dados da semana anterior (%s).", nome)
        else:
            logger.warning("Não há dados anteriores para %s.", nome)
        return False
    logger.info("Fonte %s atualizada.", nome)
    return True


def atualizar_tudo(forcar=False, hoje=None, pasta_backup=BACKUP, marcador=MARCADOR):
    """Atualiza todas as fontes. Retorna {nome_da_fonte: deu_certo}."""
    hoje = hoje or date.today()
    ultima = ler_ultima_atualizacao(marcador)
    if not forcar and not deve_atualizar(hoje, ultima and ultima.date()):
        logger.info(
            "Ainda não é hora de atualizar (dia fixo: %s; última: %s).",
            NOMES_DIAS[DIA_ATUALIZACAO],
            ultima,
        )
        return {}
    resultado = {}
    # Uma fonte com erro não impede as outras de rodarem
    for nome, fonte in montar_fontes(hoje.year).items():
        resultado[nome] = atualizar_fonte(nome, fonte, pasta_backup)
    # Só marca como atualizado se tudo deu certo; senão tenta de novo depois
    if resultado and all(resultado.values()):
        gravar_ultima_atualizacao(marcador)
    return resultado


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    parser = argparse.ArgumentParser(description="Atualização semanal dos dados")
    parser.add_argument(
        "--forcar", action="store_true", help="roda mesmo fora do dia fixo"
    )
    args = parser.parse_args()
    resultado = atualizar_tudo(forcar=args.forcar)
    logger.info("Resultado: %s", resultado)
    # Código 1 quando alguma fonte falhou, para cron/Docker perceberem
    return 0 if all(resultado.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
