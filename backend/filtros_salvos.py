"""Persistência de filtros salvos no MySQL."""

import os
import re

import pymysql
from pymysql.cursors import DictCursor

from filtros import UFS_NORDESTE, UFS_NORTE

REGIOES = {"norte", "nordeste"}
ESTADOS = UFS_NORTE | UFS_NORDESTE
TIPOS_DIVIDA = {"saudavel", "critica", "mista"}


def _conectar():
    usuario = os.environ.get("DB_USER")
    if not usuario:
        raise RuntimeError("Configure DB_USER para habilitar o MySQL.")
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=usuario,
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "AvoCredit"),
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )


def validar_filtro(dados):
    if not isinstance(dados, dict):
        raise TypeError("Envie os dados do filtro em formato JSON.")

    nome = dados.get("nome")
    if not isinstance(nome, str) or not nome.strip() or len(nome.strip()) > 100:
        raise ValueError("O nome deve ter entre 1 e 100 caracteres.")

    regiao = dados.get("regiao")
    if regiao is not None:
        if not isinstance(regiao, str):
            raise ValueError("Região deve ser norte, nordeste ou Todos.")
        regiao = regiao.strip().lower()
        if regiao in ("", "todos"):
            regiao = None
        elif regiao not in REGIOES:
            raise ValueError("Região deve ser norte, nordeste ou Todos.")

    estado = dados.get("estado")
    if estado is not None:
        if not isinstance(estado, str):
            raise ValueError("Estado deve ser uma sigla ou Todos.")
        estado = estado.strip().upper()
        if estado in ("", "TODOS"):
            estado = None
        elif estado not in ESTADOS:
            raise ValueError("A sigla do estado é inválida.")
        elif regiao == "norte" and estado not in UFS_NORTE:
            raise ValueError("O estado não pertence à região Norte.")
        elif regiao == "nordeste" and estado not in UFS_NORDESTE:
            raise ValueError("O estado não pertence à região Nordeste.")

    periodo_bruto = dados.get("periodo")
    if isinstance(periodo_bruto, bool) or not re.fullmatch(
        r"\d{1,2}", str(periodo_bruto or "")
    ):
        raise ValueError("Período deve ser um número de 1 a 12 meses.")
    periodo = int(periodo_bruto)
    if not 1 <= periodo <= 12:
        raise ValueError("Período deve ser um número de 1 a 12 meses.")

    tipo_divida = dados.get("tipo_divida", dados.get("tipoDivida"))
    if tipo_divida is not None:
        if not isinstance(tipo_divida, str):
            raise ValueError("Tipo de dívida inválido.")
        tipo_divida = tipo_divida.strip().lower()
        if tipo_divida in ("", "todos"):
            tipo_divida = None
        elif tipo_divida not in TIPOS_DIVIDA:
            raise ValueError("Tipo de dívida inválido.")

    return {
        "nome": nome.strip(),
        "regiao": regiao,
        "estado": estado,
        "periodo": periodo,
        "tipo_divida": tipo_divida,
    }


def listar_filtros():
    conexao = _conectar()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id, nome, regiao, estado, periodo, tipo_divida, criado_em "
                "FROM filtros_salvos ORDER BY criado_em DESC, id DESC"
            )
            filtros = cursor.fetchall()
        # criado_em vem em horário local (NOW()); o ISO sem fuso evita que o
        # Flask o rotule como GMT e a tela mostre 3h a menos.
        for filtro in filtros:
            if hasattr(filtro.get("criado_em"), "isoformat"):
                filtro["criado_em"] = filtro["criado_em"].isoformat()
        return filtros
    finally:
        conexao.close()


def salvar_filtro(filtro):
    conexao = _conectar()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "INSERT INTO filtros_salvos "
                "(nome, regiao, estado, periodo, tipo_divida, criado_em) "
                "VALUES (%s, %s, %s, %s, %s, NOW())",
                (
                    filtro["nome"],
                    filtro["regiao"],
                    filtro["estado"],
                    filtro["periodo"],
                    filtro["tipo_divida"],
                ),
            )
            filtro_id = cursor.lastrowid
        conexao.commit()
        return filtro_id
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def renomear_filtro(filtro_id, nome):
    if not isinstance(nome, str) or not nome.strip() or len(nome.strip()) > 100:
        raise ValueError("O nome deve ter entre 1 e 100 caracteres.")
    conexao = _conectar()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE filtros_salvos SET nome = %s WHERE id = %s",
                (nome.strip(), filtro_id),
            )
            alterado = cursor.rowcount > 0
        conexao.commit()
        return alterado
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def excluir_filtro(filtro_id):
    conexao = _conectar()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("DELETE FROM filtros_salvos WHERE id = %s", (filtro_id,))
            excluido = cursor.rowcount > 0
        conexao.commit()
        return excluido
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()
