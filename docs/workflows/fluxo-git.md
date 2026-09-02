# Fluxo Git — Convencoes de Branch, Commit e Hooks

Este documento cobre as convencoes que cada desenvolvedor aplica **localmente** no dia a dia: como nomear branches, escrever commits e o que os hooks automatizados validam.

Para o processo de Pull Request, revisao de codigo e Definition of Done, veja [processo-pr.md](processo-pr.md).

---

## 1. Politica de Branches

### Branches protegidas

As branches abaixo sao protegidas por GitHub Rulesets e **nao aceitam push direto, nao podem ser deletadas e rejeitam force push**:

| Branch    | Proposito                                              |
| :-------- | :----------------------------------------------------- |
| `main`    | Producao. Merge apenas no fechamento da Sprint.        |
| `stg`     | Homologacao / staging.                                 |
| `develop` | Integracao durante a Sprint. Base para novas branches. |

Todo codigo entra nessas branches exclusivamente via **Pull Request aprovado**.

### Nomenclatura de branches

```text
<tipo>/<JIRA-TICKET>_titulo-do-ticket
```

O hook `pre-push` (Lefthook) bloqueia qualquer push que nao respeite o formato. O workflow **Branch Name Check** repete a validacao no GitHub ao abrir um PR.

**Tipos validos:** `feat`, `fix`, `hotfix`, `refactor`, `chore`, `docs`, `test`, `style`, `perf`, `ci`, `build`

**Exemplos:**

```text
feat/FC404-42_criar-tela-de-login
fix/FC404-7_corrigir-validacao-de-token
docs/FC404-10_atualizar-readme
chore/FC404-2_configurar-lefthook
```

> Branches `main`, `stg` e `develop` sao excecoes e nao passam por essa validacao.

### Verticalidade das branches

E proibido criar branches por camada tecnica (ex: uma branch so para o Model ou so para a View). Cada branch deve representar uma **funcionalidade testavel de ponta a ponta**.

| | Exemplo |
|:--|:--|
| **Errado** | `feat/FC404-15_apenas-modelo-de-dados` |
| **Correto** | `feat/FC404-15_calculo-de-inadimplencia` (inclui model, logica e exibicao) |

---

## 2. Padrao de Commits

Os commits seguem o [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/) com o ticket Jira como **escopo obrigatorio**. O hook `commit-msg` (Lefthook + commitlint) valida automaticamente cada mensagem.

```text
<tipo>(<JIRA-TICKET>): <descricao curta no imperativo>
```

**Tipos validos:** `feat`, `fix`, `hotfix`, `refactor`, `chore`, `docs`, `test`, `style`, `perf`, `ci`, `build`, `revert`

**Exemplos:**

```text
feat(FC404-42): criar tela de login
fix(FC404-7): corrigir validacao de token expirado
chore(FC404-2): configurar lefthook e commitlint
docs(FC404-10): atualizar readme com instrucoes de instalacao
```

### Qualidade e frequencia de commits

- **Commits atomicos:** cada commit deve representar uma unica unidade logica de progresso.
- **Nao acumule alteracoes:** commits gigantes dificultam o Code Review e impossibilitam reverter um erro sem perder trabalho paralelo.
- **Evite commits triviais isolados:** pequenos ajustes esteticos devem ser agrupados em um unico commit de `style` ou `refactor`.

---

## 3. Hooks Locais — Lefthook

O [Lefthook](https://github.com/evilmartians/lefthook) executa validacoes automaticamente na maquina do desenvolvedor. Instalacao: `npm install` na raiz do repositorio (o script `prepare` roda `lefthook install` automaticamente).

| Hook         | Quando executa      | O que faz                                                                                                                                 |
| :----------- | :------------------ | :---------------------------------------------------------------------------------------------------------------------------------------- |
| `pre-commit` | A cada `git commit` | Roda ESLint + Prettier nos `.ts`/`.tsx` do frontend e Ruff nos `.py` do backend que estao em stage. Correcoes automaticas voltam ao stage. |
| `pre-push`   | A cada `git push`   | Valida se o nome da branch segue o padrao obrigatorio. Bloqueia o push caso contrario.                                                    |
| `commit-msg` | A cada `git commit` | Valida se a mensagem segue o Conventional Commits com escopo Jira obrigatorio via commitlint.                                             |

> Se um hook bloquear sua acao, leia a mensagem de erro, corrija o problema e tente novamente. **Nunca use `--no-verify`** para contornar os hooks.

---

## 4. Identificacao por Ticket Jira

O ticket Jira deve estar presente tanto no **nome da branch** quanto na **mensagem de commit**. A chave do projeto e `FC404`.

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

## Referencia Rapida

| O que fazer              | Como fazer                                                              |
| :----------------------- | :---------------------------------------------------------------------- |
| Instalar os hooks        | `npm install` na raiz do repositorio                                    |
| Criar uma nova branch    | `git checkout -b feat/FC404-XX_nome-da-feature` a partir de `develop`  |
| Commitar com o padrao    | `git commit -m "feat(FC404-XX): descricao"`                             |
| Validar branch           | O `pre-push` valida automaticamente ao rodar `git push`                 |
| Abrir um PR              | Da sua branch para `develop` — veja [processo-pr.md](processo-pr.md)   |
