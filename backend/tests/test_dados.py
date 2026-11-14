from pathlib import Path

import pandas as pd
import pytest

import dados
from dados import (
    DadosIndisponiveis,
    carregar_bcb,
    classificar_tipo_divida,
    consultar_dados,
    dados_filtrados,
    eh_credito_caro,
    ultima_data_base,
)
from filtros import Filtros


@pytest.mark.parametrize(
    ("modalidade", "submodalidade", "esperado"),
    [
        ("Empréstimos", "Cheque especial", "critica"),
        ("Empréstimos", "Cartão de crédito - não migrado", "critica"),
        ("Empréstimos", "Crédito rotativo vinculado a cartão de crédito", "critica"),
        ("Adiantamentos a depositantes", "Adiantamentos a depositantes", "critica"),
        ("Financiamentos imobiliários", "Financiamento habitacional - SFH", "saudavel"),
        ("Financiamentos rurais  (ex-financiamentos rurais e agroindustriais)", "Custeio", "saudavel"),
        ("Empréstimos", "Microcrédito", "saudavel"),
        ("Financiamentos", "Microcrédito", "saudavel"),
        ("Empréstimos", "Crédito pessoal - com consignação em folha de pagam.", "mista"),
        ("Financiamentos", "Aquisição de bens - veículos automotores", "mista"),
        ("Outros créditos", "Cartão de crédito - compra à vista e parcelado lojista", "mista"),
    ],
)  # fmt: skip
def test_classificar_tipo_divida(
    modalidade: str, submodalidade: str, esperado: str
) -> None:
    assert classificar_tipo_divida(modalidade, submodalidade) == esperado


def test_classificar_ignora_maiusculas_e_espacos_repetidos() -> None:
    assert classificar_tipo_divida("EMPRÉSTIMOS", "  Cheque   Especial ") == "critica"


@pytest.mark.parametrize(
    ("submodalidade", "esperado"),
    [
        ("Cheque especial", True),
        ("Crédito rotativo vinculado a cartão de crédito", True),
        ("Cartão de crédito - não migrado", True),
        ("Adiantamentos a depositantes", True),
        ("  CHEQUE   especial ", True),
        # crítica, mas não é crédito caro: parcelamento é consolidação da dívida
        ("Cartão de crédito - compra ou fatura parcelada pela instituição financeira emitente do cartão", False),
        ("Financiamento habitacional - SFH", False),
        ("Crédito pessoal - com consignação em folha de pagam.", False),
    ],
)  # fmt: skip
def test_eh_credito_caro(submodalidade: str, esperado: bool) -> None:
    assert eh_credito_caro(submodalidade) is esperado


def test_carregar_bcb_soma_por_mes_uf_e_tipo_de_divida(fonte_falsa) -> None:
    tabela = carregar_bcb()

    assert tabela.columns.tolist() == [
        "data_base",
        "uf",
        "tipo_divida",
        "carteira_ativa",
        "carteira_inadimplencia",
        "vencido_de_15_ate_90_dias",
        "vencido_acima_de_90_dias",
        "carteira_credito_caro",
    ]
    # BA em jul/2026: imobiliário (saudável) e cheque especial (crítica) separados
    julho_ba = tabela[(tabela["uf"] == "BA") & (tabela["data_base"] == "2026-07-31")]
    assert sorted(julho_ba["tipo_divida"]) == ["critica", "saudavel"]
    assert tabela["carteira_ativa"].sum() == fonte_falsa["carteira_ativa"].sum()
    assert pd.api.types.is_datetime64_any_dtype(tabela["data_base"])


def test_carregar_bcb_separa_a_carteira_de_credito_caro(fonte_falsa) -> None:
    tabela = carregar_bcb()

    # só as 3 linhas de cheque especial (100 cada) são crédito caro
    assert tabela["carteira_credito_caro"].sum() == 300.0
    imobiliario = tabela[tabela["tipo_divida"] == "saudavel"]
    assert imobiliario["carteira_credito_caro"].sum() == 0.0
    assert tabela["vencido_de_15_ate_90_dias"].sum() == 526.0
    assert tabela["vencido_acima_de_90_dias"].sum() == 424.0


def test_ultima_data_base(fonte_falsa) -> None:
    assert ultima_data_base() == pd.Timestamp("2026-07-31")


def test_carregar_bcb_guarda_em_cache_para_nao_ler_a_fonte_toda_vez(
    monkeypatch: pytest.MonkeyPatch, fonte_falsa
) -> None:
    leituras = []

    def ler_contando():
        leituras.append(1)
        return fonte_falsa.copy()

    monkeypatch.setattr(dados, "_ler_fonte", ler_contando)
    dados.limpar_cache()

    carregar_bcb()
    carregar_bcb()
    assert len(leituras) == 1

    dados.limpar_cache()
    carregar_bcb()
    assert len(leituras) == 2


def test_carregar_bcb_le_o_csv_quando_nao_ha_mysql_configurado(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    csv = tmp_path / "dados.csv"
    csv.write_text(
        "data_base;uf;modalidade;submodalidade;carteira_ativa;carteira_inadimplencia;"
        "vencido_de_15_ate_90_dias;vencido_acima_de_90_dias;extra\n"
        "2026-07-31;BA;Empréstimos;Cheque especial;1000,50;100,25;30,00;100,25;x\n"
        "2026-07-31;BA;Empréstimos;Cheque especial;500,00;50,00;10,00;50,00;y\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.setattr(dados, "ARQUIVO_CSV", csv)
    dados.limpar_cache()

    tabela = carregar_bcb()

    assert len(tabela) == 1
    assert tabela.loc[0, "tipo_divida"] == "critica"
    assert tabela.loc[0, "carteira_ativa"] == pytest.approx(1500.50)
    assert tabela.loc[0, "carteira_inadimplencia"] == pytest.approx(150.25)
    assert tabela.loc[0, "vencido_de_15_ate_90_dias"] == pytest.approx(40.0)
    assert tabela.loc[0, "carteira_credito_caro"] == pytest.approx(1500.50)
    dados.limpar_cache()


def test_sem_mysql_e_sem_csv_avisa_que_os_dados_estao_indisponiveis(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.setattr(dados, "ARQUIVO_CSV", tmp_path / "nao-existe.csv")
    dados.limpar_cache()

    with pytest.raises(DadosIndisponiveis, match="DB_USER"):
        carregar_bcb()


def test_mysql_fora_do_ar_avisa_que_os_dados_estao_indisponiveis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DB_USER", "root")
    monkeypatch.setenv("DB_HOST", "127.0.0.1")
    monkeypatch.setenv("DB_PORT", "1")  # nada escuta nessa porta
    dados.limpar_cache()

    with pytest.raises(DadosIndisponiveis, match="conectar ao MySQL"):
        carregar_bcb()


def test_carregar_bcb_normaliza_a_uf(monkeypatch: pytest.MonkeyPatch) -> None:
    bruto = pd.DataFrame(
        {
            "data_base": ["2026-07-31", "2026-07-31"],
            "uf": [" ba ", "BA"],
            "modalidade": ["Empréstimos", "Empréstimos"],
            "submodalidade": ["Cheque especial", "Cheque especial"],
            "carteira_ativa": [100.0, 50.0],
            "carteira_inadimplencia": [10.0, 5.0],
            "vencido_de_15_ate_90_dias": [2.0, 1.0],
            "vencido_acima_de_90_dias": [10.0, 5.0],
        }
    )
    monkeypatch.setattr(dados, "_ler_fonte", lambda: bruto)
    dados.limpar_cache()

    tabela = carregar_bcb()

    assert tabela["uf"].tolist() == ["BA"]
    assert tabela["carteira_ativa"].tolist() == [150.0]
    dados.limpar_cache()


def test_dados_filtrados_aplica_os_filtros_na_tabela(fonte_falsa) -> None:
    tabela = dados_filtrados(Filtros(regiao="nordeste", meses=1, tipo_divida="critica"))

    assert tabela["uf"].tolist() == ["BA"]
    assert tabela["tipo_divida"].tolist() == ["critica"]
    assert tabela["carteira_ativa"].tolist() == [100.0]


def test_dados_filtrados_sem_filtro_devolve_tudo(fonte_falsa) -> None:
    assert len(dados_filtrados(Filtros())) == len(carregar_bcb())


def test_consultar_dados_traz_filtros_total_e_linhas(fonte_falsa) -> None:
    resposta = consultar_dados(Filtros(estado="CE"))

    assert resposta["filtros"]["estado"] == "CE"
    assert resposta["ultima_data_base"] == "2026-07-31"
    assert resposta["total_de_linhas"] == 1
    assert resposta["dados"] == [
        {
            "data_base": "2026-07-31",
            "uf": "CE",
            "tipo_divida": "mista",
            "carteira_ativa": 2000.0,
            "carteira_inadimplencia": 44.0,
        }
    ]
