# Processo de Pull Request, Code Review e Definition of Done

Este documento cobre o que acontece **a partir do momento em que o código está pronto** para integrar: como abrir um PR, como revisar, quais regras o GitHub aplica automaticamente e quando uma tarefa é considerada concluída.

Para convenções de branch, commit e hooks locais, veja [fluxo-git.md](fluxo-git.md).

---

## 1. Fluxo de Trabalho

```text
develop
  └─► feat/FC404-XX_titulo
            └─► [PR aprovado + CI verde] ─► develop
                                                └─► [PR fechamento da Sprint] ─► stg ─► main
```

1. **Crie** sua branch a partir de `develop` seguindo o padrão de nomenclatura.
2. **Desenvolva** a funcionalidade de forma vertical e completa (backend + frontend + banco, conforme necessário).
3. **Abra um PR** da sua branch para `develop`.
4. **Preencha o template** que o GitHub carrega automaticamente: descrição, como testar e checklist.
5. **Aguarde revisão:** são necessárias **2 aprovações** de colegas antes do merge.
6. **Resolva todos os comentários** em aberto — o merge é bloqueado enquanto houver threads não resolvidas.
7. **Merge:** após CI verde e aprovações completas. Métodos permitidos: merge commit, squash ou rebase.

> O merge para `main` só ocorre no fechamento da Sprint, após validação completa pela equipe.

---

## 2. Checklist do Autor (antes de abrir o PR)

Antes de abrir o PR, o autor deve garantir que:

- [ ] A funcionalidade está completa e testável de ponta a ponta
- [ ] Testei localmente e está funcionando
- [ ] Não há `console.log` ou código de debug no código
- [ ] Os critérios de aceite do ticket Jira foram atendidos
- [ ] A branch segue o padrão de nomenclatura (`<tipo>/FC404-XX_titulo`)
- [ ] Os commits seguem o Conventional Commits com escopo Jira (`tipo(FC404-XX): descricao`)

---

## 3. Critérios de Revisão (Code Review)

Ao revisar um PR, avalie:

- **Corretude:** a lógica está correta e cobre os casos esperados?
- **Verticalidade:** a feature está completa ou falta alguma camada?
- **Segurança:** há vulnerabilidades evidentes (ex: SQL injection, dados sensíveis expostos)?
- **Legibilidade:** o código é compreensível sem necessidade de comentários excessivos?
- **Conformidade:** segue os padrões de lint, formatação e arquitetura do projeto?

Aprovações anteriores são **automaticamente descartadas** quando novos commits são enviados ao PR — revisar novamente é necessário.

---

## 4. Regras de Proteção Ativas no GitHub

As regras abaixo são aplicadas automaticamente via GitHub Rulesets e não podem ser contornadas:

| Regra                                         | Branches afetadas        | Detalhe                                                                   |
| :-------------------------------------------- | :----------------------- | :------------------------------------------------------------------------ |
| Deleção bloqueada                             | `main`, `stg`, `develop` | Nenhuma dessas branches pode ser deletada.                                |
| Force push bloqueado                          | `main`, `stg`, `develop` | Non-fast-forward pushes são rejeitados.                                   |
| PR obrigatório                                | `main`, `develop`        | Todo merge exige um Pull Request aberto.                                  |
| 2 aprovações obrigatórias                     | `main`, `develop`        | O PR precisa de pelo menos 2 revisores aprovando.                         |
| Revisões invalidadas no novo push             | `main`, `develop`        | Aprovações anteriores são descartadas quando novos commits são enviados.  |
| Threads devem ser resolvidos                  | `main`, `develop`        | Todos os comentários do PR devem estar marcados como resolvidos.          |
| Aprovação extra para mudanças não atribuídas  | `main`, `develop`        | Alterações sem autoria clara exigem aprovação adicional.                  |

---

## 5. Definition of Done (DoD)

Uma tarefa só é considerada **concluída** quando atende a todos os critérios abaixo:

1. O código está integrado em `develop` (ou superior) via PR aprovado.
2. O PR teve **2 aprovações** e todos os comentários foram resolvidos.
3. O CI passou — Frontend CI e/ou Backend CI conforme os arquivos alterados.
4. A branch de origem foi criada a partir de `develop` com o nome no padrão correto.
5. Os commits seguem o Conventional Commits com o ticket Jira no escopo.
6. Os critérios de aceite definidos no card do Backlog da Sprint foram atendidos.

> Os critérios específicos de cada User Story estão no card correspondente no [Jira](https://fatec-sjc-404-team.atlassian.net/jira/software/projects/FC404/boards/1/backlog).
