# =============================================================================
# Clase 3 — Práctico: crear un dataset y volver a cargarlo
# Del diccionario al archivo y del archivo al DataFrame: qué sobrevive al viaje
# =============================================================================
# Resolución de los ocho ejercicios de clases/clase3/ejercicios.py del curso,
# más el desafío por equipo (nuestro equipo trabaja con datos experimentales).
#
# Antes de correrlo no hace falta nada: si no existe clases/clase03/datos/,
# el script corre generar_archivos.py (el generador de la clase, sin cambios).
#
# Las respuestas que la consigna pide "en la bitácora" están escritas como
# comentarios debajo de cada ejercicio, con los números que da la corrida.
#
# Cómo correrlo: `python clases/clase03/clase03_cargar_datos.py`, o por celdas
# en VS Code. El ejercicio 5 provoca un error a propósito, pero está dentro de
# un try/except, así que el script sigue.
# =============================================================================

#%%
import runpy
from pathlib import Path

import numpy as np
import pandas as pd

# Ruta de esta carpeta, sin importar desde dónde se corra el script (ej. 6)
try:
    AQUI = Path(__file__).resolve().parent
except NameError:  # al correr celdas sueltas en VS Code
    AQUI = Path.cwd().resolve()
    if not (AQUI / "generar_archivos.py").exists():
        AQUI = AQUI / "clases" / "clase03"

CARPETA = AQUI / "datos"
if not (CARPETA / "equipo_vecino.csv").exists():
    runpy.run_path(str(AQUI / "generar_archivos.py"))


# =============================================================================
# EJERCICIO 1. DEL DICCIONARIO AL DATAFRAME: EL TIPO ES UNA DECISIÓN DE MEDICIÓN
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
df = pd.DataFrame(datos_caja)
print("Tipos por defecto:\n", df.dtypes, "\n")

# Textura: categórica nominal (no hay orden entre suave, rugoso y poroso)
df["textura"] = df["textura"].astype("category")

# Rigidez: categórica ordenada, blando < medio < rígido
TIPO_RIGIDEZ = pd.CategoricalDtype(["blando", "medio", "rígido"], ordered=True)
df["rigidez"] = df["rigidez"].astype(TIPO_RIGIDEZ)

# Certeza: escala de 1 a 5, ordenada. Se declaran las cinco categorías aunque
# el 1 no aparezca en estos diez objetos: la escala existe igual.
TIPO_CERTEZA = pd.CategoricalDtype([1, 2, 3, 4, 5], ordered=True)
df["certeza_observador"] = df["certeza_observador"].astype(TIPO_CERTEZA)

print("Tipos declarados:\n", df.dtypes)
# Ninguna columna puede quedar como texto genérico (en pandas 3 se llama
# "str"; en versiones anteriores, "object")
texto_generico = [c for c in df.columns if str(df[c].dtype) in ("str", "object")]
assert texto_generico == [], f"quedaron como texto: {texto_generico}"
print("¿El orden funciona?", (df["rigidez"] > "blando").sum(), "objetos más rígidos que blando")

# Respuesta (bitácora). En num_aristas, una esfera tiene 0 aristas: ese cero es
# una medición válida, porque la pregunta "¿cuántas aristas tiene?" tiene
# respuesta y es cero. Distinto sería que el observador no haya podido
# contarlas: ahí no hay medición, y anotar 0 mezcla "no tiene" con "no sé".
# Ese caso tendría que ir como faltante (NaN), y el diccionario de variables
# tendría que decir cómo se registra.


# =============================================================================
# EJERCICIO 2. LAS RESTRICCIONES DEL DGP, ESCRITAS COMO CÓDIGO
# =============================================================================
#%%
df_roto = df.copy()
df_roto.loc[0, "peso_estimado_g"] = -12.0
df_roto.loc[3, "num_aristas"] = -1
df_roto.loc[7, "objeto_id"] = 1


def validar(datos):
    """Devuelve una lista de problemas. Lista vacía = dataset válido."""
    problemas = []

    # 1. Peso estrictamente positivo
    malos = datos.loc[~(datos["peso_estimado_g"] > 0), "objeto_id"].tolist()
    if malos:
        problemas.append(f"peso no positivo en objeto(s) {malos}")

    # 2. Certeza entre 1 y 5 (se pasa a número para comparar)
    certeza = pd.to_numeric(datos["certeza_observador"].astype("object"), errors="coerce")
    malos = datos.loc[~certeza.between(1, 5), "objeto_id"].tolist()
    if malos:
        problemas.append(f"certeza fuera de 1-5 en objeto(s) {malos}")

    # 3. num_aristas entero y no negativo
    aristas = datos["num_aristas"]
    no_entero = aristas.notna() & (aristas % 1 != 0)
    negativo = aristas < 0
    malos = datos.loc[no_entero | negativo, "objeto_id"].tolist()
    if malos:
        problemas.append(f"num_aristas negativo o no entero en objeto(s) {malos}")

    # 4. objeto_id sin repetidos
    repetidos = datos.loc[datos["objeto_id"].duplicated(keep=False), "objeto_id"]
    if len(repetidos):
        problemas.append(f"objeto_id repetido: {sorted(set(repetidos))}")

    return problemas


print("df       ->", validar(df))
print("df_roto  ->", validar(df_roto))
assert validar(df) == []
assert len(validar(df_roto)) == 3


# =============================================================================
# EJERCICIO 3. EL DICCIONARIO DE VARIABLES
# =============================================================================
#%%
diccionario = pd.DataFrame([
    {"variable": "objeto_id", "tipo": "identificador", "unidad": "—",
     "instrumento": "número asignado al objeto antes de la dinámica",
     "rango_valido": "entero de 1 a 10, sin repetidos", "faltante": "no admite"},
    {"variable": "textura", "tipo": "categórica nominal", "unidad": "—",
     "instrumento": "tacto del observador, sin ver el objeto",
     "rango_valido": "suave, rugoso, poroso", "faltante": "vacío"},
    {"variable": "rigidez", "tipo": "categórica ordinal", "unidad": "—",
     "instrumento": "presión con los dedos, sin ver el objeto",
     "rango_valido": "blando < medio < rígido", "faltante": "vacío"},
    {"variable": "num_aristas", "tipo": "numérica discreta", "unidad": "aristas",
     "instrumento": "conteo táctil del observador",
     "rango_valido": "entero >= 0; 0 = no tiene aristas",
     "faltante": "vacío si no se pudo contar (nunca 0)"},
    {"variable": "peso_estimado_g", "tipo": "numérica continua", "unidad": "gramos",
     "instrumento": "estimación táctil del observador, 15 s, sin ver el objeto",
     "rango_valido": "> 0", "faltante": "vacío"},
    {"variable": "certeza_observador", "tipo": "categórica ordinal", "unidad": "—",
     "instrumento": "autoevaluación del observador al terminar",
     "rango_valido": "1 a 5", "faltante": "vacío"},
])
diccionario.to_csv(CARPETA / "diccionario_variables.csv", index=False, encoding="utf-8")
print(diccionario.to_string(index=False))

# Respuesta (bitácora). La columna "faltante" habría evitado el problema del 0
# en num_aristas: obliga a decir de antemano cómo se anota "no se pudo contar",
# y así el 0 queda reservado para "no tiene aristas". También ayuda
# "rango_valido", que dice qué significa el 0.


# =============================================================================
# EJERCICIO 4. EL VIAJE DE IDA Y VUELTA: QUÉ SE PIERDE AL GUARDAR
# =============================================================================
#%%
# --- ida, como en la consigna (falta index=False) ---
df.to_csv(CARPETA / "caja_negra_mio.csv")
df_leido = pd.read_csv(CARPETA / "caja_negra_mio.csv")

print("columnas originales:", list(df.columns))
print("columnas releídas  :", list(df_leido.columns))
print("rigidez original :", df["rigidez"].dtype)
print("rigidez releída  :", df_leido["rigidez"].dtype)

# Las dos pérdidas:
#  1. Apareció la columna "Unnamed: 0": es el índice de pandas (0 a 9), que
#     to_csv escribe por defecto y read_csv lee como un dato más.
#  2. rigidez volvió como texto: el CSV es texto plano y no guarda que era
#     categórica ni el orden blando < medio < rígido.

# --- corrección: escribir sin índice y reconstruir los tipos al leer ---
df.to_csv(CARPETA / "caja_negra_mio.csv", index=False)
df_leido = pd.read_csv(
    CARPETA / "caja_negra_mio.csv",
    dtype={"textura": "category", "rigidez": TIPO_RIGIDEZ,
           "certeza_observador": TIPO_CERTEZA},
)
print("\nCon index=False y dtype al leer:")
print("columnas iguales:", list(df_leido.columns) == list(df.columns))
print("tipos iguales   :", (df_leido.dtypes == df.dtypes).all())

# --- el mismo viaje con parquet ---
try:
    df.to_parquet(CARPETA / "caja_negra_mio.parquet")
    df_parquet = pd.read_parquet(CARPETA / "caja_negra_mio.parquet")
    print("\nTipo de cada columna después de pasar por parquet:")
    for col in df.columns:
        igual = "igual" if df_parquet[col].dtype == df[col].dtype else "CAMBIÓ"
        print(f"  {col:20s} {str(df_parquet[col].dtype):10s} {igual}")
    print("Orden de rigidez:", list(df_parquet["rigidez"].cat.categories),
          "| ordenada:", df_parquet["rigidez"].cat.ordered)
except ImportError:
    print("\nPara parquet hace falta instalar pyarrow: pip install pyarrow")
# Parquet guarda el tipo de cada columna junto con los datos: textura y
# rigidez vuelven como categóricas, y rigidez conserva el orden, sin declarar
# nada. Pero no es perfecto: certeza_observador (categórica ordenada con
# categorías numéricas 1 a 5) volvió como int64 en mi prueba (pandas 3.0 y
# pyarrow 26). Igual hay que verificar los tipos después de leer.


# =============================================================================
# EJERCICIO 5. EL CSV QUE ARMÓ EXCEL
# =============================================================================
#%%
RUTA = CARPETA / "caja_negra_excel.csv"

# --- intento ingenuo: registrar el error ---
try:
    malo = pd.read_csv(RUTA)
    print(malo.head())
except Exception as e:
    print(type(e).__name__, ":", e)
# Error que da (pandas 3.0):
#   UnicodeDecodeError : 'utf-8' codec can't decode byte 0xed in position 107:
#   invalid continuation byte
# 0xed es la "í" de "rígido" escrita en latin-1. read_csv espera UTF-8.
#
# Abierto con un editor de texto se ve: separador de columnas ";", decimal
# "," (45,0) y la "í" como un símbolo raro. Es lo que exporta Excel en español.

# --- lectura correcta ---
bueno = pd.read_csv(RUTA, sep=";", decimal=",", encoding="latin-1")
print(bueno.dtypes)
assert pd.api.types.is_float_dtype(bueno["peso_estimado_g"])
print("Peso medio:", bueno["peso_estimado_g"].mean())

# --- qué pasa si se omite decimal="," ---
sin_decimal = pd.read_csv(RUTA, sep=";", encoding="latin-1")
print("\nSin decimal=',', el peso queda como:", sin_decimal["peso_estimado_g"].dtype)
print(sin_decimal["peso_estimado_g"].head(3).tolist())
try:
    sin_decimal["peso_estimado_g"].mean()
except TypeError as e:
    print("Y la media falla recién acá:", type(e).__name__)

# Respuesta. Con sep=";" pero sin decimal="," el código NO falla al leer:
# sigue adelante con el peso como texto ("45,0"). El error aparece más tarde,
# al calcular, o peor, no aparece si solo se cuenta o se ordena (ordenar texto
# pone "120,5" antes que "15,0"). Por eso hay que verificar el tipo después
# de leer.


# =============================================================================
# EJERCICIO 6. DÓNDE ESTÁ EL ARCHIVO
# =============================================================================
#%%
print("Directorio de trabajo:", Path.cwd())

# La ruta se arma desde la carpeta del script (AQUI, definida arriba), no
# desde el directorio de trabajo: así funciona se corra desde donde se corra.
ruta = CARPETA / "caja_negra.csv"
if not ruta.exists():
    raise FileNotFoundError(
        f"No encuentro {ruta}. Correr primero clases/clase03/generar_archivos.py"
    )
df_base = pd.read_csv(ruta)
print(df_base.shape)

# Respuesta. Una ruta como C:/Users/jodavyt/Documents/GitHub/.../caja_negra.csv
# solo existe en la computadora de quien la escribió: tiene su nombre de
# usuario, su disco y su forma de ordenar carpetas. En otra máquina da
# FileNotFoundError. Además deja a la vista datos de esa persona. En equipo
# las rutas tienen que ser relativas a la carpeta del proyecto.


# =============================================================================
# EJERCICIO 7. EL -99 QUE SE LLEVA PUESTA LA MEDIA
# =============================================================================
#%%
RUTA = CARPETA / "caja_negra_faltantes.csv"

ingenuo = pd.read_csv(RUTA)
media_ingenua = ingenuo["peso_estimado_g"].mean()
print("Media ingenua:", round(media_ingenua, 2))

# Valores únicos de cada columna
for col in ingenuo.columns:
    valores = ingenuo[col].unique()
    print(f"{col:20s}", sorted(valores, key=lambda v: (pd.isna(v), str(v))))

# Las cuatro formas de codificar un faltante:
#   -99   en peso_estimado_g    -> read_csv NO lo reconoce: lo toma como número
#   "s/d" en textura            -> NO lo reconoce: lo toma como una categoría más
#   "NA"  en num_aristas        -> SÍ lo reconoce (está en su lista por defecto)
#   vacío en certeza_observador -> SÍ lo reconoce
print("\nFaltantes que read_csv reconoce solo:\n", ingenuo.isna().sum())

# --- releer declarando los cuatro códigos ---
declarado = pd.read_csv(RUTA, na_values=["-99", "s/d", "NA", ""])
media_declarada = declarado["peso_estimado_g"].mean()
print("\nMedia ingenua  :", round(media_ingenua, 2))
print("Media declarada:", round(media_declarada, 2))
print("\nFaltantes por columna:\n", declarado.isna().sum())

# Respuesta. La diferencia entre las dos medias (de 48,5 g a 85,3 g) no es un
# problema de programación: el código hace bien la cuenta que se le pide. Es
# un problema de medición: el -99 no es un peso, es la forma en que alguien
# anotó "no lo medí". Si esa convención no está documentada, el número entra
# como dato y arrastra la media. Se arregla con el diccionario de variables.


# =============================================================================
# EJERCICIO 8. LECTURA A CIEGAS DEL ARCHIVO DEL EQUIPO VECINO
# =============================================================================
#%%
RUTA = CARPETA / "equipo_vecino.csv"

vecino = pd.read_csv(RUTA, encoding="utf-8")
print(vecino.shape)
print(vecino.dtypes, "\n")
print(vecino.head())
print(vecino.isna().sum())
print(vecino.describe(include="all"))

print("\nPrimeras líneas del archivo tal cual:")
for linea in open(RUTA, encoding="utf-8").read().splitlines()[:4]:
    print("   ", linea)

print("\nMonto que cargó pandas para '1.295' y para '980':")
print(vecino["Monto UYU"].head(8).tolist())
# El archivo dice 1.295 (mil doscientos noventa y cinco, con punto de miles).
# pandas lo lee como 1.295 (uno coma dos), porque para él el punto es decimal.
# 980 se lee bien, porque no tiene separador. Resultado: en una misma columna
# hay montos divididos por mil y montos correctos, y nada avisa.

# --- correcciones ---
vecino = pd.read_csv(RUTA, encoding="utf-8", thousands=".")           # 1. miles
vecino.columns = (vecino.columns.str.strip().str.lower()               # 3. nombres
                  .str.replace(" ", "_"))
vecino["fecha_operacion"] = pd.to_datetime(vecino["fecha_operacion"],  # 2. fecha
                                           format="%d/%m/%Y")
vecino["sucursal"] = vecino["sucursal"].str.strip().astype("category")  # 4. espacios

print("\nDespués de corregir:")
print(vecino.dtypes)
print(vecino.describe())
print("Sucursales:", list(vecino["sucursal"].cat.categories))
assert vecino["monto_uyu"].min() > 100, "algún monto quedó dividido por mil"

# Respuesta (bitácora). Tres afirmaciones sobre el proceso que generó el
# archivo:
#  1. Es un registro transaccional con una fila por operación: el ID no se
#     repite y hay una operación por día, del 02/03 al 10/04 de 2026.
#  2. Se escribió con convenciones uruguayas (fecha dd/mm/aaaa, punto de
#     miles) y probablemente a mano o desde una planilla: los espacios
#     sobrantes en "Centro " y " Carrasco" no los pone un sistema.
#  3. Los montos están en pesos uruguayos y son enteros: se redondearon antes
#     de exportar, o el sistema no registra centésimos.
# Pregunta para el equipo que lo produjo: ¿una sola operación por día es real,
# o el archivo es un resumen diario de varias operaciones?


# =============================================================================
# DESAFÍO POR EQUIPO — Datos experimentales
# =============================================================================
# Punto de quiebre esperado: la asignación a tratamiento y el momento de
# medición.
#
# Nuestro trabajo de equipo es un experimento: una encuesta previa de rasgos
# y después un juego de decisiones. Armo un dataset mínimo de diez
# participantes con la estructura del experimento. LOS VALORES SON INVENTADOS:
# sirven para probar el viaje al CSV, no son respuestas reales.
#%%
experimento = pd.DataFrame({
    "codigo": [f"P{i:02d}" for i in range(1, 11)],
    "rol": ["dictador", "receptor"] * 5,                      # asignación
    "momento": pd.to_datetime(["2026-09-24 10:05", "2026-09-24 10:05",
                               "2026-09-24 10:12", "2026-09-24 10:12",
                               "2026-09-24 10:20", "2026-09-24 10:20",
                               "2026-09-24 10:31", "2026-09-24 10:31",
                               "2026-09-24 10:40", "2026-09-24 10:40"]),
    "generosidad": [4, 3, 5, 2, 3, 4, 2, 5, 4, 3],             # escala 1-5, previa
    "monto_entregado": [40, np.nan, 50, np.nan, 20, np.nan, 10, np.nan, 30, np.nan],
})
experimento["rol"] = experimento["rol"].astype(
    pd.CategoricalDtype(["dictador", "receptor"]))
experimento["generosidad"] = experimento["generosidad"].astype(TIPO_CERTEZA)

dicc_experimento = pd.DataFrame([
    {"variable": "codigo", "tipo": "identificador", "unidad": "—",
     "instrumento": "alias que elige el participante", "faltante": "no admite"},
    {"variable": "rol", "tipo": "categórica nominal (asignación)", "unidad": "—",
     "instrumento": "sorteo antes del juego", "faltante": "no admite"},
    {"variable": "momento", "tipo": "fecha y hora", "unidad": "hora local de Montevideo",
     "instrumento": "hora de inicio del juego", "faltante": "no admite"},
    {"variable": "generosidad", "tipo": "categórica ordinal", "unidad": "escala 1-5",
     "instrumento": "encuesta previa, antes de conocer el juego", "faltante": "vacío"},
    {"variable": "monto_entregado", "tipo": "numérica discreta", "unidad": "fichas de 100",
     "instrumento": "decisión en el juego",
     "faltante": "vacío = no aplica (los receptores no deciden)"},
])

experimento.to_csv(CARPETA / "experimento_minimo.csv", index=False, encoding="utf-8")
dicc_experimento.to_csv(CARPETA / "experimento_diccionario.csv", index=False, encoding="utf-8")

# Vuelta, como en una sesión nueva: solo con lo que dice el diccionario
releido = pd.read_csv(CARPETA / "experimento_minimo.csv")
print("Tipos al releer sin declarar nada:\n", releido.dtypes)

releido = pd.read_csv(
    CARPETA / "experimento_minimo.csv",
    parse_dates=["momento"],
    dtype={"rol": pd.CategoricalDtype(["dictador", "receptor"]),
           "generosidad": TIPO_CERTEZA},
)
print("\n¿Se perdió algo en el viaje?")
print("  tipos iguales  :", (releido.dtypes == experimento.dtypes).all())
print("  valores iguales:", releido.equals(experimento))

# Punto de quiebre encontrado:
#  1. El rol (la asignación a tratamiento) vuelve como texto y la hora como
#     texto sin zona horaria. Si no se declara, el CSV no distingue "rol" de
#     cualquier otra columna de texto.
#  2. El vacío de monto_entregado significa "no aplica" (el receptor no
#     decide), pero en el CSV es igual a "no respondió". Solo el diccionario
#     lo distingue.
#  3. generosidad se midió ANTES del juego. Si se repitiera la encuesta
#     después, el CSV no dice cuál es cuál: el momento de medición tiene que
#     ser una columna, o ir en el nombre de la variable.
