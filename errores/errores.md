# Errores

Errores que cometí o que encontré en los datos: cómo se manifestaron, cómo
los detecté y qué hice. Ordenados por fecha.

---

## Agosto — Ejercicio de fundamentos (clase 3)

**Qué pasó.** En el ejercicio de opción múltiple
(`clases/clase03/clase03_ejercicio_fundamentos.pdf`) dejé la pregunta 2 sin
responder y elegí mal la 4, la 5 y la 11.

**Cómo lo detecté.** Revisando el repositorio el 03/11, con lo visto en el
resto del curso. El PDF queda como lo entregué.

**Lo correcto, y por qué.**

- **2.** En R, `1` es un vector numérico de longitud 1: R no tiene números
  sueltos.
- **4.** En Python, `[1, 2, 3] * 2` da `[1, 2, 3, 1, 2, 3]`. Una lista
  multiplicada por un entero se repite; `[2, 4, 6]` sería el resultado con un
  vector de R o un arreglo de NumPy.
- **5.** `edad = "35"` guarda el **texto** "35": las comillas lo hacen texto.
- **11.** La ruta `C:/Users/jodavyt/datos.csv` **falla** en otra computadora,
  porque esa carpeta no existe ahí. Es el mismo error que cometí yo en la
  clase 10 (ver más abajo).

---

## 03/09 — Ruta de la plantilla (clase 5)

**Qué pasó.** La plantilla de la clase leía el archivo de
`clases/clase4/`, una carpeta que existe en el repositorio de la profesora
pero no en el mío.

**Qué hice.** Agregué una segunda línea con la ruta a mi carpeta `Data/`, y
quedaron las dos en el script: la primera no servía y la segunda la pisaba. El 03/11 dejé una sola, relativa a la raíz del
repositorio.

---

## 17/09 — VS Code no dejaba correr el script (clase 7)

**Cómo se manifestó.** No se ejecutaba nada.

**Causa.** VS Code abre las carpetas nuevas en modo restringido.

**Qué hice.** Indicar que confío en la carpeta (Trust). Ver
`recetas/correr_scripts_en_vscode.md`.

---

## 17/09 — El script de la clase pedía archivos que no tenía (clase 7)

**Qué pasó.** `carga_y_transformacion.py` lee tres archivos de enero a abril
(ozono, PM2.5 y conteo vehicular). Yo tenía solo el de ozono.

**Qué hice.** Una versión adaptada que trabaja solo con el ozono y deja
indicadas las partes que faltan:
`clases/clase07/clase07_carga_y_transformacion_ozono.py`.

---

## 17/09 — «ColÃ³n» en vez de «Colón» (clase 7)

**Cómo se manifiesta.** Leído como lo leía el script de la clase, los nombres
de las estaciones salen con símbolos raros.

**Causa.** El script de la clase leía el archivo con `encoding="latin1"`,
pero el archivo está en UTF-8. Cada letra con tilde se partía en dos
caracteres.

**Qué hice.** Leerlo con `encoding="utf-8"`. El diccionario de reemplazos que
traía el script ya no hace falta. Ver `recetas/leer_un_csv_dificil.md`.

---

## 17/09 y 22/09 — El script se quedaba frenado

**Cómo se manifestó.** Al correr el script entero se abría una ventana con
un gráfico y no pasaba nada más.

**Causa.** `plt.show()` frena el script hasta que se cierra la ventana.

**Qué hice.** Cerrar cada ventana, o correr por celdas.

---

## 22/09 — Faltaba ipykernel (clase 10)

**Qué pasó.** Para correr las celdas `# %%` en la ventana interactiva hace
falta el paquete `ipykernel`, y no estaba instalado.

**Qué hice.** Instalarlo en el mismo Python que usa VS Code:
`py -3.13 -m pip install ipykernel pandas numpy matplotlib`.

---

## 22/09 — NameError al correr el paso 3 solo (clase 10)

**Qué pasó.** Quería correr solo el bloque del paso 3, que era el gráfico que
tenía que presentar. Pero el paso 3 usa `df` y `ESTACION`, que se crean en el
paso 2: corrido solo, da `NameError: name 'df' is not defined`.

**Qué hice.** Correr desde el principio hasta el paso 3. Ahora el encabezado
del script lo advierte.

---

## 22/09 — Ruta fija de mi computadora (clase 10)

**Qué pasó.** Para que el script encontrara los datos puse la ruta completa
de mi carpeta, con mi usuario de Windows.

**Por qué está mal.** No funciona en otra computadora y muestra mi usuario.
Es la pregunta 11 del ejercicio de fundamentos.

**Qué hice (03/11).** Todos los scripts arman la ruta desde la raíz del
repositorio. Ver `recetas/rutas_que_funcionan_en_otra_compu.md`.

---

## 03/11 — Los CSV nunca estuvieron en GitHub

**Qué pasó.** Creía haber subido los CSV, pero no estaban en ningún commit:
solo los `.py`, el PDF y el `.png`.

**Qué aprendí.** Igual no corresponde subirlos: el programa del curso dice
que los datos crudos no se versionan. Ahora están en `.gitignore` y
`datos/obtener_datos.py` los baja de la fuente.

---

## 03/11 — Un script buscaba el CSV en toda mi carpeta de usuario

**Qué pasó.** `ozono_max_8h.py` tenía una función que, si no encontraba el
archivo, lo buscaba en toda la carpeta del usuario (`Path.home().rglob`).

**Por qué está mal.** Es lento y puede agarrar otro archivo con el mismo
nombre, sin avisar cuál.

**Qué hice.** Ruta fija dentro del repositorio (`datos/`) y un mensaje claro
si el archivo no está.

---

## 03/11 — Departamentos contados dos veces (clase 5)

**Cómo se manifestó.** Al contar empresas por departamento aparecían
«SAN JOSÉ» y «TACUAREMBÓ» dos veces cada uno: 22 departamentos en un país
que tiene 19.

**Cómo lo detecté.** Las dos versiones se veían idénticas. Mirando los
caracteres uno por uno, una traía un carácter invisible al final: `\x90` (de
control) en San José y `\xa0` (espacio duro) en Tacuarembó.

**Qué hice.** Sacar caracteres de control y espacios al borde antes de
contar. Quedan 19. También pasé `S/D` a faltante: 267 empresas no tienen
departamento. Ver `recetas/faltantes_disfrazados.md`.

---

## 03/11 — La hora de la tabla tránsito-aire dice UTC y no lo es (clase 12)

**Qué pasó.** En `transito_aire_junio2024.csv` la hora termina en `Z`, que
quiere decir UTC.

**Cómo lo detecté.** El tránsito de Tres Cruces es mínimo a las 4 y máximo a
las 17 tal como viene. Si fuera UTC, en hora de Montevideo el máximo caería a
las 14, lo que no tiene sentido para el tránsito.

**Qué hice.** No convertir la zona horaria y dejarlo anotado en el script.

---

## 03/11 — Parquet no conservó una categórica (clase 3)

**Qué pasó.** En el ejercicio 4, el viaje por parquet conservó textura y
rigidez (con su orden), pero `certeza_observador`, categórica ordenada de 1 a
5, volvió como número entero.

**Qué aprendí.** Parquet guarda tipos mucho mejor que el CSV, pero igual hay
que mirar `.dtypes` después de leer.
