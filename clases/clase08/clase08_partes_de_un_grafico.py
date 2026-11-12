# =============================================================================
# Clase 8 — Las partes de un gráfico (primera parte: una serie)
# =============================================================================
# Material: clases/clase8/partes-de-un-grafico-vista-previa-1.pdf y
# vizualizacion_basica_python.py del repositorio del curso.
#
# El teórico parte del gráfico de ozono mensual de la clase 7, recorre cada
# parte (figura, ejes, título, etiquetas, marcas, geometría, atributos,
# grilla, bordes, guardado) y termina con una versión corregida.
#
# Diferencia con el material: allá los valores se leyeron del gráfico
# original; acá se calculan del CSV de ozono. Dan lo mismo (29,1; 35,6;
# 24,0; 25,7 µg/m³), salvo febrero, que en el teórico figura como 35,5.
#
# Datos: datos/o3_01_2024_04_2024.csv (se baja con datos/obtener_datos.py).
# Guarda: graficos/clase08_partida.png y graficos/clase08_corregida.png.
# =============================================================================

#%%
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
RUTA = RAIZ / "datos" / "o3_01_2024_04_2024.csv"
GRAFICOS = RAIZ / "graficos"
if not RUTA.exists():
    raise FileNotFoundError(f"Falta {RUTA}. Correr primero datos/obtener_datos.py")

plt.rcParams.update({
    "font.family": ["Verdana", "Tahoma", "DejaVu Sans"],
    "font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10,
})

# =============================================================================
# Datos: media mensual de ozono (las dos estaciones juntas, como en la clase 7)
# =============================================================================
#%%
ozono = pd.read_csv(RUTA, encoding="utf-8", parse_dates=["fecha"]).dropna(subset=["o3"])
ozono_mes = (ozono.assign(mes=ozono["fecha"].dt.month)
                  .groupby("mes")
                  .agg(o3_medio_mes=("o3", "mean"), n_registros=("o3", "size"))
                  .reset_index())
print(ozono_mes.round(1))


# =============================================================================
# 1. El gráfico del que partimos (código de la clase 7, sección 4.2)
# =============================================================================
#%%
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="blue", linewidth=2)
ax.scatter(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="red", s=60, zorder=3)
ax.set(title="Concentración de Ozono en el ambiente, por mes, 2024",
       xlabel="Fecha", ylabel="Valores")
ax.grid(alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
plt.tight_layout()
fig.savefig(GRAFICOS / "clase08_partida.png", dpi=150, bbox_inches="tight")  # antes de show()
plt.show()

# Qué le falta, parte por parte:
# - Etiquetas: "Valores" no dice qué se mide ni en qué unidad; "Fecha" no
#   dice que la unidad de tiempo es el mes.
# - Marcas: aparecen 1.5, 2.5 y 3.5, meses que no existen, porque mes es
#   numérico y matplotlib lo trata como continuo.
# - Eje vertical: empieza en 24, no en 0, y exagera la variación.
# - Fuente: no dice de dónde salen los datos.
# - Nota: no dice que es el promedio de dos estaciones, ni que los meses
#   tienen cobertura distinta (febrero tiene la mitad de registros que enero).


# =============================================================================
# 2. La versión corregida: mismos datos, mismas geometrías
# =============================================================================
#%%
fig, ax = plt.subplots(figsize=(8, 5))

# Geometría: la línea muestra la tendencia; los puntos, dónde hay medición
ax.plot(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="#2E86AB", linewidth=2)
ax.scatter(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="#2E86AB", s=60, zorder=3)

# Valor de cada punto, para no tener que estimarlo con la grilla
for mes, valor in zip(ozono_mes["mes"], ozono_mes["o3_medio_mes"]):
    ax.annotate(f"{valor:.1f}", (mes, valor), xytext=(0, 9),
                textcoords="offset points", ha="center", fontsize=9)

# Marcas: solo los meses que existen, con su nombre
ax.set_xticks([1, 2, 3, 4], ["Enero", "Febrero", "Marzo", "Abril"])
# Eje vertical desde cero
ax.set_ylim(0, 40)
ax.set_yticks(range(0, 41, 10))

# Título y etiquetas: qué, dónde, cuándo y en qué unidad
ax.set_title("Ozono en Montevideo: media mensual, enero a abril de 2024", loc="left")
ax.set_xlabel("Mes (2024)")
ax.set_ylabel("Ozono, O₃ (µg/m³)")

# Grilla y bordes: solo lo que ayuda a leer
ax.grid(axis="y", alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)

# Fuente y nota al pie
fig.text(0.01, 0.01,
         "Fuente: Intendencia de Montevideo, Catálogo de Datos Abiertos. "
         "Promedio de las estaciones Colón y Curva de Maroñas.\n"
         "Datos por minuto; abril hasta el día 29. Febrero tiene la mitad de "
         "registros que enero.",
         fontsize=8, color="gray", va="bottom")
fig.tight_layout(rect=(0, 0.07, 1, 1))
fig.savefig(GRAFICOS / "clase08_corregida.png", dpi=150, bbox_inches="tight")
plt.show()

# Qué cambió: título (dice qué, dónde y cuándo), etiquetas con variable y
# unidad, marcas en los cuatro meses con nombre, eje vertical desde 0, un
# solo color (rojo y azul no codificaban nada), el valor sobre cada punto,
# grilla solo horizontal, y fuente y nota al pie.
# Qué afirma el gráfico corregido: el ozono medio estuvo entre 24 y 36 µg/m³,
# con el máximo en febrero. Con el eje desde 0 se ve que la variación entre
# meses es moderada; el gráfico de partida la hacía parecer grande.
