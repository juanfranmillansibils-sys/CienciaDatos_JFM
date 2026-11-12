# Diario

Una entrada por semana: qué intenté, qué falló, qué decidí. Máximo 150
palabras.

> **Nota.** Llevo el diario desde el 03/11/2026. Las entradas anteriores las
> escribí ese día a partir de lo que quedó registrado: mis commits, mis
> archivos y mis conversaciones con Claude. Las semanas de las que no quedó
> registro están indicadas al final, sin completar.

---

## Semana del 10/08

**Qué intenté.** Crear el repositorio de la materia en GitHub y hacer la
primera confirmación (13/08).

**Qué falló.** No lo registré.

**Qué decidí.** Un repositorio propio para la materia: `CienciaDatos_JFM`.

---

## Semana del 17/08

**Qué intenté.** El ejercicio de opción múltiple de fundamentos (objetos,
tipos y errores en R y Python). Lo subí como PDF el 20/08.

---

## Semana del 31/08

**Qué intenté.** Aplicar la plantilla de carga de datos de la clase 5 a otro
archivo: el Directorio de Empresas Industriales. Revisé identificador,
faltantes y duplicados, y conté empresas por departamento y actividad.

**Qué falló.** La plantilla leía de una carpeta del repositorio de la
profesora que en el mío no existe.

**Qué decidí.** Guardar los datos en una carpeta `Data/` de mi repositorio y
leerlos desde ahí. El RUT sirve como identificador: no se repite.

---

## Semana del 14/09

**Qué intenté.** Con el equipo, armar la encuesta previa del experimento en
Google Forms (15/09). Y ponerme al día con la clase 7: carga y
transformación del ozono, con material en R que tenía que pasar a Python.

**Qué falló.** VS Code no corría nada (modo restringido). El script de la
clase pedía tres archivos y yo tenía uno. Leído como latin-1, el archivo
mostraba «ColÃ³n». Y el script entero abría un gráfico tras otro.

**Qué decidí.** Con ayuda de Claude: una versión adaptada solo con ozono, en
UTF-8, y un script corto para el gráfico que había que entregar, el máximo
diario de la media móvil de 8 horas. Ninguna estación superó la guía OMS de
100 µg/m³; Curva de Maroñas llegó a 96 el 1/2.

---

## Semana del 21/09

**Qué intenté.** Correr el script de tránsito y calidad del aire de la clase
10 y presentar el gráfico del paso 3 (una semana en Tres Cruces). Para el
equipo, armar la diapositiva con el QR de la encuesta.

**Qué falló.** Faltaba instalar `ipykernel` para correr por celdas. Al
correr solo el paso 3 daba `NameError`, porque depende de variables del
paso 2. Para que encontrara los datos usé una ruta fija de mi computadora.

**Qué decidí.** Correr el script desde el principio hasta el paso 3. En la
diapositiva no mencionar el objetivo del experimento, para no condicionar
las respuestas.

---

## Semana del 26/10

**Qué intenté.** Preparar el parcial, que es en papel: un resumen por tipo
de ejercicio y el parcial de ejemplo resuelto ejercicio por ejercicio, con
Claude.

**Qué falló.** La clasificación de variables que tenía en el resumen era más
detallada que la vista en clase (cualitativas nominales, ordinales o
binarias, y cuantitativas) y me confundía.

**Qué decidí.** Estudiar con la clasificación de clase y usar la otra solo
como complemento.

---

## Semana del 02/11

**Qué intenté.** Ordenar el repositorio según el programa (bitácora personal
con `diario/`, `funciones/`, `recetas/` y `errores/`), subir lo que tenía
solo en mi compu y completar las actividades de las clases 2,3, 11.
Lo hice con ayuda de Claude.

**Qué falló.** Los CSV nunca habían llegado a GitHub. Un script buscaba los
datos en toda mi carpeta de usuario. El directorio de empresas contaba 22
departamentos por caracteres invisibles. La tabla de la clase 12 marca la
hora como UTC y es hora local.

**Qué decidí.** No subir datos: un script que los baja y una ficha de
fuentes. Rutas relativas en todos los scripts. Declarar el uso de IA en el
README.

