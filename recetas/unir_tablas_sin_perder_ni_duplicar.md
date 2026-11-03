# Unir tablas sin perder ni duplicar filas

**Problema.** Una unión puede perder filas (si la clave no encuentra pareja) o
multiplicarlas (si la clave se repite en la otra tabla), y pandas no avisa en
ninguno de los dos casos.

**Receta.** Contar filas antes y después, y pedirle a pandas que controle.

```python
antes = len(vuelos)
resultado = vuelos.merge(
    aerolineas,
    on="carrier",
    how="left",                 # quedan todos los vuelos
    validate="many_to_one",     # error si carrier se repite en aerolineas
    indicator=True,             # agrega _merge: both / left_only
)
print(antes, "->", len(resultado))
print(resultado["_merge"].value_counts())   # left_only = sin pareja
```

**Variantes.**

- Clave con nombres distintos: `left_on="dest", right_on="faa"`.
- Dos columnas con el mismo nombre: `suffixes=("_aerolinea", "_aeropuerto")`
  en lugar de `name_x` y `name_y`.
- Clave de varias columnas: `on=["origin", "hour"]`. Si falta una (por
  ejemplo `hour`), cada vuelo aparece una vez por hora del día.

**Cómo leer el resultado.**

| Filas después | Unión izquierda | Unión interna |
|---|---|---|
| iguales | todo bien | todas encontraron pareja |
| menos | imposible | se perdieron las que no tienen pareja |
| más | la clave se repite a la derecha | la clave se repite |

Ver `clases/clase14/clase14_unir_tablas.md`. La función `unir_y_contar` de
`funciones/utilidades.py` hace el conteo y avisa.
