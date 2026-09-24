# Mallas curriculares del plan propuesto

La malla de cada una de las diez licenciaturas, en HTML navegable y en PDF. El
tablero las abre en la vista `#/malla/<clave>`, que se llega desde el botón
«Ver la malla curricular» de cada licenciatura.

Cada malla es un deck de cuatro diapositivas de 1280×720 con el sistema
`/uam-deck`, el mismo del deck de consulta de Ingeniería Ambiental. La portada
lleva los créditos por tronco y las otras tres láminas llevan cuatro trimestres
cada una. Los troncos se distinguen por masa de color: gris con filete el
General, rojo institucional el Profesional y tinta el de Integración.

**Cada recuadro es un enlace.** El de una UEA abre la ficha de su programa en
el tablero. El de una casilla de optativa abre la lista de optativas de la
licenciatura (`#/lic/<clave>/optativas`).

## Uso

```bash
python3 extraer_mallas.py      # expediente → mallas.json
python3 construir_mallas.py    # mallas.json → <clave>.html y <clave>.pdf
python3 verificar_mallas.py    # recortes, enlaces y PDF
```

`construir_mallas.py civ com` reconstruye sólo esas dos.

## Dos salidas del mismo marcado

- `<clave>.html` enlaza al tablero con rutas relativas (`../index.html#/…`) y
  abre en la ventana principal (`target="_top"`). Funciona dentro del visor
  del tablero, suelto, sin conexión y en GitHub Pages. En pantalla, las láminas
  se escalan al ancho de la ventana con `recursos/malla.js`. Esa escala vive
  bajo `@media screen`, de modo que la impresión no la hereda.
- `<clave>.pdf` se imprime desde una copia con enlaces absolutos a
  <https://cslmuam.github.io/dcbi-modificaciones-2026/>, así que el PDF
  descargado sigue llevando a cada programa.

`recursos/` trae una copia de la hoja de estilo y de los dos logotipos del deck
por licenciatura (`Presentaciones_Licenciatura/`), porque el repositorio
publicado no incluye nada fuera de `Dashboard/`.

## De dónde sale cada malla

| Licenciatura | Fuente en el expediente | Lector |
|---|---|---|
| Ambiental, Química, Física, Eléctrica | `malla_<clave>.json` de `Presentaciones_Modificaciones/` | ya validadas al crédito para los decks de consulta, con sus nombres corregidos a mano |
| Civil | `Mapa curricular_claves_Ing_Civil (julio_2026)V4.xlsx` | renglón de clave y créditos, renglón de nombres |
| Industrial | `Diagrama de seriación Industrial 14 09 26.xlsm`, hoja «Malla Curr Presenta 7» | clave, tronco y créditos por celda |
| Metalúrgica | `Boligrama_Metalurgia y Materiales_4 sept 26.xlsx` | el mismo formato que Industrial |
| Mecánica | `Mapa Curricular_2026 - v35`, en texto | renglón «clave tronco créditos» y renglón de trimestre |
| Computación | Figura 5 de la propuesta de modificaciones, en texto | bloque por trimestre |
| Electrónica | `05_BoligramaSisEloCiber_Ago26.xlsx` | formas del dibujo del boligrama |

El boligrama de Electrónica no tiene texto en sus celdas, y por eso el corpus
del expediente lo lista entre los documentos sin capa de texto. El texto sí
está en las formas del dibujo (`xl/drawings/drawing1.xml`). Cada UEA es un
grupo de tres formas —nombre, clave y créditos— anclado a una celda, y el
trimestre sale del renglón de anclaje, porque cada trimestre ocupa un renglón
alto y el renglón bajo que lo precede.

Cada UEA se empareja con el catálogo del tablero (`../datos.js`) por clave,
cuando la clave es única y el nombre no la contradice, o por nombre. Del
catálogo salen el nombre visible y la ruta de la ficha. Los créditos son los de
la malla, que es lo que suma cada trimestre. Las diez UEA del Tronco General se
reconocen primero por su nombre y llevan el nombre y la clave canónicos.

Los casos que el emparejamiento no resuelve solo van fijos en
`extraer_mallas.py`, con su razón anotada: `CLAVE_ERRATA`, `PROVISIONALES` y
`ALIAS`.

## Cómo enlaza un recuadro a su ficha

La ficha de una UEA se direcciona por su clave (`#/uea/civ/1140024`) cuando la
clave es única en la licenciatura. «sin clave», `1130XXX` y las claves
tentativas repetidas no identifican a una sola UEA, y en ese caso la dirección
lleva el nombre normalizado con el prefijo `~`
(`#/uea/civ/~seminariodeproyectodeintegracion`). `app.js` resuelve las dos
formas con `buscaUEA`, y las tablas del propio tablero usan ahora la misma
regla (`refUEA`). Antes, una fila con clave repetida abría la primera UEA que
tuviera esa clave.

## Lo que la malla trae distinto del plan

La malla se reproduce como la entregó la coordinación, y la portada lo anota.

| Licenciatura | Malla | Plan | Detalle |
|---|---|---|---|
| Electrónica | 465 | 468 | Los recuadros del trimestre XI suman 27 créditos y la columna de totales del boligrama, 30 |
| Metalúrgica | 459 | 462 | La columna de acumulados de la propia hoja cierra en 459. Aparte, la hoja da 6 créditos a Mecánica Vectorial y a Metalurgia Mecánica, que el catálogo del plan da con 9 |
| Química | 473 | 471 | Diferencia ya registrada en el deck de consulta |

Otras particularidades de la fuente, que la malla conserva:

- **Computación** rotula sus cuatro optativas del Tronco de Integración sin
  créditos por casilla y exige «como mínimo 32 créditos» de ellas. Los totales
  de los trimestres XI (33) y XII (34) sólo cuadran con 8 créditos por casilla,
  que es lo que muestra la malla.
- **Electrónica** rotula Cultura de Paz y Género con la clave de Comunicación
  Asertiva (1100211) y Resolución de Problemas con `11500034`. Las dos se
  corrigen por nombre. Su nota exige 45 créditos de optativas y la malla dibuja
  cuatro casillas de 9.
- **Industrial** y **Mecánica** ocupan once trimestres; el duodécimo queda
  vacío en su propia malla.
- **Industrial** rotula Evaluación de Proyectos en Ingeniería como Tronco de
  Integración; su propia tabla de totales la cuenta en el Profesional.
