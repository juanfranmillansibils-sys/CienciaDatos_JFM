# Leer un CSV difícil

**Problema.** Un CSV es texto: no dice en qué codificación está, qué separa
las columnas, cómo se escriben los decimales ni cómo se marca lo que falta.
Si se adivina mal, a veces da error y a veces no, que es peor.

**Receta.** Mirar el archivo como texto antes de leerlo, y declarar todo.

```python
# 1. Mirar las primeras líneas tal cual (no con Excel)
with open(ruta, encoding="utf-8", errors="replace") as f:
    for _ in range(3):
        print(f.readline())

# 2. Leer declarando lo que se vio
df = pd.read_csv(
    ruta,
    encoding="latin-1",      # si aparece "Ã³" o UnicodeDecodeError
    sep=";",                 # si las columnas están separadas por punto y coma
    decimal=",",             # si los decimales van con coma: 45,0
    thousands=".",           # si los miles van con punto: 1.295
    na_values=["-99", "s/d", "S/D"],   # faltantes disfrazados
)

# 3. Verificar que cada columna quedó con el tipo que tiene que tener
print(df.dtypes)
```

**Qué mirar en cada caso.**

| Síntoma | Causa | Argumento |
|---|---|---|
| `UnicodeDecodeError` | el archivo no está en UTF-8 | `encoding="latin-1"` |
| «ColÃ³n», «MaroÃ±as» | archivo UTF-8 leído como latin-1 | `encoding="utf-8"` |
| una sola columna con `;` adentro | separador punto y coma | `sep=";"` |
| peso como texto: `"45,0"` | coma decimal | `decimal=","` |
| `1.295` leído como 1,295 | punto de miles | `thousands="."` |
| media rarísima | `-99` como dato | `na_values=["-99"]` |

**El caso peligroso.** Con `sep=";"` pero sin `decimal=","` no hay error: el
peso queda como texto y recién falla al calcular. Con `thousands` mal puesto
ni siquiera falla: en la clase 3 la media del monto daba 169,28 en vez de
1.471,50. Siempre `df.dtypes` y `df.describe()` después de leer.

Ver `clases/clase03/clase03_cargar_datos.py`, ejercicios 5, 7 y 8.
