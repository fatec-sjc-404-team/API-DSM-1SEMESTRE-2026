// Página inicial: Potencial de Crédito por região e por estado.
//
// O usuário escolhe uma região (Norte ou Nordeste) e, se quiser, um estado dela.
// Os valores vêm de /api/indicadores, que calcula os indicadores com a base do
// BCB. As regras do cálculo estão em docs/pesquisa/calculo-dos-indicadores.md
// (adaptação de docs/pesquisa/regras-de-indicador.md).
//
// Como funciona:
//   1. Ao trocar a região (no select ou clicando no mapa), a página busca na API
//      os indicadores daquela região. A resposta já traz cada estado dela.
//   2. Ao trocar o estado, não precisa buscar de novo: usa a resposta guardada.
//   3. O botão "Atualizar" busca de novo na API (ex.: depois de os dados mudarem).
//
// Para ligar um indicador novo (ex.: apostas, quando a US08 trouxer os dados),
// basta colocar o campo da API em INDICADORES e o data-indicador no index.html.
document.addEventListener('DOMContentLoaded', () => {
  const URL_INDICADORES = '/api/indicadores';

  // Mesmas UFs de backend/filtros.py (UFS_POR_REGIAO).
  const REGIOES = {
    norte: {
      nome: 'Norte',
      estados: {
        AC: 'Acre',
        AM: 'Amazonas',
        AP: 'Amapá',
        PA: 'Pará',
        RO: 'Rondônia',
        RR: 'Roraima',
        TO: 'Tocantins',
      },
    },
    nordeste: {
      nome: 'Nordeste',
      estados: {
        AL: 'Alagoas',
        BA: 'Bahia',
        CE: 'Ceará',
        MA: 'Maranhão',
        PB: 'Paraíba',
        PE: 'Pernambuco',
        PI: 'Piauí',
        RN: 'Rio Grande do Norte',
        SE: 'Sergipe',
      },
    },
  };

  // Cards de indicador (data-indicador no index.html) -> campo da API.
  // campo: null = o indicador ainda não é calculado pela API.
  const INDICADORES = {
    recuperacao: { campo: 'pct_recuperacao_rapida', sufixo: '%' },
    credito_caro: { campo: 'pct_credito_caro', sufixo: '%' },
    divida_saudavel: { campo: 'pct_saudavel', sufixo: '%' },
    apostas: { campo: null, sufixo: '' }, // depende dos dados da US08
  };

  const elementos = {
    regiao: document.getElementById('filtro-regiao'),
    estado: document.getElementById('filtro-estado'),
    detalharEstado: document.getElementById('estado'),
    atualizar: document.getElementById('btn-atualizar'),
    tituloPotencial: document.getElementById('titulo-potencial'),
    valorPotencial: document.getElementById('valor-potencial'),
    aviso: document.getElementById('aviso-potencial'),
    linkGraficos: document.getElementById('link-graficos'),
    mapa: document.querySelectorAll('.mapa-svg .regiao'),
    cardTitulo: document.getElementById('card-titulo'),
    cardEstados: document.getElementById('card-estados'),
    secaoEstados: document.getElementById('secao-estados'),
    descEstados: document.getElementById('estados-desc'),
    listaEstados: document.getElementById('lista-estados'),
    cards: document.querySelectorAll('[data-indicador]'),
  };

  // Só roda na página que tem os filtros do potencial de crédito.
  if (!elementos.regiao || !elementos.valorPotencial) {
    return;
  }

  // Estado da página: o que está escolhido e a última resposta da API.
  const estado = {
    regiao: '', // '' = Norte e Nordeste juntos
    uf: '', // '' = região inteira
    resposta: null,
    buscando: false,
  };

  // ---------------------------------------------------------------- API ----

  async function buscarIndicadores(regiao) {
    const parametros = new URLSearchParams();
    if (regiao) {
      parametros.set('regiao', regiao);
    }
    // O estado não vai para a API de propósito: sem ele, a resposta traz todos
    // os estados da região em "por_estado", e a lista por estado usa isso.

    const resposta = await fetch(`${URL_INDICADORES}?${parametros}`);
    const corpo = await resposta.json().catch(() => ({}));
    if (!resposta.ok) {
      throw new Error(corpo.erro || `Erro ${resposta.status} ao buscar os indicadores.`);
    }
    return corpo;
  }

  async function carregar() {
    estado.buscando = true;
    elementos.atualizar.disabled = true;
    mostrarAviso('Carregando indicadores...');

    try {
      estado.resposta = await buscarIndicadores(estado.regiao);
      mostrarAviso('');
    } catch (erro) {
      estado.resposta = null;
      mostrarAviso(`Não foi possível carregar os indicadores. ${erro.message}`);
    } finally {
      estado.buscando = false;
      elementos.atualizar.disabled = false;
      renderizar();
    }
  }

  // ------------------------------------------------------------ Filtros ----

  function preencherEstados() {
    const select = elementos.estado;
    select.innerHTML = '';
    select.append(new Option('Todos os estados', ''));

    const regioes = estado.regiao ? [estado.regiao] : Object.keys(REGIOES);
    regioes.forEach((chave) => {
      const grupo = document.createElement('optgroup');
      grupo.label = REGIOES[chave].nome;
      Object.entries(REGIOES[chave].estados).forEach(([uf, nome]) => {
        grupo.append(new Option(nome, uf));
      });
      select.append(grupo);
    });

    select.value = estado.uf;
  }

  function escolherRegiao(regiao) {
    if (regiao === estado.regiao && estado.resposta) {
      return;
    }
    estado.regiao = regiao;
    elementos.regiao.value = regiao;

    // O estado escolhido só continua se for da região nova.
    if (estado.uf && regiao && !(estado.uf in REGIOES[regiao].estados)) {
      estado.uf = '';
    }
    preencherEstados();
    carregar();
  }

  function escolherEstado(uf) {
    estado.uf = uf;
    elementos.estado.value = uf;

    // Escolher um estado de outra região troca a região também.
    const regiaoDoEstado = regiaoDaUf(uf);
    if (uf && regiaoDoEstado !== estado.regiao) {
      escolherRegiao(regiaoDoEstado);
      return;
    }
    renderizar();
  }

  function detalhandoPorEstado() {
    return !elementos.detalharEstado || elementos.detalharEstado.checked;
  }

  // ------------------------------------------------------------ Desenho ----

  // Indicadores do que está escolhido: o estado, a região ou o geral.
  function indicadoresSelecionados() {
    const resposta = estado.resposta;
    if (!resposta) {
      return null;
    }
    if (estado.uf && detalhandoPorEstado()) {
      return resposta.por_estado?.[estado.uf] ?? null;
    }
    if (estado.regiao) {
      return resposta.por_regiao?.[estado.regiao] ?? null;
    }
    return resposta.geral ?? null;
  }

  function nomeSelecionado() {
    if (estado.uf && detalhandoPorEstado()) {
      return `${nomeDaUf(estado.uf)} (${estado.uf})`;
    }
    if (estado.regiao) {
      return REGIOES[estado.regiao].nome;
    }
    return 'Norte e Nordeste';
  }

  function renderizar() {
    const indicadores = indicadoresSelecionados();

    elementos.tituloPotencial.textContent = `Potencial de Crédito Geral · ${nomeSelecionado()}`;
    elementos.valorPotencial.textContent = formatar(indicadores?.indicador_geral);

    if (estado.resposta && !indicadores) {
      mostrarAviso('Não há dados para essa seleção.');
    }

    renderizarCards(indicadores);
    renderizarMapa();
    renderizarListaEstados();
    atualizarLinkGraficos();
  }

  function renderizarCards(indicadores) {
    elementos.cards.forEach((card) => {
      const config = INDICADORES[card.dataset.indicador];
      const valor = card.querySelector('[data-valor]');
      if (!config || !valor) {
        return;
      }
      if (config.campo === null) {
        valor.textContent = '—';
        valor.title = 'Indicador ainda sem dados para o cálculo.';
        return;
      }
      valor.textContent = formatar(indicadores?.[config.campo], config.sufixo);
    });
  }

  function renderizarMapa() {
    const nomeRegiao = estado.regiao ? REGIOES[estado.regiao].nome : '';
    elementos.mapa.forEach((caminho) => {
      caminho.classList.toggle('ativa', caminho.id === nomeRegiao);
    });

    if (elementos.cardTitulo) {
      elementos.cardTitulo.textContent = nomeRegiao || 'Norte e Nordeste';
    }
    if (elementos.cardEstados) {
      const regioes = estado.regiao ? [estado.regiao] : Object.keys(REGIOES);
      elementos.cardEstados.textContent = regioes
        .flatMap((chave) => Object.keys(REGIOES[chave].estados))
        .join(', ');
    }
  }

  // Lista com o indicador geral de cada estado da região escolhida.
  function renderizarListaEstados() {
    const secao = elementos.secaoEstados;
    if (!secao) {
      return;
    }

    const mostrar = Boolean(estado.regiao) && detalhandoPorEstado();
    secao.hidden = !mostrar;
    if (!mostrar) {
      return;
    }

    const porEstado = estado.resposta?.por_estado ?? {};
    const estadosDaRegiao = Object.entries(REGIOES[estado.regiao].estados)
      .map(([uf, nome]) => ({ uf, nome, valor: porEstado[uf]?.indicador_geral ?? null }))
      // Maior potencial primeiro; estados sem dados vão para o fim.
      .sort((a, b) => (b.valor ?? -1) - (a.valor ?? -1));

    elementos.descEstados.textContent = `Indicador geral de cada estado da região ${REGIOES[estado.regiao].nome}. Clique em um estado para ver os indicadores dele.`;

    elementos.listaEstados.innerHTML = '';
    estadosDaRegiao.forEach(({ uf, nome, valor }) => {
      const item = document.createElement('li');
      const botao = document.createElement('button');
      botao.type = 'button';
      botao.className = 'estado-item';
      botao.classList.toggle('ativo', uf === estado.uf);
      botao.dataset.uf = uf;

      const rotulo = document.createElement('span');
      rotulo.className = 'estado-nome';
      rotulo.textContent = `${nome} (${uf})`;

      const barra = document.createElement('span');
      barra.className = 'estado-barra';
      const preenchimento = document.createElement('span');
      preenchimento.style.width = `${Math.max(0, Math.min(100, valor ?? 0))}%`;
      barra.append(preenchimento);

      const numero = document.createElement('strong');
      numero.className = 'estado-valor';
      numero.textContent = formatar(valor);

      botao.append(rotulo, barra, numero);
      item.append(botao);
      elementos.listaEstados.append(item);
    });
  }

  function atualizarLinkGraficos() {
    if (!elementos.linkGraficos) {
      return;
    }
    const parametros = new URLSearchParams();
    if (estado.regiao) {
      parametros.set('regiao', estado.regiao);
    }
    if (estado.uf && detalhandoPorEstado()) {
      parametros.set('estado', estado.uf);
    }
    const base = elementos.linkGraficos.dataset.base || elementos.linkGraficos.getAttribute('href');
    elementos.linkGraficos.dataset.base = base;
    elementos.linkGraficos.href = parametros.toString() ? `${base}?${parametros}` : base;
  }

  function mostrarAviso(texto) {
    if (!elementos.aviso) {
      return;
    }
    elementos.aviso.textContent = texto;
    elementos.aviso.hidden = !texto;
  }

  // ---------------------------------------------------------- Utilidades ----

  function formatar(valor, sufixo = '') {
    if (valor === null || valor === undefined || Number.isNaN(valor)) {
      return '—';
    }
    const numero = Number(valor).toLocaleString('pt-BR', {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    });
    return `${numero}${sufixo}`;
  }

  function regiaoDaUf(uf) {
    return Object.keys(REGIOES).find((chave) => uf in REGIOES[chave].estados) || '';
  }

  function nomeDaUf(uf) {
    return REGIOES[regiaoDaUf(uf)]?.estados[uf] || uf;
  }

  // ------------------------------------------------------------- Eventos ----

  elementos.regiao.addEventListener('change', () => escolherRegiao(elementos.regiao.value));
  elementos.estado.addEventListener('change', () => escolherEstado(elementos.estado.value));
  elementos.atualizar.addEventListener('click', carregar);

  if (elementos.detalharEstado) {
    elementos.detalharEstado.addEventListener('change', renderizar);
  }

  elementos.mapa.forEach((caminho) => {
    caminho.addEventListener('click', () => {
      escolherRegiao(caminho.id.toLowerCase());
    });
  });

  if (elementos.listaEstados) {
    elementos.listaEstados.addEventListener('click', (evento) => {
      const botao = evento.target.closest('.estado-item');
      if (botao) {
        escolherEstado(botao.dataset.uf === estado.uf ? '' : botao.dataset.uf);
      }
    });
  }

  // Começa com Norte e Nordeste juntos.
  preencherEstados();
  carregar();
});
