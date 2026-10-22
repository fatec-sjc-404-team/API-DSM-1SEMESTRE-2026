import pandas as pd

from filtros import Filtros
from indicadores import calcular_indicadores, consultar_indicadores


def test_calcular_indicadores_soma_antes_de_dividir() -> None:
    dados = pd.DataFrame(
        {
            "tipo_divida": ["saudavel", "critica"],
            "carteira_ativa": [900.0, 100.0],
            "carteira_inadimplencia": [0.0, 50.0],
        }
    )

    assert calcular_indicadores(dados) == {
        "carteira_ativa": 1000.0,
        "taxa_inadimplencia": 5.0,
        "pct_saudavel": 90.0,
        "pct_critica": 10.0,
        "pct_mista": 0.0,
    }


def test_calcular_indicadores_sem_carteira_ativa_devolve_vazio() -> None:
    sem_linhas = pd.DataFrame(
        columns=["tipo_divida", "carteira_ativa", "carteira_inadimplencia"]
    )
    zerada = pd.DataFrame(
        {
            "tipo_divida": ["mista"],
            "carteira_ativa": [0.0],
            "carteira_inadimplencia": [0.0],
        }
    )

    assert calcular_indicadores(sem_linhas) == {}
    assert calcular_indicadores(zerada) == {}


def test_sem_filtro_calcula_geral_por_regiao_e_por_estado(fonte_falsa) -> None:
    resultado = consultar_indicadores(Filtros())

    assert resultado["geral"] == {
        "carteira_ativa": 5300.0,
        "taxa_inadimplencia": 8.0,
        "pct_saudavel": 56.6,
        "pct_critica": 5.66,
        "pct_mista": 37.74,
    }
    assert resultado["por_regiao"]["norte"] == {
        "carteira_ativa": 200.0,
        "taxa_inadimplencia": 15.0,
        "pct_saudavel": 0.0,
        "pct_critica": 100.0,
        "pct_mista": 0.0,
    }
    assert resultado["por_regiao"]["nordeste"] == {
        "carteira_ativa": 5100.0,
        "taxa_inadimplencia": 7.73,
        "pct_saudavel": 58.82,
        "pct_critica": 1.96,
        "pct_mista": 39.22,
    }
    assert sorted(resultado["por_estado"]) == ["AC", "BA", "CE"]
    assert resultado["por_estado"]["BA"]["taxa_inadimplencia"] == 11.29
    assert resultado["por_estado"]["CE"]["taxa_inadimplencia"] == 2.2


def test_resposta_traz_os_filtros_usados_e_a_data_mais_recente(fonte_falsa) -> None:
    resultado = consultar_indicadores(Filtros(regiao="norte", meses=2))

    assert resultado["filtros"] == {
        "regiao": "norte",
        "estado": None,
        "meses": 2,
        "tipo_divida": None,
    }
    assert resultado["ultima_data_base"] == "2026-07-31"


def test_regiao_deixa_so_os_estados_dela(fonte_falsa) -> None:
    resultado = consultar_indicadores(Filtros(regiao="norte"))

    assert list(resultado["por_regiao"]) == ["norte"]
    assert list(resultado["por_estado"]) == ["AC"]
    assert resultado["geral"]["taxa_inadimplencia"] == 15.0


def test_estado_deixa_so_aquele_estado(fonte_falsa) -> None:
    resultado = consultar_indicadores(Filtros(estado="BA"))

    assert list(resultado["por_estado"]) == ["BA"]
    assert list(resultado["por_regiao"]) == ["nordeste"]
    assert resultado["geral"]["taxa_inadimplencia"] == 11.29


def test_periodo_de_um_mes_usa_so_o_ultimo_mes(fonte_falsa) -> None:
    geral = consultar_indicadores(Filtros(meses=1))["geral"]

    assert geral == {
        "carteira_ativa": 3200.0,
        "taxa_inadimplencia": 8.25,
        "pct_saudavel": 31.25,
        "pct_critica": 6.25,
        "pct_mista": 62.5,
    }


def test_tipo_de_divida_calcula_so_com_aquele_tipo(fonte_falsa) -> None:
    resultado = consultar_indicadores(Filtros(tipo_divida="critica"))

    assert resultado["geral"]["taxa_inadimplencia"] == 26.67
    assert resultado["geral"]["pct_critica"] == 100.0
    assert resultado["por_estado"]["AC"]["taxa_inadimplencia"] == 15.0
    assert resultado["por_estado"]["BA"]["taxa_inadimplencia"] == 50.0
    assert "CE" not in resultado["por_estado"]


def test_filtros_combinados(fonte_falsa) -> None:
    filtros = Filtros(regiao="nordeste", meses=1, tipo_divida="critica")

    resultado = consultar_indicadores(filtros)

    assert list(resultado["por_estado"]) == ["BA"]
    assert resultado["geral"]["taxa_inadimplencia"] == 50.0


def test_combinacao_sem_dados_devolve_tudo_vazio(fonte_falsa) -> None:
    resultado = consultar_indicadores(Filtros(regiao="norte", tipo_divida="saudavel"))

    assert resultado["geral"] == {}
    assert resultado["por_regiao"] == {}
    assert resultado["por_estado"] == {}


def test_remover_o_filtro_traz_os_indicadores_de_volta(fonte_falsa) -> None:
    com_filtro = consultar_indicadores(Filtros(estado="BA"))
    sem_filtro = consultar_indicadores(Filtros())

    assert len(com_filtro["por_estado"]) == 1
    assert len(sem_filtro["por_estado"]) == 3
