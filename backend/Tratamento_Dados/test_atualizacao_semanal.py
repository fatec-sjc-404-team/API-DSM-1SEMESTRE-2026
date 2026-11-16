from datetime import date

from Tratamento_Dados import atualizacao_semanal as atu


def test_dia_fixo(monkeypatch):
    monkeypatch.setattr(atu, "DIA_ATUALIZACAO", 0)
    assert atu.hoje_e_dia_da_atualizacao(date(2026, 11, 16)) is True  # segunda
    assert atu.hoje_e_dia_da_atualizacao(date(2026, 11, 17)) is False  # terça


def test_sucesso_troca_os_dados(tmp_path, monkeypatch):
    dados = tmp_path / "dados.csv"
    dados.write_text("semana anterior")

    def rodar_ok(modulo, entrada=None):
        dados.write_text("semana nova")

    monkeypatch.setattr(atu, "rodar_modulo", rodar_ok)
    fonte = {"modulo": "x", "dados": dados, "entrada": None}

    assert atu.atualizar_fonte("teste", fonte, tmp_path / "backup") is True
    assert dados.read_text() == "semana nova"


def test_falha_mantem_dados_da_semana_anterior(tmp_path, monkeypatch):
    dados = tmp_path / "dados.csv"
    dados.write_text("semana anterior")

    def rodar_com_falha(modulo, entrada=None):
        dados.write_text("arquivo estragado")  # a coleta estraga e depois falha
        raise RuntimeError("API fora do ar")

    monkeypatch.setattr(atu, "rodar_modulo", rodar_com_falha)
    fonte = {"modulo": "x", "dados": dados, "entrada": None}

    assert atu.atualizar_fonte("teste", fonte, tmp_path / "backup") is False
    assert dados.read_text() == "semana anterior"


def test_falha_sem_dados_anteriores_nao_trava(tmp_path, monkeypatch):
    dados = tmp_path / "dados.csv"  # não existe ainda

    def rodar_com_falha(modulo, entrada=None):
        raise RuntimeError("API fora do ar")

    monkeypatch.setattr(atu, "rodar_modulo", rodar_com_falha)
    fonte = {"modulo": "x", "dados": dados, "entrada": None}

    assert atu.atualizar_fonte("teste", fonte, tmp_path / "backup") is False


def test_uma_fonte_falha_e_a_outra_continua(tmp_path, monkeypatch):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("a antigo")
    b.write_text("b antigo")

    def rodar(modulo, entrada=None):
        if modulo == "falha":
            raise RuntimeError("fonte fora do ar")
        b.write_text("b novo")

    fontes = {
        "a": {"modulo": "falha", "dados": a, "entrada": None},
        "b": {"modulo": "ok", "dados": b, "entrada": None},
    }
    monkeypatch.setattr(atu, "rodar_modulo", rodar)
    monkeypatch.setattr(atu, "montar_fontes", lambda ano: fontes)

    resultado = atu.atualizar_tudo(forcar=True, pasta_backup=tmp_path / "backup")

    assert resultado == {"a": False, "b": True}
    assert a.read_text() == "a antigo"
    assert b.read_text() == "b novo"
