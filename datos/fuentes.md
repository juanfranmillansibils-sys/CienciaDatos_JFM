# Fuentes de datos

Los datos crudos no se versionan. Esta carpeta guarda el código que los obtiene
(`obtener_datos.py`) y esta ficha con el origen de cada archivo.

Para tenerlos en la computadora, desde la raíz del repositorio:

```
python datos/obtener_datos.py
```

Los conteos de filas se verificaron el 03/11/2026 sobre los archivos que usé en
clase. El script vuelve a contar al bajar y avisa si algo cambió.

| Archivo | Clase | Publica | Licencia | Filas | Período |
|---|---|---|---|---|---|
| `empresasdei_20230330.csv` | 5 | Ministerio de Industria, Energía y Minería | Datos abiertos de Uruguay | 1.422 | corte del 30/03/2023 |
| `o3_01_2024_04_2024.csv` | 7 | Intendencia de Montevideo | Datos abiertos de Uruguay | 291.926 | 01/01/2024 a 29/04/2024 |
| `no2_05_2024_08_2024.csv` | 10 | Intendencia de Montevideo | Datos abiertos de Uruguay | 347.952 | 01/05/2024 a 30/08/2024 |
| `pm_2_5_05_2024_08_2024.csv` | 10 | Intendencia de Montevideo | Datos abiertos de Uruguay | 433.338 | 01/05/2024 a 30/08/2024 |
| `autoscope_06_2024_volumen.csv` | 10 | Intendencia de Montevideo, Centro de Gestión de Movilidad | Datos abiertos de Uruguay | 3.688.891 | junio de 2024 |
| `transito_aire_junio2024.csv` | 12 | Repositorio del curso (tabla preparada por la cátedra) | la de los datos de origen | 2.160 | junio de 2024 |
| `ticket.jpg` | 11 | Repositorio del curso | — | — | — |

## Detalle por fuente

### Directorio de Empresas Industriales (DEI)

- Catálogo: <https://catalogodatos.gub.uy/dataset/miem-dei>
- Una fila por empresa registrada. El RUT no se repite: es el identificador.
- Lo que falta viene escrito como `S/D` (sin dato), no como celda vacía.
- Dos departamentos traen un carácter invisible al final (`SAN JOSÉ` y
  `TACUAREMBÓ`), lo que parte su cuenta en dos. Ver `errores/errores.md`.
- **Trae datos personales**: muchas empresas son unipersonales y la
  denominación social es el nombre de una persona, junto con teléfono y
  correo. Es otra razón para no subir el archivo.

### Calidad del aire: ozono, NO2 y PM2.5

- Ozono: <https://catalogodatos.gub.uy/dataset/calidad-del-aire-ozono-o3>
- NO2: <https://catalogodatos.gub.uy/dataset/dioxido-de-nitrogeno>
- PM2.5: <https://catalogodatos.gub.uy/dataset/datos-por-estacion-pm-2-5>
- Una fila por estación y minuto. Columnas: `fecha`, el contaminante (`o3`,
  `no2` o `pm2_5`, en µg/m³), `estacion`, `longitud`, `latitud`.
- Codificación UTF-8. Leerlos como latin-1 rompe los nombres de estación
  («ColÃ³n»).
- Estaciones: ozono en Colón y Curva de Maroñas; NO2 en Tres Cruces y Curva de
  Maroñas; PM2.5 en Tres Cruces, Curva de Maroñas y Museo Romántico.
- El archivo de ozono termina el 29/04, no el 30/04 como dice su nombre.

### Conteo vehicular en las principales avenidas

- Catálogo: <https://catalogodatos.gub.uy/dataset/conteo-vehicular-en-las-principales-avenidas-de-montevideo>
  (recurso «Conteo Junio 2024»)
- Una fila por detector, carril y registro. `volume` es la cantidad de
  vehículos en el intervalo; `latitud` y `longitud` ubican el detector.
- Pesa unos 330 MB.

### Tabla tránsito-aire de junio de 2024

- Repositorio del curso:
  <https://github.com/DavytJ/Introduccion-a-la-ciencia-de-datos>, carpeta
  `clases/clase10`.
- La cátedra la armó a partir de las tres fuentes anteriores: una fila por
  estación y hora, con `transito`, `no2` y `pm25`.

### Ticket

- La foto del ticket que se usó en la clase 11, del mismo repositorio
  (`clases/clase11/clase_ia/ticket.jpg`). No tiene datos personales.

## Licencia

Las fuentes de gub.uy se publican bajo la Licencia de Datos Abiertos de
Uruguay (AGESIC), que permite usarlos y redistribuirlos citando la fuente.
