# Fluxo Git — Convenções de Branch, Commit e Hooks

Este documento cobre as convenções que cada desenvolvedor aplica **localmente** no dia a dia: como nomear branches, escrever commits e o que os hooks automatizados validam.

Para o processo de Pull Request, revisão de código e Definition of Done, veja [processo-pr.md](processo-pr.md).

---

## 1. Política de Branches

### Branches protegidas

As branches abaixo são protegidas por GitHub Rulesets e **não aceitam push direto, não podem ser deletadas e rejeitam force push**:

| Branch    | Propósito                                              |
| :-------- | :----------------------------------------------------- |
| `main`    | Produção. Merge apenas no fechamento da Sprint.        |
| `stg`     | Homologação / staging.                                 |
| `develop` | Integração durante a Sprint. Base para novas branches. |

Todo código entra nessas branches exclusivamente via **Pull Request aprovado**.

### Nomenclatura de branches

```text
<tipo>/<JIRA-TICKET>_titulo-do-ticket
```

O hook `pre-push` (Lefthook) bloqueia qualquer push que não respeite o formato. O workflow **Branch Name Check** repete a validação no GitHub ao abrir um PR.

**Tipos válidos:** `feat`, `fix`, `hotfix`, `refactor`, `chore`, `docs`, `test`, `style`, `perf`, `ci`, `build`

**Exemplos:**

```text
feat/FC404-42_criar-tela-de-login
fix/FC404-7_corrigir-validacao-de-token
docs/FC404-10_atualizar-readme
chore/FC404-2_configurar-lefthook
```

> Branches `main`, `stg` e `develop` são exceções e não passam por essa validação.

### Verticalidade das branches

É proibido criar branches por camada técnica (ex: uma branch só para o Model ou só para a View). Cada branch deve representar uma **funcionalidade testável de ponta a ponta**.

| | Exemplo |
|:--|:--|
| **Errado** | `feat/FC404-15_apenas-modelo-de-dados` |
| **Correto** | `feat/FC404-15_calculo-de-inadimplencia` (inclui model, lógica e exibição) |

---

## 2. Padrão de Commits

Os commits seguem o [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/) com o ticket Jira como **escopo obrigatório**. O hook `commit-msg` (Lefthook + commitlint) valida automaticamente cada mensagem.

```text
<tipo>(<JIRA-TICKET>): <descrição curta no imperativo>
```

**Tipos válidos:** `feat`, `fix`, `hotfix`, `refactor`, `chore`, `docs`, `test`, `style`, `perf`, `ci`, `build`, `revert`

**Exemplos:**

```text
feat(FC404-42): criar tela de login
fix(FC404-7): corrigir validacao de token expirado
chore(FC404-2): configurar lefthook e commitlint
docs(FC404-10): atualizar readme com instrucoes de instalacao
```

### Qualidade e frequência de commits

- **Commits atômicos:** cada commit deve representar uma única unidade lógica de progresso.
- **Não acumule alterações:** commits gigantes dificultam o Code Review e impossibilitam reverter um erro sem perder trabalho paralelo.
- **Evite commits triviais isolados:** pequenos ajustes estéticos devem ser agrupados em um único commit de `style` ou `refactor`.

---

## 3. Hooks Locais — Lefthook

O [Lefthook](https://github.com/evilmartians/lefthook) executa validações automaticamente na máquina do desenvolvedor. Instalação: `npm install` na raiz do repositório (o script `prepare` roda `lefthook install` automaticamente). Para ativar a CLI `404`, rode também `cd node_modules/@fatec-sjc-404-team/cli && npm link && cd -`.

| Hook         | Quando executa      | O que faz                                                                                                                                    |
| :----------- | :------------------ | :------------------------------------------------------------------------------------------------------------------------------------------- |
| `pre-commit` | A cada `git commit` | Roda ESLint + Prettier nos `.ts`/`.tsx` do frontend e Ruff nos `.py` do backend que estão em stage. Correções automáticas voltam ao stage.   |
| `pre-push`   | A cada `git push`   | Valida se o nome da branch segue o padrão obrigatório. Bloqueia o push caso contrário.                                                       |
| `commit-msg` | A cada `git commit` | Valida se a mensagem segue o Conventional Commits com escopo Jira obrigatório via commitlint.                                                |

> Se um hook bloquear sua ação, leia a mensagem de erro, corrija o problema e tente novamente. **Nunca use `--no-verify`** para contornar os hooks.

---

## 4. Identificação por Ticket Jira

O ticket Jira deve estar presente tanto no **nome da branch** quanto na **mensagem de commit**. A chave do projeto é `FC404`.

```text
FC404-<numero>
```

Exemplo de rastreabilidade completa:

```text
Branch:  feat/FC404-42_criar-tela-de-login
Commits: feat(FC404-42): criar estrutura da tela de login
         feat(FC404-42): adicionar validacao de formulario
         feat(FC404-42): integrar com endpoint de autenticacao
```

---

## Referência Rápida

| O que fazer              | Como fazer                                                                              |
| :----------------------- | :-------------------------------------------------------------------------------------- |
| Instalar os hooks        | `npm install` na raiz do repositório                                                    |
| Ativar a CLI `404`       | `cd node_modules/@fatec-sjc-404-team/cli && npm link && cd -` (uma vez por máquina)    |
| Criar uma nova branch    | `404 new-branch` ou `git checkout -b feat/FC404-XX_nome-da-feature` a partir de `develop` |
| Commitar com o padrão    | `404 commit` ou `git commit -m "feat(FC404-XX): descricao"`                             |
| Criar um arquivo novo    | `404 new-file`                                                                          |
| Validar branch           | O `pre-push` valida automaticamente ao rodar `git push`                                 |
| Abrir um PR              | Da sua branch para `develop` — veja [processo-pr.md](processo-pr.md)                   |
