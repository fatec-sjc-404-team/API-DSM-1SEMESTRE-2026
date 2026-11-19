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


def escrever_csv(caminho: Path, linhas: list[str]) -> Path:
    cabecalho = (
        "data_base;uf;modalidade;submodalidade;carteira_ativa;carteira_inadimplencia;"
        "vencido_de_15_ate_90_dias;vencido_acima_de_90_dias"
    )
    caminho.write_text("\n".join([cabecalho, *linhas]) + "\n", encoding="utf-8")
    return caminho


def test_csv_ignora_negativos_e_valores_invalidos_como_o_mysql(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    csv = escrever_csv(
        tmp_path / "dados.csv",
        [
            "2026-07-31;BA;Empréstimos;Cheque especial;1000,00;100,00;10,00;100,00",
            "2026-07-31;BA;Empréstimos;Cheque especial;-500,00;NA;;-1,00",
        ],
    )
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.setattr(dados, "ARQUIVO_CSV", csv)
    dados.limpar_cache()

    tabela = carregar_bcb()

    assert tabela.loc[0, "carteira_ativa"] == pytest.approx(1000.0)
    assert tabela.loc[0, "carteira_inadimplencia"] == pytest.approx(100.0)
    assert tabela.loc[0, "vencido_acima_de_90_dias"] == pytest.approx(100.0)
    dados.limpar_cache()


def test_linha_sem_modalidade_entra_como_mista_e_nao_some(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    csv = escrever_csv(
        tmp_path / "dados.csv",
        ["2026-07-31;BA;;;300,00;30,00;3,00;30,00"],
    )
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.setattr(dados, "ARQUIVO_CSV", csv)
    dados.limpar_cache()

    tabela = carregar_bcb()

    assert tabela["tipo_divida"].tolist() == ["mista"]
    assert tabela["carteira_ativa"].tolist() == [300.0]
    dados.limpar_cache()


def test_uf_fora_do_norte_nordeste_e_data_invalida_nao_entram(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bruto = pd.DataFrame(
        {
            "data_base": ["2026-07-31", "2026-07-31", "não é data", "2026-07-31"],
            "uf": ["BA", "SP", "BA", None],
            "modalidade": ["Empréstimos"] * 4,
            "submodalidade": ["Cheque especial"] * 4,
            "carteira_ativa": [100.0, 999.0, 999.0, 999.0],
            "carteira_inadimplencia": [10.0, 1.0, 1.0, 1.0],
            "vencido_de_15_ate_90_dias": [1.0, 1.0, 1.0, 1.0],
            "vencido_acima_de_90_dias": [10.0, 1.0, 1.0, 1.0],
        }
    )
    monkeypatch.setattr(dados, "_ler_fonte", lambda: bruto)
    dados.limpar_cache()

    tabela = carregar_bcb()

    assert tabela["uf"].tolist() == ["BA"]
    assert tabela["carteira_ativa"].tolist() == [100.0]
    dados.limpar_cache()


@pytest.mark.parametrize(
    "conteudo",
    ["", "so;uma;coluna\n1;2;3\n", "data_base;uf\n\x00\xff\n"],
)
def test_csv_vazio_ou_quebrado_avisa_que_os_dados_estao_indisponiveis(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, conteudo: str
) -> None:
    csv = tmp_path / "dados.csv"
    csv.write_text(conteudo, encoding="latin-1")
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.setattr(dados, "ARQUIVO_CSV", csv)
    dados.limpar_cache()

    with pytest.raises(DadosIndisponiveis):
        carregar_bcb()


def test_fonte_fora_do_ar_continua_com_os_dados_ja_carregados(
    monkeypatch: pytest.MonkeyPatch, fonte_falsa
) -> None:
    carregar_bcb()
    tempo = [0.0]
    monkeypatch.setattr(dados.time, "monotonic", lambda: tempo[0])
    dados._cache = (0.0, dados._cache[1], dados._cache[2])

    def falhar():
        raise DadosIndisponiveis("MySQL fora do ar")

    monkeypatch.setattr(dados, "_ler_fonte", falhar)
    tempo[0] = dados.SEGUNDOS_DE_CACHE + 1

    tabela = carregar_bcb()

    assert not tabela.empty


def test_cache_le_de_novo_quando_o_csv_muda(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import os

    csv = escrever_csv(
        tmp_path / "dados.csv",
        ["2026-07-31;BA;Empréstimos;Cheque especial;100,00;10,00;1,00;10,00"],
    )
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.setattr(dados, "ARQUIVO_CSV", csv)
    dados.limpar_cache()
    assert carregar_bcb()["carteira_ativa"].tolist() == [100.0]

    escrever_csv(
        csv, ["2026-07-31;BA;Empréstimos;Cheque especial;200,00;10,00;1,00;10,00"]
    )
    os.utime(csv, ns=(1, 1))  # garante outra data de modificação

    assert carregar_bcb()["carteira_ativa"].tolist() == [200.0]
    dados.limpar_cache()


def test_conexao_com_o_mysql_tem_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    import pymysql

    argumentos = {}

    def conectar(**kwargs):
        argumentos.update(kwargs)
        raise pymysql.OperationalError(2003, "fora do ar")

    monkeypatch.setenv("DB_USER", "app")
    monkeypatch.setattr(pymysql, "connect", conectar)
    dados.limpar_cache()

    with pytest.raises(DadosIndisponiveis):
        carregar_bcb()
    assert argumentos["read_timeout"] > 0
    assert argumentos["connect_timeout"] > 0
