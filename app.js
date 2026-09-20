/* Dashboard de modificaciones curriculares DCBI 2026.
   Navegación por hash, sin dependencias, sin servidor — abre con doble clic.
   Los datos vienen de datos.js, generado por construir_datos.py. */

const $ = (s, n = document) => n.querySelector(s);
const vista = $("#vista");

const TRONCO = {
  general: "Tronco General",
  profesional: "Tronco Profesional",
  integracion: "Tronco de Integración",
  nivelacion: "Nivelación Académica",
  optativa: "Optativas",
  sin_clasificar: "Sin clasificar",
};

const EMPAREJADO = {
  clave: ["programa", "eti verde", ""],
  clave_compartida: ["programa compartido", "eti verde", "El programa se archivó en la carpeta de otra licenciatura"],
  nombre: ["programa · otra clave", "eti verde", "La tabla del plan y el programa usan claves distintas"],
  nombre_compartido: ["programa · otra clave", "eti verde", "Programa de otra licenciatura, con clave distinta"],
  nombre_clave_provisional: ["programa · clave provisional", "eti verde", "El archivo del programa lleva clave provisional"],
};

const CONTINUIDAD = {
  misma_clave: ["Continúa", "eti hueca"],
  otra_clave: ["Continúa con clave nueva", "eti hueca"],
  nueva: ["UEA nueva", "eti roja"],
};

const CAMPOS = [
  ["objetivo", "Objetivo general"],
  ["objetivos_parciales", "Objetivos parciales"],
  ["contenido", "Contenido sintético"],
  ["conduccion", "Modalidades de conducción"],
  ["evaluacion", "Modalidades de evaluación"],
  ["bibliografia", "Bibliografía"],
];

const esc = (s) =>
  String(s ?? "").replace(/[&<>"]/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

const norm = (s) =>
  String(s ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

const lic = (clave) => DATOS.licenciaturas.find((l) => l.clave === clave);
const num = (v) => (v === null || v === undefined ? "—" : v);

/* ------------------------------------------------------------ panorama */
function panorama() {
  const filas = DATOS.licenciaturas.map((l, i) => {
    const cv = l.creditos.vigente || {}, cp = l.creditos.propuesto || {};
    const dTot = cv.total && cp.total ? cp.total - cv.total : null;
    return `<tr onclick="location.hash='#/lic/${l.clave}'">
      <td><div style="display:flex;align-items:center;gap:10px">
        <span class="punto">${String(i + 1).padStart(2, "0")}</span>
        <strong>${esc(l.nombre)}</strong></div></td>
      <td class="num">${num(cv.general)}</td>
      <td class="num"><strong style="color:var(--rojo)">${num(cp.general)}</strong></td>
      <td class="num">${num(cv.total)}</td>
      <td class="num">${num(cp.total)}</td>
      <td class="num">${dTot === null ? "—" : (dTot > 0 ? "+" : "") + dTot}</td>
      <td class="num">${l.conteo.vigentes}</td>
      <td class="num">${l.conteo.plan}</td>
      <td class="num">${l.conteo.nuevas}</td>
      <td class="num">${l.conteo.renumeradas}</td>
      <td class="num">${l.conteo.salen}</td>
      <td class="num">${l.conteo.con_programa}</td>
    </tr>`;
  }).join("");

  const tg = DATOS.licenciaturas.map((l) => l.creditos.propuesto?.general).filter(Boolean);
  const tgUnico = [...new Set(tg)];

  vista.innerHTML = `
    <p class="kicker">Modificación a los planes de estudio · julio 2026</p>
    <h1>Las diez licenciaturas de la División</h1>
    <p class="sub">Comparación del plan vigente 2020 contra el plan modificado, y
    acceso al programa de cada Unidad de Enseñanza Aprendizaje (UEA) entregado en
    el expediente. Elige una licenciatura para explorarla.</p>

    <div class="datos">
      <div class="dato"><div class="n">10</div><div class="r">licenciaturas</div></div>
      <div class="dato"><div class="n acento">${tgUnico.length === 1 ? tgUnico[0] : "57"}</div>
        <div class="r">créditos del nuevo Tronco General</div></div>
      <div class="dato"><div class="n">${DATOS.licenciaturas.reduce((a, l) => a + l.conteo.plan, 0)}</div>
        <div class="r">UEA en los diez planes</div></div>
      <div class="dato"><div class="n">${DATOS.licenciaturas.reduce((a, l) => a + l.conteo.con_programa, 0)}</div>
        <div class="r">programas consultables</div></div>
    </div>

    <table>
      <thead><tr>
        <th>Licenciatura</th>
        <th class="num">TG 2020</th><th class="num">TG 2026</th>
        <th class="num">Total 2020</th><th class="num">Total 2026</th><th class="num">Δ</th>
        <th class="num">UEA 2020</th><th class="num">UEA 2026</th><th class="num">Nuevas</th>
        <th class="num">Renum.</th><th class="num">Salen</th><th class="num">Programas</th>
      </tr></thead>
      <tbody>${filas}</tbody>
    </table>

    <div class="aviso"><strong>Cómo leer las tres últimas columnas.</strong>
    «Nuevas» son UEA cuya clave y cuyo nombre no existían en el plan 2020.
    «Renum.» son UEA que continúan con el mismo nombre bajo una clave distinta,
    de modo que una renumeración no se confunda con una baja. «Salen» son UEA del
    plan vigente sin correspondencia de clave ni de nombre en el plan propuesto.
    La coincidencia por nombre es automática y aproximada, así que conviene
    verificar cualquier caso concreto contra el documento fuente antes de citarlo.</div>`;
}

/* -------------------------------------------------------- licenciatura */
function licenciatura(clave, q = "") {
  const l = lic(clave);
  if (!l) return panorama();
  const cv = l.creditos.vigente || {}, cp = l.creditos.propuesto || {};
  const tot = cv.total || 475;
  const barra = (c, titulo) => {
    const g = c.general || 0, p = c.profesional || 0;
    const o = Math.max((c.total || 0) - g - p - (c.nivelacion || 0), 0);
    const w = (x) => (100 * x) / tot;
    return `<div style="margin:10px 0 18px">
      <div style="font-size:12px;color:var(--gris);margin-bottom:3px">${titulo}
        <strong style="color:var(--tinta)">${num(c.total)} créditos</strong></div>
      <div class="barra-cmp" style="width:${Math.min(100, w(c.total || 0))}%">
        <span class="seg-tg" style="flex:${g}">TG ${g}</span>
        <span class="seg-pro" style="flex:${p}">Profesional ${p}</span>
        <span class="seg-otro" style="flex:${o}">Otros ${o}</span>
      </div></div>`;
  };

  const troncos = [...new Set(l.ueas.map((u) => u.tronco))].sort();
  const filtroT = $("#f-tronco")?.value || "";
  const filtroC = $("#f-cont")?.value || "";
  const filtroP = $("#f-prog")?.value || "";
  const nq = norm(q);

  const lista = l.ueas.filter((u) =>
    (!filtroT || u.tronco === filtroT) &&
    (!filtroC || u.continuidad === filtroC) &&
    (!filtroP || (filtroP === "si") === !!u.programa) &&
    (!nq || norm(u.nombre).includes(nq) || u.clave.includes(nq)));

  const filas = lista.map((u) => {
    const [txt, cls] = CONTINUIDAD[u.continuidad] || ["—", "eti hueca"];
    return `<tr onclick="location.hash='#/uea/${clave}/${u.clave}'">
      <td class="clave">${esc(u.clave)}</td>
      <td><strong>${esc(u.nombre)}</strong>${u.fuera_de_tabla
        ? ' <span class="eti hueca" title="El programa se entregó pero la tabla del plan no lista esta clave">fuera de la tabla</span>' : ""}</td>
      <td>${esc(TRONCO[u.tronco] || u.tronco)}</td>
      <td>${u.tipo || "—"}</td>
      <td class="num">${num(u.creditos)}</td>
      <td><span class="${cls}">${txt}</span></td>
      <td>${(() => {
        if (!u.programa) return '<span class="eti hueca">sin programa</span>';
        const [t, c, tip] = EMPAREJADO[u.emparejamiento] || ["programa", "eti verde", ""];
        return `<span class="${c}"${tip ? ` title="${esc(tip)}"` : ""}>${t}</span>`;
      })()}</td>
    </tr>`;
  }).join("");

  vista.innerHTML = `
    <div class="migaja"><a href="#/">Panorama</a> › ${esc(l.nombre)}</div>
    <p class="kicker">Licenciatura en</p>
    <h1>${esc(l.nombre)}</h1>

    <div class="datos">
      <div class="dato"><div class="n">${l.conteo.plan}</div><div class="r">UEA en el plan propuesto</div></div>
      <div class="dato"><div class="n acento">${l.conteo.nuevas}</div><div class="r">UEA nuevas</div></div>
      <div class="dato"><div class="n">${l.conteo.renumeradas}</div><div class="r">continúan con clave nueva</div></div>
      <div class="dato"><div class="n">${l.conteo.salen}</div><div class="r">sin correspondencia</div></div>
      <div class="dato"><div class="n">${l.conteo.con_programa}</div><div class="r">programas consultables</div></div>
    </div>

    <h2>Distribución de créditos</h2>
    ${barra(cv, "Plan vigente 2020")}
    ${barra(cp, "Plan modificado")}

    <h2>Unidades de Enseñanza Aprendizaje del plan propuesto</h2>
    <div class="filtros">
      <select id="f-tronco" onchange="render()">
        <option value="">Todos los troncos</option>
        ${troncos.map((t) => `<option value="${t}" ${t === filtroT ? "selected" : ""}>${TRONCO[t] || t}</option>`).join("")}
      </select>
      <select id="f-cont" onchange="render()">
        <option value="">Toda continuidad</option>
        ${Object.entries(CONTINUIDAD).map(([k, v]) =>
          `<option value="${k}" ${k === filtroC ? "selected" : ""}>${v[0]}</option>`).join("")}
      </select>
      <select id="f-prog" onchange="render()">
        <option value="">Con y sin programa</option>
        <option value="si" ${filtroP === "si" ? "selected" : ""}>Sólo con programa</option>
        <option value="no" ${filtroP === "no" ? "selected" : ""}>Sólo sin programa</option>
      </select>
      <span class="conteo">${lista.length} de ${l.ueas.length} UEA</span>
    </div>

    <table>
      <thead><tr><th>Clave</th><th>Unidad de Enseñanza Aprendizaje</th><th>Tronco</th>
        <th>Tipo</th><th class="num">Créd.</th><th>Continuidad</th><th>Programa</th></tr></thead>
      <tbody>${filas || '<tr><td colspan="7">Ningún resultado con estos filtros.</td></tr>'}</tbody>
    </table>

    ${l.discrepancias && l.discrepancias.length ? `<h2>Discrepancias entre la tabla del plan y los programas</h2>
      <p class="sub">Casos en que la clave de la tabla no coincide con la del programa, o en que
      el programa se archivó en la carpeta de otra licenciatura. No son errores del tablero:
      conviene revisarlos antes de dictaminar.</p>
      <table><thead><tr><th>Clave en el plan</th><th>Unidad de Enseñanza Aprendizaje</th>
        <th>Clave en el programa</th><th>Archivado en</th></tr></thead><tbody>
      ${l.discrepancias.map((x) => `<tr onclick="location.hash='#/uea/${l.clave}/${x.clave_plan}'">
        <td class="clave">${esc(x.clave_plan)}</td><td>${esc(x.nombre)}</td>
        <td class="clave">${x.provisional ? "clave provisional en el archivo"
          : esc(x.clave_programa || "la misma")}</td>
        <td>${x.programa_de ? esc(x.programa_de) : "esta licenciatura"}</td></tr>`).join("")}
      </tbody></table>` : ""}

    ${l.diff.salen.length ? `<h2>UEA del plan vigente sin correspondencia en el propuesto</h2>
      <p class="sub">Ni su clave ni su nombre aparecen en la tabla del plan modificado.
      Se listan con su tasa histórica de aprobación, del periodo 16I a 25O.</p>
      <table><thead><tr><th>Clave</th><th>Unidad de Enseñanza Aprendizaje</th>
        <th class="num">Créd.</th><th class="num">Aprobación</th></tr></thead><tbody>
      ${l.diff.salen.map((u) => `<tr style="cursor:default">
        <td class="clave">${esc(u.clave)}</td><td>${esc(u.nombre)}</td>
        <td class="num">${num(u.creditos)}</td>
        <td class="num">${u.aprobacion ? (100 * u.aprobacion).toFixed(1) + " %" : "—"}</td></tr>`).join("")}
      </tbody></table>` : ""}`;
}

/* ------------------------------------------------------------- una UEA */
function detalleUEA(claveLic, claveUEA) {
  const l = lic(claveLic);
  const u = l?.ueas.find((x) => x.clave === claveUEA);
  if (!u) return licenciatura(claveLic);
  const [txt, cls] = CONTINUIDAD[u.continuidad] || ["—", "eti hueca"];
  const campos = CAMPOS.filter(([k]) => u.campos && u.campos[k]);

  vista.innerHTML = `
    <div class="migaja"><a href="#/">Panorama</a> ›
      <a href="#/lic/${claveLic}">${esc(l.nombre)}</a> › ${esc(u.clave)}</div>
    <p class="kicker">${esc(TRONCO[u.tronco] || u.tronco)} ·
      ${u.tipo === "OPT" ? "Optativa" : "Obligatoria"}</p>
    <h1>${esc(u.nombre)}</h1>
    <p class="sub"><span class="clave">Clave ${esc(u.clave)}</span> ·
      <span class="${cls}">${txt}</span>
      ${u.clave_2020 ? ` · en el plan 2020 tenía la clave <span class="clave">${esc(u.clave_2020)}</span>` : ""}</p>

    <div class="datos">
      <div class="dato"><div class="n acento">${num(u.creditos)}</div><div class="r">créditos</div></div>
      <div class="dato"><div class="n">${num(u.teoria)}</div><div class="r">horas de teoría</div></div>
      <div class="dato"><div class="n">${num(u.practica)}</div><div class="r">horas de práctica</div></div>
      <div class="dato"><div class="n">${num(u.horas)}</div><div class="r">horas totales</div></div>
      <div class="dato"><div class="n" style="font-size:16px;line-height:1.35">
        ${u.seriacion ? esc(u.seriacion) : "Sin seriación"}</div><div class="r">seriación</div></div>
    </div>

    ${u.programa && u.emparejamiento !== "clave" ? `<div class="aviso">
      <strong>Procedencia del programa.</strong>
      ${EMPAREJADO[u.emparejamiento] ? esc(EMPAREJADO[u.emparejamiento][2]) : ""}.
      ${u.programa_de ? `Se tomó de <strong>${esc(u.programa_de)}</strong>.` : ""}
      ${u.clave_programa && !String(u.clave_programa).startsWith("prov:")
        ? `La tabla del plan lo lista como <span class="clave">${esc(u.clave)}</span> y el
           propio programa se identifica como <span class="clave">${esc(u.clave_programa)}</span>.` : ""}
      </div>` : ""}
    ${campos.length
      ? campos.map(([k, t]) => `<div class="campo"><h3>${t}</h3><pre>${esc(u.campos[k])}</pre></div>`).join("")
      : `<div class="aviso">El expediente no incluye el programa de esta UEA, o su
         archivo no tiene capa de texto extraíble. La tabla del plan sí la lista.</div>`}

    ${u.ruta ? `<div class="campo"><h3>Documento fuente</h3>
      <p class="ruta">Modificaciones Licenciaturas Julio 2026/${esc(u.ruta)}</p></div>` : ""}`;
}

/* ----------------------------------------------------- búsqueda global */
function buscar(q) {
  const nq = norm(q);
  const res = [];
  for (const l of DATOS.licenciaturas) {
    for (const u of l.ueas) {
      if (norm(u.nombre).includes(nq) || u.clave.includes(nq)) {
        res.push([l, u]);
      }
    }
  }
  vista.innerHTML = `
    <div class="migaja"><a href="#/">Panorama</a> › Búsqueda</div>
    <h1>“${esc(q)}”</h1>
    <p class="sub">${res.length} UEA en los diez planes propuestos.</p>
    <table><thead><tr><th>Clave</th><th>Unidad de Enseñanza Aprendizaje</th>
      <th>Licenciatura</th><th>Tronco</th><th>Programa</th></tr></thead><tbody>
    ${res.slice(0, 300).map(([l, u]) => `<tr onclick="location.hash='#/uea/${l.clave}/${u.clave}'">
      <td class="clave">${esc(u.clave)}</td><td><strong>${esc(u.nombre)}</strong></td>
      <td>${esc(l.nombre)}</td><td>${esc(TRONCO[u.tronco] || u.tronco)}</td>
      <td>${u.programa ? '<span class="eti verde">programa</span>' : '<span class="eti hueca">sin programa</span>'}</td>
      </tr>`).join("") || '<tr><td colspan="5">Sin resultados.</td></tr>'}
    </tbody></table>
    ${res.length > 300 ? '<p class="sub">Se muestran los primeros 300 resultados.</p>' : ""}`;
}

/* ------------------------------------------------------------- ruteo */
function render() {
  const h = location.hash.replace(/^#\/?/, "");
  const p = h.split("/").filter(Boolean);
  const q = $("#buscador").value.trim();

  if (p[0] === "buscar") { buscar(decodeURIComponent(p[1] || "")); }
  else if (p[0] === "uea" && p[1] && p[2]) { detalleUEA(p[1], p[2]); }
  else if (p[0] === "lic" && p[1]) { licenciatura(p[1], q); }
  else { panorama(); }

  document.querySelectorAll("header nav a").forEach((a) =>
    a.classList.toggle("activo", a.getAttribute("href") === "#/" + (p[0] || "")));
  window.scrollTo(0, 0);
}

window.addEventListener("hashchange", render);
window.addEventListener("DOMContentLoaded", () => {
  const b = $("#buscador");
  b.addEventListener("input", () => {
    const q = b.value.trim();
    const p = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean);
    if (p[0] === "lic") render();
    else if (q.length >= 3) location.hash = "#/buscar/" + encodeURIComponent(q);
    else if (p[0] === "buscar") location.hash = "#/";
  });
  render();
});
