# =============================================================================
# Clase 2 — Generación de datos: de la caja negra al dataset
# =============================================================================
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


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


GRAFICOS = raiz_proyecto() / "graficos"

plt.rcParams.update({
    "font.family": ["Verdana", "Tahoma", "DejaVu Sans"],
    "font.size": 10, "axes.titlesize": 11, "figure.titlesize": 12,
})


# =============================================================================
# 1. El dataset de la caja
# =============================================================================
#%%
datos_caja = {
    "objeto_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "textura": ["suave", "rugoso", "poroso", "suave", "rugoso",
                "suave", "poroso", "rugoso", "suave", "poroso"],
    "rigidez": ["blando", "rígido", "medio", "blando", "rígido",
                "rígido", "blando", "medio", "medio", "blando"],
    "num_aristas": [0, 8, 0, 4, 12, 0, 0, 6, 4, 0],
    "peso_estimado_g": [45.0, 120.5, 15.0, 85.0, 210.0,
                        35.0, 18.5, 95.0, 70.0, 22.0],
    "certeza_observador": [5, 4, 3, 5, 4, 2, 4, 3, 4, 3],
}
caja = pd.DataFrame(datos_caja)

# Tipos según la tipología de la clase
caja["textura"] = caja["textura"].astype("category")                 # nominal
caja["rigidez"] = pd.Categorical(caja["rigidez"],                     # ordinal
                                 categories=["blando", "medio", "rígido"],
                                 ordered=True)
caja["certeza_observador"] = pd.Categorical(caja["certeza_observador"],  # metadato ordinal
                                            categories=[1, 2, 3, 4, 5],
                                            ordered=True)
# num_aristas queda entero (discreta) y peso_estimado_g decimal (continua)

caja.info()
print(caja.describe())


# =============================================================================
# 2. Método 1: bootstrap (muestreo con reemplazo, N = 100)
# =============================================================================
#%%
bootstrap = caja.sample(n=100, replace=True, random_state=42).reset_index(drop=True)

print("Objetos distintos en el bootstrap:", bootstrap["objeto_id"].nunique(), "de 10")
print("Veces que aparece cada objeto:")
print(bootstrap["objeto_id"].value_counts().sort_index().to_dict())

# El bootstrap no inventa valores: todo peso del bootstrap es un peso real
assert set(bootstrap["peso_estimado_g"]) <= set(caja["peso_estimado_g"])


# =============================================================================
# 3. Método 2: sintético paramétrico (normal, N = 500)
# =============================================================================
#%%
rng = np.random.default_rng(42)
mu = caja["peso_estimado_g"].mean()
sigma = caja["peso_estimado_g"].std()
print(f"Normal ajustada: media = {mu:.1f} g, desvío = {sigma:.1f} g")

pesos_crudos = rng.normal(loc=mu, scale=sigma, size=500)
# Restricción del mundo real: un peso no puede ser 0 ni negativo
pesos_sinteticos = np.clip(pesos_crudos, a_min=1.0, a_max=None)

recortados = (pesos_crudos < 1.0).sum()
debajo_del_minimo = (pesos_sinteticos < caja["peso_estimado_g"].min()).sum()
encima_del_maximo = (pesos_sinteticos > caja["peso_estimado_g"].max()).sum()
print(f"Pesos negativos o casi cero que el clip convirtió en 1 g: {recortados} de 500")
print(f"Pesos más livianos que el objeto más liviano de la caja (15 g): {debajo_del_minimo}")
print(f"Pesos más pesados que el objeto más pesado (210 g): {encima_del_maximo}")


# =============================================================================
# 4. ¿Qué conserva cada método? La relación entre rigidez y peso
# =============================================================================
#%%
print("\nPeso medio por rigidez:")
print("  caja     :", caja.groupby("rigidez", observed=True)["peso_estimado_g"].mean().round(1).to_dict())
print("  bootstrap:", bootstrap.groupby("rigidez", observed=True)["peso_estimado_g"].mean().round(1).to_dict())
# El sintético paramétrico generó solo pesos: no tiene rigidez. Esa relación
# no existe en los datos sintéticos.


# =============================================================================
# 5. Gráfico: la misma variable con los tres orígenes
# =============================================================================
#%%
fig, axes = plt.subplots(3, 1, figsize=(8, 7), sharex=True)
bordes = np.arange(0, 260, 10)
paneles = [
    (axes[0], caja["peso_estimado_g"], "Caja: 10 objetos medidos", "#2E86AB"),
    (axes[1], bootstrap["peso_estimado_g"], "Bootstrap: 100 filas remuestreadas", "#7B4B2A"),
    (axes[2], pd.Series(pesos_sinteticos), "Sintético normal: 500 pesos inventados", "#D4A373"),
]
for ax, serie, titulo, color in paneles:
    ax.hist(serie, bins=bordes, color=color, edgecolor="white")
    ax.set_title(titulo, loc="left")
    ax.set_ylabel("Cantidad")
    ax.grid(axis="y", alpha=0.3)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))  # cantidades enteras
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)

axes[2].annotate(f"{recortados} valores negativos\nconvertidos en 1 g",
                 xy=(5, recortados), xytext=(40, recortados + 5),
                 fontsize=9, arrowprops={"arrowstyle": "->", "color": "gray"})
axes[2].set_xlabel("Peso estimado (g)")
fig.suptitle("Peso estimado de los objetos de la caja negra, según cómo se generó el dato")
fig.text(0.01, 0.005, "Fuente: dinámica de la clase 2 (10 objetos). "
         "Bootstrap y sintético con semilla 42.", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.02, 1, 1))
fig.savefig(GRAFICOS / "clase02_caja_negra_sinteticos.png", dpi=150, bbox_inches="tight")
plt.show()


# =============================================================================
# Respuestas
# =============================================================================
# ¿Qué hace cada método?
# - El bootstrap repite filas reales. Con 100 filas aparecen los 10 objetos,
#   unos más que otros. No inventa ningún valor y conserva la fila entera,
#   así que conserva las relaciones: los rígidos siguen siendo los más
#   pesados. Lo que no puede hacer es mostrar un objeto que no estaba en la
#   muestra.
# - El sintético normal inventa pesos que nadie midió. Con media 71,6 g y
#   desvío 60,4 g, la normal pone probabilidad en pesos negativos: 61 de los
#   500 valores salieron negativos o casi cero y el clip los convirtió en
#   1 g. En total, 86 pesos sintéticos son más livianos que el objeto más
#   liviano de la caja (15 g). Esa pila de 1 g es un dato "fantasma": lo
#   crea el modelo, no la caja.
#   (El material de la clase dice desvío ~58,3 g; con pandas, que divide por
#   n - 1, da 60,4 g. Con n = 10 la diferencia se nota.)
# - Además, el sintético se hizo solo para el peso: perdió la rigidez, la
#   textura y las aristas, y con ellas la relación entre peso y rigidez.
#
# El problema de fondo: la caja tiene objetos livianos (15 a 45 g) y pesados
# (85 a 210 g), no una campana alrededor de 71,6 g. Suponer una normal para
# un proceso con grupos distintos genera valores en zonas donde no hay
# ningún objeto. Agrandar la tabla no agrega información sobre la caja: los
# 500 pesos salen de dos números calculados con 10 mediciones.
