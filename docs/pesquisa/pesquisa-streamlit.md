# pesquisa-streamlit

**Data:** 2026-09-10
**Autor:** Rafael Matheus
**Participantes:**
**Facilitador:**

---

# STREAMLIT

## O que é:

O Streamlit é uma biblioteca do Python que permite a criação de aplicativos web para análise de dados, permitindo transformar scripts de Python em app web de uma forma mais simples, sem exigir conhecimentos muito avançados de desenvolvimento web. Usado por desenvolvedores que trabalham com visualização de dados.

Ideal para equipes com pouca experiência em programação.

Trata-se de um framework de código aberto, desenvolvido em Python, que se destina à criação de aplicações voltadas para ciência de dados e aprendizado de máquina. A ideia central é transformar um script Python comum em uma interface web só adicionando algumas chamadas de função.

## Para que serve:

> Criação de dashboards interativos, ideal para prototipagem rápida e compartilhamento de dados.
>
> Cria interfaces interativas com widgets.
>
> Possível integrar com o Matplotlib e outras bibliotecas.
>
> Usado para machine learning.
>
> Permite testar modelos, ajustar hiperparâmetros e visualizar previsões em tempo real.
>
> Protótipos rápidos de ideias de ML/IA.
>
> Demos e provas de conceito.

## Streamlit:

Para quem já programa em Python, a curva de aprendizagem para usar o Streamlit é muito tranquila, pois sua criação de interface se dá de forma declarativa.

## Como usar:

Instalar a biblioteca Streamlit é feito através do pip (o gerenciador de pacotes do Python). No terminal coloque:

```bash
pip install streamlit
```

### Estrutura básica:

Dentro da pasta que está trabalhando, a mesma que tem seu código Python, você cria um segundo arquivo chamado `app.py`. Inicialmente a base para usar é:

```python
import streamlit as st
st.title("Meu Primeiro App com Streamlit")
st.write("Olá, mundo!")
```

Depois de já ter feito todo seu código rode no terminal:

```bash
streamlit run app.py
```

Isso vai abrir uma janela no navegador já rodando seu app.

## Algumas das principais funções:

- `st.write` - Pode ser usado para exibir textos, tabelas, gráficos, entre outros.
- `st.table` - Exibe tabelas estáticas.
- `st.dataframe` - Exibe tabelas interativas.

## Integração entre Matplotlib:

Primeiro se cria o gráfico usando o Matplotlib e depois usa o Streamlit para exibi-lo usando `st.pyplot()`.

## Como o Streamlit funciona por baixo dos panos (o modelo de execução):

O script inteiro roda de novo a cada interação. Quando você clica em um botão, move um slider, ou digita algo em um campo, o Streamlit não atualiza só aquele componente — ele reexecuta o arquivo Python inteiro, de cima a baixo, e redesenha a tela com os novos valores. Principal problema com isso é que se você usar uma base de dados muito extensa, seu app vai ficar muito pesado e lento.

## Anatomia típica de um projeto grande:

```
meu_app/
├── app.py              # ponto de entrada (página principal)
├── pages/              # páginas extras (multi-page app)
│   ├── 1_Relatorios.py
│   └── 2_Configuracoes.py
├── utils/              # funções auxiliares (conexão com dados, lógica)
│   └── data.py
├── .streamlit/
│   └── config.toml     # tema, configurações do servidor
└── requirements.txt
```
