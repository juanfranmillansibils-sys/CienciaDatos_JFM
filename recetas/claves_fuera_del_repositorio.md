# Claves fuera del repositorio

**Problema.** Para usar una API (Gemini, en la clase 11) hace falta una
clave. Si queda escrita en el código y se sube a GitHub, cualquiera que vea
el repositorio la puede usar.

**Receta.** La clave va en un archivo que Git ignora, o en una variable de
entorno. El código la lee, nunca la contiene.

```python
import os
from pathlib import Path

clave = os.environ.get("GEMINI_API_KEY", "")
archivo = Path("datos/clave_gemini.txt")
if not clave and archivo.exists():
    clave = archivo.read_text(encoding="utf-8").strip()
if not clave:
    raise SystemExit("Falta la clave: guardarla en datos/clave_gemini.txt")
```

Y en `.gitignore`:

```
clave_*.txt
.env
```

**Antes de confirmar.** En GitHub Desktop, la pestaña *Changes* muestra todo
lo que se va a subir. Si aparece un archivo con una clave, no hay que
confirmarlo: hay que agregarlo al `.gitignore`.

**Si ya se subió.** Borrarlo en una confirmación nueva **no alcanza**: la
confirmación anterior sigue en el historial y la clave se puede ver ahí. Lo
que hay que hacer es **anular la clave** en el sitio que la dio y sacar una
nueva.
