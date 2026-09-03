# Jira — Fluxo de Trabalho e Gestão de Cards

Este documento descreve como usar o Jira durante a Sprint: o que cada status significa, quem move o card e quando, e como preencher os campos de uma tarefa.

---

## 1. Campos de uma Tarefa

Ao criar ou abrir um card, preencha os campos conforme abaixo:

| Campo | Obrigatório | Descrição |
| :---- | :---------: | :-------- |
| **Description** | Sim | O que precisa ser feito, critérios de aceite e contexto necessário para o dev começar |
| **Assignee** | Sim | O desenvolvedor responsável pela tarefa |
| **Parent** | Sim | A User Story ou Épico ao qual essa tarefa pertence |
| **Sprint** | Sim | A Sprint na qual a tarefa será executada |
| **Priority** | Sim | Nível de urgência: Highest, High, Medium, Low, Lowest |
| **Labels** | Sim | Categoria da tarefa — obrigatório conforme configuração do projeto |
| **Story point estimate** | Sim | Estimativa de esforço em pontos acordada durante o Planning |
| **Due date** | Não | Prazo específico, se aplicável |
| **Start date** | Não | Data de início, se aplicável |
| **Reporter** | Automático | Preenchido automaticamente com quem criou o card |

---

## 2. Board — Colunas e Significado

O board tem 7 colunas. Cada uma representa um estado claro da tarefa:

| Status | Responsável | O que significa |
| :----- | :---------- | :-------------- |
| **To Do** | — | Tarefa planejada para a Sprint, ainda não iniciada |
| **In Progress** | Dev | Desenvolvimento em andamento |
| **Peer Review** | Dev | PR aberto no GitHub, aguardando revisão de colegas |
| **Blocked** | Qualquer um | Tarefa impedida por dependência externa, dúvida sem resposta ou reprovação em QA |
| **Ready for QA** | Dev | PR aprovado e mergeado em `develop`, pronto para validação |
| **QA in Progress** | PO / SM | PO ou SM está validando a funcionalidade |
| **Done** | Dev / PO / SM | Tarefa concluída e aprovada em QA |

---

## 3. Fluxo de Movimentação

O dev é responsável por mover o próprio card em todas as etapas até o QA. O PO/SM assume a partir do QA in Progress.

```text
To Do
  └─► In Progress        (dev cria a branch e começa o desenvolvimento)
            └─► Peer Review     (dev abre o PR no GitHub)
                      └─► Ready for QA    (PR aprovado e mergeado em develop)
                                └─► QA in Progress  (PO/SM inicia a validação)
                                          └─► Done          (aprovado em QA)
```

### Quando mover cada card

| Transição | Quem move | Quando mover |
| :-------- | :-------- | :----------- |
| To Do → **In Progress** | Dev | Ao criar a branch de trabalho |
| In Progress → **Peer Review** | Dev | Ao abrir o PR no GitHub |
| Peer Review → **Ready for QA** | Dev | Após o PR ser aprovado e mergeado em `develop` |
| Ready for QA → **QA in Progress** | PO / SM | Ao começar a validar a funcionalidade |
| QA in Progress → **Done** | PO / SM | Após validação aprovada |
| Qualquer status → **Blocked** | Qualquer um | Ao identificar um impedimento |

---

## 4. Reprovação em QA

Se o PO ou SM identificar um problema durante o QA, o card **não volta diretamente para In Progress**. O fluxo correto é:

1. PO/SM move o card para **Blocked**
2. PO/SM adiciona um **comentário no card** descrevendo o problema encontrado
3. Dev lê o comentário, corrige o problema e reabre o PR (ou cria um novo commit no PR existente)
4. Dev move o card de volta para **In Progress** e segue o fluxo normal

> Usar **Blocked** em vez de voltar direto para In Progress mantém o histórico visível e deixa claro para o time que aquela tarefa teve uma reprovação.

---

## 5. Coluna Blocked

O status **Blocked** pode ser aplicado a partir de qualquer outro status e serve para dois casos:

- **Impedimento externo:** dependência de outra tarefa, dúvida sem resposta, aguardando decisão
- **Reprovação em QA:** funcionalidade não passou na validação do PO/SM

Sempre que um card for movido para Blocked, adicione um comentário explicando o motivo. Sem comentário, o time não sabe o que está impedindo.

---

## 6. Integração Jira + GitHub

O Jira possui integração com o GitHub, mas **não utilize a criação de branches diretamente pelo Jira**. A integração gera nomes de branch em um formato diferente do padrão do projeto, que seria rejeitado pelo hook `pre-push` e pelo workflow Branch Name Check.

Crie sempre a branch manualmente seguindo o padrão documentado em [fluxo-git.md](fluxo-git.md):

```text
<tipo>/FC404-XX_titulo-do-ticket
```

A rastreabilidade entre o card e os commits é garantida pelo ticket Jira no escopo de cada commit (`tipo(FC404-XX): descricao`), não pela integração automática de branch.
