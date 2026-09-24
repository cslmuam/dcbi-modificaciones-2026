# Dashboard de modificaciones curriculares — DCBI 2026

Tablero navegable para comparar el plan de estudios vigente 2020 contra el plan
modificado de las diez licenciaturas de la División de Ciencias Básicas e
Ingeniería, y para consultar el programa de cada Unidad de Enseñanza
Aprendizaje (UEA) entregado en el expediente de julio de 2026.

Abre `index.html` con doble clic. No necesita servidor, ni conexión, ni
dependencias.

## Qué permite hacer

**Portada.** Al abrir sin destino, el tablero recibe con una portada en modo
oscuro: fondo de tinta `#1C1C1C`, emblema en negativo, las cuatro cifras que
resumen el expediente contando hasta su valor, y el Punto de acento sangrando
por la esquina. Un enlace profundo —`#/lic/civ`, `#/uea/…`— la salta y entra
directo a lo que pidió, de modo que un enlace compartido sigue llevando a su
destino.

El paso de un nivel a otro lo hace un plano que barre la pantalla —entra por la
derecha al bajar de nivel, por la izquierda al subir— y descubre la vista nueva
ya pintada debajo. Lleva el color del bloque de encabezado del nivel que llega —rojo
el del panorama, tinta el de la licenciatura, papel la ficha, que no tiene
bloque—, de modo que el barrido deposita la firma del nivel al retirarse y el
escalón se ve aunque dos niveles compartan campo. Dentro de un mismo nivel
—de una UEA a otra, de una búsqueda a su siguiente letra— el plano no aparece:
sólo un asentamiento de 180 ms, para no cobrarle espera a quien navega rápido.
Las cédulas de dato entran escalonadas y los eslabones de las cadenas responden
al cursor. Todo se desactiva con `prefers-reduced-motion`, incluidos los
contadores, que en ese caso muestran su cifra final de inmediato.

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

**Cambio de denominación.** Tres licenciaturas cambian de nombre en la
modificación, y el tablero muestra el nuevo con el anterior al lado. Ingeniería
Eléctrica pasa a Ingeniería Eléctrica y Tecnologías Sostenibles, Ingeniería
Electrónica a Ingeniería en Sistemas Electrónicos y Ciberfísicos, e Ingeniería
Metalúrgica a Ingeniería en Metalurgia y Materiales. Las tres se tomaron del
propio expediente: la pertinencia de Eléctrica describe el tránsito de una
denominación a la otra, la de Electrónica indica la sustitución del nombre, y
el plan de Metalúrgica ya usa el nuevo en su perfil de egreso. Se registra
también el título que se expedirá, que no siempre sigue al nombre del plan —
Eléctrica seguirá titulando Ingeniero o Ingeniera Electricista.

**Cadenas de seriación.** Cada licenciatura compara su plan vigente contra el
modificado en cuatro medidas: cuántas UEA exigen haber aprobado otra, cuántas
seriaciones hay, cuál es la cadena más larga —cuántas UEA hay que ir librando
una tras otra para llegar a la más encadenada— y la profundidad media, que
promedia ese recorrido sobre todas las UEA del plan. Debajo se dibujan las dos
cadenas más largas, eslabón por eslabón.

La cadena más larga se acorta en las diez licenciaturas. En Computación pasa
de nueve UEA encadenadas a cuatro, en Electrónica de nueve a cuatro, en
Ambiental de ocho a cinco. La profundidad media baja en todas.

Se cuentan sólo los prerrequisitos de UEA. Los mínimos de créditos se reportan
aparte, porque no encadenan una UEA con otra: cualquier combinación de UEA
sirve para reunirlos. La distinción importa en Física, cuyo plan modificado
condiciona 23 UEA a un mínimo de créditos y casi ninguna a una UEA
antecedente, de modo que su cadena de 1 es el plan y no un dato faltante. El
tablero lo explica en esa licenciatura con una nota propia.

La seriación se lee de la tabla del plan, que es donde la fija, y la ficha del
programa queda como respaldo. Al principio se leía sólo de la ficha, y por eso
Electrónica y Física aparecían sin seriación: ambas la declaran únicamente en
la tabla.

**Plan de estudios.** Cada licenciatura tiene un botón que abre su plan
propuesto en PDF, con sus tablas y su jerarquía, dentro del propio tablero y
con enlaces para abrirlo aparte o descargarlo. Siete coordinaciones entregaron
PDF y se sirve el suyo tal cual; Eléctrica, Metalúrgica y Química entregaron
sólo Word, así que su PDF se generó a partir de ese archivo con `textutil` y
Chrome —lo que conserva las tablas— y la vista advierte que esa conversión no
es el documento que obra en el expediente. Debajo queda plegado el texto
extraído, sin formato, que sirve para buscar dentro o copiar un párrafo.

Los PDF se preparan con `python3 preparar_planes.py`, que también genera la
imagen de la primera página, la que ve quien abre desde un navegador que no
incrusta PDF.

**Malla curricular.** Cada licenciatura tiene un botón que abre su malla
del plan propuesto, los doce trimestres con los tres troncos por color, dentro
del propio tablero y con enlaces para abrirla aparte, como PDF o descargarla.
Cada recuadro abre el programa de su UEA, y cada casilla de optativa, la lista
de optativas de la licenciatura. Las mallas se generan con el sistema de decks
institucional y viven en `mallas/`, cuyo README documenta de qué archivo del
expediente sale cada una y en qué difiere del plan.

**Árbol de dependencias.** La ficha de cada UEA muestra dos árboles
navegables: lo que hay que aprobar antes de llegar a ella y lo que se abre
después, con el total de UEA implicadas en cada dirección y hasta tres niveles
desplegados. Cuando la UEA continúa del plan vigente, se muestra también el
árbol que tenía entonces, de modo que la comparación es directa. Las UEA del
plan vigente tienen su propia ficha, con su tasa histórica de aprobación y su
árbol de 2020; se llega a ellas desde la tabla de bajas o desde cualquier
eslabón del árbol.

El recorrido marca «ya visto» cuando una rama vuelve sobre sí misma, cosa que
ocurre si una clave tentativa se repite, en vez de entrar en un ciclo.

**Búsqueda.** Por nombre o por clave, sobre las 909 UEA de los diez planes.

Cada vista tiene su propia dirección (`#/lic/civ`, `#/uea/civ/1100211`,
`#/malla/civ`), de modo que un hallazgo concreto se puede enviar por correo como
enlace. Una UEA cuya clave no es única en su licenciatura —«sin clave»,
`1130XXX`, claves tentativas repetidas— se direcciona por su nombre normalizado
con el prefijo `~`.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | La página. Único punto de entrada. |
| `estilo.css` | Identidad institucional. Los valores citan su numeral del manual. |
| `app.js` | Ruteo por hash, campo de color por nivel, filtros, búsqueda y las vistas. |
| `datos.js` | Datos ya procesados, ~3.2 MB. **Generado, no se edita a mano.** |
| `construir_datos.py` | Genera `datos.js` desde las fuentes. |
| `assets/` | Emblema institucional, en positivo y en negativo. |
| `mallas/` | Malla curricular de cada licenciatura en HTML y PDF, con sus generadores. |
| `versionar.py` | Marca cada hoja de estilo y script con la huella de su contenido (`app.js?v=…`), para que un cambio publicado se vea sin esperar a que caduque la caché. Se corre antes de cada publicación. |

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
101 UEA sin programa. Hoy son 16 de 909.

**La descarga no es la causa.** `verificar_descarga_drive.py` compara el árbol
de Drive contra la carpeta local sin bajar contenido: 1,411 archivos de un lado
y 1,411 del otro, coincidencia exacta byte a byte. Tampoco es la indexación:
los archivos están en el corpus.

**La causa es que las claves todavía no identifican a las UEA nuevas.** Las
claves definitivas se asignan en una ronda posterior del proceso, de modo que
las que circulan hoy en el expediente son tentativas. Muchos programas llevan
un marcador del tipo `11XXXXX` en el nombre del archivo, y muchos otros
conservan en su ficha la clave del programa del que se derivaron. Por eso 23
claves aparecen en más de un programa dentro de una misma licenciatura — en
Computación, 1125014 la traen cinco programas de redes—. No es una
inconsistencia que haya que corregir ahora: es el estado del proceso.

Eso provocaba un **defecto grave en este tablero, ya corregido**: al indexar los
programas por clave, los campos de dos UEA distintas se fundían en un solo
registro, de modo que una ficha podía mostrar el objetivo de una UEA y la
bibliografía de otra. Los programas se indexan ahora **por documento**, y la
identidad de cada UEA es su nombre. La clave sirve sólo como referencia al
documento, y el tablero la muestra marcada «por asignar» cuando corresponde.

El emparejamiento con la tabla del plan va en cascada, y empieza por el nombre
del archivo, que resultó más confiable que la clave de la ficha: nombre exacto,
nombre truncado por el extractor, clave única, clave en otra licenciatura para
las UEA compartidas. Cada UEA registra cómo se emparejó, y la vista de
licenciatura lista las UEA compartidas cuyo programa se archivó en otra carrera.

Quedan **16 UEA sin programa**, listadas nominalmente en el tablero, y **70
programas entregados que la tabla del plan no lista**. Unas y otros necesitan
criterio humano, así que el tablero los marca en vez de adivinar.

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

**Cada nivel es un campo con un bloque de encabezado de otro color**, y ese
bloque es la firma del nivel. Es lo primero que se ve al llegar, porque sangra
de borde a borde y arranca pegado al encabezado fijo.

| Nivel | Campo | Bloque de encabezado |
|---|---|---|
| Portada | tinta `#1C1C1C` | el Punto, círculo sangrando por la esquina |
| Panorama | papel `#FFFFFF` | **Plano rojo** con kicker, título, bajada y cédulas |
| Licenciatura | papel `#FFFFFF` | **bloque de tinta** con migaja, título y cédulas |
| UEA y búsqueda | papel `#FFFFFF` | ninguno; el rojo vuelve a ser color de texto |

El acento aparece con el área que cada nivel puede sostener: el círculo y el
plano donde casi no hay texto, la cédula y los chips donde se trabaja, y nada
más que el rótulo donde se lee prosa larga. Dentro de un bloque oscuro el rojo
deja de ser color de texto —`#CD032E` sobre tinta da 2.96:1— y pasa a ser
exclusivamente masa sólida; dentro del Plano rojo la masa se invierte a blanco
pleno con el número en rojo, porque un rojo sobre rojo es nada. Todas las
combinaciones de texto y fondo cumplen WCAG AA, con 5.76:1 en el caso más
ajustado.

Dentro del tablero el campo es siempre papel y lo único que cambia entre las
tres vistas es el bloque —rojo, tinta, ninguno—; la portada queda como el único
campo oscuro. La cortina de transición refuerza el escalón sin añadir
vocabulario, porque llega con el color del bloque del nivel que entra y al
retirarse parece depositarlo. Fuera del bloque todo es papel corriente: la
tabla de las diez licenciaturas y el panel de UEA comparten factura —filete
fino, Punto rojo numerando, chips de masa roja sobre la cifra que sostiene la
comparación— y las barras de crédito llevan sus segmentos canónicos —Tronco
General en rojo, Profesional en la masa oscura, resto en gris—, iguales a los
del carrusel y el deck del mismo proyecto.

El emblema cambia con el campo: sobre papel va el positivo, sobre tinta el
negativo en blanco. Ninguno se recolorea por CSS (numeral 3.2).

**En el teléfono es el mismo tablero, no otra página**: misma URL, mismo código
y mismo sistema de campos y bloques. Lo que cambia es la forma de las tablas y
el tamaño de lo que se toca, con dos umbrales. Por debajo de **980 px** cada
tabla se apila en fichas —una por fila, con el rótulo de cada dato tomado del
atributo `data-r` que escribe `app.js`— y todo lo que se toca crece a 44 px; una
tableta en vertical ya entra aquí, porque sus 768 px no alcanzan ni para las
trece columnas del panorama ni para las siete del panel de UEA, y porque
también se toca con el dedo. Por debajo de **720 px** se recompone la página:
encabezado en dos filas, cédulas en retícula de dos, cadenas de seriación en
vertical con la flecha girada, y los dos árboles de dependencias uno debajo del
otro con la sangría justa para que sigan leyéndose como árbol. Ninguna vista
pide desplazamiento horizontal en ningún ancho, y se comprueba comparando
`scrollWidth` contra `innerWidth`, no a ojo.

**En el teléfono se llega antes a lo que se busca.** Lo que es lectura de
contexto —la distribución de créditos, las cadenas de seriación con sus avisos,
las listas complementarias de la cola, las notas sobre la clave de una UEA—
nace plegado en una sección con su resumen, y se abre tocándolo; en pantalla
ancha ese envoltorio ni siquiera se emite, así que el escritorio es el de
siempre, verificado por comparación de píxeles. Los filtros del panel de UEA
hacen lo mismo, y su resumen lleva la cuenta («Filtrar · 111 de 111 UEA»). Una
sección abierta sigue abierta cuando el tablero se repinta por un filtro o por
el buscador. Y la fila de cédulas se compacta a una sola línea de datos, donde
la cifra sigue siendo la figura y el dato que sostiene el hallazgo conserva su
masa roja.

El efecto, medido a 390 × 844 desde el borde superior del documento:

| Vista | Hasta | Antes | Ahora |
|---|---|---|---|
| `#/lic/civ` | la lista de UEA | 2 978 px | **647 px** |
| `#/lic/civ` | el primer botón | 546 px | **381 px** |
| `#/uea/…` | el programa | 525 px | **364 px** |
| `#/` | la primera licenciatura | 564 px | **472 px** |

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
