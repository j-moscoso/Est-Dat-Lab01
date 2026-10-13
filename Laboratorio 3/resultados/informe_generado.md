# Informe de resultados (generado automáticamente)

Generado a partir de `resultados/*.csv`. Todas las cifras de este archivo se calculan de tus datos.

## 1. Diseño experimental

| Parámetro | Valor |
|---|---|
| Estructuras | Lista (búsqueda lineal), ABB sin balanceo, árbol B+ |
| Escenarios | IDs insertados en orden aleatorio / en orden ascendente (mismo conjunto de IDs) |
| Tamaños N | 100, 500, 1.000, 2.000, 5.000, 10.000, 20.000, 50.000, 100.000 |
| M (búsquedas, exp. 1) | 1.000 |
| Repeticiones por configuración | 10 |
| Orden del B+ (máx. claves/nodo) | 64 (búsqueda en nodo con bisect (C)) |
| Límite de N para ABB con IDs ordenados | 20.000 (la construcción es O(N²)) |
| Experimento 2 | N = 10.000, M ∈ {10, 100, 1.000, 10.000} |
| Experimento 3 | B+ con N = 100.000, máx. claves ∈ {4, 8, 16, 32, 64, 128, 256, 512} |
| Semilla base | 2026 |

## 2. Entorno

| Elemento | Valor |
|---|---|
| fecha_hora | 2026-10-12T17:08:36 |
| sistema_operativo | Windows-10-10.0.26300-SP0 |
| python | CPython 3.11.9 |
| cpu | AMD Ryzen 7 5800X 8-Core Processor |
| numpy | 2.4.6 |
| pandas | 3.0.6 |
| matplotlib | 3.11.2 |
| nucleos_fisicos | 8 |
| nucleos_logicos | 16 |
| frecuencia_cpu_mhz | 4200 |
| ram_total_gb | 31.9 |
| conectado_a_corriente | None |

## 3. Resultados (media ± desviación estándar de las repeticiones)

### 3,1 Búsqueda: tiempo total de M búsquedas (s)

| N | Lista · aleat. | ABB · aleat. | B+ · aleat. | Lista · ord. | ABB · ord. | B+ · ord. |
|---|---|---|---|---|---|---|
| 100 | 0,001251 ± 3,1e-05 | 0,000281 ± 1,1e-05 | 0,00031 ± 1,9e-06 | 0,001192 ± 5,2e-05 | 0,001499 ± 4,4e-05 | 0,0003093 ± 1,4e-06 |
| 500 | 0,006361 ± 0,00022 | 0,0003664 ± 1,9e-05 | 0,000337 ± 7,2e-06 | 0,005915 ± 0,00017 | 0,007127 ± 0,0003 | 0,0003326 ± 5,1e-06 |
| 1.000 | 0,01371 ± 0,00036 | 0,0004306 ± 1,5e-05 | 0,0003612 ± 2,5e-06 | 0,01331 ± 0,00051 | 0,01496 ± 0,00046 | 0,000358 ± 2,9e-06 |
| 2.000 | 0,0311 ± 0,0011 | 0,0004756 ± 1,6e-05 | 0,000376 ± 4,6e-06 | 0,03168 ± 0,0011 | 0,03017 ± 0,00092 | 0,0003722 ± 2e-06 |
| 5.000 | 0,08756 ± 0,0044 | 0,0005627 ± 2,5e-05 | 0,0004626 ± 4,3e-06 | 0,1053 ± 0,0022 | 0,0775 ± 0,0024 | 0,0004607 ± 4e-06 |
| 10.000 | 0,1681 ± 0,0043 | 0,0006143 ± 1,4e-05 | 0,000494 ± 4,6e-06 | 0,2202 ± 0,0054 | 0,1718 ± 0,0038 | 0,000492 ± 4,6e-06 |
| 20.000 | 0,3136 ± 0,014 | 0,0006716 ± 2e-05 | 0,000525 ± 2,8e-06 | 0,4656 ± 0,013 | 0,3561 ± 0,0087 | 0,0005289 ± 8,7e-06 |
| 50.000 | 0,7977 ± 0,025 | 0,000751 ± 1,3e-05 | 0,0005726 ± 6,6e-06 | 2,028 ± 0,16 | no medido | 0,0005676 ± 7,8e-06 |
| 100.000 | 4,746 ± 0,4 | 0,0008703 ± 2,2e-05 | 0,0006216 ± 1,3e-05 | 8,738 ± 0,16 | no medido | 0,0006681 ± 1,3e-05 |

**Tiempo medio por búsqueda (µs)**

| N | Lista · aleat. | ABB · aleat. | B+ · aleat. | Lista · ord. | ABB · ord. | B+ · ord. |
|---|---|---|---|---|---|---|
| 100 | 1,251 | 0,281 | 0,31 | 1,192 | 1,499 | 0,3093 |
| 500 | 6,361 | 0,3664 | 0,337 | 5,915 | 7,127 | 0,3326 |
| 1.000 | 13,71 | 0,4306 | 0,3612 | 13,31 | 14,96 | 0,358 |
| 2.000 | 31,1 | 0,4756 | 0,376 | 31,68 | 30,17 | 0,3722 |
| 5.000 | 87,56 | 0,5627 | 0,4626 | 105,3 | 77,5 | 0,4607 |
| 10.000 | 168,1 | 0,6143 | 0,494 | 220,2 | 171,8 | 0,492 |
| 20.000 | 313,6 | 0,6716 | 0,525 | 465,6 | 356,1 | 0,5289 |
| 50.000 | 797,7 | 0,751 | 0,5726 | 2028 | no medido | 0,5676 |
| 100.000 | 4746 | 0,8703 | 0,6216 | 8738 | no medido | 0,6681 |

### 3,2 Construcción: tiempo de insertar los N estudiantes (s)

| N | Lista · aleat. | ABB · aleat. | B+ · aleat. | Lista · ord. | ABB · ord. | B+ · ord. |
|---|---|---|---|---|---|---|
| 100 | 5,847e-06 ± 4,6e-08 | 4,585e-05 ± 2,4e-06 | 4,107e-05 ± 4,1e-07 | 5,894e-06 ± 1,2e-07 | 0,0001891 ± 3,6e-06 | 3,729e-05 ± 4,5e-07 |
| 500 | 2,888e-05 ± 1,3e-06 | 0,0002809 ± 1,3e-05 | 0,0002564 ± 6,4e-06 | 2,815e-05 ± 4,1e-07 | 0,004241 ± 0,0001 | 0,0002231 ± 4,7e-06 |
| 1.000 | 5,764e-05 ± 6,2e-07 | 0,0006427 ± 1,6e-05 | 0,0005643 ± 5,2e-06 | 5,9e-05 ± 2,7e-06 | 0,01743 ± 0,00026 | 0,000491 ± 3e-06 |
| 2.000 | 0,000115 ± 1,4e-06 | 0,001406 ± 2,6e-05 | 0,001192 ± 1,2e-05 | 0,0001154 ± 1,4e-06 | 0,06885 ± 0,0019 | 0,001023 ± 9,7e-06 |
| 5.000 | 0,0002907 ± 1,1e-05 | 0,004048 ± 0,00016 | 0,003335 ± 7,6e-05 | 0,0002921 ± 1,7e-06 | 0,4402 ± 0,0083 | 0,002889 ± 3,7e-05 |
| 10.000 | 0,0005679 ± 1,3e-05 | 0,00883 ± 0,00017 | 0,007259 ± 8,3e-05 | 0,0005903 ± 6,9e-06 | 1,925 ± 0,019 | 0,006261 ± 0,00013 |
| 20.000 | 0,001137 ± 2e-05 | 0,02001 ± 0,00063 | 0,01585 ± 0,00023 | 0,001221 ± 1,7e-05 | 7,933 ± 0,25 | 0,01404 ± 0,00039 |
| 50.000 | 0,002872 ± 3e-05 | 0,05747 ± 0,00086 | 0,04387 ± 0,00088 | 0,003188 ± 7,3e-05 | no medido | 0,03975 ± 0,00051 |
| 100.000 | 0,00597 ± 0,00026 | 0,1452 ± 0,0022 | 0,1064 ± 0,0029 | 0,007195 ± 0,00032 | no medido | 0,08666 ± 0,0015 |

**Tiempo medio por inserción (µs)**

| N | Lista · aleat. | ABB · aleat. | B+ · aleat. | Lista · ord. | ABB · ord. | B+ · ord. |
|---|---|---|---|---|---|---|
| 100 | 0,05847 | 0,4585 | 0,4107 | 0,05894 | 1,891 | 0,3729 |
| 500 | 0,05776 | 0,5618 | 0,5129 | 0,0563 | 8,482 | 0,4462 |
| 1.000 | 0,05764 | 0,6427 | 0,5643 | 0,059 | 17,43 | 0,491 |
| 2.000 | 0,05751 | 0,703 | 0,5961 | 0,05772 | 34,42 | 0,5113 |
| 5.000 | 0,05815 | 0,8096 | 0,6671 | 0,05842 | 88,04 | 0,5777 |
| 10.000 | 0,05679 | 0,883 | 0,7259 | 0,05903 | 192,5 | 0,6261 |
| 20.000 | 0,05686 | 1,001 | 0,7927 | 0,06106 | 396,6 | 0,7018 |
| 50.000 | 0,05743 | 1,149 | 0,8775 | 0,06376 | no medido | 0,7949 |
| 100.000 | 0,0597 | 1,452 | 1,064 | 0,07195 | no medido | 0,8666 |

### 3,3 Listado ordenado por ID (s)

| N | Lista · aleat. | ABB · aleat. | B+ · aleat. | Lista · ord. | ABB · ord. | B+ · ord. |
|---|---|---|---|---|---|---|
| 100 | 3,656e-06 ± 1e-07 | 9,57e-06 ± 6e-07 | 3,81e-07 ± 2,4e-08 | 2,243e-06 ± 3,5e-08 | 2,352e-05 ± 1,3e-06 | 4,181e-07 ± 9,1e-09 |
| 500 | 2,361e-05 ± 1,1e-06 | 4,594e-05 ± 2,1e-06 | 2,247e-06 ± 1e-07 | 1,188e-05 ± 3,3e-07 | 0,0001189 ± 3e-06 | 2,505e-06 ± 5,1e-08 |
| 1.000 | 5,945e-05 ± 2,4e-06 | 9,178e-05 ± 4,1e-06 | 4,584e-06 ± 2,3e-07 | 2,76e-05 ± 1,2e-06 | 0,0002345 ± 1,2e-05 | 4,904e-06 ± 9,3e-08 |
| 2.000 | 0,0001863 ± 3,4e-06 | 0,0001868 ± 6,3e-06 | 9,57e-06 ± 3,9e-07 | 6,908e-05 ± 1,5e-06 | 0,0004901 ± 2,8e-05 | 1,085e-05 ± 1,8e-07 |
| 5.000 | 0,0005475 ± 1,3e-05 | 0,0004688 ± 1,3e-05 | 2,379e-05 ± 7,5e-07 | 0,000212 ± 1,7e-06 | 0,001169 ± 3,9e-05 | 2,612e-05 ± 9,7e-07 |
| 10.000 | 0,001194 ± 1,5e-05 | 0,0009324 ± 3,4e-05 | 4,38e-05 ± 7,4e-07 | 0,0004537 ± 7,7e-06 | 0,002445 ± 1,2e-05 | 4,749e-05 ± 1,3e-06 |
| 20.000 | 0,002609 ± 5,1e-05 | 0,001873 ± 4,1e-05 | 9,366e-05 ± 3,7e-06 | 0,0009647 ± 1,2e-05 | 0,005026 ± 6,3e-05 | 9,772e-05 ± 2,7e-06 |
| 50.000 | 0,007671 ± 0,00022 | 0,005111 ± 0,00013 | 0,0002895 ± 8,2e-06 | 0,004732 ± 0,00037 | no medido | 0,0003093 ± 5,1e-06 |
| 100.000 | 0,02658 ± 0,00085 | 0,01511 ± 0,00061 | 0,0007781 ± 3,5e-05 | 0,01993 ± 0,00039 | no medido | 0,0007871 ± 3,1e-05 |

### 3,4 Altura de los árboles (niveles; media ± desv.)

| N | ABB · aleat. | B+ · aleat. | ABB · ord. | B+ · ord. |
|---|---|---|---|---|
| 100 | 13,8 ± 1,0 | 2,0 ± 0,0 | 100,0 ± 0,0 | 2,0 ± 0,0 |
| 500 | 18,8 ± 1,2 | 2,0 ± 0,0 | 500,0 ± 0,0 | 2,0 ± 0,0 |
| 1.000 | 21,8 ± 1,8 | 2,0 ± 0,0 | 1000,0 ± 0,0 | 2,0 ± 0,0 |
| 2.000 | 24,1 ± 1,5 | 2,0 ± 0,0 | 2000,0 ± 0,0 | 2,0 ± 0,0 |
| 5.000 | 29,5 ± 2,5 | 3,0 ± 0,0 | 5000,0 ± 0,0 | 3,0 ± 0,0 |
| 10.000 | 31,0 ± 2,4 | 3,0 ± 0,0 | 10000,0 ± 0,0 | 3,0 ± 0,0 |
| 20.000 | 34,9 ± 2,1 | 3,0 ± 0,0 | 20000,0 ± 0,0 | 3,0 ± 0,0 |
| 50.000 | 37,6 ± 1,8 | 3,0 ± 0,0 | no medido | 3,0 ± 0,0 |
| 100.000 | 39,7 ± 1,8 | 3,0 ± 0,0 | no medido | 4,0 ± 0,0 |

### 3,5 Caso de referencia del enunciado original: N = 10.000 y M = 100 búsquedas

| Estructura | IDs | N | Tiempo de 100 búsquedas (s) |
|---|---|---|---|
| Lista | aleatorio | 10.000 | 0,01428 ± 0,0027 |
| ABB | aleatorio | 10.000 | 5,454e-05 ± 1,9e-06 |
| B+ | aleatorio | 10.000 | 4,229e-05 ± 2e-07 |
| Lista | ordenado | 10.000 | 0,02146 ± 0,001 |
| ABB | ordenado | 10.000 | 0,01657 ± 0,0011 |
| B+ | ordenado | 10.000 | 4,235e-05 ± 2,1e-07 |

### 3,6 Escalamiento con M (exp. 2) — pendiente log-log del tiempo vs M (teoría: 1)

| Estructura | IDs | Pendiente | R² |
|---|---|---|---|
| Lista | aleatorio | 1,01 | 1,0000 |
| ABB | aleatorio | 1,01 | 1,0000 |
| B+ | aleatorio | 1,02 | 0,9999 |
| Lista | ordenado | 1,00 | 0,9999 |
| ABB | ordenado | 1,01 | 1,0000 |
| B+ | ordenado | 1,02 | 0,9999 |

Una pendiente menor que 1 en las estructuras muy rápidas (ABB aleatorio, B+) indica que parte del tiempo es un costo fijo que no depende de M (preparar el bucle, llamadas al cronómetro), que pesa más cuando M es pequeño y el tiempo total es de microsegundos.


### 3,7 Sensibilidad del B+ al orden (exp. 3)

| IDs | Máx. claves/nodo | Altura | Búsqueda (s) | Construcción (s) |
|---|---|---|---|---|
| aleatorio | 4 | 9,0 | 0,001122 ± 1,9e-05 | 0,2413 ± 0,0043 |
| aleatorio | 8 | 6,8 | 0,0009148 ± 2,3e-05 | 0,1697 ± 0,0035 |
| aleatorio | 16 | 5,0 | 0,000757 ± 9,7e-06 | 0,132 ± 0,0038 |
| aleatorio | 32 | 4,0 | 0,0006741 ± 5,1e-06 | 0,1136 ± 0,0039 |
| aleatorio | 64 | 3,0 | 0,0006004 ± 3,2e-06 | 0,1033 ± 0,0033 |
| aleatorio | 128 | 3,0 | 0,0006023 ± 3,5e-06 | 0,1068 ± 0,0034 |
| aleatorio | 256 | 3,0 | 0,0005979 ± 2,1e-06 | 0,1065 ± 0,0034 |
| aleatorio | 512 | 2,0 | 0,0005577 ± 3,7e-06 | 0,1102 ± 0,0028 |
| ordenado | 4 | 11,0 | 0,001252 ± 1,1e-05 | 0,1966 ± 0,0013 |
| ordenado | 8 | 7,0 | 0,0009178 ± 6,7e-06 | 0,1367 ± 0,0012 |
| ordenado | 16 | 5,0 | 0,0007461 ± 6,4e-06 | 0,1051 ± 0,0012 |
| ordenado | 32 | 4,0 | 0,0006785 ± 1,7e-05 | 0,09104 ± 0,0008 |
| ordenado | 64 | 4,0 | 0,0006489 ± 3,5e-06 | 0,08411 ± 0,00094 |
| ordenado | 128 | 3,0 | 0,0005923 ± 3,5e-06 | 0,08151 ± 0,00083 |
| ordenado | 256 | 3,0 | 0,0005956 ± 6e-06 | 0,07827 ± 0,00096 |
| ordenado | 512 | 2,0 | 0,0005354 ± 4,2e-06 | 0,07588 ± 0,00093 |

### 3,8 Valores atípicos (criterio de Tukey: fuera de [Q1 − 1,5·IQR, Q3 + 1,5·IQR])

| Estructura | IDs | Operación | Atípicos | Mediciones | CV medio |
|---|---|---|---|---|---|
| ABB | aleatorio | búsqueda | 1 | 90 | 3,3 % |
| ABB | aleatorio | construcción (N inserciones) | 4 | 90 | 2,9 % |
| ABB | aleatorio | listado ordenado | 3 | 90 | 3,8 % |
| ABB | ordenado | búsqueda | 2 | 70 | 3,0 % |
| ABB | ordenado | construcción (N inserciones) | 1 | 70 | 2,1 % |
| ABB | ordenado | listado ordenado | 1 | 70 | 3,4 % |
| B+ | aleatorio | búsqueda | 9 | 90 | 1,2 % |
| B+ | aleatorio | construcción (N inserciones) | 4 | 90 | 1,7 % |
| B+ | aleatorio | listado ordenado | 3 | 90 | 4,0 % |
| B+ | ordenado | búsqueda | 5 | 90 | 1,1 % |
| B+ | ordenado | construcción (N inserciones) | 3 | 90 | 1,6 % |
| B+ | ordenado | listado ordenado | 6 | 90 | 2,5 % |
| Lista | aleatorio | búsqueda | 2 | 90 | 4,0 % |
| Lista | aleatorio | construcción (N inserciones) | 9 | 90 | 2,3 % |
| Lista | aleatorio | listado ordenado | 3 | 90 | 2,8 % |
| Lista | ordenado | búsqueda | 7 | 90 | 3,5 % |
| Lista | ordenado | construcción (N inserciones) | 9 | 90 | 2,1 % |
| Lista | ordenado | listado ordenado | 1 | 90 | 2,7 % |

Los valores atípicos **no se eliminan**: se reportan y se compara la media con la mediana (columnas `mediana` y `media_sin_atipicos` en `resultados/resumen_exp1.csv`).

## 4. Contraste con la complejidad teórica

Pendiente de la recta ajustada a log(tiempo) vs log(N): ~1 → crecimiento lineal; ~2 → cuadrático; cerca de 0 → casi constante o logarítmico. «Mejor modelo» = el que menor error logarítmico tiene entre O(1), O(log N), O(N), O(N log N), O(N²) con constante libre (es evidencia descriptiva, no una prueba).

| Operación | Estructura | IDs | Teoría | Pendiente (todo N) | Pendiente (N ≥ 5.000) | R² | Mejor modelo |
|---|---|---|---|---|---|---|---|
| búsqueda | Lista | aleatorio | O(N) | 1,13 | 1,26 | 0,987 | O(N log N) |
| búsqueda | Lista | ordenado | O(N) | 1,26 | 1,46 | 0,990 | O(N log N) |
| búsqueda | ABB | aleatorio | O(log N) promedio | 0,16 | 0,14 | 0,994 | O(log N) |
| búsqueda | ABB | ordenado | O(N) (árbol degenerado) | 1,04 | 1,10 | 0,999 | O(N) |
| búsqueda | B+ | aleatorio | O(log N) | 0,11 | 0,10 | 0,973 | O(log N) |
| búsqueda | B+ | ordenado | O(log N) | 0,12 | 0,12 | 0,964 | O(log N) |
| construcción (N inserciones) | Lista | aleatorio | O(N) | 1,00 | 1,01 | 1,000 | O(N) |
| construcción (N inserciones) | Lista | ordenado | O(N) | 1,02 | 1,07 | 1,000 | O(N) |
| construcción (N inserciones) | ABB | aleatorio | O(N log N) | 1,16 | 1,19 | 1,000 | O(N log N) |
| construcción (N inserciones) | ABB | ordenado | O(N²) | 2,01 | 2,09 | 1,000 | O(N²) |
| construcción (N inserciones) | B+ | aleatorio | O(N log N) | 1,13 | 1,15 | 1,000 | O(N log N) |
| construcción (N inserciones) | B+ | ordenado | O(N log N) | 1,12 | 1,14 | 1,000 | O(N log N) |
| listado ordenado | Lista | aleatorio | O(N log N) | 1,27 | 1,27 | 0,998 | O(N log N) |
| listado ordenado | Lista | ordenado | O(N) (Timsort) | 1,28 | 1,51 | 0,990 | O(N log N) |
| listado ordenado | ABB | aleatorio | O(N) | 1,04 | 1,14 | 0,997 | O(N) |
| listado ordenado | ABB | ordenado | O(N) | 1,01 | 1,05 | 1,000 | O(N) |
| listado ordenado | B+ | aleatorio | O(N) | 1,07 | 1,17 | 0,997 | O(N log N) |
| listado ordenado | B+ | ordenado | O(N) | 1,06 | 1,15 | 0,998 | O(N) |

## 5. Preguntas del enunciado, con tus datos

### 5,1 ¿Los resultados se comportan como predice la complejidad teórica?

Ver la tabla de la sección 4 y la gráfica `07_tiempo_normalizado_busqueda.png` (una curva plana indica coincidencia con la teoría).

### 5,2 ¿En qué situaciones el ABB deja de comportarse como O(log N)? / ¿Qué pasa con datos ordenados?

| N | log₂(N+1) (altura mínima posible) | Altura ABB aleatorio | Altura ABB ordenado | Altura aleat. ÷ mínima |
|---|---|---|---|---|
| 100 | 6,7 | 13,8 | 100,0 | 2,07× |
| 500 | 9,0 | 18,8 | 500,0 | 2,10× |
| 1.000 | 10,0 | 21,8 | 1000,0 | 2,19× |
| 2.000 | 11,0 | 24,1 | 2000,0 | 2,20× |
| 5.000 | 12,3 | 29,5 | 5000,0 | 2,40× |
| 10.000 | 13,3 | 31,0 | 10000,0 | 2,33× |
| 20.000 | 14,3 | 34,9 | 20000,0 | 2,44× |
| 50.000 | 15,6 | 37,6 | — | 2,41× |
| 100.000 | 16,6 | 39,7 | — | 2,39× |

Con IDs ordenados cada inserción agrega el nodo como hijo derecho del último: la altura es exactamente N y el ABB equivale a una lista enlazada.

### 5,3 ¿Qué relación existe entre la altura del árbol y el tiempo de búsqueda?

- **ABB**: ajuste log-log tiempo por búsqueda vs. pasos medios → exponente = 0,98 (1 = proporcional), r = 0,999; costo mediano ≈ 0,0356 µs por paso.
- **Lista**: ajuste log-log tiempo por búsqueda vs. pasos medios → exponente = 1,19 (1 = proporcional), r = 0,991; costo mediano ≈ 0,0321 µs por paso.

Gráfica: `06_altura_vs_tiempo.png`.

### 5,4 y 5,5 Diferencias entre casos aleatorios y ordenados (tiempo ordenado ÷ tiempo aleatorio)

| N | construcción · Lista | construcción · ABB | construcción · B+ | búsqueda · Lista | búsqueda · ABB | búsqueda · B+ | listado · Lista | listado · ABB | listado · B+ |
|---|---|---|---|---|---|---|---|---|---|
| 100 | 1,01× | 4,12× | 0,91× | 0,95× | 5,33× | 1,00× | 0,61× | 2,46× | 1,10× |
| 500 | 0,97× | 15,10× | 0,87× | 0,93× | 19,45× | 0,99× | 0,50× | 2,59× | 1,11× |
| 1.000 | 1,02× | 27,13× | 0,87× | 0,97× | 34,75× | 0,99× | 0,46× | 2,55× | 1,07× |
| 2.000 | 1,00× | 48,97× | 0,86× | 1,02× | 63,43× | 0,99× | 0,37× | 2,62× | 1,13× |
| 5.000 | 1,00× | 108,74× | 0,87× | 1,20× | 137,74× | 1,00× | 0,39× | 2,49× | 1,10× |
| 10.000 | 1,04× | 218,01× | 0,86× | 1,31× | 279,70× | 1,00× | 0,38× | 2,62× | 1,08× |
| 20.000 | 1,07× | 396,34× | 0,89× | 1,48× | 530,18× | 1,01× | 0,37× | 2,68× | 1,04× |
| 50.000 | 1,11× | — | 0,91× | 2,54× | — | 0,99× | 0,62× | — | 1,07× |
| 100.000 | 1,21× | — | 0,81× | 1,84× | — | 1,07× | 0,75× | — | 1,01× |

**Ojo con la Lista:** con N = 100.000 hace prácticamente los mismos pasos en ambos escenarios (pasos ordenado ÷ aleatorio = 1,00×) pero su tiempo de búsqueda cambia 1,84×. La diferencia no viene del algoritmo sino de la **localidad de memoria**: los registros se crean en orden aleatorio, así que recorrer la lista ordenada por ID salta por direcciones de memoria dispersas (más fallos de caché) mientras que la lista en orden aleatorio recorre registros creados consecutivamente. Es un ejemplo de cómo el hardware modifica las constantes sin cambiar la complejidad.


### 5,6 ¿A partir de qué tamaño de entrada son claramente visibles las diferencias en la búsqueda?

Primer N de la rejilla donde la lista es ≥ k veces más lenta y los intervalos de confianza al 95 % de ambas medias no se solapan:

| Comparación | Diferencia | Primer N |
|---|---|---|
| Lista vs ABB (IDs aleatorios) | ≥ 2× | 100 |
| Lista vs ABB (IDs aleatorios) | ≥ 10× | 500 |
| Lista vs ABB (IDs aleatorios) | ≥ 100× | 5.000 |
| Lista vs B+ (IDs aleatorios) | ≥ 2× | 100 |
| Lista vs B+ (IDs aleatorios) | ≥ 10× | 500 |
| Lista vs B+ (IDs aleatorios) | ≥ 100× | 5.000 |
| ABB vs B+ (IDs aleatorios) | ≥ 1,5× | no se alcanza en la rejilla |

### 5,7 ¿Hay costos constantes que igualen algoritmos de distinta complejidad con N pequeño?

| N | Lista (µs/búsq.) | ABB aleat. (µs/búsq.) | B+ (µs/búsq.) | ABB ordenado (µs/búsq.) |
|---|---|---|---|---|
| 100 | 1,25 | 0,281 | 0,31 | 1,5 |
| 500 | 6,36 | 0,366 | 0,337 | 7,13 |
| 1.000 | 13,7 | 0,431 | 0,361 | 15 |
| 2.000 | 31,1 | 0,476 | 0,376 | 30,2 |

Con N = 100 la lista es 4,5× más lenta que el ABB aleatorio y 4,0× más lenta que el B+; con N = 2.000 la brecha ya es de 65,4× y 82,7×. Con N pequeño dominan el costo de llamar a la función, el bucle de consultas y las constantes de cada implementación, no el número de comparaciones; por eso las diferencias se achican (y a veces se invierten, p. ej. ABB con IDs ordenados vs Lista).

## 6. Gráficas generadas (carpeta `graficas/`)

| Archivo | Qué muestra |
|---|---|
| 01_busqueda_vs_N.png | Tiempo de M búsquedas vs N, 3 estructuras, IDs aleatorios y ordenados |
| 02_busqueda_aleatorio_vs_ordenado.png | Lo mismo, pero separado por estructura para ver el efecto del orden |
| 03_construccion_vs_N.png | Tiempo de construir (N inserciones) vs N |
| 04_listado_vs_N.png | Tiempo del listado ordenado vs N |
| 05_altura_vs_N.png | Altura de ABB y B+ vs N y vs log₂(N+1) |
| 06_altura_vs_tiempo.png | Tiempo por búsqueda vs pasos medios (relación altura–tiempo) |
| 07_tiempo_normalizado_busqueda.png | Tiempo ÷ complejidad teórica (¿plano = coincide con la teoría?) |
| 08_aceleracion_vs_lista.png | Cuántas veces la lista es más lenta que ABB/B+ según N |
| 09_penalizacion_orden.png | Cociente tiempo ordenado ÷ aleatorio por operación |
| 10_busqueda_vs_M.png | Experimento 2: tiempo vs número de búsquedas M |
| 11_bplus_vs_orden.png | Experimento 3: B+ según máx. claves por nodo |

