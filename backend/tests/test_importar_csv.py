from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from database.Importar_csv import converter_linha, importar_csv


class CursorFalso:
    def __init__(self, falhar: bool = False) -> None:
        self.comandos = []
        self.lotes = []
        self.falhar = falhar

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, comando: str) -> None:
        self.comandos.append(comando)

    def executemany(self, comando: str, lote: list[tuple]) -> None:
        if self.falhar:
            raise RuntimeError("falha simulada")
        self.lotes.append((comando, lote.copy()))


class ConexaoFalsa:
    def __init__(self, falhar: bool = False) -> None:
        self.cursor_falso = CursorFalso(falhar)
        self.commits = 0
        self.rollbacks = 0

    def cursor(self) -> CursorFalso:
        return self.cursor_falso

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def test_converter_linha_converte_data_operacoes_e_valores_monetarios() -> None:
    resultado = converter_linha(
        {
            "data_base": "2026-01-01",
            "numero_de_operacoes": "42",
            "carteira_ativa": "1234,56",
            "uf": "SP",
        },
        ["data_base", "numero_de_operacoes", "carteira_ativa", "uf"],
        {"carteira_ativa"},
    )

    assert resultado == (date(2026, 1, 1), 42, Decimal("1234.56"), "SP")


def test_importar_csv_substitui_dados_em_uma_transacao(tmp_path: Path) -> None:
    arquivo_csv = tmp_path / "dados.csv"
    arquivo_csv.write_text(
        "data_base;numero_de_operacoes;carteira_ativa;uf\n2026-01-01;42;1234,56;SP\n",
        encoding="utf-8",
    )
    conexao = ConexaoFalsa()

    total = importar_csv(conexao, arquivo_csv)

    assert total == 1
    assert conexao.cursor_falso.comandos == ["DELETE FROM BCB"]
    assert len(conexao.cursor_falso.lotes) == 1
    assert conexao.commits == 1
    assert conexao.rollbacks == 0


def test_importar_csv_reverte_a_transacao_se_a_insercao_falhar(
    tmp_path: Path,
) -> None:
    arquivo_csv = tmp_path / "dados.csv"
    arquivo_csv.write_text(
        "data_base;numero_de_operacoes;carteira_ativa;uf\n2026-01-01;42;1234,56;SP\n",
        encoding="utf-8",
    )
    conexao = ConexaoFalsa(falhar=True)

    with pytest.raises(RuntimeError, match="falha simulada"):
        importar_csv(conexao, arquivo_csv)

    assert conexao.commits == 0
    assert conexao.rollbacks == 1
