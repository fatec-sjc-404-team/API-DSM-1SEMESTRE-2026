document.addEventListener('DOMContentLoaded', () => {
  
  const checkboxEstado = document.getElementById('estado');
  const grupoEstado = document.getElementById('group-by-state');

  if (checkboxEstado && grupoEstado) {
    function visibleState() {
      grupoEstado.style.display = checkboxEstado.checked ? '' : 'none';
    }

    visibleState();
    
    checkboxEstado.addEventListener('change', visibleState);
  }

  const VERDE = '#2e7d32';
  const ESTADOS = { AL: 57.4, BA: 64.2, CE: 68.9, MA: 53.1, PB: 59.7, PE: 66.3, PI: 50.8, RN: 63.5, SE: 55.9 };
  const SEMANAS = ['Sem 29', 'Sem 30', 'Sem 31', 'Sem 32', 'Sem 33', 'Sem 34', 'Sem 35', 'Sem 36', 'Sem 37'];
  const SERIE = [51.2, 53.5, 55, 56.8, 58.3, 59.7, 61, 62.2, 62.2];

  const rotulos = {
    id: 'rotulos',
    afterDatasetsDraw(c) {
      const x = c.ctx; x.save();
      x.fillStyle = '#333'; x.font = '11px sans-serif'; x.textAlign = 'center';
      c.getDatasetMeta(0).data.forEach((b, i) => x.fillText(c.data.datasets[0].data[i], b.x, b.y - 6));
      x.restore();
    }
  };

  const canvasBarras = document.getElementById('barras');
  if (canvasBarras && canvasBarras.tagName === 'CANVAS') {
    new Chart(canvasBarras, {
      type: 'bar',
      data: {
        labels: Object.keys(ESTADOS),
        datasets: [{ data: Object.values(ESTADOS), backgroundColor: VERDE, borderRadius: 3, barPercentage: .8, categoryPercentage: .8 }]
      },
      options: {
        responsive: true, maintainAspectRatio: false, layout: { padding: { top: 18 } },
        plugins: { legend: { display: false }, tooltip: { displayColors: false } },
        scales: { y: { min: 0, max: 100 }, x: { grid: { display: false } } }
      },
      plugins: [rotulos]
    });
  }

  const canvasLinha = document.getElementById('linha');
  if (canvasLinha && canvasLinha.tagName === 'CANVAS') {
    new Chart(canvasLinha, {
      type: 'line',
      data: {
        labels: SEMANAS,
        datasets: [{ label: 'Potencial Geral', data: SERIE, borderColor: VERDE, backgroundColor: VERDE, pointRadius: 4, tension: 0 }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { min: 40, max: 80 }, x: { grid: { display: false } } }
      }
    });
  }

  const dadosRegioes = {
    Norte: "AC, AM, AP, PA, RO, RR, TO",
    Nordeste: "AL, BA, CE, MA, PB, PE, PI, RN, SE",
    CentroOeste: "GO, MT, MS, DF",
    Sudeste: "ES, MG, RJ, SP",
    Sul: "PR, RS, SC"
  };

  const regioesSvg = document.querySelectorAll('.regiao');
  const tituloCard = document.getElementById('card-titulo');
  const estadosCard = document.getElementById('card-estados');

  // Adiciona o evento de clique só se o mapa existir na tela
  if (regioesSvg.length > 0) {
    regioesSvg.forEach(regiao => {
      regiao.addEventListener('click', (evento) => {
        // Limpa a cor de todos
        regioesSvg.forEach(r => r.classList.remove('ativa'));
        
        // Pinta a região clicada (DOM element)
        const regiaoClicada = evento.target;
        regiaoClicada.classList.add('ativa');
        
        // Atualiza o texto dinamicamente
        const nomeRegiao = regiaoClicada.id;
        tituloCard.textContent = nomeRegiao;
        estadosCard.textContent = dadosRegioes[nomeRegiao] || "";
      });
    });
  }

});