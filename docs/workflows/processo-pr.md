# Processo de Pull Request, Code Review e Definition of Done

Este documento cobre o que acontece **a partir do momento em que o codigo esta pronto** para integrar: como abrir um PR, como revisar, quais regras o GitHub aplica automaticamente e quando uma tarefa e considerada concluida.

Para convencoes de branch, commit e hooks locais, veja [fluxo-git.md](fluxo-git.md).

---

## 1. Fluxo de Trabalho

```text
develop
  └─► feat/FC404-XX_titulo
            └─► [PR aprovado + CI verde] ─► develop
                                                └─► [PR fechamento da Sprint] ─► stg ─► main
```

1. **Crie** sua branch a partir de `develop` seguindo o padrao de nomenclatura.
2. **Desenvolva** a funcionalidade de forma vertical e completa (backend + frontend + banco, conforme necessario).
3. **Abra um PR** da sua branch para `develop`.
4. **Preencha o template** que o GitHub carrega automaticamente: descricao, como testar e checklist.
5. **Aguarde revisao:** sao necessarias **2 aprovacoes** de colegas antes do merge.
6. **Resolva todos os comentarios** em aberto — o merge e bloqueado enquanto houver threads nao resolvidas.
7. **Merge:** apos CI verde e aprovacoes completas. Metodos permitidos: merge commit, squash ou rebase.

> O merge para `main` so ocorre no fechamento da Sprint, apos validacao completa pela equipe.

---

## 2. Checklist do Autor (antes de abrir o PR)

Antes de abrir o PR, o autor deve garantir que:

- [ ] A funcionalidade esta completa e testavel de ponta a ponta
- [ ] Testei localmente e esta funcionando
- [ ] Nao ha `console.log` ou codigo de debug no codigo
- [ ] Os criterios de aceite do ticket Jira foram atendidos
- [ ] A branch segue o padrao de nomenclatura (`<tipo>/FC404-XX_titulo`)
- [ ] Os commits seguem o Conventional Commits com escopo Jira (`tipo(FC404-XX): descricao`)

---

## 3. Criterios de Revisao (Code Review)

Ao revisar um PR, avalie:

- **Corretude:** a logica esta correta e cobre os casos esperados?
- **Verticalidade:** a feature esta completa ou falta alguma camada?
- **Seguranca:** ha vulnerabilidades evidentes (ex: SQL injection, dados sensiveis expostos)?
- **Legibilidade:** o codigo e compreensivel sem necessidade de comentarios excessivos?
- **Conformidade:** segue os padroes de lint, formatacao e arquitetura do projeto?

Aprovacoes anteriores sao **automaticamente descartadas** quando novos commits sao enviados ao PR — rerevisar e necessario.

---

## 4. Regras de Protecao Ativas no GitHub

As regras abaixo sao aplicadas automaticamente via GitHub Rulesets e nao podem ser contornadas:

| Regra                                        | Branches afetadas        | Detalhe                                                                  |
| :------------------------------------------- | :----------------------- | :----------------------------------------------------------------------- |
| Delecao bloqueada                            | `main`, `stg`, `develop` | Nenhuma dessas branches pode ser deletada.                               |
| Force push bloqueado                         | `main`, `stg`, `develop` | Non-fast-forward pushes sao rejeitados.                                  |
| PR obrigatorio                               | `main`, `develop`        | Todo merge exige um Pull Request aberto.                                 |
| 2 aprovacoes obrigatorias                    | `main`, `develop`        | O PR precisa de pelo menos 2 revisores aprovando.                        |
| Revisoes invalidadas no novo push            | `main`, `develop`        | Aprovacoes anteriores sao descartadas quando novos commits sao enviados. |
| Threads devem ser resolvidos                 | `main`, `develop`        | Todos os comentarios do PR devem estar marcados como resolvidos.         |
| Aprovacao extra para mudancas nao atribuidas | `main`, `develop`        | Alteracoes sem autoria clara exigem aprovacao adicional.                 |

---

## 5. Definition of Done (DoD)

Uma tarefa so e considerada **concluida** quando atende a todos os criterios abaixo:

1. O codigo esta integrado em `develop` (ou superior) via PR aprovado.
2. O PR teve **2 aprovacoes** e todos os comentarios foram resolvidos.
3. O CI passou — Frontend CI e/ou Backend CI conforme os arquivos alterados.
4. A branch de origem foi criada a partir de `develop` com o nome no padrao correto.
5. Os commits seguem o Conventional Commits com o ticket Jira no escopo.
6. Os criterios de aceite definidos no card do Backlog da Sprint foram atendidos.

> Os criterios especificos de cada User Story estao no card correspondente no [Jira](https://fatec-sjc-404-team.atlassian.net/jira/software/projects/FC404/boards/1/backlog).
