
# Juan Manuel Moscoso Torres - CC 1042151495
## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| `generar_matriz.py` | Código que construye la matriz y la escribe en disco de forma optimizada. |
| `README.md` | Este archivo, con la explicación del código y los comandos usados para visualizar la matriz. |
| `matriz_optimizada.txt` | *(generado al ejecutar el script — no incluido en el repo por su tamaño, ver sección de Reproducción más abajo)* |

## `generar_matriz.py` — Generación de la matriz

```python
# Definición de las dimensiones de la matriz (100.000 x 100.000)
FILAS = 100_000
COLUMNAS = 100_000

# Se utiliza la multiplicación de cadenas para crear arreglos horizontales instantáneos.
# El carácter '\n' (salto de línea) actúa como delimitador vertical de cada fila.
fila0 = ("0" * COLUMNAS) + "\n"
fila1 = ("1" * COLUMNAS) + "\n"

# Se abre el archivo en modo escritura ('w') con codificación UTF-8.
# Se itera FILAS // 2 veces (50.000 iteraciones) escribiendo un par de filas
# en cada ciclo para maximizar el rendimiento del búfer de I/O.
with open("matriz_optimizada.txt", "w", encoding="utf-8") as f:
    for _ in range(FILAS // 2):
        f.write(fila0)
        f.write(fila1)
```

### ¿Qué hace?

- **Construcción de las filas una sola vez:** como la matriz solo va a tener "0" y "1" que se repiten, `fila0` y `fila1` se construyen una única vez antes del ciclo, no en cada iteración. Para no reconstruir una cadena de 100.000 caracteres 50.000 veces.
- **Concatenación de strings con `*`:** `"0" * COLUMNAS` repite el carácter "0" y "1" las 100.000 veces necesarias y arma la cadena completa de una sola vez.
- **Apertura del archivo con `"w"` y `encoding="utf-8"`:** el modo `"w"` abre el archivo para escritura (y lo crea si no existe, o lo sobrescribe si ya existía). Uso `encoding="utf-8"` para dejar explícito con qué codificación se guardan los caracteres.
- **Reutilización de las variables:** Dentro del bucle, ya no construyo nada, solo escribo las dos variables que ya tengo listas (`fila0` y `fila1`) directamente al archivo con `f.write()`, cada línea se entrega al buffer de escritura del sistema operativo tal cual. Esto lo repito 50.000 veces (`FILAS // 2`) para completar las 100.000 filas.

**Resultado:** un archivo .txt de ~9.5 GB (100.000 filas × 100.001 bytes por fila, incluyendo el salto de línea) generado en segundos.

## Visualización de la matriz (comandos de consola)

No se puede imprimir la matriz completa en pantalla porque tardaría  días. En su lugar, muestro la matriz mediante la primera fila completa y la primera columna completa, además de una verificación de sus dimensiones. Estos comandos se ejecutan directamente en la terminal, en el mismo directorio donde está `matriz_optimizada.txt`:

```bash
echo "=== PRIMERA FILA COMPLETA (100.000 caracteres) ===" && head -n 1 matriz_optimizada.txt && echo -e "\n=== PRIMERA COLUMNA COMPLETA (100.000 elementos) ===" && cut -c 1 matriz_optimizada.txt
```

### ¿Qué hace?

- **`echo "..."`:** Imprime encabezados en la terminal para organizar la salida visual.
- **`head -n 1 matriz_optimizada.txt`:** Muestra la primera fila completa en pantalla con sus 100.000 ceros contiguos.
- **`echo -e "\n..."`:** Agrega una línea en blanco e imprime el segundo encabezado.
- **`cut -c 1 matriz_optimizada.txt`:** Recorre las 100.000 filas del archivo y recorta exclusivamente el carácter número 1 (columna 0) de cada una, imprimiendo la primera columna de arriba a abajo.
- **`&&`:** Ejecuta el siguiente comando únicamente si el anterior finaliza sin errores.

```bash
echo "--- COLUMNAS EN LA PRIMERA FILA ---" && head -n 1 matriz_optimizada.txt | tr -d '\r\n' | wc -c && echo "--- TOTAL DE FILAS (PRIMERA COLUMNA) ---" && wc -l < matriz_optimizada.txt
```

### ¿Qué hace?

- **`echo "..."`:** Imprime encabezados en la terminal para organizar la salida visual.
- **`head -n 1 matriz_optimizada.txt`:** Extrae únicamente la primera fila (línea 0) del archivo .
- **`| tr -d '\r\n'`:** Pasa la línea extraída al comando tr, eliminando el carácter invisible de salto de línea (\n) para asegurar que solo se cuenten los dígitos reales.
- **`| wc -c`:** Cuenta los bytes/caracteres resultantes. Retorna: 100000, que sería el numero de columnas en la primera fila.
- **`wc -l < matriz_optimizada.txt`:** Cuenta el número total de saltos de línea en el archivo de forma directa, validando el total de filas verticales. Retorna: 100000.
- **`&&`:** Ejecuta el siguiente comando únicamente si el anterior finaliza sin errores.


## Reproducción (En consola de Linux)

```bash
# 1. Generar la matriz (necesita como 9.5 GB libres en disco)
python3 generar_matriz.py
```
```bash
# 2. Revisar la matriz (parado en la misma carpeta del archivo)
echo "=== PRIMERA FILA COMPLETA (100.000 caracteres) ===" && head -n 1 matriz_optimizada.txt && echo -e "\n=== PRIMERA COLUMNA COMPLETA (100.000 elementos) ===" && cut -c 1 matriz_optimizada.txt
```
```bash
echo "--- COLUMNAS EN LA PRIMERA FILA ---" && head -n 1 matriz_optimizada.txt | tr -d '\r\n' | wc -c && echo "--- TOTAL DE FILAS (PRIMERA COLUMNA) ---" && wc -l < matriz_optimizada.txt
```
