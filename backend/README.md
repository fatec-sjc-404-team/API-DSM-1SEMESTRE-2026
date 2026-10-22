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
| GET    | `/api/dados` | Dados do BCB só com as linhas que atendem aos filtros |
| GET    | `/api/indicadores` | Indicadores calculados só com os dados que atendem aos filtros |

Para testar pelo terminal:

```bash
curl http://localhost:8000/health
# {"status": "ok"}

curl http://localhost:8000/hello-world
# {"mensagem": "Hello, World!"}
```

## Filtros

Os filtros (`filtros.py`) chegam como parâmetros na URL de `/api/dados` e `/api/indicadores`, por exemplo `/api/indicadores?regiao=nordeste&estado=BA&periodo=6_meses`. Eles são aplicados nos dados antes de qualquer cálculo, então o gráfico ou a tela que consumir essas rotas já recebe o resultado filtrado.

| Parâmetro    | Valores                                   | Observação                                                  |
| ------------ | ----------------------------------------- | ----------------------------------------------------------- |
| `regiao`     | `todos`, `norte`, `nordeste`              |                                                             |
| `estado`     | sigla da UF (ex. `BA`) ou `todos`         | precisa pertencer à região escolhida                        |
| `periodo`    | `1_mes`, `2_meses` ... `12_meses`         | conta por mês, a partir do mês mais recente dos dados       |
| `tipoDivida` | `todos`, `saudavel`, `critica`, `mista`   | veja "Tipo de dívida" abaixo                                |

- Valor vazio ou `todos` conta como filtro não usado, então remover um filtro traz os dados de volta.
- Valor inválido devolve erro `400` com a mensagem do problema.
- Se o MySQL e o CSV não estiverem disponíveis, a API devolve erro `503`.

### De onde vêm os dados

`dados.py` lê a tabela `BCB` e soma por mês, UF e tipo de dívida. Se a variável `DB_USER` estiver definida, lê do MySQL; senão, lê o CSV `Tratamento_Dados/saida/scrdata_norte_nordeste_pessoa_fisica_baixa_renda.csv`. O resultado fica 5 minutos na memória, então depois de reimportar o CSV espere esse tempo ou reinicie a API.

| Variável      | Padrão      | Descrição                  |
| ------------- | ----------- | -------------------------- |
| `DB_USER`     | (sem valor) | usuário do MySQL; ativa a leitura pelo banco |
| `DB_PASSWORD` | vazio       | senha do MySQL             |
| `DB_HOST`     | `localhost` | servidor do MySQL          |
| `DB_PORT`     | `3306`      | porta do MySQL             |
| `DB_NAME`     | `AvoCredit` | banco                      |

```bash
DB_USER=root DB_PASSWORD=sua_senha python app.py
```

### Respostas

`/api/dados` devolve as linhas que sobraram nos filtros, somadas por mês (`data_base`), UF e tipo de dívida, com `carteira_ativa` e `carteira_inadimplencia`.

`/api/indicadores` devolve os indicadores `geral`, `por_regiao` e `por_estado`:

| Indicador            | Como é calculado                                                        |
| -------------------- | ----------------------------------------------------------------------- |
| `carteira_ativa`     | soma da carteira ativa                                                  |
| `taxa_inadimplencia` | `carteira_inadimplencia ÷ carteira_ativa × 100`                         |
| `pct_saudavel`, `pct_critica`, `pct_mista` | quanto da carteira ativa é de cada tipo de dívida, em % |

Os valores são somados antes de dividir, então regiões e estados com carteira maior pesam mais. Grupos sem carteira ativa não aparecem. Se houver filtro de `tipoDivida`, os `pct_*` valem só para o que sobrou do filtro. As duas respostas trazem os `filtros` usados e a `ultima_data_base` dos dados.

Os indicadores da US01 que ainda não existem (recuperação rápida, crédito caro e apostas) devem usar `dados_filtrados(filtros)` em `dados.py`, que já devolve a tabela filtrada.

### Tipo de dívida

A coluna `tipo_divida` não existe no CSV: `dados.py` calcula a partir da modalidade e da submodalidade (função `classificar_tipo_divida`), seguindo a regra de [`docs/pesquisa/regras-de-indicador.md`](../docs/pesquisa/regras-de-indicador.md):

| Tipo       | O que entra                                                                                     |
| ---------- | ----------------------------------------------------------------------------------------------- |
| `critica`  | cartão de crédito (rotativo, fatura parcelada, não migrado), cheque especial, adiantamento a depositantes, capital de giro com teto rotativo |
| `saudavel` | financiamentos imobiliários, financiamentos rurais, microcrédito, financiamentos agroindustriais |
| `mista`    | todo o resto (consignado, crédito pessoal, veículos, compras no cartão sem juros etc.)         |

Essa classificação é **temporária**: é uma proposta que ainda não foi validada pelo grupo e pode ser ajustada nas constantes no topo de `dados.py`.

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

O script [`database/AvoData.sql`](database/AvoData.sql) cria o banco `AvoCredit` e a
tabela `BCB`, com as 24 colunas do CSV final. Também adiciona uma
coluna técnica `id` como chave primária, sem precisar que ela exista no CSV.
Os valores monetários usam `DECIMAL(20, 2)` para manter precisão decimal, e o
banco/tabela usam `utf8mb4` para armazenar texto.

Para criar o modelo pelo MySQL Workbench:

1. Abra `backend/database/AvoData.sql`.
2. Conecte-se ao servidor MySQL e execute o script inteiro.
3. Atualize a lista de schemas; o banco `AvoCredit` e a tabela `BCB`
   deverão aparecer.

O script não apaga nem altera tabelas já existentes. `CREATE TABLE IF NOT
EXISTS` não atualiza uma tabela que já tenha sido criada com outra estrutura.

### Importar o CSV para o MySQL

Antes da importação, execute as três etapas de tratamento descritas acima e
confirme que o arquivo final existe em
`Tratamento_Dados/saida/scrdata_norte_nordeste_pessoa_fisica_baixa_renda.csv`.
Crie o banco e a tabela usando `database/AvoData.sql` e instale as dependências
do projeto (`python -m pip install -r requirements.txt`). Na pasta `backend/`,
execute:

```bash
python database/Importar_csv.py
```

O script solicita o usuário e a senha do MySQL no terminal. A carga substitui
os registros existentes em `BCB` pelos dados do CSV dentro de uma única
transação; se ocorrer um erro, a transação é revertida e os dados anteriores
são preservados.
