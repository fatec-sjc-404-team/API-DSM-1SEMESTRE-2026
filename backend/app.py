from flasgger import Swagger
from flask import Flask, jsonify, render_template, request

from dados import DadosIndisponiveis, consultar_dados
from filtros import ler_filtros
from indicadores import consultar_indicadores

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
    Vêm o resultado geral, por região (norte, nordeste) e por estado.
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
          Indicadores de cada grupo. taxa_inadimplencia e pct_* são porcentagens.
          Grupos sem carteira ativa não aparecem.
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
            por_regiao:
              type: object
              description: Mesmos indicadores de "geral", uma chave por região
            por_estado:
              type: object
              description: Mesmos indicadores de "geral", uma chave por UF
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


@app.get("/filtros_salvos")
def filtros_salvos():
    return render_template("filtros_salvos.html")


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


if __name__ == "__main__":
    app.run(port=8000, debug=True)
