# Media móvil sin saltar huecos

**Problema.** `rolling(8)` promedia **8 filas**, no 8 horas. Si a la serie le
faltan horas, una ventana de 8 filas puede abarcar 15 horas reales, y el
resultado ya no es el indicador que pide la norma (la guía OMS 2021 de ozono
usa el máximo diario de la media móvil de 8 horas).

**Receta.** Completar la grilla horaria con NaN y exigir la ventana entera.

```python
# 1. De minutos a horas
por_hora = (df.groupby(["estacion", pd.Grouper(key="fecha", freq="h")])["o3"]
              .mean().rename("media").reset_index())

# 2. Grilla completa: todas las horas para todas las estaciones
grilla = pd.date_range(por_hora["fecha"].min(), por_hora["fecha"].max(), freq="h")
indice = pd.MultiIndex.from_product(
    [sorted(por_hora["estacion"].unique()), grilla], names=["estacion", "fecha"])
completa = (por_hora.set_index(["estacion", "fecha"])[["media"]]
                    .reindex(indice).reset_index())

# 3. Media móvil que da NaN si falta alguna de las 8 horas
completa["media_8h"] = (completa.groupby("estacion")["media"]
                                .transform(lambda s: s.rolling(8, min_periods=8).mean()))

# 4. Máximo diario
max_dia = (completa.assign(dia=completa["fecha"].dt.floor("D"))
                   .groupby(["estacion", "dia"])["media_8h"].max())
```

**Cuánto cambia.** En el ozono de enero a abril había 4.312 horas con dato,
y la grilla completa tiene 5.760: faltaba una de cada cuatro horas. Sin
completar, muchas ventanas habrían mezclado horas lejanas.

Ver `clases/clase07/clase07_ozono_max_8h.py`. La función con su prueba está
en `funciones/utilidades.py` (`media_movil_completa`).
