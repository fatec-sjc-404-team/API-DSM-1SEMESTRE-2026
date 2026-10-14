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

## Tratamento dos dados por estado

Cada pessoa deve colocar uma cópia do CSV chamado `scrdata_202601.csv` em
`Tratamento_Dados/entrada/`. O caminho é relativo ao script, então não depende
do nome de usuário ou da pasta onde o repositório foi clonado. Com o ambiente
virtual ativado e o terminal na pasta `backend/`, execute:

```powershell
python Tratamento_Dados/Estados.py
```

O script mantém todas as colunas, filtra as linhas para as UFs do Norte e do
Nordeste e salva um novo arquivo em `Tratamento_Dados/saida/`, sem alterar o
original. Os CSVs nas pastas `entrada/` e `saida/` são ignorados pelo Git.

### Etapas seguintes do tratamento

Execute os scripts na ordem abaixo, a partir da pasta `backend/`. Cada etapa
usa a saída da anterior e grava um novo arquivo em `Tratamento_Dados/saida/`:

```bash
python Tratamento_Dados/Tipo_Pessoa.py
python Tratamento_Dados/Renda.py
```

`Tipo_Pessoa.py` mantém apenas clientes `PF`. `Renda.py` mantém os portes
`Sem rendimento`, `Até 1 salário mínimo` e `Mais de 1 a 2 salários mínimos`.

Atualmente, os caminhos e nomes de saída estão configurados para o arquivo de
janeiro de 2026 (`scrdata_202601.csv`). Apenas adicionar CSVs de outros meses à
pasta `entrada/` não os inclui no processamento. Para analisar vários meses,
será necessário adaptar o pipeline para carregar todos os arquivos e manter
`data_base` na agregação temporal.

### Testes automatizados

Os testes usam DataFrames pequenos criados durante o teste; não precisam do CSV
real nem de um caminho específico do sistema operacional. Na pasta `backend/`,
execute:

```bash
python -m pytest
```

Para verificar no terminal o resultado produzido com o CSV real, depois de
executar as três etapas (`Estados.py`, `Tipo_Pessoa.py` e `Renda.py`), rode:

```bash
python Tratamento_Dados/Validar_Resultado.py
```

O verificador mostra as quantidades de linhas e colunas e os resultados das
validações após cada etapa: UFs do Norte/Nordeste, clientes PF e faixas de renda
selecionadas.
