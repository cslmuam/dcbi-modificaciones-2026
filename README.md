# Dashboard de modificaciones curriculares — DCBI 2026

Tablero navegable para comparar el plan de estudios vigente 2020 contra el plan
modificado de las diez licenciaturas de la División de Ciencias Básicas e
Ingeniería, y para consultar el programa de cada Unidad de Enseñanza
Aprendizaje (UEA) entregado en el expediente de julio de 2026.

Abre `index.html` con doble clic. No necesita servidor, ni conexión, ni
dependencias.

## Qué permite hacer

**Panorama.** Las diez licenciaturas en una tabla, con los créditos del Tronco
General y del plan completo antes y después, el número de UEA de cada plan, y
cuántas son nuevas, cuántas continúan con clave distinta y cuántas no tienen
correspondencia.

**Licenciatura.** Distribución de créditos por tronco en barras comparadas, y
la lista completa de UEA del plan propuesto, filtrable por tronco, por tipo de
continuidad y por disponibilidad de programa. Al final, las UEA del plan
vigente que no encuentran correspondencia, con su tasa histórica de aprobación.

**UEA.** Ficha con créditos, horas de teoría y práctica, horas totales y
seriación, más el programa completo — objetivo general, objetivos parciales,
contenido sintético, modalidades de conducción y de evaluación, y bibliografía—
y la ruta del documento fuente.

**Búsqueda.** Por nombre o por clave, sobre las 909 UEA de los diez planes.

Cada vista tiene su propia dirección (`#/lic/civ`, `#/uea/civ/1100211`), de modo
que un hallazgo concreto se puede enviar por correo como enlace.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | La página. Único punto de entrada. |
| `estilo.css` | Identidad institucional. Los valores citan su numeral del manual. |
| `app.js` | Ruteo por hash, filtros, búsqueda y las tres vistas. |
| `datos.js` | Datos ya procesados, ~3.2 MB. **Generado, no se edita a mano.** |
| `construir_datos.py` | Genera `datos.js` desde las fuentes. |
| `assets/` | Emblema institucional. |

Para regenerar los datos, por ejemplo tras una entrega nueva de las
coordinaciones:

```bash
python3 construir_datos.py
```

## Fuentes

- **Expediente julio 2026** — `RAG_ModificacionesJulio2026/data/modificaciones_julio2026.json`,
  9,418 unidades citables extraídas de 1,403 documentos de la carpeta de la
  Secretaría Académica, con actualizaciones de las coordinaciones hasta
  septiembre de 2026.
- **Planes vigentes 2020** — `Metanalisis/RAG_GrafoUEA2020/`, 692 UEA con
  tronco, créditos y tasa de aprobación histórica del periodo 16I a 25O.
- **Distribución de créditos 2020** — `Metanalisis/RAG_PlanesEstudio2020/`.

## Cómo se construyen las cifras, y qué margen tienen

**La lista de UEA de cada plan propuesto** sale de la tabla de la sección 3 del
documento de plan de estudios, no del conjunto de programas entregados. La
distinción importa: una coordinación puede haber entregado el programa de una
UEA que la tabla no lista, o al revés. Las UEA en el primer caso se marcan
«fuera de la tabla», y las del segundo aparecen «sin programa».

**La continuidad de cada UEA** se resuelve primero por clave y, cuando la clave
no coincide, por nombre normalizado. Sin este segundo paso, una renumeración se
leería como si la UEA hubiera desaparecido, que es justo lo que ocurría en una
primera versión de este tablero. La coincidencia por nombre es automática y
aproximada, así que **cualquier caso concreto debe verificarse contra el
documento fuente antes de citarlo** ante un órgano colegiado. La ficha de cada
UEA indica su ruta exacta.

**El tronco** de cada UEA se toma del encabezado que la precede en la tabla del
plan. Las coordinaciones entregaron con estructuras de carpetas y formatos de
tabla distintos —unas con tabulación, otras con barras—, de modo que el parser
tolera ambas formas y marca «sin clasificar» lo que no puede resolver, en vez
de adivinar.

**Las tasas de aprobación** son dato observado del periodo 16I a 25O, no una
predicción.

### Por qué una UEA puede aparecer «sin programa»

Diagnóstico del 19 de septiembre de 2026, a raíz de que el tablero reportaba
101 UEA sin programa.

**La descarga no es la causa.** `verificar_descarga_drive.py` compara el árbol
de Drive contra la carpeta local sin bajar contenido: 1,411 archivos de un lado
y 1,411 del otro, coincidencia exacta byte a byte. Tampoco es la indexación:
los archivos están en el corpus.

La causa real es que **la clave de la tabla del plan y la del programa no
siempre coinciden**, y que varias UEA compartidas tienen un único programa
archivado en la carpeta de otra licenciatura. El emparejamiento se hace ahora
en cascada — clave en la misma licenciatura, clave en cualquier otra, nombre
normalizado, nombre con clave provisional— y eso bajó los casos sin programa de
101 a 29. Cada UEA registra cómo se emparejó, y la vista de licenciatura
lista las 72 discrepancias para que puedan revisarse.

Los patrones encontrados, todos ellos del expediente y no del tablero:

- Archivos con clave provisional en el nombre (`11XXXXX-Plantas
  Potabilizadoras.docx`) cuyo contenido sí trae una clave firme, distinta de la
  que usa el plan.
- Claves de seis dígitos en la tabla del plan de Computación, donde las claves
  de UEA son de siete.
- Un archivo cuyo nombre anuncia una UEA y cuyo contenido es el programa de
  otra: `110019 Álgebra lineal OBL.docx` contiene el programa de Sistemas de
  Ecuaciones Lineales y Matrices, clave 1114056, que es del Tronco General.
- UEA compartidas entre licenciaturas con el programa archivado una sola vez.

**Defecto del propio tablero, ya corregido.** El orden de las columnas de la
tabla del plan cambia de una coordinación a otra: unas ponen los créditos antes
de las horas totales y otras al revés, de modo que Computación mostraba UEA de
«108 créditos». Ahora el crédito se elige por cercanía a la fórmula del
artículo 56 del Reglamento de Estudios Superiores —dos créditos por hora de
teoría más uno por hora de práctica—, en vez de confiar en la posición de la
columna. No queda ninguna UEA con créditos imposibles.

### Limitaciones conocidas

- Cuatro documentos del expediente no tienen capa de texto —los boligramas de
  Electrónica y Mecánica en `.xlsx`, el de Mecánica en `.pdf` y la malla
  curricular de Física—, así que su contenido no aparece aquí.
- Varias UEA nuevas llevan todavía clave provisional en el propio expediente
  (`1100XXX`, `115xxxx`). Se conservan tal cual, sin inventar la definitiva.
- La cifra de «salen» depende de qué tan completa quedó la tabla parseada de
  cada plan. Conviene leerla junto a la columna «UEA 2020», que da la
  proporción.

## Identidad institucional

El tablero es sobrio — filetes casi imperceptibles, mucho aire, un solo acento
de color reservado al dato. Del ensayo neobrutalista quedan dos elementos que
conviven bien con esa sobriedad: el **chip circular rojo** que numera las diez
licenciaturas en el panorama, y la **caja de aviso** con marco firme y etiqueta
de masa sólida, que separa la advertencia metodológica del cuerpo de la tabla
sin competir con ella.

Los valores son los del Acuerdo 06/2012, verificados con `/identidad-uam`.

- Color de la Unidad Azcapotzalco, Pantone 186 C `#CD032E` (numeral 5.3, p. 49).
- Tipografía Verdana para medios electrónicos, con Arial y Tahoma como
  alternativas (numeral 4.1). Helvetica Neue queda reservada al material
  primario impreso.
- Negro puro `#000000` se reserva al emblema (numeral 2.3), así que la tinta de
  cuerpo es `#1C1C1C`.
- El emblema del encabezado no se redibuja, se toma del catálogo en
  `Personal/IdentidadGrafica/`.

## Alcance

Documento de trabajo para la revisión divisional. No es una publicación
institucional ni sustituye al expediente, que es el documento que los órganos
colegiados dictaminan.
