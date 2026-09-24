#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marca cada hoja de estilo y cada script de index.html con la huella de su
contenido (`app.js?v=3f9a1c2e`), y hace lo mismo con los recursos que cita
cada malla suelta (`mallas/<clave>.html`).

GitHub Pages sirve todo con `cache-control: max-age=600` y los navegadores de
teléfono retienen la copia más tiempo, así que un cambio publicado podía no
verse durante un buen rato. Con la huella en la dirección, cualquier archivo
que cambie tiene una dirección nueva y el navegador lo pide de nuevo; los que
no cambian conservan la suya y siguen saliendo de la caché.

Se corre después de regenerar cualquier cosa y antes de publicar:

    python3 versionar.py
"""
import glob
import hashlib
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))
PATRON = re.compile(r'((?:href|src)=")([^"#?]+\.(?:css|js))(?:\?v=[0-9a-f]+)?(")')


def huella(ruta):
    return hashlib.sha1(open(ruta, "rb").read()).hexdigest()[:8]


def versiona(html):
    base = os.path.dirname(html)
    texto = open(html, encoding="utf-8").read()

    def cambia(m):
        ruta = os.path.normpath(os.path.join(base, m.group(2)))
        if m.group(2).startswith(("http:", "https:", "//")) or not os.path.exists(ruta):
            return m.group(0)
        return f"{m.group(1)}{m.group(2)}?v={huella(ruta)}{m.group(3)}"

    nuevo = PATRON.sub(cambia, texto)
    if nuevo != texto:
        open(html, "w", encoding="utf-8").write(nuevo)
    return len(PATRON.findall(nuevo))


if __name__ == "__main__":
    for html in [os.path.join(AQUI, "index.html")] + sorted(
            glob.glob(os.path.join(AQUI, "mallas", "*.html"))):
        print(f"{os.path.relpath(html, AQUI):20s} {versiona(html)} recursos marcados")
