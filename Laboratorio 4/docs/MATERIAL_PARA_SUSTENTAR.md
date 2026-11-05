# Material para la sustentación – Laboratorio 4

Los números de este documento corresponden a la corrida guardada en `resultados/informe_analisis.md`. Los tiempos pueden cambiar entre máquinas; lo que se mantiene es la forma de las curvas.

---

## 1. Resumen en una página

**Problema.** 10.000 puntos de entrega estáticos en una ciudad. Responder (1) qué puntos están a 500 m o menos de una ubicación y (2) cuál es el punto más cercano.

**Qué se hizo.** Un Quadtree 2D desde cero (sin scipy ni librerías de árboles), búsqueda por radio, k vecinos más cercanos, pruebas contra fuerza bruta, verificación visual y una comparación de tiempos para N entre 10 y 10.000.

**Resultado principal.** El Quadtree empieza a ganar a la fuerza bruta desde N = 50 en las dos consultas medidas. Con N = 10.000 es 17,8 veces más rápido en radio y 79,6 veces en vecino más cercano.

**Por qué ocurre.** La fuerza bruta mide N distancias por consulta. El Quadtree descarta rectángulos enteros y solo mide las distancias de los puntos cercanos (103 distancias en vez de 10.000 con N = 10.000). Con pocos puntos, ese ahorro no compensa el costo de recorrer el árbol.

---

## 2. Qué hace cada archivo

| Archivo | Qué contiene |
|---|---|
| `Quadtreetree.py` | Quadtree 2D (insertar, radio, k cercanos), fuerza bruta y generadores de puntos |
| `test.py` | 10 pruebas unitarias, análisis de las pruebas y 3 gráficas de verificación visual |
| `analisis.py` | Mediciones de tiempo, 6 gráficas, CSV con los datos crudos e informe |

---

## 3. Decisiones de diseño y su justificación

Esta es la tabla más importante: cada fila es una pregunta que te pueden hacer.

| Decisión | Por qué | Por qué no la alternativa |
|---|---|---|
| **Solo 2D** | El problema usa coordenadas (x, y). Cada nodo tiene 4 hijos. | K dimensiones daría 2ᴷ hijos por nodo y código más abstracto; se permitía 2D en el enunciado y es lo más fácil de explicar. |
| **Coordenadas en metros** | El radio de 500 es 500 m y las distancias salen en metros sin conversión. | Con latitud y longitud habría que convertir grados a metros (1° de latitud ≈ 111 km) o usar Haversine. Tampoco hay que hacerlo si los datos son sintéticos. |
| **Ciudad de 10 km × 10 km** | Un tamaño razonable para una ciudad mediana; con 10.000 puntos da una densidad de 1 punto por 10.000 m², o sea cerca de 78 puntos por radio de 500 m. | Cualquier otro tamaño sirve; lo importante es que el radio no cubra casi toda la ciudad. |
| **Datos sintéticos uniformes (y agrupados como prueba extra)** | El enunciado permite generarlos y así se controla N. Los agrupados simulan barrios. | Datos reales: no hacía falta y cada N distinto exigiría reducir un conjunto real. |
| **Capacidad 4 por hoja** | Hojas pequeñas, simples de entender. | No se probó otra capacidad (limitación). Una capacidad mayor da árboles menos profundos pero hojas con más puntos por revisar. |
| **Profundidad máxima 20** | Evita recursión infinita con puntos repetidos. | Sin tope, 5 puntos idénticos se dividen sin parar. |
| **Distancia al cuadrado** | Evita calcular raíces; el orden entre distancias no cambia. | Calcular `math.sqrt` en cada comparación es más lento y no aporta nada. La raíz se aplica solo al devolver. |
| **Poda con distancia al rectángulo** | Si el punto del rectángulo más cercano a la consulta ya está fuera del radio, ningún otro punto de ese rectángulo puede estar dentro. | Revisar todos los nodos sería recorrer todo el árbol y no ahorrar nada. |
| **`<=` al comparar con el radio** | Un punto a exactamente 500 m está "a un radio de 500 m o menos". La prueba 3-4-5 lo verifica. | Con `<` ese punto se perdería. |
| **k cercanos con una lista ordenada y `sort()`** | Con k pequeño la lista tiene a lo sumo k + 1 elementos; `sort()` sobre tuplas ordena por la primera componente (la distancia²). No hace falta `key=` ni `lambda`. | `heapq` sería válido pero más difícil de explicar y sin beneficio con k pequeño. |
| **Visitar primero el hijo donde cae la consulta** | Encuentra buenos candidatos pronto, así se puede podar más. El resultado es el mismo en cualquier orden. | Visitar en orden fijo también es correcto, solo más lento. |
| **Recursión en insertar y en las búsquedas** | La profundidad máxima es 20, así que no hay riesgo de desbordar la pila. Es más corta y fácil de leer. | Una versión con pila explícita sería más larga. En `hojas()` sí se usó pila porque era igual de simple. |
| **Fuerza bruta con listas y un `for`** | Es lo que dice el enunciado ("no árboles, sí listas") y es la forma más natural. | NumPy vectorizaría la fuerza bruta y la haría mucho más rápida; comparar contra eso sería comparar contra otra herramienta. Se menciona como limitación. |
| **Mismo lenguaje y mismas consultas para ambos** | Comparación justa: solo cambia el algoritmo. | |
| **Medir tiempo por consulta, no total** | Es la cantidad que importa en un sistema de entregas y no depende de cuántas consultas se hicieron. | |
| **200 consultas × 10 repeticiones** | Una consulta sola dura microsegundos y el ruido del sistema la distorsiona; promediando 200 consultas y repitiendo 10 veces con datos nuevos se ve la variabilidad (barras de error). | |
| **`gc.disable()` al medir** | El recolector de basura de Python puede pausar el programa a mitad de una medición y meter ruido. | |
| **Quadtree sin borrado ni actualización** | Los datos son estáticos, así que solo se necesita insertar y buscar. | |

### Lo que se evitó a propósito

- **`key=lambda` y construcciones raras:** donde hay que ordenar, se ordenan tuplas `(distancia², punto)` que Python ya compara bien. Todo el código se puede explicar línea por línea. Si te preguntan por algo que no sepas explicar, es mejor decirlo que inventar.
- **Librerías de árboles o `scipy`:** el enunciado las prohíbe. Solo se usa `matplotlib` para graficar.

---

## 4. Cómo leer cada gráfica

**Por qué ejes lineales.** En un eje logarítmico, una diferencia de 10 veces se ve como un paso corto y las curvas de dos métodos muy distintos pueden parecer cercanas. Aquí lo que se quiere mostrar es cuánto más lenta es la fuerza bruta, así que se usaron ejes lineales y, como el cruce ocurre en N pequeños que se aplastan contra el eje, cada gráfica tiene un panel con **zoom a N ≤ 500**. Además hay una gráfica de **aceleración** (cociente entre ambos tiempos) donde 1 significa empate.

| Gráfica | Qué muestra | Qué decir |
|---|---|---|
| `01_verificacion_radio` | Ciudad completa y zoom con el círculo y los puntos encontrados en rojo | El Quadtree encuentra los mismos puntos que la fuerza bruta (ambos números están en el título del zoom). Los rojos son todos los puntos dentro del círculo y ninguno afuera. |
| `02_verificacion_vecinos` | Vecino más cercano y los 5 más cercanos | El círculo con radio igual a la distancia del vecino más lejano no contiene otros puntos. |
| `03_estructura_pequena` | Quadtree con 40 puntos | Se subdivide más donde hay más puntos. |
| `04_tiempo_radio_vs_N` | Tiempo por consulta de radio | La fuerza bruta crece en línea recta con N; el Quadtree casi no crece. En el zoom se ve el cruce. |
| `05_tiempo_vecino_vs_N` | Lo mismo para el vecino más cercano | Misma lectura; el Quadtree gana más por la poda. |
| `06_aceleracion_vs_N` | Fuerza bruta ÷ Quadtree | La línea punteada en 1 es el empate. Donde la curva cruza 1 está la respuesta a la pregunta del profesor. |
| `07_distancias_vs_N` | Distancias calculadas por consulta | No depende de la máquina ni del lenguaje. La fuerza bruta calcula N; el Quadtree muy pocas. |
| `08_construccion_vs_N` | Tiempo de construir el árbol | Es un costo que se paga una vez, porque los datos son estáticos. |
| `09_efecto_del_radio` | Tiempo y aceleración según el radio con N = 10.000 | Con radios grandes el árbol deja de ganar. |

---

