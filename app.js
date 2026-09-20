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
  nombre: ["programa", "eti verde", ""],
  nombre_truncado: ["programa", "eti verde", "El nombre del archivo llegó truncado al extraerse"],
  nombre_aproximado: ["programa", "eti verde", "Emparejado por parecido del nombre, no exacto"],
  clave_compartida: ["programa compartido", "eti verde", "UEA compartida: el programa se archivó en otra licenciatura"],
  nombre_compartido: ["programa compartido", "eti verde", "UEA compartida: el programa se archivó en otra licenciatura"],
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
        <div><strong>${esc(l.nombre)}</strong>${l.nombre_propuesto
          ? `<div class="renombrada">pasa a llamarse ${esc(l.nombre_propuesto)}</div>` : ""}
        </div></div></td>
      <td class="num" data-r="TG 2020">${num(cv.general)}</td>
      <td class="num" data-r="TG 2026"><strong class="realce">${num(cp.general)}</strong></td>
      <td class="num" data-r="Total 2020">${num(cv.total)}</td>
      <td class="num" data-r="Total 2026">${num(cp.total)}</td>
      <td class="num" data-r="Δ créditos">${dTot === null ? "—" : (dTot > 0 ? "+" : "") + dTot}</td>
      <td class="num" data-r="UEA 2020">${l.conteo.vigentes}</td>
      <td class="num" data-r="UEA 2026">${l.conteo.plan}</td>
      <td class="num" data-r="Nuevas">${l.conteo.nuevas}</td>
      <td class="num" data-r="Renumeradas">${l.conteo.renumeradas}</td>
      <td class="num" data-r="Salen">${l.conteo.salen}</td>
      <td class="num" data-r="Cadena">${l.seriacion?.vigente?.profundidad_max ?? "—"} →
        <strong class="realce">${l.seriacion?.propuesto?.sin_columna
          ? "?" : l.seriacion?.propuesto?.profundidad_max ?? "—"}</strong></td>
      <td class="num" data-r="Programas">${l.conteo.con_programa}</td>
    </tr>`;
  }).join("");

  const tg = DATOS.licenciaturas.map((l) => l.creditos.propuesto?.general).filter(Boolean);
  const tgUnico = [...new Set(tg)];

  vista.innerHTML = `
    <div class="plano plano-cabecera plano-rojo">
    <p class="kicker">Modificación a los planes de estudio · julio 2026</p>
    <h1>Las diez licenciaturas de la División</h1>
    <p class="sub">Comparación del plan vigente 2020 contra el plan modificado, y
    acceso al programa de cada Unidad de Enseñanza Aprendizaje (UEA) entregado en
    el expediente. Elige una licenciatura para explorarla.</p>

    <div class="datos">
      <div class="dato"><div class="n">10</div><div class="r">licenciaturas</div></div>
      <div class="dato acentuada"><div class="n acento">${tgUnico.length === 1 ? tgUnico[0] : "57"}</div>
        <div class="r">créditos del nuevo Tronco General</div></div>
      <div class="dato"><div class="n">${DATOS.licenciaturas.reduce((a, l) => a + l.conteo.plan, 0)}</div>
        <div class="r">UEA en los diez planes</div></div>
      <div class="dato"><div class="n">${DATOS.licenciaturas.reduce((a, l) => a + l.conteo.con_programa, 0)}</div>
        <div class="r">programas consultables</div></div>
    </div>
    </div>

    <table class="apilada">
      <thead><tr>
        <th>Licenciatura</th>
        <th class="num">TG 2020</th><th class="num">TG 2026</th>
        <th class="num">Total 2020</th><th class="num">Total 2026</th><th class="num">Δ</th>
        <th class="num">UEA 2020</th><th class="num">UEA 2026</th><th class="num">Nuevas</th>
        <th class="num">Renum.</th><th class="num">Salen</th>
        <th class="num">Cadena</th><th class="num">Programas</th>
      </tr></thead>
      <tbody>${filas}</tbody>
    </table>

    <div class="aviso"><strong>Sobre las claves.</strong>
    Las claves de las UEA nuevas son tentativas. Las definitivas se asignan en una ronda
    posterior del proceso, así que el tablero identifica cada UEA por su nombre y usa la clave
    sólo como referencia al documento.</div>

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
      <div class="tenue" style="font-size:12px;margin-bottom:3px">${titulo}
        <strong class="fuerte">${num(c.total)} créditos</strong></div>
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
      <td class="clave" data-r="Clave">${esc(u.clave)}${u.clave_por_asignar
        ? ' <span class="eti hueca" title="La clave definitiva se asigna más adelante en el proceso">por asignar</span>' : ""}</td>
      <td><strong>${esc(u.nombre)}</strong>${u.fuera_de_tabla
        ? ' <span class="eti hueca" title="El programa se entregó pero la tabla del plan no lista esta clave">fuera de la tabla</span>' : ""}</td>
      <td data-r="Tronco">${esc(TRONCO[u.tronco] || u.tronco)}</td>
      <td data-r="Tipo">${u.tipo || "—"}</td>
      <td class="num" data-r="Créditos">${num(u.creditos)}</td>
      <td data-r="Continuidad"><span class="${cls}">${txt}</span></td>
      <td data-r="Programa">${(() => {
        if (!u.programa) return '<span class="eti hueca">sin programa</span>';
        const [t, c, tip] = EMPAREJADO[u.emparejamiento] || ["programa", "eti verde", ""];
        return `<span class="${c}"${tip ? ` title="${esc(tip)}"` : ""}>${t}</span>`;
      })()}</td>
    </tr>`;
  }).join("");

  vista.innerHTML = `
    <div class="plano plano-cabecera plano-tinta">
    <div class="migaja"><a href="#/">Panorama</a> › ${esc(l.nombre)}</div>
    <p class="kicker">Licenciatura en</p>
    <h1>${esc(l.nombre_propuesto || l.nombre)}</h1>
    ${l.nombre_propuesto ? `<div class="aviso">
      <strong>Cambia de denominación.</strong>
      El plan vigente se llama <em>Licenciatura en ${esc(l.nombre)}</em> y el modificado
      pasa a ser <em>Licenciatura en ${esc(l.nombre_propuesto)}</em>. El título que se
      expide será de ${esc(l.titulo_propuesto)}.</div>` : ""}

    <div class="datos">
      <div class="dato"><div class="n">${l.conteo.plan}</div><div class="r">UEA en el plan propuesto</div></div>
      <div class="dato acentuada"><div class="n acento">${l.conteo.nuevas}</div><div class="r">UEA nuevas</div></div>
      <div class="dato"><div class="n">${l.conteo.renumeradas}</div><div class="r">continúan con clave nueva</div></div>
      <div class="dato"><div class="n">${l.conteo.salen}</div><div class="r">sin correspondencia</div></div>
      <div class="dato"><div class="n">${l.conteo.con_programa}</div><div class="r">programas consultables</div></div>
    </div>
    </div>

    <h2>Distribución de créditos</h2>
    ${barra(cv, "Plan vigente 2020")}
    ${barra(cp, "Plan modificado")}

    ${seriacion(l)}

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

    <table class="apilada por-nombre">
      <thead><tr><th>Clave</th><th>Unidad de Enseñanza Aprendizaje</th><th>Tronco</th>
        <th>Tipo</th><th class="num">Créd.</th><th>Continuidad</th><th>Programa</th></tr></thead>
      <tbody>${filas || '<tr><td colspan="7">Ningún resultado con estos filtros.</td></tr>'}</tbody>
    </table>

    ${(() => {
      const sp = l.ueas.filter((u) => !u.programa && !u.fuera_de_tabla);
      if (!sp.length) return "";
      return `<h2>UEA sin programa localizado en el expediente</h2>
      <p class="sub">La tabla del plan las lista, pero no se encontró su programa. Se muestra
      lo más parecido que hay en el expediente, para poder preguntar a la coordinación si el
      programa falta o si está entregado bajo otro nombre.</p>
      <table class="apilada por-nombre"><thead><tr><th>Clave en el plan</th><th>Unidad de Enseñanza Aprendizaje</th>
        <th>Tronco</th><th>Lo más parecido en el expediente</th></tr></thead><tbody>
      ${sp.map((u) => `<tr onclick="location.hash='#/uea/${l.clave}/${u.clave}'">
        <td class="clave" data-r="Clave">${esc(u.clave)}</td><td><strong>${esc(u.nombre)}</strong></td>
        <td data-r="Tronco">${esc(TRONCO[u.tronco] || u.tronco || "")}</td>
        <td data-r="Lo más parecido">${u.candidato ? `${esc(u.candidato.nombre)}
             <span class="eti hueca">${esc(u.candidato.lic)} · ${u.candidato.similitud}</span>`
             : "<span class=\"eti hueca\">sin parecido</span>"}</td></tr>`).join("")}
      </tbody></table>`;
    })()}

    ${l.procedencias && l.procedencias.length ? `<h2>Programas archivados en otra licenciatura</h2>
      <p class="sub">UEA compartidas entre carreras cuyo programa se entregó una sola vez.
      El tablero lo toma de donde está.</p>
      <table class="apilada por-nombre"><thead><tr><th>Clave en el plan</th><th>Unidad de Enseñanza Aprendizaje</th>
        <th>Archivado en</th></tr></thead><tbody>
      ${l.procedencias.map((x) => `<tr onclick="location.hash='#/uea/${l.clave}/${x.clave_plan}'">
        <td class="clave" data-r="Clave">${esc(x.clave_plan)}</td><td>${esc(x.nombre)}</td>
        <td data-r="Archivado en">${esc(x.programa_de || "")}</td></tr>`).join("")}
      </tbody></table>` : ""}

    ${l.diff.salen.length ? `<h2>UEA del plan vigente sin correspondencia en el propuesto</h2>
      <p class="sub">Ni su clave ni su nombre aparecen en la tabla del plan modificado.
      Se listan con su tasa histórica de aprobación, del periodo 16I a 25O.</p>
      <table class="apilada por-nombre"><thead><tr><th>Clave</th><th>Unidad de Enseñanza Aprendizaje</th>
        <th class="num">Créd.</th><th class="num">Aprobación</th></tr></thead><tbody>
      ${l.diff.salen.map((u) => `<tr onclick="location.hash='#/uea2020/${l.clave}/${u.clave}'">
        <td class="clave" data-r="Clave">${esc(u.clave)}</td><td>${esc(u.nombre)}</td>
        <td class="num" data-r="Créditos">${num(u.creditos)}</td>
        <td class="num" data-r="Aprobación 16I–25O">${u.aprobacion ? (100 * u.aprobacion).toFixed(1) + " %" : "—"}</td></tr>`).join("")}
      </tbody></table>` : ""}`;
}

/* --------------------------------------------------------- seriación */
function cadena(nombres) {
  if (!nombres || nombres.length < 2) return '<p class="sub">Sin cadenas de seriación.</p>';
  return `<div class="cadena">${nombres.map((n, i) =>
    `<span class="eslabon"><span class="punto pq">${i + 1}</span>${esc(n)}</span>`).join(
    '<span class="flecha">→</span>')}</div>`;
}

function seriacion(l) {
  const v = l.seriacion?.vigente, p = l.seriacion?.propuesto;
  if (!v || !p) return "";
  const fila = (t, m, acento) => `<tr>
    <td><strong>${t}</strong></td>
    <td class="num" data-r="UEA con prerrequisito">${m.con_prerrequisito} <span class="tenue">de ${m.ueas}</span></td>
    <td class="num" data-r="Porcentaje">${m.pct_con_prerrequisito} %</td>
    <td class="num" data-r="Seriaciones">${m.aristas}</td>
    <td class="num" data-r="Cadena más larga"><strong${acento ? ' class="realce"' : ""}>${m.profundidad_max}</strong></td>
    <td class="num" data-r="Profundidad media"><strong${acento ? ' class="realce"' : ""}>${m.profundidad_media}</strong></td></tr>`;
  return `<h2>Cadenas de seriación</h2>
    ${p.sin_columna ? `<div class="aviso"><strong>Dato incompleto.</strong>
      La tabla del plan propuesto de esta licenciatura no dejó legible la columna de
      seriación al extraerse, así que sus cifras aparecen en cero y no deben leerse como
      ausencia de seriación. El plan vigente sí se midió.</div>`
      : (p.aristas <= 2 && p.por_creditos > 5) ? `<div class="aviso">
      <strong>Este plan casi no encadena UEA con UEA.</strong>
      En lugar de pedir una UEA antecedente, condiciona ${p.por_creditos} de sus UEA a un
      mínimo de créditos acumulados, que no crea cadena: cualquier combinación de UEA sirve
      para reunirlos. Por eso su cadena más larga es de ${p.profundidad_max}.</div>` : ""}
    <table class="apilada"><thead><tr><th>Plan</th><th class="num">UEA con prerrequisito</th>
      <th class="num">%</th><th class="num">Seriaciones</th>
      <th class="num">Cadena más larga</th><th class="num">Profundidad media</th></tr></thead>
      <tbody>${fila("Vigente 2020", v, false)}${fila("Modificado", p, true)}</tbody></table>
    <div class="aviso"><strong>Cómo se mide.</strong>
      La <em>cadena más larga</em> es cuántas UEA hay que ir librando, una tras otra, para
      llegar a la más encadenada del plan. La <em>profundidad media</em> promedia ese
      recorrido sobre todas las UEA, así que resume en una cifra cuánto encadena el plan
      entero: cuanto más baja, antes se puede llegar a cualquier UEA. Sólo se cuentan los
      prerrequisitos de UEA; los mínimos de créditos van aparte${
        p.por_creditos ? ` — en este plan, ${p.por_creditos} UEA los piden` : ""}.</div>
    <h3>La cadena más larga del plan vigente 2020</h3>
    ${cadena(v.cadena_nombres)}
    <h3>La cadena más larga del plan modificado</h3>
    ${p.sin_columna ? '<p class="sub">No medible con la columna extraída.</p>'
      : cadena(p.cadena_nombres)}`;
}


/* ------------------------------------------------- árbol de dependencias */
function indices(l, plan) {
  const aristas = l.grafo?.[plan] || [];
  const antes = {}, despues = {};
  for (const [x, y] of aristas) {
    (antes[y] = antes[y] || []).push(x);
    (despues[x] = despues[x] || []).push(y);
  }
  const nombres = {};
  if (plan === "propuesto") {
    for (const u of l.ueas) nombres[u.clave] = u.nombre;
  } else {
    for (const u of l.vigentes) nombres[u.clave] = u.nombre;
  }
  return { antes, despues, nombres };
}

function rama(clave, mapa, nombres, lic, plan, nivel, vistos, max) {
  const hijos = mapa[clave] || [];
  if (!hijos.length || nivel >= max) return "";
  return `<ul class="arbol">${hijos.map((h) => {
    const ciclo = vistos.has(h);
    const v2 = new Set(vistos); v2.add(h);
    const ruta = plan === "propuesto" ? `#/uea/${lic}/${h}` : `#/uea2020/${lic}/${h}`;
    return `<li><a href="${ruta}">${esc(nombres[h] || h)}</a>
      <span class="clave">${esc(h)}</span>
      ${ciclo ? '<span class="eti hueca">ya visto</span>'
              : rama(h, mapa, nombres, lic, plan, nivel + 1, v2, max)}</li>`;
  }).join("")}</ul>`;
}

function cuenta(clave, mapa) {
  const vistos = new Set(), cola = [clave];
  while (cola.length) {
    for (const h of mapa[cola.pop()] || []) {
      if (!vistos.has(h)) { vistos.add(h); cola.push(h); }
    }
  }
  return vistos.size;
}

function dependencias(l, clave, plan, titulo) {
  const { antes, despues, nombres } = indices(l, plan);
  if (!nombres[clave] && plan === "propuesto") return "";
  const nA = cuenta(clave, antes), nD = cuenta(clave, despues);
  if (!nA && !nD) {
    return `<div class="campo"><h3>${titulo}</h3>
      <p class="sub">Ninguna UEA la antecede ni depende de ella en este plan.</p></div>`;
  }
  const bloque = (mapa, t, n, vacio) => `<div class="mitad">
    <h4>${t} <span class="conteo-arbol">${n}</span></h4>
    ${n ? rama(clave, mapa, nombres, l.clave, plan, 0, new Set([clave]), 3)
        : `<p class="sub">${vacio}</p>`}</div>`;
  return `<div class="campo"><h3>${titulo}</h3>
    <div class="dos-arboles">
      ${bloque(antes, "Hay que aprobar antes", nA, "Nada la antecede: se puede cursar desde el principio.")}
      ${bloque(despues, "Se abren después", nD, "No bloquea ninguna otra UEA.")}
    </div></div>`;
}

/* -------------------------------------------------- UEA del plan vigente */
function detalleUEA2020(claveLic, claveUEA) {
  const l = lic(claveLic);
  const u = l?.vigentes.find((x) => x.clave === claveUEA);
  if (!u) return licenciatura(claveLic);
  vista.innerHTML = `
    <div class="migaja"><a href="#/">Panorama</a> ›
      <a href="#/lic/${claveLic}">${esc(l.nombre)}</a> › plan vigente 2020</div>
    <p class="kicker">Plan vigente 2020 · ${esc(TRONCO[u.tronco] || u.tronco || "")}</p>
    <h1>${esc(u.nombre)}</h1>
    <p class="sub"><span class="clave">Clave ${esc(u.clave)}</span></p>
    <div class="datos">
      <div class="dato acentuada"><div class="n acento">${num(u.creditos)}</div><div class="r">créditos</div></div>
      <div class="dato"><div class="n">${u.aprobacion ? (100 * u.aprobacion).toFixed(1) + " %" : "—"}</div>
        <div class="r">aprobación histórica 16I–25O</div></div>
      <div class="dato"><div class="n">${u.intentos ?? "—"}</div>
        <div class="r">inscripciones esperadas</div></div>
    </div>
    ${dependencias(l, u.clave, "vigente", "Dependencias en el plan vigente 2020")}
    <div class="aviso">Esta ficha corresponde al plan vigente. El expediente no
    incluye programas de las UEA que sólo existen en él.</div>`;
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
    <p class="sub"><span class="clave">Clave ${esc(u.clave)}</span>${u.clave_por_asignar
      ? ' <span class="eti hueca">por asignar</span>' : ""} ·
      <span class="${cls}">${txt}</span>
      ${u.clave_2020 ? ` · en el plan 2020 era
        <a href="#/uea2020/${claveLic}/${esc(u.clave_2020)}">la clave
        <span class="clave">${esc(u.clave_2020)}</span></a>` : ""}</p>

    <div class="datos">
      <div class="dato acentuada"><div class="n acento">${num(u.creditos)}</div><div class="r">créditos</div></div>
      <div class="dato"><div class="n">${num(u.teoria)}</div><div class="r">horas de teoría</div></div>
      <div class="dato"><div class="n">${num(u.practica)}</div><div class="r">horas de práctica</div></div>
      <div class="dato"><div class="n">${num(u.horas)}</div><div class="r">horas totales</div></div>
      <div class="dato"><div class="n" style="font-size:16px;line-height:1.35">
        ${u.seriacion ? esc(u.seriacion) : "Sin seriación"}</div><div class="r">seriación</div></div>
    </div>

    ${u.clave_programa || u.programa_sin_clave || u.clave_repetida ? `<div class="aviso">
      <strong>Sobre la clave.</strong>
      Las claves de los programas nuevos son tentativas — las definitivas se asignan en una
      ronda posterior del proceso —, así que un programa puede conservar la clave de aquel del
      que se derivó.
      ${u.clave_programa ? `Aquí la tabla del plan lo lista como
        <span class="clave">${esc(u.clave)}</span> y la ficha del programa trae
        <span class="clave">${esc(u.clave_programa)}</span>.` : ""}
      ${u.clave_repetida ? "Esa clave aparece además en otro programa de la misma licenciatura." : ""}
      El tablero empareja por nombre, no por clave.</div>` : ""}
    ${u.programa_de ? `<div class="aviso">
      <strong>Procedencia del programa.</strong>
      Es una UEA compartida y su programa se archivó en
      <strong>${esc(u.programa_de)}</strong>, de donde se tomó.
      </div>` : ""}
    ${campos.length
      ? campos.map(([k, t]) => `<div class="campo"><h3>${t}</h3><pre>${esc(u.campos[k])}</pre></div>`).join("")
      : `<div class="aviso"><strong>Sin programa localizado.</strong>
         La tabla del plan lista esta UEA, pero no se encontró su programa en el expediente.
         ${u.candidato ? `Lo más parecido es <strong>${esc(u.candidato.nombre)}</strong>,
           de ${esc(u.candidato.lic)}, con una similitud de ${u.candidato.similitud}.` : ""}
         Conviene preguntar a la coordinación si falta o si se entregó con otro nombre.</div>`}

    ${dependencias(l, u.clave, "propuesto", "Dependencias en el plan modificado")}
    ${u.clave_2020 || u.continuidad === "misma_clave"
      ? dependencias(l, u.clave_2020 || u.clave, "vigente",
                     "Dependencias que tenía en el plan vigente 2020") : ""}

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
    <table class="apilada por-nombre"><thead><tr><th>Clave</th><th>Unidad de Enseñanza Aprendizaje</th>
      <th>Licenciatura</th><th>Tronco</th><th>Programa</th></tr></thead><tbody>
    ${res.slice(0, 300).map(([l, u]) => `<tr onclick="location.hash='#/uea/${l.clave}/${u.clave}'">
      <td class="clave" data-r="Clave">${esc(u.clave)}</td><td><strong>${esc(u.nombre)}</strong></td>
      <td data-r="Licenciatura">${esc(l.nombre)}</td><td data-r="Tronco">${esc(TRONCO[u.tronco] || u.tronco)}</td>
      <td data-r="Programa">${u.programa ? '<span class="eti verde">programa</span>' : '<span class="eti hueca">sin programa</span>'}</td>
      </tr>`).join("") || '<tr><td colspan="5">Sin resultados.</td></tr>'}
    </tbody></table>
    ${res.length > 300 ? '<p class="sub">Se muestran los primeros 300 resultados.</p>' : ""}`;
}

/* ═══════════════════════════════════════════════════════════════════
   Niveles, campo cromático y cortina
   ═══════════════════════════════════════════════════════════════════
   El tablero tiene cuatro niveles de profundidad y a cada uno le toca un
   campo de color, declarado en estilo.css. Aquí sólo se decide en qué
   nivel está el usuario y se orquesta el paso de un campo a otro.

     0 portada      tinta   umbral
     1 panorama     rojo    índice de las diez licenciaturas
     2 licenciatura tinta   comparación plan contra plan
     3 UEA          papel   programa completo, prosa larga
       búsqueda     papel   atajo al nivel 3, comparte su campo

   El paso de un campo a otro lo hace un plano del color que llega, que
   entra por la derecha al bajar de nivel y por la izquierda al subir. La
   vista nueva se pinta mientras el plano tapa, de modo que al retirarse
   descubre una página ya hecha. Si el campo no cambia —de una UEA a otra,
   de una búsqueda a su resultado— no hay plano: sólo un asentamiento de
   180 ms, para no cobrarle espera a quien navega rápido. */

const CAMPO = { panorama: "papel", lic: "papel", uea: "papel", buscar: "papel" };
const HONDURA = { panorama: 1, lic: 2, uea: 3, buscar: 3 };
// Color del plano que barre al llegar a cada nivel. El panorama trae el suyo
// en rojo —el mismo plano que se queda de encabezado— y la licenciatura en
// tinta, de modo que bajar del índice al plan se ve aunque los dos campos
// sean oscuros: el barrido se lleva el plano rojo y no lo devuelve.
const CORTINA = { panorama: "#CD032E", lic: "#1C1C1C", uea: "#FFFFFF", buscar: "#FFFFFF" };

const reducido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* Reproduce exactamente las mismas salvaguardas que los pintores: si la
   clave no existe, la vista que se dibuja es la de su nivel superior, y el
   campo tiene que corresponder a lo que se ve, no a lo que pedía la ruta. */
function nivelDe(p) {
  if (p[0] === "buscar") return "buscar";
  if ((p[0] === "uea" || p[0] === "uea2020") && p[1] && p[2]) {
    const l = lic(p[1]);
    if (!l) return "panorama";
    const hay = p[0] === "uea"
      ? l.ueas?.some((x) => x.clave === p[2])
      : l.vigentes?.some((x) => x.clave === p[2]);
    return hay ? "uea" : "lic";   // una clave que no existe cae a su licenciatura
  }
  if (p[0] === "lic") return lic(p[1]) ? "lic" : "panorama";
  return "panorama";
}

let nivelActual = null, rutaActual = null, animCortina = null;

function aplicarCampo(nivel) {
  document.body.dataset.campo = CAMPO[nivel];
  document.body.dataset.nivel = nivel;
}

// ms del viaje del plano. En pantalla de teléfono el recorrido es más corto
// —la misma firma de nivel, menos espera— porque el barrido cruza una pantalla
// pequeña y cualquier demora se siente el doble mientras se navega con el pulgar.
const estrecho = () => window.matchMedia("(max-width: 720px)").matches;
const TAPA = () => (estrecho() ? 170 : 230);
const DESCUBRE = () => (estrecho() ? 210 : 300);
let generacion = 0;

function barrido(nivel, haciaDentro, alCubrir) {
  const c = $("#cortina");
  const desde = haciaDentro ? "translateX(100%)" : "translateX(-100%)";
  const hasta = haciaDentro ? "translateX(-100%)" : "translateX(100%)";
  const mia = ++generacion;   // una navegación nueva invalida la anterior
  c.style.background = CORTINA[nivel];
  c.style.display = "block";
  if (animCortina) animCortina.cancel();
  const msTapa = TAPA(), msDescubre = DESCUBRE();
  const tapa = c.animate([{ transform: desde }, { transform: "translateX(0)" }],
    { duration: msTapa, easing: "cubic-bezier(.66,0,.34,1)", fill: "forwards" });
  animCortina = tapa;

  // El relevo va atado al reloj de la animación, pero con red: si el motor
  // no la corre —pestaña en segundo plano, contexto sin composición— un
  // temporizador hace el relevo igual, para que el plano no se quede
  // tapando la página. La vista se pinta una sola vez, pase lo que pase.
  let relevado = false, cerrado = false;
  const seguir = () => {
    if (relevado || mia !== generacion) return;
    relevado = true;
    clearTimeout(redTapa);
    alCubrir();
    const descubre = c.animate([{ transform: "translateX(0)" }, { transform: hasta }],
      { duration: msDescubre, easing: "cubic-bezier(.32,0,.18,1)", fill: "forwards" });
    animCortina = descubre;
    const cerrar = () => {
      if (cerrado || mia !== generacion) return;
      cerrado = true;
      clearTimeout(redFin);
      c.style.display = "none";
      animCortina = null;
    };
    const redFin = setTimeout(cerrar, msDescubre + 400);
    descubre.finished.then(cerrar).catch(() => {});
  };
  const redTapa = setTimeout(seguir, msTapa + 400);
  tapa.finished.then(seguir).catch(() => {});
}

function quitarPortada() {
  const p = $("#portada");
  if (p) p.remove();
  document.body.classList.remove("con-portada");
}

function contadores() {
  if (reducido) {
    document.querySelectorAll(".p-cifras b").forEach((b) => (b.textContent = b.dataset.hasta));
    return;
  }
  document.querySelectorAll(".p-cifras b").forEach((b) => {
    const hasta = +b.dataset.hasta, ini = performance.now(), dur = 1100;
    const paso = (t) => {
      const k = Math.min((t - ini) / dur, 1);
      // desaceleración cúbica: la cifra corre y se asienta, no aterriza de golpe
      b.textContent = Math.round(hasta * (1 - Math.pow(1 - k, 3)));
      if (k < 1) requestAnimationFrame(paso);
    };
    requestAnimationFrame(paso);
  });
}

/* ------------------------------------------------------------- ruteo */
function pintar(p, q) {
  if (p[0] === "buscar") { buscar(decodeURIComponent(p[1] || "")); }
  else if (p[0] === "uea2020" && p[1] && p[2]) { detalleUEA2020(p[1], p[2]); }
  else if (p[0] === "uea" && p[1] && p[2]) { detalleUEA(p[1], p[2]); }
  else if (p[0] === "lic" && p[1]) { licenciatura(p[1], q); }
  else { panorama(); }

  document.querySelectorAll("header nav a").forEach((a) =>
    a.classList.toggle("activo", a.getAttribute("href") === "#/" + (p[0] || "")));
  window.scrollTo(0, 0);
}

function anima(clase) {
  if (reducido) return;
  vista.classList.remove("entrando", "rapido");
  void vista.offsetWidth;
  vista.classList.add(clase);
}

function render(opts = {}) {
  const h = location.hash.replace(/^#\/?/, "");
  const p = h.split("/").filter(Boolean);
  const q = $("#buscador").value.trim();
  const nivel = nivelDe(p);
  const clave = p.join("/");
  const previo = nivelActual;
  // Un filtro o una tecla dentro de la misma vista repinta sin animar: la
  // animación es para el cambio de vista, no para el cambio de contenido.
  // Teclear en el buscador reescribe la ruta con cada letra, así que se
  // cuenta como la misma vista mientras se siga buscando.
  const mismaVista = !opts.forzar &&
    (clave === rutaActual || (nivel === "buscar" && previo === "buscar"));
  rutaActual = clave;
  nivelActual = nivel;

  const cortina = !reducido && previo !== null &&
    (opts.cortina || !!$("#portada") || CORTINA[nivel] !== CORTINA[previo]);

  if (!cortina) {
    if (previo !== null) quitarPortada();
    aplicarCampo(nivel);
    pintar(p, q);
    if (!mismaVista) anima(nivel === previo ? "rapido" : "entrando");
    return;
  }
  barrido(nivel, HONDURA[nivel] >= HONDURA[previo], () => {
    quitarPortada();
    aplicarCampo(nivel);
    pintar(p, q);
    anima("entrando");
  });
}

window.addEventListener("hashchange", () => render());
window.addEventListener("DOMContentLoaded", () => {
  // La portada sólo recibe a quien llega sin destino. Un enlace profundo
  // —#/lic/civ, #/uea/…— entra directo a lo que pidió.
  if (location.hash.replace(/^#\/?/, "")) {
    quitarPortada();
  } else {
    document.body.classList.add("con-portada");
    contadores();
    $("#portada").addEventListener("click", (e) => {
      if (e.target.closest(".p-entrar")) {
        e.preventDefault();
        render({ cortina: true, forzar: true });
      }
    });
  }
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
