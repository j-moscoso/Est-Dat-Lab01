import hashlib

def h(data):
    return hashlib.sha256(data.encode()).hexdigest()

def construir_arbol(bloques):
    # Hojas: hash de cada bloque. Cada nivel: hash de pares (izq+der).
    # Si un nivel queda impar, se duplica el ultimo nodo antes de combinar.
    nivel = [h(b) for b in bloques]
    niveles = [nivel]
    duplicados = []  # guarda en que nivel hubo que duplicar, para mostrarlo despues
    while len(nivel) > 1:
        if len(nivel) % 2 != 0:
            nivel = nivel + [nivel[-1]]
            duplicados.append(len(niveles) - 1)
        nivel = [h(nivel[i] + nivel[i+1]) for i in range(0, len(nivel), 2)]
        niveles.append(nivel)
    return niveles, duplicados

def generar_prueba(niveles, indice):
    # Guarda los hashes "hermanos" en el camino de la hoja hasta la raiz
    prueba = []
    i = indice
    for nivel in niveles[:-1]:
        if i % 2 == 0:
            j = i + 1 if i + 1 < len(nivel) else i
            prueba.append((nivel[j], "derecha"))
        else:
            prueba.append((nivel[i-1], "izquierda"))
        i //= 2
    return prueba

def verificar_prueba(dato, prueba, raiz_esperada):
    # Recalcula el camino hacia la raiz usando el dato y los hermanos
    actual = h(dato)
    for hermano, lado in prueba:
        actual = h(actual + hermano) if lado == "derecha" else h(hermano + actual)
    return actual == raiz_esperada

def imprimir_arbol(niveles, bloques, duplicados):
    # Diagrama ASCII: de la raiz (arriba) a los datos originales (abajo).
    # Si un nivel fue impar, se marca cual nodo se duplico para poder combinarlo.
    print("\n=== DIAGRAMA DEL ARBOL ===")
    for n in range(len(niveles)-1, -1, -1):
        etiqueta = "RAIZ" if n == len(niveles)-1 else f"Nivel {n}"
        linea = "  ".join(x[:8] for x in niveles[n])
        if n in duplicados:
            linea += f"  <- IMPAR: se duplico '{niveles[n][-1][:8]}' para combinar"
        print(f"{etiqueta:>8}: {linea}")
    print(f"{'Datos':>8}: " + "  ".join(bloques))


# ---------- EXPERIMENTO ----------

bloques = [
    "Ana paga 150",
    "Luis paga 230",
    "Carlos paga 80",
    "Maria paga 95",
    "Pedro paga 300",
]

# 1. Mostrar los bloques creados
print("Bloques creados:")
for i, b in enumerate(bloques, start=1):
    print(f" {i}. Bloque{i}: {b}")

# 2. Construir el arbol y mostrar la raiz completa
niveles, duplicados = construir_arbol(bloques)
raiz = niveles[-1][0]
print("\nArbol construido. RAIZ:", raiz)

# 3. Modificar un bloque (por teclado) y demostrar que la raiz cambia
num_mod = int(input("\n¿Que bloque quieres modificar? (numero 1-5): "))
nuevo_texto = input("Escribe el nuevo texto para ese bloque: ")

bloques_mod = bloques.copy()
bloques_mod[num_mod - 1] = nuevo_texto
raiz_mod = construir_arbol(bloques_mod)[0][-1][0]
print("\nRAIZ tras modificar el Bloque", num_mod, ":", raiz_mod)
print("¿Cambio la raiz?", "SI" if raiz_mod != raiz else "NO")

# 4-5. Prueba de inclusion: se elige la POSICION del bloque a verificar,
# y luego se escribe el texto que se dice que tiene esa posicion.
num = int(input("\n¿Que bloque quieres verificar? (numero 1-5): "))
texto = input("Escribe el texto que dices que tiene ese bloque: ")

indice = num - 1
prueba = generar_prueba(niveles, indice)
resultado = verificar_prueba(texto, prueba, raiz)
print("¿El texto coincide con ese bloque del arbol?",
      "SI, verificado" if resultado else "NO, correctamente rechazado")

# 6. Diagrama ASCII del arbol original, al final
imprimir_arbol(niveles, bloques, duplicados)