/* Malla en teléfono: el selector de trimestres lleva a cada uno y marca el
   que está a la vista. La usan la página suelta de la malla y el tablero, que
   llama a mallaMovil() cada vez que dibuja el fragmento. */
window.mallaMovil = function (raiz, tope) {
  const mm = raiz.querySelector(".mm");
  if (!mm) return;
  mm.style.setProperty("--mm-tope", (tope || 0) + "px");
  const nav = mm.querySelector(".mm-nav");
  const botones = [...nav.querySelectorAll("button")];
  const secciones = [...mm.querySelectorAll(".mm-trim")];
  const reducido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const marca = (t) => botones.forEach((b) => {
    const si = b.dataset.t === String(t);
    b.classList.toggle("activo", si);
    b.setAttribute("aria-current", si ? "true" : "false");
    if (si) nav.scrollTo({ left: b.offsetLeft - nav.clientWidth / 2 + b.offsetWidth / 2,
                           behavior: reducido ? "auto" : "smooth" });
  });
  botones.forEach((b) => b.addEventListener("click", () => {
    const s = secciones.find((x) => x.dataset.t === b.dataset.t);
    s?.scrollIntoView({ behavior: reducido ? "auto" : "smooth", block: "start" });
    marca(b.dataset.t);
  }));

  // El trimestre activo es el último cuyo título ya pasó bajo el selector.
  let pendiente = false;
  const actualiza = () => {
    pendiente = false;
    if (!mm.isConnected) { window.removeEventListener("scroll", alDesplazar); return; }
    const linea = (tope || 0) + nav.offsetHeight + 8;
    let actual = secciones[0];
    for (const s of secciones) if (s.getBoundingClientRect().top <= linea) actual = s;
    if (actual && !botones.some((b) => b.classList.contains("activo") && b.dataset.t === actual.dataset.t))
      marca(actual.dataset.t);
  };
  const alDesplazar = () => { if (!pendiente) { pendiente = true; requestAnimationFrame(actualiza); } };
  window.addEventListener("scroll", alDesplazar, { passive: true });
  actualiza();
};

// Página suelta: el fragmento ya está en el documento.
if (document.querySelector(".mm-pagina")) window.mallaMovil(document.querySelector(".mm-pagina"), 0);
