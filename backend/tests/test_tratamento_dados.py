import pandas as pd
import pytest
from Tratamento_Dados.csv_pipeline import filtrar_arquivos_csv
from Tratamento_Dados.Estados import filtrar_norte_nordeste
from Tratamento_Dados.Renda import filtrar_baixa_renda
from Tratamento_Dados.Tipo_Pessoa import filtrar_pessoas_fisicas
from Tratamento_Dados.Validar_Resultado import validar_etapa


def test_filtrar_norte_nordeste_normaliza_uf_e_preserva_colunas() -> None:
    dados = pd.DataFrame(
        {
            "uf": [" AC ", "sp", "TO", None],
            "cliente": ["PF", "PJ", "PF", "PJ"],
            "carteira_ativa": [100, 200, 300, 400],
        }
    )

    resultado = filtrar_norte_nordeste(dados)

    assert resultado["uf"].tolist() == [" AC ", "TO"]
    assert resultado.columns.tolist() == dados.columns.tolist()
    assert len(dados) == 4


def test_filtrar_norte_nordeste_exige_coluna_uf() -> None:
    with pytest.raises(ValueError, match="coluna chamada 'uf'"):
        filtrar_norte_nordeste(pd.DataFrame({"estado": ["SP"]}))


def test_filtrar_pessoas_fisicas_normaliza_cliente_e_preserva_colunas() -> None:
    dados = pd.DataFrame(
        {
            "uf": ["AC", "BA", "SP", "TO"],
            "cliente": [" PF ", "PJ", " pf", None],
            "carteira_ativa": [100, 200, 300, 400],
        }
    )

    resultado = filtrar_pessoas_fisicas(dados)

    assert resultado["cliente"].tolist() == [" PF ", " pf"]
    assert resultado.columns.tolist() == dados.columns.tolist()
    assert len(dados) == 4


def test_filtrar_pessoas_fisicas_exige_coluna_cliente() -> None:
    with pytest.raises(ValueError, match="coluna chamada 'cliente'"):
        filtrar_pessoas_fisicas(pd.DataFrame({"tipo": ["PF"]}))


def test_filtrar_baixa_renda_mantem_tres_faixas_e_preserva_colunas() -> None:
    dados = pd.DataFrame(
        {
            "porte": [
                "Sem rendimento",
                "Até 1 salário mínimo",
                "Mais de 1 a 2 salários mínimos",
                "Mais de 2 a 3 salários mínimos",
                " Até 1 salário mínimo ",
                None,
            ],
            "cliente": ["PF"] * 6,
            "carteira_ativa": [100, 200, 300, 400, 500, 600],
        }
    )

    resultado = filtrar_baixa_renda(dados)

    assert resultado.index.tolist() == [0, 1, 2, 4]
    assert resultado.columns.tolist() == dados.columns.tolist()
    assert len(dados) == 6


def test_filtrar_baixa_renda_exige_coluna_porte() -> None:
    with pytest.raises(ValueError, match="coluna chamada 'porte'"):
        filtrar_baixa_renda(pd.DataFrame({"renda": ["PF"]}))


def test_combina_csvs_mantendo_dados_e_interpretando_decimais(tmp_path) -> None:
    primeiro = tmp_path / "mes_1.csv"
    segundo = tmp_path / "mes_2.csv"
    saida = tmp_path / "saida.csv"
    primeiro.write_text("data_base;uf;carteira_ativa\n2026-01-31;AC;123,45\n")
    segundo.write_text("data_base;uf;carteira_ativa\n2026-02-28;PA;678,90\n")

    linhas = filtrar_arquivos_csv(
        [segundo, primeiro],
        saida,
        lambda lote: lote,
    )
    resultado = pd.read_csv(saida, sep=";", decimal=",")

    assert linhas == 2
    assert resultado["data_base"].tolist() == ["2026-01-31", "2026-02-28"]
    assert resultado["carteira_ativa"].tolist() == [123.45, 678.90]


def test_combinar_csvs_rejeita_esquemas_diferentes(tmp_path) -> None:
    primeiro = tmp_path / "mes_1.csv"
    segundo = tmp_path / "mes_2.csv"
    primeiro.write_text("uf;cliente\nAC;PF\n")
    segundo.write_text("cliente;uf\nPF;AC\n")

    with pytest.raises(ValueError, match="colunas diferentes"):
        filtrar_arquivos_csv(
            [primeiro, segundo], tmp_path / "saida.csv", lambda lote: lote
        )


def test_validador_verifica_pf_em_todos_os_lotes(tmp_path, monkeypatch) -> None:
    import Tratamento_Dados.Validar_Resultado as validador

    caminho = tmp_path / "pessoas.csv"
    caminho.write_text("uf;cliente;porte\nAC;PJ;Sem rendimento\nPA;PF;Sem rendimento\n")
    monkeypatch.setattr(validador, "TAMANHO_LOTE", 1)

    assert not validar_etapa("teste", caminho, True, False)
