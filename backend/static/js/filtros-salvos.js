// US06: lista os filtros salvos no MySQL e permite aplicar um deles nos Gráficos.
document.addEventListener('DOMContentLoaded', () => {
  const tabela = document.querySelector('.tabela-filtros-salvos');
  if (!tabela) return;

  const URL_API = '/api/filtros-salvos';
  const URL_GRAFICOS = '/graficos';
  const corpo = tabela.querySelector('tbody');
  const botaoNovo = document.querySelector('.button-filter');
  const regioes = { norte: 'Norte', nordeste: 'Nordeste' };
  const tipos = { saudavel: 'Saudável', critica: 'Crítica', mista: 'Mista' };
  const modalExclusao = document.getElementById('modal-excluir-filtro');
  const botaoCancelarExclusao = document.getElementById('cancelar-exclusao');
  const botaoConfirmarExclusao = document.getElementById('confirmar-exclusao');
  let filtrosSalvos = [];
  let filtroParaExcluir = null;
  let focoAntesDoModal = null;

  function descreverPeriodo(periodo) {
    const meses = Number(periodo);
    if (meses === 12) return 'Último ano';
    if (meses === 1) return 'Último mês';
    return `Últimos ${meses} meses`;
  }

  function formatarCriacao(criadoEm) {
    const data = new Date(criadoEm);
    return Number.isNaN(data.getTime()) ? criadoEm : data.toLocaleString('pt-BR');
  }

  function exibirMensagem(mensagem) {
    corpo.replaceChildren();
    const celula = corpo.insertRow().insertCell();
    celula.colSpan = tabela.tHead.rows[0].cells.length;
    celula.textContent = mensagem;
  }

  function aplicar(filtro) {
    const meses = Number(filtro.periodo);
    const parametros = new URLSearchParams({
      regiao: filtro.regiao || 'todos',
      periodo: `${meses}_${meses === 1 ? 'mes' : 'meses'}`,
      nome: filtro.nome,
    });
    if (filtro.estado) parametros.set('estado', filtro.estado);
    if (filtro.tipo_divida) parametros.set('tipoDivida', filtro.tipo_divida);
    window.location.href = `${URL_GRAFICOS}?${parametros}`;
  }

  function criarBotao(icone, rotulo, executar) {
    const botao = document.createElement('button');
    botao.type = 'button';
    botao.className = 'material-symbols-outlined';
    botao.textContent = icone;
    botao.title = rotulo;
    botao.setAttribute('aria-label', rotulo);
    botao.addEventListener('click', executar);
    return botao;
  }

  function iniciarEdicao(filtro, celulaNome) {
    const grupoEdicao = document.createElement('div');
    grupoEdicao.className = 'filtro-edicao';

    const inputNome = document.createElement('input');
    inputNome.type = 'text';
    inputNome.maxLength = 100;
    inputNome.value = filtro.nome;
    inputNome.setAttribute('aria-label', 'Nome do filtro');

    const botaoOk = document.createElement('button');
    botaoOk.type = 'button';
    botaoOk.textContent = 'OK';

    function cancelarEdicao() {
      renderizar(filtrosSalvos);
    }

    async function salvarEdicao() {
      const nome = inputNome.value.trim();
      if (!nome) {
        window.alert('O nome do filtro não pode ficar vazio.');
        inputNome.focus();
        return;
      }

      try {
        await requisitar(`${URL_API}/${filtro.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ nome }),
        });
        filtrosSalvos = filtrosSalvos.map((item) =>
          item.id === filtro.id ? { ...item, nome } : item,
        );
        renderizar(filtrosSalvos);
      } catch (erro) {
        window.alert(`Não foi possível renomear o filtro: ${erro.message}`);
        inputNome.focus();
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

  function abrirModalExclusao(filtro) {
    if (!modalExclusao) {
      window.alert('Não foi possível abrir a confirmação de exclusão.');
      return;
    }
    filtroParaExcluir = filtro;
    focoAntesDoModal = document.activeElement;
    modalExclusao.hidden = false;
    modalExclusao.querySelector('.filtro-modal-dialogo').focus();
  }

  function fecharModalExclusao() {
    if (modalExclusao) {
      modalExclusao.hidden = true;
    }
    const destinoFoco = focoAntesDoModal?.isConnected
      ? focoAntesDoModal
      : corpo.querySelector('button') || botaoNovo;
    destinoFoco?.focus();
    focoAntesDoModal = null;
    filtroParaExcluir = null;
  }

  async function excluirFiltro() {
    if (!filtroParaExcluir) {
      fecharModalExclusao();
      return;
    }

    try {
      await requisitar(`${URL_API}/${filtroParaExcluir.id}`, { method: 'DELETE' });
      filtrosSalvos = filtrosSalvos.filter(
        (filtro) => filtro.id !== filtroParaExcluir.id,
      );
      renderizar(filtrosSalvos);
      fecharModalExclusao();
    } catch (erro) {
      window.alert(`Não foi possível excluir o filtro: ${erro.message}`);
    }
  }

  function renderizar(filtros) {
    filtrosSalvos = filtros;
    corpo.replaceChildren();
    if (!filtros.length) {
      exibirMensagem('Nenhum filtro salvo.');
      return;
    }

    filtros.forEach((filtro) => {
      const linha = corpo.insertRow();
      const valores = [
        filtro.nome,
        regioes[filtro.regiao] || 'Todos',
        filtro.estado || 'Todos',
        descreverPeriodo(filtro.periodo),
        tipos[filtro.tipo_divida] || 'Todos',
        formatarCriacao(filtro.criado_em),
      ];
      valores.forEach((valor) => { linha.insertCell().textContent = valor; });
      const celulaNome = linha.cells[0];
      const celulaAcoes = linha.insertCell();
      celulaAcoes.append(
        criarBotao('play_arrow', 'Aplicar filtro', () => aplicar(filtro)),
        criarBotao('edit', 'Editar filtro', () => iniciarEdicao(filtro, celulaNome)),
        criarBotao('delete', 'Excluir filtro', () => abrirModalExclusao(filtro)),
      );
    });
  }

  async function requisitar(url, opcoes) {
    const resposta = await fetch(url, opcoes);
    const dados = await resposta.json();
    if (!resposta.ok) {
      throw new Error(dados.erro || 'Falha ao acessar os filtros salvos.');
    }
    return dados;
  }

  async function carregar() {
    try {
      const dados = await requisitar(URL_API);
      renderizar(dados.filtros);
    } catch (erro) {
      exibirMensagem(`Não foi possível carregar os filtros: ${erro.message}`);
    }
  }

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
      if (modalExclusao.hidden) {
        return;
      }
      if (evento.key === 'Escape') {
        fecharModalExclusao();
        return;
      }
      // Tab fica preso dentro do modal enquanto ele está aberto.
      if (evento.key === 'Tab') {
        const focaveis = Array.from(modalExclusao.querySelectorAll('button'));
        const primeiro = focaveis[0];
        const ultimo = focaveis[focaveis.length - 1];
        const dentro = modalExclusao.contains(document.activeElement);
        if (evento.shiftKey && (!dentro || document.activeElement === primeiro
          || document.activeElement === modalExclusao.querySelector('.filtro-modal-dialogo'))) {
          evento.preventDefault();
          ultimo.focus();
        } else if (!evento.shiftKey && (!dentro || document.activeElement === ultimo)) {
          evento.preventDefault();
          primeiro.focus();
        }
      }
    });
  }

  botaoNovo?.addEventListener('click', () => {
    window.location.href = URL_GRAFICOS;
  });

  carregar();
});
