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

### Preparar o ambiente

Na raiz do repositório, crie e ative o ambiente virtual:

```bash
python -m venv backend/.venv
source backend/.venv/bin/activate
```

No PowerShell do Windows, use a ativação correspondente:

```powershell
.\backend\.venv\Scripts\Activate.ps1
```

Instale as dependências a partir da pasta `backend/`:

```bash
cd backend
python -m pip install -r requirements.txt
```

### Preparar os CSVs e executar as etapas

Coloque todos os CSVs mensais em `Tratamento_Dados/entrada/`. Os nomes podem
variar, mas cada arquivo deve usar `;` como separador e ter as mesmas colunas na
mesma ordem. Os valores decimais com vírgula são reconhecidos. Na pasta
`backend/`, com o ambiente virtual ativo, execute as etapas na ordem:

```powershell
python -m Tratamento_Dados.Estados
python -m Tratamento_Dados.Tipo_Pessoa
python -m Tratamento_Dados.Renda
```

As etapas leem os arquivos em lotes de 50.000 linhas, mantêm todas as colunas e
criam um CSV combinado por etapa. Não alteram os arquivos originais. Os
resultados são:

| Etapa | Filtro | Arquivo de saída |
|---|---|---|
| 1 | UFs do Norte e Nordeste | `Tratamento_Dados/saida/scrdata_norte_nordeste.csv` |
| 2 | Apenas clientes `PF` | `Tratamento_Dados/saida/scrdata_norte_nordeste_pessoa_fisica.csv` |
| 3 | `Sem rendimento`, `Até 1 salário mínimo` e `Mais de 1 a 2 salários mínimos` | `Tratamento_Dados/saida/scrdata_norte_nordeste_pessoa_fisica_baixa_renda.csv` |

### Testes automatizados

Os testes usam DataFrames pequenos criados durante o teste; não precisam do CSV
real. Na pasta `backend/`, execute:

```bash
python -m pytest
```

Resultado esperado: `9 passed`. Esses testes verificam os filtros, a combinação
de arquivos mensais, a preservação de colunas, os valores decimais e a rejeição
de arquivos com colunas incompatíveis.

### Validar os resultados das etapas

Depois de executar os três scripts, confira no terminal as linhas, colunas e
validações de cada saída:

```bash
python -m Tratamento_Dados.Validar_Resultado
```

Com os sete arquivos de janeiro a julho de 2026 usados no teste, os resultados
esperados foram:

| Etapa | Linhas após o filtro | Colunas |
|---|---:|---:|
| Norte e Nordeste | 1.003.958 | 24 |
| Pessoas físicas (`PF`) | 622.708 | 24 |
| Baixa renda | 182.157 | 24 |

O verificador também deve mostrar `OK` para as UFs do Norte/Nordeste, clientes
PF e faixas de renda permitidas. Essas contagens são uma referência para essa
versão dos sete CSVs; podem mudar se os arquivos de entrada forem diferentes.
`data_base` é preservada para identificar o mês de cada linha. Os CSVs nas
pastas `entrada/` e `saida/` são ignorados pelo Git. Reexecutar uma etapa
substitui a saída anterior com o mesmo nome.

## Modelo físico no MySQL

O script [`database/schema.sql`](database/schema.sql) cria o banco `api_dsm` e a
tabela `dados_tratados`, com as 24 colunas do CSV final. Também adiciona uma
coluna técnica `id` como chave primária, sem precisar que ela exista no CSV.
Os valores monetários usam `DECIMAL(20, 2)` para manter precisão decimal, e o
banco/tabela usam `utf8mb4` para armazenar texto.

Para criar o modelo pelo MySQL Workbench:

1. Abra `backend/database/schema.sql`.
2. Conecte-se ao servidor MySQL e execute o script inteiro.
3. Atualize a lista de schemas; o banco `api_dsm` e a tabela `dados_tratados`
   deverão aparecer.

O script não apaga nem altera tabelas já existentes. `CREATE TABLE IF NOT
EXISTS` não atualiza uma tabela que já tenha sido criada com outra estrutura.
Este passo cria somente o modelo; a carga automática do CSV para o MySQL ainda
precisa ser implementada.
