# Encontrar faltantes disfrazados

**Problema.** `df.isna().sum()` solo cuenta lo que pandas reconoce como
faltante: celdas vacías, `NA`, `NaN`, `null`. Un `-99`, un `S/D` o un texto con
un carácter invisible pasan como dato válido.

**Receta.**

```python
# 1. Mirar los valores únicos de cada columna (los raros saltan a la vista)
for col in df.columns:
    print(col, sorted(df[col].unique(), key=lambda v: (pd.isna(v), str(v)))[:20])

# 2. Contar los códigos sospechosos
print((df == "S/D").sum())
print((df == -99).sum())

# 3. Sacar caracteres invisibles de las columnas de texto
for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = (df[col].str.replace(r"[\x00-\x1f\x7f-\x9f]", "", regex=True)
                      .str.strip())

# 4. Convertir los códigos en faltantes de verdad
df = df.replace({"S/D": pd.NA, -99: pd.NA})
```

**Casos reales del curso.**

- Clase 3: el `-99` en el peso bajaba la media de 85,3 g a 48,5 g.
- Clase 5: el Directorio de Empresas Industriales marca lo que falta con
  `S/D` (267 empresas sin departamento), y dos departamentos traían un
  carácter invisible al final que los contaba dos veces.

**Pregunta que hay que hacerse.** ¿Ese código quiere decir «no se midió» o
«no aplica»? No es lo mismo, y el diccionario de variables tiene que decirlo
(ver el desafío de la clase 3).
