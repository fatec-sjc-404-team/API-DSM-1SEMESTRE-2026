# Analise jupyter

**Data:** 2026-09-08

**Autor:** Rafael Matheus

**Status:** Em aberto

---

# Jupyter

No Jupyter criamos arquivos chamados *notebooks* para escrever nossos códigos.

O Jupyter Notebook permite escrever linhas de código em Python de maneira "blocada", ou seja, os códigos são organizados em blocos/células.

Pode ser usado com o aplicativo instalado na sua máquina (essa é a forma local; ele abre uma página no navegador). Também é possível usar de forma hospedada, o que seria muito bom para trabalharmos em equipe. Além disso, é possível instalar uma extensão no VS Code.

Usar o Jupyter facilita divulgar e documentar nosso trabalho.

É interessante usar o Jupyter através do Anaconda Navigator, caso seja de forma local.

## Formas de usar o Jupyter hospedado

> Google Colab  
> Deepnote

## Como e por que usar Jupyter na análise de dados

> É usado para análise de dados pelo fato de os códigos serem escritos em blocos, o que facilita a leitura e a interpretação.

> Na análise de dados, você precisa ir testando, vendo o resultado e ajustando. Você não sabe exatamente o que vai fazer logo de cara, então o Jupyter ajuda muito nisso: você pode escrever uma ou mais linhas, ver se deu certo, se o gráfico funcionou e fez sentido, e continuar testando.

> Para usar com as bibliotecas de dados do Python, ajuda porque você já vê o gráfico logo abaixo da célula, o que facilita e adianta o trabalho.

> Você pode inspecionar variáveis sem quebrar todo o código, só adicionando uma célula.

## Bibliotecas para usar

> Matplotlib  
> Pandas  
> Streamlit

## Streamlit vs. Matplotlib

Perguntei para algumas I.A a diferença entre elas e dei nosso contexto de trabalho de faculdade. Ele fez a seguinte comparação:

Se o TCC final for um relatório/documento (PDF, Word ou até um notebook exportado como HTML), Matplotlib (ou Seaborn, que é baseado nele e fica mais bonito) resolve bem, porque os gráficos viram imagens dentro do documento.

Se o TCC final for uma página web com várias seções e o dashboard for só uma parte dela, bibliotecas de gráficos interativos que geram HTML embutível, como Plotly (gera uma `<div>` de gráfico que você insere dentro de qualquer página HTML), podem ser mais adequadas que o Streamlit — porque aí você tem interatividade (zoom, *hover*) sem precisar de um app separado rodando.

## Uso básico do Jupyter + Matplotlib

```python
import matplotlib.pyplot as plt
%matplotlib inline

...
```

```python
%matplotlib notebook
import matplotlib.pyplot as plt

...
```

## Decisão após a análise

Decidimos não usar o Jupyter de forma local, pelo fato de que já será obrigatória a utilização do Google Colab.

