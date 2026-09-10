const API_BASE = import.meta.env.PUBLIC_API_BASE ?? 'http://localhost:8000';

export async function getVendas(periodo) {
  const resposta = await fetch(`${API_BASE}/vendas?periodo=${periodo}`);
  if (!resposta.ok) throw new Error('Falha ao buscar vendas');
  return resposta.json();
}

export async function getUsuarios() {
  const resposta = await fetch(`${API_BASE}/usuarios`);
  if (!resposta.ok) throw new Error('Falha ao buscar usuários');
  return resposta.json();
}

export async function healthCheck() {
  const resposta = await fetch(`${API_BASE}/health`);
  if (!resposta.ok) throw new Error('Falha ao verificar saúde da API');
  return resposta.json();
}
