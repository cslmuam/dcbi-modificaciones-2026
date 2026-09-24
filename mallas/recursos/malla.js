/* Dos ajustes de pantalla, ninguno de impresión.

   1. En pantalla ancha, cada lámina de 1280 px se escala al ancho de la
      ventana o del visor del tablero con la variable --escala, que sólo usa
      la regla `@media screen` de malla.css. En pantalla estrecha las láminas
      se ocultan y se lee la versión de teléfono.
   2. Dentro del visor del tablero, la malla avisa su alto a la página que la
      contiene, para que el visor crezca con ella y no haya una segunda barra
      de desplazamiento dentro de la página. */
(function () {
  const raiz = document.documentElement;
  const incrustada = window.self !== window.top;
  if (incrustada) raiz.classList.add("incrustada");

  const avisa = () => {
    if (incrustada) {
      // El alto del contenido, no el del documento: éste nunca baja del alto
      // del visor, y el visor no podría encogerse al ensanchar la ventana.
      const alto = Math.ceil(document.body.getBoundingClientRect().bottom + window.scrollY + 24);
      window.parent.postMessage({ malla: true, alto }, "*");
    }
  };
  const ajusta = () => {
    const z = Math.min(1, (raiz.clientWidth - 32) / 1280);
    raiz.style.setProperty("--escala", z > 0.2 ? z : 0.2);
    requestAnimationFrame(avisa);
  };
  ajusta();
  window.addEventListener("resize", ajusta);
  window.addEventListener("load", avisa);
  if ("ResizeObserver" in window) new ResizeObserver(avisa).observe(document.body);
})();
