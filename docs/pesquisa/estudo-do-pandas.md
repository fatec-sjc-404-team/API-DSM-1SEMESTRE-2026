# Estudo do Pandas

**Data:** 2026-09-23

**Autor:** Pedro Henrique Cabral Leite

**Status:** Finalizado

---

## O que é o Pandas

O Pandas é uma biblioteca do Python para mexer com dados. Ele tem uma estrutura chamada DataFrame que basicamente organiza os dados em linhas e colunas, tipo uma planilha do Excel, só que dentro do código. Dá pra ler CSV, filtrar, agrupar, calcular coisas, tudo com poucas linhas.

---

## Como instalar

Primeiro, confira se o Python está instalado rodando `python --version` no terminal.

Depois é só instalar com o pip:

```bash
pip install pandas
```

Pra checar se deu certo:

```bash
python -c "import pandas; print(pandas.__version__)"
```

Se aparecer a versão, tá pronto. Caso esteja usando um ambiente virtual do projeto (venv), lembre de ativar ele antes de rodar o pip.

---

## Como e por que usar no nosso projeto

> Leitura e tratamento de dados
Dá pra ler CSV, Excel e JSON em poucas linhas e já sair filtrando e agrupando. No nosso projeto a gente precisa limpar as bases antes de mostrar qualquer coisa, então isso ajuda bastante.

> Integração com o Flask
Como o back-end usa Flask, a gente consegue pegar o DataFrame, converter pra JSON e devolver direto pela rota da API.

> Análise rápida dos dados
Com comandos tipo `.mean()`, `.value_counts()`, `.describe()`, dá pra ter uma noção geral dos dados sem muito esforço. Ajuda na hora de decidir o que vale a pena mostrar na interface.

> Limpeza de dados
Tem funções prontas pra lidar com dados faltantes, tirar duplicata, renomear coluna. Poupa trabalho na hora de arrumar os dados.

---

## Exemplo simples de uso

Um exemplo básico de como o Pandas funciona para ler um CSV e filtrar dados:

```python
import pandas as pd

# Lendo um arquivo CSV e transformando em DataFrame
df = pd.read_csv('dados.csv')

# Mostrando as 5 primeiras linhas para conferir
print(df.head())

# Filtrando apenas as linhas onde a coluna 'status' é 'ativo'
ativos = df[df['status'] == 'ativo']

# Calculando a média de uma coluna numérica
media = df['valor'].mean()
print(f"Média dos valores: {media}")
```

---

## Bibliotecas que podemos usar junto

* **Matplotlib:** Pra gerar gráficos a partir dos dados tratados.
* **NumPy:** O Pandas já usa por baixo, mas às vezes precisa usar direto pra fazer contas mais específicas.
* **Openpyxl:** Necessário se for ler ou salvar arquivos Excel (.xlsx).

---

## Pontos de atenção

> Memória
O Pandas carrega tudo na RAM. Se a base for muito pesada, pode travar. Dá pra contornar lendo em pedaços com `chunksize` ou só as colunas que importam com `usecols`.

> Tipos de dados
Quando lê um CSV, ele tenta adivinhar o tipo de cada coluna, mas nem sempre acerta. Datas podem vir como texto, número com vírgula pode dar ruim. Sempre bom dar um `df.dtypes` pra conferir.

