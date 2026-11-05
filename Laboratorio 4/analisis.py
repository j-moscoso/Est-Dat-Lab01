"""
Métricas de rendimiento: Quadtree vs fuerza bruta.

    python analisis.py

Genera graficas/04..09_*.png, resultados/resultados_crudos.csv y resultados/informe_analisis.md.
Todo lo que aparece en el informe sale de las mediciones de esta corrida.
"""
import csv
import gc
import os
import platform
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from Quadtreetree import (construir, generar_puntos, generar_puntos_agrupados,
                          radio_fuerza_bruta, mas_cercano_fuerza_bruta)

LADO = 10000                 # la ciudad es un cuadrado de 10 km x 10 km (coordenadas en metros)
RADIO = 500                  # metros
TAMANOS = [10, 20, 50, 100, 200, 300, 500, 1000, 2000, 5000, 10000]
CONSULTAS = 200              # consultas por repetición (puntos de consulta al azar en la ciudad)
REPETICIONES = 10
SEMILLA = 2026
RADIOS = [50, 100, 250, 500, 1000, 2000, 3000, 5000]
REPETICIONES_RADIOS = 5

COLOR_BF = "#E4572E"
COLOR_QT = "#2E86AB"
COLOR_3 = "#2CA58D"


# ====================================================================== mediciones
def tiempo_radio_bf(puntos, consultas, radio):
    encontrados = 0
    inicio = time.perf_counter()
    for (x, y) in consultas:
        encontrados += len(radio_fuerza_bruta(puntos, x, y, radio))
    total = time.perf_counter() - inicio
    return total / len(consultas), encontrados / len(consultas)


def tiempo_radio_qt(arbol, consultas, radio):
    arbol.visitas = 0
    arbol.distancias = 0
    encontrados = 0
    inicio = time.perf_counter()
    for (x, y) in consultas:
        encontrados += len(arbol.buscar_radio(x, y, radio))
    total = time.perf_counter() - inicio
    n = len(consultas)
    return total / n, encontrados / n, arbol.visitas / n, arbol.distancias / n


def tiempo_vecino_bf(puntos, consultas):
    inicio = time.perf_counter()
    for (x, y) in consultas:
        mas_cercano_fuerza_bruta(puntos, x, y)
    return (time.perf_counter() - inicio) / len(consultas)


def tiempo_vecino_qt(arbol, consultas):
    arbol.visitas = 0
    arbol.distancias = 0
    inicio = time.perf_counter()
    for (x, y) in consultas:
        arbol.mas_cercano(x, y)
    total = time.perf_counter() - inicio
    n = len(consultas)
    return total / n, arbol.visitas / n, arbol.distancias / n


def crear_puntos(n, distribucion, semilla):
    if distribucion == "uniforme":
        return generar_puntos(n, LADO, semilla)
    return generar_puntos_agrupados(n, LADO, semilla)


def medir_tamano(n, repeticion, distribucion):
    semilla = SEMILLA + n * 100 + repeticion
    puntos = crear_puntos(n, distribucion, semilla)
    consultas = generar_puntos(CONSULTAS, LADO, semilla + 1)

    gc.collect()
    gc.disable()
    inicio = time.perf_counter()
    arbol = construir(puntos, LADO)
    t_construccion = time.perf_counter() - inicio

    t_radio_bf, hallados_bf = tiempo_radio_bf(puntos, consultas, RADIO)
    t_radio_qt, hallados_qt, visitas_radio, dist_radio = tiempo_radio_qt(arbol, consultas, RADIO)
    t_vecino_bf = tiempo_vecino_bf(puntos, consultas)
    t_vecino_qt, visitas_vecino, dist_vecino = tiempo_vecino_qt(arbol, consultas)
    gc.enable()

    assert hallados_bf == hallados_qt, "el Quadtree y la fuerza bruta encontraron distinta cantidad de puntos"
    return {
        "distribucion": distribucion, "N": n, "repeticion": repeticion,
        "t_construccion": t_construccion,
        "t_radio_bf": t_radio_bf, "t_radio_qt": t_radio_qt,
        "t_vecino_bf": t_vecino_bf, "t_vecino_qt": t_vecino_qt,
        "hallados_radio": hallados_qt,
        "visitas_radio": visitas_radio, "dist_radio_qt": dist_radio,
        "visitas_vecino": visitas_vecino, "dist_vecino_qt": dist_vecino,
    }


def medir_radios(radio, repeticion):
    n = 10000
    semilla = SEMILLA + radio + repeticion
    puntos = generar_puntos(n, LADO, semilla)
    consultas = generar_puntos(CONSULTAS, LADO, semilla + 1)
    arbol = construir(puntos, LADO)
    gc.collect()
    gc.disable()
    t_bf, _ = tiempo_radio_bf(puntos, consultas, radio)
    t_qt, hallados, _, _ = tiempo_radio_qt(arbol, consultas, radio)
    gc.enable()
    return {"radio": radio, "repeticion": repeticion, "t_bf": t_bf, "t_qt": t_qt, "hallados": hallados}


def calentar():
    puntos = generar_puntos(500, LADO, 1)
    consultas = generar_puntos(50, LADO, 2)
    arbol = construir(puntos, LADO)
    for _ in range(3):
        tiempo_radio_bf(puntos, consultas, RADIO)
        tiempo_radio_qt(arbol, consultas, RADIO)
        tiempo_vecino_bf(puntos, consultas)
        tiempo_vecino_qt(arbol, consultas)


# ====================================================================== resúmenes
def por_n(filas, distribucion, columna):
    """Media y desviación estándar de una columna para cada N de TAMANOS."""
    medias = []
    desviaciones = []
    for n in TAMANOS:
        valores = []
        for f in filas:
            if f["distribucion"] == distribucion and f["N"] == n:
                valores.append(f[columna])
        medias.append(statistics.mean(valores))
        desviaciones.append(statistics.stdev(valores))
    return medias, desviaciones


def dividir(a, b):
    resultado = []
    for i in range(len(a)):
        resultado.append(a[i] / b[i])
    return resultado


def multiplicar(lista, factor):
    resultado = []
    for v in lista:
        resultado.append(v * factor)
    return resultado


def primer_n_ganador(tamanos, t_bf, t_qt):
    """Menor N desde el cual el Quadtree es más rápido y lo sigue siendo para todos los N mayores."""
    ganador = None
    for i in range(len(tamanos) - 1, -1, -1):
        if t_qt[i] < t_bf[i]:
            ganador = tamanos[i]
        else:
            break
    return ganador


def consultas_para_compensar(t_construccion, t_bf, t_qt):
    """Cuántas consultas hacen falta para que construir el árbol se pague solo (None si nunca)."""
    ahorro = t_bf - t_qt
    if ahorro <= 0:
        return None
    return t_construccion / ahorro


# ====================================================================== gráficas
def grafica_dos_paneles(archivo, titulo, ylabel, series, zoom_n=500, n_cruce=None, linea_en_1=False):
    """Izquierda: todos los N. Derecha: zoom a los N pequeños. Ejes lineales."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    for ax, limite in ((ax1, max(TAMANOS)), (ax2, zoom_n)):
        for (etiqueta, valores, desviaciones, color, estilo) in series:
            xs = []
            ys = []
            es = []
            for i in range(len(TAMANOS)):
                if TAMANOS[i] <= limite:
                    xs.append(TAMANOS[i])
                    ys.append(valores[i])
                    if desviaciones is not None:
                        es.append(desviaciones[i])
            if desviaciones is not None:
                ax.errorbar(xs, ys, yerr=es, marker="o", capsize=3, color=color, linestyle=estilo, label=etiqueta)
            else:
                ax.plot(xs, ys, marker="o", color=color, linestyle=estilo, label=etiqueta)
        if linea_en_1:
            ax.axhline(1, color="#888888", linestyle=":")
        if n_cruce is not None and n_cruce <= limite:
            ax.axvline(n_cruce, color="#555555", linestyle="--", linewidth=1)
        ax.set_xlabel("Número de puntos de entrega N")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)
    ax1.set_title("Todos los tamaños")
    ax2.set_title(f"Zoom: N ≤ {zoom_n}")
    fig.suptitle(titulo, fontweight="bold")
    fig.savefig("graficas/" + archivo, dpi=150, bbox_inches="tight")
    plt.close(fig)


def grafica_radios(archivo, radios, t_bf, t_qt, e_bf, e_qt):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    ax1.errorbar(radios, multiplicar(t_bf, 1e6), yerr=multiplicar(e_bf, 1e6), marker="o", capsize=3,
                 color=COLOR_BF, label="Fuerza bruta")
    ax1.errorbar(radios, multiplicar(t_qt, 1e6), yerr=multiplicar(e_qt, 1e6), marker="o", capsize=3,
                 color=COLOR_QT, label="Quadtree")
    ax1.set_ylabel("Tiempo por consulta (µs)")
    ax1.set_title("Tiempo según el radio")
    ax2.plot(radios, dividir(t_bf, t_qt), marker="o", color=COLOR_3)
    ax2.axhline(1, color="#888888", linestyle=":")
    ax2.set_ylabel("Aceleración = t fuerza bruta / t Quadtree")
    ax2.set_title("Cuántas veces es más rápido el Quadtree (1 = empate)")
    for ax in (ax1, ax2):
        ax.set_xlabel("Radio de búsqueda (m)")
        ax.grid(True, alpha=0.3)
    ax1.legend()
    fig.suptitle("Efecto del radio con N = 10.000 puntos", fontweight="bold")
    fig.savefig("graficas/" + archivo, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ====================================================================== informe
def tabla(encabezados, filas):
    lineas = ["| " + " | ".join(encabezados) + " |", "|" + "|".join(["---"] * len(encabezados)) + "|"]
    for fila in filas:
        textos = []
        for celda in fila:
            textos.append(str(celda))
        lineas.append("| " + " | ".join(textos) + " |")
    return "\n".join(lineas)


def texto_n(n):
    if n is None:
        return "ningún N de los medidos"
    return str(n)


def anterior_en_rejilla(n):
    """Último N medido que es menor que n (para decir 'entre X y n')."""
    anterior = None
    for t in TAMANOS:
        if t < n:
            anterior = t
    return anterior


def escribir_informe(r, resumen):
    n_final = TAMANOS[-1]
    i = len(TAMANOS) - 1
    lineas = []
    w = lineas.append
    w("# Informe de rendimiento: Quadtree vs fuerza bruta (generado automáticamente)\n")
    w("## 1. Condiciones de la medición\n")
    w(tabla(["Parámetro", "Valor"], [
        ["Ciudad", f"cuadrado de {LADO} m x {LADO} m, coordenadas en metros"],
        ["Radio de búsqueda", f"{RADIO} m"],
        ["Tamaños N", ", ".join(str(n) for n in TAMANOS)],
        ["Consultas por repetición", f"{CONSULTAS} puntos de consulta al azar (los mismos para ambos métodos)"],
        ["Repeticiones", f"{REPETICIONES} (datos nuevos en cada una); media ± desviación estándar"],
        ["Quadtree", "2D, 4 puntos por hoja, profundidad máxima 20"],
        ["Fuerza bruta", "recorre la lista completa de puntos, mismo lenguaje (Python puro)"],
        ["Equipo", f"{platform.platform()}, CPU: {platform.processor()}"],
        ["Python", platform.python_version()],
    ]))

    w("\n## 2. Resultados con puntos uniformes (tiempo por consulta en µs)\n")
    filas = []
    for k in range(len(TAMANOS)):
        filas.append([TAMANOS[k],
                      f"{r['radio_bf'][k] * 1e6:.1f}", f"{r['radio_qt'][k] * 1e6:.1f}", f"{r['acel_radio'][k]:.2f}x",
                      f"{r['vecino_bf'][k] * 1e6:.1f}", f"{r['vecino_qt'][k] * 1e6:.1f}", f"{r['acel_vecino'][k]:.2f}x"])
    w(tabla(["N", "Radio: fuerza bruta", "Radio: Quadtree", "Aceleración radio",
             "Vecino: fuerza bruta", "Vecino: Quadtree", "Aceleración vecino"], filas))

    w("\n## 3. Respuesta a la pregunta del enunciado\n")
    n_radio = resumen["cruce_radio"]
    n_vecino = resumen["cruce_vecino"]
    n_radio_ag = resumen["cruce_radio_agrupado"]
    w(f"- **Búsqueda por radio ({RADIO} m), puntos uniformes:** el Quadtree empieza a ser más rápido desde "
      f"N = {texto_n(n_radio)} (y se mantiene más rápido para todos los N mayores medidos). "
      f"El último tamaño donde todavía perdía era N = {texto_n(anterior_en_rejilla(n_radio) if n_radio else None)}.")
    w(f"- **Vecino más cercano, puntos uniformes:** desde N = {texto_n(n_vecino)}.")
    w(f"- **Búsqueda por radio con puntos agrupados (barrios):** desde N = {texto_n(n_radio_ag)}.")
    w(f"- Con N = {n_final} puntos (el caso del enunciado) el Quadtree es {r['acel_radio'][i]:.1f} veces más rápido en radio "
      f"y {r['acel_vecino'][i]:.1f} veces en vecino más cercano.")
    w("- El punto de cruce depende de la rejilla de N medida y de la máquina: es una estimación, no un valor exacto.\n")

    w("## 4. Cuántas distancias se calculan por consulta (no depende de la máquina)\n")
    filas = []
    for k in range(len(TAMANOS)):
        filas.append([TAMANOS[k], TAMANOS[k], f"{r['dist_radio_qt'][k]:.1f}", f"{r['visitas_radio'][k]:.1f}",
                      f"{r['dist_vecino_qt'][k]:.1f}", f"{r['visitas_vecino'][k]:.1f}"])
    w(tabla(["N", "Fuerza bruta (distancias)", "Quadtree radio (distancias)", "Quadtree radio (nodos visitados)",
             "Quadtree vecino (distancias)", "Quadtree vecino (nodos visitados)"], filas))
    w(f"\nLa fuerza bruta siempre calcula N distancias. Con N = {n_final} el Quadtree en radio calcula "
      f"{r['dist_radio_qt'][i]:.0f} distancias y visita {r['visitas_radio'][i]:.0f} nodos; "
      f"{r['hallados_radio'][i]:.1f} de esos puntos están dentro del radio.")
    w(f"Eso es {n_final / r['dist_radio_qt'][i]:.0f} veces menos distancias, pero el tiempo mejora solo "
      f"{r['acel_radio'][i]:.1f} veces: recorrer nodos, llamar funciones y comparar rectángulos también cuesta.\n")

    w("## 5. Costo de construir el árbol y cuándo se paga\n")
    filas = []
    for k in range(len(TAMANOS)):
        q = resumen["compensar"][k]
        filas.append([TAMANOS[k], f"{r['construccion'][k] * 1e3:.2f}", "nunca (pierde en radio)" if q is None else f"{q:.0f}"])
    w(tabla(["N", "Construcción (ms)", "Consultas de radio para compensar la construcción"], filas))
    w("\nSi los puntos son estáticos (como pide el ejercicio) el árbol se construye una vez y se reutiliza, "
      "así que este costo se reparte entre todas las consultas.\n")

    w("## 6. Efecto del radio (N = 10.000)\n")
    filas = []
    for k in range(len(RADIOS)):
        filas.append([RADIOS[k], f"{resumen['hallados_radios'][k]:.1f}", f"{resumen['radios_bf'][k] * 1e6:.1f}",
                      f"{resumen['radios_qt'][k] * 1e6:.1f}", f"{resumen['radios_acel'][k]:.2f}x"])
    w(tabla(["Radio (m)", "Puntos encontrados (promedio)", "Fuerza bruta (µs)", "Quadtree (µs)", "Aceleración"], filas))
    w(f"\nMientras más grande el radio, más puntos hay que devolver y menos nodos se pueden descartar, "
      f"por eso la aceleración baja. Radio más grande probado donde el Quadtree sigue ganando: "
      f"{resumen['radio_limite']} m.\n")

    w("## 7. Discusión\n")
    w("- La fuerza bruta cuesta O(N): cada consulta revisa todos los puntos. Su tiempo crece en línea recta con N.")
    w("- El Quadtree descarta rectángulos enteros que quedan fuera del radio, así que solo revisa los puntos de "
      "la zona cercana. Su costo crece muy lento con N (aproximadamente con la altura del árbol más los puntos que "
      "realmente están cerca).")
    w("- Con N pequeño el Quadtree no gana porque cada nodo visitado cuesta una llamada de función y una comparación "
      "con el rectángulo, y con pocos puntos la fuerza bruta ya es casi instantánea. Esa sobrecarga es el costo "
      "constante que el ahorro de comparaciones tiene que superar.")
    w("- Las gráficas usan ejes lineales a propósito: en un eje logarítmico una diferencia de 10 veces se ve como un "
      "paso corto y las curvas parecen cercanas. Con ejes lineales la brecha se ve tal cual, y la gráfica de "
      "aceleración muestra directamente cuántas veces gana un método.")
    w(f"- Con puntos agrupados y N = {n_final} la aceleración en radio es {resumen['acel_agrupado_final']:.1f}x "
      f"(con puntos uniformes: {r['acel_radio'][i]:.1f}x). Se probó para ver si la distribución de los puntos cambia la conclusión.\n")
    w("## 8. Limitaciones\n")
    w("- Mediciones en Python puro y en un solo equipo: sirven para comparar tendencias y proporciones, no tiempos absolutos.")
    w("- Una fuerza bruta con NumPy (vectorizada) sería mucho más rápida que la de listas y movería el punto de cruce; "
      "aquí se compara con listas porque es lo que pide el enunciado.")
    w("- Los contadores de nodos y distancias suman una pequeña sobrecarga al Quadtree, lo que juega en su contra.")
    w("- La rejilla de N es finita: el punto de cruce real está entre el último N donde pierde y el primero donde gana.")
    w("- Datos sintéticos (uniformes y agrupados), no coordenadas reales de una ciudad.")
    return "\n".join(lineas) + "\n"


# ====================================================================== principal
def main():
    os.makedirs("graficas", exist_ok=True)
    os.makedirs("resultados", exist_ok=True)
    calentar()

    filas = []
    for distribucion in ("uniforme", "agrupado"):
        for n in TAMANOS:
            for rep in range(REPETICIONES):
                filas.append(medir_tamano(n, rep, distribucion))
            print(f"{distribucion:9s} N={n:>6} listo")

    filas_radios = []
    for radio in RADIOS:
        for rep in range(REPETICIONES_RADIOS):
            filas_radios.append(medir_radios(radio, rep))
        print(f"radio {radio} m listo")

    with open("resultados/resultados_crudos.csv", "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)

    # ---- resúmenes para uniforme
    r = {}
    r["radio_bf"], e_radio_bf = por_n(filas, "uniforme", "t_radio_bf")
    r["radio_qt"], e_radio_qt = por_n(filas, "uniforme", "t_radio_qt")
    r["vecino_bf"], e_vecino_bf = por_n(filas, "uniforme", "t_vecino_bf")
    r["vecino_qt"], e_vecino_qt = por_n(filas, "uniforme", "t_vecino_qt")
    r["construccion"], e_construccion = por_n(filas, "uniforme", "t_construccion")
    r["dist_radio_qt"], _ = por_n(filas, "uniforme", "dist_radio_qt")
    r["visitas_radio"], _ = por_n(filas, "uniforme", "visitas_radio")
    r["dist_vecino_qt"], _ = por_n(filas, "uniforme", "dist_vecino_qt")
    r["visitas_vecino"], _ = por_n(filas, "uniforme", "visitas_vecino")
    r["hallados_radio"], _ = por_n(filas, "uniforme", "hallados_radio")
    r["acel_radio"] = dividir(r["radio_bf"], r["radio_qt"])
    r["acel_vecino"] = dividir(r["vecino_bf"], r["vecino_qt"])

    ag_radio_bf, _ = por_n(filas, "agrupado", "t_radio_bf")
    ag_radio_qt, _ = por_n(filas, "agrupado", "t_radio_qt")
    acel_agrupado = dividir(ag_radio_bf, ag_radio_qt)

    resumen = {
        "acel_agrupado_final": acel_agrupado[-1],
        "cruce_radio": primer_n_ganador(TAMANOS, r["radio_bf"], r["radio_qt"]),
        "cruce_vecino": primer_n_ganador(TAMANOS, r["vecino_bf"], r["vecino_qt"]),
        "cruce_radio_agrupado": primer_n_ganador(TAMANOS, ag_radio_bf, ag_radio_qt),
    }
    compensar = []
    for k in range(len(TAMANOS)):
        compensar.append(consultas_para_compensar(r["construccion"][k], r["radio_bf"][k], r["radio_qt"][k]))
    resumen["compensar"] = compensar

    # ---- resumen del experimento de radios
    r_bf, r_qt, r_hall, e_bf, e_qt = [], [], [], [], []
    for radio in RADIOS:
        bf, qt, hall = [], [], []
        for f in filas_radios:
            if f["radio"] == radio:
                bf.append(f["t_bf"])
                qt.append(f["t_qt"])
                hall.append(f["hallados"])
        r_bf.append(statistics.mean(bf))
        r_qt.append(statistics.mean(qt))
        r_hall.append(statistics.mean(hall))
        e_bf.append(statistics.stdev(bf))
        e_qt.append(statistics.stdev(qt))
    resumen["radios_bf"] = r_bf
    resumen["radios_qt"] = r_qt
    resumen["hallados_radios"] = r_hall
    resumen["radios_acel"] = dividir(r_bf, r_qt)
    limite = "ninguno de los probados"
    for k in range(len(RADIOS)):
        if resumen["radios_acel"][k] > 1:
            limite = RADIOS[k]
    resumen["radio_limite"] = limite

    # ---- gráficas
    n_cruce = resumen["cruce_radio"]
    grafica_dos_paneles("04_tiempo_radio_vs_N.png", f"Búsqueda por radio de {RADIO} m: tiempo por consulta",
                        "Tiempo por consulta (µs)",
                        [("Fuerza bruta", multiplicar(r["radio_bf"], 1e6), multiplicar(e_radio_bf, 1e6), COLOR_BF, "-"),
                         ("Quadtree", multiplicar(r["radio_qt"], 1e6), multiplicar(e_radio_qt, 1e6), COLOR_QT, "-")],
                        n_cruce=n_cruce)
    grafica_dos_paneles("05_tiempo_vecino_vs_N.png", "Vecino más cercano: tiempo por consulta",
                        "Tiempo por consulta (µs)",
                        [("Fuerza bruta", multiplicar(r["vecino_bf"], 1e6), multiplicar(e_vecino_bf, 1e6), COLOR_BF, "-"),
                         ("Quadtree", multiplicar(r["vecino_qt"], 1e6), multiplicar(e_vecino_qt, 1e6), COLOR_QT, "-")],
                        n_cruce=resumen["cruce_vecino"])
    grafica_dos_paneles("06_aceleracion_vs_N.png",
                        "Aceleración del Quadtree = tiempo fuerza bruta / tiempo Quadtree (por encima de 1 gana el Quadtree)",
                        "Veces más rápido",
                        [("Radio, puntos uniformes", r["acel_radio"], None, COLOR_QT, "-"),
                         ("Vecino más cercano, puntos uniformes", r["acel_vecino"], None, COLOR_3, "-"),
                         ("Radio, puntos agrupados", acel_agrupado, None, COLOR_BF, "--")],
                        n_cruce=n_cruce, linea_en_1=True)
    grafica_dos_paneles("07_distancias_vs_N.png", "Distancias calculadas por consulta (no depende de la máquina)",
                        "Distancias calculadas por consulta",
                        [("Fuerza bruta (siempre N)", TAMANOS, None, COLOR_BF, "-"),
                         ("Quadtree, radio", r["dist_radio_qt"], None, COLOR_QT, "-"),
                         ("Quadtree, vecino más cercano", r["dist_vecino_qt"], None, COLOR_3, "-")])
    grafica_dos_paneles("08_construccion_vs_N.png", "Tiempo de construir el Quadtree",
                        "Tiempo de construcción (ms)",
                        [("Quadtree", multiplicar(r["construccion"], 1e3), multiplicar(e_construccion, 1e3), COLOR_QT, "-")])
    grafica_radios("09_efecto_del_radio.png", RADIOS, r_bf, r_qt, e_bf, e_qt)

    with open("resultados/informe_analisis.md", "w", encoding="utf-8") as f:
        f.write(escribir_informe(r, resumen))

    print("\nListo. Revisa resultados/informe_analisis.md y graficas/")
    print(f"El Quadtree gana en búsqueda por radio desde N = {resumen['cruce_radio']}")
    print(f"El Quadtree gana en vecino más cercano desde N = {resumen['cruce_vecino']}")


if __name__ == "__main__":
    main()
