# Documentação do Projeto

Este arquivo centraliza a documentação do projeto e descreve o conteúdo de cada pasta.

---

## Estrutura

```text
docs/
├── README.md          ← este arquivo
└── workflows/         ← processos e fluxos de trabalho do time
└── produto/           ← documentações sobre o produto
└── arquitetura/       ← decisões de arquitetura e definição do projeto
└── pesquisa/          ← estudos e pesquisas técnicas do time
```

> **CLI [`uva`](https://github.com/ihFernando/uva-cli):** o repositório inclui uma CLI interativa para criar branches, commits e arquivos seguindo os padrões do projeto. Consulte o [Manual de Instalação](../README.md#instalacao) no README raiz para ativá-la.

---

## workflows/

Documentação dos processos que o time segue durante o desenvolvimento. Deve ser consultada no início do projeto e sempre que houver dúvida sobre fluxo, convenções ou ferramentas.

| Arquivo | Conteúdo |
| :------ | :------- |
| [acordos.md](workflows/acordos.md) | Working agreements: comunicação, cerimônias, WIP, tomada de decisão e calendário das Sprints |
| [fluxo-git.md](workflows/fluxo-git.md) | Convenções de branch, commits, hooks locais (Lefthook) e rastreabilidade com Jira |
| [processo-pr.md](workflows/processo-pr.md) | Fluxo de Pull Request, code review, regras de proteção do GitHub, promoção de ambiente e Definition of Done |
| [jira.md](workflows/jira.md) | Campos de tarefa, board, movimentação de cards, reprovação em QA e integração com GitHub |

## produto/

Documentações sobre o produto, backlog e entregas por Sprint.

| Arquivo | Conteúdo |
| :------ | :------- |
| [backlog.md](produto/backlog.md) | Backlog do produto com as User Stories e critérios de aceite por Sprint |

## arquitetura/

Decisões de arquitetura (ADRs) e definição técnica do projeto.

| Arquivo | Conteúdo |
| :------ | :------- |
| [definicao-do-projeto.md](arquitetura/definicao-do-projeto.md) | ADR de definição do projeto: objetivo, stack tecnológica (Flask, Python, SQL, Google Colab) e entregas da Sprint 1 |

## pesquisa/

Estudos e pesquisas técnicas realizados pelo time para embasar decisões de arquitetura e tecnologia.

| Arquivo | Conteúdo |
| :------ | :------- |
| [analise-jupyter.md](pesquisa/analise-jupyter.md) | Análise do Jupyter Notebook como ambiente de dados, comparação de bibliotecas de visualização e decisão pelo Google Colab |
| [estudo-do-google-colab.md](pesquisa/estudo-do-google-colab.md) | Estudo de aplicabilidade do Google Colab para prototipagem Python, exploração de dados e modelagem na API |
| [pesquisa-streamlit.md](pesquisa/pesquisa-streamlit.md) | Pesquisa sobre Streamlit como framework para criação de dashboards e interfaces de visualização de dados em Python |
| [estudo-do-flask.md](pesquisa/estudo-do-flask.md) | Estudo de aplicabilidade do Flask para criar APIs Python, visão geral do framework, integração com análises em Python e decisão de usar Flask como backend do projeto |
| [raspagem-de-dados.md](pesquisa/raspagem-de-dados.md) | Guia sobre web scraping: definição, como funciona, fontes de dados (Serasa, IBGE, Banco Central) e boas práticas de coleta responsável |
| [pesquisa-spa.md](pesquisa/pesquisa-spa.md) | Pesquisa sobre a Secretaria de Prêmios e Apostas: organização, regulamentação do mercado de apostas e impacto na inadimplência das famílias brasileiras |
| [pesquisa-data-senado.md](pesquisa/pesquisa-data-senado.md) | Pesquisa sobre DataSenado: órgão de pesquisas de opinião pública do Senado Federal e sua relação com análise de endividamento e capacidade de pagamento das famílias brasileiras |

## dados/

Coleta de Dados (IBGE, BCB, Bacen) Realizada pela equipe, para manipulação, tratamento e governança de Dados.

| Arquivo | Conteúdo |
| :------ | :------- |
| [dados-bcb.md](dados/dados-bcb.md) | O tratamento de dados do BCB, IBGE e Bacen envolve a coleta, organização e análise de informações econômicas e financeiras. Esses dados permitem acompanhar indicadores como crédito, inadimplência, juros, renda e consumo da população. |
| [dados-ibge.md](dados/dados-ibge.md) | Indicadores econômicos e financeiros do IBGE: rendimento domiciliar per capita, endividamento de risco, inadimplência e comportamento de consumo por região |
