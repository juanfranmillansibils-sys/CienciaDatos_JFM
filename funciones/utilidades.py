"""
Utilidades propias: funciones que necesité más de una vez en el curso.

Cada una tiene su caso de prueba en funciones/test_utilidades.py.
Para usarlas desde otro script:

    import sys
    sys.path.append("funciones")      # desde la raíz del repositorio
    from utilidades import numero_uy, unir_y_contar
"""

from pathlib import Path

import numpy as np
import pandas as pd


def raiz_proyecto(desde=None):
    """Devuelve la carpeta raíz del repositorio (la que tiene .git).

    Sube desde `desde` (o desde la carpeta actual) hasta encontrarla. Sirve
    para armar rutas que funcionen en cualquier computadora.
    """
    actual = Path(desde or Path.cwd()).resolve()
    for carpeta in [actual, *actual.parents]:
        if (carpeta / ".git").exists() or (carpeta / "datos" / "fuentes.md").exists():
            return carpeta
    raise FileNotFoundError(f"No encontré la raíz del repositorio subiendo desde {actual}")


def arreglar_mojibake(texto):
    """Repara un texto UTF-8 que se leyó como latin-1: "ColÃ³n" -> "Colón".

    Si el texto no tiene ese problema, lo devuelve igual.
    """
    if not isinstance(texto, str):
        return texto
    try:
        return texto.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return texto


def limpiar_invisibles(serie):
    """Saca caracteres de control y espacios al borde (incluido el espacio duro).

    Ejemplo real (Directorio de Empresas Industriales): "SAN JOSÉ\\x90" y
    "SAN JOSÉ" se ven iguales pero cuentan como dos departamentos.
    """
    return (serie.astype("string")
                 .str.replace(r"[\x00-\x1f\x7f-\x9f]", "", regex=True)
                 .str.strip())


def numero_uy(texto):
    """Convierte un número escrito a la uruguaya en float.

    "1.250,50" -> 1250.5   (punto de miles, coma decimal)
    "980"      -> 980.0
    "" o None  -> NaN
    """
    if texto is None or (isinstance(texto, float) and np.isnan(texto)):
        return np.nan
    texto = str(texto).strip().replace("$", "").replace(" ", "")
    if texto == "":
        return np.nan
    return float(texto.replace(".", "").replace(",", "."))


def dist_km(lat1, lon1, lat2, lon2):
    """Distancia en km sobre la esfera terrestre (fórmula del haversine)."""
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    a = (np.sin((lat2 - lat1) / 2) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def media_movil_completa(serie, ventana=8):
    """Media móvil sobre una serie horaria, sin saltar huecos.

    Primero completa la grilla horaria con NaN (una media móvil cuenta
    posiciones, no horas) y después exige la ventana entera: si falta una
    hora, el resultado es NaN. `serie` tiene que tener índice de fechas.
    """
    grilla = pd.date_range(serie.index.min(), serie.index.max(), freq="h")
    completa = serie.reindex(grilla)
    return completa.rolling(ventana, min_periods=ventana).mean()


def rachas(serie_booleana):
    """Agrupa valores consecutivos iguales: una fila por racha, con su largo.

    Equivale a rle() de R. Útil para ver si los faltantes de un sensor son
    sueltos (ruido) o en bloque (sensor apagado).
    """
    valores = pd.Series(serie_booleana).to_numpy()
    if len(valores) == 0:
        return pd.DataFrame({"valor": [], "largo": []})
    id_racha = np.concatenate([[0], np.cumsum(valores[1:] != valores[:-1])])
    return (pd.DataFrame({"valor": valores, "id": id_racha})
              .groupby("id")
              .agg(valor=("valor", "first"), largo=("valor", "size"))
              .reset_index(drop=True))


def unir_y_contar(izquierda, derecha, **kwargs):
    """Hace un merge e informa cuántas filas había antes y cuántas quedaron.

    Avisa si una unión izquierda devolvió más filas que la tabla de la
    izquierda: eso quiere decir que la clave se repite en la derecha.
    """
    resultado = izquierda.merge(derecha, **kwargs)
    tipo = kwargs.get("how", "inner")
    print(f"Unión {tipo}: {len(izquierda)} filas a la izquierda -> {len(resultado)} filas")
    if tipo == "left" and len(resultado) > len(izquierda):
        print("  ¡Ojo! Hay filas de más: la clave se repite en la tabla de la derecha.")
    return resultado
