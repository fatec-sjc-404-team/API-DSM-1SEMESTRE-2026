// US06: lista, aplica, renomeia e exclui os filtros salvos no MySQL.
document.addEventListener('DOMContentLoaded', () => {
  const tabela = document.querySelector('.tabela-filtros-salvos');
  if (!tabela) return;

  const URL_API = '/api/filtros-salvos';
  const URL_GRAFICOS = '/graficos';
  const corpo = tabela.querySelector('tbody');
  const modalExclusao = document.getElementById('modal-excluir-filtro');
  const mensagemExclusao = document.getElementById('mensagem-modal-exclusao');
  const botaoCancelarExclusao = document.getElementById('cancelar-exclusao');
  const botaoConfirmarExclusao = document.getElementById('confirmar-exclusao');
  const aviso = document.getElementById('aviso-filtros');
  const regioes = { norte: 'Norte', nordeste: 'Nordeste' };
  const tipos = { saudavel: 'Saudável', critica: 'Crítica', mista: 'Mista' };

  let filtros = [];
  let filtroParaExcluir = null;
  let focoAntesDoModal = null;

  async function requisicao(url, opcoes = {}) {
    const resposta = await fetch(url, opcoes);
    if (resposta.status === 204) return null;
    const dados = await resposta.json();
    if (!resposta.ok) {
      throw new Error(dados.erro || 'Falha ao acessar os filtros salvos.');
    }
    return dados;
  }

  // Mostra o erro acima da tabela (sem a caixinha do navegador).
  function mostrarAviso(mensagem) {
    aviso.textContent = mensagem;
    aviso.hidden = false;
  }

  function esconderAviso() {
    aviso.hidden = true;
    aviso.textContent = '';
  }

  function descreverPeriodo(periodo) {
    const meses = Number(periodo);
    if (meses === 12) return 'Último ano';
    if (meses === 1) return 'Último mês';
    return `Últimos ${meses} meses`;
  }

  function exibirMensagem(mensagem) {
    corpo.replaceChildren();
    const celula = corpo.insertRow().insertCell();
    celula.colSpan = 8;
    celula.textContent = mensagem;
  }

  function criarAcao(filtro, icone, rotulo, executar) {
    const botao = document.createElement('button');
    botao.type = 'button';
    botao.className = 'material-symbols-outlined';
    botao.textContent = icone;
    botao.title = rotulo;
    botao.setAttribute('aria-label', `${rotulo} ${filtro.nome}`);
    botao.addEventListener('click', () => executar(filtro, botao));
    return botao;
  }

  function renderizar() {
    corpo.replaceChildren();
    if (!filtros.length) {
      exibirMensagem('Nenhum filtro salvo.');
      return;
    }

    filtros.forEach((filtro) => {
      const linha = corpo.insertRow();
      linha.dataset.id = filtro.id;
      const data = new Date(filtro.criado_em);
      const valores = [
        filtro.nome,
        regioes[filtro.regiao] || 'Todos',
        filtro.estado || 'Todos',
        descreverPeriodo(filtro.periodo),
        tipos[filtro.tipo_divida] || 'Todos',
        'Todos',
        Number.isNaN(data.getTime()) ? filtro.criado_em : data.toLocaleString('pt-BR'),
      ];
      valores.forEach((valor) => { linha.insertCell().textContent = valor; });

      linha.insertCell().append(
        criarAcao(filtro, 'play_arrow', 'Aplicar', aplicar),
        criarAcao(filtro, 'edit', 'Renomear', iniciarEdicao),
        criarAcao(filtro, 'delete', 'Excluir', abrirModalExclusao),
      );
    });
  }

  async function carregar() {
    try {
      filtros = (await requisicao(URL_API)).filtros;
      renderizar();
    } catch (erro) {
      exibirMensagem(erro.message);
    }
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

  // Troca o nome por um campo de texto na própria linha (Enter salva, Esc cancela).
  function iniciarEdicao(filtro) {
    const linha = corpo.querySelector(`tr[data-id="${filtro.id}"]`);
    if (!linha) return;

    const grupo = document.createElement('div');
    grupo.className = 'filtro-edicao';
    const input = document.createElement('input');
    input.type = 'text';
    input.maxLength = 100;
    input.value = filtro.nome;
    input.setAttribute('aria-label', 'Nome do filtro');
    const botaoOk = document.createElement('button');
    botaoOk.type = 'button';
    botaoOk.textContent = 'OK';

    async function salvar() {
      const nome = input.value.trim();
      if (!nome) {
        input.setAttribute('aria-invalid', 'true');
        mostrarAviso('O nome do filtro não pode ficar vazio.');
        input.focus();
        return;
      }
      esconderAviso();
      if (nome === filtro.nome) {
        renderizar();
        return;
      }
      botaoOk.disabled = true;
      try {
        await requisicao(`${URL_API}/${filtro.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ nome }),
        });
        await carregar();
      } catch (erro) {
        botaoOk.disabled = false;
        mostrarAviso(`Não foi possível renomear o filtro: ${erro.message}`);
      }
    }

    botaoOk.addEventListener('click', salvar);
    input.addEventListener('keydown', (evento) => {
      if (evento.key === 'Enter') {
        evento.preventDefault();
        salvar();
      } else if (evento.key === 'Escape') {
        esconderAviso();
        renderizar();
      }
    });

    grupo.append(input, botaoOk);
    linha.cells[0].replaceChildren(grupo);
    input.focus();
    input.select();
  }

  function abrirModalExclusao(filtro) {
    filtroParaExcluir = filtro;
    focoAntesDoModal = document.activeElement;
    if (mensagemExclusao) {
      mensagemExclusao.textContent = `Tem certeza que deseja apagar o filtro "${filtro.nome}"? `
        + 'Esta ação não pode ser desfeita.';
    }
    modalExclusao.hidden = false;
    modalExclusao.querySelector('.filtro-modal-dialogo').focus();
  }

  function fecharModalExclusao() {
    modalExclusao.hidden = true;
    filtroParaExcluir = null;
    if (focoAntesDoModal && focoAntesDoModal.isConnected) {
      focoAntesDoModal.focus();
    }
  }

  async function excluir() {
    if (!filtroParaExcluir) {
      fecharModalExclusao();
      return;
    }
    botaoConfirmarExclusao.disabled = true;
    try {
      await requisicao(`${URL_API}/${filtroParaExcluir.id}`, { method: 'DELETE' });
      esconderAviso();
      fecharModalExclusao();
      await carregar();
    } catch (erro) {
      fecharModalExclusao();
      mostrarAviso(`Não foi possível excluir o filtro: ${erro.message}`);
    } finally {
      botaoConfirmarExclusao.disabled = false;
    }
  }

  botaoCancelarExclusao.addEventListener('click', fecharModalExclusao);
  botaoConfirmarExclusao.addEventListener('click', excluir);
  modalExclusao.addEventListener('click', (evento) => {
    if (evento.target.matches('[data-fechar-modal]')) fecharModalExclusao();
  });
  document.addEventListener('keydown', (evento) => {
    if (evento.key === 'Escape' && !modalExclusao.hidden) fecharModalExclusao();
  });

  document.querySelector('.button-filter')?.addEventListener('click', () => {
    window.location.href = URL_GRAFICOS;
  });

  carregar();
});
