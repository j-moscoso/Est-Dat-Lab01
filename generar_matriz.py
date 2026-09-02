"""
Laboratorio 01
"""

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