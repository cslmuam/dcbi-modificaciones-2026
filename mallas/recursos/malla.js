/* Ajusta el lienzo de 1280 px al ancho de la ventana (o del visor del
   tablero) sin tocar la impresión: la escala es una variable que sólo usa la
   regla `@media screen` de malla.css. */
(function () {
  const ajusta = () => {
    const ancho = document.documentElement.clientWidth;
    const z = Math.min(1, (ancho - 32) / 1280);
    document.documentElement.style.setProperty("--escala", z > 0.2 ? z : 0.2);
  };
  ajusta();
  window.addEventListener("resize", ajusta);
})();
