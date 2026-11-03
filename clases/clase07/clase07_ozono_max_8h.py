# =============================================================================
# Clase 7 — Máximo diario de la media móvil de 8 horas
# Ozono, Montevideo (enero-abril de 2024)
# =============================================================================
# Lee datos/o3_01_2024_04_2024.csv, calcula el indicador de la guía OMS 2021
# y guarda el gráfico en graficos/clase07_ozono_max_8h.png.
#
# Datos: se bajan con datos/obtener_datos.py (ver datos/fuentes.md).
# =============================================================================

from pathlib import Path

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


RAIZ = raiz_proyecto()
RUTA_CSV = RAIZ / "datos" / "o3_01_2024_04_2024.csv"
SALIDA = RAIZ / "graficos" / "clase07_ozono_max_8h.png"

if not RUTA_CSV.exists():
    raise FileNotFoundError(
        f"No se encontró {RUTA_CSV}. Correr primero datos/obtener_datos.py"
    )

# -----------------------------------------------------------------------------
# 1. Carga
# -----------------------------------------------------------------------------
# El archivo está en UTF-8; parse_dates convierte 'fecha' a datetime64, que es
# lo que habilita la aritmética de fechas y el ordenamiento cronológico.
ozono = pd.read_csv(RUTA_CSV, encoding="utf-8", parse_dates=["fecha"])

# Se eliminan las mediciones faltantes: el identificador (fecha + estacion)
# nunca falta, así que no se pierden filas de referencia.
ozono = ozono.dropna(subset=["o3"])

# -----------------------------------------------------------------------------
# 2. Agregación minutal -> horaria
# -----------------------------------------------------------------------------
ozono_hora = (
    ozono.groupby(["estacion", pd.Grouper(key="fecha", freq="h")])["o3"]
    .mean()
    .rename("media")
    .reset_index()
    .rename(columns={"fecha": "fecha_hora"})
)

# -----------------------------------------------------------------------------
# 3. Grilla horaria completa
# -----------------------------------------------------------------------------
# Una media móvil opera sobre POSICIONES, no sobre tiempo. Si faltan horas,
# ocho posiciones consecutivas pueden abarcar más de ocho horas reales y el
# indicador deja de ser el que define la norma. Por eso se completa la grilla
# con NaN antes de correr la ventana.
grilla = pd.date_range(
    ozono_hora["fecha_hora"].min(), ozono_hora["fecha_hora"].max(), freq="h"
)
indice_completo = pd.MultiIndex.from_product(
    [sorted(ozono_hora["estacion"].unique()), grilla],
    names=["estacion", "fecha_hora"],
)
ozono_8h = (
    ozono_hora.set_index(["estacion", "fecha_hora"])[["media"]]
    .reindex(indice_completo)
    .reset_index()
)

# min_periods=8: si falta alguna de las 8 horas el resultado es NaN.
# Es deliberado: una ventana incompleta no es una media móvil de 8 horas.
ozono_8h["media_8h"] = ozono_8h.groupby("estacion")["media"].transform(
    lambda s: s.rolling(8, min_periods=8).mean()
)

# -----------------------------------------------------------------------------
# 4. Máximo diario de la media móvil (indicador OMS 2021)
# -----------------------------------------------------------------------------
max_8h_dia = (
    ozono_8h.assign(dia=lambda d: d["fecha_hora"].dt.floor("D"))
    .groupby(["estacion", "dia"])["media_8h"]
    .agg(max_8h="max", horas_validas="count")
    .reset_index()
)

# -----------------------------------------------------------------------------
# 5. Gráfico
# -----------------------------------------------------------------------------
plt.rcParams.update(
    {
        "font.family": ["Verdana", "Tahoma", "DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "legend.fontsize": 10,
    }
)

fig, ax = plt.subplots(figsize=(10, 5.5))

for estacion, datos in max_8h_dia.groupby("estacion"):
    ax.plot(datos["dia"], datos["max_8h"], linewidth=1.6, label=estacion)

# Guía OMS 2021 para ozono: 100 µg/m³
ax.axhline(100, linestyle="--", color="#555555", linewidth=1)
ax.text(
    max_8h_dia["dia"].min(), 102, "Guía OMS 2021: 100 µg/m³",
    fontsize=9, color="#555555",
)

ax.set_title("Máximo diario de la media móvil de 8 horas\nOzono en Montevideo, enero-abril 2024")
ax.set_xlabel("Fecha")
ax.set_ylabel("O₃ (µg/m³)")
ax.legend(title="Estación", frameon=False)
ax.grid(alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)

plt.tight_layout()
plt.savefig(SALIDA, dpi=200)
print("Gráfico guardado en:", SALIDA)

# Resumen numérico
print(
    max_8h_dia.groupby("estacion")["max_8h"].agg(
        dias="size", promedio="mean", maximo="max"
    ).round(1)
)

plt.show()
