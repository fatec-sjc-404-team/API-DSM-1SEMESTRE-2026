# ADR: pesquisa matplotlib

**Data:** 2026-09-19
**Autor:** Rafael Matheus
**Status:** Proposto

---

# Matplotlib

## O que é:

O Matplotlib se trata de uma biblioteca para visualizar dados em Python, usada por analistas e cientistas de dados. Ele pega números "frios e crus" e os transforma em gráficos.

## Para que serve:

Serve para transformar tabelas e planilhas cheias de números em gráficos, para tornar mais fácil a visualização desses dados. Dando o devido contexto, esses dados passam a contar histórias, o que é essencial para atender às necessidades dos clientes.

A capacidade de visualizar os dados é uma das partes essenciais para quem faz análises. Com o Matplotlib, dá para mostrar tendências, comparações e distribuições de maneira muito intuitiva. Com ele, é possível criar:

- Histogramas;
- Gráficos de linha;
- Gráficos de dispersão;
- Gráficos de barras;
- Gráficos de pizza;
- Diagramas de caixa;
- Gráficos 2D e 3D.

## Como instalar:

No terminal, digite:

Para instalar o pip:

```bash
python -m ensurepip
python -m pip install --upgrade pip
```

No Linux/Mac:

```bash
sudo pip install matplotlib
```

Para instalar o Matplotlib:

```bash
pip install matplotlib
```

## Como utilizar:

### Exemplo de tabela de dados

- jan - 12316561
- fev - 74645
- mar - 7116413
- abr - 21354634

Agora, como transformar esses dados de vendas em gráficos usando o Matplotlib?

A biblioteca principal é a `matplotlib` e, para criar os gráficos, usamos o módulo específico `pyplot`:

```python
import matplotlib.pyplot as plt
```

### Criando listas com os dados da tabela:

```python
meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho']
valores = [105235, 107697, 110256, 109236, 108859, 109986]
```

Agora solicitamos ao `pyplot` que plote (`plot`) o gráfico:

```python
matplotlib.pyplot.plot(meses, valores)
```

Depois é só exibir o gráfico:

```python
matplotlib.pyplot.show()
```

Pode-se adicionar um título ao gráfico usando o `matplotlib.pyplot.title`.

Essa é apenas uma das maneiras básicas de se usar o Matplotlib, apenas para conhecermos sua sintaxe, mas ele oferece diversas formas e utilidades para usar.
