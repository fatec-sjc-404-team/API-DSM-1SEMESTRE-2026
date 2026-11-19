import subprocess
from datetime import date, datetime

import pytest

from Tratamento_Dados import atualizacao_semanal as atu
from Tratamento_Dados import coleta_bcb


def test_dia_fixo(monkeypatch):
    monkeypatch.setattr(atu, "DIA_ATUALIZACAO", 0)
    semana_passada = date(2026, 11, 10)
    assert atu.deve_atualizar(date(2026, 11, 16), semana_passada) is True  # segunda
    assert atu.deve_atualizar(date(2026, 11, 17), date(2026, 11, 16)) is False  # terça


def test_nao_atualiza_duas_vezes_no_mesmo_dia():
    assert atu.deve_atualizar(date(2026, 11, 16), date(2026, 11, 16)) is False


def test_sem_atualizacao_anterior_atualiza_na_hora():
    assert atu.deve_atualizar(date(2026, 11, 18), None) is True


def test_atualizacao_atrasada_roda_fora_do_dia_fixo(monkeypatch):
    monkeypatch.setattr(atu, "DIA_ATUALIZACAO", 0)
    # a segunda (16/11) foi perdida; na quarta já faz uma semana
    assert atu.deve_atualizar(date(2026, 11, 18), date(2026, 11, 9)) is True
    assert atu.deve_atualizar(date(2026, 11, 18), date(2026, 11, 16)) is False


def fonte_de_teste(dados, atualizar):
    return {"atualizar": atualizar, "dados": [dados]}


def test_sucesso_troca_os_dados(tmp_path):
    dados = tmp_path / "dados.csv"
    dados.write_text("semana anterior")

    fonte = fonte_de_teste(dados, lambda: dados.write_text("semana nova"))

    assert atu.atualizar_fonte("teste", fonte, tmp_path / "backup") is True
    assert dados.read_text() == "semana nova"


def test_falha_mantem_dados_da_semana_anterior(tmp_path):
    dados = tmp_path / "dados.csv"
    dados.write_text("semana anterior")

    def atualizar_com_falha():
        dados.write_text("arquivo estragado")  # a coleta estraga e depois falha
        raise RuntimeError("API fora do ar")

    fonte = fonte_de_teste(dados, atualizar_com_falha)

    assert atu.atualizar_fonte("teste", fonte, tmp_path / "backup") is False
    assert dados.read_text() == "semana anterior"


def test_falha_sem_dados_anteriores_nao_trava(tmp_path):
    dados = tmp_path / "dados.csv"  # não existe ainda

    def atualizar_com_falha():
        raise RuntimeError("API fora do ar")

    fonte = fonte_de_teste(dados, atualizar_com_falha)

    assert atu.atualizar_fonte("teste", fonte, tmp_path / "backup") is False


def test_uma_fonte_falha_e_a_outra_continua(tmp_path, monkeypatch):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("a antigo")
    b.write_text("b antigo")

    def falhar():
        raise RuntimeError("fonte fora do ar")

    fontes = {
        "a": fonte_de_teste(a, falhar),
        "b": fonte_de_teste(b, lambda: b.write_text("b novo")),
    }
    monkeypatch.setattr(atu, "montar_fontes", lambda ano: fontes)
    marcador = tmp_path / "ultima.txt"

    resultado = atu.atualizar_tudo(
        forcar=True, pasta_backup=tmp_path / "backup", marcador=marcador
    )

    assert resultado == {"a": False, "b": True}
    assert a.read_text() == "a antigo"
    assert b.read_text() == "b novo"
    # com falha não marca como atualizado, para tentar de novo depois
    assert not marcador.exists()


def test_sucesso_grava_a_data_da_atualizacao(tmp_path, monkeypatch):
    dados = tmp_path / "dados.csv"
    fontes = {"a": fonte_de_teste(dados, lambda: dados.write_text("novo"))}
    monkeypatch.setattr(atu, "montar_fontes", lambda ano: fontes)
    marcador = tmp_path / "ultima.txt"

    resultado = atu.atualizar_tudo(
        hoje=date(2026, 11, 16), pasta_backup=tmp_path / "backup", marcador=marcador
    )

    assert resultado == {"a": True}
    assert atu.ler_ultima_atualizacao(marcador).date() == date.today()


def test_fora_de_hora_nao_roda_nada(tmp_path, monkeypatch):
    marcador = tmp_path / "ultima.txt"
    atu.gravar_ultima_atualizacao(marcador, datetime(2026, 11, 16, 3, 0))
    monkeypatch.setattr(
        atu, "montar_fontes", lambda ano: pytest.fail("não devia rodar")
    )

    assert atu.atualizar_tudo(hoje=date(2026, 11, 17), marcador=marcador) == {}


def test_atualizar_bcb_roda_coleta_tratamento_e_importacao(monkeypatch):
    chamados = []
    monkeypatch.setattr(
        atu, "rodar_modulo", lambda modulo, argumentos=(): chamados.append(modulo)
    )
    monkeypatch.setenv("DB_USER", "app")

    atu.atualizar_bcb(2026)

    assert chamados == [
        atu.MODULO_COLETA,
        *atu.ETAPAS_TRATAMENTO,
        atu.MODULO_IMPORTACAO,
    ]


def test_atualizar_bcb_sem_mysql_nao_importa(monkeypatch):
    chamados = []
    monkeypatch.setattr(
        atu, "rodar_modulo", lambda modulo, argumentos=(): chamados.append(modulo)
    )
    monkeypatch.delenv("DB_USER", raising=False)

    atu.atualizar_bcb(2026)

    assert atu.MODULO_IMPORTACAO not in chamados


def test_etapa_com_erro_interrompe_a_atualizacao(monkeypatch):
    chamados = []

    def rodar(modulo, argumentos=()):
        chamados.append(modulo)
        if modulo == "Tratamento_Dados.Validar_Resultado":
            raise subprocess.CalledProcessError(1, modulo)

    monkeypatch.setattr(atu, "rodar_modulo", rodar)
    monkeypatch.setenv("DB_USER", "app")

    with pytest.raises(subprocess.CalledProcessError):
        atu.atualizar_bcb(2026)
    assert atu.MODULO_IMPORTACAO not in chamados


def test_ano_ainda_nao_publicado_baixa_o_anterior(monkeypatch):
    anos = []

    def rodar(modulo, argumentos=()):
        anos.append(argumentos[-1])
        if argumentos[-1] == "2027":
            raise subprocess.CalledProcessError(atu.CODIGO_ANO_SEM_ARQUIVO, modulo)

    monkeypatch.setattr(atu, "rodar_modulo", rodar)

    atu.coletar_bcb(2027)

    assert anos == ["2027", "2026"]


def test_erro_de_rede_na_coleta_nao_tenta_outro_ano(monkeypatch):
    def rodar(modulo, argumentos=()):
        raise subprocess.CalledProcessError(1, modulo)

    monkeypatch.setattr(atu, "rodar_modulo", rodar)

    with pytest.raises(subprocess.CalledProcessError):
        atu.coletar_bcb(2027)


def test_codigo_de_ano_sem_arquivo_e_o_mesmo_da_coleta():
    assert atu.CODIGO_ANO_SEM_ARQUIVO == coleta_bcb.SAIDA_ANO_SEM_ARQUIVO


def test_coleta_com_erro_sai_com_codigo_de_erro(monkeypatch):
    def sem_arquivo(ano):
        raise FileNotFoundError("O BCB não tem arquivo para o ano 2027.")

    monkeypatch.setattr(coleta_bcb, "baixar_zip", sem_arquivo)
    assert coleta_bcb.main(["--ano", "2027"]) == coleta_bcb.SAIDA_ANO_SEM_ARQUIVO

    assert coleta_bcb.main(["--ano", "abc"]) == coleta_bcb.SAIDA_ERRO


def test_main_devolve_erro_quando_alguma_fonte_falha(monkeypatch):
    monkeypatch.setattr(atu, "atualizar_tudo", lambda forcar: {"bcb": False})
    monkeypatch.setattr("sys.argv", ["atualizacao_semanal"])
    assert atu.main() == 1

    monkeypatch.setattr(atu, "atualizar_tudo", lambda forcar: {})
    assert atu.main() == 0
