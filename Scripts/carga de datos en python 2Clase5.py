# %%
from pathlib import Path
import pandas as pd

# 1. Definir la ruta raíz del proyecto o del directorio de trabajo actual
BASE_DIR = Path.cwd()

# 2. Construir la ruta relativa de forma segura utilizando el operador /
# Estructura esperada: tu_proyecto/data/raw/datos.csv
archivo = "empresasdei_20230330.csv"
ruta_csv = BASE_DIR / "clases" / "clase4" / archivo

ruta_csv = BASE_DIR / "Data" / archivo

# 3. Verificar que el archivo realmente existe antes de cargarlo
if not ruta_csv.exists():
    raise FileNotFoundError(f"No se encontró el archivo en: {ruta_csv}")

# 4. Cargar el archivo CSV
df = pd.read_csv(ruta_csv)

# 5. Inspección inicial de los datos
print(f"--- Archivo cargado exitosamente desde: {ruta_csv.name} ---")
print(df.info())
print("\nPrimeras 5 filas:")
print(df.head())

# 5.1. Dimensiones y estructura
print("\n" + "="*60)
print("ESTRUCTURA DEL DATASET")
print("="*60)
print(f"Dimensiones: {df.shape}")

# 5.2. Identificar Primary Key (RUT debería ser único)
print("\n" + "="*60)
print("IDENTIFICAR PRIMARY KEY")
print("="*60)
print(f"Registros únicos por RUT: {df['RUT'].nunique()}")
print(f"Total de registros: {len(df)}")

# 5.3 Datos faltantes
print("\n" + "="*60)
print("DATOS FALTANTES (NA)")
print("="*60)
print(df.isnull().sum())
print("\nFalsos nulos (cadenas vacías):")
print((df == "").sum())

# 5.4 Duplicados
print("\n" + "="*60)
print("REGISTROS DUPLICADOS")
print("="*60)
print(f"Filas duplicadas: {df.duplicated().sum()}")
print(f"RUTs duplicados: {df['RUT'].duplicated().sum()}")

## 5.5. Primeras filas
print("\nPrimeras 5 filas:")
print(df.head())

# ====== ANÁLISIS ADICIONAL ======

# 6. Empresas por departamento
print("\n" + "="*60)
print("EMPRESAS POR DEPARTAMENTO")
print("="*60)
empresas_por_depto = df["Departamento Estab. Principal"].value_counts()
print(empresas_por_depto)

# 7. Actividades CIIU más frecuentes
print("\n" + "="*60)
print("ACTIVIDADES INDUSTRIALES (CIIU) MÁS FRECUENTES")
print("="*60)
ciiu_frecuencia = df["Descripción Código CIIU principal"].value_counts().head(10)
print(ciiu_frecuencia)

# Resumen
print("\n" + "="*60)
print("RESUMEN")
print("="*60)
print(f"Total de empresas: {len(df)}")
print(f"Total de departamentos: {df['Departamento Estab. Principal'].nunique()}")
print(f"Total de actividades CIIU: {df['Descripción Código CIIU principal'].nunique()}")
