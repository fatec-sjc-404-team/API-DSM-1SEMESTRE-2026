import pandas as pd

from dados import dados_filtrados, descrever_consulta
from filtros import UFS_POR_REGIAO, Filtros

TIPOS_DIVIDA = ("saudavel", "critica", "mista")
REGIAO_DA_UF = {uf: regiao for regiao, ufs in UFS_POR_REGIAO.items() for uf in ufs}


def calcular_indicadores(dados: pd.DataFrame) -> dict[str, float]:
    """Indicadores de um grupo de linhas (tudo, uma região ou um estado).

    - carteira_ativa: soma da carteira ativa.
    - taxa_inadimplencia: carteira inadimplente / carteira ativa, em %.
    - pct_saudavel, pct_critica, pct_mista: quanto da carteira ativa é de cada
      tipo de dívida, em %.

    Os valores são somados antes de dividir, então grupos grandes pesam mais que
    os pequenos. Devolve {} se o grupo não tiver carteira ativa.
    """
    carteira_ativa = dados["carteira_ativa"].sum()
    if carteira_ativa <= 0:
        return {}

    inadimplencia = dados["carteira_inadimplencia"].sum()
    por_tipo = dados.groupby("tipo_divida")["carteira_ativa"].sum()

    indicadores = {
        "carteira_ativa": round(carteira_ativa, 2),
        "taxa_inadimplencia": round(inadimplencia / carteira_ativa * 100, 2),
    }
    for tipo in TIPOS_DIVIDA:
        indicadores[f"pct_{tipo}"] = round(
            por_tipo.get(tipo, 0) / carteira_ativa * 100, 2
        )
    return indicadores


def consultar_indicadores(filtros: Filtros) -> dict:
    """Resposta de /api/indicadores: indicadores gerais, por região e por estado.

    Os filtros são aplicados nos dados antes de calcular. Se houver filtro de tipo
    de dívida, os percentuais por tipo valem só para o que sobrou do filtro.
    """
    dados = dados_filtrados(filtros)
    regioes = dados["uf"].map(REGIAO_DA_UF)

    return {
        **descrever_consulta(filtros),
        "geral": calcular_indicadores(dados),
        "por_regiao": _por_grupo(dados, regioes),
        "por_estado": _por_grupo(dados, dados["uf"]),
    }


def _por_grupo(dados: pd.DataFrame, grupos: pd.Series) -> dict[str, dict[str, float]]:
    resultado = {}
    for nome, linhas in dados.groupby(grupos):
        indicadores = calcular_indicadores(linhas)
        if indicadores:
            resultado[str(nome)] = indicadores
    return resultado
