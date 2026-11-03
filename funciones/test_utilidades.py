"""
Casos de prueba de funciones/utilidades.py.

Cómo correrlo, desde la raíz del repositorio:
    python funciones/test_utilidades.py

Si todo está bien, imprime "OK" por cada función. Si algo falla, se detiene
en el assert que no se cumple.
"""

import numpy as np
import pandas as pd

from utilidades import (arreglar_mojibake, dist_km, limpiar_invisibles,
                        media_movil_completa, numero_uy, rachas, raiz_proyecto,
                        unir_y_contar)


def test_raiz_proyecto():
    raiz = raiz_proyecto(__file__ if "__file__" in globals() else None)
    assert (raiz / "funciones" / "utilidades.py").exists()
    print("OK raiz_proyecto:", raiz.name)


def test_arreglar_mojibake():
    assert arreglar_mojibake("ColÃ³n") == "Colón"
    assert arreglar_mojibake("Curva de MaroÃ±as") == "Curva de Maroñas"
    assert arreglar_mojibake("Tres Cruces") == "Tres Cruces"   # sano, queda igual
    assert arreglar_mojibake("Colón") == "Colón"               # ya arreglado, igual
    assert arreglar_mojibake(None) is None
    print("OK arreglar_mojibake")


def test_limpiar_invisibles():
    sucia = pd.Series(["SAN JOSÉ", "SAN JOSÉ\x90", "TACUAREMBÓ\xa0", " Centro "])
    limpia = limpiar_invisibles(sucia)
    assert sucia.nunique() == 4
    assert limpia.tolist() == ["SAN JOSÉ", "SAN JOSÉ", "TACUAREMBÓ", "Centro"]
    assert limpia.nunique() == 3
    print("OK limpiar_invisibles")


def test_numero_uy():
    assert numero_uy("1.250,50") == 1250.5
    assert numero_uy("1.295") == 1295.0     # el monto del equipo vecino (clase 3)
    assert numero_uy("980") == 980.0
    assert numero_uy("$ 50,00") == 50.0
    assert np.isnan(numero_uy(""))
    assert np.isnan(numero_uy(None))
    print("OK numero_uy")


def test_dist_km():
    # Un grado de latitud son unos 111,2 km
    assert abs(dist_km(-34.0, -56.0, -35.0, -56.0) - 111.19) < 0.01
    # Mismo punto: cero
    assert dist_km(-34.9, -56.16, -34.9, -56.16) == 0
    # Tres Cruces a Curva de Maroñas (coordenadas de los archivos de aire)
    d = dist_km(-34.894293, -56.164671, -34.858960, -56.133249)
    assert 4.5 < d < 5.0, d
    print(f"OK dist_km (Tres Cruces a Curva de Maroñas: {d:.2f} km)")


def test_media_movil_completa():
    horas = pd.date_range("2024-01-01 00:00", periods=10, freq="h")
    serie = pd.Series(10.0, index=horas)
    # Sin huecos: a partir de la octava hora la media es 10
    mm = media_movil_completa(serie)
    assert mm.isna().sum() == 7 and mm.dropna().eq(10).all()
    # Con un hueco: se saca la hora 3. Una media "ingenua" sobre las filas que
    # quedan seguiría dando números; la completa da NaN en toda ventana que
    # incluya la hora que falta.
    con_hueco = serie.drop(horas[3])
    ingenua = con_hueco.rolling(8, min_periods=8).mean()
    completa = media_movil_completa(con_hueco)
    assert ingenua.notna().sum() == 2
    assert completa.notna().sum() == 0
    print("OK media_movil_completa")


def test_rachas():
    faltante = [False, True, True, True, False, True, False, False]
    r = rachas(faltante)
    assert r["largo"].tolist() == [1, 3, 1, 1, 2]
    assert r.loc[r["valor"], "largo"].tolist() == [3, 1]   # dos rachas de faltantes
    assert len(rachas([])) == 0
    print("OK rachas")


def test_unir_y_contar():
    vuelos = pd.DataFrame({"vuelo": [1, 2, 3], "origin": ["EWR", "EWR", "JFK"]})
    clima = pd.DataFrame({"origin": ["EWR", "EWR", "JFK"], "hour": [5, 6, 5]})
    resultado = unir_y_contar(vuelos, clima, on="origin", how="left")
    assert len(resultado) == 5        # la clave se repite: filas de más
    print("OK unir_y_contar")


if __name__ == "__main__":
    test_raiz_proyecto()
    test_arreglar_mojibake()
    test_limpiar_invisibles()
    test_numero_uy()
    test_dist_km()
    test_media_movil_completa()
    test_rachas()
    test_unir_y_contar()
    print("\nTodas las pruebas pasaron.")
