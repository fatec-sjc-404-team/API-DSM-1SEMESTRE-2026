import os
import time
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from filtros import Filtros, aplicar_filtros

ARQUIVO_CSV = (
    Path(__file__).parent
    / "Tratamento_Dados"
    / "saida"
    / "scrdata_norte_nordeste_pessoa_fisica_baixa_renda.csv"
)

# Colunas de valor lidas da fonte. As faixas de vencido são usadas no indicador
# de recuperação rápida (veja indicadores.py).
COLUNAS_VALORES = [
    "carteira_ativa",
    "carteira_inadimplencia",
    "vencido_de_15_ate_90_dias",
    "vencido_acima_de_90_dias",
]

# Colunas que a /api/dados devolve em cada linha.
COLUNAS_RESPOSTA = [
    "data_base",
    "uf",
    "tipo_divida",
    "carteira_ativa",
    "carteira_inadimplencia",
]

# Quanto tempo a tabela fica guardada na memória antes de ler a fonte de novo.
SEGUNDOS_DE_CACHE = 300

# Tipo de dívida, seguindo a regra de docs/pesquisa/regras-de-indicador.md:
# crítica = consumo imediato com juros altos (rotativo do cartão, cheque especial),
# saudável = patrimônio ou crédito produtivo (imóvel, rural, microcrédito).
# O que não cai em nenhuma das duas fica como "mista".
# Classificação temporária: proposta ainda não validada pelo grupo.
CARTAO_SAQUE_FINANCIADO = (
    "cartão de crédito - compra, fatura parcelada ou saque financiado pela "
    "instituição financeira emitente do cartão"
)
CARTAO_FATURA_PARCELADA = (
    "cartão de crédito - compra ou fatura parcelada pela instituição "
    "financeira emitente do cartão"
)
SUBMODALIDADES_CRITICAS = frozenset(
    {
        "cartão de crédito - não migrado",
        CARTAO_SAQUE_FINANCIADO,
        CARTAO_FATURA_PARCELADA,
        "crédito rotativo vinculado a cartão de crédito",
        "cheque especial",
        "adiantamentos a depositantes",
        "capital de giro com teto rotativo",
    }
)
MODALIDADES_SAUDAVEIS = ("financiamentos imobiliários", "financiamentos rurais")
SUBMODALIDADES_SAUDAVEIS = frozenset({"microcrédito", "financiamentos agroindustriais"})

# Crédito caro, seguindo a regra de docs/pesquisa/regras-de-indicador.md:
# rotativo do cartão e cheque especial (as linhas de juros mais altos).
# É uma parte da dívida "crítica": o parcelamento da fatura fica de fora porque
# tem juros menores e, pela regra, é uma operação de consolidação da dívida.
# Classificação temporária: proposta ainda não validada pelo grupo.
SUBMODALIDADES_CREDITO_CARO = frozenset(
    {
        "cartão de crédito - não migrado",
        "crédito rotativo vinculado a cartão de crédito",
        "cheque especial",
        "adiantamentos a depositantes",
    }
)

_cache: tuple[float, pd.DataFrame] | None = None


class DadosIndisponiveis(Exception):
    """A fonte dos dados (MySQL ou CSV) não pôde ser lida."""


def classificar_tipo_divida(modalidade: str, submodalidade: str) -> str:
    """Devolve 'saudavel', 'critica' ou 'mista' para a modalidade do crédito."""
    modalidade = _normalizar(modalidade)
    submodalidade = _normalizar(submodalidade)

    if submodalidade in SUBMODALIDADES_CRITICAS:
        return "critica"
    if (
        modalidade.startswith(MODALIDADES_SAUDAVEIS)
        or submodalidade in SUBMODALIDADES_SAUDAVEIS
    ):
        return "saudavel"
    return "mista"


def eh_credito_caro(submodalidade: str) -> bool:
    """True se a submodalidade é rotativo do cartão ou cheque especial."""
    return _normalizar(submodalidade) in SUBMODALIDADES_CREDITO_CARO


def carregar_bcb() -> pd.DataFrame:
    """Dados do BCB somados por mês, UF e tipo de dívida.

    Colunas: data_base, uf, tipo_divida, carteira_ativa, carteira_inadimplencia,
    vencido_de_15_ate_90_dias, vencido_acima_de_90_dias e carteira_credito_caro
    (parte da carteira ativa que é crédito caro, veja eh_credito_caro).
    Lê do MySQL se DB_USER estiver definido; senão, do CSV do tratamento de dados.
    """
    global _cache

    agora = time.monotonic()
    if _cache is None or agora - _cache[0] > SEGUNDOS_DE_CACHE:
        _cache = (agora, _resumir(_ler_fonte()))
    return _cache[1]


def limpar_cache() -> None:
    global _cache
    _cache = None


def ultima_data_base() -> pd.Timestamp:
    return carregar_bcb()["data_base"].max()


def dados_filtrados(filtros: Filtros) -> pd.DataFrame:
    """Dados do BCB (veja carregar_bcb) só com as linhas que atendem aos filtros."""
    return aplicar_filtros(carregar_bcb(), filtros)


def descrever_consulta(filtros: Filtros) -> dict:
    """Cabeçalho das respostas da API: filtros usados e mês mais recente dos dados."""
    return {
        "filtros": asdict(filtros),
        "ultima_data_base": f"{ultima_data_base():%Y-%m-%d}",
    }


def consultar_dados(filtros: Filtros) -> dict:
    """Resposta de /api/dados: as linhas filtradas, somadas por mês, UF e tipo de dívida."""
    tabela = dados_filtrados(filtros)[COLUNAS_RESPOSTA]
    tabela = tabela.sort_values(["data_base", "uf", "tipo_divida"])
    tabela = tabela.assign(data_base=tabela["data_base"].dt.strftime("%Y-%m-%d"))
    linhas = tabela.round(2).to_dict("records")

    return {
        **descrever_consulta(filtros),
        "total_de_linhas": len(linhas),
        "dados": linhas,
    }


def _ler_fonte() -> pd.DataFrame:
    """Lê as colunas necessárias, já somadas por mês, UF, modalidade e submodalidade."""
    if os.environ.get("DB_USER"):
        return _ler_mysql()
    return _ler_csv()


def _ler_mysql() -> pd.DataFrame:
    import pymysql

    try:
        conexao = pymysql.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", "3306")),
            user=os.environ["DB_USER"],
            password=os.environ.get("DB_PASSWORD", ""),
            database=os.environ.get("DB_NAME", "AvoCredit"),
            charset="utf8mb4",
        )
    except pymysql.MySQLError as erro:
        raise DadosIndisponiveis(
            f"Não foi possível conectar ao MySQL: {erro}"
        ) from erro

    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT data_base, uf, modalidade, submodalidade, "
                + ", ".join(f"SUM({coluna})" for coluna in COLUNAS_VALORES)
                + " FROM BCB GROUP BY data_base, uf, modalidade, submodalidade"
            )
            linhas = cursor.fetchall()
    except pymysql.MySQLError as erro:
        raise DadosIndisponiveis(f"Erro ao consultar a tabela BCB: {erro}") from erro
    finally:
        conexao.close()

    colunas = ["data_base", "uf", "modalidade", "submodalidade", *COLUNAS_VALORES]
    return pd.DataFrame(linhas, columns=colunas)


def _ler_csv() -> pd.DataFrame:
    if not ARQUIVO_CSV.is_file():
        raise DadosIndisponiveis(
            f"Fonte de dados não encontrada. Defina DB_USER para ler do MySQL "
            f"ou gere o CSV em {ARQUIVO_CSV}."
        )

    colunas = ["data_base", "uf", "modalidade", "submodalidade", *COLUNAS_VALORES]
    dados = pd.read_csv(ARQUIVO_CSV, sep=";", decimal=",", usecols=colunas)
    return dados.groupby(colunas[:4], as_index=False)[COLUNAS_VALORES].sum()


def _resumir(dados: pd.DataFrame) -> pd.DataFrame:
    """Troca modalidade/submodalidade pelo tipo de dívida e soma de novo.

    Antes de somar, separa a carteira ativa de crédito caro numa coluna própria,
    porque depois de agrupar por tipo de dívida a submodalidade se perde.
    """
    dados = dados.copy()
    dados["data_base"] = pd.to_datetime(dados["data_base"])
    dados["uf"] = dados["uf"].astype("string").str.strip().str.upper()
    dados[COLUNAS_VALORES] = dados[COLUNAS_VALORES].astype(float)
    dados["tipo_divida"] = [
        classificar_tipo_divida(modalidade, submodalidade)
        for modalidade, submodalidade in zip(
            dados["modalidade"], dados["submodalidade"], strict=True
        )
    ]
    caro = dados["submodalidade"].map(eh_credito_caro).astype(bool)
    dados["carteira_credito_caro"] = dados["carteira_ativa"].where(caro, 0.0)

    chaves = ["data_base", "uf", "tipo_divida"]
    valores = [*COLUNAS_VALORES, "carteira_credito_caro"]
    return dados.groupby(chaves, as_index=False)[valores].sum()


def _normalizar(texto: str) -> str:
    return " ".join(str(texto).split()).casefold()
