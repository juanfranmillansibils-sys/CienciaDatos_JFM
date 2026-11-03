# Correr los scripts en VS Code (Windows)

**Instalar lo necesario, una sola vez.** En la terminal de VS Code
(Terminal → New Terminal), parada en la carpeta del repositorio:

```
py -3.13 -m pip install -r requirements.txt ipykernel
```

`py -3.13 -m pip` instala en el mismo Python que usa VS Code. Si se escribe
solo `pip`, puede instalar en otro Python, o Windows puede decir que no lo
reconoce. `ipykernel` es lo que permite correr celdas.

**Correr por celdas (recomendado).** Cada `# %%` en el script es una celda.
Cursor adentro y **Shift+Enter**: se corre esa celda y el resultado aparece
en la ventana interactiva, al costado.

- Hay que correrlas **de arriba hacia abajo**. Si se corre una celda del
  medio sola, aparece `NameError: name 'df' is not defined`: la variable se
  crea en una celda anterior que todavía no se corrió.

**Correr el script entero.** En la terminal:

```
py -3.13 clases/clase07/clase07_ozono_max_8h.py
```

- Cada `plt.show()` abre una ventana con el gráfico y **el script se frena
  hasta que se cierra**. No está colgado: está esperando.

**Si no deja correr nada.** VS Code abre las carpetas nuevas en *modo
restringido*. Arriba aparece un aviso: elegir que se confía en la carpeta
(Trust) y vuelve a funcionar.

**Orden para este repositorio.**

1. `py -3.13 datos/obtener_datos.py` (baja los datos, una vez)
2. `py -3.13 funciones/test_utilidades.py` (comprueba las funciones)
3. Cualquier script de `clases/`
