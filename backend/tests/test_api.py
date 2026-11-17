from unittest.mock import MagicMock

import pytest

import app as modulo_app
import dados
import filtros_salvos as modulo_filtros_salvos
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


def test_listar_filtros_salvos_consulta_a_persistencia(cliente, monkeypatch) -> None:
    filtros = [
        {
            "id": 7,
            "nome": "Regiao Norte",
            "regiao": "norte",
            "estado": "AM",
            "periodo": 6,
            "tipo_divida": "critica",
            "criado_em": "2026-11-14T12:00:00",
        }
    ]
    monkeypatch.setattr(modulo_app, "listar_filtros", lambda: filtros)

    resposta = cliente.get("/api/filtros-salvos")

    assert resposta.status_code == 200
    assert resposta.get_json()["filtros"] == filtros


def test_salvar_filtro_envia_composicao_nomeada_e_ignora_campos_nao_suportados(
    cliente, monkeypatch
) -> None:
    persistido = {}

    def salvar(filtro):
        persistido.update(filtro)
        return 42

    monkeypatch.setattr(modulo_app, "salvar_filtro", salvar)
    resposta = cliente.post(
        "/api/filtros-salvos",
        json={
            "nome": "  Regiao Norte - Debito Critico  ",
            "regiao": "norte",
            "estado": "am",
            "periodo": 6,
            "tipo_divida": "critica",
            "prazo": "90 dias",
            "apostas": True,
        },
    )

    assert resposta.status_code == 201
    assert resposta.get_json()["id"] == 42
    assert persistido == {
        "nome": "Regiao Norte - Debito Critico",
        "regiao": "norte",
        "estado": "AM",
        "periodo": 6,
        "tipo_divida": "critica",
    }


def test_salvar_filtro_mantem_null_para_todos(cliente, monkeypatch) -> None:
    persistido = {}
    monkeypatch.setattr(
        modulo_app,
        "salvar_filtro",
        lambda filtro: persistido.update(filtro) or 43,
    )

    resposta = cliente.post(
        "/api/filtros-salvos",
        json={
            "nome": "Sem filtros opcionais",
            "regiao": None,
            "estado": None,
            "periodo": 12,
            "tipo_divida": None,
        },
    )

    assert resposta.status_code == 201
    assert persistido == {
        "nome": "Sem filtros opcionais",
        "regiao": None,
        "estado": None,
        "periodo": 12,
        "tipo_divida": None,
    }


@pytest.mark.parametrize(
    "dados",
    [
        {"nome": "", "periodo": 1},
        {"nome": "x" * 101, "periodo": 1},
        {"nome": "Sem período"},
        {"nome": "Período inválido", "periodo": 13},
    ],
)
def test_salvar_filtro_rejeita_dados_invalidos(cliente, dados) -> None:
    resposta = cliente.post("/api/filtros-salvos", json=dados)

    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()


def test_renomear_filtro_salvo(cliente, monkeypatch) -> None:
    renomeado = {}

    def renomear(filtro_id, nome):
        renomeado.update(id=filtro_id, nome=nome)
        return True

    monkeypatch.setattr(modulo_app, "renomear_filtro", renomear)
    resposta = cliente.patch(
        "/api/filtros-salvos/42",
        json={"nome": "  Meu filtro atualizado  "},
    )

    assert resposta.status_code == 200
    assert renomeado == {"id": 42, "nome": "Meu filtro atualizado"}


def test_renomear_filtro_salvo_rejeita_nome_invalido(cliente, monkeypatch) -> None:
    monkeypatch.setattr(
        modulo_app,
        "renomear_filtro",
        lambda *_: pytest.fail("Não deve chamar o banco com um nome inválido."),
    )

    resposta = cliente.patch("/api/filtros-salvos/42", json={"nome": " "})

    assert resposta.status_code == 400
    assert "nome" in resposta.get_json()["erro"].lower()


def test_renomear_filtro_salvo_inexistente(cliente, monkeypatch) -> None:
    monkeypatch.setattr(modulo_app, "renomear_filtro", lambda *_: False)

    resposta = cliente.patch(
        "/api/filtros-salvos/42",
        json={"nome": "Filtro atualizado"},
    )

    assert resposta.status_code == 404


def test_excluir_filtro_salvo(cliente, monkeypatch) -> None:
    excluido = {}

    def excluir(filtro_id):
        excluido["id"] = filtro_id
        return True

    monkeypatch.setattr(modulo_app, "excluir_filtro", excluir)
    resposta = cliente.delete("/api/filtros-salvos/42")

    assert resposta.status_code == 200
    assert excluido == {"id": 42}


def test_excluir_filtro_salvo_inexistente(cliente, monkeypatch) -> None:
    monkeypatch.setattr(modulo_app, "excluir_filtro", lambda *_: False)

    resposta = cliente.delete("/api/filtros-salvos/42")

    assert resposta.status_code == 404


def test_renomear_filtro_atualiza_e_confirma_transacao(monkeypatch) -> None:
    cursor = MagicMock()
    cursor.__enter__.return_value = cursor
    cursor.rowcount = 1
    conexao = MagicMock()
    conexao.cursor.return_value = cursor
    monkeypatch.setattr(modulo_filtros_salvos, "_conectar", lambda: conexao)

    assert modulo_filtros_salvos.renomear_filtro(42, "Novo nome")

    cursor.execute.assert_called_once_with(
        "UPDATE filtros_salvos SET nome = %s WHERE id = %s",
        ("Novo nome", 42),
    )
    conexao.commit.assert_called_once()


def test_renomear_filtro_existente_com_mesmo_nome_nao_vira_404(monkeypatch) -> None:
    cursor = MagicMock()
    cursor.__enter__.return_value = cursor
    cursor.rowcount = 0
    cursor.fetchone.return_value = {"id": 42}
    conexao = MagicMock()
    conexao.cursor.return_value = cursor
    monkeypatch.setattr(modulo_filtros_salvos, "_conectar", lambda: conexao)

    assert modulo_filtros_salvos.renomear_filtro(42, "Mesmo nome")
    assert cursor.execute.call_count == 2
    conexao.commit.assert_called_once()


def test_excluir_filtro_remove_e_confirma_transacao(monkeypatch) -> None:
    cursor = MagicMock()
    cursor.__enter__.return_value = cursor
    cursor.rowcount = 1
    conexao = MagicMock()
    conexao.cursor.return_value = cursor
    monkeypatch.setattr(modulo_filtros_salvos, "_conectar", lambda: conexao)

    assert modulo_filtros_salvos.excluir_filtro(42)

    cursor.execute.assert_called_once_with(
        "DELETE FROM filtros_salvos WHERE id = %s",
        (42,),
    )
    conexao.commit.assert_called_once()


def test_pagina_inicio_renderiza_mapa_e_elementos_de_indicadores(cliente) -> None:
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    html = resposta.get_data(as_text=True)

    assert 'id="filtro-regiao"' in html
    assert 'id="filtro-estado"' in html
    assert 'id="valor-potencial"' in html
    assert 'id="btn-limpar-estado"' in html
    assert "mapa-brasil-svg" in html
    assert 'id="mapa-tooltip"' in html
    assert 'id="regiao-norte"' in html
    assert 'id="regiao-nordeste"' in html
    assert 'id="secao-estados"' in html
    assert "potencial-credito.js" in html


def test_elementos_responsivos_e_menu_expansivo_presentes(cliente) -> None:
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    html = resposta.get_data(as_text=True)

    assert "mobile-nav-bar" in html
    assert 'id="btn-menu-mobile"' in html
    assert 'id="sidebar-backdrop"' in html
    assert 'id="btn-toggle-indicators"' in html
    assert 'id="cards-indicadores"' in html
    assert 'id="btn-toggle-estados"' in html
    assert 'id="conteudo-estados"' in html
