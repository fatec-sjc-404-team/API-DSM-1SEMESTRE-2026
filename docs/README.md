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
| [estudo-do-flask.md](pesquisa/estudo-do-flask.md) | Estudo de aplicabilidade do Flask para criar APIs Python, visão geral do framework, integração com análises em Python e decisão de usar Flask como backend do projeto |