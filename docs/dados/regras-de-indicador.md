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

- **Ingestão e Identificação dos dados**

É necessário capturar as transações via extrato bancário ou fatura do cartão:

- MCC (Merchant Category Code): Filtrar compras no cartão com códigos de jogos de azar e apostas.
 
- CNPJs credenciados: Cruzar chaves Pix e transferências com a base de CNPJs de operadoreas autorizadas de apostas.

- **Criação das variáveis**

Transforma os dados brutos em métricas quantitativas de risco:

- Comprometimento de Renda (Gambling-to-income):
    GTI = (Total gasto em apostas no mês / Renda líquida estimada) * 100

- Velocidade de Gasto: Quantidade de depósitos em casas de aposta em janelas curtas

- Uso de Linhas Emergenciais: Se o Pix para a casa de apostas foi feito enquanto a conta estava negativa (usando cheque especial) ou logo após um saque de cartão de crédito.

- **Definição dos limiares lógicos**

No motor de decisão, configure as regras condicionais:

- Nível 1: Recusa Sumária (Hard Rule / Knockout)

``` SE (Saldo_Cheque_Especial > 0 E Gasto_Apostas_30d > 0) ENTÃO Recusar_Novo_Crédito```

```SE (GTI > 25%) ENTÃO Recusar_Novo_Crédito```

- Nível 2: Redução Preventiva de Exposição

```SE (GTI > 15% E Score_Biro >= 700) ENTÃO Reduzir_Limite_Cartao_em_50%```

- Nível 3: Punição no Score Interno

```SE (Frequencia_Apostas >= 5 transações/semana) ENTÃO Subtrair_Score_Interno(-80_pontos)```

- **Ações automatizadas**

A depender de onde o cliente está na jornada, o sistema dispara a ação correspondente:

- Na entrada (concessão): Reprova o pedido ou aprova apenas linhas com garantia real (consignado, veículo).

- Na base ativa (gestão de portfólio): Bloqueia aumentos automáticos de limite e reduz limites de cheque especial e rotativo para evitar o calote iminente.

##  Regra de Recuperação Rápida

### O que é:
É o indicador que mede a resiliência financeira do tomador. Considera-se dívida de recuperação rápida aquela que entra em atraso inicial, mas é totalmente quitada em até $20$ dias a partir do vencimento.

### Como funciona:
Calcula-se o intervalo de tempo entre a data de vencimento original e a data efetiva de pagamento. Se a quitação ocorrer dentro da janela de $1$ a $20$ dias após o vencimento, a operação é classificada como recuperação rápida.

### Como o banco enxerga isso:
Os bancos tradicionais geralmente tratam qualquer dia de atraso como inadimplência pura. Sob a ótica do crédito inclusivo, entende-se que imprevistos de fluxo de caixa são comuns na base da pirâmide e que quem paga em até $20$ dias demonstra comprometimento e alta capacidade de reequilíbrio, não sendo um mau pagador crônico.

## tenho que colocar aplicacao

---

##  Regra de Dívida Saudável x Crítica

### O que é:
É a classificação do perfil de endividamento com base na finalidade do crédito tomado. Separa o que gera patrimônio/desenvolvimento daquilo que apenas cobre buracos de consumo imediato.

### Como funciona:
Categoriza-se as linhas de crédito disponíveis:
* **Dívida Saudável:** Créditos voltados à construção de patrimônio, investimentos de longo prazo ou crédito produtivo (Ex: financiamento de imóveis).
* **Dívida Crítica:** Créditos voltados ao consumo imediato ou linhas de emergência com juros abusivos (Ex: rotativo de cartão de crédito e cheque especial).

### Como o banco enxerga isso:
O modelo tradicional olha apenas o volume total de dívidas e descarta o cliente se o montante for alto. A visão inclusiva diferencia a qualidade da dívida: um financiamento imobiliário alto indica investimento e estabilidade, enquanto um valor menor em cartão rotativo sinaliza alto risco de insolvência. O banco passa a enxergar a finalidade e o impacto real desse crédito na vida do tomador.

## tenho que colocar aplicacao
