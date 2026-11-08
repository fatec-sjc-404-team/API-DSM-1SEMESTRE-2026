// Gráficos da página "Gráficos" (Chart.js é carregado no base.html).
document.addEventListener('DOMContentLoaded', () => {
  const filtroRegiao = document.getElementById('filtro-regiao');
  const filtroEstado = document.getElementById('filtro-estado');

  if (filtroRegiao && filtroEstado) {
    const atualizarEstados = () => {
      const regiaoSelecionada = filtroRegiao.value;

      filtroEstado.querySelectorAll('optgroup[data-regiao]').forEach((grupo) => {
        grupo.hidden = regiaoSelecionada !== 'todos'
          && grupo.dataset.regiao !== regiaoSelecionada;
      });

      const grupoEstadoSelecionado = Array.from(
        filtroEstado.querySelectorAll('optgroup[data-regiao]'),
      ).find((grupo) =>
        Array.from(grupo.querySelectorAll('option')).some(
          (opcao) => opcao.value === filtroEstado.value,
        ),
      );

      if (
        grupoEstadoSelecionado
        && regiaoSelecionada !== 'todos'
        && grupoEstadoSelecionado.dataset.regiao !== regiaoSelecionada
      ) {
        filtroEstado.value = '';
      }
    };

    filtroRegiao.addEventListener('change', atualizarEstados);
    atualizarEstados();
  }

  // ---- Dados dos gráficos vindos da API (FC404-159) ----
  // Os filtros do formulário são mandados para /api/indicadores e os gráficos
  // são desenhados com a resposta. Veja docs/pesquisa/calculo-dos-indicadores.md.

  const VERDE = '#2e7d32';
  const URL_INDICADORES = '/api/indicadores';

  // Filtros que a API entende (mesmos names do formulário).
  // O "prazo" ainda não existe na API, então não vai.
  const FILTROS_DA_API = ['regiao', 'estado', 'periodo', 'tipoDivida'];

  const NOMES_REGIAO = { norte: 'Norte', nordeste: 'Nordeste' };
  const NOMES_MES = [
    'jan', 'fev', 'mar', 'abr', 'mai', 'jun',
    'jul', 'ago', 'set', 'out', 'nov', 'dez',
  ];

  // Opções do select do gráfico de linha -> campo da resposta da API.
  const INDICADORES_DA_LINHA = {
    potencial: { campo: 'indicador_geral', nome: 'Potencial de Crédito' },
    recuperacao: { campo: 'pct_recuperacao_rapida', nome: 'Recuperação Rápida (%)' },
    credito: { campo: 'pct_credito_caro', nome: 'Crédito Caro (%)' },
    divida: { campo: 'pct_saudavel', nome: 'Dívida Saudável (%)' },
  };

  const formulario = document.getElementById('painel-filtros-container');
  const seletorLinha = document.getElementById('seletor-linha');
  const aviso = document.getElementById('graficos-aviso');
  const subBarras = document.getElementById('sub-barras');
  const tituloLinha = document.getElementById('titulo-linha');
  const dataAtualizacao = document.getElementById('data-atualizacao');

  const rotulos = {
    id: 'rotulos',
    afterDatasetsDraw(c) {
      const x = c.ctx;
      x.save();
      x.fillStyle = '#333';
      x.font = '11px sans-serif';
      x.textAlign = 'center';
      c.getDatasetMeta(0).data.forEach((b, i) => {
        const valor = c.data.datasets[0].data[i];
        if (valor !== null && valor !== undefined) {
          x.fillText(valor.toFixed(1), b.x, b.y - 6);
        }
      });
      x.restore();
    },
  };

  let graficoBarras = null;
  const canvasBarras = document.getElementById('barras');
  if (canvasBarras && canvasBarras.tagName === 'CANVAS') {
    graficoBarras = new Chart(canvasBarras, {
      type: 'bar',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Potencial de crédito',
            data: [],
            backgroundColor: VERDE,
            borderRadius: 3,
            barPercentage: 0.8,
            categoryPercentage: 0.8,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: { padding: { top: 18 } },
        plugins: { legend: { display: false }, tooltip: { displayColors: false } },
        scales: { y: { min: 0, max: 100 }, x: { grid: { display: false } } },
      },
      plugins: [rotulos],
    });
  }

  let graficoLinha = null;
  const canvasLinha = document.getElementById('linha');
  if (canvasLinha && canvasLinha.tagName === 'CANVAS') {
    graficoLinha = new Chart(canvasLinha, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: INDICADORES_DA_LINHA.potencial.nome,
            data: [],
            borderColor: VERDE,
            backgroundColor: VERDE,
            pointRadius: 4,
            tension: 0,
            spanGaps: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { min: 0, max: 100 }, x: { grid: { display: false } } },
      },
    });
  }

  // Última resposta da API: trocar o select da linha redesenha sem buscar de novo.
  let ultimaResposta = null;
  // Se dois pedidos se cruzarem, só o mais recente desenha.
  let ultimoPedido = 0;

  function montarParametros() {
    const parametros = new URLSearchParams();
    if (!formulario) {
      return parametros;
    }

    const campos = new FormData(formulario);
    FILTROS_DA_API.forEach((nome) => {
      const valor = campos.get(nome);
      if (valor) {
        parametros.set(nome, valor);
      }
    });
    return parametros;
  }

  function mostrarAviso(texto) {
    if (aviso) {
      aviso.textContent = texto;
      aviso.hidden = !texto;
    }
  }

  function nomeDoMes(dataBase) {
    const [ano, mes] = dataBase.split('-');
    return `${NOMES_MES[Number(mes) - 1]}/${ano.slice(2)}`;
  }

  function dataBrasileira(dataBase) {
    const [ano, mes, dia] = dataBase.split('-');
    return `${dia}/${mes}/${ano}`;
  }

  function descreverLocal(filtros) {
    if (filtros.estado) {
      return `o estado ${filtros.estado}`;
    }
    if (filtros.regiao) {
      return `a região ${NOMES_REGIAO[filtros.regiao] || filtros.regiao}`;
    }
    return 'as regiões Norte e Nordeste';
  }

  function desenharBarras(resposta) {
    if (!graficoBarras) {
      return;
    }
    const estados = Object.keys(resposta.por_estado).sort();
    graficoBarras.data.labels = estados;
    graficoBarras.data.datasets[0].data = estados.map(
      (uf) => resposta.por_estado[uf].indicador_geral ?? null,
    );
    graficoBarras.update();

    if (subBarras) {
      subBarras.textContent = `Comparativo entre os estados (${descreverLocal(resposta.filtros)})`;
    }
  }

  function desenharLinha(resposta) {
    if (!graficoLinha) {
      return;
    }
    const escolhido = INDICADORES_DA_LINHA[seletorLinha?.value]
      || INDICADORES_DA_LINHA.potencial;
    const meses = Object.keys(resposta.por_mes).sort();

    graficoLinha.data.labels = meses.map(nomeDoMes);
    graficoLinha.data.datasets[0].label = escolhido.nome;
    graficoLinha.data.datasets[0].data = meses.map(
      (mes) => resposta.por_mes[mes][escolhido.campo] ?? null,
    );
    graficoLinha.update();

    if (tituloLinha) {
      tituloLinha.textContent = `Evolução de ${escolhido.nome} — ${descreverLocal(resposta.filtros)}`;
    }
  }

  function desenhar(resposta) {
    desenharBarras(resposta);
    desenharLinha(resposta);

    if (dataAtualizacao && resposta.ultima_data_base) {
      dataAtualizacao.textContent = `Dados atualizados em ${dataBrasileira(resposta.ultima_data_base)}`;
    }
    const semDados = Object.keys(resposta.por_estado).length === 0;
    mostrarAviso(semDados ? 'Nenhum dado encontrado para esses filtros.' : '');
  }

  // Busca os indicadores com os filtros do formulário e redesenha os gráficos.
  // Pode ser chamada de fora (ex.: ao trocar um filtro, FC404-154).
  async function aplicarFiltros() {
    const pedido = ++ultimoPedido;
    try {
      const resposta = await fetch(`${URL_INDICADORES}?${montarParametros()}`);
      const corpo = await resposta.json();
      if (pedido !== ultimoPedido) {
        return;
      }
      if (!resposta.ok) {
        throw new Error(corpo.erro || `erro ${resposta.status}`);
      }
      ultimaResposta = corpo;
      desenhar(corpo);
    } catch (erro) {
      if (pedido === ultimoPedido) {
        mostrarAviso(`Não foi possível carregar os gráficos: ${erro.message}`);
      }
    }
  }
  window.aplicarFiltrosGraficos = aplicarFiltros;

  if (formulario) {
    formulario.addEventListener('submit', (evento) => {
      evento.preventDefault();
      aplicarFiltros();
    });
  }

  if (seletorLinha) {
    seletorLinha.addEventListener('change', () => {
      if (ultimaResposta) {
        desenharLinha(ultimaResposta);
      }
    });
  }

  if (graficoBarras || graficoLinha) {
    aplicarFiltros();
  }
});
