import matplotlib.pyplot as plt


# 1 DADOS
segmentos = [
    "Pessoas fiísicas\ncrédito livre",
    "Pessoas fíísicas\ncrédito direcionado",
    "Pessoas jurídicas\ncrédito livre",
]

norte = [14.3, 10.2, 2.2]
nordeste = [12.0, 12.2, 5.8]


# 2  POSIÇÕES DAS BARRAS
posicoes = list(range(len(segmentos))) # cria uma variável com os índices dos segmentos para com possição 0 1 2

largura = 0.35 # Define a largura das barras e o tamanho do gráfico

# 3) DESENHO
fig, ax = plt.subplots(figsize=(9, 5)) #define o tamanho da tela do gráfico


# Cria as barras para cada região
barras_norte = ax.bar(
    [p - largura / 2 for p in posicoes], norte, largura, label="Norte")
barras_nordeste = ax.bar(
    [p + largura / 2 for p in posicoes], nordeste, largura, label="Nordeste")

# Adiciona os rótulos de valor nas barras
ax.bar_label(barras_norte, fmt="%.2f%%")
ax.bar_label(barras_nordeste, fmt="%.2f%%")


# 4) ACABAMENTO
# Adiciona rótulos, título e legenda
ax.set_xticks(posicoes)
ax.set_xticklabels(segmentos)
ax.set_ylabel("Taxa de inadimplência (%)")
ax.set_title("Inadimplência por segmento: Norte vs Nordeste")
ax.legend()

plt.tight_layout()

# Salva o gráfico em um arquivo PNG
plt.savefig("grafico_inadimplencia.png", dpi=300)

# Exibe o gráfico
plt.show()