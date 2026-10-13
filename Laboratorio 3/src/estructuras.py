"""
Tres estrategias de almacenamiento y búsqueda para el sistema de estudiantes.

Todas exponen la misma interfaz:
    insertar(registro) -> bool      (False si el ID ya existía y no se insertó; la Lista no verifica)
    buscar(id)         -> dict|None
    listar()           -> list[dict] ordenada ascendentemente por ID
    altura()           -> int|None   (niveles del árbol; None si no aplica)
    pasos_medios(ids)  -> float      (comparaciones/niveles promedio para buscar esos IDs; NO se cronometra)

Un registro es un dict: {"id": int, "nombre": str, "edad": int, "promedio": float}.

Decisión de diseño: todo está escrito en Python "puro" con bucles explícitos (sin recursión,
para que un ABB degenerado de 100.000 nodos no desborde la pila). La única excepción
configurable es el B+, que puede usar `bisect` (implementado en C) dentro de cada nodo.
"""
from bisect import bisect_left, bisect_right
from operator import itemgetter

_clave_id = itemgetter("id")


# --------------------------------------------------------------------------------------
# 1) Lista (arreglo dinámico de Python, sin ordenar)
# --------------------------------------------------------------------------------------
class ListaEstudiantes:
    """Lista sin ordenar. insertar: O(1) amortizado. buscar: O(N) (búsqueda lineal).
    listar: ordena una copia con Timsort -> O(N log N) (O(N) si ya venía ordenada).

    Nota: NO verifica IDs duplicados al insertar (verificarlo costaría O(N) por inserción).
    El generador de datos garantiza IDs únicos."""

    def __init__(self):
        self.datos = []

    def __len__(self):
        return len(self.datos)

    def insertar(self, registro):
        self.datos.append(registro)
        return True

    def buscar(self, id_):
        for r in self.datos:
            if r["id"] == id_:
                return r
        return None

    def listar(self):
        return sorted(self.datos, key=_clave_id)

    def altura(self):
        return None

    def pasos_medios(self, ids):
        # Buscar el elemento en la posición i cuesta i+1 comparaciones.
        pos = {r["id"]: i + 1 for i, r in enumerate(self.datos)}
        return sum(pos[i] for i in ids) / len(ids)


# --------------------------------------------------------------------------------------
# 2) Árbol binario de búsqueda (sin balanceo)
# --------------------------------------------------------------------------------------
class _NodoABB:
    __slots__ = ("id", "registro", "izq", "der")

    def __init__(self, registro):
        self.id = registro["id"]
        self.registro = registro
        self.izq = None
        self.der = None


class ABB:
    """ABB sin balanceo. Caso promedio (IDs aleatorios): altura ~ O(log N).
    Peor caso (IDs insertados en orden): altura = N, y buscar/insertar son O(N)."""

    def __init__(self):
        self.raiz = None
        self.n = 0

    def __len__(self):
        return self.n

    def insertar(self, registro):
        clave = registro["id"]
        nuevo = _NodoABB(registro)
        if self.raiz is None:
            self.raiz = nuevo
            self.n = 1
            return True
        actual = self.raiz
        while True:
            if clave < actual.id:
                if actual.izq is None:
                    actual.izq = nuevo
                    break
                actual = actual.izq
            elif clave > actual.id:
                if actual.der is None:
                    actual.der = nuevo
                    break
                actual = actual.der
            else:
                return False  # ID duplicado
        self.n += 1
        return True

    def buscar(self, id_):
        actual = self.raiz
        while actual is not None:
            if id_ < actual.id:
                actual = actual.izq
            elif id_ > actual.id:
                actual = actual.der
            else:
                return actual.registro
        return None

    def listar(self):
        """Recorrido inorden iterativo -> IDs en orden ascendente. O(N)."""
        resultado = []
        pila = []
        actual = self.raiz
        while pila or actual is not None:
            while actual is not None:
                pila.append(actual)
                actual = actual.izq
            actual = pila.pop()
            resultado.append(actual.registro)
            actual = actual.der
        return resultado

    def _profundidades(self):
        """dict id -> profundidad (la raíz tiene profundidad 1). O(N), iterativo."""
        prof = {}
        if self.raiz is None:
            return prof
        pila = [(self.raiz, 1)]
        while pila:
            nodo, d = pila.pop()
            prof[nodo.id] = d
            if nodo.izq is not None:
                pila.append((nodo.izq, d + 1))
            if nodo.der is not None:
                pila.append((nodo.der, d + 1))
        return prof

    def altura(self):
        """Número de nodos del camino más largo raíz->hoja. Árbol vacío: 0."""
        prof = self._profundidades()
        return max(prof.values()) if prof else 0

    def pasos_medios(self, ids):
        prof = self._profundidades()
        return sum(prof[i] for i in ids) / len(ids)


# --------------------------------------------------------------------------------------
# 3) Árbol B+
# --------------------------------------------------------------------------------------
def _pos_izq_py(claves, x):
    """bisect_left en Python puro."""
    lo, hi = 0, len(claves)
    while lo < hi:
        mid = (lo + hi) // 2
        if claves[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def _pos_der_py(claves, x):
    """bisect_right en Python puro."""
    lo, hi = 0, len(claves)
    while lo < hi:
        mid = (lo + hi) // 2
        if x < claves[mid]:
            hi = mid
        else:
            lo = mid + 1
    return lo


class _Hoja:
    __slots__ = ("claves", "valores", "siguiente")

    def __init__(self):
        self.claves = []
        self.valores = []
        self.siguiente = None


class _Interno:
    __slots__ = ("claves", "hijos")

    def __init__(self):
        self.claves = []
        self.hijos = []


class BPlus:
    """Árbol B+ (solo inserción y búsqueda; no se necesita borrado en este laboratorio).

    * Los registros viven únicamente en las hojas; las hojas forman una lista enlazada.
    * Los nodos internos solo guardan claves "separadoras" para dirigir la búsqueda.
    * `max_claves` = máximo de claves por nodo (hoja o interno). Si un nodo llega a
      max_claves + 1 claves, se parte en dos. Un nodo interno tiene hasta max_claves + 1 hijos.
    * Convención del separador: hijos[i] contiene claves k con claves[i-1] <= k < claves[i].
    * Altura = número de niveles (una raíz que es hoja tiene altura 1).
    * Todas las hojas están siempre al mismo nivel -> el árbol está perfectamente balanceado,
      sin importar el orden de inserción.

    Si `usar_bisect` es False, la búsqueda dentro de cada nodo se hace con una búsqueda binaria
    escrita en Python (comparación "justa" frente al ABB y la lista, que también son Python puro).
    """

    def __init__(self, max_claves=64, usar_bisect=True):
        if max_claves < 3:
            raise ValueError("max_claves debe ser >= 3")
        self.max_claves = max_claves
        self.raiz = _Hoja()
        self._altura = 1
        self.n = 0
        self._izq = bisect_left if usar_bisect else _pos_izq_py
        self._der = bisect_right if usar_bisect else _pos_der_py

    def __len__(self):
        return self.n

    def _descender(self, clave):
        nodo = self.raiz
        der = self._der
        while type(nodo) is _Interno:
            nodo = nodo.hijos[der(nodo.claves, clave)]
        return nodo

    def buscar(self, id_):
        nodo = self.raiz
        der = self._der
        while type(nodo) is _Interno:
            nodo = nodo.hijos[der(nodo.claves, id_)]
        i = self._izq(nodo.claves, id_)
        if i < len(nodo.claves) and nodo.claves[i] == id_:
            return nodo.valores[i]
        return None

    def insertar(self, registro):
        clave = registro["id"]
        izq, der = self._izq, self._der
        # 1) Descender a la hoja guardando el camino (nodo interno, índice del hijo tomado).
        camino = []
        nodo = self.raiz
        while type(nodo) is _Interno:
            i = der(nodo.claves, clave)
            camino.append((nodo, i))
            nodo = nodo.hijos[i]
        # 2) Insertar en la hoja (si no es duplicado).
        i = izq(nodo.claves, clave)
        if i < len(nodo.claves) and nodo.claves[i] == clave:
            return False
        nodo.claves.insert(i, clave)
        nodo.valores.insert(i, registro)
        self.n += 1
        if len(nodo.claves) <= self.max_claves:
            return True
        # 3) Partir la hoja: la clave del primer elemento de la hoja derecha "sube" (se copia).
        medio = len(nodo.claves) // 2
        nueva = _Hoja()
        nueva.claves = nodo.claves[medio:]
        nueva.valores = nodo.valores[medio:]
        nodo.claves = nodo.claves[:medio]
        nodo.valores = nodo.valores[:medio]
        nueva.siguiente = nodo.siguiente
        nodo.siguiente = nueva
        clave_sube = nueva.claves[0]
        hijo_nuevo = nueva
        # 4) Propagar hacia arriba mientras los padres se desborden.
        while camino:
            padre, i = camino.pop()
            padre.claves.insert(i, clave_sube)
            padre.hijos.insert(i + 1, hijo_nuevo)
            if len(padre.claves) <= self.max_claves:
                return True
            medio = len(padre.claves) // 2
            clave_sube = padre.claves[medio]  # en un nodo interno la clave del medio SUBE (se mueve)
            nuevo = _Interno()
            nuevo.claves = padre.claves[medio + 1:]
            nuevo.hijos = padre.hijos[medio + 1:]
            padre.claves = padre.claves[:medio]
            padre.hijos = padre.hijos[:medio + 1]
            hijo_nuevo = nuevo
        # 5) Se partió la raíz: el árbol crece un nivel.
        nueva_raiz = _Interno()
        nueva_raiz.claves = [clave_sube]
        nueva_raiz.hijos = [self.raiz, hijo_nuevo]
        self.raiz = nueva_raiz
        self._altura += 1
        return True

    def listar(self):
        """Recorre la lista enlazada de hojas desde la más a la izquierda. O(N)."""
        nodo = self.raiz
        while type(nodo) is _Interno:
            nodo = nodo.hijos[0]
        resultado = []
        while nodo is not None:
            resultado.extend(nodo.valores)
            nodo = nodo.siguiente
        return resultado

    def rango(self, desde, hasta):
        """Registros con desde <= id <= hasta (la ventaja clásica del B+). Extra, no se mide."""
        hoja = self._descender(desde)
        resultado = []
        while hoja is not None:
            for k, v in zip(hoja.claves, hoja.valores):
                if k > hasta:
                    return resultado
                if k >= desde:
                    resultado.append(v)
            hoja = hoja.siguiente
        return resultado

    def altura(self):
        return self._altura

    def pasos_medios(self, ids):
        # Toda búsqueda visita exactamente `altura` nodos (raíz -> hoja).
        return float(self._altura)

    def validar(self):
        """Comprueba los invariantes del B+. Lanza AssertionError si algo está mal (usado en pruebas)."""
        niveles_hojas = set()

        def rec(nodo, nivel, minimo, maximo):
            assert len(nodo.claves) <= self.max_claves, "nodo desbordado"
            assert nodo.claves == sorted(nodo.claves), "claves desordenadas"
            for k in nodo.claves:
                assert (minimo is None or k >= minimo) and (maximo is None or k < maximo), "clave fuera de rango"
            if type(nodo) is _Hoja:
                assert len(nodo.claves) == len(nodo.valores)
                niveles_hojas.add(nivel)
                return
            assert len(nodo.hijos) == len(nodo.claves) + 1, "hijos != claves + 1"
            limites = [minimo] + list(nodo.claves) + [maximo]
            for j, h in enumerate(nodo.hijos):
                rec(h, nivel + 1, limites[j], limites[j + 1])

        rec(self.raiz, 1, None, None)
        assert len(niveles_hojas) <= 1, "hojas en niveles distintos"
        assert niveles_hojas == {self._altura} or self.n == 0, "altura inconsistente"
        claves = [r["id"] for r in self.listar()]
        assert claves == sorted(claves) and len(claves) == self.n, "cadena de hojas inconsistente"
        return True
