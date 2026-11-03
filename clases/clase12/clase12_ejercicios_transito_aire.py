# =============================================================================
# Clase 12 — Tránsito y calidad del aire, junio de 2024 — Ejercicios resueltos
# Versión en Python (pandas + matplotlib + statsmodels)
# =============================================================================
# Consignas: clases/clase13/clase12_ejercicios(1).py del repositorio del curso.
# La PREPARACIÓN es la de la cátedra, sin cambios salvo la ruta del archivo.
# Debajo de cada ejercicio está la resolución y, en comentarios, la respuesta
# con los números de la corrida. Los ejercicios 1 a 4 los comparé con
# clase12_soluciones(1).py; del 5 al 7 no hay solución publicada.
#
# LA TABLA (datos/transito_aire_junio2024.csv): una fila por estación y hora
#   estacion   estación de calidad de aire (tres estaciones)
#   hora       fecha y hora de la medición
#   transito   vehículos por hora cerca de la estación
#   no2        dióxido de nitrógeno, promedio de la hora (µg/m³)
#   pm25       material particulado fino, promedio de la hora (µg/m³)
#
# Ojo con la hora: viene marcada como UTC (termina en "Z"), pero es hora de
# Montevideo. El tránsito de Tres Cruces es mínimo a las 4 y máximo a las 17
# tal como viene; si se convirtiera a hora local, el máximo pasaría a las 14,
# lo que no tiene sentido. Por eso NO se convierte la zona horaria.
#
# Datos: se bajan con datos/obtener_datos.py. Los gráficos se guardan en
# graficos/clase12_*.png.
# Paquetes: pip install pandas numpy matplotlib statsmodels
# =============================================================================

#%%
# =============================================================================
# PREPARACIÓN (de la cátedra)
# =============================================================================
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)


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
RUTA = RAIZ / "datos" / "transito_aire_junio2024.csv"
GRAFICOS = RAIZ / "graficos"
if not RUTA.exists():
    raise FileNotFoundError(f"Falta {RUTA}. Correr primero datos/obtener_datos.py")


def mostrar(fig, nombre):
    """Guarda el gráfico en graficos/ y lo muestra."""
    fig.savefig(GRAFICOS / f"{nombre}.png", dpi=150, bbox_inches="tight")
    plt.show()


COL_TRANSITO = "#2E86AB"
COL_NO2      = "#7B4B2A"
COL_PM25     = "#D4A373"
COL_OSCURO   = "#5C3A21"

# ---- La tabla original -------------------------------------------------------
aire = pd.read_csv(RUTA, parse_dates=["hora"])

# ---- Variables nuevas --------------------------------------------------------
datos = aire.copy()
datos["h"] = datos["hora"].dt.hour
datos["tipo_dia"] = np.where(datos["hora"].dt.dayofweek >= 5,
                             "fin de semana", "lunes a viernes")
datos["hora_pico"] = np.where(datos["h"].isin([7, 8, 9, 17, 18, 19]),
                              "hora pico", "resto")
datos["franja"] = pd.cut(datos["h"], bins=[-1, 5, 11, 17, 23],
                         labels=["madrugada", "mañana", "tarde", "noche"])
datos["transito_rel"] = datos["transito"] / datos.groupby("estacion")["transito"].transform("mean")
datos["transito_miles"] = datos["transito"] / 1000
datos["log_pm25"] = np.log(datos["pm25"])

# ---- Promedios por estación y franja (para el ejercicio 3) -------------------
por_franja = (datos.groupby(["estacion", "franja"], observed=True)
                   [["transito", "transito_rel", "no2", "pm25"]]
                   .mean()
                   .reset_index())
print(por_franja.round(1))

ESTACIONES = sorted(datos["estacion"].unique())

# ---- Tres Cruces, solo las horas con NO2 (para los ejercicios 4 a 7) ---------
tc = datos[(datos["estacion"] == "Tres Cruces") & datos["no2"].notna()].copy()

modelo_tc3 = smf.ols("no2 ~ transito_miles + pm25", data=tc).fit()
print(modelo_tc3.params)
print("R² modelo_tc3:", round(modelo_tc3.rsquared, 3))


#%%
# =============================================================================
# EJERCICIO 1. FALTANTES
# =============================================================================
columnas = ["transito", "no2", "pm25", "franja", "tipo_dia", "transito_rel", "log_pm25"]
faltantes = datos[columnas].isna().groupby(datos["estacion"]).sum()
print(faltantes)

# ¿Coinciden los faltantes de log_pm25 con los de pm25, fila por fila?
print("Mismas filas:", (datos["log_pm25"].isna() == datos["pm25"].isna()).all())

# Respuesta. La única variable nueva con faltantes es log_pm25, y le faltan
# exactamente las mismas filas que a pm25 (0 en Curva de Maronias, 144 en
# Museo Romántico y 326 en Tres Cruces). Si falta el PM2.5 no hay de qué sacar
# el logaritmo: una variable calculada hereda los faltantes de la variable de
# la que sale. No aparecen faltantes nuevos por log(0) porque en esta tabla
# ningún PM2.5 vale 0. El NO2 falta mucho más (1.214 horas): Museo Romántico
# no lo mide y en las otras dos hay huecos.


#%%
# =============================================================================
# EJERCICIO 2. ¿ESTÁ BIEN DEFINIDA LA HORA PICO?
# =============================================================================
print(datos["hora_pico"].value_counts())

semana_tc = datos[(datos["estacion"] == "Tres Cruces") &
                  (datos["tipo_dia"] == "lunes a viernes")]
promedio_hora = semana_tc.groupby("h")["transito"].mean()
print(promedio_hora.round(0))

# 1. Mirando el gráfico de la consigna: no, las barras oscuras no son las más
#    altas. Las 7, las 18 y las 19 están marcadas como hora pico y tienen
#    menos tránsito que cualquier hora de 10 a 16. El tránsito no tiene dos
#    picos (mañana y tarde): sube a las 8 y se mantiene alto hasta las 17.
#    Mal clasificadas: 7, 18 y 19 (marcadas y no son altas) y de 10 a 16
#    (son altas y no están marcadas).

# 2. Variable nueva: las horas de 8 a 17. Criterio: cada hora marcada tiene
#    más tránsito promedio que cualquier hora sin marcar (se controla abajo).
datos["transito_alto"] = np.where(datos["h"].between(8, 17),
                                  "tránsito alto", "resto")
print(datos["transito_alto"].value_counts())   # 900 y 1260

# Control: con la nueva definición, cada hora marcada tiene más tránsito que
# cada hora sin marcar
dentro = promedio_hora.loc[8:17]
fuera = promedio_hora.drop(range(8, 18))
print("¿Mínimo adentro > máximo afuera?", dentro.min() > fuera.max(),
      f"({dentro.min():.0f} contra {fuera.max():.0f})")

# 3. El mismo gráfico con la variable nueva
semana_tc = datos[(datos["estacion"] == "Tres Cruces") &
                  (datos["tipo_dia"] == "lunes a viernes")]
por_hora = semana_tc.groupby(["h", "transito_alto"])["transito"].mean().reset_index()
# El diccionario de map() tiene que usar el nombre nuevo de la categoría; si
# quedara "hora pico", ninguna barra se pintaría.
colores = por_hora["transito_alto"].map({"tránsito alto": COL_OSCURO, "resto": "lightgrey"})

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.bar(por_hora["h"], por_hora["transito"], color=colores)
ax.set_title("Tránsito promedio por hora del día, Tres Cruces, lunes a viernes")
ax.set_xlabel("Hora del día (en color: tránsito alto, de 8 a 17)")
ax.set_ylabel("Vehículos por hora")
mostrar(fig, "clase12_ej2_transito_alto")


#%%
# =============================================================================
# EJERCICIO 3. PM2.5 POR FRANJA HORARIA
# =============================================================================
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
for ax, est in zip(axes, ESTACIONES):
    parte = por_franja[por_franja["estacion"] == est]
    ax.bar(parte["franja"].astype(str), parte["pm25"], color=COL_PM25)
    ax.set_title(est)
axes[0].set_ylabel("PM2.5 (µg/m³)")
fig.suptitle("PM2.5 promedio por franja horaria")
fig.tight_layout()
mostrar(fig, "clase12_ej3_pm25_por_franja")

tabla_franja = por_franja.pivot(index="franja", columns="estacion",
                                values=["transito_rel", "pm25"]).round(2)
print(tabla_franja)
print("Franja de máximo PM2.5:\n",
      por_franja.loc[por_franja.groupby("estacion")["pm25"].idxmax(), ["estacion", "franja"]])
print("Franja de máximo tránsito:\n",
      por_franja.loc[por_franja.groupby("estacion")["transito_rel"].idxmax(), ["estacion", "franja"]])

# Respuesta. En las tres estaciones el PM2.5 es máximo de noche (Tres Cruces:
# 31,9 µg/m³ de noche contra 17,2 de tarde), y el tránsito es máximo de
# tarde. No es la misma franja. Coincide con lo que vimos en la clase 10: el
# PM2.5 no sale del caño y se va, se acumula durante el día y llega a su
# máximo varias horas después del tránsito.


#%%
# =============================================================================
# EJERCICIO 4. AGREGAR UNA VARIABLE AL MODELO
# =============================================================================
modelo_tc4 = smf.ols("no2 ~ transito_miles + pm25 + franja", data=tc).fit()
print(modelo_tc4.params.round(2))
print("R² modelo_tc3:", round(modelo_tc3.rsquared, 3))
print("R² modelo_tc4:", round(modelo_tc4.rsquared, 3))

# Respuesta. El R² pasa de 0,47 a 0,49: mejora poco, y a cambio el modelo
# tiene tres coeficientes más. La franja de referencia es la madrugada:
# franja[T.noche] = 6,2 quiere decir que, a igual tránsito y PM2.5, una hora
# de la noche tiene 6,2 µg/m³ más de NO2 que una de la madrugada.


#%%
# =============================================================================
# EJERCICIO 5. UNA VARIABLE BINARIA A PARTIR DEL RESULTADO
# =============================================================================
print(modelo_tc4.summary().tables[1])

tc["noche"] = np.where(tc["franja"] == "noche", 1, 0)
modelo_tc5 = smf.ols("no2 ~ transito_miles + pm25 + noche", data=tc).fit()
print(modelo_tc5.params.round(2))
print("R² modelo_tc5:", round(modelo_tc5.rsquared, 3))
print("p-valor de noche:", round(modelo_tc5.pvalues["noche"], 4))

# Respuesta. La noche suma 3,8 µg/m³ de NO2 frente al resto del día, a igual
# tránsito y PM2.5. El R² queda en 0,48: casi lo mismo que con las tres
# franjas (0,49 en modelo_tc4) y más que sin franja (0,47). Con un solo
# coeficiente en lugar de tres se explica casi lo mismo.
# El 3,8 es menor que el 6,2 del modelo anterior porque compara cosas
# distintas: allá era la noche contra la madrugada; acá, la noche contra
# todo el resto del día junto.
# Cuidado: elegí la noche porque fue la que dio distinta de cero en el
# modelo anterior, con los mismos datos. Eso hace que su p-valor (0,03)
# parezca más firme de lo que es: se buscó y se confirmó con lo mismo.


#%%
# =============================================================================
# EJERCICIO 6. INTERACCIONES
# =============================================================================
COL_FRANJA = {"madrugada": "#0072B2", "mañana": "#E69F00",
              "tarde": "#009E73", "noche": "#CC79A7"}

pendientes = {}
fig, ax = plt.subplots(figsize=(8, 5))
for f in ["madrugada", "mañana", "tarde", "noche"]:
    parte = tc[tc["franja"] == f]
    ax.scatter(parte["transito_miles"], parte["no2"], s=15, alpha=0.6,
               color=COL_FRANJA[f], label=f)
    pendiente, ordenada = np.polyfit(parte["transito_miles"], parte["no2"], 1)
    pendientes[f] = pendiente
    x = np.array([parte["transito_miles"].min(), parte["transito_miles"].max()])
    ax.plot(x, ordenada + pendiente * x, color=COL_FRANJA[f], linewidth=2)
ax.set_title("Tránsito y NO2 en Tres Cruces, por franja horaria")
ax.set_xlabel("Miles de vehículos por hora")
ax.set_ylabel("NO2 (µg/m³)")
ax.legend()
mostrar(fig, "clase12_ej6_rectas_por_franja")

print("Pendiente de cada recta (µg/m³ por cada mil vehículos):")
print(pd.Series(pendientes).round(2))
mas_empinada = max(pendientes, key=pendientes.get)
print("La más empinada:", mas_empinada)

# 1. La recta más empinada es la de la madrugada (2,9 µg/m³ por cada mil
#    vehículos, contra 0,5 a 1,1 en las otras franjas).
print("Rango de tránsito por franja (miles de vehículos por hora):")
print(tc.groupby("franja", observed=True)["transito_miles"].agg(["min", "max", "size"]).round(1))

# 2. Variable binaria para esa franja
tc["madrugada"] = np.where(tc["franja"] == "madrugada", 1, 0)

# 3. Modelo con interacción: transito_miles * madrugada incluye el tránsito,
#    la madrugada y el producto de los dos (la pendiente extra de la madrugada).
modelo_tc7 = smf.ols("no2 ~ transito_miles * madrugada", data=tc).fit()
print(modelo_tc7.params.round(2))
print("R² modelo_tc7:", round(modelo_tc7.rsquared, 3))

b = modelo_tc7.params
print(f"Pendiente fuera de la madrugada: {b['transito_miles']:.2f} por mil vehículos")
print(f"Pendiente de madrugada: {b['transito_miles'] + b['transito_miles:madrugada']:.2f} por mil vehículos")

# Respuesta. El coeficiente transito_miles:madrugada (2,4) es la pendiente
# extra de la madrugada. Fuera de la madrugada, mil vehículos más se asocian
# con 0,6 µg/m³ más de NO2; de madrugada, con 2,9: casi cinco veces más.
# Cómo lo leo: de madrugada el tránsito va de 5 a 19 mil vehículos por hora,
# y en ese tramo cada auto de más se nota; de día el tránsito ya es alto y el
# NO2 depende más de otras cosas (sol, viento, mezcla del aire). Es una
# lectura posible, no una prueba: la recta de madrugada se apoya en 72 horas
# y en un rango de tránsito corto.
# El R² (0,40) es menor que el de modelo_tc5 (0,48) porque este modelo no
# tiene el PM2.5.


#%%
# =============================================================================
# EJERCICIO 7. ¿QUÉ PASA EN LA TARDE?
# =============================================================================
tarde = tc[tc["franja"] == "tarde"]
COL_TIPO_DIA = {"lunes a viernes": "#0072B2", "fin de semana": "#E69F00"}

fig, ax = plt.subplots(figsize=(8, 5))
for t in ["lunes a viernes", "fin de semana"]:
    parte = tarde[tarde["tipo_dia"] == t]
    ax.scatter(parte["transito_miles"], parte["no2"], s=15, alpha=0.6,
               color=COL_TIPO_DIA[t], label=t)
    pendiente, ordenada = np.polyfit(parte["transito_miles"], parte["no2"], 1)
    x = np.array([parte["transito_miles"].min(), parte["transito_miles"].max()])
    ax.plot(x, ordenada + pendiente * x, color=COL_TIPO_DIA[t], linewidth=2)
ax.set_title("Tránsito y NO2 en Tres Cruces, de tarde, por tipo de día")
ax.set_xlabel("Miles de vehículos por hora")
ax.set_ylabel("NO2 (µg/m³)")
ax.legend()
mostrar(fig, "clase12_ej7_tarde_por_tipo_de_dia")

print(tarde.groupby("tipo_dia")[["transito_miles", "no2"]].agg(["mean", "min", "max", "size"]).round(1))

# Respuesta. Los dos grupos son los días de semana y el fin de semana. De
# lunes a viernes, de tarde, pasan entre 38 y 49 mil vehículos por hora; el
# fin de semana, entre 22 y 39 mil. Casi no se superponen. El NO2 promedio
# también cambia: 50 µg/m³ entre semana y 42 el fin de semana.
# La franja "tarde" junta dos situaciones distintas, y una sola recta para
# las dos mezcla la diferencia entre tipos de día con la relación entre
# tránsito y NO2. Ojo: el fin de semana se apoya en 24 horas con NO2 (en
# junio el NO2 de Tres Cruces solo está en la primera mitad del mes).
