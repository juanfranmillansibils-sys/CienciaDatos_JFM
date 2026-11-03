# =============================================================================
# Clase 11 — Inteligencia artificial para leer documentos
# Mandar la foto de un ticket a Gemini y recibir una tabla
# =============================================================================
# Basado en clases/clase11/clase_ia/leer_ticket.py del curso. Cambios:
#   - la foto y la tabla de salida van en datos/ (no se suben a GitHub);
#   - la clave se lee de datos/clave_gemini.txt o de la variable de entorno
#     GEMINI_API_KEY, y nunca se escribe en el código;
#   - al final se verifica la respuesta contra lo que dice el ticket, porque
#     la salida de un modelo hay que controlarla por otra vía.
#
# Antes de correrlo:
#   1. python datos/obtener_datos.py   (baja la foto del ticket de la clase)
#   2. Sacar una clave gratis en https://aistudio.google.com ("Get API key")
#      y guardarla en datos/clave_gemini.txt. El .gitignore ignora clave_*.txt.
#   3. pip install requests pandas
#
# Sin clave, el script hace la parte local (pasar la foto a base64 y armar la
# solicitud) y se detiene con un aviso antes de enviarla.
# =============================================================================

#%%
import base64
import os
from io import StringIO
from pathlib import Path

import pandas as pd
import requests


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


# -----------------------------------------------------------------------------
# 1. Datos de la solicitud
# -----------------------------------------------------------------------------
DATOS = raiz_proyecto() / "datos"
FOTO = DATOS / "ticket.jpg"
ARCHIVO_CLAVE = DATOS / "clave_gemini.txt"
SALIDA = DATOS / "ticket_gemini.csv"
TIPO = "image/jpeg"            # si la foto es .png, poner "image/png"
MODELO = "gemini-3.5-flash-lite"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent"

INSTRUCCION = """Transcribí los ítems de este ticket de compra.
Respondé solo con una tabla CSV, sin ningún otro texto, con dos columnas:
descripcion,monto
- monto con punto decimal y sin separador de miles (1.250,00 se escribe 1250.00)
- no incluyas SUBTOTAL, IVA, TOTAL, EFECTIVO, CAMBIO ni TARJETA
- si algo no se puede leer, dejalo vacío; no lo inventes"""

if not FOTO.exists():
    raise FileNotFoundError(f"Falta {FOTO}. Correr primero datos/obtener_datos.py")

#%%
# -----------------------------------------------------------------------------
# 2. Pasar la foto a base64 (texto), porque el JSON solo admite texto
# -----------------------------------------------------------------------------
bytes_foto = FOTO.read_bytes()
imagen_base64 = base64.b64encode(bytes_foto).decode("ascii")

print("La foto pesa", len(bytes_foto), "bytes")
print("En base64 son", len(imagen_base64), "caracteres y empieza con", imagen_base64[:4])
# Control de la cuenta: base64 escribe 4 caracteres por cada 3 bytes, y
# redondea hacia arriba al múltiplo de 4.
esperado = 4 * ((len(bytes_foto) + 2) // 3)
assert len(imagen_base64) == esperado
print("Cuenta verificada: 4 × techo(bytes / 3) =", esperado)
# "/9j/" al principio es la marca de un JPEG (los bytes FF D8 FF en base64).

#%%
# -----------------------------------------------------------------------------
# 3. Armar el cuerpo de la solicitud (un diccionario que se envía como JSON)
# -----------------------------------------------------------------------------
cuerpo = {
    "contents": [{
        "parts": [
            {"text": INSTRUCCION},
            {"inline_data": {"mime_type": TIPO, "data": imagen_base64}},
        ]
    }],
    "generationConfig": {"temperature": 0},   # 0 = la respuesta más estable
}

# -----------------------------------------------------------------------------
# 4. La clave: de un archivo ignorado por Git o de una variable de entorno
# -----------------------------------------------------------------------------
CLAVE = os.environ.get("GEMINI_API_KEY", "")
if not CLAVE and ARCHIVO_CLAVE.exists():
    CLAVE = ARCHIVO_CLAVE.read_text(encoding="utf-8").strip()
if not CLAVE:
    raise SystemExit(
        "No hay clave: guardarla en datos/clave_gemini.txt (ver el encabezado). "
        "Hasta acá el script corrió bien; falta solo el envío."
    )

#%%
# -----------------------------------------------------------------------------
# 5. Enviar la solicitud: método POST, con la clave en un encabezado
# -----------------------------------------------------------------------------
respuesta = requests.post(URL, headers={"x-goog-api-key": CLAVE}, json=cuerpo, timeout=120)

print("Código de estado:", respuesta.status_code)   # 200 = todo bien
if respuesta.status_code != 200:
    print(respuesta.text)                          # el mensaje de error del servidor
    raise SystemExit("La solicitud falló: revisar el código de estado")

#%%
# -----------------------------------------------------------------------------
# 6. Leer la respuesta
# -----------------------------------------------------------------------------
datos = respuesta.json()                                   # JSON -> diccionario
texto = datos["candidates"][0]["content"]["parts"][0]["text"]
print(texto)

uso = datos["usageMetadata"]
print("Tokens de entrada (imagen + instrucción):", uso["promptTokenCount"])
print("Tokens de salida (la respuesta):", uso["candidatesTokenCount"])

# -----------------------------------------------------------------------------
# 7. Guardar la tabla y abrirla con pandas
# -----------------------------------------------------------------------------
texto = texto.replace("```csv", "").replace("```", "").strip()   # por si la envuelve
SALIDA.write_text(texto + "\n", encoding="utf-8")
tabla = pd.read_csv(StringIO(texto))
print(tabla)

#%%
# -----------------------------------------------------------------------------
# 8. Verificar la salida del modelo contra el ticket
# -----------------------------------------------------------------------------
# Lo que dice el ticket de la clase, leído a mano: dos ítems (leche 18,00 y
# pan 32,00) y TOTAL $ 50,00. El "Pago total" de 48,36 no es la suma de los
# ítems: es el total menos el descuento de IVA de la ley 19.210 por pagar con
# tarjeta (-1,64). Si el modelo devolviera 48,36 como total, estaría mal.
TOTAL_IMPRESO = 50.00
ITEMS_ESPERADOS = 2

problemas = []
if list(tabla.columns) != ["descripcion", "monto"]:
    problemas.append(f"columnas inesperadas: {list(tabla.columns)}")
if len(tabla) != ITEMS_ESPERADOS:
    problemas.append(f"devolvió {len(tabla)} ítems y el ticket tiene {ITEMS_ESPERADOS}")
if tabla["monto"].isna().any():
    problemas.append("hay montos vacíos (el modelo no pudo leerlos)")
suma = round(tabla["monto"].sum(), 2)
if suma != TOTAL_IMPRESO:
    problemas.append(f"la suma de los ítems da {suma} y el TOTAL impreso es {TOTAL_IMPRESO}")

print("Suma de los ítems:", suma, "| TOTAL impreso:", TOTAL_IMPRESO)
print("Verificación:", "sin problemas" if not problemas else problemas)
