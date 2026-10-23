# Filtros da página de gráficos

Orientação curta para ajustar os filtros já existentes em
[`graficos.html`](../../backend/templates/graficos.html), usando as colunas da
tabela [`BCB`](../../backend/database/AvoData.sql).

## Reaproveitar os filtros atuais

| Filtro atual | O que fazer | Opções |
| --- | --- | --- |
| Região | Manter | Todos, Norte, Nordeste |
| Estado | Manter | Todos e UFs existentes: AC, AM, AP, PA, RO, RR, TO, AL, BA, CE, MA, PB, PE, PI, RN, SE. O estado deve corresponder à região selecionada. |
| Período | Manter | Último 1 mês até últimos 12 meses, como já está na página. |
| Prazo | Manter e ajustar os nomes | Todos; até 90 dias, 91–360 dias, 361–1.080 dias, 1.081–1.800 dias, 1.801–5.400 dias, acima de 5.400 dias, vencidos de 15–90 dias e vencidos acima de 90 dias. |
| Tipo de Carteira | Renomear para **Indicador** | Carteira a vencer, carteira vencida, carteira ativa, carteira em inadimplência, ativo problemático ou número de operações. |

Na página atual, “Tipo de Carteira” representa uma **métrica do gráfico**, não
um filtro de categoria. Por isso, o nome **Indicador** é mais claro. O seletor
de período pode continuar com as opções existentes.

### Nomes sugeridos para as opções de prazo

Os nomes exibidos podem ser simples e parecidos com as colunas do banco. Não é
necessário repetir “A vencer” em cada opção:

- **Todos**
- **Até 90 dias**
- **91–360 dias**
- **361–1.080 dias**
- **1.081–1.800 dias**
- **1.801–5.400 dias**
- **Acima de 5.400 dias**
- **Vencidos: 15–90 dias**
- **Vencidos: acima de 90 dias**

Para “Indicador”, use nomes claros e próximos dos termos do banco, como
**Carteira em inadimplência** e **Número de operações**.

## Filtros opcionais para uma próxima etapa

Quando fizermos funcionar a primeira etapa

Podem ser adicionados depois, se forem úteis para os gráficos:

| Filtro | Coluna | Opções |
| --- | --- | --- |
| Segmento | `segmento` | Todos + valores existentes na base |
| Cliente | `cliente` | Todos + valores existentes na base |
| Porte | `porte` | Todos + valores existentes na base |
| Atividade/ocupação | `cnae_ocupacao` | Todos + valores existentes na base; incluir busca, pois pode haver muitas opções |
| Modalidade | `modalidade` | Todas + valores existentes na base |
| Submodalidade | `submodalidade` | Todas + valores existentes na base, filtradas pela modalidade escolhida |
| Origem | `origem` | Todas + valores existentes na base |
| Indexador | `indexador` | Todos + valores existentes na base |

O SQL não lista os valores possíveis desses campos. As opções devem vir dos
dados reais, em vez de serem inventadas ou escritas manualmente.

