# Informe de rendimiento: Quadtree vs fuerza bruta (generado automáticamente)

## 1. Condiciones de la medición

| Parámetro | Valor |
|---|---|
| Ciudad | cuadrado de 10000 m x 10000 m, coordenadas en metros |
| Radio de búsqueda | 500 m |
| Tamaños N | 10, 20, 50, 100, 200, 300, 500, 1000, 2000, 5000, 10000 |
| Consultas por repetición | 200 puntos de consulta al azar (los mismos para ambos métodos) |
| Repeticiones | 10 (datos nuevos en cada una); media ± desviación estándar |
| Quadtree | 2D, 4 puntos por hoja, profundidad máxima 20 |
| Fuerza bruta | recorre la lista completa de puntos, mismo lenguaje (Python puro) |
| Equipo | Windows-10-10.0.26300-SP0, CPU: AMD64 Family 25 Model 33 Stepping 0, AuthenticAMD |
| Python | 3.11.9 |

## 2. Resultados con puntos uniformes (tiempo por consulta en µs)

| N | Radio: fuerza bruta | Radio: Quadtree | Aceleración radio | Vecino: fuerza bruta | Vecino: Quadtree | Aceleración vecino |
|---|---|---|---|---|---|---|
| 10 | 1.8 | 3.7 | 0.50x | 1.9 | 4.4 | 0.42x |
| 20 | 3.5 | 5.2 | 0.68x | 3.6 | 6.6 | 0.55x |
| 50 | 8.5 | 7.1 | 1.19x | 8.8 | 8.4 | 1.05x |
| 100 | 16.8 | 9.4 | 1.79x | 17.4 | 10.4 | 1.67x |
| 200 | 33.4 | 11.9 | 2.82x | 34.1 | 11.9 | 2.87x |
| 300 | 50.7 | 14.0 | 3.62x | 50.9 | 12.6 | 4.02x |
| 500 | 83.5 | 17.3 | 4.83x | 84.5 | 14.0 | 6.03x |
| 1000 | 167.9 | 23.6 | 7.11x | 170.0 | 15.6 | 10.89x |
| 2000 | 372.3 | 39.8 | 9.35x | 375.9 | 19.7 | 19.06x |
| 5000 | 941.0 | 66.1 | 14.23x | 926.2 | 21.2 | 43.63x |
| 10000 | 1986.6 | 111.9 | 17.76x | 1990.1 | 25.0 | 79.62x |

## 3. Respuesta a la pregunta del enunciado

- **Búsqueda por radio (500 m), puntos uniformes:** el Quadtree empieza a ser más rápido desde N = 50 (y se mantiene más rápido para todos los N mayores medidos). El último tamaño donde todavía perdía era N = 20.
- **Vecino más cercano, puntos uniformes:** desde N = 50.
- **Búsqueda por radio con puntos agrupados (barrios):** desde N = 50.
- Con N = 10000 puntos (el caso del enunciado) el Quadtree es 17.8 veces más rápido en radio y 79.6 veces en vecino más cercano.
- El punto de cruce depende de la rejilla de N medida y de la máquina: es una estimación, no un valor exacto.

## 4. Cuántas distancias se calculan por consulta (no depende de la máquina)

| N | Fuerza bruta (distancias) | Quadtree radio (distancias) | Quadtree radio (nodos visitados) | Quadtree vecino (distancias) | Quadtree vecino (nodos visitados) |
|---|---|---|---|---|---|
| 10 | 10 | 2.8 | 5.4 | 4.4 | 5.7 |
| 20 | 20 | 2.8 | 8.1 | 4.6 | 9.2 |
| 50 | 50 | 4.1 | 11.2 | 5.3 | 11.8 |
| 100 | 100 | 4.9 | 15.0 | 5.5 | 15.4 |
| 200 | 200 | 7.0 | 19.0 | 5.8 | 17.7 |
| 300 | 300 | 8.6 | 22.4 | 5.8 | 19.2 |
| 500 | 500 | 11.3 | 27.2 | 6.0 | 21.3 |
| 1000 | 1000 | 17.9 | 36.1 | 6.2 | 23.4 |
| 2000 | 2000 | 28.4 | 51.1 | 6.0 | 26.3 |
| 5000 | 5000 | 58.1 | 83.6 | 6.1 | 29.0 |
| 10000 | 10000 | 103.0 | 124.9 | 6.3 | 31.4 |

La fuerza bruta siempre calcula N distancias. Con N = 10000 el Quadtree en radio calcula 103 distancias y visita 125 nodos; 75.1 de esos puntos están dentro del radio.
Eso es 97 veces menos distancias, pero el tiempo mejora solo 17.8 veces: recorrer nodos, llamar funciones y comparar rectángulos también cuesta.

## 5. Costo de construir el árbol y cuándo se paga

| N | Construcción (ms) | Consultas de radio para compensar la construcción |
|---|---|---|
| 10 | 0.02 | nunca (pierde en radio) |
| 20 | 0.03 | nunca (pierde en radio) |
| 50 | 0.07 | 53 |
| 100 | 0.15 | 21 |
| 200 | 0.30 | 14 |
| 300 | 0.48 | 13 |
| 500 | 0.85 | 13 |
| 1000 | 1.85 | 13 |
| 2000 | 4.14 | 12 |
| 5000 | 11.58 | 13 |
| 10000 | 25.09 | 13 |

Si los puntos son estáticos (como pide el ejercicio) el árbol se construye una vez y se reutiliza, así que este costo se reparte entre todas las consultas.

## 6. Efecto del radio (N = 10.000)

| Radio (m) | Puntos encontrados (promedio) | Fuerza bruta (µs) | Quadtree (µs) | Aceleración |
|---|---|---|---|---|
| 50 | 0.8 | 1906.5 | 22.1 | 86.31x |
| 100 | 3.1 | 1886.2 | 28.5 | 66.16x |
| 250 | 19.2 | 1927.7 | 51.9 | 37.18x |
| 500 | 75.4 | 1918.4 | 109.9 | 17.46x |
| 1000 | 290.3 | 2069.9 | 331.0 | 6.25x |
| 2000 | 1044.7 | 2132.6 | 974.9 | 2.19x |
| 3000 | 2144.8 | 2140.8 | 1827.5 | 1.17x |
| 5000 | 4792.1 | 2155.6 | 3671.9 | 0.59x |

Mientras más grande el radio, más puntos hay que devolver y menos nodos se pueden descartar, por eso la aceleración baja. Radio más grande probado donde el Quadtree sigue ganando: 3000 m.

## 7. Discusión

- La fuerza bruta cuesta O(N): cada consulta revisa todos los puntos. Su tiempo crece en línea recta con N.
- El Quadtree descarta rectángulos enteros que quedan fuera del radio, así que solo revisa los puntos de la zona cercana. Su costo crece muy lento con N (aproximadamente con la altura del árbol más los puntos que realmente están cerca).
- Con N pequeño el Quadtree no gana porque cada nodo visitado cuesta una llamada de función y una comparación con el rectángulo, y con pocos puntos la fuerza bruta ya es casi instantánea. Esa sobrecarga es el costo constante que el ahorro de comparaciones tiene que superar.
- Las gráficas usan ejes lineales a propósito: en un eje logarítmico una diferencia de 10 veces se ve como un paso corto y las curvas parecen cercanas. Con ejes lineales la brecha se ve tal cual, y la gráfica de aceleración muestra directamente cuántas veces gana un método.
- Con puntos agrupados y N = 10000 la aceleración en radio es 19.5x (con puntos uniformes: 17.8x). Se probó para ver si la distribución de los puntos cambia la conclusión.

## 8. Limitaciones

- Mediciones en Python puro y en un solo equipo: sirven para comparar tendencias y proporciones, no tiempos absolutos.
- Una fuerza bruta con NumPy (vectorizada) sería mucho más rápida que la de listas y movería el punto de cruce; aquí se compara con listas porque es lo que pide el enunciado.
- Los contadores de nodos y distancias suman una pequeña sobrecarga al Quadtree, lo que juega en su contra.
- La rejilla de N es finita: el punto de cruce real está entre el último N donde pierde y el primero donde gana.
- Datos sintéticos (uniformes y agrupados), no coordenadas reales de una ciudad.
