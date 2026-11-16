"""Atualização semanal dos dados do BCB (FC404-112)."""

import argparse
import logging
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

# dia fixo da atualização (0 = segunda ... 6 = domingo)
DIA_ATUALIZACAO = 0
NOMES_DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]

# Pastas do projeto (entrada e saida são ignoradas pelo Git)
PASTA_TRATAMENTO = Path(__file__).resolve().parent
PASTA_BACKEND = PASTA_TRATAMENTO.parent
ENTRADA = PASTA_TRATAMENTO / "entrada"
SAIDA = PASTA_TRATAMENTO / "saida"
# Cópia dos dados da semana anterior (fica dentro de saida, não vai para o Git)
BACKUP = SAIDA / "backup_semana_anterior"


def montar_fontes(ano):
    """Lista as fontes: qual módulo roda e onde ficam os dados dela."""
    return {
        "bcb": {
            "modulo": "Tratamento_Dados.coleta_bcb",
            "dados": ENTRADA,
            # O coleta_bcb pergunta o ano com input(), então enviamos a resposta
            "entrada": f"{ano}\n",
        },
    }


def hoje_e_dia_da_atualizacao(hoje=None):
    """Diz se hoje é o dia fixo da atualização."""
    hoje = hoje or date.today()
    return hoje.weekday() == DIA_ATUALIZACAO


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


def rodar_modulo(modulo, entrada=None):
    """Roda um módulo da coleta como se fosse na mão (python3 -m ...)."""
    subprocess.run(
        [sys.executable, "-m", modulo],
        cwd=PASTA_BACKEND,  # precisa rodar de dentro de backend/
        input=entrada,
        text=True,
        check=True,  # erro no módulo vira exceção
        timeout=300,  # não fica preso se a fonte demorar demais
    )


def atualizar_fonte(nome, fonte, pasta_backup=BACKUP):
    """atualiza uma fonte; se falhar, mantém os dados anteriores."""
    backup = pasta_backup / nome
    guardar_backup(fonte["dados"], backup)
    try:
        rodar_modulo(fonte["modulo"], fonte.get("entrada"))
    except Exception as erro:  # qualquer falha não pode derrubar a aplicação  # noqa: BLE001
        logger.error("Falha na fonte %s: %s", nome, erro)
        if restaurar_backup(fonte["dados"], backup):
            logger.warning("Usando os dados da semana anterior (%s).", nome)
        else:
            logger.warning("Não há dados anteriores para %s.", nome)
        return False
    logger.info("Fonte %s atualizada.", nome)
    return True


def atualizar_tudo(forcar=False, hoje=None, pasta_backup=BACKUP):
    """Atualiza todas as fontes. Retorna {nome_da_fonte: deu_certo}."""
    if not forcar and not hoje_e_dia_da_atualizacao(hoje):
        logger.info(
            "Hoje não é o dia da atualização (%s).", NOMES_DIAS[DIA_ATUALIZACAO]
        )
        return {}
    ano = (hoje or date.today()).year
    resultado = {}
    # Uma fonte com erro não impede as outras de rodarem
    for nome, fonte in montar_fontes(ano).items():
        resultado[nome] = atualizar_fonte(nome, fonte, pasta_backup)
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


if __name__ == "__main__":
    main()
