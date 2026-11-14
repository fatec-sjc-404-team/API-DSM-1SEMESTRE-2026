import pandas as pd
import pytest

import dados

# Linhas no formato da tabela BCB (somadas por mês, UF, modalidade e submodalidade).
# Os números são pensados para dar taxas fáceis de conferir à mão.
# Como no BCB, o vencido acima de 90 dias é igual à carteira inadimplente.
LINHAS_BCB = [
    # data_base, uf, modalidade, submodalidade, carteira_ativa, carteira_inadimplencia,
    # vencido_de_15_ate_90_dias, vencido_acima_de_90_dias
    ("2026-05-31", "BA", "Financiamentos imobiliários", "Financiamento habitacional - SFH", 1000, 50, 50, 50),
    ("2026-06-30", "BA", "Financiamentos imobiliários", "Financiamento habitacional - SFH", 1000, 100, 100, 100),
    ("2026-07-31", "BA", "Financiamentos imobiliários", "Financiamento habitacional - SFH", 1000, 150, 150, 150),
    ("2026-07-31", "BA", "Empréstimos", "Cheque especial", 100, 50, 0, 50),
    ("2026-07-31", "CE", "Empréstimos", "Crédito pessoal - com consignação em folha de pagam.", 2000, 44, 176, 44),
    ("2026-07-31", "AC", "Empréstimos", "Cheque especial", 100, 20, 20, 20),
    ("2026-06-30", "AC", "Empréstimos", "Cheque especial", 100, 10, 30, 10),
]  # fmt: skip

COLUNAS_BCB = [
    "data_base",
    "uf",
    "modalidade",
    "submodalidade",
    "carteira_ativa",
    "carteira_inadimplencia",
    "vencido_de_15_ate_90_dias",
    "vencido_acima_de_90_dias",
]


@pytest.fixture
def fonte_falsa(monkeypatch: pytest.MonkeyPatch) -> pd.DataFrame:
    """Faz o código ler LINHAS_BCB em vez do MySQL ou do CSV."""
    tabela = pd.DataFrame(LINHAS_BCB, columns=COLUNAS_BCB)
    monkeypatch.setattr(dados, "_ler_fonte", lambda: tabela.copy())
    dados.limpar_cache()
    yield tabela
    dados.limpar_cache()
