# =============================================================================
# Clase 7 — Carga y transformación: ozono, Montevideo (enero-abril de 2024)
# =============================================================================
# Versión adaptada del script de la clase (carga_y_transformacion.py). El de la
# clase usa tres archivos de enero-abril (ozono, PM2.5 y conteo vehicular); yo
# tenía solo el de ozono, así que esta versión trabaja con ese y deja indicado
# lo que falta.
#
# Datos: datos/o3_01_2024_04_2024.csv, se baja con datos/obtener_datos.py.
#
# Cómo correrlo:
#   a) Completo, desde la terminal:
#        python clases/clase07/clase07_carga_y_transformacion_ozono.py
#      (se abre una ventana por gráfico; hay que cerrarla para que siga)
#   b) Por bloques, recomendado: en VS Code cada "# %%" es una celda.
#      Cursor adentro y Shift+Enter, de arriba hacia abajo.
# =============================================================================

# %%
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def raiz_proyecto():
    """Sube carpetas hasta encontrar la raíz del repositorio (la que tiene .git)."""
    try:
        actual = Path(__file__).resolve().parent
    except NameError:  # al correr celdas sueltas en VS Code
        actual = Path.cwd().resolve()
    for carpeta in [actual, *actual.parents]:
        if (carpeta / ".git").exists() or (carpeta / "datos" / "fuentes.md").exists():
            return carpeta
    raise FileNotFoundError("No encontré la raíz del repositorio CienciaDatos_JFM.")


RUTA_CSV = raiz_proyecto() / "datos" / "o3_01_2024_04_2024.csv"
if not RUTA_CSV.exists():
    raise FileNotFoundError(
        f"No se encontró {RUTA_CSV}. Correr primero datos/obtener_datos.py"
    )

print("Leyendo:", RUTA_CSV)


# =============================================================================
# 1. Carga de datos
# =============================================================================
# read_csv de R detecta fechas automáticamente; pandas necesita parse_dates.
# El archivo está en UTF-8. Leerlo como latin1 rompe los nombres de estación
# ("ColÃ³n"), que es lo que después obliga al diccionario de reemplazos.

# %%
ozono = pd.read_csv(RUTA_CSV, encoding="utf-8", parse_dates=["fecha"])

# Copia con los NaN todavía adentro: la sección 10 la necesita, porque la
# evidencia sobre el funcionamiento del sensor vive en los faltantes.
ozono_limpio = ozono.copy()

# --- Fuentes que NO tenemos en esta versión ---
# pm   = pd.read_csv(CLASE / "pm_2_5_01_2024_04_2024.csv", ...)
# auto = pd.read_csv(CLASE / "autoscope_04_2024_volumen.csv", ...)


# =============================================================================
# 2. Data profiling: id, nulos y duplicados
# =============================================================================

# %%
## 2.1 Información básica del dataset (equivale a str() de R)
ozono.info()
print(ozono.head())

# %%
## 2.2 Identificador
# Los datos se toman por estación (que tiene una ubicación geográfica: es una
# característica de la estación, no de la medición) y por fecha.
# El identificador es la combinación fecha + estacion.
print(ozono.iloc[0:10, 2])
print(ozono["estacion"].unique())

# Si hubieras leído con latin1, acá harías la limpieza de caracteres:
# pauta_limpieza = {"Ã³": "o", "Ã±": "ni", "Ã¡": "á", "Ã©": "é",
#                   "Ã­": "í", "Ãº": "ú", "Ã“": "Ó", "Ã‘": "NI", "Ã": "í"}
# for buscar, reemplazar in pauta_limpieza.items():
#     ozono_limpio["estacion"] = ozono_limpio["estacion"].str.replace(
#         buscar, reemplazar, regex=False)

# %%
## 2.3 Valores faltantes (equivale a colSums(is.na()))
print(ozono.isna().sum())

# Cómo se reparten los faltantes entre estaciones
print(
    ozono.groupby("estacion")["o3"].agg(
        n_filas="size",
        n_na=lambda s: s.isna().sum(),
        prop_na=lambda s: s.isna().mean(),
    )
)

# La única variable con faltantes es la medición, así que se pueden eliminar:
# no perdemos identificador. (Podría discutirse si hay que eliminar las fechas
# sin registro o conservarlas como evidencia.)
ozono_sinna = ozono_limpio.dropna(subset=["o3"]).copy()
print("Filas tras eliminar NaN:", len(ozono_sinna))

# %%
## 2.4 Duplicados
# Filas repetidas en todo el dataset
print("Filas idénticas repetidas:", ozono_sinna.duplicated().sum())

# Más importante: ¿la clave declarada es realmente única?
print(
    "Claves fecha+estacion repetidas:",
    ozono_sinna.duplicated(subset=["fecha", "estacion"]).sum(),
)

# Ver TODAS las filas involucradas en un duplicado (la primera y sus copias)
ozono_repetidas = ozono_sinna[ozono_sinna.duplicated(keep=False)]

## 2.5 Eliminar duplicados
dataset_sindup = ozono_sinna.drop_duplicates()


# =============================================================================
# 3. Tipos de datos y transformación
# =============================================================================

# %%
## 3.1 Fechas
# El equivalente de POSIXct es datetime64: por dentro es un entero (tiempo
# transcurrido desde el 1/1/1970), lo que hace rápida la aritmética de fechas
# y habilita .dt.year, .dt.floor("h"), y el ordenamiento cronológico correcto.
print(ozono["fecha"].dtype)

# Si no se hubiera parseado al leer:
# ozono["fecha"] = pd.to_datetime(ozono["fecha"])

# %%
## 3.2 Crear variables (el accesor .dt cumple el rol de lubridate)
ozono_new = ozono_sinna.assign(
    anio=lambda d: d["fecha"].dt.year,
    mes=lambda d: d["fecha"].dt.month,
    hora=lambda d: d["fecha"].dt.hour,
)
print(ozono_new.head())

# Chequeo de cobertura antes de graficar
print(ozono_new["anio"].unique())
print(ozono_new["mes"].value_counts().sort_index())


# =============================================================================
# 4. Generación de información
# =============================================================================

# %%
## 4.1 Agregación mensual
# n_registros_mes viaja junto al promedio: sin él no sabés cuánto dato lo
# respalda, y dos meses con cobertura muy distinta se ven igual en el gráfico.
ozono_mes = (
    ozono_new.groupby("mes")
    .agg(o3_medio_mes=("o3", "mean"), n_registros_mes=("o3", "size"))
    .reset_index()
)
print(ozono_mes)

# %%
## 4.2 Visualización
# Partes básicas de un gráfico: dataset, variable x, variable y, tipo de
# gráfico, y títulos (del gráfico y de los ejes).
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="blue", linewidth=2)
ax.scatter(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="red", s=60, zorder=3)
ax.set(
    title="Concentración de Ozono en el ambiente, por mes, 2024",
    xlabel="Mes",
    ylabel="O3 (µg/m³)",
)
ax.set_xticks(ozono_mes["mes"])
ax.grid(alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
plt.tight_layout()
plt.show()


# =============================================================================
# 5. Agregación temporal: minutal -> horario -> diario
# =============================================================================
# Pregunta central: al agregar, ¿qué estadístico representa el fenómeno?
#   - media: nivel típico
#   - máximo: episodios puntuales (muy sensible a errores del sensor)
#   - percentil 95: episodios altos, robusto a picos aislados
#   - n: cuántos minutos respaldan el valor agregado (cobertura)


# %%
def p95(x):
    return x.quantile(0.95)


## 5.1 Horario
# pd.Grouper(freq="h") cumple el rol de floor_date() + group_by()
ozono_hora = (
    ozono_sinna.groupby(["estacion", pd.Grouper(key="fecha", freq="h")])["o3"]
    .agg(media="mean", maximo="max", p95=p95, n_min="size")  # n_min: máx 60
    .reset_index()
    .rename(columns={"fecha": "fecha_hora"})
)
print(ozono_hora.head())

# %%
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(ozono_hora["fecha_hora"], ozono_hora["media"], color="blue", linewidth=1)
ax.set(
    title="Concentración de Ozono en el ambiente, por hora, 2024",
    xlabel="Fecha",
    ylabel="O3 (µg/m³)",
)
ax.grid(alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
plt.tight_layout()
plt.show()


# =============================================================================
# 6. Teoría estadística
# =============================================================================
# En la versión de la profe acá se ejecuta estadistica_basica.py, que dibuja
# los paneles A, B y C. No lo tenemos, pero la conclusión es la que importa:
# con 10 picos falsos de 500 µg/m³ entre 1450 datos, la media se mueve +3.2 y
# el p95 solo +1.3. En la media cada dato pesa por su VALOR; en el p95 pesa
# por su POSICIÓN en el orden. 10 de 1450 es 0.7 %, muy por debajo del 5 %,
# así que al p95 no le importa cuánto valían esos picos.
# runpy.run_path(str(CLASE / "estadistica_basica.py"))


# =============================================================================
# 7. Diario
# =============================================================================

# %%
ozono_dia = (
    ozono_sinna.groupby(["estacion", pd.Grouper(key="fecha", freq="D")])["o3"]
    .agg(media="mean", maximo="max", p95=p95, n_min="size")  # n_min: máx 1440
    .reset_index()
    .rename(columns={"fecha": "dia"})
)
print(ozono_dia.head())

# %%
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(ozono_dia["dia"], ozono_dia["media"], color="blue", linewidth=1)
ax.scatter(ozono_dia["dia"], ozono_dia["media"], color="red", s=8, zorder=3)
ax.set(
    title="Concentración de Ozono en el ambiente, por día, 2024",
    xlabel="Fecha",
    ylabel="O3 (µg/m³)",
)
ax.grid(alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
plt.tight_layout()
plt.show()

# %%
# Las tres curvas cuentan historias distintas sobre el mismo día
estaciones = ozono_dia["estacion"].unique()
fig, axes = plt.subplots(
    len(estaciones), 1, figsize=(9, 3 * len(estaciones)), sharex=True, squeeze=False
)
for ax, est in zip(axes[:, 0], estaciones):
    d = ozono_dia[ozono_dia["estacion"] == est]
    for col in ("media", "p95", "maximo"):
        ax.plot(d["dia"], d[col], label=col)
    ax.set_title(est)
    ax.set_ylabel("O3 (µg/m³)")
    ax.grid(alpha=0.3)
axes[0, 0].legend()
fig.suptitle("Agregación diaria: media, p95 y máximo por estación")
plt.tight_layout()
plt.show()


# =============================================================================
# 8. El estadístico normativo: máximo diario de la media móvil de 8 horas
# =============================================================================
# Las guías OMS (2021) para O3 usan el máximo diario de la media móvil de 8 h.
# Una media móvil opera sobre POSICIONES, no sobre tiempo: si faltan horas,
# ocho posiciones consecutivas pueden abarcar quince horas reales y el
# resultado deja de ser lo que define el estándar. Por eso primero se completa
# la grilla horaria y recién después se corre la ventana.

# %%
grilla_horaria = pd.date_range(
    ozono_hora["fecha_hora"].min(), ozono_hora["fecha_hora"].max(), freq="h"
)

# Producto cartesiano estación x hora = equivalente de tidyr::complete()
indice_completo = pd.MultiIndex.from_product(
    [sorted(ozono_hora["estacion"].unique()), grilla_horaria],
    names=["estacion", "fecha_hora"],
)

ozono_8h = (
    ozono_hora.set_index(["estacion", "fecha_hora"])[["media"]]
    .reindex(indice_completo)  # inserta NaN en las horas ausentes
    .reset_index()
)
print("Horas con dato:", ozono_hora.shape[0])
print("Horas tras completar la grilla:", ozono_8h.shape[0])

# min_periods=8: si falta alguna de las 8 horas, el resultado es NaN.
# Es deliberado: una ventana incompleta no es una media móvil de 8 h.
ozono_8h["media_8h"] = ozono_8h.groupby("estacion")["media"].transform(
    lambda s: s.rolling(8, min_periods=8).mean()
)

max_8h_dia = (
    ozono_8h.assign(dia=lambda d: d["fecha_hora"].dt.floor("D"))
    .groupby(["estacion", "dia"])["media_8h"]
    .agg(max_8h="max", horas_validas="count")  # count no cuenta los NaN
    .reset_index()
)
print(max_8h_dia.head())

# %%
fig, ax = plt.subplots(figsize=(9, 5))
for est, d in max_8h_dia.groupby("estacion"):
    ax.plot(d["dia"], d["max_8h"], label=est)
ax.axhline(100, linestyle="--", color="black")  # guía OMS 2021: 100 µg/m³
ax.set(title="Máximo diario de la media móvil de 8 h", ylabel="O3 (µg/m³)")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# =============================================================================
# 9. Mapa
# =============================================================================
# Requiere mapa.py, que no tenemos. Necesitaría folium o geopandas.
# runpy.run_path(str(CLASE / "mapa.py"))


# =============================================================================
# 10. Patrones de faltantes
# =============================================================================
# Tres tipos de faltante en una serie de sensor:
#   a) explícito: la fila existe, o3 es NaN
#   b) en rachas: muchos NaN consecutivos -> sensor caído o en mantenimiento
#   c) implícito: la fila no existe (el minuto no está en el archivo)
# Eliminar NaN sin mirar esto borra evidencia sobre el proceso de medición.
# Por eso esta sección trabaja sobre ozono_limpio, NO sobre ozono_sinna.

# %%
## 10.1 Faltantes explícitos por estación
resumen_na = (
    ozono_limpio.groupby("estacion")["o3"]
    .agg(
        n_filas="size",
        n_na=lambda s: s.isna().sum(),
        prop_na=lambda s: s.isna().mean(),
    )
    .reset_index()
)
print(resumen_na)

# %%
## 10.2 ¿Cuándo faltan? Proporción de NaN por día
na_dia = (
    ozono_limpio.assign(es_na=lambda d: d["o3"].isna())
    .groupby(["estacion", pd.Grouper(key="fecha", freq="D")])["es_na"]
    .mean()
    .rename("prop_na")
    .reset_index()
    .rename(columns={"fecha": "dia"})
)

estaciones = na_dia["estacion"].unique()
fig, axes = plt.subplots(
    len(estaciones), 1, figsize=(9, 2.5 * len(estaciones)), sharex=True, squeeze=False
)
for ax, est in zip(axes[:, 0], estaciones):
    d = na_dia[na_dia["estacion"] == est]
    ax.bar(d["dia"], d["prop_na"], color="grey", width=1)
    ax.set_title(est)
    ax.set_ylabel("Proporción de NaN")
fig.suptitle("Proporción de minutos sin dato, por día y estación")
plt.tight_layout()
plt.show()


# %%
## 10.3 Rachas de NaN consecutivos (equivalente de rle() de R)
def rachas_na(serie: pd.Series) -> pd.DataFrame:
    """Devuelve una fila por racha: si es faltante y cuántos minutos dura."""
    es_na = serie.isna().to_numpy()
    if len(es_na) == 0:
        return pd.DataFrame({"faltante": [], "largo": []})
    # cada cambio de valor abre una racha nueva
    cambios = np.concatenate([[0], np.cumsum(es_na[1:] != es_na[:-1])])
    return (
        pd.DataFrame({"faltante": es_na, "id_racha": cambios})
        .groupby("id_racha")
        .agg(faltante=("faltante", "first"), largo=("faltante", "size"))
        .reset_index(drop=True)
    )


partes = []
for est, grupo in ozono_limpio.sort_values(["estacion", "fecha"]).groupby("estacion"):
    r = rachas_na(grupo["o3"])
    r["estacion"] = est
    partes.append(r)
rachas = pd.concat(partes, ignore_index=True)

tabla_rachas = (
    rachas[rachas["faltante"]]
    .assign(
        tipo=lambda d: pd.cut(
            d["largo"],
            bins=[0, 1, 10, 60, 1440, np.inf],
            labels=["1 min", "2-10 min", "11 min-1 h", "1 h-1 día", "> 1 día"],
        )
    )
    .groupby(["estacion", "tipo"], observed=True)
    .size()
    .rename("n_rachas")
    .reset_index()
)
print(tabla_rachas)
# Lectura: muchas rachas de 1 min = ruido de transmisión.
# Pocas rachas de más de 1 día = sensor fuera de servicio.
# Son mecanismos distintos y se tratan distinto.

# %%
## 10.4 Faltantes implícitos: minutos que no están en el archivo
# Este es el faltante que isna() NO puede ver, porque no hay fila que contar.
implicitos = (
    ozono_limpio.groupby("estacion")["fecha"]
    .agg(primero="min", ultimo="max", presentes="nunique")
    .assign(
        esperados=lambda d: (
            (d["ultimo"] - d["primero"]) / pd.Timedelta(minutes=1)
        ).astype(int)
        + 1,
        implicitos=lambda d: d["esperados"] - d["presentes"],
        prop_implicitos=lambda d: d["implicitos"] / d["esperados"],
    )
    .reset_index()
)
print(implicitos)

# %%
## 10.5 Cobertura contra la grilla del período pedido
INICIO = pd.Timestamp("2024-01-01 00:00:00")
FIN = pd.Timestamp("2024-04-30 23:59:00")
ESPERADOS = int((FIN - INICIO) / pd.Timedelta(minutes=1)) + 1

cobertura = (
    ozono_limpio.groupby("estacion")
    .agg(presentes=("fecha", "nunique"), validos=("o3", "count"))  # count ignora NaN
    .assign(
        esperados=ESPERADOS,
        sin_fila=lambda d: d["esperados"] - d["presentes"],
        fila_sin_medicion=lambda d: d["presentes"] - d["validos"],
        cobertura=lambda d: 100 * (d["validos"] / d["esperados"]).round(3),
    )
    .reset_index()
)
print(cobertura)
