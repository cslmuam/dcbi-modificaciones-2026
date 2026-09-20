#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera `datos.js` para el dashboard de modificaciones curriculares DCBI 2026.

Fuentes, todas locales y ya verificadas en este repositorio.
  · Expediente julio 2026 — RAG_ModificacionesJulio2026/data/modificaciones_julio2026.json
    (9,418 unidades citables extraídas de 1,403 documentos de la carpeta de la
    Secretaría Académica).
  · Planes vigentes 2020 — Metanalisis/RAG_GrafoUEA2020/data/grafo_conocimiento_2020.json
    (692 UEA con tronco, créditos y datos históricos 16I-25O).
  · Distribución de créditos 2020 — Metanalisis/RAG_PlanesEstudio2020/data/planes_2020.json

Salida `datos.js`, un único archivo con `const DATOS = {...}` para que el
dashboard abra desde el sistema de archivos sin servidor (un `fetch` a
`file://` lo bloquea el navegador).

Uso:  python3 construir_datos.py
"""
import json
import pathlib
import re
import unicodedata
from collections import defaultdict

AQUI = pathlib.Path(__file__).parent
RAIZ = AQUI.parent
CASA = pathlib.Path.home()

F_2026 = RAIZ / "RAG_ModificacionesJulio2026/data/modificaciones_julio2026.json"
F_GRAFO = CASA / "Claude_Projects/Admin_duties/Metanalisis/RAG_GrafoUEA2020/data/grafo_conocimiento_2020.json"
F_PLAN20 = CASA / "Claude_Projects/Admin_duties/Metanalisis/RAG_PlanesEstudio2020/data/planes_2020.json"

LIC = {
    "amb": "Ingeniería Ambiental",
    "civ": "Ingeniería Civil",
    "com": "Ingeniería en Computación",
    "ele": "Ingeniería Eléctrica",
    "elo": "Ingeniería Electrónica",
    "fis": "Ingeniería Física",
    "ind": "Ingeniería Industrial",
    "mec": "Ingeniería Mecánica",
    "met": "Ingeniería Metalúrgica",
    "qui": "Ingeniería Química",
}

CAMPOS = ["objetivo", "objetivos_parciales", "contenido", "conduccion",
          "evaluacion", "bibliografia"]


def sin_acentos(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()


def tronco_de_ruta(ruta):
    """Cada coordinación entregó con su propia estructura de carpetas, así que
    el tronco se infiere de la ruta y se normaliza a cuatro valores."""
    r = sin_acentos(ruta)
    if "tronco general" in r or "tronco basico general" in r:
        return "general"
    if "integracion" in r:
        return "integracion"
    if "profesional" in r or "ps obligatorios" in r or "ps optativos" in r:
        return "profesional"
    if "optativ" in r:
        return "optativa"
    return "sin_clasificar"


# --------------------------------------------------------------- ficha
RE_CLAVE = re.compile(r"CLAVE\s*\n?\s*(\d{6,7})")
RE_CRED = re.compile(r"CREDITOS?\s*\n?\s*([\d.]+)", re.I)
RE_TEO = re.compile(r"HORAS\s*\n?\s*TEOR[IÍ]A\s*\n?\s*([\d.]+)", re.I)
RE_PRA = re.compile(r"HORAS\s*PR[AÁ]CTICA\s*\n?\s*([\d.]+)", re.I)
RE_TOT = re.compile(r"HORAS\s*TOTALES\s*\n?\s*([\d.]+)", re.I)
RE_SER = re.compile(r"SERIACI[OÓ]N\s*\n\s*([^\n|]+)")
RE_OPT = re.compile(r"OPT\.?\s*/\s*OBL\.?\s*\n?\s*(OBL|OPT)", re.I)


def parsea_ficha(texto):
    def num(rx):
        m = rx.search(texto)
        return float(m.group(1)) if m else None
    ser = RE_SER.search(texto)
    ser = ser.group(1).strip(" .|") if ser else None
    if ser and (sin_acentos(ser).startswith("no tiene") or len(ser) < 4
                or sin_acentos(ser).startswith("unidad")):
        ser = None
    opt = RE_OPT.search(texto)
    return {
        "creditos": num(RE_CRED), "teoria": num(RE_TEO),
        "practica": num(RE_PRA), "horas": num(RE_TOT),
        "seriacion": ser, "tipo": (opt.group(1).upper() if opt else None),
    }


def limpia(texto, prefijo_lic, clave, nombre):
    """Quita el prefijo de contexto que el corpus antepone a cada unidad."""
    t = texto.strip()
    for pref in (f"{prefijo_lic}. UEA {clave} {nombre}.", f"{prefijo_lic}."):
        if t.startswith(pref):
            t = t[len(pref):].lstrip()
    t = re.sub(r"^[^.]{0,80}\((?:clave|objetivo)[^)]*\)\.\s*", "", t, flags=re.I)
    t = re.sub(r"^(objetivos?\s+(general|parciales)|contenido\s+sint[eé]tico|"
               r"modalidades\s+de\s+(conducci[oó]n|evaluaci[oó]n)|bibliograf[ií]a)"
               r"[\s.:—-]*", "", t, flags=re.I)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()



def norma_nombre(n):
    """Nombre comparable entre planes — sin acentos, sin puntuación ni ruido."""
    t = sin_acentos(n or "")
    t = re.sub(r"\blaboratorio\b", "lab", t)
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    t = re.sub(r"\b(de|del|la|el|los|las|y|en|para|a)\b", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ------------------------------------------------- tabla del plan propuesto
RE_FRAG = re.compile(r"fragmento\s+(\d+)\s*/", re.I)
# las coordinaciones entregaron la tabla con tabulación o con barras
RE_FILA = re.compile(
    r"(?P<clave>\d{6,7})\s*\|?\s*"
    r"(?P<nombre>[A-Za-zÁÉÍÓÚÑáéíóúñ][^|\n]{3,70}?)\s*\|?\s*"
    r"(?P<tipo>OBL|OPT)\.?(?![A-Za-z])\s*\|?\s*(?P<resto>[^\n]*)")
RE_TRONCO = re.compile(
    r"TRONCO\s+(GENERAL|B[AÁ]SICO\s+PROFESIONAL|PROFESIONAL|DE\s+INTEGRACI[OÓ]N|"
    r"INTER\s*Y\s*MULTIDISCIPLINAR|DE\s+NIVELACI[OÓ]N[^\n]*)", re.I)


def normaliza_tronco(txt):
    t = sin_acentos(txt)
    if "general" in t:
        return "general"
    if "integracion" in t or "multidisciplinar" in t:
        return "integracion"
    if "profesional" in t:
        return "profesional"
    if "nivelacion" in t:
        return "nivelacion"
    return "sin_clasificar"


def tabla_del_plan(corpus, lic):
    """Lee la sección 3 del plan propuesto y devuelve las UEA que lista, con su
    tronco tomado del encabezado que las precede. Es la fuente correcta para
    comparar planes — el corpus de programas sólo trae los entregados."""
    frags = [u for u in corpus["unidades"]
             if u.get("tipo") == "plan_estudios" and u.get("clave_lic") == lic]
    # un mismo plan puede venir en .docx y .pdf; se toma el documento más largo
    por_doc = defaultdict(list)
    for u in frags:
        por_doc[u.get("documento", "")].append(u)
    if not por_doc:
        return {}
    doc = max(por_doc.values(), key=lambda v: sum(len(x.get("texto", "")) for x in v))

    def orden(u):
        m = RE_FRAG.search(u.get("nombre", ""))
        return int(m.group(1)) if m else 0
    texto = "\n".join(u.get("texto", "") for u in sorted(doc, key=orden))

    filas, tronco = {}, "sin_clasificar"
    for linea in texto.split("\n"):
        th = RE_TRONCO.search(linea)
        if th:
            tronco = normaliza_tronco(th.group(1))
        m = RE_FILA.search(linea)
        if not m:
            continue
        clave = m.group("clave")
        nombre = re.sub(r"\s{2,}", " ", m.group("nombre")).strip(" .|")
        if len(nombre) < 4 or nombre.isdigit():
            continue
        nums = [float(x) for x in
                re.findall(r"\d+(?:\.\d+)?", m.group("resto").replace("|", " "))]
        reg = filas.get(clave, {})
        reg.update({"clave": clave, "nombre": nombre,
                    "tipo": m.group("tipo").upper(), "tronco": tronco})
        if len(nums) >= 3:
            teoria, practica = nums[0], nums[1]
            # El orden de las columnas cambia de una coordinación a otra: unas
            # ponen créditos antes que horas totales y otras al revés. En vez de
            # fijar una posición, se elige el candidato que más se acerca a la
            # fórmula del artículo 56 del RES — dos créditos por hora de teoría
            # más uno por hora de práctica.
            esperado = 2 * teoria + practica
            cand = [x for x in nums[2:5] if 0 < x <= 30]
            creditos = min(cand, key=lambda x: abs(x - esperado)) if cand else None
            horas = max([x for x in nums[2:5] if x > 30], default=None)
            reg.setdefault("teoria", teoria)
            reg.setdefault("practica", practica)
            if creditos is not None:
                reg.setdefault("creditos", creditos)
            if horas is not None:
                reg.setdefault("horas", horas)
        filas[clave] = reg
    return filas


def main():
    corpus = json.loads(F_2026.read_text())
    grafo = json.loads(F_GRAFO.read_text())
    planes20 = json.loads(F_PLAN20.read_text())

    # ---------------------------------------------------- UEA propuestas
    ueas = defaultdict(dict)          # lic -> clave -> registro
    for u in corpus["unidades"]:
        if u.get("tipo") != "programa_uea":
            continue
        lic, clave = u.get("clave_lic"), u.get("clave_uea")
        if not lic:
            continue
        if not clave:
            # el archivo trae clave provisional (11XXXXX-Nombre.docx), así que
            # el extractor no pudo leerla; se indexa por nombre para no perderlo
            base = re.sub(r"^1?1[0-9X]{4,6}\s*[-_ ]\s*", "",
                          (u.get("nombre_uea") or "").strip(), flags=re.I)
            if not base:
                continue
            clave = "prov:" + norma_nombre(base)[:60]
        reg = ueas[lic].setdefault(clave, {
            "clave": clave, "nombre": u.get("nombre_uea") or "",
            "tronco": tronco_de_ruta(u.get("ruta", "")),
            "ruta": u.get("ruta", ""), "campos": {},
        })
        # el nombre del archivo a veces arrastra sufijos de versión
        nom = (u.get("nombre_uea") or "").strip()
        nom = re.sub(r"^1?1[0-9X]{4,6}\s*[-_ ]\s*", "", nom, flags=re.I)
        nom = re.sub(r"^\d{6,7}[_\s-]*", "", nom)
        nom = re.sub(r"[_\s-]*v\d+$", "", nom, flags=re.I).replace("_", " ").strip()
        # los archivos rematan con OBL/OPT y con sufijos de versión
        nom = re.sub(r"\s*[-_ ](OBL|OPT)\.?\s*$", "", nom, flags=re.I).strip(" -_")
        # se prefiere siempre el nombre ya limpio, nunca el más largo: el largo
        # es justo el que conserva la clave pegada al título
        if nom and not nom.isdigit():
            reg["nombre"] = nom
        if reg["tronco"] == "sin_clasificar":
            reg["tronco"] = tronco_de_ruta(u.get("ruta", ""))
        campo = u.get("campo")
        texto = limpia(u.get("texto", ""), u.get("carrera", ""),
                       clave, u.get("nombre_uea") or "")
        if campo == "ficha":
            reg.update(parsea_ficha(u.get("texto", "")))
        elif campo in CAMPOS:
            # se conserva la versión más extensa entre .docx y .pdf
            if len(texto) > len(reg["campos"].get(campo, "")):
                reg["campos"][campo] = texto

    # ---------------------------------------------------- UEA vigentes 2020
    v2020 = defaultdict(dict)
    for n in grafo["nodes"]:
        for lic in (n.get("planes") or []):
            if lic in LIC:
                v2020[lic][n["id"]] = {
                    "clave": n["id"], "nombre": n.get("nombre", ""),
                    "creditos": n.get("creditos"), "tronco": n.get("tronco"),
                    "aprobacion": n.get("tasa_aprobacion"),
                    "intentos": n.get("Esperanza_Intentos"),
                }

    # ---------------------------------------------------- créditos por tronco
    cred20 = {}
    for u in planes20["unidades"]:
        if u.get("tipo") != "distribucion_creditos":
            continue
        lic = u["id"].split(":")[1]
        t = re.sub(r"\.{2,}", " ", u.get("texto", ""))
        def busca(rx):
            m = re.search(rx, t, re.I)
            return int(m.group(1)) if m else None
        cred20[lic] = {
            "general": busca(r"TRONCO GENERAL[\s.]*(\d{2,3})"),
            "nivelacion": busca(r"NIVELACI[OÓ]N ACAD[EÉ]MICA[\s.]*(\d{1,3})"),
            "profesional": busca(r"TRONCO B[AÁ]SICO PROFESIONAL[\s.]*(\d{2,3})"),
            "total": busca(r"TOTAL DEL PLAN[\s.]*(\d{3})"),
        }

    cred26 = {}
    for u in corpus["unidades"]:
        if u.get("tipo") != "plan_estudios":
            continue
        lic = u.get("clave_lic")
        if lic not in LIC:
            continue
        t = re.sub(r"[ \t]{2,}", " | ", u.get("texto", ""))
        d = cred26.setdefault(lic, {})
        for k, rx in (("general", r"Tronco [Gg]eneral[\s|.…]*(\d{2,3})"),
                      ("profesional", r"Tronco (?:b[aá]sico )?profesional[\s|.…]*(\d{2,3})"),
                      ("total", r"TOTAL DEL PLAN[\s|.…]*(\d{3})|Total del plan de estudios[\s|.…]*(\d{3})")):
            m = re.search(rx, t, re.I)
            if m and not d.get(k):
                d[k] = int(next(g for g in m.groups() if g))

    # ---------------------------------------------------- ensamblado
    salida = {"licenciaturas": [], "generado": "2026-09-19"}
    for lic, nombre in LIC.items():
        plan = tabla_del_plan(corpus, lic)      # UEA que lista el plan propuesto
        prog = ueas.get(lic, {})                # programas entregados
        vig = v2020.get(lic, {})                # UEA del plan vigente 2020

        for clave, reg in plan.items():
            # Emparejamiento en cascada. La clave de la tabla del plan y la del
            # programa no siempre coinciden — hay claves provisionales
            # (11XXXXX), claves de seis dígitos y renumeraciones — y varias UEA
            # compartidas tienen un único programa, archivado en la carpeta de
            # otra licenciatura. Sin la cascada, 88 de 101 UEA se reportaban
            # "sin programa" teniendo su programa en el expediente.
            p = prog.get(clave)
            reg["emparejamiento"] = "clave" if p else None
            if not p:
                for otra_lic, otras in ueas.items():
                    if clave in otras and otras[clave]["campos"]:
                        p = otras[clave]
                        reg["emparejamiento"] = "clave_compartida"
                        reg["programa_de"] = LIC.get(otra_lic, otra_lic)
                        break
            if not p:
                n = norma_nombre(reg["nombre"])
                for cand in prog.values():
                    if cand["campos"] and norma_nombre(cand["nombre"]) == n:
                        p = cand
                        reg["emparejamiento"] = "nombre"
                        reg["clave_programa"] = cand["clave"]
                        break
            if not p:
                n = norma_nombre(reg["nombre"])
                cand = prog.get("prov:" + n[:60])
                if cand and cand["campos"]:
                    p = cand
                    reg["emparejamiento"] = "nombre_clave_provisional"
            if not p:
                n = norma_nombre(reg["nombre"])
                for otra_lic, otras in ueas.items():
                    if otra_lic == lic:
                        continue
                    for cand in otras.values():
                        if cand["campos"] and norma_nombre(cand["nombre"]) == n:
                            p, reg["emparejamiento"] = cand, "nombre_compartido"
                            reg["programa_de"] = LIC.get(otra_lic, otra_lic)
                            reg["clave_programa"] = cand["clave"]
                            break
                    if p:
                        break
            reg["programa"] = bool(p and p["campos"])
            if p:
                reg["campos"] = p["campos"]
                reg["ruta"] = p["ruta"]
                for k in ("horas", "seriacion"):
                    if p.get(k) is not None:
                        reg.setdefault(k, p[k])
                for k in ("teoria", "practica", "creditos"):
                    if reg.get(k) is None and p.get(k) is not None:
                        reg[k] = p[k]
            else:
                reg["campos"] = {}
        # programas entregados de UEA que la tabla del plan no listó
        huerfanos = [dict(r, programa=True, tipo=r.get("tipo") or "",
                          tronco=r["tronco"], fuera_de_tabla=True)
                     for c, r in prog.items() if c not in plan]

        claves_p, claves_v = set(plan), set(vig)
        provisional = {c for c in claves_p if not c.isdigit()}
        # Una UEA puede continuar con clave nueva, así que la coincidencia por
        # clave se complementa con la del nombre normalizado. Sin esto, una
        # renumeración se leería como si la UEA desapareciera.
        nom_v = defaultdict(list)
        for c, r in vig.items():
            nom_v[norma_nombre(r["nombre"])].append(c)
        nom_p = defaultdict(list)
        for c, r in plan.items():
            nom_p[norma_nombre(r["nombre"])].append(c)
        for c, r in plan.items():
            if c in claves_v:
                r["continuidad"] = "misma_clave"
            elif nom_v.get(norma_nombre(r["nombre"])):
                r["continuidad"] = "otra_clave"
                r["clave_2020"] = nom_v[norma_nombre(r["nombre"])][0]
            else:
                r["continuidad"] = "nueva"
        renumeradas = sorted(c for c, r in plan.items() if r.get("continuidad") == "otra_clave")
        nuevas = sorted(c for c, r in plan.items()
                        if r.get("continuidad") == "nueva" and c not in provisional)
        siguen = sorted(claves_p & claves_v)
        salen = sorted(c for c, r in vig.items()
                       if c not in claves_p and not nom_p.get(norma_nombre(r["nombre"])))
        salida["licenciaturas"].append({
            "clave": lic, "nombre": nombre,
            "creditos": {"vigente": cred20.get(lic, {}), "propuesto": cred26.get(lic, {})},
            "conteo": {"plan": len(claves_p), "vigentes": len(claves_v),
                       "nuevas": len(nuevas), "salen": len(salen),
                       "siguen": len(siguen), "renumeradas": len(renumeradas),
                       "provisionales": len(provisional),
                       "con_programa": sum(1 for r in plan.values() if r["programa"]),
                       "huerfanos": len(huerfanos)},
            "diff": {"nuevas": nuevas, "salen": [vig[c] for c in salen],
                     "siguen": siguen, "renumeradas": renumeradas,
                     "provisionales": sorted(provisional)},
            "emparejamiento": {
                "clave": sum(1 for r in plan.values() if r.get("emparejamiento") == "clave"),
                "clave_compartida": sum(1 for r in plan.values() if r.get("emparejamiento") == "clave_compartida"),
                "nombre": sum(1 for r in plan.values() if r.get("emparejamiento") == "nombre"),
                "nombre_compartido": sum(1 for r in plan.values() if r.get("emparejamiento") == "nombre_compartido"),
                "clave_provisional": sum(1 for r in plan.values() if r.get("emparejamiento") == "nombre_clave_provisional"),
                "sin_programa": sum(1 for r in plan.values() if not r.get("programa")),
            },
            "discrepancias": [
                {"clave_plan": r["clave"],
                 "clave_programa": (None if str(r.get("clave_programa", "")).startswith("prov:")
                                    else r.get("clave_programa")),
                 "provisional": str(r.get("clave_programa", "")).startswith("prov:"),
                 "nombre": r["nombre"], "programa_de": r.get("programa_de")}
                for r in plan.values()
                if r.get("emparejamiento") in ("nombre", "nombre_compartido",
                                               "clave_compartida", "nombre_clave_provisional")],
            "ueas": sorted(list(plan.values()) + huerfanos,
                           key=lambda r: (r.get("tronco") or "", r.get("nombre") or "")),
            "vigentes": sorted(vig.values(), key=lambda r: r["nombre"]),
        })

    js = "// generado por construir_datos.py — no editar a mano\nconst DATOS = "
    js += json.dumps(salida, ensure_ascii=False, separators=(",", ":"))
    js += ";\n"
    (AQUI / "datos.js").write_text(js, encoding="utf-8")

    tot = sum(l["conteo"]["plan"] for l in salida["licenciaturas"])
    print(f"datos.js  ·  {len(js)/1e6:.2f} MB  ·  {tot} UEA en los diez planes propuestos")
    for l in salida["licenciaturas"]:
        c = l["conteo"]
        sc = sum(1 for u in l["ueas"] if u.get("tronco") == "sin_clasificar")
        print(f"  {l['clave']}  {l['nombre'][:26]:28s} plan {c['plan']:3d}"
              f"  vig {c['vigentes']:3d}  nuevas {c['nuevas']:3d}  salen {c['salen']:3d}"
              f"  siguen {c['siguen']:3d}  renum {c['renumeradas']:3d}"
              f"  c/prog {c['con_programa']:3d}"
              f"  fuera de tabla {c['huerfanos']:3d}  sin tronco {sc:3d}")
        e = l["emparejamiento"]
        print(f"        emparejado por clave {e['clave']:3d} · clave compartida "
              f"{e['clave_compartida']:3d} · nombre {e['nombre']:3d} · nombre compartido "
              f"{e['nombre_compartido']:3d} · clave provisional {e['clave_provisional']:3d}"
              f" · sin programa {e['sin_programa']:3d}")


if __name__ == "__main__":
    main()
