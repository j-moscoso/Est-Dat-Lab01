# Laboratorio 2 — Juan Manuel Moscoso Torres

## Contenido de la carpeta

| Archivo | Descripción |
|---|---|
| `merkle_tree.py` | Código fuente del laboratorio: construcción del árbol, prueba de inclusión y diagrama ASCII. |
| `Diagrama del árbol construido.png` | Diagrama gráfico del árbol de Merkle ya construido, con sus 5 bloques, ramas y raíz. |
| `Verificación válida.png` | Captura de pantalla de la ejecución del script probando un bloque con su texto correcto. |
| `Verificación inválida.png` | Captura de pantalla de la ejecución del script probando un bloque con un texto alterado. |
| `README.md` | Este documento. |

## Código fuente

El código completo está en [`merkle_tree.py`](./merkle_tree.py). Las funciones principales son:

| Función | Qué hace |
|---|---|
| `h(data)` | Calcula el hash SHA-256 de un texto. |
| `construir_arbol(bloques)` | Construye todos los niveles del árbol (hojas → raíz), duplicando el último nodo cuando un nivel es impar. |
| `generar_prueba(niveles, indice)` | Genera los hashes "hermanos" del camino desde una hoja hasta la raíz. |
| `verificar_prueba(dato, prueba, raiz_esperada)` | Recalcula el camino hacia la raíz con un dato y confirma si coincide. |
| `imprimir_arbol(...)` | Dibuja el árbol en ASCII, marcando explícitamente en qué niveles hubo duplicación por ser impares. |


## Cómo ejecutar

```bash
python3 merkle_tree.py
```

El programa pedirá dos entradas por teclado:
1. Número del bloque a modificar (1–5) y el nuevo texto.
2. Número del bloque a verificar (1–5) y el texto que se afirma que contiene, para la prueba de inclusión.

## Uso de Inteligencia Artificial

Usé Claude (Anthropic) como apoyo puntual durante el desarrollo, no para resolver el laboratorio de principio a fin. Así fue el proceso:
 
- **Base propia:** ya había resuelto antes los ejercicios de la clase, así que llegué a este laboratorio con la lógica general ya clara y solo necesitaba extenderla a 5 bloques y a un formato de entrega más completo.
- **Le pedí ayuda para escribir el código a partir de mis propias soluciones anteriores**, usando las soluciones anteriores en una base de cómo creía resolver el laboratorio le pedí que me ayudara a adaptar y extender mi código para cumplir las condiciones del laboratorio.
- **Toma de decisiones:** le pedí ayuda para decidir qué era lo mejor para resolver cada parte del laboratorio cuando me surgían varias ideas de cómo hacerlo.
- Fui iterando el código en varias rondas hasta llegar a la versión final, revisando cada cambio y ajustando cuando algo no me convencía o no representaba bien lo que yo quería mostrar.

En resumen, la IA me ayudó a expandir mi lógica en el código, y a corregir errores puntuales en cómo yo estaba planteando la solución.
 
