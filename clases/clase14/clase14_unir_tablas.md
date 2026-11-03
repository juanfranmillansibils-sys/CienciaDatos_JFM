# Clase 14 — Ejercicios 58 a 61: unir tablas

Ejercicios en papel del curso (`clases/clase14/ejercicios_58_61_papel.pdf`).
Cada respuesta está comprobada en pandas con `clase14_unir_tablas.py`, y
después la comparé con las soluciones publicadas.

Lo que hay que tener presente en los cuatro:

- **Unión izquierda**: quedan todas las filas de la tabla de la izquierda. Si
  una no encuentra pareja, lo que viene de la derecha queda vacío.
- **Unión interna**: quedan solo las filas que encuentran pareja en las dos.
- Si la clave se repite en la tabla de la derecha, una fila de la izquierda
  aparece varias veces. Por eso hay que **contar filas antes y después**.

## Ejercicio 58. Completar una unión

**a)** Unión izquierda de `vuelos` con `aerolineas`, clave `carrier`:

| vuelo | carrier | name |
|---|---|---|
| 1 | UA | United Air Lines Inc. |
| 2 | AA | American Airlines Inc. |
| 3 | B6 | JetBlue Airways |
| 4 | UA | United Air Lines Inc. |
| 5 | DL | *(vacío)* |

United aparece en dos filas: una aerolínea puede tener muchos vuelos.

**b)** La unión interna tiene **4 filas**.

**c)** Se pierde el **vuelo 5**. Su aerolínea, DL, no está en la tabla
`aerolineas`. El vuelo existió: lo que falta es el dato en la otra tabla.

## Ejercicio 59. Clave con nombres distintos

**a)** En `vuelos` la clave es `dest`; en `aeropuertos` es `faa`. Las dos
guardan el código del aeropuerto, con distinto nombre. En pandas:
`vuelos.merge(aeropuertos, left_on="dest", right_on="faa", how="left")`.

**b)**

| vuelo | dest | name |
|---|---|---|
| 1 | IAH | George Bush Intercontinental |
| 2 | MIA | Miami Intl |
| 3 | SJU | *(vacío)* |
| 4 | ORD | Chicago Ohare Intl |
| 5 | ATL | Hartsfield Jackson Atlanta Intl |

**c)** La unión interna tiene **4 filas**: se pierde el vuelo 3, porque SJU no
está en `aeropuertos`.

**Para ir más lejos.** Una `name` es el nombre de la aerolínea y la otra el
del aeropuerto de destino. pandas las llama `name_x` y `name_y`, que no dicen
nada. Mejor `nombre_aerolinea` y `nombre_aeropuerto_destino`, o pasarle
`suffixes=("_aerolinea", "_aeropuerto")` al unir.

## Ejercicio 60. Una clave incompleta

**a)** Con clave `origin` y `hour`: **3 filas**. Cada vuelo encuentra una sola
fila de clima.

**b)** Con clave `origin` solamente: **6 filas**. Cada vuelo se aparea con las
dos horas de su aeropuerto.

**c)**

| vuelo | origin | hour (de vuelos) | hour (de clima) | visib |
|---|---|---|---|---|
| 1 | EWR | 5 | 5 | 10 |
| 1 | EWR | 5 | 6 | 2 |
| 2 | EWR | 6 | 5 | 10 |
| 2 | EWR | 6 | 6 | 2 |
| 3 | JFK | 5 | 5 | 10 |
| 3 | JFK | 5 | 6 | 0,5 |

**d)** Sirve la de **(a)**. En la de (b) cada vuelo tiene dos visibilidades y
no se sabe cuál fue la de su salida. Además, la tabla deja de tener una fila
por vuelo: cualquier conteo o promedio por vuelo da mal.

**Para ir más lejos.** Sin la fila JFK, 5: la unión izquierda sigue con
**3 filas** y el vuelo 3 queda con `visib` **vacío**; la interna tiene
**2 filas**.

## Ejercicio 61. Leer el número de filas

**a)** A: igual. B: menos. C: más. D: igual.

**b)** 27.004 − 26.324 = **680 vuelos** perdidos: sus destinos no están en
la tabla de aeropuertos.

**c)** 646.428 / 27.004 ≈ **23,9**: cada vuelo aparece casi 24 veces, una por
hora del día. A la clave le falta **`hour`**. No da 24 justo porque al clima
le faltan algunas horas.

**d)** Con unión izquierda **no cambia**: siguen siendo 27.004 filas, y los
4.479 vuelos sin avión quedan con las columnas del avión vacías. Con unión
interna quedan **22.525 filas** (27.004 − 4.479).

**Para ir más lejos.** Para calcular la antigüedad de los aviones solo sirven
los vuelos que encontraron su avión, así que en la práctica es la interna (o
la izquierda, descartando después las filas vacías). Lo que se gana: cada fila
tiene el año del avión. Lo que se pierde: 4.479 vuelos, y si los vuelos sin
avión se concentran en algunas aerolíneas, el resultado habla solo de las
otras. Antes de sacar conclusiones conviene mirar de quién son esos vuelos.
La izquierda conserva todos los vuelos para otras preguntas, con la condición
de recordar que esas filas tienen faltantes.
