// Mostra ou esconde o campo "Estado" conforme o checkbox "Detalhar por estado".
document.addEventListener('DOMContentLoaded', () => {
  const checkboxEstado = document.getElementById('estado');
  const grupoEstado = document.getElementById('group-by-state');

  if (!checkboxEstado || !grupoEstado) {
    return;
  }

  const atualizarVisibilidade = () => {
    grupoEstado.style.display = checkboxEstado.checked ? '' : 'none';
  };

  atualizarVisibilidade();
  checkboxEstado.addEventListener('change', atualizarVisibilidade);
});
