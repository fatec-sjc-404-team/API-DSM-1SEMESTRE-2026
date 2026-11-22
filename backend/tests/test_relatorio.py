import re

import pytest

import app as modulo_app
import dados
from app import app
from relatorio import descrever_filtros, gerar_relatorio_pdf


@pytest.fixture
def cliente():
    return app.test_client()


def _contar_paginas(pdf: bytes) -> int:
    # "/Type /Page" é cada página; "/Type /Pages" (o índice) fica de fora pelo \b.
    return len(re.findall(rb"/Type\s*/Page\b", pdf))


def test_relatorio_devolve_pdf_para_download(cliente, fonte_falsa) -> None:
    resposta = cliente.get("/api/relatorio.pdf")

    assert resposta.status_code == 200
    assert resposta.mimetype == "application/pdf"
    assert resposta.data.startswith(b"%PDF")
    assert "attachment" in resposta.headers["Content-Disposition"]
    assert _contar_paginas(resposta.data) == 3


def test_relatorio_aceita_os_mesmos_filtros_da_tela(cliente, fonte_falsa) -> None:
    resposta = cliente.get(
        "/api/relatorio.pdf?regiao=nordeste&estado=BA&periodo=2_meses&tipoDivida=saudavel"
    )

    assert resposta.status_code == 200
    assert resposta.data.startswith(b"%PDF")


def test_relatorio_sem_dados_nos_filtros_gera_so_a_pagina_de_aviso(
    cliente, fonte_falsa
) -> None:
    # O CE só tem crédito consignado (dívida mista), então não sobra nada.
    resposta = cliente.get("/api/relatorio.pdf?estado=CE&tipoDivida=saudavel")

    assert resposta.status_code == 200
    assert _contar_paginas(resposta.data) == 1


def test_relatorio_com_filtro_invalido_devolve_erro_400(cliente, fonte_falsa) -> None:
    resposta = cliente.get("/api/relatorio.pdf?regiao=sul")

    assert resposta.status_code == 400
    assert "Região inválida" in resposta.get_json()["erro"]


def test_relatorio_com_fonte_fora_do_ar_devolve_erro_503(
    cliente, monkeypatch: pytest.MonkeyPatch
) -> None:
    def falhar():
        raise dados.DadosIndisponiveis("MySQL fora do ar")

    monkeypatch.setattr(dados, "_ler_fonte", falhar)
    dados.limpar_cache()

    resposta = cliente.get("/api/relatorio.pdf")

    assert resposta.status_code == 503
    assert resposta.get_json()["erro"] == modulo_app.MENSAGEM_SEM_DADOS
    dados.limpar_cache()


def test_relatorio_aguenta_indicador_sem_dado_no_mes() -> None:
    # pct_recuperacao_rapida é None quando o mês não tem nada vencido.
    indicadores = {
        "filtros": {"regiao": None, "estado": None, "meses": None, "tipo_divida": None},
        "ultima_data_base": "2026-07-31",
        "geral": {"indicador_geral": 75.06, "carteira_ativa": 1234.5, "pct_recuperacao_rapida": None},
        "por_regiao": {},
        "por_estado": {"BA": {"indicador_geral": 70.0}},
        "por_mes": {
            "2026-06-30": {"indicador_geral": 70.0, "pct_recuperacao_rapida": None, "pct_credito_caro": 5.0, "pct_saudavel": 90.0},
            "2026-07-31": {"indicador_geral": 72.0, "pct_recuperacao_rapida": 40.0, "pct_credito_caro": 4.0, "pct_saudavel": 91.0},
        },
    }  # fmt: skip

    assert gerar_relatorio_pdf(indicadores).startswith(b"%PDF")


def test_descrever_filtros_usa_todos_quando_o_filtro_nao_foi_usado() -> None:
    filtros = {"regiao": None, "estado": None, "meses": None, "tipo_divida": None}

    assert descrever_filtros(filtros) == [
        "Região: Todas",
        "Estado: Todos",
        "Período: todo o histórico",
        "Tipo de dívida: Todos",
    ]


def test_descrever_filtros_com_todos_os_filtros() -> None:
    filtros = {
        "regiao": "nordeste",
        "estado": "BA",
        "meses": 6,
        "tipo_divida": "critica",
    }

    assert descrever_filtros(filtros) == [
        "Região: Nordeste",
        "Estado: BA",
        "Período: últimos 6 meses",
        "Tipo de dívida: Crítica",
    ]


def test_relatorio_reaproveita_o_pdf_enquanto_os_dados_nao_mudam(
    cliente, fonte_falsa, monkeypatch: pytest.MonkeyPatch
) -> None:
    geracoes = []

    def gerar_contando(indicadores):
        geracoes.append(1)
        return b"%PDF-1.4 teste"

    monkeypatch.setattr(modulo_app, "gerar_relatorio_pdf", gerar_contando)
    modulo_app._pdfs.clear()

    cliente.get("/api/relatorio.pdf?regiao=norte")
    cliente.get("/api/relatorio.pdf?regiao=norte")
    assert len(geracoes) == 1

    # dados novos na fonte: gera de novo
    dados.limpar_cache()
    cliente.get("/api/relatorio.pdf?regiao=norte")
    assert len(geracoes) == 2
    modulo_app._pdfs.clear()
