import matplotlib.pyplot as plt

#1 DADOS
segmentos = [
    "Edividamento de risco",
    "Inadimplência — critério do estudo de\nendividamento de risco"
]

norte = [15.9, 18.1]
nordeste = [14.4, 16.8]

#Cria posições
posicoes = list(range(len(segmentos))) #variavel que cria a possição 0 1 

largura = 0.43 # define a largura de cada barra

# Definir a tela do grafica=o
fig, ax = plt.subplots(figsize=(9, 5))

#cria barras
barras_norte = ax.bar(
    [p - largura / 2 for p in posicoes], norte, largura, label="Norte")

barras_nordeste = ax.bar(
    [p + largura / 2 for p in posicoes], nordeste, largura, label="Nordeste")

#Define formato de porcentagem para os dados
ax.bar_label(barras_norte, fmt="%.2f%%")
ax.bar_label(barras_nordeste, fmt="%.2f%%")

#acabamento
ax.set_xticks(posicoes)
ax.set_xticklabels(segmentos)
ax.set_ylabel("Endividamento de risco (%)")
ax.set_title("Risco por região: Norte vs Nordeste")
ax.legend()

plt.tight_layout()

plt.savefig("grafico_endividamento_risco.png", dpi=300)

# Exibe o gráfico
plt.show()