import pandas as pd
import pytest

import dados

# Linhas no formato da tabela BCB (somadas por mês, UF, modalidade e submodalidade).
# Os números são pensados para dar taxas fáceis de conferir à mão.
LINHAS_BCB = [
    # data_base, uf, modalidade, submodalidade, carteira_ativa, carteira_inadimplencia
    ("2026-05-31", "BA", "Financiamentos imobiliários", "Financiamento habitacional - SFH", 1000, 50),
    ("2026-06-30", "BA", "Financiamentos imobiliários", "Financiamento habitacional - SFH", 1000, 100),
    ("2026-07-31", "BA", "Financiamentos imobiliários", "Financiamento habitacional - SFH", 1000, 150),
    ("2026-07-31", "BA", "Empréstimos", "Cheque especial", 100, 50),
    ("2026-07-31", "CE", "Empréstimos", "Crédito pessoal - com consignação em folha de pagam.", 2000, 44),
    ("2026-07-31", "AC", "Empréstimos", "Cheque especial", 100, 20),
    ("2026-06-30", "AC", "Empréstimos", "Cheque especial", 100, 10),
]  # fmt: skip

COLUNAS_BCB = [
    "data_base",
    "uf",
    "modalidade",
    "submodalidade",
    "carteira_ativa",
    "carteira_inadimplencia",
]


@pytest.fixture
def fonte_falsa(monkeypatch: pytest.MonkeyPatch) -> pd.DataFrame:
    """Faz o código ler LINHAS_BCB em vez do MySQL ou do CSV."""
    tabela = pd.DataFrame(LINHAS_BCB, columns=COLUNAS_BCB)
    monkeypatch.setattr(dados, "_ler_fonte", lambda: tabela.copy())
    dados.limpar_cache()
    yield tabela
    dados.limpar_cache()
