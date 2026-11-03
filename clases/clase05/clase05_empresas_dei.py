# =============================================================================
# Clase 5 — Carga de datos y primera inspección
# Directorio de Empresas Industriales (DEI), MIEM
# =============================================================================
# Parte de la plantilla de la clase 5 ("carga de datos en python 2.py") y la
# aplica a otro archivo: el Directorio de Empresas Industriales.
#
# Qué hace:
#   1. Carga datos/empresasdei_20230330.csv.
#   2. Revisa estructura, identificador (RUT), faltantes y duplicados.
#   3. Cuenta empresas por departamento y por actividad (CIIU).
#
# Datos: se bajan con datos/obtener_datos.py (ver datos/fuentes.md).
# El archivo trae nombres de personas, teléfonos y correos de empresas
# unipersonales: por eso no se sube al repositorio.
#
# Cómo correrlo: desde la terminal, `python clases/clase05/clase05_empresas_dei.py`,
# o por celdas en VS Code (Shift+Enter en cada "# %%").
# =============================================================================

# %%
from pathlib import Path

import pandas as pd


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


# 1. Ruta relativa a la raíz del repositorio: funciona en cualquier computadora
ruta_csv = raiz_proyecto() / "datos" / "empresasdei_20230330.csv"

# 2. Verificar que el archivo existe antes de cargarlo
if not ruta_csv.exists():
    raise FileNotFoundError(
        f"No se encontró {ruta_csv}. Correr primero datos/obtener_datos.py"
    )

# 3. Cargar el archivo CSV
df = pd.read_csv(ruta_csv)

# %%
# 4. Inspección inicial
print(f"--- Archivo cargado: {ruta_csv.name} ---")
df.info()  # info() ya imprime; envolverlo en print() agrega un "None"
print("\nPrimeras 5 filas:")
print(df.head())

# %%
# 4.1 Dimensiones
print("\n" + "=" * 60)
print("ESTRUCTURA DEL DATASET")
print("=" * 60)
print(f"Dimensiones: {df.shape}")

# 4.2 Identificador: el RUT debería ser único
print("\n" + "=" * 60)
print("IDENTIFICADOR (RUT)")
print("=" * 60)
print(f"RUT distintos: {df['RUT'].nunique()}")
print(f"Total de registros: {len(df)}")
print("¿El RUT identifica cada fila?", df["RUT"].nunique() == len(df))

# %%
# 4.3 Datos faltantes
print("\n" + "=" * 60)
print("DATOS FALTANTES")
print("=" * 60)
print(df.isna().sum())
print("\nFalsos nulos (cadenas vacías):")
print((df == "").sum().sum())
# El archivo marca lo que falta con "S/D" (sin dato). read_csv no lo reconoce
# como faltante, así que hay que contarlo aparte.
print("\nCeldas con 'S/D' por columna:")
print((df == "S/D").sum())

# %%
# 4.4 Duplicados
print("\n" + "=" * 60)
print("REGISTROS DUPLICADOS")
print("=" * 60)
print(f"Filas duplicadas: {df.duplicated().sum()}")
print(f"RUT duplicados: {df['RUT'].duplicated().sum()}")

# %%
# 5. Limpieza mínima antes de contar
# Al contar por departamento aparecen "SAN JOSÉ" y "TACUAREMBÓ" dos veces cada
# uno. No es un error de tipeo visible: una de las versiones trae un carácter
# invisible al final (un espacio duro \xa0 o un carácter de control \x90).
# Para pandas son textos distintos, y la cuenta se parte en dos.
depto_crudo = df["Departamento Estab. Principal"]
print("Departamentos distintos, tal cual vienen:", depto_crudo.nunique())

columnas_texto = df.select_dtypes(include=["object", "string"]).columns
limpio = df.copy()
for col in columnas_texto:
    limpio[col] = (
        limpio[col]
        .str.replace(r"[\x00-\x1f\x7f-\x9f]", "", regex=True)  # caracteres de control
        .str.strip()  # espacios al borde, incluido el espacio duro \xa0
    )

# "S/D" (sin dato) es un faltante disfrazado: se pasa a NaN para que cuente
limpio = limpio.replace("S/D", pd.NA)

print("Departamentos distintos, después de limpiar:",
      limpio["Departamento Estab. Principal"].nunique())

# %%
# 6. Empresas por departamento (con la tabla limpia)
print("\n" + "=" * 60)
print("EMPRESAS POR DEPARTAMENTO")
print("=" * 60)
print(limpio["Departamento Estab. Principal"].value_counts(dropna=False))

# 7. Actividades CIIU más frecuentes
print("\n" + "=" * 60)
print("ACTIVIDADES INDUSTRIALES (CIIU) MÁS FRECUENTES")
print("=" * 60)
print(limpio["Descripción Código CIIU principal"].value_counts().head(10))

# %%
# Resumen
print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)
print(f"Total de empresas: {len(limpio)}")
print(f"Departamentos (sin contar los faltantes): "
      f"{limpio['Departamento Estab. Principal'].nunique()}")
print(f"Empresas sin departamento registrado: "
      f"{limpio['Departamento Estab. Principal'].isna().sum()}")
print(f"Actividades CIIU distintas: "
      f"{limpio['Descripción Código CIIU principal'].nunique()}")
