import re
from collections.abc import Mapping
from dataclasses import dataclass

import pandas as pd

# UFs de cada região, usadas pra filtrar pela coluna "uf" dos dados.
UFS_NORTE = frozenset({"AC", "AM", "AP", "PA", "RO", "RR", "TO"})
UFS_NORDESTE = frozenset({"AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"})
UFS_POR_REGIAO = {"norte": UFS_NORTE, "nordeste": UFS_NORDESTE}

TIPOS_DIVIDA = frozenset({"saudavel", "critica", "mista"})

# O formulário manda o período como "1_mes", "2_meses", ... "12_meses".
PADRAO_PERIODO = re.compile(r"^(\d{1,2})_mes(?:es)?$")
MAXIMO_MESES = 12


@dataclass(frozen=True)
class Filtros:
    """Filtros escolhidos pelo usuário. None significa que o filtro não foi usado."""

    regiao: str | None = None
    estado: str | None = None
    meses: int | None = None
    tipo_divida: str | None = None


def ler_filtros(parametros: Mapping[str, str]) -> Filtros:
    """Lê e valida os filtros vindos da URL (regiao, estado, periodo, tipoDivida).

    Valor vazio ou "todos" conta como filtro não usado. Levanta ValueError se
    algum valor for inválido.
    """
    regiao = _valor(parametros, "regiao")
    estado = _valor(parametros, "estado")
    periodo = _valor(parametros, "periodo")
    tipo_divida = _valor(parametros, "tipoDivida")

    if regiao is not None:
        regiao = regiao.lower()
        if regiao not in UFS_POR_REGIAO:
            raise ValueError(f"Região inválida: '{regiao}'. Use norte ou nordeste.")

    if estado is not None:
        estado = estado.upper()
        todas_as_ufs = UFS_NORTE | UFS_NORDESTE
        if estado not in todas_as_ufs:
            raise ValueError(f"Estado inválido: '{estado}'.")
        if regiao is not None and estado not in UFS_POR_REGIAO[regiao]:
            raise ValueError(f"O estado {estado} não pertence à região {regiao}.")

    meses = None
    if periodo is not None:
        correspondencia = PADRAO_PERIODO.match(periodo.lower())
        if correspondencia is None or not 1 <= int(correspondencia[1]) <= MAXIMO_MESES:
            raise ValueError(
                f"Período inválido: '{periodo}'. Use de 1_mes até {MAXIMO_MESES}_meses."
            )
        meses = int(correspondencia[1])

    if tipo_divida is not None:
        tipo_divida = tipo_divida.lower()
        if tipo_divida not in TIPOS_DIVIDA:
            raise ValueError(
                f"Tipo de dívida inválido: '{tipo_divida}'. "
                "Use saudavel, critica ou mista."
            )

    return Filtros(regiao, estado, meses, tipo_divida)


def aplicar_filtros(dados: pd.DataFrame, filtros: Filtros) -> pd.DataFrame:
    """Devolve só as linhas que atendem aos filtros, mantendo todas as colunas.

    Cada filtro usa uma coluna: uf (região e estado), data_base (período) e
    tipo_divida. Levanta ValueError se um filtro for usado e a coluna não existir.
    Sem nenhum filtro, devolve tudo.
    """
    mascara = pd.Series(True, index=dados.index)

    if filtros.regiao is not None:
        _exigir_coluna(dados, "uf")
        mascara &= _uf(dados).isin(UFS_POR_REGIAO[filtros.regiao])

    if filtros.estado is not None:
        _exigir_coluna(dados, "uf")
        mascara &= _uf(dados) == filtros.estado

    if filtros.meses is not None:
        _exigir_coluna(dados, "data_base")
        # Conta por mês, não por dia: os dados vêm no fim de cada mês (30/06, 31/07)
        # e subtrair meses de uma data de fim de mês cairia no dia errado.
        meses = pd.to_datetime(dados["data_base"]).dt.to_period("M")
        mascara &= meses > meses.max() - filtros.meses

    if filtros.tipo_divida is not None:
        _exigir_coluna(dados, "tipo_divida")
        tipo = dados["tipo_divida"].astype("string").str.strip().str.lower()
        mascara &= tipo == filtros.tipo_divida

    # fillna: valores nulos (ex: UF vazia) nunca atendem ao filtro
    return dados.loc[mascara.fillna(False)].copy()


def _uf(dados: pd.DataFrame) -> pd.Series:
    return dados["uf"].astype("string").str.strip().str.upper()


def _exigir_coluna(dados: pd.DataFrame, coluna: str) -> None:
    if coluna not in dados.columns:
        raise ValueError(f"A tabela precisa ter a coluna '{coluna}' para esse filtro.")


def _valor(parametros: Mapping[str, str], nome: str) -> str | None:
    valor = parametros.get(nome, "").strip()
    return None if valor == "" or valor.lower() == "todos" else valor
