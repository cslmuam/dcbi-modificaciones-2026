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
import difflib
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



# ---------------------------------------------- cadenas de seriación
RE_CLAVES = re.compile(r"\b(\d{6,7})\b")
RE_CREDITOS = re.compile(r"(\d{2,3})\s*CR[EÉ]DITOS?", re.I)


def grafo_seriacion(ueas):
    """Aristas antecedente → consecuente dentro de un mismo plan. La columna de
    seriación mezcla claves de UEA, mínimos de créditos y corregistros, así que
    sólo se toman las claves que pertenecen al propio plan."""
    presentes = {u["clave"] for u in ueas}
    aristas, creditos = [], {}
    for u in ueas:
        txt = str(u.get("seriacion") or "")
        if not txt:
            continue
        m = RE_CREDITOS.search(txt)
        if m:
            creditos[u["clave"]] = int(m.group(1))
        for ant in RE_CLAVES.findall(txt):
            if ant in presentes and ant != u["clave"]:
                aristas.append((ant, u["clave"]))
    return sorted(set(aristas)), creditos


def metricas_cadena(nodos, aristas):
    """Profundidad de cada nodo — cuántas UEA hay que librar antes de llegar a
    él— y la cadena más larga. Tolera ciclos, que aparecen cuando una clave
    tentativa se repite."""
    ent = defaultdict(list)
    for a, b in aristas:
        ent[b].append(a)
    prof, camino, estado = {}, {}, {}

    def calcula(n):
        if estado.get(n) == "listo":
            return prof[n]
        if estado.get(n) == "visitando":      # ciclo
            return 0
        estado[n] = "visitando"
        mejor, ruta = 0, [n]
        for a in ent.get(n, []):
            d = calcula(a) + 1
            if d > mejor:
                mejor, ruta = d, camino.get(a, [a]) + [n]
        prof[n], camino[n], estado[n] = mejor, ruta, "listo"
        return mejor

    for n in nodos:
        calcula(n)
    con_prereq = [n for n in nodos if ent.get(n)]
    prof_max = max(prof.values(), default=0)
    cadena = max((camino.get(n, [n]) for n in nodos if prof.get(n) == prof_max),
                 key=len, default=[])
    return {
        "ueas": len(nodos), "aristas": len(aristas),
        "con_prerrequisito": len(con_prereq),
        "pct_con_prerrequisito": round(100 * len(con_prereq) / max(len(nodos), 1), 1),
        "profundidad_max": prof_max,
        "profundidad_media": round(sum(prof.values()) / max(len(nodos), 1), 2),
        "cadena_mas_larga": cadena,
    }



def compatible(a, b):
    """Dos nombres muy parecidos pueden ser UEA distintas. Un laboratorio no es
    su teoría, y un «I» no es un «II», aunque el resto del nombre coincida."""
    lab_a, lab_b = a.startswith("lab"), b.startswith("lab")
    if lab_a != lab_b:
        return False
    rom = lambda t: (re.findall(r"\b(i{1,3}|iv|v)\b$", t) or [""])[0]
    if rom(a) != rom(b):
        return False
    return True


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
            # las horas totales son once semanas por hora semanal; la columna
            # de seriación trae claves de UEA, que caen muy por encima del tope
            esperado_h = 11 * (teoria + practica)
            cand_h = [x for x in nums[2:5] if 10 <= x <= 600]
            horas = (min(cand_h, key=lambda x: abs(x - esperado_h))
                     if cand_h else None)
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

    # ---------------------------------------------------- programas entregados
    # Se indexan por DOCUMENTO, no por clave. Hay 27 claves que más de un
    # programa declara como propia — típicamente porque un programa nuevo se
    # derivó de otro sin corregir la ficha —, de modo que indexar por clave
    # fusionaba en un solo registro los campos de dos UEA distintas.
    docs = {}
    for u in corpus["unidades"]:
        if u.get("tipo") != "programa_uea" or not u.get("ruta"):
            continue
        lic = u.get("clave_lic")
        if not lic:
            continue
        # Varias coordinaciones entregan el mismo programa dos veces, en .docx y
        # en .pdf, y a veces en carpetas hermanas (doc/ y pdf/). El documento se
        # identifica por el nombre del archivo, no por la ruta, para que esas
        # copias no cuenten como programas distintos.
        doc = pathlib.Path(u["ruta"]).name
        doc = re.sub(r"\.(docx|pdf|doc)$", "", doc, flags=re.I)
        doc = re.sub(r"\.(docx|pdf|doc)$", "", doc, flags=re.I)   # ".docx.pdf"
        doc = norma_nombre(doc)
        # Una clave por asignar no es un defecto: es el estado del proceso.
        # La clave definitiva se fija después, así que el expediente circula con
        # marcadores del tipo 11XXXXX y con fichas que conservan la clave del
        # programa del que se derivó el nuevo.
        sin_clave = bool(re.match(r"^\s*1?1[0-9]{0,4}[Xx]{3,}", pathlib.Path(u["ruta"]).name))
        reg = docs.setdefault((lic, doc), {
            "lic": lic, "ruta": u["ruta"], "clave_ficha": u.get("clave_uea"),
            "nombre": "", "campos": {}, "clave_por_asignar": sin_clave,
        })
        nom = re.sub(r"^1?1[0-9Xx]{4,6}\s*[-_ ]\s*", "", (u.get("nombre_uea") or "").strip())
        nom = re.sub(r"^\d{6,7}[_\s-]*", "", nom)
        nom = re.sub(r"[_\s-]*v\d+$", "", nom, flags=re.I).replace("_", " ")
        nom = re.sub(r"\s*[-_ ](OBL|OPT)\.?\s*$", "", nom, flags=re.I).strip(" -_")
        # algunos archivos llevan doble extensión (.docx.pdf) y el extractor
        # dejó la primera dentro del nombre
        nom = re.sub(r"\.(docx|pdf|doc)$", "", nom, flags=re.I).strip()
        if nom and not nom.isdigit():
            reg["nombre"] = nom
        campo = u.get("campo")
        texto = limpia(u.get("texto", ""), u.get("carrera", ""),
                       u.get("clave_uea") or "", u.get("nombre_uea") or "")
        if campo == "ficha":
            reg.update({k: v for k, v in parsea_ficha(u.get("texto", "")).items()
                        if v is not None})
        elif campo in CAMPOS and len(texto) > len(reg["campos"].get(campo, "")):
            reg["campos"][campo] = texto

    # índices de búsqueda, por licenciatura
    por_nombre = defaultdict(dict)      # lic -> nombre normalizado -> documento
    por_clave = defaultdict(lambda: defaultdict(list))   # lic -> clave -> documentos
    for (lic, _), reg in docs.items():
        if not reg["campos"]:
            continue
        n = norma_nombre(reg["nombre"])
        if n and n not in por_nombre[lic]:
            por_nombre[lic][n] = reg
        if reg.get("clave_ficha"):
            por_clave[lic][reg["clave_ficha"]].append(reg)
    # Las claves de los programas nuevos son tentativas: las definitivas se
    # asignan en una ronda posterior del proceso. Por eso una misma clave puede
    # aparecer en varios programas, sin que eso sea una inconsistencia — suele
    # ser la clave del programa del que se derivó el nuevo. Aquí sólo se
    # registra el hecho, para saber de cuántas claves no conviene fiarse.
    repetidas = {}
    for lic, dd in por_clave.items():
        for c, v in dd.items():
            distintos = sorted({r["nombre"] for r in v
                                if norma_nombre(r["nombre"])})
            if len({norma_nombre(n)[:28] for n in distintos}) > 1:
                repetidas[(lic, c)] = distintos

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
    salida = {"licenciaturas": [], "generado": "2026-09-19",
              "claves_repetidas": [{"lic": k[0], "clave": k[1], "programas": v}
                                   for k, v in sorted(repetidas.items())]}
    for lic, nombre in LIC.items():
        plan = tabla_del_plan(corpus, lic)      # UEA que lista el plan propuesto
        # los programas ya viven en docs/por_nombre/por_clave
        vig = v2020.get(lic, {})                # UEA del plan vigente 2020

        for clave, reg in plan.items():
            # El nombre del archivo resultó más confiable que la clave de la
            # ficha, porque esa clave a veces quedó sin actualizar al derivar
            # un programa de otro. Por eso el nombre va primero en la cascada.
            n = norma_nombre(reg["nombre"])
            p, como, de = None, None, None
            if n in por_nombre[lic]:
                p, como = por_nombre[lic][n], "nombre"
            if p is None:
                cands = por_clave[lic].get(clave, [])
                if len(cands) == 1:
                    p, como = cands[0], "clave"
                elif len(cands) > 1:
                    # clave declarada por varios programas: se desempata por nombre
                    mejor = [c for c in cands if norma_nombre(c["nombre"]) == n]
                    if mejor:
                        p, como = mejor[0], "clave"
            if p is None and len(n) >= 12:
                # varios nombres llegaron truncados ("Aprovechamiento y
                # Tratamiento de Re"), así que se admite prefijo inequívoco
                pref = [r for k, r in por_nombre[lic].items()
                        if len(k) >= 12 and compatible(n, k)
                        and (k.startswith(n) or n.startswith(k))]
                if len(pref) == 1:
                    p, como = pref[0], "nombre_truncado"
            if p is None and len(n) >= 10:
                # último recurso: similitud alta dentro de la misma
                # licenciatura, para nombres con erratas ("Tratamieno") o con
                # la clave tentativa pegada al título ("114002X Estructuras")
                mejor, sc_mejor = None, 0.0
                for k, r in por_nombre[lic].items():
                    if not compatible(n, k):
                        continue
                    sc = difflib.SequenceMatcher(None, n, k).ratio()
                    if sc > sc_mejor:
                        mejor, sc_mejor = r, sc
                if sc_mejor >= 0.88:
                    p, como = mejor, "nombre_aproximado"
                    reg["similitud"] = round(sc_mejor, 2)
            if p is None:
                for otra in LIC:
                    if otra == lic:
                        continue
                    if n in por_nombre[otra]:
                        p, como, de = por_nombre[otra][n], "nombre_compartido", LIC[otra]
                        break
                    cands = por_clave[otra].get(clave, [])
                    if len(cands) == 1:
                        p, como, de = cands[0], "clave_compartida", LIC[otra]
                        break
                    if len(n) >= 10:
                        for k, r in por_nombre[otra].items():
                            if (compatible(n, k)
                                    and difflib.SequenceMatcher(None, n, k).ratio() >= 0.95):
                                p, como, de = r, "nombre_compartido", LIC[otra]
                                break
                        if p:
                            break
            reg["clave_por_asignar"] = (not clave.isdigit()) or len(clave) < 7
            reg["programa"] = bool(p and p["campos"])
            reg["emparejamiento"] = como
            if de:
                reg["programa_de"] = de
            if p:
                reg["_doc"] = p
                reg["campos"] = p["campos"]
                reg["ruta"] = p["ruta"]
                if p.get("clave_por_asignar"):
                    reg["programa_sin_clave"] = True
                if p.get("clave_ficha") and p["clave_ficha"] != clave:
                    reg["clave_programa"] = p["clave_ficha"]
                if (lic, p.get("clave_ficha")) in repetidas:
                    reg["clave_repetida"] = True
                for k in ("horas", "seriacion"):
                    if p.get(k) is not None:
                        reg.setdefault(k, p[k])
                for k in ("teoria", "practica", "creditos"):
                    if reg.get(k) is None and p.get(k) is not None:
                        reg[k] = p[k]
            else:
                reg["campos"] = {}

        # programas entregados de UEA que la tabla del plan no listó
        usados = {r["ruta"] for r in
                  [x.get("_doc") for x in plan.values()] if r}
        huerfanos = [{"clave": r.get("clave_ficha") or "sin clave", "nombre": r["nombre"],
                      "tronco": tronco_de_ruta(r["ruta"]), "tipo": r.get("tipo"),
                      "creditos": r.get("creditos"), "teoria": r.get("teoria"),
                      "practica": r.get("practica"), "horas": r.get("horas"),
                      "seriacion": r.get("seriacion"), "campos": r["campos"],
                      "ruta": r["ruta"], "programa": True, "fuera_de_tabla": True}
                     for (l2, _), r in docs.items()
                     if l2 == lic and r["campos"] and r["ruta"] not in usados]

        for reg in plan.values():
            if reg.get("programa"):
                continue
            n = norma_nombre(reg["nombre"])
            mejor, sc = None, 0.0
            for lic2 in list(LIC) + ["tg"]:
                for k, r in por_nombre[lic2].items():
                    v = difflib.SequenceMatcher(None, n, k).ratio()
                    if v > sc:
                        mejor, sc = (r, lic2), v
            if mejor and sc >= 0.45:
                reg["candidato"] = {"nombre": mejor[0]["nombre"],
                                    "lic": LIC.get(mejor[1], "Tronco General"),
                                    "similitud": round(sc, 2)}

        # --- seriación: plan propuesto ---
        lista_p = list(plan.values())
        ar_p, cred_p = grafo_seriacion(lista_p)
        m_p = metricas_cadena([u["clave"] for u in lista_p], ar_p)
        m_p["por_creditos"] = len(cred_p)
        nom_p_clave = {u["clave"]: u["nombre"] for u in lista_p}
        m_p["cadena_nombres"] = [nom_p_clave.get(c, c) for c in m_p.pop("cadena_mas_larga")]
        m_p["sin_columna"] = sum(1 for u in lista_p if not u.get("seriacion")) == len(lista_p) \
            or len(ar_p) + len(cred_p) < 3

        # --- seriación: plan vigente 2020, del grafo curricular ---
        ar_v = sorted({(l["source"], l["target"]) for l in grafo["links"]
                       if l.get("tipo") == "seriacion"
                       and lic in (l.get("planes") or [])
                       and l["source"] in vig and l["target"] in vig})
        m_v = metricas_cadena(list(vig), ar_v)
        m_v["por_creditos"] = None
        m_v["cadena_nombres"] = [vig[c]["nombre"] if c in vig else c
                                 for c in m_v.pop("cadena_mas_larga")]
        m_v["sin_columna"] = False

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
            "seriacion": {"vigente": m_v, "propuesto": m_p},
            "emparejamiento": {
                "clave": sum(1 for r in plan.values() if r.get("emparejamiento") == "clave"),
                "clave_compartida": sum(1 for r in plan.values() if r.get("emparejamiento") == "clave_compartida"),
                "nombre": sum(1 for r in plan.values() if r.get("emparejamiento") == "nombre"),
                "nombre_compartido": sum(1 for r in plan.values() if r.get("emparejamiento") == "nombre_compartido"),
                "clave_repetida": sum(1 for r in plan.values() if r.get("clave_repetida")),
                "clave_por_asignar": sum(1 for r in plan.values() if r.get("clave_por_asignar")),
                "programa_sin_clave": sum(1 for r in plan.values() if r.get("programa_sin_clave")),
                "sin_programa": sum(1 for r in plan.values() if not r.get("programa")),
            },
            "procedencias": [
                {"clave_plan": r["clave"],
                 "clave_programa": (None if str(r.get("clave_programa", "")).startswith("prov:")
                                    else r.get("clave_programa")),
                 "provisional": str(r.get("clave_programa", "")).startswith("prov:"),
                 "nombre": r["nombre"], "programa_de": r.get("programa_de")}
                for r in plan.values()
                if r.get("programa_de")],
            "ueas": sorted([{k: v for k, v in r.items() if k != "_doc"}
                            for r in plan.values()] + huerfanos,
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
              f"{e['nombre_compartido']:3d} · clave repetida {e['clave_repetida']:3d}"
              f" · sin programa {e['sin_programa']:3d}")


if __name__ == "__main__":
    main()
