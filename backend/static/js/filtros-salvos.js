// US06: lista os filtros salvos no MySQL e permite aplicar um deles nos Gráficos.
document.addEventListener('DOMContentLoaded', () => {
  const tabela = document.querySelector('.tabela-filtros-salvos');
  if (!tabela) return;

  const URL_API = '/api/filtros-salvos';
  const URL_GRAFICOS = '/graficos';
  const corpo = tabela.querySelector('tbody');
  const regioes = { norte: 'Norte', nordeste: 'Nordeste' };
  const tipos = { saudavel: 'Saudável', critica: 'Crítica', mista: 'Mista' };

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

  function criarBotaoAplicar(filtro) {
    const botao = document.createElement('button');
    botao.type = 'button';
    botao.className = 'material-symbols-outlined';
    botao.textContent = 'play_arrow';
    botao.title = 'Aplicar';
    botao.setAttribute('aria-label', `Aplicar ${filtro.nome}`);
    botao.addEventListener('click', () => aplicar(filtro));
    return botao;
  }

  function renderizar(filtros) {
    corpo.replaceChildren();
    if (!filtros.length) {
      exibirMensagem('Nenhum filtro salvo.');
      return;
    }

    filtros.forEach((filtro) => {
      const linha = corpo.insertRow();
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
      linha.insertCell().append(criarBotaoAplicar(filtro));
    });
  }

  async function carregar() {
    try {
      const resposta = await fetch(URL_API);
      const dados = await resposta.json();
      if (!resposta.ok) {
        throw new Error(dados.erro || 'Falha ao acessar os filtros salvos.');
      }
      renderizar(dados.filtros);
    } catch (erro) {
      exibirMensagem(erro.message);
    }
  }

  document.querySelector('.button-filter')?.addEventListener('click', () => {
    window.location.href = URL_GRAFICOS;
  });

  carregar();
});
