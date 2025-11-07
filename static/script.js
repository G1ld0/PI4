// Espera o evento "load" (página 100% carregada)
window.addEventListener('load', () => {
  const loader = document.querySelector('.loader-wrapper');
  // Adiciona a classe que faz o loader desaparecer
  loader.classList.add('loader-hidden');
});