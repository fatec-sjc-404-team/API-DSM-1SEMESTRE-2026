# regras de indicador

**Data:** 2026-09-18
**Autor:** Fernando
**Participantes:** Isabela
**Facilitador:**

---

# O que são as regras de indicador

Em análise de crédito, regras de indicador são condições lógicas e parâmetros quantitativos, que são aplicados sobre métricas para disparar ações automáticas, alertas ou fazer decisões.

Elas funcionam em formata condicional: **Se** [Indicador], **atender à** [Condição/Limite], **então** [Ação/Classificação].


## Regra de crédito caro

- ### O que é:

É um parâmetro restritivo utilizado pelas instituições financeiras (Bancos, cooperativas de crédito), para avaliar a saúde financeira e a capacidade de pagamento de um proponente antes de aprovar uma nova operação.

- ###  Como funciona:

Essa regra analisa se o cliente possui dívidas ativas ou algum histórico recorrente, principalmente o roativo do cartão de crédito e o cheque especial. Se esse for o caso, a instituição recusa o cliente por mostrar um forte sinal de estresse e descontrole financeiro. 

- ### A aplicação: 

- Regra eliminatória: 
 Se o cliente estiver usando mais de um percentual crítico do cheque especial, ou rolando a fatura do cartão há mais de 30/60 dias, a concessão de novos empréstimos ou cartões é recusada.

- Regra de precificação:
 Caso o crédito não seja recusado imdiatamente, a presença de dívida cara rebaixa a avaliação interna do cliente, reduzindo o limite aprovado ou exigindo garantias adicionais para compensar o risco.

- Operação de consolidação: 
 É uma renegociação com o cliente, quando ele quer pagar a dívida, mas não tem condições de fazer isso com o salário que recebe. Então a instituição financeira parcela a dívida em parcelas menores que ele vai conseguir pagar, mas em um prazo maior. 


 ## Regra de endividamento por apostas

- ### O que é:

É uma análise comportamental para indentificar se o cliente está usando recursos financeiros, próprios ou de terceiros, para sustentar plataformas de apostas online.

- ### Como o banco enxerga isso:

Apostas online entram na categoria de risco sistêmico de perda rápida de liquidez, enquanto no modelo tradicional, o banco olha se você tem renda e se paga as contas em dia.

- Assimetria de perda:
 Quando alguém financia um carro ou reforma uma casa, há um bem tangível, ou um patrimônio agregado. Mas o dinheiro destinado a apostas tem uma expectativa estatistica negativa e volatilidade extrema.

- Comportamento compulsivo:
 O motor de crédito monitora a tentativa de "recuperar o prejuízo". Quando algúem perde, a tendência observada é tomar um empréstimo de curto prazo para cointinuar apostando.

- Risco de contágio de despesas essenciais:
 O apostador descontrolado frequentemente sacrifica moradia, alimentação ou contas básicas para manter o saldo na casa de apostas.

- ### Como funciona:

A regra é configurada por meio de variáveis e gatilhos automatizados em motores decisão.

- Mapeamento de transações:
 O sistema rastreia transações via cartão e transferências Pix para CNPJs cadastrados como casas de apostas.

- Métrica de comprometimento:
 - Volume absoluto: Calcula o percentual de renda líquida destinada a essas casas de apostas no mês.

 - Frequência e horário: Múltiplas transferências no mesmo dia, repasses imediatos após o recebimento do salário disparam alertas de risco comportamental.

- Ações disparadas pela política:
 - Recusa automática: Se o cliente já estiver com cheque especial ou crédito pré aprovado e, logo em seguida, transferindo para a casa de apostas, novos limites solicitados são automaticamente negados.

 - Redução preventiva de limite: Limites de cartão e cheque especial são cortados para limitar a exposição do banco a uma perda inevitável.

 - Punição no Score Interno: O cliente é rebaixado da faixa de risco, mesmo que o CPF ainda esteja sem negativação em birôs como o Serasa ou SPC.

- ### A Aplicação: