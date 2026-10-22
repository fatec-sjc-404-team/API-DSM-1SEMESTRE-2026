import pytest

import dados
from app import app


@pytest.fixture
def cliente():
    return app.test_client()


def test_dados_sem_filtros_devolve_todas_as_linhas(cliente, fonte_falsa) -> None:
    resposta = cliente.get("/api/dados")

    corpo = resposta.get_json()
    assert resposta.status_code == 200
    assert corpo["total_de_linhas"] == 7
    assert corpo["ultima_data_base"] == "2026-07-31"
    assert corpo["dados"][0] == {
        "data_base": "2026-05-31",
        "uf": "BA",
        "tipo_divida": "saudavel",
        "carteira_ativa": 1000.0,
        "carteira_inadimplencia": 50.0,
    }


def test_dados_vem_ordenados_por_mes_uf_e_tipo(cliente, fonte_falsa) -> None:
    linhas = cliente.get("/api/dados").get_json()["dados"]

    chaves = [(l["data_base"], l["uf"], l["tipo_divida"]) for l in linhas]
    assert chaves == sorted(chaves)


def test_dados_filtrados_por_estado(cliente, fonte_falsa) -> None:
    corpo = cliente.get("/api/dados?estado=BA").get_json()

    assert corpo["total_de_linhas"] == 4
    assert {linha["uf"] for linha in corpo["dados"]} == {"BA"}


def test_dados_filtrados_por_regiao(cliente, fonte_falsa) -> None:
    corpo = cliente.get("/api/dados?regiao=norte").get_json()

    assert corpo["total_de_linhas"] == 2
    assert {linha["uf"] for linha in corpo["dados"]} == {"AC"}


def test_dados_filtrados_por_periodo(cliente, fonte_falsa) -> None:
    corpo = cliente.get("/api/dados?periodo=1_mes").get_json()

    assert corpo["total_de_linhas"] == 4
    assert {linha["data_base"] for linha in corpo["dados"]} == {"2026-07-31"}


def test_dados_filtrados_por_tipo_de_divida(cliente, fonte_falsa) -> None:
    corpo = cliente.get("/api/dados?tipoDivida=critica").get_json()

    assert corpo["total_de_linhas"] == 3
    assert {linha["tipo_divida"] for linha in corpo["dados"]} == {"critica"}


def test_dados_com_filtros_combinados(cliente, fonte_falsa) -> None:
    corpo = cliente.get(
        "/api/dados?regiao=nordeste&periodo=2_meses&tipoDivida=saudavel"
    ).get_json()

    assert [(l["data_base"], l["uf"]) for l in corpo["dados"]] == [
        ("2026-06-30", "BA"),
        ("2026-07-31", "BA"),
    ]
    assert corpo["filtros"] == {
        "regiao": "nordeste",
        "estado": None,
        "meses": 2,
        "tipo_divida": "saudavel",
    }


def test_dados_remover_o_filtro_traz_as_linhas_de_volta(cliente, fonte_falsa) -> None:
    com_filtro = cliente.get("/api/dados?estado=BA").get_json()
    sem_filtro = cliente.get("/api/dados?estado=").get_json()

    assert com_filtro["total_de_linhas"] == 4
    assert sem_filtro["total_de_linhas"] == 7


def test_dados_combinacao_sem_resultado_devolve_lista_vazia(
    cliente, fonte_falsa
) -> None:
    resposta = cliente.get("/api/dados?regiao=norte&tipoDivida=saudavel")

    assert resposta.status_code == 200
    assert resposta.get_json()["dados"] == []
    assert resposta.get_json()["total_de_linhas"] == 0


def test_indicadores_sem_filtros(cliente, fonte_falsa) -> None:
    resposta = cliente.get("/api/indicadores")

    corpo = resposta.get_json()
    assert resposta.status_code == 200
    assert corpo["geral"]["taxa_inadimplencia"] == 8.0
    assert sorted(corpo["por_estado"]) == ["AC", "BA", "CE"]
    assert sorted(corpo["por_regiao"]) == ["nordeste", "norte"]


def test_indicadores_com_filtros_combinados(cliente, fonte_falsa) -> None:
    corpo = cliente.get(
        "/api/indicadores?regiao=nordeste&estado=BA&periodo=2_meses&tipoDivida=critica"
    ).get_json()

    assert list(corpo["por_estado"]) == ["BA"]
    assert corpo["geral"]["taxa_inadimplencia"] == 50.0


def test_indicadores_remover_o_filtro_traz_os_dados_de_volta(
    cliente, fonte_falsa
) -> None:
    com_filtro = cliente.get("/api/indicadores?estado=BA").get_json()
    sem_filtro = cliente.get("/api/indicadores?estado=").get_json()

    assert len(com_filtro["por_estado"]) == 1
    assert len(sem_filtro["por_estado"]) == 3


@pytest.mark.parametrize("rota", ["/api/dados", "/api/indicadores"])
def test_filtro_invalido_devolve_erro_400(cliente, fonte_falsa, rota: str) -> None:
    resposta = cliente.get(f"{rota}?regiao=norte&estado=BA")

    assert resposta.status_code == 400
    assert "não pertence à região" in resposta.get_json()["erro"]


@pytest.mark.parametrize("rota", ["/api/dados", "/api/indicadores"])
def test_fonte_de_dados_fora_do_ar_devolve_erro_503(
    cliente, monkeypatch: pytest.MonkeyPatch, rota: str
) -> None:
    def falhar():
        raise dados.DadosIndisponiveis("MySQL fora do ar")

    monkeypatch.setattr(dados, "_ler_fonte", falhar)
    dados.limpar_cache()

    resposta = cliente.get(rota)

    assert resposta.status_code == 503
    assert resposta.get_json()["erro"] == "MySQL fora do ar"
    dados.limpar_cache()


def test_paginas_do_grupo_continuam_abrindo(cliente) -> None:
    for rota in ("/", "/graficos", "/filtros_salvos", "/health"):
        assert cliente.get(rota).status_code == 200
