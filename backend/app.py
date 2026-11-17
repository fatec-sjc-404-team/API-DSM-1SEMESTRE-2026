import os
from pathlib import Path

import pymysql
from flasgger import Swagger
from flask import Flask, Response, jsonify, render_template, request

from dados import DadosIndisponiveis, consultar_dados
from filtros import ler_filtros
from filtros_salvos import (
    excluir_filtro,
    listar_filtros,
    renomear_filtro,
    salvar_filtro,
    validar_filtro,
    validar_nome_filtro,
)
from indicadores import consultar_indicadores
from relatorio import gerar_relatorio_pdf

app = Flask(__name__)

# Gera a documentação Swagger a partir das docstrings das rotas (acessível em /apidocs)
Swagger(app)


@app.get("/")
def inicio():
    """Renderiza a página principal.
    tags:
      - Páginas
    responses:
      200:
        description: Página HTML carregada com sucesso
    """
    return render_template("index.html")


@app.get("/graficos")
def graficos():
    return render_template("graficos.html")


def _consultar(montar_resposta):
    """Lê os filtros da URL e devolve a resposta (400 se inválidos, 503 sem dados)."""
    try:
        filtros = ler_filtros(request.args)
    except ValueError as erro:
        return jsonify(erro=str(erro)), 400

    try:
        return jsonify(montar_resposta(filtros))
    except DadosIndisponiveis as erro:
        return jsonify(erro=str(erro)), 503


@app.get("/api/dados")
def api_dados():
    """Devolve os dados do BCB só com as linhas que atendem aos filtros.
    As linhas vêm somadas por mês (data_base), UF e tipo de dívida.
    ---
    tags:
      - Filtros
    parameters:
      - name: regiao
        in: query
        type: string
        enum: [todos, norte, nordeste]
        description: Região dos dados
      - name: estado
        in: query
        type: string
        description: Sigla da UF (ex. BA). Precisa pertencer à região escolhida
      - name: periodo
        in: query
        type: string
        description: Últimos meses, de 1_mes até 12_meses
        example: 6_meses
      - name: tipoDivida
        in: query
        type: string
        enum: [todos, saudavel, critica, mista]
        description: Tipo de dívida
    responses:
      200:
        description: Linhas que atendem aos filtros
        schema:
          type: object
          properties:
            filtros:
              type: object
              description: Filtros que foram aplicados (null = não usado)
            ultima_data_base:
              type: string
              example: "2026-07-31"
            total_de_linhas:
              type: integer
            dados:
              type: array
              items:
                type: object
                properties:
                  data_base:
                    type: string
                    example: "2026-07-31"
                  uf:
                    type: string
                    example: BA
                  tipo_divida:
                    type: string
                    enum: [saudavel, critica, mista]
                  carteira_ativa:
                    type: number
                  carteira_inadimplencia:
                    type: number
      400:
        description: Algum filtro tem valor inválido
        schema:
          type: object
          properties:
            erro:
              type: string
      503:
        description: A fonte dos dados (MySQL ou CSV) não está disponível
        schema:
          type: object
          properties:
            erro:
              type: string
    """
    return _consultar(consultar_dados)


@app.get("/api/indicadores")
def api_indicadores():
    """Devolve os indicadores calculados só com os dados que atendem aos filtros.
    Vêm o resultado geral, por região (norte, nordeste), por estado e por mês.
    ---
    tags:
      - Filtros
    parameters:
      - name: regiao
        in: query
        type: string
        enum: [todos, norte, nordeste]
        description: Região dos dados
      - name: estado
        in: query
        type: string
        description: Sigla da UF (ex. BA). Precisa pertencer à região escolhida
      - name: periodo
        in: query
        type: string
        description: Últimos meses, de 1_mes até 12_meses
        example: 6_meses
      - name: tipoDivida
        in: query
        type: string
        enum: [todos, saudavel, critica, mista]
        description: Tipo de dívida
    responses:
      200:
        description: >
          Indicadores de cada grupo. taxa_inadimplencia e pct_* são porcentagens;
          indicador_geral é uma nota de 0 a 100 (maior é melhor).
          Grupos sem carteira ativa não aparecem.
          Regras em docs/pesquisa/calculo-dos-indicadores.md.
        schema:
          type: object
          properties:
            filtros:
              type: object
              description: Filtros que foram aplicados (null = não usado)
            ultima_data_base:
              type: string
              example: "2026-07-31"
            geral:
              type: object
              properties:
                carteira_ativa:
                  type: number
                taxa_inadimplencia:
                  type: number
                  example: 8.24
                pct_saudavel:
                  type: number
                pct_critica:
                  type: number
                pct_mista:
                  type: number
                pct_credito_caro:
                  type: number
                  description: Parte da carteira ativa em rotativo do cartão e cheque especial
                pct_recuperacao_rapida:
                  type: number
                  x-nullable: true
                  description: >
                    Parte da carteira vencida no atraso inicial (15 a 90 dias).
                    null quando não há nada vencido
                indicador_geral:
                  type: number
                  x-nullable: true
                  example: 75.06
                  description: Nota de 0 a 100 que junta os indicadores menores
            por_regiao:
              type: object
              description: Mesmos indicadores de "geral", uma chave por região
            por_estado:
              type: object
              description: Mesmos indicadores de "geral", uma chave por UF
            por_mes:
              type: object
              description: >
                Mesmos indicadores de "geral", uma chave por mês (data_base,
                ex. "2026-07-31"), em ordem. Usado no gráfico de evolução
      400:
        description: Algum filtro tem valor inválido
        schema:
          type: object
          properties:
            erro:
              type: string
      503:
        description: A fonte dos dados (MySQL ou CSV) não está disponível
        schema:
          type: object
          properties:
            erro:
              type: string
    """
    return _consultar(consultar_indicadores)


@app.get("/api/relatorio.pdf")
def api_relatorio_pdf():
    """Baixa um relatório em PDF com os indicadores e gráficos dos filtros aplicados.
    ---
    tags:
      - Relatório
    produces:
      - application/pdf
    parameters:
      - name: regiao
        in: query
        type: string
        enum: [todos, norte, nordeste]
        description: Região dos dados
      - name: estado
        in: query
        type: string
        description: Sigla da UF (ex. BA). Precisa pertencer à região escolhida
      - name: periodo
        in: query
        type: string
        description: Últimos meses, de 1_mes até 12_meses
        example: 6_meses
      - name: tipoDivida
        in: query
        type: string
        enum: [todos, saudavel, critica, mista]
        description: Tipo de dívida
    responses:
      200:
        description: Arquivo PDF do relatório
      400:
        description: Algum filtro tem valor inválido
      503:
        description: A fonte dos dados (MySQL ou CSV) não está disponível
    """
    try:
        filtros = ler_filtros(request.args)
    except ValueError as erro:
        return jsonify(erro=str(erro)), 400

    try:
        indicadores = consultar_indicadores(filtros)
    except DadosIndisponiveis as erro:
        return jsonify(erro=str(erro)), 503

    return Response(
        gerar_relatorio_pdf(indicadores),
        mimetype="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="relatorio-potencial-credito.pdf"'
        },
    )


@app.get("/filtros_salvos")
def filtros_salvos():
    return render_template("filtros_salvos.html")


@app.get("/api/filtros-salvos")
def api_listar_filtros_salvos():
    try:
        return jsonify(filtros=listar_filtros())
    except (RuntimeError, pymysql.MySQLError):
        app.logger.exception("Não foi possível acessar o banco MySQL de filtros.")
        return jsonify(erro="Não foi possível acessar os filtros salvos."), 503


@app.post("/api/filtros-salvos")
def api_salvar_filtro():
    try:
        filtro = validar_filtro(request.get_json(silent=True))
        filtro_id = salvar_filtro(filtro)
    except (TypeError, ValueError) as erro:
        return jsonify(erro=str(erro)), 400
    except (RuntimeError, pymysql.MySQLError):
        app.logger.exception("Não foi possível salvar o filtro no banco MySQL.")
        return jsonify(erro="Não foi possível salvar o filtro."), 503
    return jsonify(id=filtro_id, mensagem="Filtro salvo com sucesso."), 201


@app.patch("/api/filtros-salvos/<int:filtro_id>")
def api_renomear_filtro(filtro_id):
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify(erro="Envie o nome do filtro em formato JSON."), 400

    try:
        nome = validar_nome_filtro(dados.get("nome"))
        alterado = renomear_filtro(filtro_id, nome)
    except ValueError as erro:
        return jsonify(erro=str(erro)), 400
    except (RuntimeError, pymysql.MySQLError):
        app.logger.exception("Não foi possível renomear o filtro no banco MySQL.")
        return jsonify(erro="Não foi possível renomear o filtro."), 503

    if not alterado:
        return jsonify(erro="Filtro não encontrado."), 404
    return jsonify(mensagem="Filtro renomeado com sucesso.")


@app.delete("/api/filtros-salvos/<int:filtro_id>")
def api_excluir_filtro(filtro_id):
    try:
        excluido = excluir_filtro(filtro_id)
    except (RuntimeError, pymysql.MySQLError):
        app.logger.exception("Não foi possível excluir o filtro no banco MySQL.")
        return jsonify(erro="Não foi possível excluir o filtro."), 503

    if not excluido:
        return jsonify(erro="Filtro não encontrado."), 404
    return jsonify(mensagem="Filtro excluído com sucesso.")


@app.get("/health")
def health():
    """Verifica se a API está no ar.
    ---
    tags:
      - Status
    responses:
      200:
        description: API funcionando
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
    """
    return jsonify(status="ok")


@app.get("/hello-world")
def hello_world():
    """Retorna uma mensagem de boas-vindas.
    ---
    tags:
      - Exemplo
    responses:
      200:
        description: Mensagem de hello world
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Hello, World!
    """
    return jsonify(mensagem="Hello, World!")


ARQUIVO_ENV = Path(__file__).with_name(".env")


def carregar_env(caminho=ARQUIVO_ENV):
    """Lê o backend/.env (CHAVE=valor) sem sobrescrever variáveis já definidas."""
    if not caminho.is_file():
        return
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


if __name__ == "__main__":
    carregar_env()
    app.run(port=8000, debug=True)
