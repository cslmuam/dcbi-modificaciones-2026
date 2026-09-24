#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprueba las mallas generadas, en tres frentes:

1. Ningún recuadro recorta su texto. Chrome carga cada HTML con un script que
   compara el alto y ancho de contenido de cada celda contra su caja; el
   recorte ocurre dentro de la celda, así que no se ve en el pie ni en el PDF
   extraído a texto.
2. Cada enlace a una UEA resuelve a exactamente una ficha del tablero, con la
   misma regla que app.js (`buscaUEA`).
3. El PDF lleva un enlace por recuadro, a la dirección pública del tablero.
4. El Tronco General trae sus diez UEA, cada una una sola vez. Un
   emparejamiento por parecido confundía Fundamentos de Física y
   Aplicaciones II con la I.

Uso:  python3 verificar_mallas.py
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extraer_mallas import catalogo, norm, sin_marcador  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SONDA = ('<script>addEventListener("load",()=>{document.querySelectorAll(".celda")'
         '.forEach(c=>{if(c.scrollHeight>c.clientHeight+1||c.scrollWidth>c.clientWidth+1)'
         'document.body.insertAdjacentHTML("beforeend","<i class=RECORTE>"+c.textContent+"</i>")});'
         'document.body.insertAdjacentHTML("beforeend","<i class=LISTO></i>")})</script>')

mallas = json.load(open(os.path.join(AQUI, "mallas.json"), encoding="utf-8"))
cat = {l["clave"]: l for l in catalogo()}
fallas = 0
for lic, m in mallas.items():
    html = open(os.path.join(AQUI, f"{lic}.html"), encoding="utf-8").read()
    tmp = os.path.join(AQUI, "_sonda.html")
    open(tmp, "w", encoding="utf-8").write(
        html.replace('<script src="recursos/malla.js"></script>', SONDA))
    dom = subprocess.run([CHROME, "--headless", "--disable-gpu", "--window-size=1280,800",
                          "--virtual-time-budget=3000", "--dump-dom", "file://" + tmp],
                         capture_output=True, text=True).stdout
    os.remove(tmp)
    recortes = re.findall(r'class="RECORTE">([^<]*)', dom)
    if 'class="LISTO"' not in dom:
        recortes = ["(la sonda no terminó)"]

    malas = []
    for t in m["trimestres"]:
        for u in t["ueas"]:
            if not u["ruta"]:
                continue
            k = u["ruta"].rsplit("/", 1)[1]
            hits = [x for x in cat[lic]["ueas"]
                    if (norm(sin_marcador(x["nombre"])) == k[1:] if k.startswith("~")
                        else x["clave"] == k)]
            if len(hits) != 1:
                malas.append(u["nombre"])

    celdas = sum(len(t["ueas"]) for t in m["trimestres"])
    pdf = open(os.path.join(AQUI, f"{lic}.pdf"), "rb").read()
    enlaces = len(re.findall(rb"/URI \(https://cslmuam\.github\.io/dcbi-modificaciones-2026/#/", pdf))

    tg = [u["clave"] for t in m["trimestres"] for u in t["ueas"] if u["tronco"] == "general"]
    tg_ok = len(tg) == 10 and len(set(tg)) == 10

    ok = not recortes and not malas and enlaces == celdas and tg_ok
    fallas += not ok
    print(f"{lic}  {'ok ' if ok else 'MAL'}  {celdas} recuadros, {enlaces} enlaces en el PDF"
          + (f"  · recortes: {recortes}" if recortes else "")
          + (f"  · sin ficha única: {malas}" if malas else "")
          + ("" if tg_ok else f"  · Tronco General: {sorted(tg)}"))
sys.exit(1 if fallas else 0)
