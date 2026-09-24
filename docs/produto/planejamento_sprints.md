# Planejamento das 3 Sprints — AvoCredit (Norte/Nordeste)

---

# Sprint 1 — MVP com dado real + esboço de site

### Sprint Goal

Calcular os indicadores com dados reais de pelo menos duas regiões e apresentar um primeiro esboço de tela onde esses dados aparecem, já com uma direção visual definida.

## Épico 1 — Indicador de Crédito Alternativo

### US01 — Calcular os indicadores menores (completa)

- [x] [US01] Pesquisar os dados necessários
- [x] [US01] Definir a regra de cada indicador
- [x] [US01] Programar o cálculo dos 4 indicadores
- [x] [US01] Testar com dados reais de pelo menos 2 regiões

### US02 — Calcular o indicador geral (completa)

- [x] [US02] Decidir como juntar os 4 indicadores em um só número
- [x] [US02] Programar o cálculo do indicador geral usando os resultados da US01
- [x] [US02] Testar e ajustar com dados de exemplo

> **Por quê aqui:** sem US01 e US02, não existe "dado real" para mostrar — é a base de tudo, então precisa vir primeiro.

---

## Épico 2 — Ver os Dados e Gráficos (parcial)

### US03 — Consultar os dados por região

- [ ] [US03] Montar a consulta/tela que mostra o indicador geral por região e por estado
- [ ] [US03] Permitir ver cada indicador menor separadamente

> **Por quê aqui:** é literalmente o "esboço de site" pedido pelo cliente — a primeira tela navegável mostrando os números reais calculados acima.

---

## Épico 5 — Interface (parcial, antecipado propositalmente)

### US09 — Escolher e aplicar uma paleta de cores neutra (só a primeira task)

- [ ] [US09] Escolher, com o cliente, uma paleta de cores neutra

### US10 — Manter a navegação simples e direta (completa)

- [x] [US10] Garantir que não existe tela de login
- [x] [US10] Organizar as telas/blocos do notebook numa ordem lógica e fácil de seguir

> **Por quê aqui:** trazemos só a decisão da paleta e a estrutura de navegação para dentro da Sprint 1 (não a aplicação final da cor em tudo).

> Isso evita que o esboço da US03 saia "torto" e precise ser refeito visualmente depois.

> É a única antecipação de escopo do Épico 5, feita de propósito para sustentar a entrega combinada com o cliente.

---

# Sprint 2 — Interatividade e automação de dados

### Sprint Goal

Deixar a aplicação interativa (filtros e gráficos) e com a base de dados principal se atualizando sozinha toda semana.

## Épico 2 — Ver os Dados e Gráficos (finalização)

### US04 — Ver gráficos dos indicadores (completa)

- [x] [US04] Escolher a ferramenta de gráficos a ser usada no Colab
- [x] [US04] Fazer pelo menos dois tipos de gráfico
- [x] [US04] Ligar os gráficos aos filtros aplicados (US05)

---

## Épico 3 — Filtros (parcial)

### US05 — Aplicar filtros aos dados e gráficos (completa)

- [x] [US05] Definir os filtros disponíveis
- [x] [US05] Programar a aplicação dos filtros nos dados, indicadores e gráficos
- [x] [US05] Testar os filtros com diferentes combinações

> **Por quê nessa ordem:** [US04] Ligar os gráficos aos filtros depende de US05 existir — por isso os dois entram juntos na mesma sprint, e os filtros vêm sendo programados em paralelo aos gráficos.

---

## Épico 4 — Base de Dados (parcial)

### US07 — Atualizar os dados do BCB, IBGE e BACEN toda semana (completa)

- [x] [US07] Programar a coleta dos dados dessas três fontes
- [x] [US07] Limpar e organizar os dados
- [x] [US07] Programar a atualização semanal

> **Por quê aqui:** a Sprint 1 usou dados coletados manualmente/pontualmente para provar o cálculo; agora automatizamos a coleta das 3 fontes principais, sem travar a entrega da Sprint 1.

---

# Sprint 3 — Persistência, dado de apostas e refinamento final

### Sprint Goal

Fechar o backlog: usuário consegue salvar/reutilizar filtros, o indicador de apostas passa a ter dado real, e a interface recebe o acabamento final revisado com o cliente.

## Épico 3 — Filtros (finalização)

### US06 — Salvar e gerenciar filtros salvos (completa)

- [x] [US06] Programar o "salvar filtro"
- [x] [US06] Programar o "usar filtro salvo"
- [x] [US06] Programar editar e apagar filtros salvos

---

## Épico 4 — Base de Dados (finalização)

### US08 — Trazer dados sobre apostas (SPA, IBGE, Data Senado) (completa)

- [x] [US08] Pesquisar e programar a coleta de dados de apostas nessas fontes
- [x] [US08] Juntar essa coleta ao processo semanal (US07)
- [x] [US08] Tratar o caso de uma fonte estar fora do ar

> **Por quê aqui:** US08 reaproveita a lógica de atualização semanal criada em US07 (Sprint 2) — só faz sentido depois que ela já existe.

---

## Épico 5 — Interface (finalização)

### US09 — Escolher e aplicar uma paleta de cores neutra (task restante)

- [ ] [US09] Aplicar essa paleta em toda a aplicação e revisar com o cliente

> **Por quê aqui:** só faz sentido "aplicar em toda a aplicação" depois que todas as telas (indicadores, gráficos, filtros) já existirem — senão a paleta precisaria ser reaplicada de novo a cada nova tela criada nas sprints seguintes.

---

# Resumo da lógica de sequenciamento

| Sprint | Entrega principal ao cliente |
|---|---|
| **Sprint 1** | Indicadores calculados com dado real + esboço de tela navegável + estrutura/paleta definidas |
| **Sprint 2** | Aplicação interativa: gráficos + filtros funcionando + dados oficiais atualizando sozinhos |
| **Sprint 3** | Aplicação completa: filtros salvos, dado de apostas integrado, interface final revisada |