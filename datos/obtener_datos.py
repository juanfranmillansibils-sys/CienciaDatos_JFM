# =============================================================================
# Obtener los datos del repositorio
# =============================================================================
# Los datos crudos no se suben a GitHub: se sube este script, que los baja de
# su fuente original y los deja en esta misma carpeta (datos/).
#
# Cómo correrlo, desde la raíz del repositorio:
#     python datos/obtener_datos.py
#
# - Si un archivo ya está en datos/, no lo vuelve a bajar.
# - Al terminar muestra cuántas filas tiene cada CSV, para comparar con
#   datos/fuentes.md. Si no coinciden, la fuente cambió.
# - El conteo vehicular de junio pesa unos 330 MB: tarda.
#
# Origen, licencia y cantidad de registros de cada archivo: datos/fuentes.md
# =============================================================================

import sys
import urllib.request
from datetime import date
from pathlib import Path

CARPETA = Path(__file__).resolve().parent

CKAN = "https://ckan-data.montevideo.gub.uy/dataset"
CATALOGO = "https://catalogodatos.gub.uy/dataset"
CURSO = "https://raw.githubusercontent.com/DavytJ/Introduccion-a-la-ciencia-de-datos/main"

# nombre del archivo -> (dirección de descarga, filas esperadas sin el encabezado)
ARCHIVOS = {
    # Clase 5. Directorio de Empresas Industriales (MIEM)
    "empresasdei_20230330.csv": (
        f"{CATALOGO}/575ccb87-ae74-4dcd-ba4b-cf050bd8e08a/resource/"
        "e56d1949-3e94-42a9-801f-c6d2523b185d/download/empresasdei_20230330.csv",
        1422,
    ),
    # Clase 7. Ozono, enero-abril de 2024 (Intendencia de Montevideo)
    "o3_01_2024_04_2024.csv": (
        f"{CKAN}/70a1a63d-4157-43c0-9ae6-00fc14dae29a/resource/"
        "a97d7ffb-be66-4438-8de8-fa4c7cacf66c/download/o3_01_2024_04_2024.csv",
        291926,
    ),
    # Clase 10. NO2, mayo-agosto de 2024 (Intendencia de Montevideo)
    "no2_05_2024_08_2024.csv": (
        f"{CKAN}/bd346fc1-3251-48de-b36a-e57596b250c7/resource/"
        "cd458e42-a2ee-4874-b566-87a53b944ed8/download/no2_05_2024_08_2024.csv",
        347952,
    ),
    # Clase 10. PM2.5, mayo-agosto de 2024 (Intendencia de Montevideo)
    "pm_2_5_05_2024_08_2024.csv": (
        f"{CKAN}/b9904d06-d466-4a2a-b582-ec01c6700a3c/resource/"
        "26cfdc3e-355f-4315-9d1e-2fc33949a9b9/download/pm_2_5_05_2024_08_2024.csv",
        433338,
    ),
    # Clase 10. Conteo vehicular, junio de 2024 (Centro de Gestión de Movilidad)
    "autoscope_06_2024_volumen.csv": (
        f"{CKAN}/a2b2243b-358f-4f03-b7bc-0a32c25ed10c/resource/"
        "90b6b287-bd28-447b-9cd9-fd19d36e4433/download/autoscope_06_2024_volumen.csv",
        3688891,
    ),
    # Clase 12. Tabla tránsito-aire por hora, preparada por la cátedra
    "transito_aire_junio2024.csv": (
        f"{CURSO}/clases/clase10/transito_aire_junio2024.csv",
        2160,
    ),
    # Clase 11. Foto del ticket usada en clase (no tiene datos personales)
    "ticket.jpg": (
        f"{CURSO}/clases/clase11/clase_ia/ticket.jpg",
        None,
    ),
}


def bajar(url, destino):
    """Baja url a destino mostrando el avance. Escribe primero a un temporal."""
    temporal = destino.with_suffix(destino.suffix + ".parcial")

    def avance(bloques, tam_bloque, total):
        if total > 0:
            pct = min(100, bloques * tam_bloque * 100 // total)
            print(f"\r    {pct:3d} %", end="", flush=True)

    urllib.request.urlretrieve(url, temporal, reporthook=avance)
    print()
    temporal.replace(destino)


def contar_filas(ruta):
    """Filas de datos (sin el encabezado). Cuenta líneas: no lee el CSV entero."""
    with open(ruta, "rb") as f:
        return sum(1 for _ in f) - 1


def main():
    print(f"Carpeta de datos: {CARPETA}")
    print(f"Fecha de obtención: {date.today():%d/%m/%Y}\n")
    problemas = []
    for nombre, (url, esperadas) in ARCHIVOS.items():
        destino = CARPETA / nombre
        if destino.exists():
            print(f"[ya está] {nombre}")
        else:
            print(f"[bajando] {nombre}")
            try:
                bajar(url, destino)
            except Exception as e:  # sin internet, dirección cambiada, etc.
                print(f"    no se pudo bajar: {e}")
                problemas.append(nombre)
                continue
        if esperadas is not None:
            filas = contar_filas(destino)
            marca = "ok" if filas == esperadas else f"ESPERABA {esperadas}"
            print(f"    {filas} filas ({marca})")
            if filas != esperadas:
                problemas.append(nombre)

    if problemas:
        print("\nRevisar:", ", ".join(problemas))
        print("Ver direcciones y conteos en datos/fuentes.md")
        sys.exit(1)
    print("\nTodo listo.")


if __name__ == "__main__":
    main()
