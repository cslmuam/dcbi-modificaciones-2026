#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mallas curriculares de las diez licenciaturas, en HTML navegable y en PDF.

Cada malla es un deck de cuatro diapositivas de 1280x720 con el sistema
`/uam-deck` —el mismo aparato del deck de consulta de Ingeniería Ambiental—:
una portada con los créditos por tronco y tres láminas de cuatro trimestres,
con los troncos distinguidos por masa de color. Cada recuadro de UEA es un
enlace a la ficha de su programa en el tablero; cada casilla de optativa lleva
a la lista de optativas de la licenciatura.

Dos salidas por licenciatura, del mismo marcado:

- `<clave>.html`, con enlaces relativos al tablero (`../index.html#/…`) que
  abren en la ventana principal, de modo que funcionan dentro del visor del
  tablero, sueltos, sin conexión y en GitHub Pages.
- `<clave>.pdf`, impreso por Chrome desde una copia con enlaces absolutos a
  la dirección pública del tablero, para que el PDF descargado siga llevando
  a cada programa.

Lee `mallas.json`, que produce `extraer_mallas.py`. Uso:

    python3 extraer_mallas.py && python3 construir_mallas.py [clave …]
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PUBLICO = "https://cslmuam.github.io/dcbi-modificaciones-2026/"
LOCAL = "../index.html"

ROMANO = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII",
          8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"}

# Documento del expediente del que sale cada malla (ver extraer_mallas.py).
FUENTE = {
    "amb": "Ing. Ambiental/5. Boligrama/Malla curricular-Ing. Ambiental 2026.xlsx",
    "civ": "Ing. Civil/Mapa curricular_claves_Ing_Civil (julio_2026)V4.xlsx",
    "com": "Ing. Computación/1. Pertinencia y justificación, Figura 5",
    "ele": "Ing. Electrica/05.- Boligrama/Mapa_curricular_09_2026.pdf",
    "elo": "Ing. Electrónica/05_BoligramaSisEloCiber_Ago26.xlsx",
    "fis": "Ing. Física/MALLA CURRICULAR.pdf",
    "ind": "Ing. Industrial/5. Boligrama/Diagrama de seriación Industrial 14 09 26.xlsm",
    "mec": "Ing. Mecánica/5. Boligrama/Mapa Curricular_2026 - v35.pdf",
    "met": "Ing. Metalúrgica/Boligrama_Metalurgia y Materiales_4 sept 26.xlsx",
    "qui": "Ing. Química/Mapa Curricular (12-07-2026).xlsx",
}

# Lo que la malla de la coordinación trae distinto del plan. Se imprime en la
# portada: la malla se reproduce tal como se entregó.
NOTA = {
    "elo": "Los recuadros del trimestre XI suman 27 cr&eacute;ditos y la columna "
           "de totales del boligrama, 30. La malla suma 465 y el plan declara 468.",
    "met": "La malla de la coordinaci&oacute;n suma 459 cr&eacute;ditos y el plan "
           "declara 462.",
    "qui": "La malla de la coordinaci&oacute;n suma 473 cr&eacute;ditos y el plan "
           "declara 471.",
}

ENTIDAD = {"á": "&aacute;", "é": "&eacute;", "í": "&iacute;", "ó": "&oacute;",
           "ú": "&uacute;", "ñ": "&ntilde;", "Á": "&Aacute;", "É": "&Eacute;",
           "Í": "&Iacute;", "Ó": "&Oacute;", "Ú": "&Uacute;", "Ñ": "&Ntilde;",
           "ü": "&uuml;", "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}


def ent(texto):
    return "".join(ENTIDAD.get(c, c) for c in str(texto))


def nombre_html(nombre):
    """El numeral romano final no se queda solo en un renglón («Aplicaciones
    I»): lo une a la palabra anterior un espacio que no se parte."""
    return re.sub(r" ([IVX]{1,4})$", r"&nbsp;\1", ent(nombre))


def _cr(n):
    return f"{n:g}" if n else "&mdash;"


# ── componentes, los del deck de Ambiental ───────────────────────────────────
def footer(tag, n, total):
    return (f'<div class="footer-rule"></div>\n<div class="footer">\n'
            f'  <img src="recursos/logo_footer_web.png" alt="UAM">\n'
            f'  <span class="folio">{tag} &middot; {n:02d}/{total}</span>\n</div>')


def header(kicker, title, subtitle=""):
    sub = f'<p class="subtitle">{subtitle}</p>' if subtitle else ""
    return (f'<div class="slide-body"><div class="hd">\n'
            f'  <p class="kicker">{kicker}</p>\n'
            f'  <h1 class="title">{title}</h1>\n  {sub}\n'
            f'  <div class="hd-rule"></div>\n</div>')


def dato(num, label, accent=False):
    ncls = "num" + (" accent" if accent else "")
    return (f'<div class="dato"><div class="{ncls}">{num}</div>'
            f'<div class="label">{label}</div></div>')


TRONCO_COLOR = {
    "general": ("var(--uamlightgray)", "var(--uamblue)", "var(--uamgray)",
                "box-shadow: inset 0 0 0 1px var(--hairline);"),
    "profesional": ("var(--uamred)", "#FFFFFF", "rgba(255,255,255,.82)", ""),
    "integracion": ("var(--uamblue)", "#FFFFFF", "rgba(255,255,255,.72)", ""),
}


def celda(u, tipo, base, lic):
    nom_px, nom_lh, cr_px, pad = tipo
    if len(u["nombre"]) > 55:        # nombres de cinco renglones: un paso menos
        nom_px, nom_lh = nom_px - 1.5, nom_lh - 2
    fondo, tinta, tinta_cr, extra = TRONCO_COLOR[u["tronco"]]
    if u["opt"]:
        href, titulo = f"{base}#/lic/{lic}/optativas", "Ver las optativas de la licenciatura"
    elif u["ruta"]:
        href, titulo = base + u["ruta"], f"Abrir el programa de {u['nombre']}"
    else:
        href = titulo = None
    estilo = (f'background:{fondo}; color:{tinta}; {extra} padding:{pad}; '
              f'display:flex; flex-direction:column; justify-content:space-between; '
              f'min-height:0; overflow:hidden; text-decoration:none;')
    cuerpo = (f'<span style="font-size:{nom_px}px; line-height:{nom_lh}px; font-weight:700;">'
              f'{nombre_html(u["nombre"])}</span>'
              f'<span style="font-size:{cr_px}px; color:{tinta_cr}; margin-top:5px;">'
              f'{_cr(u["creditos"])} cr&eacute;ditos</span>')
    if not href:
        return f'<div class="celda" style="{estilo}">{cuerpo}</div>'
    return (f'<a class="celda t-{u["tronco"]}" href="{ent(href)}" target="_top" '
            f'title="{ent(titulo)}" style="{estilo}">{cuerpo}</a>')


def renglon_trimestre(t, columnas, tipo, lbl_w, base, lic):
    cuerpo = "".join(celda(u, tipo, base, lic) for u in t["ueas"])
    cuerpo += "<div></div>" * (columnas - len(t["ueas"]))
    return (f'<div style="display:grid; grid-template-columns:{lbl_w}px repeat({columnas}, 1fr); '
            f'gap:6px; flex:1; min-height:0;">'
            f'<div style="display:flex; flex-direction:column; justify-content:center; '
            f'border-right:1px solid var(--hairline); padding-right:10px;">'
            f'<span style="font-size:12px; font-weight:700; letter-spacing:.05em; '
            f'white-space:nowrap; color:var(--uamblue);">TRIMESTRE {ROMANO[t["trimestre"]]}</span>'
            f'<span style="font-size:{tipo[2]}px; color:var(--uamgray); margin-top:3px;">'
            f'{_cr(t["creditos"])} cr&eacute;ditos</span></div>{cuerpo}</div>')


def leyenda(color, texto, borde=False):
    bd = "border:1px solid var(--hairline);" if borde else ""
    return (f'<span style="display:inline-flex; align-items:center; gap:9px; margin-right:24px;">'
            f'<span style="width:14px; height:14px; background:{color}; {bd} flex:none;"></span>'
            f'<span style="font-size:12.5px; color:var(--uamgray);">{texto}</span></span>')


def matriz(filas, glosa, base, lic):
    columnas = max(len(t["ueas"]) for t in filas)
    if columnas >= 8:
        tipo, lbl_w = (10, 12.5, 9.5, "6px 7px"), 100
    elif columnas >= 6:
        tipo, lbl_w = (11.5, 14.5, 10, "8px 9px"), 110
    else:
        tipo, lbl_w = (13, 16.5, 11, "10px 12px"), 118
    cuerpo = "".join(renglon_trimestre(t, columnas, tipo, lbl_w, base, lic) for t in filas)
    pie = ('<div style="flex:none; display:flex; align-items:baseline; '
           'justify-content:space-between; gap:24px; padding-top:10px; '
           'border-top:1px solid var(--hairline);"><div>' +
           leyenda("var(--uamlightgray)", "Tronco General", borde=True) +
           leyenda("var(--uamred)", "Tronco Profesional") +
           leyenda("var(--uamblue)", "Tronco de Integraci&oacute;n") +
           '</div><span style="font-size:12px; line-height:16px; color:var(--uamgray); '
           f'text-align:right;">{glosa}</span></div>')
    return cuerpo + pie


# ── lectura en teléfono ──────────────────────────────────────────────────────
NOMBRE_TRONCO = {"general": "Tronco General", "profesional": "Tronco Profesional",
                 "integracion": "Tronco de Integraci&oacute;n"}


def fila(u, base, lic):
    """Una UEA en la lista de teléfono: marca de masa en el color del tronco,
    nombre completo, y debajo el tronco y los créditos en texto, para que el
    tronco no dependa sólo del color."""
    if u["opt"]:
        href = f"{base}#/lic/{lic}/optativas"
    elif u["ruta"]:
        href = base + u["ruta"]
    else:
        href = None
    cuerpo = (f'<span class="mm-marca t-{u["tronco"]}"></span>'
              f'<span class="mm-txt"><span class="mm-nombre">{nombre_html(u["nombre"])}</span>'
              f'<span class="mm-meta">{NOMBRE_TRONCO[u["tronco"]]} &middot; '
              f'{_cr(u["creditos"])} cr&eacute;ditos</span></span>')
    if not href:
        return f'<li><div class="mm-uea">{cuerpo}</div></li>'
    return (f'<li><a class="mm-uea" href="{ent(href)}" target="_top">{cuerpo}'
            f'<span class="mm-ir" aria-hidden="true">&rsaquo;</span></a></li>')


def movil(m, base, cr, total, nota):
    """Malla para pantallas de 720 px o menos, redistribuida para leerse en un
    teléfono y no como una lámina reacomodada. Un resumen con la barra de
    créditos por tronco, un selector fijo de trimestres y una lista por
    trimestre. El tablero inserta este mismo fragmento en su propia página
    (fragmentos.js); la página suelta lo lleva dentro. La impresión nunca lo
    usa: el PDF es siempre el deck."""
    lic = m["clave"]
    seg = "".join(
        f'<span class="mm-seg t-{t}" style="flex:{cr[t]:g}"></span>'
        for t in ("general", "profesional", "integracion") if cr[t])
    ley = "".join(
        f'<li><span class="mm-marca t-{t}"></span><span>{NOMBRE_TRONCO[t]}</span>'
        f'<span class="mm-num">{cr[t]:g}</span></li>'
        for t in ("general", "profesional", "integracion"))
    nav = "".join(
        f'<button type="button" data-t="{t["trimestre"]}" '
        f'aria-label="Trimestre {ROMANO[t["trimestre"]]}">{ROMANO[t["trimestre"]]}</button>'
        for t in m["trimestres"])
    trims = "".join(
        f'<section class="mm-trim" id="mm-{lic}-t{t["trimestre"]}" data-t="{t["trimestre"]}">'
        f'<h2><span class="mm-chip">{ROMANO[t["trimestre"]]}</span>'
        f'<span class="mm-trim-tit">Trimestre {ROMANO[t["trimestre"]]}</span>'
        f'<span class="mm-trim-cr">{t["creditos"]:g} cr&eacute;ditos</span></h2>'
        f'<ol class="mm-lista">{"".join(fila(u, base, lic) for u in t["ueas"])}</ol></section>'
        for t in m["trimestres"])
    nota_html = f'<p class="mm-nota"><strong>Nota.</strong> {nota}</p>' if nota else ""
    return (f'<div class="mm" data-lic="{lic}">'
            f'<div class="mm-resumen"><p class="mm-total"><span>{total:g}</span> '
            f'cr&eacute;ditos en {len(m["trimestres"])} trimestres</p>'
            f'<div class="mm-barra" aria-hidden="true">{seg}</div>'
            f'<ul class="mm-leyenda">{ley}</ul></div>'
            f'<nav class="mm-nav" aria-label="Trimestres">{nav}</nav>'
            f'{trims}{nota_html}'
            f'<p class="mm-fuente">Fuente &middot; {ent(FUENTE[lic])}</p></div>')


# ── deck ─────────────────────────────────────────────────────────────────────
def construir(m, base):
    lic = m["clave"]
    nombre = ent(m["nombre"])
    tag = f"MAPA CURRICULAR &middot; {ent(m['nombre'].upper())}"
    trims = {t["trimestre"]: t for t in m["trimestres"]}
    ultimo = max(trims)
    cr = Counter()
    for t in m["trimestres"]:
        for u in t["ueas"]:
            cr[u["tronco"]] += u["creditos"] or 0
    total = sum(cr.values())
    n_uea = sum(1 for t in m["trimestres"] for u in t["ueas"] if not u["opt"])
    n_opt = sum(1 for t in m["trimestres"] for u in t["ueas"] if u["opt"])
    fin_tg = max(t for t, x in trims.items() if any(u["tronco"] == "general" for u in x["ueas"]))
    ini_ti = min(t for t, x in trims.items() if any(u["tronco"] == "integracion" for u in x["ueas"]))

    nota = NOTA.get(lic, "")
    nota_html = (f'<p style="font-size:15px; line-height:21px; color:var(--uamblue); margin:0 0 8px 0;">'
                 f'<span style="color:var(--uamred); font-weight:700;">Nota.</span> {nota}</p>'
                 if nota else "")
    optativas = (f" y {n_opt} casillas de optativa del Tronco de Integraci&oacute;n"
                 if n_opt else "")
    slides = [f'''
<div style="position:absolute; left:72px; top:56px;">
  <img src="recursos/logo_cover_web.png" style="width:256px;" alt="UAM"></div>
<div style="position:absolute; right:72px; top:64px; text-align:right;">
  <p class="kicker" style="margin:0;">MAPA CURRICULAR</p>
  <p class="kicker muted" style="margin:4px 0 0 0; letter-spacing:0.08em;">
    PLAN DE ESTUDIOS PROPUESTO &middot; 2026</p>
</div>
<div style="position:absolute; left:72px; right:260px; top:176px;">
  <p class="kicker">LICENCIATURA EN</p>
  <h1 class="title" style="font-size:56px; line-height:60px;">{nombre}</h1>
  <p class="subtitle" style="margin-top:16px;">{len(trims)} trimestres, {n_uea} UEA{optativas}</p>
</div>
<div style="position:absolute; right:72px; top:236px;">
  <div style="width:150px; height:150px; border-radius:50%; background:var(--uamred);"></div></div>
<div style="position:absolute; left:72px; right:72px; top:400px;">
  <div class="datorow" style="display:grid; grid-template-columns:repeat(4, 1fr); gap:24px;">
    {dato(f"{cr['general']:g}", "Tronco General")}
    {dato(f"{cr['profesional']:g}", "Tronco Profesional")}
    {dato(f"{cr['integracion']:g}", "Tronco de Integraci&oacute;n")}
    {dato(f"{total:g}", "Cr&eacute;ditos de la malla", accent=True)}
  </div>
</div>
<div style="position:absolute; left:72px; right:72px; bottom:84px;">
  {nota_html}
  <p style="font-size:15px; line-height:21px; color:var(--uamgray); margin:0;">
    Cada recuadro abre el programa de su Unidad de Ense&ntilde;anza-Aprendizaje (UEA)
    en el tablero de modificaciones.</p>
  <p class="mono" style="font-size:12px; line-height:18px; color:var(--uamgray); margin:4px 0 0 0;">
    Fuente &middot; {ent(FUENTE[lic])}</p>
</div>''']

    bloques = [r for r in ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12))
               if any(t in trims for t in r)]
    for rango in bloques:
        filas = [trims[t] for t in rango if t in trims]
        a, b = filas[0]["trimestre"], filas[-1]["trimestre"]
        glosa = []
        if a <= fin_tg <= b:
            glosa.append(f"El Tronco General concluye<br>en el trimestre {ROMANO[fin_tg]}.")
        if a <= ini_ti <= b:
            glosa.append(f"El Tronco de Integraci&oacute;n<br>abre en el trimestre {ROMANO[ini_ti]}.")
        if b == ultimo and not glosa:
            glosa.append(f"La malla concluye<br>en el trimestre {ROMANO[ultimo]}.")
        suma = sum(t["creditos"] for t in filas)
        slides.append(
            header(f"MAPA CURRICULAR &middot; {ent(m['nombre'].upper())}",
                   f"Trimestres {ROMANO[a]} a {ROMANO[b]}",
                   subtitle=f"{suma:g} cr&eacute;ditos en estos {len(filas)} trimestres") +
            '<div class="content"><div style="height:100%; display:flex; '
            'flex-direction:column; gap:6px;">' +
            matriz(filas, glosa[0] if glosa else "", base, lic) +
            '</div></div></div>')

    for s in slides:
        saldo = s.count("<div") - s.count("</div>")
        if saldo:
            raise SystemExit(f"{lic}: <div> sin cerrar ({saldo:+d})")
    total_s = len(slides)
    partes = [f'<section class="slide" id="s{n}">\n{s}\n{footer(tag, n, total_s)}\n</section>'
              for n, s in enumerate(slides, 1)]
    return ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>Mapa curricular &middot; {nombre}</title>\n'
            '<link rel="stylesheet" href="recursos/style.css">\n'
            '<link rel="stylesheet" href="recursos/malla.css">\n'
            '<link rel="stylesheet" href="recursos/movil.css">\n'
            '</head>\n<body>\n'
            f'<div class="mm-pagina"><p class="mm-kicker">Malla curricular &middot; '
            f'plan propuesto</p><h1>{nombre}</h1>'
            f'<p class="mm-ayuda">Toca una UEA para abrir su programa. Las casillas '
            f'de optativa llevan a la lista de optativas.</p>'
            f'<p class="mm-pdf"><a href="{lic}.pdf">Versi&oacute;n en PDF</a></p>'
            + movil(m, base, cr, total, nota) + '</div>\n' +
            "\n".join(partes) +
            '\n<script src="recursos/movil.js"></script>'
            '\n<script src="recursos/malla.js"></script>\n</body>\n</html>')


def render(html, pdf):
    """Chrome imprime desde una copia temporal junto al original, para que
    las rutas relativas de hoja de estilo y logotipos resuelvan igual."""
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=AQUI,
                                     delete=False, encoding="utf-8") as f:
        f.write(html)
        tmp = f.name
    try:
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", "--no-sandbox", "file://" + tmp],
                       check=True, capture_output=True)
    finally:
        os.remove(tmp)


def fragmentos(mallas):
    """La malla de teléfono de las diez licenciaturas, con enlaces relativos a
    la propia página del tablero, para que app.js la dibuje sin iframe."""
    out = {}
    for lic, m in mallas.items():
        cr = Counter()
        for t in m["trimestres"]:
            for u in t["ueas"]:
                cr[u["tronco"]] += u["creditos"] or 0
        out[lic] = movil(m, "", cr, sum(cr.values()), NOTA.get(lic, ""))
    with open(os.path.join(AQUI, "fragmentos.js"), "w", encoding="utf-8") as f:
        f.write("/* Generado por construir_mallas.py. No se edita a mano. */\n"
                "window.MALLAS_MOVIL = " + json.dumps(out, ensure_ascii=False) + ";\n")


def main(claves):
    mallas = json.load(open(os.path.join(AQUI, "mallas.json"), encoding="utf-8"))
    fragmentos(mallas)
    for lic in claves or list(mallas):
        m = mallas[lic]
        with open(os.path.join(AQUI, f"{lic}.html"), "w", encoding="utf-8") as f:
            f.write(construir(m, LOCAL))
        pdf = os.path.join(AQUI, f"{lic}.pdf")
        if os.path.exists(CHROME):
            render(construir(m, PUBLICO), pdf)
        print(f"{lic}  {m['nombre']:48s} {lic}.html  {lic}.pdf")


if __name__ == "__main__":
    main(sys.argv[1:])
