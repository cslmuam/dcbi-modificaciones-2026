#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deja en `planes/` el plan de estudios propuesto de cada licenciatura, en PDF.

Siete coordinaciones entregaron PDF y se copia el suyo tal cual. Las otras tres
—Eléctrica, Metalúrgica y Química— entregaron sólo .docx, así que aquí se
convierte con `textutil` y Chrome, que conserva las tablas del documento. Esa
conversión no es el archivo que entregó la coordinación y el tablero lo dice.

Uso:  python3 preparar_planes.py
"""
import collections
import json
import pathlib
import shutil
import subprocess
import tempfile

AQUI = pathlib.Path(__file__).parent
RAIZ = AQUI.parent
CORPUS = RAIZ / "RAG_ModificacionesJulio2026/data/modificaciones_julio2026.json"
EXPEDIENTE = RAIZ / "Modificaciones Licenciaturas Julio 2026"
DESTINO = AQUI / "planes"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

LIC = ["amb", "civ", "com", "ele", "elo", "fis", "ind", "mec", "met", "qui"]
NOMBRE = {"ele": "Ingeniería Eléctrica y Tecnologías Sostenibles",
          "met": "Ingeniería en Metalurgia y Materiales",
          "qui": "Ingeniería Química"}


def documento_del_plan(corpus, lic):
    """La ruta del plan de estudios de esa licenciatura, en PDF si lo hay y en
    .docx si no. Se elige el documento más extenso, que es el criterio que ya
    usa el resto del tablero cuando una coordinación entregó varias versiones."""
    us = [u for u in corpus["unidades"]
          if u.get("tipo") == "plan_estudios" and u.get("clave_lic") == lic
          and u.get("ruta")]
    largo = collections.Counter()
    for u in us:
        largo[u["ruta"]] += len(u.get("texto", ""))
    pdfs = {r: n for r, n in largo.items() if r.lower().endswith(".pdf")}
    if pdfs:
        return max(pdfs, key=pdfs.get), True
    return (max(largo, key=largo.get), False) if largo else (None, False)


def docx_a_pdf(origen, destino, titulo):
    """textutil para leer el .docx y Chrome para imprimirlo. Preserva las tablas,
    que es justo lo que se pierde al extraer sólo el texto."""
    with tempfile.TemporaryDirectory() as tmp:
        html = pathlib.Path(tmp) / "plan.html"
        subprocess.run(["textutil", "-convert", "html", str(origen),
                        "-output", str(html)], check=True, capture_output=True)
        # sin esto el visor de PDF muestra «plan.html» como título del documento
        t = html.read_text(encoding="utf-8", errors="ignore")
        html.write_text(t.replace("<title></title>", f"<title>{titulo}</title>", 1),
                        encoding="utf-8")
        subprocess.run([CHROME, "--headless", "--disable-gpu",
                        "--no-pdf-header-footer", f"--print-to-pdf={destino}",
                        html.as_uri()], check=True, capture_output=True)


def main():
    corpus = json.loads(CORPUS.read_text())
    DESTINO.mkdir(exist_ok=True)
    indice = {}
    for lic in LIC:
        ruta, es_pdf = documento_del_plan(corpus, lic)
        if not ruta:
            print(f"{lic}  sin documento de plan")
            continue
        origen = EXPEDIENTE / ruta
        salida = DESTINO / f"{lic}.pdf"
        if es_pdf:
            shutil.copy2(origen, salida)
        else:
            docx_a_pdf(origen, salida,
                       f"Plan de estudios propuesto · {NOMBRE[lic]}")
        # imagen de la primera página: es lo que ve quien abre desde un
        # navegador que no incrusta PDF, iOS entre ellos
        subprocess.run(["pdftoppm", "-png", "-r", "70", "-f", "1", "-l", "1",
                        str(salida), str(DESTINO / f"{lic}-p1")],
                       check=True, capture_output=True)
        for f in DESTINO.glob(f"{lic}-p1-*.png"):
            f.rename(DESTINO / f"{lic}-p1.png")
        indice[lic] = {"archivo": f"planes/{lic}.pdf", "original": ruta,
                       "convertido": not es_pdf,
                       "kb": round(salida.stat().st_size / 1024),
                       "portada": f"planes/{lic}-p1.png"}
        print(f"{lic}  {indice[lic]['kb']:5d} kB  "
              f"{'convertido del .docx' if not es_pdf else 'PDF entregado'}")
    (DESTINO / "indice.json").write_text(
        json.dumps(indice, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    total = sum(v["kb"] for v in indice.values())
    print(f"\n{len(indice)} planes · {total/1024:.1f} MB en {DESTINO}")


if __name__ == "__main__":
    main()
