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
  const UFS_POR_REGIAO = {
    norte: ['AC', 'AM', 'AP', 'PA', 'RO', 'RR', 'TO'],
    nordeste: ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
  };
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
    celula.colSpan = 7;
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

  function criarSelect(rotulo, opcoes, valorAtual) {
    const select = document.createElement('select');
    select.setAttribute('aria-label', rotulo);
    opcoes.forEach(([valor, texto]) => select.add(new Option(texto, valor)));
    select.value = valorAtual ?? '';
    return select;
  }

  // Estados que podem ser escolhidos para a região (todos, se a região for "Todos").
  function opcoesDeEstado(regiao) {
    const ufs = regiao
      ? UFS_POR_REGIAO[regiao]
      : [...UFS_POR_REGIAO.norte, ...UFS_POR_REGIAO.nordeste];
    return [['', 'Todos'], ...ufs.map((uf) => [uf, uf])];
  }

  // Transforma a linha em formulário: nome, região, estado, período e tipo de dívida.
  // Enter salva, Esc cancela. Só uma linha fica em edição por vez.
  function iniciarEdicao(filtro, celulaNome) {
    renderizar(filtrosSalvos);
    const linha = [...corpo.rows].find((tr) => tr.dataset.id === String(filtro.id))
      || celulaNome.parentElement;
    linha.classList.add('filtro-em-edicao');

    const inputNome = document.createElement('input');
    inputNome.type = 'text';
    inputNome.maxLength = 100;
    inputNome.value = filtro.nome;
    inputNome.setAttribute('aria-label', 'Nome do filtro');

    const selectRegiao = criarSelect(
      'Região',
      [['', 'Todos'], ['norte', 'Norte'], ['nordeste', 'Nordeste']],
      filtro.regiao,
    );
    const selectEstado = criarSelect('Estado', opcoesDeEstado(filtro.regiao), filtro.estado);
    const selectPeriodo = criarSelect(
      'Período',
      Array.from({ length: 12 }, (_, i) => [String(i + 1), descreverPeriodo(i + 1)]),
      String(filtro.periodo),
    );
    const selectTipo = criarSelect(
      'Tipo de dívida',
      [['', 'Todos'], ...Object.entries(tipos)],
      filtro.tipo_divida,
    );

    // Ao trocar a região, mostra só os estados dela (e limpa o estado se não pertencer).
    selectRegiao.addEventListener('change', () => {
      const anterior = selectEstado.value;
      selectEstado.replaceChildren();
      opcoesDeEstado(selectRegiao.value).forEach(([valor, texto]) => {
        selectEstado.add(new Option(texto, valor));
      });
      selectEstado.value = [...selectEstado.options].some((o) => o.value === anterior)
        ? anterior
        : '';
    });

    const botaoSalvar = document.createElement('button');
    botaoSalvar.type = 'button';
    botaoSalvar.className = 'filtro-edicao-salvar';
    botaoSalvar.textContent = 'Salvar';

    const botaoCancelar = document.createElement('button');
    botaoCancelar.type = 'button';
    botaoCancelar.className = 'filtro-edicao-cancelar';
    botaoCancelar.textContent = 'Cancelar';

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

      const atualizado = {
        nome,
        regiao: selectRegiao.value || null,
        estado: selectEstado.value || null,
        periodo: Number(selectPeriodo.value),
        tipo_divida: selectTipo.value || null,
      };

      botaoSalvar.disabled = true;
      try {
        await requisitar(`${URL_API}/${filtro.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(atualizado),
        });
        filtrosSalvos = filtrosSalvos.map((item) =>
          item.id === filtro.id ? { ...item, ...atualizado } : item,
        );
        renderizar(filtrosSalvos);
      } catch (erro) {
        botaoSalvar.disabled = false;
        window.alert(`Não foi possível atualizar o filtro: ${erro.message}`);
        inputNome.focus();
      }
    }

    botaoSalvar.addEventListener('click', salvarEdicao);
    botaoCancelar.addEventListener('click', cancelarEdicao);
    linha.addEventListener('keydown', (evento) => {
      if (evento.key === 'Enter' && evento.target.tagName !== 'BUTTON') {
        evento.preventDefault();
        salvarEdicao();
      } else if (evento.key === 'Escape') {
        cancelarEdicao();
      }
    });

    const grupoEdicao = document.createElement('div');
    grupoEdicao.className = 'filtro-edicao';
    grupoEdicao.append(inputNome);
    linha.cells[0].replaceChildren(grupoEdicao);
    linha.cells[1].replaceChildren(selectRegiao);
    linha.cells[2].replaceChildren(selectEstado);
    linha.cells[3].replaceChildren(selectPeriodo);
    linha.cells[4].replaceChildren(selectTipo);
    linha.cells[7].replaceChildren(botaoSalvar, botaoCancelar);
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
      linha.dataset.id = filtro.id;
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
      if (evento.key === 'Escape' && !modalExclusao.hidden) {
        fecharModalExclusao();
      }
    });
  }

  botaoNovo?.addEventListener('click', () => {
    window.location.href = URL_GRAFICOS;
  });

  carregar();
});
