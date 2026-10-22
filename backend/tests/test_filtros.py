import pandas as pd
import pytest

from filtros import Filtros, aplicar_filtros, ler_filtros


@pytest.fixture
def dados() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "uf": ["AC", "BA", " ce ", "SP", None, "BA"],
            "data_base": [
                "2026-01-31",
                "2026-05-31",
                "2026-07-31",
                "2026-07-31",
                "2026-07-31",
                "2026-07-31",
            ],
            "tipo_divida": [
                "saudavel",
                "critica",
                "mista",
                "saudavel",
                "critica",
                "critica",
            ],
            "carteira_ativa": [10, 20, 30, 40, 50, 60],
        }
    )


def test_ler_filtros_sem_nada_nao_filtra() -> None:
    assert ler_filtros({}) == Filtros()
    assert (
        ler_filtros({"regiao": "todos", "estado": "", "tipoDivida": "Todos"})
        == Filtros()
    )


def test_ler_filtros_converte_os_valores() -> None:
    filtros = ler_filtros(
        {
            "regiao": "Nordeste",
            "estado": "ba",
            "periodo": "6_meses",
            "tipoDivida": "critica",
        }
    )

    assert filtros == Filtros("nordeste", "BA", 6, "critica")


def test_ler_filtros_aceita_um_mes_no_singular() -> None:
    assert ler_filtros({"periodo": "1_mes"}).meses == 1


@pytest.mark.parametrize(
    "parametros",
    [
        {"regiao": "sul"},
        {"estado": "XX"},
        {"periodo": "13_meses"},
        {"periodo": "0_meses"},
        {"periodo": "ontem"},
        {"tipoDivida": "ruim"},
    ],
)
def test_ler_filtros_rejeita_valor_invalido(parametros: dict[str, str]) -> None:
    with pytest.raises(ValueError):
        ler_filtros(parametros)


def test_ler_filtros_rejeita_estado_fora_da_regiao() -> None:
    with pytest.raises(ValueError, match="não pertence à região"):
        ler_filtros({"regiao": "norte", "estado": "BA"})


def test_aplicar_filtros_sem_filtro_devolve_tudo(dados: pd.DataFrame) -> None:
    assert len(aplicar_filtros(dados, Filtros())) == len(dados)


def test_aplicar_filtros_por_regiao_normaliza_uf(dados: pd.DataFrame) -> None:
    resultado = aplicar_filtros(dados, Filtros(regiao="nordeste"))

    assert resultado["uf"].tolist() == ["BA", " ce ", "BA"]


def test_aplicar_filtros_por_estado(dados: pd.DataFrame) -> None:
    resultado = aplicar_filtros(dados, Filtros(estado="BA"))

    assert resultado["carteira_ativa"].tolist() == [20, 60]


def test_aplicar_filtros_por_periodo_conta_a_partir_do_mes_mais_recente(
    dados: pd.DataFrame,
) -> None:
    ultimo_mes = aplicar_filtros(dados, Filtros(meses=1))
    tres_meses = aplicar_filtros(dados, Filtros(meses=3))

    assert set(ultimo_mes["data_base"]) == {"2026-07-31"}
    assert set(tres_meses["data_base"]) == {"2026-05-31", "2026-07-31"}


def test_periodo_nao_inclui_o_mes_anterior_quando_o_ultimo_mes_tem_30_dias() -> None:
    # 30/06 menos 1 mês dá 30/05, e 31/05 é maior que isso: por data exata o
    # mês anterior entraria junto. Por mês-calendário não entra.
    dados = pd.DataFrame(
        {"data_base": ["2026-04-30", "2026-05-31", "2026-06-30"], "valor": [1, 2, 3]}
    )

    um_mes = aplicar_filtros(dados, Filtros(meses=1))
    dois_meses = aplicar_filtros(dados, Filtros(meses=2))

    assert um_mes["valor"].tolist() == [3]
    assert dois_meses["valor"].tolist() == [2, 3]


def test_periodo_funciona_com_datas_do_pandas_e_com_texto() -> None:
    texto = pd.DataFrame({"data_base": ["2026-05-31", "2026-06-30"]})
    datas = pd.DataFrame({"data_base": pd.to_datetime(texto["data_base"])})

    assert len(aplicar_filtros(texto, Filtros(meses=1))) == 1
    assert len(aplicar_filtros(datas, Filtros(meses=1))) == 1


def test_aplicar_filtros_por_tipo_de_divida(dados: pd.DataFrame) -> None:
    resultado = aplicar_filtros(dados, Filtros(tipo_divida="critica"))

    assert resultado["carteira_ativa"].tolist() == [20, 50, 60]


def test_aplicar_filtros_combinados(dados: pd.DataFrame) -> None:
    filtros = Filtros(regiao="nordeste", meses=1, tipo_divida="critica")

    resultado = aplicar_filtros(dados, filtros)

    assert resultado["carteira_ativa"].tolist() == [60]


def test_aplicar_filtros_nao_altera_o_original_e_mantem_colunas(
    dados: pd.DataFrame,
) -> None:
    resultado = aplicar_filtros(dados, Filtros(estado="BA"))

    assert len(dados) == 6
    assert resultado.columns.tolist() == dados.columns.tolist()


def test_remover_o_filtro_traz_os_dados_de_volta(dados: pd.DataFrame) -> None:
    filtrado = aplicar_filtros(dados, Filtros(estado="BA"))
    sem_filtro = aplicar_filtros(dados, Filtros())

    assert len(filtrado) < len(sem_filtro) == len(dados)


def test_combinacao_sem_resultado_devolve_tabela_vazia(dados: pd.DataFrame) -> None:
    resultado = aplicar_filtros(dados, Filtros(regiao="norte", estado="AC", meses=1))

    assert resultado.empty
    assert resultado.columns.tolist() == dados.columns.tolist()


@pytest.mark.parametrize(
    ("filtros", "coluna"),
    [
        (Filtros(regiao="norte"), "uf"),
        (Filtros(estado="BA"), "uf"),
        (Filtros(meses=1), "data_base"),
        (Filtros(tipo_divida="critica"), "tipo_divida"),
    ],
)
def test_filtro_exige_a_coluna_correspondente(filtros: Filtros, coluna: str) -> None:
    with pytest.raises(ValueError, match=f"coluna '{coluna}'"):
        aplicar_filtros(pd.DataFrame({"valor": [1]}), filtros)
