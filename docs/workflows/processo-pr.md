# Processo de Pull Request, Code Review e Definition of Done

Este documento cobre o que acontece **a partir do momento em que o código está pronto** para integrar: como abrir um PR, como revisar, quais regras o GitHub aplica automaticamente e quando uma tarefa é considerada concluída.

Para convenções de branch, commit e hooks locais, veja [fluxo-git.md](fluxo-git.md).

---

## 1. Fluxo de Trabalho

O fluxo tem duas fases: **desenvolvimento** (contínuo durante a Sprint) e **promoção de ambiente** (ao final da Sprint).

```text
── DESENVOLVIMENTO (durante a Sprint) ──────────────────────────────

  develop
    └─► feat/FC404-XX_titulo
              └─► [PR: 2 aprovações + CI verde] ─► develop


── PROMOÇÃO DE AMBIENTE (fechamento da Sprint) ──────────────────────

  develop ──► [PR] ──► stg  (validação pelo cliente)
                         │
                    ┌────┴────────────────────┐
                    │ bugs encontrados        │ tudo aprovado
                    ▼                         ▼
              novo ticket de bug         [PR] ──► main (produção)
              aberto na Sprint
```

### Fase 1 — Desenvolvimento (durante a Sprint)

1. **Crie** sua branch a partir de `develop` seguindo o padrão de nomenclatura.
2. **Desenvolva** a funcionalidade de forma vertical e completa (backend + frontend + banco, conforme necessário).
3. **Abra um PR** da sua branch para `develop`.
4. **Preencha o template** que o GitHub carrega automaticamente: descrição, como testar e checklist.
5. **Aguarde revisão:** são necessárias **2 aprovações** de colegas antes do merge.
6. **Resolva todos os comentários** em aberto — o merge é bloqueado enquanto houver threads não resolvidas.
7. **Merge** após CI verde e aprovações completas. Métodos permitidos: merge commit, squash ou rebase.

### Fase 2 — Promoção de Ambiente (fechamento da Sprint)

Após o PO/SM aprovar todas as tarefas da Sprint no Jira (status **Done**), o código sobe para os ambientes superiores:

1. **develop → stg:** abre-se um PR de `develop` para `stg`. Após merge, o cliente valida a entrega no ambiente de homologação.
2. **Bugs encontrados em stg:** se o cliente identificar problemas, **não se corrige diretamente em `stg`**. Abre-se um novo ticket de bug na Sprint, o fluxo normal de desenvolvimento é seguido (`fix/FC404-XX_...` → `develop`) e uma nova promoção para `stg` é feita.
3. **stg → main:** somente após aprovação completa do cliente em `stg`, abre-se um PR de `stg` para `main`. Esse merge representa a entrega oficial da Sprint em produção.

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

Para que qualquer User Story e Pull Request seja definido como concluído e seja integrado à branch principal (`main`), os seguintes critérios devem ser atendidos:

- [ ] O código está integrado em `develop` (ou superior) via PR aprovado.
- [ ] O PR teve ao menos 2 aprovações e todos os comentários foram resolvidos.
- [ ] O CI passou com sucesso — Frontend CI e/ou Backend CI conforme os arquivos alterados.
- [ ] A branch de origem foi criada a partir de `develop` com o nome no padrão correto.
- [ ] Os commits seguem o Conventional Commits com o ticket Jira no escopo.
- [ ] Os critérios de aceite definidos no card do Backlog da Sprint foram atendidos.
- [ ] Testes unitários foram criados ou atualizados para novas regras de negócio e passaram com 100% de sucesso.
- [ ] `README.md` e documentos necessários foram devidamente atualizados conforme a demanda da task.

> Os critérios específicos de cada User Story estão no card correspondente no [Jira](https://fatec-sjc-404-team.atlassian.net/jira/software/projects/FC404/boards/1/backlog).
