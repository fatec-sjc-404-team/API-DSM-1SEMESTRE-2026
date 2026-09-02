<h1 align="center">API DSM 1º SEMESTRE 2026</h1>

<h2 align="center"> [PROJETO - A DEFINIR] </h2>

<p align="center">
  <a href="#cliente">Cliente</a> |
  <a href="#dor">Dor do Cliente</a> |
  <a href="#desafio">Desafio</a> |
  <a href="#solucao">Solução</a> |
  <a href="#backlog">Backlog do Produto</a> |
  <a href="#dor-ready">DoR</a> |
  <a href="#dod">DoD</a> |
  <a href="#requisitos">Requisitos</a> |
  <a href="#arquitetura">Arquitetura</a> |
  <a href="#cicd">CI/CD</a> |
  <a href="#branch">Estratégia de Branch</a> |
  <a href="#jira">Integração Jira + GitHub</a> |
  <a href="#instalacao">Manual de Instalação</a> |
  <a href="#sprint">Cronograma de Sprints</a> |
  <a href="#tecnologias">Tecnologias</a> |
  <a href="#equipe">Equipe</a>
</p>

> **Status do Projeto:** Planejamento / Pré-Kick-off ⏳
>
> **Documentação:** [Adicionar link]
>
> **Jira:** [Acessar o Jira do projeto](https://fatec-sjc-404-team.atlassian.net/jira/software/projects/FC404/boards/1/backlog)
>
> **Vídeo do Projeto:** [Adicionar link]

---

## 🏢 Cliente <a id="cliente"></a>

[Preencher após o Kick-off.]

---

## 😢 Dor do Cliente <a id="dor"></a>

[Preencher após o Kick-off.]

---

## 🏅 Desafio <a id="desafio"></a>

[Preencher após o Kick-off.]

---

## 💡 Solução <a id="solucao"></a>

[Preencher após o Kick-off.]

---

# 📋 Backlog do Produto <a id="backlog"></a>

[Preencher após levantamento e refinamento do Product Backlog.]

| Rank | Prioridade | User Story | Estimativa | Sprint | Status |
| :--: | :--------: | ---------- | :--------: | :----: | :----: |
|      |            |            |            |        |        |

---

# ✅ Definition of Ready e Definition of Done

## 🏃 DoR — Definition of Ready <a id="dor-ready"></a>

[Definir após o Kick-off.]

---

## 🏆 DoD — Definition of Done <a id="dod"></a>

Os critérios de conclusão de cada tarefa estão documentados em **[docs/workflows/processo-pr.md](docs/workflows/processo-pr.md#5-definition-of-done-dod)**.

Os critérios específicos de cada User Story estão no card correspondente no [Jira](https://fatec-sjc-404-team.atlassian.net/jira/software/projects/FC404/boards/1/backlog).

---

# 📝 Requisitos <a id="requisitos"></a>

## 🎯 Requisitos Funcionais — RF

[Preencher após o Kick-off.]

---

## ⚙️ Requisitos Não Funcionais — RNF

[Preencher após o Kick-off.]

---

# 🏗️ Arquitetura do Sistema <a id="arquitetura"></a>

[Definir após o Kick-off e escolha das tecnologias.]

## Diagrama de Arquitetura

[Adicionar diagrama.]

## Componentes

[Preencher.]

## Banco de Dados

[Preencher.]

## APIs / Integrações

[Preencher.]

---

# 🔄 Integração e Entrega Contínua — CI/CD <a id="cicd"></a>

A estratégia de CI é dividida em duas camadas: **hooks locais** (executados na máquina do desenvolvedor antes do commit/push) e **workflows remotos** (executados no GitHub a cada push ou PR).

## Pipeline

### Hooks Locais — Lefthook

O [Lefthook](https://github.com/evilmartians/lefthook) gerencia os hooks do Git localmente. Ele é configurado pelo arquivo `lefthook.yml` na raiz do repositório e instalado automaticamente ao rodar `npm install`.

| Hook | Quando executa | O que faz |
| :--- | :--- | :--- |
| `pre-commit` | A cada `git commit` | Roda ESLint + Prettier nos arquivos `.ts`/`.tsx` do frontend e Ruff nos arquivos `.py` do backend que estão em stage. Arquivos corrigidos automaticamente são re-adicionados ao stage. |
| `pre-push` | A cada `git push` | Valida se o nome da branch segue o padrão obrigatório. Bloqueia o push caso contrário. |
| `commit-msg` | A cada `git commit` | Valida se a mensagem de commit segue o padrão Conventional Commits com ticket Jira. |

### Workflows Remotos — GitHub Actions

Três workflows são executados no GitHub em resposta a pushes e pull requests:

| Workflow | Arquivo | Gatilho | O que faz |
| :--- | :--- | :--- | :--- |
| **Frontend CI** | `.github/workflows/frontend.yml` | Push ou PR com mudanças em `frontend/**` | Instala dependências, roda lint e build |
| **Backend CI** | `.github/workflows/backend.yml` | Push ou PR com mudanças em `backend/**` | Roda `ruff check` e `ruff format --check` |
| **Branch Name Check** | `.github/workflows/branch-name.yml` | Abertura de PR para `main`, `stg` ou `develop` | Valida o nome da branch de origem |

> Os workflows de frontend e backend são disparados **apenas quando arquivos da respectiva pasta mudam**, evitando execuções desnecessárias.

## Ferramentas

| Ferramenta | Finalidade |
| :--- | :--- |
| [Lefthook](https://github.com/evilmartians/lefthook) | Gerenciador de hooks Git (local) |
| [commitlint](https://commitlint.js.org/) | Validação de mensagens de commit |
| [ESLint](https://eslint.org/) + [Prettier](https://prettier.io/) | Lint e formatação do frontend |
| [Ruff](https://docs.astral.sh/ruff/) | Lint e formatação do backend Python |
| [GitHub Actions](https://docs.github.com/en/actions) | CI remoto |

---

# 🌿 Estratégia de Branch <a id="branch"></a>

As convenções de branches, commits e rastreabilidade com Jira estão documentadas em detalhes em:

**[docs/workflows/fluxo-git.md](docs/workflows/fluxo-git.md)**

## Resumo rápido

| O que | Padrão |
| :---- | :----- |
| Branch | `<tipo>/FC404-XX_titulo-do-ticket` |
| Commit | `<tipo>(FC404-XX): descricao curta` |
| Tipos válidos | `feat`, `fix`, `hotfix`, `refactor`, `chore`, `docs`, `test`, `style`, `perf`, `ci`, `build` |

Branches `main`, `stg` e `develop` são protegidas — não aceitam push direto nem deleção.

## Pull Requests

O fluxo de PR, regras de proteção do GitHub, critérios de Code Review e Definition of Done estão em:

**[docs/workflows/processo-pr.md](docs/workflows/processo-pr.md)**

---

# 🧪 Estratégia de Testes

[Definir após o Kick-off.]

## Testes de Integração

[Preencher.]

## Testes de API

[Preencher.]

## Testes de Interface

[Preencher, caso aplicável.]

---

# 📖 Manual de Instalação <a id="instalacao"></a>

## ⚙️ Pré-requisitos

- [Node.js 20+](https://nodejs.org/) — necessário para todos os membros (instala os hooks Git automaticamente)
- [Ruff](https://docs.astral.sh/ruff/installation/) — necessário apenas para quem trabalha no backend Python

---

## 🚀 Passo a Passo de Instalação

### 1. Clonar o repositório

```bash
git clone [URL_DO_REPOSITORIO]
cd [NOME_DO_REPOSITORIO]
```

### 2. Instalar dependências e ativar os hooks Git

```bash
npm install
```

> O `npm install` já instala os hooks Git automaticamente via Lefthook (script `prepare`). Após isso, as validações de commit, branch e lint passam a funcionar localmente.

### 3. Configurar ambiente

```text
[Preencher após o Kick-off — variáveis de ambiente, .env, etc.]
```

### 4. Executar aplicação

```bash
[COMANDO]
```

### 5. Acessar o sistema

```text
[URL / PORTA]
```

---

# 🗓️ Cronograma de Sprints <a id="sprint"></a>

[Preencher após definição oficial do calendário.]

|  Sprint  | Período | Objetivo | Status |
| :------: | ------- | -------- | :----: |
| Sprint 1 |         |          |   ⏳   |
| Sprint 2 |         |          |   ⏳   |
| Sprint 3 |         |          |   ⏳   |

---

# 🛠️ Tecnologias Utilizadas <a id="tecnologias"></a>

[Definir após o Kick-off.]

## Frontend

[Preencher.]

## Backend

[Preencher.]

## Banco de Dados

[Preencher.]

## Testes

[Preencher.]

## Gestão e Qualidade de Código

- GitHub — versionamento e CI/CD
- Jira — gerenciamento de tarefas e sprints
- Lefthook — hooks Git locais (lint, validação de branch e commit)
- commitlint — padronização de mensagens de commit
- GitHub Actions — integração contínua remota

---

## 👥 Equipe <a id="equipe"></a>

| Integrante         | Papel              |                                                                         GitHub                                                                          |                                                                               LinkedIn                                                                                |
| :----------------- | :----------------- | :-----------------------------------------------------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------: 
| **Iago Lima** | PO / Developer | <a href="https://github.com/zixx0080"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/github/github-original.svg" width="30"></a> | <a href="https://www.linkedin.com/in/iago-lima-940376358/"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/linkedin/linkedin-original.svg" width="30"></a> |
| **Fernando Gomes** | Master / Developer | <a href="https://github.com/ihfernando"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/github/github-original.svg" width="30"></a> | <a href="https://www.linkedin.com/in/ihfernando/"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/linkedin/linkedin-original.svg" width="30"></a> |
| **Rafael Matheus** |  Developer | <a href="https://github.com/RafaelM-sants"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/github/github-original.svg" width="30"></a> | <a href="https://www.linkedin.com/in/rafael-matheus-dos-santos-7a9344397"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/linkedin/linkedin-original.svg" width="30"></a> |
| **Pedro Henrique** | Developer | <a href="https://github.com/pedrohl45"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/github/github-original.svg" width="30"></a> | <a href="https://www.linkedin.com/in/pedrohl45/"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/linkedin/linkedin-original.svg" width="30"></a> |
 **Lucas Vinicius** | Developer | <a href="https://github.com/lucasvn1"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/github/github-original.svg" width="30"></a> | <a href="https://www.linkedin.com/in/lucasviniciusant"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/linkedin/linkedin-original.svg" width="30"></a> |
| **Isabela Alves** | Developer | <a href="https://github.com/isa-alvxs"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/github/github-original.svg" width="30"></a> | <a href="https://www.linkedin.com/in/isabela-alves-778402316/"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/linkedin/linkedin-original.svg" width="30"></a> |
| **Fernando Ferreira** | Developer | <a href="https://github.com/fesafer"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/github/github-original.svg" width="30"></a> | <a href="https://www.linkedin.com/in/fernando-henrique-de-s%C3%A1-ferreira-250623352/"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/linkedin/linkedin-original.svg" width="30"></a> |
| **Khalil Ayoub** | Developer | <a href="https://github.com/KhaosKhalil"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/github/github-original.svg" width="30"></a> | <a href="https://www.linkedin.com/in/khalil-ayoub-083767429/"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/linkedin/linkedin-original.svg" width="30"></a> |
# 📚 Documentação

## Documentação Geral

- [Fluxo Git — Convenções de Branch, Commit e Hooks](docs/workflows/fluxo-git.md)
- [Processo de Pull Request, Code Review e Definition of Done](docs/workflows/processo-pr.md)

## Atas de Reunião

[Adicionar links.]

## Documentação das Sprints

[Adicionar links.]

## Diagramas

[Adicionar links.]

---

# 📹 Vídeos das Entregas

|  Sprint  | Vídeo       |
| :------: | ----------- |
| Sprint 1 | [Adicionar] |
| Sprint 2 | [Adicionar] |
| Sprint 3 | [Adicionar] |

---

# 📌 Status do Projeto

**Fase atual:** Pré-Kick-off.

O conteúdo técnico e funcional deste README será atualizado após o Kick-off oficial, conforme definição do problema, requisitos, arquitetura, tecnologias e planejamento das Sprints.
