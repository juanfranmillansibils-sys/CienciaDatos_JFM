# =============================================================================
# Clase 14 — Ejercicios 58 a 61: unir tablas
# =============================================================================
# Los ejercicios son en papel (clases/clase14/ejercicios_58_61_papel.pdf del
# curso). Las respuestas razonadas están en clase14_unir_tablas.md. Este
# script arma las mismas tablas chicas en pandas y comprueba cada respuesta:
# si alguna estuviera mal, un assert lo avisa.
#
# Cómo correrlo: `python clases/clase14/clase14_unir_tablas.py`
# =============================================================================

#%%
import numpy as np
import pandas as pd

vuelos = pd.DataFrame({
    "vuelo": [1, 2, 3, 4, 5],
    "carrier": ["UA", "AA", "B6", "UA", "DL"],
    "dest": ["IAH", "MIA", "SJU", "ORD", "ATL"],
    "dep_delay": [2, -4, 33, 0, -6],
})
aerolineas = pd.DataFrame({
    "carrier": ["UA", "AA", "B6"],
    "name": ["United Air Lines Inc.", "American Airlines Inc.", "JetBlue Airways"],
})
aeropuertos = pd.DataFrame({
    "faa": ["IAH", "MIA", "ORD", "ATL"],
    "name": ["George Bush Intercontinental", "Miami Intl",
             "Chicago Ohare Intl", "Hartsfield Jackson Atlanta Intl"],
})

#%%
# --- Ejercicio 58: completar una unión ----------------------------------------
izq = vuelos.merge(aerolineas, on="carrier", how="left")
print(izq[["vuelo", "carrier", "name"]])
assert izq.loc[izq["vuelo"] == 5, "name"].isna().all()       # a) DL queda vacío

inner = vuelos.merge(aerolineas, on="carrier", how="inner")
assert len(inner) == 4                                         # b) 4 filas
assert set(vuelos["vuelo"]) - set(inner["vuelo"]) == {5}       # c) se pierde el 5

#%%
# --- Ejercicio 59: clave con nombres distintos --------------------------------
izq = vuelos.merge(aeropuertos, left_on="dest", right_on="faa", how="left")
print(izq[["vuelo", "dest", "name"]])
assert izq.loc[izq["vuelo"] == 3, "name"].isna().all()        # b) SJU queda vacío
inner = vuelos.merge(aeropuertos, left_on="dest", right_on="faa", how="inner")
assert len(inner) == 4                                         # c) 4 filas

# Para ir más lejos: dos columnas name. pandas las llama name_x y name_y;
# mejor ponerles nombre al unir.
doble = (vuelos.merge(aerolineas, on="carrier", how="left")
               .merge(aeropuertos, left_on="dest", right_on="faa", how="left",
                      suffixes=("_aerolinea", "_aeropuerto")))
print(doble.columns.tolist())
assert {"name_aerolinea", "name_aeropuerto"} <= set(doble.columns)

#%%
# --- Ejercicio 60: una clave incompleta ---------------------------------------
vuelos60 = pd.DataFrame({"vuelo": [1, 2, 3],
                         "origin": ["EWR", "EWR", "JFK"],
                         "hour": [5, 6, 5]})
clima = pd.DataFrame({"origin": ["EWR", "EWR", "JFK", "JFK"],
                      "hour": [5, 6, 5, 6],
                      "visib": [10, 2, 10, 0.5]})

a = vuelos60.merge(clima, on=["origin", "hour"], how="left")
assert len(a) == 3                                             # a) 3 filas
b = vuelos60.merge(clima, on="origin", how="left", suffixes=("_vuelos", "_clima"))
assert len(b) == 6                                             # b) 6 filas
print(b)                                                       # c) la tabla
# d) sirve la (a): cada vuelo queda con la visibilidad de su hora de salida
assert a.set_index("vuelo")["visib"].to_dict() == {1: 10, 2: 2, 3: 10}

# Para ir más lejos: sin la fila JFK, 5
clima_sin = clima.drop(index=2)
a2 = vuelos60.merge(clima_sin, on=["origin", "hour"], how="left")
i2 = vuelos60.merge(clima_sin, on=["origin", "hour"], how="inner")
assert len(a2) == 3 and len(i2) == 2
assert np.isnan(a2.loc[a2["vuelo"] == 3, "visib"].item())     # visib vacío

#%%
# --- Ejercicio 61: leer el número de filas ------------------------------------
n_vuelos = 27_004
filas = {"A": 27_004, "B": 26_324, "C": 646_428, "D": 27_004}
clasificacion = {k: ("igual" if v == n_vuelos else "menos" if v < n_vuelos else "más")
                 for k, v in filas.items()}
print(clasificacion)
assert clasificacion == {"A": "igual", "B": "menos", "C": "más", "D": "igual"}
print("b) vuelos perdidos en B:", n_vuelos - filas["B"])              # 680
print("c) apariciones por vuelo en C:", round(filas["C"] / n_vuelos, 2))  # 23,94
print("d) filas de la unión interna en D:", n_vuelos - 4_479)          # 22.525
