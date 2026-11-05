"""
Pruebas unitarias, verificaciones visuales y análisis de las pruebas.

    python test.py            (o también: pytest test.py)

Genera graficas/01_verificacion_radio.png, 02_verificacion_vecinos.png, 03_estructura_pequena.png
y resultados/analisis_pruebas.txt
"""
import math
import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

from Quadtreetree import (Quadtree, construir, generar_puntos,
                          radio_fuerza_bruta, mas_cercano_fuerza_bruta,
                          k_cercanos_fuerza_bruta)

LADO = 10000
N = 10000
RADIO = 500


# ====================================================================== pruebas unitarias
def test_subdivision_con_puntos_conocidos():
    arbol = Quadtree(0, 0, 10, 10)
    for (x, y) in [(1, 1), (9, 1), (1, 9), (9, 9)]:
        arbol.insertar(x, y)
    assert arbol.raiz.hijos is None            # con 4 puntos todavía es hoja
    arbol.insertar(2, 2)                       # el 5.º punto obliga a subdividir
    assert arbol.raiz.hijos is not None
    cantidades = []
    for hijo in arbol.raiz.hijos:
        cantidades.append(len(hijo.puntos))
    assert cantidades == [2, 1, 1, 1]          # SO, SE, NO, NE


def test_construccion_conserva_todos_los_puntos():
    puntos = generar_puntos(N, LADO, 1)
    arbol = construir(puntos, LADO)
    assert arbol.contar_puntos() == N
    for hoja in arbol.hojas():                 # cada punto está dentro del rectángulo de su hoja
        for (x, y) in hoja.puntos:
            assert hoja.xmin <= x <= hoja.xmax
            assert hoja.ymin <= y <= hoja.ymax


def test_radio_igual_a_fuerza_bruta():
    puntos = generar_puntos(N, LADO, 2)
    arbol = construir(puntos, LADO)
    consultas = generar_puntos(300, LADO, 3)
    for radio in (100, 500, 1500):
        for (x, y) in consultas:
            esperado = sorted(radio_fuerza_bruta(puntos, x, y, radio))
            obtenido = sorted(arbol.buscar_radio(x, y, radio))
            assert obtenido == esperado


def test_unidades_triangulo_3_4_5():
    arbol = Quadtree(0, 0, LADO, LADO)
    arbol.insertar(1300, 1400)    # dx=300, dy=400 -> distancia exacta 500 m
    arbol.insertar(1300, 1401)    # distancia 500.001 m, queda afuera
    arbol.insertar(1000, 1000)    # el propio centro
    encontrados = arbol.buscar_radio(1000, 1000, 500)
    assert sorted(encontrados) == [(1000, 1000), (1300, 1400)]


def test_radio_cero_y_sin_vecinos():
    arbol = Quadtree(0, 0, LADO, LADO)
    arbol.insertar(5000, 5000)
    assert arbol.buscar_radio(5000, 5000, 0) == [(5000, 5000)]
    assert arbol.buscar_radio(100, 100, 500) == []


def test_mas_cercano_igual_a_fuerza_bruta():
    puntos = generar_puntos(N, LADO, 4)
    arbol = construir(puntos, LADO)
    consultas = generar_puntos(300, LADO, 5)
    consultas.append((-3000, 4000))            # consultas fuera del área también deben funcionar
    consultas.append((15000, 15000))
    for (x, y) in consultas:
        d_arbol, _ = arbol.mas_cercano(x, y)
        d_bruta, _ = mas_cercano_fuerza_bruta(puntos, x, y)
        assert math.isclose(d_arbol, d_bruta)


def test_k_cercanos_igual_a_fuerza_bruta():
    puntos = generar_puntos(N, LADO, 6)
    arbol = construir(puntos, LADO)
    consultas = generar_puntos(100, LADO, 7)
    for k in (1, 5, 10):
        for (x, y) in consultas:
            d_arbol = []
            for d, _ in arbol.k_cercanos(x, y, k):
                d_arbol.append(d)
            d_bruta = []
            for d, _ in k_cercanos_fuerza_bruta(puntos, x, y, k):
                d_bruta.append(d)
            assert d_arbol == d_bruta


def test_puntos_repetidos():
    arbol = Quadtree(0, 0, LADO, LADO)
    for _ in range(50):
        arbol.insertar(2500, 2500)             # sin PROFUNDIDAD_MAX esto nunca terminaría
    assert arbol.contar_puntos() == 50
    assert len(arbol.buscar_radio(2500, 2500, 1)) == 50


def test_arbol_vacio_y_un_punto():
    arbol = Quadtree(0, 0, LADO, LADO)
    assert arbol.buscar_radio(10, 10, 500) == []
    assert arbol.mas_cercano(10, 10) is None
    arbol.insertar(3000, 3000)
    assert arbol.mas_cercano(3000, 4000) == (1000.0, (3000, 3000))
    assert len(arbol.k_cercanos(0, 0, 5)) == 1   # k mayor que la cantidad de puntos


def test_punto_fuera_del_area():
    arbol = Quadtree(0, 0, LADO, LADO)
    try:
        arbol.insertar(-1, 5)
        assert False, "debió lanzar ValueError"
    except ValueError:
        pass


# ====================================================================== análisis de las pruebas
def analisis_de_pruebas():
    puntos = generar_puntos(N, LADO, 10)
    arbol = construir(puntos, LADO)
    consultas = generar_puntos(1000, LADO, 11)
    hojas = arbol.hojas()
    vacias = 0
    for h in hojas:
        if len(h.puntos) == 0:
            vacias += 1

    cantidades = []
    distintos = 0
    for (x, y) in consultas:
        a = sorted(arbol.buscar_radio(x, y, RADIO))
        b = sorted(radio_fuerza_bruta(puntos, x, y, RADIO))
        cantidades.append(len(a))
        if a != b:
            distintos += 1

    distancias = []
    for (x, y) in consultas:
        d_arbol, _ = arbol.mas_cercano(x, y)
        d_bruta, _ = mas_cercano_fuerza_bruta(puntos, x, y)
        distancias.append(d_arbol)
        if not math.isclose(d_arbol, d_bruta):
            distintos += 1

    esperado = N / (LADO * LADO) * math.pi * RADIO ** 2
    lineas = [
        f"Quadtree con N = {N} puntos en {LADO} m x {LADO} m (capacidad por hoja = 4)",
        f"  hojas: {len(hojas)} (vacías: {vacias}), altura: {arbol.altura()}, "
        f"puntos por hoja: {N / len(hojas):.2f}",
        f"Búsqueda por radio de {RADIO} m con 1000 consultas aleatorias",
        f"  vecinos encontrados: mínimo {min(cantidades)}, máximo {max(cantidades)}, "
        f"promedio {sum(cantidades) / len(cantidades):.1f}",
        f"  promedio teórico sin efecto de borde: densidad x área = {esperado:.1f}",
        f"Vecino más cercano con 1000 consultas aleatorias",
        f"  distancia promedio: {sum(distancias) / len(distancias):.1f} m, máxima: {max(distancias):.1f} m",
        f"Diferencias entre Quadtree y fuerza bruta en las 2000 verificaciones: {distintos}",
    ]
    return lineas


# ====================================================================== visualizaciones
def dibujar_hojas(ax, arbol, xlim=None, ylim=None):
    for h in arbol.hojas():
        if xlim is not None:
            if h.xmax < xlim[0] or h.xmin > xlim[1] or h.ymax < ylim[0] or h.ymin > ylim[1]:
                continue
        ax.add_patch(Rectangle((h.xmin, h.ymin), h.xmax - h.xmin, h.ymax - h.ymin,
                               fill=False, edgecolor="#bbbbbb", linewidth=0.5))


def puntos_en_ventana(puntos, xlim, ylim):
    resultado = []
    for (x, y) in puntos:
        if xlim[0] <= x <= xlim[1] and ylim[0] <= y <= ylim[1]:
            resultado.append((x, y))
    return resultado


def separar_xy(lista):
    xs = []
    ys = []
    for (x, y) in lista:
        xs.append(x)
        ys.append(y)
    return xs, ys


def visualizar_radio(puntos, arbol):
    qx, qy = 4200, 6100
    encontrados = arbol.buscar_radio(qx, qy, RADIO)
    en_conjunto = set(encontrados)
    no_encontrados = []
    for p in puntos:
        if p not in en_conjunto:
            no_encontrados.append(p)
    bruta = radio_fuerza_bruta(puntos, qx, qy, RADIO)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5))

    # ciudad completa
    dibujar_hojas(ax1, arbol)
    xs, ys = separar_xy(no_encontrados)
    ax1.scatter(xs, ys, s=1, color="#888888")
    xs, ys = separar_xy(encontrados)
    ax1.scatter(xs, ys, s=8, color="red")
    ax1.add_patch(Circle((qx, qy), RADIO, fill=False, edgecolor="red", linewidth=1.5))
    ax1.set_xlim(0, LADO)
    ax1.set_ylim(0, LADO)
    ax1.set_title(f"Ciudad completa ({N} puntos de entrega)")

    # zoom alrededor de la consulta
    mitad = RADIO * 1.6
    xlim = (qx - mitad, qx + mitad)
    ylim = (qy - mitad, qy + mitad)
    dibujar_hojas(ax2, arbol, xlim, ylim)
    xs, ys = separar_xy(puntos_en_ventana(no_encontrados, xlim, ylim))
    ax2.scatter(xs, ys, s=14, color="#555555", label="fuera del radio")
    xs, ys = separar_xy(encontrados)
    ax2.scatter(xs, ys, s=22, color="red", label=f"dentro del radio ({len(encontrados)})")
    ax2.add_patch(Circle((qx, qy), RADIO, fill=False, edgecolor="red", linewidth=1.5))
    ax2.scatter([qx], [qy], marker="*", s=250, color="black", label="punto de consulta", zorder=5)
    ax2.set_xlim(*xlim)
    ax2.set_ylim(*ylim)
    ax2.set_title(f"Zoom (radio {RADIO} m): Quadtree {len(encontrados)} puntos, "
                  f"fuerza bruta {len(bruta)} puntos", fontsize=10)
    ax2.legend(loc="upper right", fontsize=8)

    for ax in (ax1, ax2):
        ax.set_aspect("equal")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
    fig.suptitle("Verificación visual de la búsqueda por radio (rectángulos grises = hojas del Quadtree)",
                 fontweight="bold")
    fig.savefig("graficas/01_verificacion_radio.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def visualizar_vecinos(puntos, arbol):
    qx, qy = 7300, 2500
    vecinos = arbol.k_cercanos(qx, qy, 5)
    d1 = vecinos[0][0]
    d5 = vecinos[-1][0]
    mitad = d5 * 2.2
    xlim = (qx - mitad, qx + mitad)
    ylim = (qy - mitad, qy + mitad)
    cercanos = puntos_en_ventana(puntos, xlim, ylim)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5))
    for ax in (ax1, ax2):
        dibujar_hojas(ax, arbol, xlim, ylim)
        xs, ys = separar_xy(cercanos)
        ax.scatter(xs, ys, s=14, color="#555555")
        ax.scatter([qx], [qy], marker="*", s=250, color="black", zorder=5, label="punto de consulta")
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")

    # izquierda: el más cercano
    px, py = vecinos[0][1]
    ax1.add_patch(Circle((qx, qy), d1, fill=False, edgecolor="green", linewidth=1.5))
    ax1.plot([qx, px], [qy, py], color="green")
    ax1.scatter([px], [py], s=60, color="green", label=f"más cercano ({d1:.1f} m)", zorder=4)
    ax1.set_title("Vecino más cercano (el círculo no contiene ningún otro punto)")
    ax1.legend(loc="upper right", fontsize=8)

    # derecha: los 5 más cercanos
    ax2.add_patch(Circle((qx, qy), d5, fill=False, edgecolor="blue", linewidth=1.5))
    desplazamientos = [(8, -16), (8, 6), (-62, 8), (8, 6), (8, 6)]   # para que las etiquetas no se tapen
    numero = 1
    for d, (px, py) in vecinos:
        ax2.plot([qx, px], [qy, py], color="blue", linewidth=0.8)
        ax2.scatter([px], [py], s=60, color="blue", zorder=4)
        ax2.annotate(f"{numero}: {d:.0f} m", (px, py), textcoords="offset points", xytext=desplazamientos[numero - 1], fontsize=9)
        numero += 1
    ax2.set_title("Los 5 vecinos más cercanos (numerados por distancia)")
    ax2.legend(loc="upper right", fontsize=8)

    fig.suptitle("Verificación visual de los vecinos más cercanos", fontweight="bold")
    fig.savefig("graficas/02_verificacion_vecinos.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def visualizar_estructura_pequena():
    puntos = generar_puntos(40, 100, 8)
    arbol = construir(puntos, 100)
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    dibujar_hojas(ax, arbol)
    xs, ys = separar_xy(puntos)
    ax.scatter(xs, ys, s=25, color="#2E86AB")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")
    ax.set_title(f"Quadtree con 40 puntos: {len(arbol.hojas())} hojas, altura {arbol.altura()}\n"
                 "(donde hay más puntos, las celdas son más pequeñas)")
    fig.savefig("graficas/03_estructura_pequena.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ====================================================================== ejecución
if __name__ == "__main__":
    os.makedirs("graficas", exist_ok=True)
    os.makedirs("resultados", exist_ok=True)

    pruebas = []
    for nombre, funcion in sorted(globals().items()):
        if nombre.startswith("test_"):
            pruebas.append((nombre, funcion))
    for nombre, funcion in pruebas:
        funcion()
        print("OK ", nombre)
    print(f"\nTodas las pruebas pasaron ({len(pruebas)}).\n")

    lineas = analisis_de_pruebas()
    for linea in lineas:
        print(linea)
    with open("resultados/analisis_pruebas.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    puntos = generar_puntos(N, LADO, 10)
    arbol = construir(puntos, LADO)
    visualizar_radio(puntos, arbol)
    visualizar_vecinos(puntos, arbol)
    visualizar_estructura_pequena()
    print("\nGráficas guardadas en graficas/")
