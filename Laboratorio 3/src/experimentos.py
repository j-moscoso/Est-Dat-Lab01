"""
Ejecuta los experimentos y guarda los datos CRUDOS (una fila por medición) en resultados/*.csv.

    python src/experimentos.py              # perfil completo (el del informe)
    python src/experimentos.py --rapido     # prueba de humo (~1 min), NO usar para el informe
    python src/experimentos.py --exp 1      # solo un experimento (1, 2 o 3)

Experimento 1: para cada N y cada escenario (IDs aleatorios / IDs ordenados) y cada estructura mide
               construcción (= N inserciones), M búsquedas y listado ordenado.
Experimento 2: N fijo; se varía M (número de búsquedas) para ver que el costo crece linealmente con M.
Experimento 3: sensibilidad del B+ a su parámetro "máx. claves por nodo".
"""
import argparse
import csv
import gc
import json
import random
import sys
import time
from operator import itemgetter
from time import perf_counter_ns

import config
from entorno import advertencias_de_entorno, capturar_entorno
from estructuras import ABB, BPlus, ListaEstudiantes

NOMBRES = ["Ana", "Carlos", "María", "Juan", "Laura", "Andrés", "Camila", "Santiago", "Valentina", "Daniel",
           "Sofía", "Mateo", "Isabella", "Sebastián", "Luciana", "Felipe", "Daniela", "Nicolás", "Mariana", "David"]
APELLIDOS = ["Gómez", "Rodríguez", "Martínez", "López", "García", "Pérez", "Ramírez", "Torres", "Díaz", "Vargas",
             "Castro", "Ruiz", "Ortiz", "Moreno", "Jiménez", "Hernández", "Muñoz", "Rojas", "Suárez", "Mejía"]


# ------------------------------------------------------------------ generación de datos
def generar_ids(n, semilla):
    """N IDs únicos tomados al azar de [1, 10N]. El universo 10 veces mayor deja huecos (IDs no existentes)."""
    return random.Random(f"{semilla}-ids").sample(range(1, 10 * n + 1), n)


def generar_registros(ids, semilla):
    rng = random.Random(f"{semilla}-datos")
    return [{"id": i,
             "nombre": f"{rng.choice(NOMBRES)} {rng.choice(APELLIDOS)}",
             "edad": rng.randint(17, 35),
             "promedio": round(rng.uniform(0.0, 10.0), 2)} for i in ids]


def generar_consultas(ids, m, semilla):
    """M IDs de búsqueda elegidos al azar (con reemplazo) entre los IDs existentes. Mismas consultas
    para todas las estructuras y escenarios de una repetición (diseño pareado)."""
    return random.Random(f"{semilla}-consultas").choices(ids, k=m)


def fabricas(cfg, orden=None):
    o = orden or cfg["orden_bplus"]
    return {"Lista": ListaEstudiantes, "ABB": ABB, "B+": lambda: BPlus(o, cfg["usar_bisect_bplus"])}


# ------------------------------------------------------------------ medición
def _cronometrar(funcion):
    gc.collect()
    gc.disable()
    try:
        inicio = perf_counter_ns()
        resultado = funcion()
        return resultado, (perf_counter_ns() - inicio) / 1e9
    finally:
        gc.enable()


def _medir_repetido(operacion, minimo_s):
    resultado, tiempo = _cronometrar(operacion)
    if tiempo >= minimo_s:
        return resultado, tiempo
    repeticiones = max(1, min(100_000, int(minimo_s / max(tiempo, 1e-7) * 1.05)))
    def bloque():
        ultimo = resultado
        for _ in range(repeticiones):
            ultimo = operacion()
        return ultimo
    ultimo, total = _cronometrar(bloque)
    return ultimo, total / repeticiones


def _medir_busquedas(est, consultas, minimo_s, semilla):
    def ejecutar(ids):
        return sum(est.buscar(q) is not None for q in ids)

    encontrados, tiempo = _cronometrar(lambda: ejecutar(consultas))
    if encontrados != len(consultas):
        raise AssertionError("una búsqueda de un ID existente falló")
    if tiempo >= minimo_s:
        return tiempo

    rng = random.Random(semilla)
    estimadas = max(1, min(100_000, int(minimo_s / max(tiempo, 1e-7) * 1.05)))
    max_lotes = max(1, 200_000 // len(consultas))
    total = 0.0
    lotes_medidos = 0
    while total < minimo_s:
        repeticiones = min(estimadas, max_lotes)
        lotes = [[rng.choice(consultas) for _ in consultas] for _ in range(repeticiones)]
        def bloque():
            encontrados = 0
            for nuevas in lotes:
                encontrados += ejecutar(nuevas)
            return encontrados
        encontrados, parcial = _cronometrar(bloque)
        if encontrados != len(consultas) * repeticiones:
            raise AssertionError("una búsqueda de un ID existente falló")
        total += parcial
        lotes_medidos += repeticiones
        estimadas = max(1, min(100_000, int((minimo_s - total) / max(parcial / repeticiones, 1e-7) * 1.05)))
    return total / lotes_medidos


def medir_estructura(fabrica, registros, consultas, ids_ordenados, minimo_s, semilla):
    """Mide cada operación sobre una ventana mínima, con verificaciones fuera del cronómetro."""
    def construir():
        est = fabrica()
        for registro in registros:
            est.insertar(registro)
        return est

    est, t_construccion = _medir_repetido(construir, minimo_s)
    t_busqueda = _medir_busquedas(est, consultas, minimo_s, semilla)
    listado, t_listado = _cronometrar(est.listar)
    if t_listado < minimo_s:
        repeticiones = max(1, min(100_000, int(minimo_s / max(t_listado, 1e-7) * 1.05)))
        def bloque_listados():
            ultimo = None
            for _ in range(repeticiones):
                ultimo = est.listar()
            return ultimo
        _, total = _cronometrar(bloque_listados)
        t_listado = total / repeticiones

    return dict(
        t_construccion_s=t_construccion,
        t_busqueda_s=t_busqueda,
        t_listado_s=t_listado,
        altura=est.altura(),
        pasos_medios=est.pasos_medios(consultas),
        encontrados=len(consultas),
        listado_ok=(len(est) == len(registros) and [r["id"] for r in listado] == ids_ordenados),
    ), est


def construir_sin_medir(fabrica, registros):
    est = fabrica()
    for r in registros:
        est.insertar(r)
    return est


def calentar(cfg):
    """Ejecuciones descartadas para que el intérprete y las cachés estén 'calientes'."""
    ids = generar_ids(500, "calentamiento")
    regs = generar_registros(ids, "calentamiento")
    cons = generar_consultas(ids, 200, "calentamiento")
    for _ in range(3):
        for fab in fabricas(cfg).values():
            medir_estructura(fab, regs, cons, sorted(ids), cfg["minimo_s"], "calentamiento")


def _abrir_csv(ruta, campos):
    f = open(ruta, "w", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=campos)
    w.writeheader()
    return f, w


def _escenarios(registros):
    return {"aleatorio": registros, "ordenado": sorted(registros, key=itemgetter("id"))}


# ------------------------------------------------------------------ experimentos
def experimento_1(cfg):
    campos = ["escenario", "estructura", "N", "M", "repeticion", "t_construccion_s", "t_busqueda_s",
              "t_listado_s", "altura", "pasos_medios", "encontrados", "listado_ok"]
    f, w = _abrir_csv(config.DIR_RESULTADOS / "exp1_crudo.csv", campos)
    t_ini = time.time()
    print("\n=== Experimento 1: escalamiento con N ===")
    for n in cfg["tamanos"]:
        for rep in range(cfg["repeticiones"]):
            semilla = f"{cfg['semilla']}-{n}-{rep}"
            ids = generar_ids(n, semilla)
            registros = generar_registros(ids, semilla)
            consultas = generar_consultas(ids, cfg["m"], semilla)
            ids_ord = sorted(ids)
            escenarios = list(_escenarios(registros).items())
            random.Random(f"{semilla}-escenarios").shuffle(escenarios)
            for escenario, regs in escenarios:
                estructuras = list(fabricas(cfg).items())
                random.Random(f"{semilla}-{escenario}-estructuras").shuffle(estructuras)
                for nombre, fab in estructuras:
                    if nombre == "ABB" and escenario == "ordenado" and n > cfg["max_n_abb_ordenado"]:
                        continue
                    res, _ = medir_estructura(
                        fab, regs, consultas, ids_ord, cfg["minimo_s"], f"{semilla}-{nombre}"
                    )
                    assert res["encontrados"] == cfg["m"], "una búsqueda de un ID existente falló"
                    assert res["listado_ok"], "el listado no salió ordenado/completo"
                    w.writerow(dict(escenario=escenario, estructura=nombre, N=n, M=cfg["m"], repeticion=rep, **res))
            f.flush()
        print(f"  N={n:>7,} listo ({cfg['repeticiones']} repeticiones)  [{time.time() - t_ini:7.1f} s]")
    f.close()


def experimento_2(cfg):
    campos = ["escenario", "estructura", "N", "M", "repeticion", "t_busqueda_s"]
    f, w = _abrir_csv(config.DIR_RESULTADOS / "exp2_crudo.csv", campos)
    n, m_max = cfg["n_fijo_exp2"], max(cfg["m_valores_exp2"])
    t_ini = time.time()
    print(f"\n=== Experimento 2: escalamiento con M (N = {n:,}) ===")
    for rep in range(cfg["repeticiones"]):
        semilla = f"{cfg['semilla']}-exp2-{rep}"
        ids = generar_ids(n, semilla)
        registros = generar_registros(ids, semilla)
        consultas = generar_consultas(ids, m_max, semilla)
        for escenario, regs in _escenarios(registros).items():
            for nombre, fab in fabricas(cfg).items():
                est = construir_sin_medir(fab, regs)
                for m in cfg["m_valores_exp2"]:
                    t = _medir_busquedas(
                        est, consultas[:m], cfg["minimo_s"], f"{semilla}-{nombre}-{m}"
                    )
                    w.writerow(dict(escenario=escenario, estructura=nombre, N=n, M=m, repeticion=rep, t_busqueda_s=t))
        f.flush()
        print(f"  repetición {rep + 1}/{cfg['repeticiones']} lista  [{time.time() - t_ini:7.1f} s]")
    f.close()


def experimento_3(cfg):
    campos = ["escenario", "orden", "N", "M", "repeticion", "t_construccion_s", "t_busqueda_s", "altura"]
    f, w = _abrir_csv(config.DIR_RESULTADOS / "exp3_crudo.csv", campos)
    n = cfg["n_exp3"]
    t_ini = time.time()
    print(f"\n=== Experimento 3: B+ según máx. claves por nodo (N = {n:,}) ===")
    for rep in range(cfg["repeticiones"]):
        semilla = f"{cfg['semilla']}-exp3-{rep}"
        ids = generar_ids(n, semilla)
        registros = generar_registros(ids, semilla)
        consultas = generar_consultas(ids, cfg["m"], semilla)
        ids_ord = sorted(ids)
        escenarios = list(_escenarios(registros).items())
        random.Random(f"{semilla}-escenarios").shuffle(escenarios)
        for escenario, regs in escenarios:
            ordenes = list(cfg["ordenes_exp3"])
            random.Random(f"{semilla}-{escenario}-ordenes").shuffle(ordenes)
            for orden in ordenes:
                fab = fabricas(cfg, orden)["B+"]
                res, _ = medir_estructura(
                    fab, regs, consultas, ids_ord, cfg["minimo_s"], f"{semilla}-{orden}"
                )
                assert res["encontrados"] == cfg["m"] and res["listado_ok"]
                w.writerow(dict(escenario=escenario, orden=orden, N=n, M=cfg["m"], repeticion=rep,
                                t_construccion_s=res["t_construccion_s"], t_busqueda_s=res["t_busqueda_s"],
                                altura=res["altura"]))
        f.flush()
        print(f"  repetición {rep + 1}/{cfg['repeticiones']} lista  [{time.time() - t_ini:7.1f} s]")
    f.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rapido", action="store_true", help="perfil reducido para probar que todo funciona")
    ap.add_argument("--exp", type=int, choices=[1, 2, 3], help="ejecutar solo un experimento")
    args = ap.parse_args()
    cfg = config.RAPIDO if args.rapido else config.COMPLETO

    config.DIR_RESULTADOS.mkdir(exist_ok=True)
    info = capturar_entorno()
    print("Entorno:", json.dumps(info, ensure_ascii=False, indent=2))
    for a in advertencias_de_entorno(info):
        print("  [ADVERTENCIA]", a)
    if args.rapido:
        print("  [ADVERTENCIA] PERFIL RAPIDO: sirve para probar el pipeline, no para el informe final.")
    (config.DIR_RESULTADOS / "entorno.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    (config.DIR_RESULTADOS / "config_usada.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nCalentando intérprete...")
    calentar(cfg)
    t0 = time.time()
    for k, fn in {1: experimento_1, 2: experimento_2, 3: experimento_3}.items():
        if args.exp in (None, k):
            fn(cfg)
    print(f"\nListo en {(time.time() - t0) / 60:.1f} minutos. Datos en {config.DIR_RESULTADOS}")
    print("Siguiente paso:  python src/analisis.py")


if __name__ == "__main__":
    sys.exit(main())
