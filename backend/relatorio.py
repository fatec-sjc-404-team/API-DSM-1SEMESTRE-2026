from io import BytesIO

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

VERDE = "#2e7d32"
CINZA = "#555555"
TAMANHO_PAGINA = (8.27, 11.69)  # A4 em polegadas

NOMES_REGIAO = {"norte": "Norte", "nordeste": "Nordeste"}
NOMES_TIPO_DIVIDA = {"saudavel": "Saudável", "critica": "Crítica", "mista": "Mista"}

# Linhas da tabela de indicadores gerais: (campo da API, rótulo, sufixo).
INDICADORES_DA_TABELA = [
    ("indicador_geral", "Potencial de crédito (0 a 100)", ""),
    ("carteira_ativa", "Carteira ativa (R$)", ""),
    ("taxa_inadimplencia", "Taxa de inadimplência", "%"),
    ("pct_saudavel", "Dívida saudável", "%"),
    ("pct_critica", "Dívida crítica", "%"),
    ("pct_mista", "Dívida mista", "%"),
    ("pct_credito_caro", "Crédito caro", "%"),
    ("pct_recuperacao_rapida", "Recuperação rápida", "%"),
]

# Gráficos de evolução mensal: (campo da API, título).
INDICADORES_DA_LINHA = [
    ("indicador_geral", "Potencial de crédito"),
    ("pct_recuperacao_rapida", "Recuperação rápida (%)"),
    ("pct_credito_caro", "Crédito caro (%)"),
    ("pct_saudavel", "Dívida saudável (%)"),
]


def gerar_relatorio_pdf(indicadores: dict) -> bytes:
    """Monta o PDF a partir da resposta de consultar_indicadores.

    A primeira página traz os filtros e os indicadores gerais; depois vêm os
    mesmos gráficos da tela (por estado e evolução mensal). Sem dados para os
    filtros, o PDF só avisa isso na primeira página.
    """
    paginas = [_pagina_resumo(indicadores)]
    if indicadores["por_estado"]:
        paginas.append(_pagina_barras(indicadores))
        paginas.append(_pagina_linhas(indicadores))

    saida = BytesIO()
    with PdfPages(saida) as pdf:
        for pagina in paginas:
            pdf.savefig(pagina)
    return saida.getvalue()


def descrever_filtros(filtros: dict) -> list[str]:
    """Texto de cada filtro aplicado; filtro não usado aparece como "Todos"."""
    regiao = filtros.get("regiao")
    meses = filtros.get("meses")
    tipo_divida = filtros.get("tipo_divida")
    return [
        f"Região: {NOMES_REGIAO.get(regiao, 'Todas')}",
        f"Estado: {filtros.get('estado') or 'Todos'}",
        f"Período: {_descrever_periodo(meses)}",
        f"Tipo de dívida: {NOMES_TIPO_DIVIDA.get(tipo_divida, 'Todos')}",
    ]


def _descrever_periodo(meses: int | None) -> str:
    if meses is None:
        return "todo o histórico"
    return "último mês" if meses == 1 else f"últimos {meses} meses"


def _pagina_resumo(indicadores: dict) -> Figure:
    figura = Figure(figsize=TAMANHO_PAGINA)
    figura.text(
        0.08, 0.94, "Relatório de Potencial de Crédito", fontsize=18, weight="bold"
    )
    figura.text(0.08, 0.915, "Regiões Norte e Nordeste", fontsize=11, color=CINZA)

    figura.text(0.08, 0.87, "Filtros aplicados", fontsize=12, weight="bold")
    for posicao, texto in enumerate(descrever_filtros(indicadores["filtros"])):
        figura.text(0.08, 0.845 - posicao * 0.025, texto, fontsize=10)

    data_base = indicadores.get("ultima_data_base")
    if data_base:
        figura.text(
            0.08,
            0.735,
            f"Dados atualizados em {_data_brasileira(data_base)}",
            fontsize=10,
            color=CINZA,
        )

    if not indicadores["por_estado"]:
        figura.text(
            0.08, 0.68, "Nenhum dado encontrado para esses filtros.", fontsize=11
        )
        return figura

    figura.text(0.08, 0.69, "Indicadores gerais", fontsize=12, weight="bold")
    eixo = figura.add_axes((0.08, 0.38, 0.84, 0.29))
    eixo.axis("off")
    tabela = eixo.table(
        cellText=_linhas_da_tabela(indicadores["geral"]),
        colLabels=["Indicador", "Valor"],
        colWidths=[0.65, 0.35],
        loc="upper center",
        cellLoc="left",
    )
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    tabela.scale(1, 1.6)
    return figura


def _pagina_barras(indicadores: dict) -> Figure:
    figura = Figure(figsize=TAMANHO_PAGINA)
    figura.text(
        0.08, 0.94, "Potencial de crédito por estado", fontsize=14, weight="bold"
    )

    por_estado = indicadores["por_estado"]
    estados = sorted(
        por_estado, key=lambda uf: por_estado[uf]["indicador_geral"] or 0, reverse=True
    )
    valores = [por_estado[uf]["indicador_geral"] or 0 for uf in estados]

    eixo = figura.add_axes((0.1, 0.55, 0.82, 0.34))
    barras = eixo.bar(estados, valores, color=VERDE)
    eixo.bar_label(barras, fmt="%.1f", fontsize=9)
    eixo.set_ylim(0, 100)
    eixo.set_ylabel("Potencial de crédito (0 a 100)")
    return figura


def _pagina_linhas(indicadores: dict) -> Figure:
    figura = Figure(figsize=TAMANHO_PAGINA)
    figura.text(0.08, 0.96, "Evolução mensal", fontsize=14, weight="bold")

    por_mes = indicadores["por_mes"]
    meses = sorted(por_mes)
    rotulos = [f"{mes[5:7]}/{mes[:4]}" for mes in meses]

    for posicao, (campo, titulo) in enumerate(INDICADORES_DA_LINHA):
        eixo = figura.add_axes((0.1, 0.72 - posicao * 0.24, 0.82, 0.17))
        # None (indicador sem dado no mês) vira buraco na linha.
        valores = [
            por_mes[mes][campo] if por_mes[mes][campo] is not None else float("nan")
            for mes in meses
        ]
        eixo.plot(rotulos, valores, color=VERDE, marker="o")
        eixo.set_title(titulo, fontsize=10, loc="left")
        eixo.tick_params(axis="x", labelsize=8)
    return figura


def _linhas_da_tabela(geral: dict) -> list[list[str]]:
    linhas = []
    for campo, rotulo, sufixo in INDICADORES_DA_TABELA:
        valor = geral.get(campo)
        if valor is None:
            texto = "não se aplica"
        elif campo == "carteira_ativa":
            texto = (
                f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        else:
            texto = f"{valor:.2f}".replace(".", ",") + sufixo
        linhas.append([rotulo, texto])
    return linhas


def _data_brasileira(data: str) -> str:
    ano, mes, dia = data.split("-")
    return f"{dia}/{mes}/{ano}"
