# Rutas que funcionan en otra computadora

**Problema.** `pd.read_csv(r"C:\Users\<mi usuario>\Documents\...\datos.csv")`
funciona en mi computadora y en ninguna otra. Además muestra mi nombre de
usuario.

**Receta.** Armar la ruta desde la raíz del repositorio, no desde mi disco.

```python
from pathlib import Path

def raiz_proyecto():
    try:
        actual = Path(__file__).resolve().parent   # al correr el script entero
    except NameError:
        actual = Path.cwd().resolve()              # al correr celdas en VS Code
    for carpeta in [actual, *actual.parents]:
        if (carpeta / ".git").exists():
            return carpeta
    raise FileNotFoundError("No encontré la raíz del repositorio")

ruta = raiz_proyecto() / "datos" / "o3_01_2024_04_2024.csv"
if not ruta.exists():
    raise FileNotFoundError(f"No está {ruta}: correr datos/obtener_datos.py")
```

**Por qué así.**

- `Path.cwd()` es la carpeta desde donde se corre, que cambia según cómo se
  abra VS Code. `Path(__file__)` es la carpeta del script, que no cambia.
- En las celdas de VS Code `__file__` no existe: por eso el `try`.
- Verificar con `.exists()` antes de leer da un mensaje que dice qué hacer,
  en vez de un `FileNotFoundError` con una ruta larga.
- La barra `/` de `pathlib` arma la ruta bien en Windows y en Mac.

Usada en todos los scripts de `clases/`. La versión con prueba está en
`funciones/utilidades.py`.
