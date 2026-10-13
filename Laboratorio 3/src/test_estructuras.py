"""
Pruebas de correctitud de las tres estructuras (se ejecutan en segundos).

    python src/test_estructuras.py        (o:  pytest src/test_estructuras.py)

Se comparan contra un "oráculo" trivial: un dict de Python y la función sorted().
Si estas pruebas fallan, NO tiene sentido medir tiempos.
"""
import math
import random

from estructuras import ABB, BPlus, ListaEstudiantes


def _registros(ids):
    return [{"id": i, "nombre": f"E{i}", "edad": 18 + i % 10, "promedio": (i % 100) / 10} for i in ids]


def _fabricas():
    return {
        "Lista": ListaEstudiantes,
        "ABB": ABB,
        "B+ (64, bisect)": lambda: BPlus(64, True),
        "B+ (64, python)": lambda: BPlus(64, False),
        "B+ (3, stress)": lambda: BPlus(3, True),
        "B+ (4, stress)": lambda: BPlus(4, False),
        "B+ (5)": lambda: BPlus(5, True),
    }


def _ordenes_de_insercion(n, rng):
    ids = rng.sample(range(1, 10 * n + 1), n)
    return {"aleatorio": ids, "ascendente": sorted(ids), "descendente": sorted(ids, reverse=True)}


def test_buscar_listar_insertar():
    rng = random.Random(1)
    for n in (0, 1, 2, 3, 10, 100, 1500):
        for orden, ids in _ordenes_de_insercion(n, rng).items():
            for nombre, fab in _fabricas().items():
                est = fab()
                for r in _registros(ids):
                    assert est.insertar(r) is True
                assert len(est) == n, (nombre, orden, n)
                oraculo = {r["id"]: r for r in _registros(ids)}
                for i in ids:                                    # todo lo insertado se encuentra
                    assert est.buscar(i) == oraculo[i], (nombre, orden, n, i)
                universo = set(ids)
                ausentes = [x for x in range(0, 10 * n + 5, 7) if x not in universo]
                for x in ausentes[:300]:                         # lo no insertado NO se encuentra
                    assert est.buscar(x) is None, (nombre, orden, n, x)
                listado = est.listar()                           # listado ordenado y completo
                assert [r["id"] for r in listado] == sorted(ids), (nombre, orden, n)
                assert est.buscar(-5) is None and est.buscar(10 ** 9) is None


def test_inserciones_intercaladas_con_busquedas():
    """Inserta nuevos estudiantes DESPUÉS de haber buscado/listado (uso real del sistema)."""
    rng = random.Random(2)
    for nombre, fab in _fabricas().items():
        est, oraculo = fab(), {}
        for ronda in range(30):
            nuevos = [i for i in rng.sample(range(1, 5000), 40) if i not in oraculo]
            for r in _registros(nuevos):
                est.insertar(r)
                oraculo[r["id"]] = r
            for i in rng.sample(sorted(oraculo), min(25, len(oraculo))):
                assert est.buscar(i) == oraculo[i], nombre
            assert [r["id"] for r in est.listar()] == sorted(oraculo), nombre


def test_duplicados():
    for nombre, fab in _fabricas().items():
        if nombre == "Lista":
            continue  # la lista documenta que no verifica duplicados
        est = fab()
        for r in _registros([5, 3, 8]):
            est.insertar(r)
        assert est.insertar(_registros([3])[0]) is False, nombre
        assert len(est) == 3, nombre
        assert [r["id"] for r in est.listar()] == [3, 5, 8], nombre


def test_invariantes_bplus():
    rng = random.Random(3)
    for max_claves in (3, 4, 5, 8, 64):
        for usar_bisect in (True, False):
            for orden, ids in _ordenes_de_insercion(2000, rng).items():
                t = BPlus(max_claves, usar_bisect)
                for r in _registros(ids):
                    t.insertar(r)
                assert t.validar()
    # altura: con 2000 claves y max_claves=3 la altura debe estar acotada por log2
    t = BPlus(3)
    for r in _registros(range(1, 2001)):
        t.insertar(r)
    assert t.altura() <= math.ceil(math.log2(2000)) + 1


def test_alturas_abb():
    n = 1000
    abb = ABB()
    for r in _registros(range(1, n + 1)):          # IDs ascendentes -> árbol degenerado
        abb.insertar(r)
    assert abb.altura() == n
    abb = ABB()
    for r in _registros(range(n, 0, -1)):          # descendentes -> también degenerado
        abb.insertar(r)
    assert abb.altura() == n
    # Árbol perfectamente balanceado de 2^k - 1 nodos: altura k
    def balanceado(lo, hi, acc):
        if lo > hi:
            return
        mid = (lo + hi) // 2
        acc.append(mid)
        balanceado(lo, mid - 1, acc)
        balanceado(mid + 1, hi, acc)
    orden = []
    balanceado(1, 127, orden)
    abb = ABB()
    for r in _registros(orden):
        abb.insertar(r)
    assert abb.altura() == 7
    # ABB aleatorio: altura típica ~ 2-4 * log2(N), muy lejos de N
    rng = random.Random(4)
    ids = rng.sample(range(1, 100_001), 10_000)
    abb = ABB()
    for r in _registros(ids):
        abb.insertar(r)
    assert abb.altura() < 8 * math.log2(10_000)


def test_pasos_medios():
    ids = [10, 20, 30]
    lista = ListaEstudiantes()
    for r in _registros(ids):
        lista.insertar(r)
    assert lista.pasos_medios([10, 20, 30]) == 2.0       # (1 + 2 + 3) / 3
    abb = ABB()
    for r in _registros([20, 10, 30]):
        abb.insertar(r)
    assert abb.pasos_medios([10, 20, 30]) == (2 + 1 + 2) / 3
    bp = BPlus(64)
    for r in _registros(ids):
        bp.insertar(r)
    assert bp.pasos_medios(ids) == 1.0


def test_rango_bplus():
    t = BPlus(4)
    ids = random.Random(5).sample(range(1, 3000), 800)
    for r in _registros(ids):
        t.insertar(r)
    esperado = [i for i in sorted(ids) if 500 <= i <= 900]
    assert [r["id"] for r in t.rango(500, 900)] == esperado


if __name__ == "__main__":
    pruebas = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for p in pruebas:
        p()
        print(f"OK  {p.__name__}")
    print(f"\nTodas las pruebas pasaron ({len(pruebas)}).")
