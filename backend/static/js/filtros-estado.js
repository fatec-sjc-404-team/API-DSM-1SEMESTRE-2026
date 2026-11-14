// Mostra ou esconde o campo "Estado" conforme o checkbox "Detalhar por estado".
// Interações da página "Filtros Salvos" (FC404-228).
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

  // ---- Página "Filtros Salvos" (FC404-228) ----
  // Só roda quando a tabela existe: nas outras páginas não faz nada.
  function iniciarFiltrosSalvos(tabela) {
    const URL_GRAFICOS = '/graficos';
    const corpo = tabela.querySelector('tbody');
    const botaoNovo = document.querySelector('.button-filter');
    const CHAVE_FILTROS = 'avocredit:filtrosSalvos';
    const modalExclusao = document.getElementById('modal-excluir-filtro');
    const botaoCancelarExclusao = document.getElementById('cancelar-exclusao');
    const botaoConfirmarExclusao = document.getElementById('confirmar-exclusao');
    let linhaParaExcluir = null;
    let focoAntesDoModal = null;

    function lerLinha(linha) {
      return {
        nome: linha.cells[0].textContent.trim(),
        regiao: linha.cells[1].textContent.trim(),
        estado: linha.cells[2].textContent.trim(),
        periodo: linha.cells[3].textContent.trim(),
        tipoDivida: linha.cells[4].textContent.trim(),
        apostas: linha.cells[5].textContent.trim(),
        criadoEm: linha.cells[6].textContent.trim(),
      };
    }

    function gravarFiltros(filtros) {
      try {
        localStorage.setItem(CHAVE_FILTROS, JSON.stringify({
          inicializado: true,
          filtros,
        }));
        return true;
      } catch (erro) {
        window.alert(`Não foi possível salvar os filtros neste navegador: ${erro.message}`);
        return false;
      }
    }

    function renderizarFiltros(filtros) {
      corpo.replaceChildren();
      filtros.forEach((filtro) => {
        const linha = corpo.insertRow();
        [
          filtro.nome,
          filtro.regiao,
          filtro.estado,
          filtro.periodo,
          filtro.tipoDivida,
          filtro.apostas,
          filtro.criadoEm,
        ].forEach((valor) => {
          linha.insertCell().textContent = valor;
        });

        const celulaAcoes = linha.insertCell();
        ['play_arrow', 'edit', 'delete'].forEach((acao) => {
          const icone = document.createElement('span');
          icone.className = 'material-symbols-outlined';
          icone.setAttribute('aria-hidden', 'true');
          icone.textContent = acao;
          celulaAcoes.appendChild(icone);
        });
      });
    }

    let filtrosSalvos;
    try {
      const armazenados = localStorage.getItem(CHAVE_FILTROS);
      const estado = armazenados ? JSON.parse(armazenados) : null;
      if (
        (armazenados && estado === null)
        || (estado !== null
          && (!Array.isArray(estado.filtros)
          || typeof estado.inicializado !== 'boolean'
          || estado.filtros.some((filtro) =>
            !filtro || ['nome', 'regiao', 'estado', 'periodo', 'tipoDivida', 'apostas', 'criadoEm']
              .some((campo) => typeof filtro[campo] !== 'string'),
          )))
      ) {
        throw new Error('Os filtros salvos neste navegador estão em um formato inválido.');
      }

      const filtrosIniciais = Array.from(corpo.rows, lerLinha);
      if (!estado || !estado.inicializado) {
        filtrosSalvos = filtrosIniciais.concat(estado ? estado.filtros : []);
        if (!gravarFiltros(filtrosSalvos)) {
          return;
        }
      } else {
        filtrosSalvos = estado.filtros;
      }
      renderizarFiltros(filtrosSalvos);
    } catch (erro) {
      window.alert(`Não foi possível carregar os filtros salvos: ${erro.message}`);
      return;
    }

    const semAcento = (texto) => texto
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .trim();

    const nomeDoFiltro = (linha) => linha.cells[0].textContent.trim();

    // Lê as células da linha (região, estado, período, tipo de dívida)
    // e monta os parâmetros que a página Gráficos entende.
    function filtrosDaLinha(linha) {
      const parametros = new URLSearchParams();

      const regiao = semAcento(linha.cells[1].textContent);
      if (['todos', 'norte', 'nordeste'].includes(regiao)) {
        parametros.set('regiao', regiao);
      }

      // A página Gráficos aceita um estado por vez: só envia se o filtro tiver um.
      const estados = linha.cells[2].textContent
        .split(',')
        .map((uf) => uf.trim())
        .filter(Boolean);
      if (estados.length === 1 && estados[0].length === 2) {
        parametros.set('estado', estados[0].toUpperCase());
      }

      const periodo = linha.cells[3].textContent;
      const meses = periodo.match(/\d+/);
      if (meses) {
        parametros.set('periodo', `${meses[0]}_${meses[0] === '1' ? 'mes' : 'meses'}`);
      } else if (semAcento(periodo).includes('ano')) {
        parametros.set('periodo', '12_meses');
      }

      const tipo = semAcento(linha.cells[4].textContent);
      if (['saudavel', 'critica', 'mista'].includes(tipo)) {
        parametros.set('tipoDivida', tipo);
      }

      return parametros;
    }

    function mostrarMensagemSeVazia() {
      if (!corpo.querySelector('tr:not(.sem-filtros)')) {
        corpo.insertAdjacentHTML(
          'beforeend',
          '<tr class="sem-filtros"><td colspan="8">Nenhum filtro salvo.</td></tr>',
        );
      }
    }

    function prepararAcoes() {
      tabela.querySelectorAll(`tbody ${SELETOR_ICONE}`).forEach((icone) => {
        const acao = ACOES[icone.textContent.trim()];
        if (!acao) {
          return;
        }
        icone.removeAttribute('aria-hidden');
        icone.setAttribute('role', 'button');
        icone.setAttribute('tabindex', '0');
        icone.setAttribute('aria-label', acao.rotulo);
        icone.setAttribute('title', acao.rotulo);
        icone.dataset.acao = icone.textContent.trim();
      });
    }

    function atualizarTabela(filtros) {
      filtrosSalvos = filtros;
      renderizarFiltros(filtrosSalvos);
      prepararAcoes();
      mostrarMensagemSeVazia();
    }

    function iniciarEdicao(linha) {
      const indice = Array.from(corpo.rows).indexOf(linha);
      const filtro = filtrosSalvos[indice];
      if (!filtro) {
        return;
      }

      const celulaNome = linha.cells[0];
      const grupoEdicao = document.createElement('div');
      grupoEdicao.className = 'filtro-edicao';

      const inputNome = document.createElement('input');
      inputNome.type = 'text';
      inputNome.value = filtro.nome;
      inputNome.setAttribute('aria-label', 'Nome do filtro');

      const botaoOk = document.createElement('button');
      botaoOk.type = 'button';
      botaoOk.textContent = 'OK';

      function cancelarEdicao() {
        renderizarFiltros(filtrosSalvos);
        prepararAcoes();
      }

      function salvarEdicao() {
        const nome = inputNome.value.trim();
        if (!nome) {
          window.alert('O nome do filtro não pode ficar vazio.');
          inputNome.focus();
          return;
        }

        const atualizados = filtrosSalvos.map((item, i) =>
          i === indice ? { ...item, nome } : item,
        );
        if (gravarFiltros(atualizados)) {
          atualizarTabela(atualizados);
        }
      }

      botaoOk.addEventListener('click', salvarEdicao);
      inputNome.addEventListener('keydown', (evento) => {
        if (evento.key === 'Enter') {
          evento.preventDefault();
          salvarEdicao();
        } else if (evento.key === 'Escape') {
          cancelarEdicao();
        }
      });

      grupoEdicao.append(inputNome, botaoOk);
      celulaNome.replaceChildren(grupoEdicao);
      inputNome.focus();
      inputNome.select();
    }

    function abrirModalExclusao(linha) {
      if (!modalExclusao) {
        window.alert('Não foi possível abrir a confirmação de exclusão.');
        return;
      }
      linhaParaExcluir = linha;
      focoAntesDoModal = document.activeElement;
      modalExclusao.hidden = false;
      modalExclusao.querySelector('.filtro-modal-dialogo').focus();
    }

    function fecharModalExclusao() {
      if (modalExclusao) {
        modalExclusao.hidden = true;
      }
      if (focoAntesDoModal && focoAntesDoModal.isConnected) {
        focoAntesDoModal.focus();
      }
      linhaParaExcluir = null;
    }

    function excluirFiltro() {
      if (!linhaParaExcluir) {
        fecharModalExclusao();
        return;
      }
      const indice = Array.from(corpo.rows).indexOf(linhaParaExcluir);
      const atualizados = filtrosSalvos.filter((_, i) => i !== indice);
      if (gravarFiltros(atualizados)) {
        atualizarTabela(atualizados);
        fecharModalExclusao();
      }
    }

    const ACOES = {
      // Abre os Gráficos já com os filtros desta linha.
      play_arrow: {
        rotulo: 'Aplicar filtro',
        executar(linha) {
          window.location.href = `${URL_GRAFICOS}?${filtrosDaLinha(linha)}`;
        },
      },
      // Abre os Gráficos com os filtros e o nome preenchidos em "Salvar como".
      edit: {
        rotulo: 'Editar filtro',
        executar: iniciarEdicao,
      },
      delete: {
        rotulo: 'Excluir filtro',
        executar: abrirModalExclusao,
      },
    };

    const SELETOR_ICONE = 'td:last-child .material-symbols-outlined';

    prepararAcoes();
    mostrarMensagemSeVazia();

    function executarAcao(alvo) {
      const icone = alvo.closest(SELETOR_ICONE);
      const acao = icone && ACOES[icone.dataset.acao];
      const linha = icone && icone.closest('tr');
      if (acao && linha) {
        acao.executar(linha);
        return true;
      }
      return false;
    }

    corpo.addEventListener('click', (evento) => {
      executarAcao(evento.target);
    });

    corpo.addEventListener('keydown', (evento) => {
      if ((evento.key === 'Enter' || evento.key === ' ') && executarAcao(evento.target)) {
        evento.preventDefault();
      }
    });

    if (botaoCancelarExclusao) {
      botaoCancelarExclusao.addEventListener('click', fecharModalExclusao);
    }
    if (botaoConfirmarExclusao) {
      botaoConfirmarExclusao.addEventListener('click', excluirFiltro);
    }
    if (modalExclusao) {
      modalExclusao.addEventListener('click', (evento) => {
        if (evento.target.matches('[data-fechar-modal]')) {
          fecharModalExclusao();
        }
      });
      document.addEventListener('keydown', (evento) => {
        if (evento.key === 'Escape' && !modalExclusao.hidden) {
          fecharModalExclusao();
        }
      });
    }

    if (botaoNovo) {
      botaoNovo.addEventListener('click', () => {
        window.location.href = URL_GRAFICOS;
      });
    }
  }

  const tabelaFiltrosSalvos = document.querySelector('.tabela-filtros-salvos');
  if (tabelaFiltrosSalvos) {
    iniciarFiltrosSalvos(tabelaFiltrosSalvos);
  }
});