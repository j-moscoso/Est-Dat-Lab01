"""
Quadtree 2D hecho desde cero + búsqueda por fuerza bruta.
Todas las coordenadas y distancias están en metros.
"""
import math
import random

CAPACIDAD = 4          # puntos máximos en una hoja antes de subdividirla
PROFUNDIDAD_MAX = 20   # tope para que puntos repetidos no subdividan para siempre


class Nodo:
    def __init__(self, xmin, ymin, xmax, ymax, profundidad):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.profundidad = profundidad
        self.puntos = []     # solo se usa si el nodo es hoja
        self.hijos = None    # None = hoja; si no, lista de 4 nodos [SO, SE, NO, NE]


def distancia2_a_nodo(nodo, x, y):
    """Distancia al cuadrado desde (x, y) hasta el rectángulo del nodo (0 si está dentro)."""
    dx = max(nodo.xmin - x, 0, x - nodo.xmax)
    dy = max(nodo.ymin - y, 0, y - nodo.ymax)
    return dx * dx + dy * dy


class Quadtree:
    def __init__(self, xmin, ymin, xmax, ymax):
        self.raiz = Nodo(xmin, ymin, xmax, ymax, 0)
        self.visitas = 0      # nodos visitados (solo para el análisis)
        self.distancias = 0   # distancias a puntos calculadas (solo para el análisis)

    # ---------------------------------------------------------- construcción
    def insertar(self, x, y):
        r = self.raiz
        if not (r.xmin <= x <= r.xmax and r.ymin <= y <= r.ymax):
            raise ValueError("el punto está fuera del área del Quadtree")
        self._insertar(r, (x, y))

    def _insertar(self, nodo, punto):
        if nodo.hijos is None:
            if len(nodo.puntos) < CAPACIDAD or nodo.profundidad >= PROFUNDIDAD_MAX:
                nodo.puntos.append(punto)
                return
            self._subdividir(nodo)
        i = self._indice_hijo(nodo, punto[0], punto[1])
        self._insertar(nodo.hijos[i], punto)

    def _indice_hijo(self, nodo, x, y):
        xmed = (nodo.xmin + nodo.xmax) / 2
        ymed = (nodo.ymin + nodo.ymax) / 2
        i = 0
        if x >= xmed:
            i += 1
        if y >= ymed:
            i += 2
        return i

    def _subdividir(self, nodo):
        xmed = (nodo.xmin + nodo.xmax) / 2
        ymed = (nodo.ymin + nodo.ymax) / 2
        p = nodo.profundidad + 1
        nodo.hijos = [
            Nodo(nodo.xmin, nodo.ymin, xmed, ymed, p),   # 0 = SO
            Nodo(xmed, nodo.ymin, nodo.xmax, ymed, p),   # 1 = SE
            Nodo(nodo.xmin, ymed, xmed, nodo.ymax, p),   # 2 = NO
            Nodo(xmed, ymed, nodo.xmax, nodo.ymax, p),   # 3 = NE
        ]
        for punto in nodo.puntos:
            i = self._indice_hijo(nodo, punto[0], punto[1])
            self._insertar(nodo.hijos[i], punto)
        nodo.puntos = []

    # ---------------------------------------------------------- búsqueda por radio
    def buscar_radio(self, x, y, radio):
        encontrados = []
        self._radio(self.raiz, x, y, radio * radio, encontrados)
        return encontrados

    def _radio(self, nodo, x, y, r2, encontrados):
        self.visitas += 1
        if distancia2_a_nodo(nodo, x, y) > r2:
            return
        if nodo.hijos is None:
            for (px, py) in nodo.puntos:
                self.distancias += 1
                if (px - x) ** 2 + (py - y) ** 2 <= r2:
                    encontrados.append((px, py))
        else:
            for hijo in nodo.hijos:
                self._radio(hijo, x, y, r2, encontrados)

    # ---------------------------------------------------------- vecinos más cercanos
    def k_cercanos(self, x, y, k):
        """Devuelve [(distancia, punto), ...] de los k puntos más cercanos, de menor a mayor."""
        mejores = []   # lista de (distancia al cuadrado, punto), siempre ordenada
        self._cercanos(self.raiz, x, y, k, mejores)
        resultado = []
        for d2, punto in mejores:
            resultado.append((math.sqrt(d2), punto))
        return resultado

    def mas_cercano(self, x, y):
        resultado = self.k_cercanos(x, y, 1)
        if len(resultado) == 0:
            return None
        return resultado[0]

    def _cercanos(self, nodo, x, y, k, mejores):
        self.visitas += 1
        if len(mejores) == k and distancia2_a_nodo(nodo, x, y) > mejores[-1][0]:
            return
        if nodo.hijos is None:
            for punto in nodo.puntos:
                self.distancias += 1
                d2 = (punto[0] - x) ** 2 + (punto[1] - y) ** 2
                if len(mejores) < k or d2 < mejores[-1][0]:
                    mejores.append((d2, punto))
                    mejores.sort()
                    if len(mejores) > k:
                        mejores.pop()
        else:
            primero = self._indice_hijo(nodo, x, y)
            self._cercanos(nodo.hijos[primero], x, y, k, mejores)
            for i in range(4):
                if i != primero:
                    self._cercanos(nodo.hijos[i], x, y, k, mejores)

    # ---------------------------------------------------------- utilidades
    def hojas(self):
        resultado = []
        pila = [self.raiz]
        while len(pila) > 0:
            nodo = pila.pop()
            if nodo.hijos is None:
                resultado.append(nodo)
            else:
                pila.extend(nodo.hijos)
        return resultado

    def contar_puntos(self):
        total = 0
        for hoja in self.hojas():
            total += len(hoja.puntos)
        return total

    def altura(self):
        mayor = 0
        for hoja in self.hojas():
            if hoja.profundidad > mayor:
                mayor = hoja.profundidad
        return mayor


# -------------------------------------------------------------- fuerza bruta
def radio_fuerza_bruta(puntos, x, y, radio):
    encontrados = []
    r2 = radio * radio
    for (px, py) in puntos:
        if (px - x) ** 2 + (py - y) ** 2 <= r2:
            encontrados.append((px, py))
    return encontrados


def mas_cercano_fuerza_bruta(puntos, x, y):
    mejor = None
    mejor_d2 = 0
    for punto in puntos:
        d2 = (punto[0] - x) ** 2 + (punto[1] - y) ** 2
        if mejor is None or d2 < mejor_d2:
            mejor = punto
            mejor_d2 = d2
    if mejor is None:
        return None
    return (math.sqrt(mejor_d2), mejor)


def k_cercanos_fuerza_bruta(puntos, x, y, k):
    todos = []
    for punto in puntos:
        d2 = (punto[0] - x) ** 2 + (punto[1] - y) ** 2
        todos.append((d2, punto))
    todos.sort()
    resultado = []
    for d2, punto in todos[:k]:
        resultado.append((math.sqrt(d2), punto))
    return resultado


# -------------------------------------------------------------- datos de prueba
def generar_puntos(n, lado=10000, semilla=0):
    """n puntos uniformes en un cuadrado de lado x lado metros."""
    azar = random.Random(semilla)
    puntos = []
    for _ in range(n):
        puntos.append((azar.uniform(0, lado), azar.uniform(0, lado)))
    return puntos


def generar_puntos_agrupados(n, lado=10000, semilla=0, centros=5, dispersion=800):
    """n puntos concentrados alrededor de unos pocos centros (como barrios de una ciudad)."""
    azar = random.Random(semilla)
    lista_centros = []
    for _ in range(centros):
        lista_centros.append((azar.uniform(0, lado), azar.uniform(0, lado)))
    puntos = []
    while len(puntos) < n:
        cx, cy = azar.choice(lista_centros)
        x = azar.gauss(cx, dispersion)
        y = azar.gauss(cy, dispersion)
        if 0 <= x <= lado and 0 <= y <= lado:
            puntos.append((x, y))
    return puntos


def construir(puntos, lado=10000):
    arbol = Quadtree(0, 0, lado, lado)
    for (x, y) in puntos:
        arbol.insertar(x, y)
    return arbol
