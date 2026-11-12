import pandas as pd
import pytest

from filtros import Filtros
from indicadores import (
    calcular_indicador_geral,
    calcular_indicadores,
    calcular_recuperacao_rapida,
    consultar_indicadores,
)


def _grupo(**colunas) -> pd.DataFrame:
    """Linhas no formato de carregar_bcb, com zero nas colunas não informadas."""
    padrao = {
        "tipo_divida": ["mista"],
        "carteira_ativa": [0.0],
        "carteira_inadimplencia": [0.0],
        "vencido_de_15_ate_90_dias": [0.0],
        "vencido_acima_de_90_dias": [0.0],
        "carteira_credito_caro": [0.0],
    }
    tamanho = len(next(iter(colunas.values())))
    padrao = {nome: valores * tamanho for nome, valores in padrao.items()}
    return pd.DataFrame({**padrao, **colunas})


def test_calcular_indicadores_soma_antes_de_dividir() -> None:
    dados = _grupo(
        tipo_divida=["saudavel", "critica"],
        carteira_ativa=[900.0, 100.0],
        carteira_inadimplencia=[0.0, 50.0],
        vencido_de_15_ate_90_dias=[30.0, 20.0],
        vencido_acima_de_90_dias=[0.0, 50.0],
        carteira_credito_caro=[0.0, 60.0],
    )

    assert calcular_indicadores(dados) == {
        "carteira_ativa": 1000.0,
        "taxa_inadimplencia": 5.0,
        "pct_saudavel": 90.0,
        "pct_critica": 10.0,
        "pct_mista": 0.0,
        "pct_credito_caro": 6.0,
        "pct_recuperacao_rapida": 50.0,
        # notas: crédito caro 94, saudável x crítica 90, recuperação 50
        "indicador_geral": 78.0,
    }


def test_recuperacao_rapida_e_o_atraso_inicial_sobre_todo_o_vencido() -> None:
    dados = _grupo(
        vencido_de_15_ate_90_dias=[60.0, 20.0],
        vencido_acima_de_90_dias=[10.0, 10.0],
    )

    assert calcular_recuperacao_rapida(dados) == 80.0


def test_recuperacao_rapida_sem_nada_vencido_nao_se_aplica() -> None:
    assert calcular_recuperacao_rapida(_grupo(carteira_ativa=[100.0])) is None


def test_sem_nada_vencido_o_geral_usa_so_as_outras_notas() -> None:
    indicadores = calcular_indicadores(
        _grupo(
            tipo_divida=["saudavel", "critica"],
            carteira_ativa=[800.0, 200.0],
            carteira_credito_caro=[0.0, 100.0],
        )
    )

    assert indicadores["pct_recuperacao_rapida"] is None
    # notas: crédito caro 90, saudável x crítica 50 + (80 - 20) / 2 = 80
    assert indicadores["indicador_geral"] == 85.0


@pytest.mark.parametrize(
    ("pct_saudavel", "pct_critica", "nota"),
    [(100.0, 0.0, 100.0), (0.0, 100.0, 0.0), (0.0, 0.0, 50.0), (50.0, 50.0, 50.0)],
)
def test_nota_de_divida_saudavel_x_critica(
    pct_saudavel: float, pct_critica: float, nota: float
) -> None:
    indicadores = {"pct_saudavel": pct_saudavel, "pct_critica": pct_critica}

    assert calcular_indicador_geral(indicadores) == nota


def test_geral_sem_nenhuma_nota_devolve_none() -> None:
    assert calcular_indicador_geral({}) is None


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
        "pct_credito_caro": 5.66,
        "pct_recuperacao_rapida": 55.37,  # 526 / (526 + 424)
        "indicador_geral": 75.06,  # (94.34 + 75.47 + 55.37) / 3
    }
    assert resultado["por_regiao"]["norte"] == {
        "carteira_ativa": 200.0,
        "taxa_inadimplencia": 15.0,
        "pct_saudavel": 0.0,
        "pct_critica": 100.0,
        "pct_mista": 0.0,
        "pct_credito_caro": 100.0,
        "pct_recuperacao_rapida": 62.5,  # 50 / (50 + 30)
        "indicador_geral": 20.83,  # (0 + 0 + 62.5) / 3
    }
    assert resultado["por_regiao"]["nordeste"] == {
        "carteira_ativa": 5100.0,
        "taxa_inadimplencia": 7.73,
        "pct_saudavel": 58.82,
        "pct_critica": 1.96,
        "pct_mista": 39.22,
        "pct_credito_caro": 1.96,
        "pct_recuperacao_rapida": 54.71,  # 476 / (476 + 394)
        "indicador_geral": 77.06,  # (98.04 + 78.43 + 54.71) / 3
    }
    assert sorted(resultado["por_estado"]) == ["AC", "BA", "CE"]
    assert resultado["por_estado"]["BA"]["taxa_inadimplencia"] == 11.29
    assert resultado["por_estado"]["CE"]["taxa_inadimplencia"] == 2.2


def test_por_mes_traz_os_indicadores_de_cada_mes_em_ordem(fonte_falsa) -> None:
    por_mes = consultar_indicadores(Filtros(regiao="nordeste"))["por_mes"]

    assert list(por_mes) == ["2026-05-31", "2026-06-30", "2026-07-31"]
    assert por_mes["2026-05-31"]["carteira_ativa"] == 1000.0
    # julho no Nordeste: imobiliário BA + cheque especial BA + consignado CE
    assert por_mes["2026-07-31"]["carteira_ativa"] == 3100.0


def test_por_mes_respeita_o_filtro_de_periodo(fonte_falsa) -> None:
    por_mes = consultar_indicadores(Filtros(meses=2))["por_mes"]

    assert list(por_mes) == ["2026-06-30", "2026-07-31"]


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
        "pct_credito_caro": 6.25,
        "pct_recuperacao_rapida": 56.72,  # 346 / (346 + 264)
        "indicador_geral": 70.99,  # (93.75 + 62.5 + 56.72) / 3
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
