import pandas as pd
import pytest
from Tratamento_Dados.Estados import filtrar_norte_nordeste
from Tratamento_Dados.Renda import filtrar_baixa_renda
from Tratamento_Dados.Tipo_Pessoa import filtrar_pessoas_fisicas


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
