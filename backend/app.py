from flasgger import Swagger
from flask import Flask, jsonify

app = Flask(__name__)

# Gera a documentação Swagger a partir das docstrings das rotas (acessível em /apidocs)
Swagger(app)


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
