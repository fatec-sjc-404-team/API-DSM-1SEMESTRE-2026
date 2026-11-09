import pandas as pd

from dados import dados_filtrados, descrever_consulta
from filtros import UFS_POR_REGIAO, Filtros

TIPOS_DIVIDA = ("saudavel", "critica", "mista")
REGIAO_DA_UF = {uf: regiao for regiao, ufs in UFS_POR_REGIAO.items() for uf in ufs}


def calcular_indicadores(dados: pd.DataFrame) -> dict[str, float | None]:
    """Indicadores de um grupo de linhas (tudo, uma região ou um estado).

    - carteira_ativa: soma da carteira ativa.
    - taxa_inadimplencia: carteira inadimplente / carteira ativa, em %.
    - pct_saudavel, pct_critica, pct_mista: quanto da carteira ativa é de cada
      tipo de dívida, em % (indicador de dívida saudável x crítica).
    - pct_credito_caro: quanto da carteira ativa é rotativo do cartão ou cheque
      especial, em % (indicador de crédito caro).
    - pct_recuperacao_rapida: quanto da carteira vencida ainda está no atraso
      inicial (15 a 90 dias), em % (indicador de recuperação rápida). Fica None
      se o grupo não tiver nada vencido.
    - indicador_geral: nota de 0 a 100 que junta os indicadores acima
      (veja calcular_indicador_geral).

    Os valores são somados antes de dividir, então grupos grandes pesam mais que
    os pequenos. Devolve {} se o grupo não tiver carteira ativa.
    """
    carteira_ativa = dados["carteira_ativa"].sum()
    if carteira_ativa <= 0:
        return {}

    inadimplencia = dados["carteira_inadimplencia"].sum()
    por_tipo = dados.groupby("tipo_divida")["carteira_ativa"].sum()

    indicadores: dict[str, float | None] = {
        "carteira_ativa": round(carteira_ativa, 2),
        "taxa_inadimplencia": _pct(inadimplencia, carteira_ativa),
    }
    for tipo in TIPOS_DIVIDA:
        indicadores[f"pct_{tipo}"] = _pct(por_tipo.get(tipo, 0), carteira_ativa)

    indicadores["pct_credito_caro"] = _pct(
        dados["carteira_credito_caro"].sum(), carteira_ativa
    )
    indicadores["pct_recuperacao_rapida"] = calcular_recuperacao_rapida(dados)
    indicadores["indicador_geral"] = calcular_indicador_geral(indicadores)
    return indicadores


def calcular_recuperacao_rapida(dados: pd.DataFrame) -> float | None:
    """Parte da carteira vencida que está no atraso inicial (15 a 90 dias), em %.

    A regra de docs/pesquisa/regras-de-indicador.md olha a data de pagamento de
    cada dívida (quitada até 20 dias depois do vencimento). Os dados do BCB não
    têm datas de pagamento, só o saldo vencido por faixa de atraso, e a primeira
    faixa já começa em 15 dias. Então usamos a faixa de 15 a 90 dias como sinal
    de atraso que ainda pode ser recuperado: quanto maior a porcentagem, menos
    dívida virou atraso longo (acima de 90 dias).

    Devolve None se não houver nada vencido, porque aí o indicador não se aplica.
    """
    atraso_inicial = dados["vencido_de_15_ate_90_dias"].sum()
    vencido = atraso_inicial + dados["vencido_acima_de_90_dias"].sum()
    if vencido <= 0:
        return None
    return _pct(atraso_inicial, vencido)


def calcular_indicador_geral(indicadores: dict[str, float | None]) -> float | None:
    """Junta os indicadores menores em uma nota de 0 a 100 (maior é melhor).

    Cada indicador vira uma nota de 0 a 100 e o geral é a média simples delas:
    - crédito caro: 100 - pct_credito_caro (menos crédito caro, nota maior).
    - dívida saudável x crítica: 50 + (pct_saudavel - pct_critica) / 2, ou seja,
      100 se for tudo saudável, 0 se for tudo crítico e 50 se for tudo misto.
    - recuperação rápida: o próprio pct_recuperacao_rapida. Fica de fora da
      média quando é None (nada vencido).
    - endividamento por apostas: ainda não existe (depende dos dados da US08).
      Quando existir, entra aqui como mais uma nota.

    Devolve None se nenhuma nota puder ser calculada.
    """
    notas = []

    if indicadores.get("pct_credito_caro") is not None:
        notas.append(100 - indicadores["pct_credito_caro"])

    if indicadores.get("pct_saudavel") is not None:
        saldo = indicadores["pct_saudavel"] - indicadores["pct_critica"]
        notas.append(50 + saldo / 2)

    if indicadores.get("pct_recuperacao_rapida") is not None:
        notas.append(indicadores["pct_recuperacao_rapida"])

    if not notas:
        return None
    return round(sum(notas) / len(notas), 2)


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


def _por_grupo(
    dados: pd.DataFrame, grupos: pd.Series
) -> dict[str, dict[str, float | None]]:
    resultado = {}
    for nome, linhas in dados.groupby(grupos):
        indicadores = calcular_indicadores(linhas)
        if indicadores:
            resultado[str(nome)] = indicadores
    return resultado


def _pct(parte: float, total: float) -> float:
    return round(parte / total * 100, 2)
