# Backend (API Flask)

API do projeto feita em **Python + Flask**, com documentação **Swagger** (via [Flasgger](https://github.com/flasgger/flasgger)) e lint/formatação com **Ruff**.

## Pré-requisitos

- [Python 3.12+](https://www.python.org/downloads/)

## Como rodar

Todos os comandos abaixo são executados dentro da pasta `backend/`.

### 1. Criar e ativar o ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Subir a API

```bash
python app.py
```

A API fica disponível em `http://localhost:8000`.

## Endpoints

| Método | Rota           | Descrição                           |
| ------ | -------------- | ----------------------------------- |
| GET    | `/health`      | Verifica se a API está no ar        |
| GET    | `/hello-world` | Retorna uma mensagem de boas-vindas |

Para testar pelo terminal:

```bash
curl http://localhost:8000/health
# {"status": "ok"}

curl http://localhost:8000/hello-world
# {"mensagem": "Hello, World!"}
```

## Documentação (Swagger)

Com a API rodando, acesse [http://localhost:8000/apidocs](http://localhost:8000/apidocs) para ver e testar os endpoints pelo navegador.

Para documentar uma nova rota, escreva a especificação em YAML na docstring da função, depois do `---` (veja os exemplos em `app.py`).

## Lint e formatação (Ruff)

```bash
ruff check .     # aponta problemas no código
ruff format .    # formata o código
```
