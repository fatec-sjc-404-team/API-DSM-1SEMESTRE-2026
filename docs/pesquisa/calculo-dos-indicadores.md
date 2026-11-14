# calculo-dos-indicadores

**Data:** 2026-11-08
**Autor:** Pedro Henrique Cabral Leite
**Status:** Proposta, aguardando validação do grupo
**Jira:** FC404-94 (US01), FC404-97 (US02), FC404-132, FC404-133

---

# Por que as regras precisaram ser adaptadas

As regras de [regras-de-indicador.md](regras-de-indicador.md) falam de **um cliente**: data de pagamento de cada dívida, saldo do cheque especial, transferências Pix para casas de apostas.

A tabela `BCB` (SCR.data) não tem nada por cliente. Ela traz **saldos somados** por mês, UF, modalidade e submodalidade do crédito, com faixas de vencimento. Então cada regra foi traduzida para uma porcentagem que dá para calcular com esses saldos, por região e por estado.

O código fica em `backend/indicadores.py` (cálculo) e `backend/dados.py` (classificação das modalidades).

---

# Os indicadores menores (US01)

| Indicador | Regra original | Como é calculado | Campo na API |
| :--- | :--- | :--- | :--- |
| Dívida saudável x crítica | Classificar o crédito pela finalidade | % da carteira ativa em cada tipo (`classificar_tipo_divida`) | `pct_saudavel`, `pct_critica`, `pct_mista` |
| Crédito caro | Cliente com rotativo do cartão e cheque especial é sinal de estresse financeiro | carteira ativa de crédito caro / carteira ativa × 100 | `pct_credito_caro` |
| Recuperação rápida | Dívida quitada de 1 a 20 dias depois do vencimento | vencido de 15 a 90 dias / (vencido de 15 a 90 + vencido acima de 90) × 100 | `pct_recuperacao_rapida` |
| Endividamento por apostas | Gasto em apostas / renda líquida | **Ainda não calculado**: não há dados de apostas (depende da US08) | — |

## Crédito caro

Submodalidades consideradas crédito caro (`SUBMODALIDADES_CREDITO_CARO` em `dados.py`):

- Cartão de crédito - não migrado (rotativo)
- Crédito rotativo vinculado a cartão de crédito
- Cheque especial
- Adiantamentos a depositantes (conta que ficou negativa)

Toda essa carteira também é "crítica", mas nem toda dívida crítica é crédito caro: a **fatura parcelada** do cartão fica de fora porque tem juros menores e, pela regra, funciona como operação de consolidação da dívida.

## Recuperação rápida

O SCR não tem datas de pagamento, e a primeira faixa de atraso começa em 15 dias. Por isso a janela da regra (1 a 20 dias) foi aproximada pela faixa de **15 a 90 dias**: é o atraso que ainda não virou inadimplência (acima de 90 dias).

Quanto maior a porcentagem, mais do atraso da região está no começo, ou seja, ainda pode ser recuperado. Se o grupo não tem nada vencido, o indicador fica `null` (não se aplica).

**Limitação:** isso mede o atraso inicial num mês, não se a dívida foi de fato quitada. Para medir a quitação seria preciso comparar meses seguidos ou ter dados por cliente.

---

# O indicador geral (US02)

Cada indicador menor vira uma nota de 0 a 100 (maior é melhor), e o indicador geral é a **média simples** das notas:

| Indicador | Nota |
| :--- | :--- |
| Crédito caro | `100 - pct_credito_caro` |
| Dívida saudável x crítica | `50 + (pct_saudavel - pct_critica) / 2` → 100 tudo saudável, 0 tudo crítico, 50 tudo misto |
| Recuperação rápida | `pct_recuperacao_rapida` (fica fora da média quando é `null`) |
| Endividamento por apostas | entra como mais uma nota quando a US08 trouxer os dados |

Exemplo com os dados de teste (geral sem filtros): `(94,34 + 75,47 + 55,37) / 3 = 75,06`.

A taxa de inadimplência continua na resposta, mas **não entra** no geral, porque não é um dos 4 indicadores da US01.

---

# Pontos para o grupo decidir

1. A lista de submodalidades de crédito caro está certa?
2. A faixa de 15 a 90 dias é uma boa aproximação para a recuperação rápida?
3. Os pesos devem ser iguais? Como crédito caro faz parte da dívida crítica, uma região com muito crédito caro perde nota nos dois indicadores.
4. Quando a coleta de apostas existir (US08), como ela vira nota de 0 a 100?
