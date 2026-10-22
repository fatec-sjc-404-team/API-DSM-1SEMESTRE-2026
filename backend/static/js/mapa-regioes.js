// Mapa da página inicial: ao clicar numa região, atualiza o card com os estados dela.
document.addEventListener('DOMContentLoaded', () => {
  const dadosRegioes = {
    Norte: 'AC, AM, AP, PA, RO, RR, TO',
    Nordeste: 'AL, BA, CE, MA, PB, PE, PI, RN, SE',
    CentroOeste: 'GO, MT, MS, DF',
    Sudeste: 'ES, MG, RJ, SP',
    Sul: 'PR, RS, SC',
  };

  const regioesSvg = document.querySelectorAll('.regiao');
  const tituloCard = document.getElementById('card-titulo');
  const estadosCard = document.getElementById('card-estados');

  // Adiciona o evento de clique só se o mapa existir na tela
  if (regioesSvg.length > 0) {
    regioesSvg.forEach((regiao) => {
      regiao.addEventListener('click', (evento) => {
        // Limpa a cor de todos
        regioesSvg.forEach((r) => r.classList.remove('ativa'));

        // Pinta a região clicada (DOM element)
        const regiaoClicada = evento.target;
        regiaoClicada.classList.add('ativa');

        // Atualiza o texto dinamicamente
        const nomeRegiao = regiaoClicada.id;
        tituloCard.textContent = nomeRegiao;
        estadosCard.textContent = dadosRegioes[nomeRegiao] || '';
      });
    });
  }
});
