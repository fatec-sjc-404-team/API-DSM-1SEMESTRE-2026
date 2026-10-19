const VERDE = '#2e7d32';

const ESTADOS = { AL: 57.4, BA: 64.2, CE: 68.9, MA: 53.1, PB: 59.7, PE: 66.3, PI: 50.8, RN: 63.5, SE: 55.9 };
const SEMANAS = ['Sem 29 (14/07)', 'Sem 30 (21/07)', 'Sem 31 (28/07)', 'Sem 32 (04/08)', 'Sem 33 (11/08)',
                 'Sem 34 (18/08)', 'Sem 35 (25/08)', 'Sem 36 (01/09)', 'Sem 37 (08/09)'];
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

new Chart(document.getElementById('barras'), {
  type: 'bar',
  data: {
    labels: Object.keys(ESTADOS),
    datasets: [{ data: Object.values(ESTADOS), backgroundColor: VERDE, borderRadius: 3, barPercentage: .8, categoryPercentage: .8 }]
  },
  options: {
    responsive: true, maintainAspectRatio: false, layout: { padding: { top: 18 } },
    plugins: { legend: { display: false }, tooltip: { displayColors: false, callbacks: { label: c => 'Potencial : ' + c.parsed.y } } },
    scales: { y: { min: 0, max: 100, ticks: { stepSize: 25 }, grid: { color: 'rgba(128,128,128,.15)' } }, x: { grid: { display: false } } }
  },
  plugins: [rotulos]
});

new Chart(document.getElementById('linha'), {
  type: 'line',
  data: {
    labels: SEMANAS,
    datasets: [{ label: 'Potencial Geral', data: SERIE, borderColor: VERDE, backgroundColor: VERDE, pointRadius: 4, tension: 0 }]
  },
  options: {
    responsive: true, maintainAspectRatio: false, interaction: { mode: 'index', intersect: false },
    plugins: { legend: { display: false } },
    scales: { y: { min: 40, max: 80, ticks: { stepSize: 10 }, grid: { color: 'rgba(128,128,128,.15)' } }, x: { grid: { display: false } } }
  }
});
