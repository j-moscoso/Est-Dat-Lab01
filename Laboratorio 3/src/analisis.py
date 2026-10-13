"""
Lee los datos crudos de resultados/, calcula las estadísticas, genera las gráficas (carpeta graficas/)
y un informe con tablas y cifras calculadas (resultados/informe_generado.md).

    python src/analisis.py

Todo lo que aparece en gráficas y tablas sale de resultados/*.csv; nada está escrito a mano.
"""
import datetime
import json
import math
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config

ESCENARIOS, ESTRUCTURAS = config.ESCENARIOS, config.ESTRUCTURAS
COL = {"Lista": "#E4572E", "ABB": "#2E86AB", "B+": "#2CA58D"}
ESTILO = {"aleatorio": dict(ls="-", marker="o"), "ordenado": dict(ls="--", marker="s")}
NOM_ESC = {"aleatorio": "IDs aleatorios", "ordenado": "IDs ordenados (ascendentes)"}
NOM_MET = {"t_busqueda_s": "búsqueda", "t_construccion_s": "construcción (N inserciones)", "t_listado_s": "listado ordenado"}
# t de Student, 95 % bilateral, por grados de libertad
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
       11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093,
       20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048,
       29: 2.045, 30: 2.042}


_SEP_MILES = "."


def miles(n):
    return f"{int(n):,}".replace(",", _SEP_MILES)


# ====================================================================== estadística
def estadisticos(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    n = len(x)
    media = float(x.mean())
    std = float(x.std(ddof=1)) if n > 1 else 0.0
    q1, q3 = np.percentile(x, [25, 75])
    iqr = q3 - q1
    atip = (x < q1 - 1.5 * iqr) | (x > q3 + 1.5 * iqr)          # criterio de Tukey (1.5 * IQR)
    sin = x[~atip] if (~atip).any() else x
    ic = T95.get(n - 1, 1.96) * std / math.sqrt(n) if n > 1 else 0.0
    return dict(n=n, media=media, std=std, ic95=ic, mediana=float(np.median(x)), minimo=float(x.min()),
                maximo=float(x.max()), cv=std / media if media else float("nan"), n_atipicos=int(atip.sum()),
                media_sin_atipicos=float(sin.mean()))


def resumir(df, grupo, metricas):
    filas = []
    for clave, g in df.groupby(grupo, sort=True):
        for m in metricas:
            if g[m].isna().all():
                continue
            filas.append({**dict(zip(grupo, clave)), "metrica": m, **estadisticos(g[m])})
    return pd.DataFrame(filas)


def serie(res, esc, est, metrica):
    d = res[(res["escenario"] == esc) & (res["estructura"] == est) & (res["metrica"] == metrica)]
    return d.sort_values("N", kind="stable")


def pendiente(Ns, ts, nmin=0):
    Ns, ts = np.asarray(Ns, float), np.asarray(ts, float)
    k = (Ns >= nmin) & (ts > 0)
    if k.sum() < 3:
        return float("nan"), float("nan")
    x, y = np.log(Ns[k]), np.log(ts[k])
    p = np.polyfit(x, y, 1)
    r2 = float(np.corrcoef(x, y)[0, 1] ** 2)
    return float(p[0]), r2


MODELOS = {"O(1)": lambda n: np.ones_like(n), "O(log N)": lambda n: np.log2(n), "O(N)": lambda n: n,
           "O(N log N)": lambda n: n * np.log2(n), "O(N²)": lambda n: n ** 2}


def mejor_modelo(Ns, ts):
    """Modelo t = c·f(N) con menor error cuadrático medio en escala logarítmica (c libre)."""
    Ns, ts = np.asarray(Ns, float), np.asarray(ts, float)
    if len(Ns) < 3 or (ts <= 0).any():
        return "—", {}
    lt = np.log(ts)
    err = {}
    for nombre, f in MODELOS.items():
        r = lt - np.log(f(Ns))
        err[nombre] = float(np.sqrt(np.mean((r - r.mean()) ** 2)))
    return min(err, key=err.get), err


def teoria(est, esc, metrica):
    if metrica == "t_busqueda_s":
        return {"Lista": "O(N)", "ABB": "O(log N) promedio" if esc == "aleatorio" else "O(N) (árbol degenerado)",
                "B+": "O(log N)"}[est]
    if metrica == "t_construccion_s":
        return {"Lista": "O(N)", "ABB": "O(N log N)" if esc == "aleatorio" else "O(N²)", "B+": "O(N log N)"}[est]
    return {"Lista": "O(N log N)" if esc == "aleatorio" else "O(N) (Timsort)", "ABB": "O(N)", "B+": "O(N)"}[est]


# ====================================================================== gráficas
def _etiquetas(cfg):
    return {"Lista": "Lista – búsqueda lineal",
            "ABB": "ABB (sin balanceo)",
            "B+": f"Árbol B+ (máx. {cfg['orden_bplus']} claves/nodo)"}


def _nota_cap(cfg, res):
    """Aclaración que se agrega al pie cuando el ABB con IDs ordenados no llega al mayor N."""
    if res is not None and res["N"].max() > cfg["max_n_abb_ordenado"]:
        return f" El ABB con IDs ordenados solo se mide hasta N = {miles(cfg['max_n_abb_ordenado'])} (construirlo es O(N²))."
    return ""


def _pie(fig, texto):
    import textwrap
    ancho = max(40, int(fig.get_figwidth() * 12))          # caracteres por línea según el ancho de la figura
    fig.text(0.5, -0.02, textwrap.fill(texto, ancho), ha="center", va="top", fontsize=8.5, color="#444444")


def _guardar(fig, nombre):
    config.DIR_GRAFICAS.mkdir(exist_ok=True)
    fig.savefig(config.DIR_GRAFICAS / nombre, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _congelar_limites(ax):
    ax.relim()
    ax.autoscale_view()
    ax.set_autoscale_on(False)


def _ref(ax, Ns, y0, N0, k, texto):
    Ns = np.asarray(Ns, float)
    ax.plot(Ns, y0 * (Ns / N0) ** k, color="#888888", lw=1.1, ls=":" if k == 1 else "-.", label=texto)


def fig_dos_paneles(res, cfg, metrica, titulo, ylabel, archivo, refs):
    ET = _etiquetas(cfg)
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.2), sharey=True)
    for ax, esc in zip(axs, ESCENARIOS):
        for est in ESTRUCTURAS:
            d = serie(res, esc, est, metrica)
            if d.empty:
                continue
            ax.errorbar(d["N"], d["media"], yerr=d["std"], marker="o", ms=5, capsize=3, lw=1.6,
                        color=COL[est], label=ET[est])
        ax.set_xscale("log")
        ax.set_yscale("log")
        _congelar_limites(ax)
        for est_ref, k, texto in refs.get(esc, []):
            d = serie(res, esc, est_ref, metrica)
            if not d.empty:
                _ref(ax, d["N"], d["media"].iloc[0], d["N"].iloc[0], k, texto)
        ax.set_title(NOM_ESC[esc])
        ax.set_xlabel("Tamaño de entrada N (número de estudiantes)")
        ax.grid(True, which="both", alpha=.25)
        ax.legend(fontsize=8.5, loc="upper left")
    axs[0].set_ylabel(ylabel)
    fig.suptitle(titulo, fontsize=13, fontweight="bold")
    _pie(fig, f"Cada punto = media de {cfg['repeticiones']} repeticiones; barras = ±1 desviación estándar. "
              "Ejes logarítmicos. Línea punteada = pendiente teórica de referencia (anclada al primer punto de la serie indicada)." + _nota_cap(cfg, res))
    _guardar(fig, archivo)


def fig_escenarios_por_estructura(res, cfg, metrica, archivo, titulo):
    ET = _etiquetas(cfg)
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
    for ax, est in zip(axs, ESTRUCTURAS):
        for esc in ESCENARIOS:
            d = serie(res, esc, est, metrica)
            if d.empty:
                continue
            ax.errorbar(d["N"], d["media"], yerr=d["std"], capsize=3, lw=1.6, color=COL[est], ms=5,
                        alpha=1 if esc == "aleatorio" else .75, label=NOM_ESC[esc], **ESTILO[esc])
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(ET[est])
        ax.set_xlabel("Tamaño de entrada N (número de estudiantes)")
        ax.grid(True, which="both", alpha=.25)
        ax.legend(fontsize=9, loc="upper left")
    axs[0].set_ylabel("Tiempo (s)")
    fig.suptitle(titulo, fontsize=13, fontweight="bold")
    _pie(fig, f"Media de {cfg['repeticiones']} repeticiones ± 1 desviación estándar. Línea continua = IDs aleatorios; "
              "línea discontinua = IDs insertados en orden ascendente." + _nota_cap(cfg, res))
    _guardar(fig, archivo)


def fig_altura(res, cfg, archivo):
    ET = _etiquetas(cfg)
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    Ns = None
    for est, esc, etiqueta in [("ABB", "aleatorio", "ABB – IDs aleatorios"), ("ABB", "ordenado", "ABB – IDs ordenados"),
                               ("B+", "aleatorio", ET["B+"] + " – aleatorios"),
                               ("B+", "ordenado", ET["B+"] + " – ordenados")]:
        d = serie(res, esc, est, "altura")
        if d.empty:
            continue
        Ns = d["N"] if Ns is None or len(d) > len(Ns) else Ns
        ax.errorbar(d["N"], d["media"], yerr=d["std"], capsize=3, color=COL[est], label=etiqueta,
                    **{**ESTILO[esc], "ls": ESTILO[esc]["ls"]})
    if Ns is not None:
        n = np.linspace(Ns.min(), Ns.max(), 200)
        ax.plot(n, np.log2(n + 1), color="#555", ls=":", lw=1.3, label="log₂(N+1): altura mínima posible de un árbol binario")
        ax.plot(n, n, color="#999", ls="-.", lw=1.0, label="N (árbol degenerado = lista enlazada)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Tamaño de entrada N (número de estudiantes)")
    ax.set_ylabel("Altura del árbol (número de niveles)")
    ax.set_title("Altura de ABB y B+ según N y orden de inserción", fontweight="bold")
    ax.grid(True, which="both", alpha=.25)
    ax.legend(fontsize=8.5)
    _pie(fig, f"Media de {cfg['repeticiones']} repeticiones ± 1 desviación estándar (altura = nodos del camino más largo raíz→hoja).")
    _guardar(fig, archivo)


def fig_pasos_vs_tiempo(e1, cfg, archivo):
    ET = _etiquetas(cfg)
    df = e1.copy()
    df["us_busq"] = df["t_busqueda_s"] / df["M"] * 1e6
    fig, ax = plt.subplots(figsize=(9, 6))
    for est in ESTRUCTURAS:
        for esc in ESCENARIOS:
            d = df[(df["estructura"] == est) & (df["escenario"] == esc)]
            if d.empty:
                continue
            ax.scatter(d["pasos_medios"], d["us_busq"], s=26, alpha=.65, color=COL[est], marker=ESTILO[esc]["marker"],
                       label=f"{ET[est]} – {NOM_ESC[esc]}")
    stats, lineas = {}, []
    for est in ("ABB", "Lista"):
        d = df[df["estructura"] == est]
        if len(d) > 2:
            lx, ly = np.log(d["pasos_medios"]), np.log(d["us_busq"])
            a, b = np.polyfit(lx, ly, 1)
            r = float(np.corrcoef(lx, ly)[0, 1])
            us_paso = float((d["us_busq"] / d["pasos_medios"]).median())
            stats[est] = dict(exponente=float(a), r_log=r, us_por_paso_mediana=us_paso)
            lineas.append(f"{est}: tiempo ∝ pasos^{a:.2f}  (r log-log = {r:.3f});  mediana {us_paso:.4f} µs/paso")
            xs = np.geomspace(d["pasos_medios"].min(), d["pasos_medios"].max(), 50)
            ax.plot(xs, np.exp(b) * xs ** a, color=COL[est], lw=1, alpha=.8)
    ax.text(0.02, 0.98, "\n".join(lineas), transform=ax.transAxes, va="top", fontsize=9,
            bbox=dict(boxstyle="round", fc="white", ec="#bbbbbb"))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Pasos medios por búsqueda (nodos visitados / elementos comparados)")
    ax.set_ylabel("Tiempo medio por búsqueda (µs)")
    ax.set_title("Relación entre profundidad de búsqueda (altura efectiva) y tiempo", fontweight="bold")
    ax.grid(True, which="both", alpha=.25)
    ax.legend(fontsize=8, loc="lower right")
    _pie(fig, "Cada punto = una repetición de un (N, escenario, estructura). Línea = ajuste de ley de potencias (regresión lineal en escala log-log). Exponente ≈ 1 → el tiempo es proporcional a los pasos.")
    _guardar(fig, archivo)
    return stats


def _f_teorica(est, esc, N):
    N = np.asarray(N, float)
    if est == "Lista" or (est == "ABB" and esc == "ordenado"):
        return N
    return np.log2(N)


def fig_normalizada(res, cfg, archivo):
    ET = _etiquetas(cfg)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for est in ESTRUCTURAS:
        for esc in ESCENARIOS:
            d = serie(res, esc, est, "t_busqueda_s")
            if d.empty:
                continue
            y = d["media"].values / _f_teorica(est, esc, d["N"].values)
            ax.plot(d["N"], y / y[0], color=COL[est], label=f"{ET[est]} – {NOM_ESC[esc]}  [÷ {'N' if _f_teorica(est, esc, [2.0])[0] == 2 else 'log₂N'}]",
                    **ESTILO[esc])
    ax.axhline(1, color="#888", lw=1, ls=":")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Tamaño de entrada N (número de estudiantes)")
    ax.set_ylabel("Tiempo de búsqueda ÷ complejidad teórica (relativo al menor N)")
    ax.set_title("¿Se comportan los datos como predice la teoría? (curva plana = sí)", fontweight="bold")
    ax.grid(True, which="both", alpha=.25)
    ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.01, 1.0))
    _pie(fig, "Se divide el tiempo medio de búsqueda entre N (Lista, ABB ordenado) o log₂N (ABB aleatorio, B+) y se normaliza al primer punto. "
              "Una curva horizontal en 1 indica que el crecimiento coincide con la teoría; una curva que sube indica crecimiento más rápido.")
    _guardar(fig, archivo)


def fig_exp2(r2, cfg, archivo):
    ET = _etiquetas(cfg)
    n = int(r2["N"].iloc[0])
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.2), sharey=True)
    for ax, esc in zip(axs, ESCENARIOS):
        for est in ESTRUCTURAS:
            d = serie(r2.rename(columns={}), esc, est, "t_busqueda_s")
            if d.empty:
                continue
            ax.errorbar(d["M"], d["media"], yerr=d["std"], marker="o", ms=5, capsize=3, lw=1.6, color=COL[est], label=ET[est])
        ax.set_xscale("log")
        ax.set_yscale("log")
        _congelar_limites(ax)
        d = serie(r2, esc, "Lista", "t_busqueda_s")
        if not d.empty:
            _ref(ax, d["M"], d["media"].iloc[0], d["M"].iloc[0], 1, "pendiente 1 (lineal en M)")
        ax.set_title(NOM_ESC[esc])
        ax.set_xlabel("Número de búsquedas M")
        ax.grid(True, which="both", alpha=.25)
        ax.legend(fontsize=8.5, loc="upper left")
    axs[0].set_ylabel("Tiempo total de las M búsquedas (s)")
    fig.suptitle(f"Escalamiento con el número de búsquedas M (N = {miles(n)} fijo)", fontsize=13, fontweight="bold")
    _pie(fig, f"Media de {cfg['repeticiones']} repeticiones ± 1 desviación estándar. Si el tiempo crece proporcional a M, la curva es paralela a la línea punteada.")
    _guardar(fig, archivo)


def fig_exp3(r3, cfg, archivo):
    n = int(r3["N"].iloc[0])
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.8))
    paneles = [("t_busqueda_s", f"Tiempo de {int(cfg['m'])} búsquedas (s)", "Búsqueda"),
               ("t_construccion_s", f"Tiempo de construir ({miles(n)} inserciones) (s)", "Construcción"),
               ("altura", "Altura del B+ (niveles)", "Altura")]
    for ax, (met, yl, tit) in zip(axs, paneles):
        for esc in ESCENARIOS:
            d = r3[(r3["escenario"] == esc) & (r3["metrica"] == met)].sort_values("orden")
            ax.errorbar(d["orden"], d["media"], yerr=d["std"], capsize=3, color=COL["B+"], label=NOM_ESC[esc], **ESTILO[esc])
        ax.set_xscale("log", base=2)
        ax.set_xlabel("Máx. claves por nodo del B+ (parámetro de orden)")
        ax.set_ylabel(yl)
        ax.set_title(tit)
        ax.grid(True, which="both", alpha=.25)
        ax.legend(fontsize=9)
    fig.suptitle(f"Sensibilidad del árbol B+ a su orden (N = {miles(n)})", fontsize=13, fontweight="bold")
    _pie(fig, f"Media de {cfg['repeticiones']} repeticiones ± 1 desviación estándar.")
    _guardar(fig, archivo)


def _cociente(res, esc, num, den, metrica, esc_den=None):
    a = serie(res, esc, num, metrica).set_index("N")["media"]
    b = serie(res, esc_den or esc, den, metrica).set_index("N")["media"]
    return (a / b).dropna()


def fig_aceleracion(res, cfg, archivo):
    ET = _etiquetas(cfg)
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.2), sharey=True)
    for ax, esc in zip(axs, ESCENARIOS):
        for est in ("ABB", "B+"):
            c = _cociente(res, esc, "Lista", est, "t_busqueda_s")
            if len(c):
                ax.plot(c.index, c.values, color=COL[est], marker="o", lw=1.6, label=f"Lista ÷ {ET[est]}")
        ax.axhline(1, color="#888", ls=":", lw=1.2, label="igual de rápidas (1×)")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(NOM_ESC[esc])
        ax.set_xlabel("Tamaño de entrada N (número de estudiantes)")
        ax.grid(True, which="both", alpha=.25)
        ax.legend(fontsize=9, loc="upper left")
    axs[0].set_ylabel("Lista ÷ estructura (veces más lenta)")
    fig.suptitle("¿A partir de qué N se notan las diferencias? (Lista ÷ estructura, búsqueda)", fontsize=13, fontweight="bold")
    _pie(fig, "Cociente entre el tiempo medio de la lista y el de la estructura indicada. Por encima de 1 la estructura es más rápida que la lista; por debajo, más lenta." + _nota_cap(cfg, res))
    _guardar(fig, archivo)


def fig_penalizacion_orden(res, cfg, archivo):
    ET = _etiquetas(cfg)
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.8))
    for ax, met in zip(axs, ["t_construccion_s", "t_busqueda_s", "t_listado_s"]):
        for est in ESTRUCTURAS:
            c = _cociente(res, "ordenado", est, est, met, esc_den="aleatorio")
            if len(c):
                ax.plot(c.index, c.values, color=COL[est], marker="o", lw=1.6, label=ET[est])
        ax.axhline(1, color="#888", ls=":", lw=1.2)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(f"Operación: {NOM_MET[met]}")
        ax.set_xlabel("Tamaño de entrada N (número de estudiantes)")
        ax.grid(True, which="both", alpha=.25)
        ax.legend(fontsize=8.5, loc="upper left")
    axs[0].set_ylabel("Tiempo con IDs ordenados ÷ tiempo con IDs aleatorios")
    fig.suptitle("Efecto del orden de inserción (>1: insertar en orden perjudica)", fontsize=13, fontweight="bold")
    _pie(fig, "Cociente de tiempos medios (ordenados ÷ aleatorios) para la misma estructura y el mismo conjunto de IDs." + _nota_cap(cfg, res))
    _guardar(fig, archivo)


# ====================================================================== informe en Markdown
def md_tabla(encabezados, filas):
    out = ["| " + " | ".join(encabezados) + " |", "|" + "|".join(["---"] * len(encabezados)) + "|"]
    out += ["| " + " | ".join(str(c) for c in f) + " |" for f in filas]
    return "\n".join(out)


def fmt_t(m, s):
    return f"{m:.4g} ± {s:.2g}"


def tabla_por_N(res, metrica, fmt=fmt_t, factor=1.0, estructuras=None):
    cols = [(est, esc) for esc in ESCENARIOS for est in (estructuras or ESTRUCTURAS)]
    enc = ["N"] + [f"{est} · {'aleat.' if esc == 'aleatorio' else 'ord.'}" for est, esc in cols]
    Ns = sorted(res["N"].unique())
    filas = []
    for n in Ns:
        fila = [miles(n)]
        for est, esc in cols:
            d = serie(res, esc, est, metrica)
            d = d[d["N"] == n]
            fila.append("no medido" if d.empty else fmt(d["media"].iloc[0] * factor, d["std"].iloc[0] * factor))
        filas.append(fila)
    return md_tabla(enc, filas)


def primer_N_visible(res, lenta, rapida, esc, metrica, umbral):
    a = serie(res, esc, lenta, metrica).set_index("N")
    b = serie(res, esc, rapida, metrica).set_index("N")
    for n in sorted(a.index.intersection(b.index)):
        if a.loc[n, "media"] >= umbral * b.loc[n, "media"] and (a.loc[n, "media"] - a.loc[n, "ic95"]) > (b.loc[n, "media"] + b.loc[n, "ic95"]):
            return n
    return None


def generar_informe(cfg, e1_raw, r1, r2, r3, stats_pasos, entorno):
    global _SEP_MILES
    _SEP_MILES = "\x00"            # marca temporal: los puntos de miles se restauran al final
    try:
        texto = _generar_informe(cfg, e1_raw, r1, r2, r3, stats_pasos, entorno)
    finally:
        _SEP_MILES = "."
    texto = re.sub(r"(?<=\d)\.(?=\d)", ",", texto)        # decimales con coma (convención en español)
    return texto.replace("\x00", ".").replace("\x01", ".")


def _generar_informe(cfg, e1_raw, r1, r2, r3, stats_pasos, entorno):
    L = []
    w = L.append
    ET = _etiquetas(cfg)
    w("# Informe de resultados (generado automáticamente)\n")
    w(f"Generado el {datetime.datetime.now():%Y-%m-%d %H:%M} a partir de `resultados/*.csv`. "
      "Todas las cifras de este archivo se calculan de tus datos; **verifícalas y escribe tu propia interpretación**.\n")
    if cfg["perfil"] != "completo":
        w("> ⚠️ **Estos datos son del perfil RÁPIDO (solo prueba). No los uses en el informe final.**\n")

    w("## 1. Diseño experimental\n")
    w(md_tabla(["Parámetro", "Valor"], [
        ["Estructuras", "Lista (búsqueda lineal), ABB sin balanceo, árbol B+"],
        ["Escenarios", "IDs insertados en orden aleatorio / en orden ascendente (mismo conjunto de IDs)"],
        ["Tamaños N", ", ".join(miles(n) for n in cfg["tamanos"])],
        ["M (búsquedas, exp. 1)", miles(cfg["m"])],
        ["Repeticiones por configuración", cfg["repeticiones"]],
        ["Orden del B+ (máx. claves/nodo)", f"{cfg['orden_bplus']} (búsqueda en nodo con {'bisect (C)' if cfg['usar_bisect_bplus'] else 'Python puro'})"],
        ["Límite de N para ABB con IDs ordenados", miles(cfg["max_n_abb_ordenado"]) + " (la construcción es O(N²))"],
        ["Experimento 2", f"N = {miles(cfg['n_fijo_exp2'])}, M ∈ {{{', '.join(miles(m) for m in cfg['m_valores_exp2'])}}}"],
        ["Experimento 3", f"B+ con N = {miles(cfg['n_exp3'])}, máx. claves ∈ {{{', '.join(map(str, cfg['ordenes_exp3']))}}}"],
        ["Semilla base", cfg["semilla"]],
    ]))
    w("\n## 2. Entorno\n")
    w(md_tabla(["Elemento", "Valor"], [[k, str(v).replace(".", "\x01")] for k, v in entorno.items()]))

    w("\n## 3. Resultados (media ± desviación estándar de las repeticiones)\n")
    w("### 3.1 Búsqueda: tiempo total de M búsquedas (s)\n")
    w(tabla_por_N(r1, "t_busqueda_s"))
    w("\n**Tiempo medio por búsqueda (µs)**\n")
    w(tabla_por_N(r1, "t_busqueda_s", fmt=lambda m, s: f"{m:.4g}", factor=1e6 / cfg["m"]))
    w("\n### 3.2 Construcción: tiempo de insertar los N estudiantes (s)\n")
    w(tabla_por_N(r1, "t_construccion_s"))
    w("\n**Tiempo medio por inserción (µs)**\n")
    w(tabla_por_N(_dividir_por_N(r1), "t_construccion_s", fmt=lambda m, s: f"{m:.4g}", factor=1e6))
    w("\n### 3.3 Listado ordenado por ID (s)\n")
    w(tabla_por_N(r1, "t_listado_s"))
    w("\n### 3.4 Altura de los árboles (niveles; media ± desv.)\n")
    w(tabla_por_N(r1[r1["metrica"] == "altura"], "altura", fmt=lambda m, s: f"{m:.1f} ± {s:.1f}", estructuras=["ABB", "B+"]))

    w(f"\n### 3.5 Caso de referencia del enunciado original: N = {miles(10000)} y M = 100 búsquedas\n")
    if r2 is not None:
        n2, filas = int(r2["N"].iloc[0]), []
        for esc in ESCENARIOS:
            for est in ESTRUCTURAS:
                d = serie(r2, esc, est, "t_busqueda_s")
                d = d[d["M"] == 100]
                if not d.empty:
                    filas.append([est, esc, miles(n2), fmt_t(d["media"].iloc[0], d["std"].iloc[0])])
        w(md_tabla(["Estructura", "IDs", "N", "Tiempo de 100 búsquedas (s)"], filas))
        w("\n### 3.6 Escalamiento con M (exp. 2) — pendiente log-log del tiempo vs M (teoría: 1)\n")
        filas = []
        for esc in ESCENARIOS:
            for est in ESTRUCTURAS:
                d = serie(r2, esc, est, "t_busqueda_s")
                p, r2v = pendiente(d["M"], d["media"])
                filas.append([est, esc, f"{p:.2f}", f"{r2v:.4f}"])
        w(md_tabla(["Estructura", "IDs", "Pendiente", "R²"], filas))
        w("\nUna pendiente menor que 1 en las estructuras muy rápidas (ABB aleatorio, B+) indica que parte del tiempo es un costo fijo que no "
          "depende de M (preparar el bucle, llamadas al cronómetro), que pesa más cuando M es pequeño y el tiempo total es de microsegundos.\n")
    if r3 is not None:
        w("\n### 3.7 Sensibilidad del B+ al orden (exp. 3)\n")
        filas = []
        for esc in ESCENARIOS:
            for o in sorted(r3["orden"].unique()):
                g = r3[(r3["escenario"] == esc) & (r3["orden"] == o)].set_index("metrica")
                filas.append([esc, o, f"{g.loc['altura', 'media']:.1f}", fmt_t(g.loc['t_busqueda_s', 'media'], g.loc['t_busqueda_s', 'std']),
                              fmt_t(g.loc['t_construccion_s', 'media'], g.loc['t_construccion_s', 'std'])])
        w(md_tabla(["IDs", "Máx. claves/nodo", "Altura", "Búsqueda (s)", "Construcción (s)"], filas))

    w("\n### 3.8 Valores atípicos (criterio de Tukey: fuera de [Q1 − 1,5·IQR, Q3 + 1,5·IQR])\n")
    at = r1[r1["metrica"].isin(["t_busqueda_s", "t_construccion_s", "t_listado_s"])]
    filas = []
    for (est, esc, met), g in at.groupby(["estructura", "escenario", "metrica"]):
        filas.append([est, esc, NOM_MET[met], int(g["n_atipicos"].sum()), int(g["n"].sum()),
                      f"{(g['cv'].mean() * 100):.1f} %"])
    w(md_tabla(["Estructura", "IDs", "Operación", "Atípicos", "Mediciones", "CV medio"], filas))
    w("\nLos valores atípicos **no se eliminan**: se reportan y se compara la media con la mediana "
      "(columnas `mediana` y `media_sin_atipicos` en `resultados/resumen_exp1.csv`).\n")

    w("## 4. Contraste con la complejidad teórica\n")
    w("Pendiente de la recta ajustada a log(tiempo) vs log(N): ~1 → crecimiento lineal; ~2 → cuadrático; cerca de 0 → casi constante "
      "o logarítmico. «Mejor modelo» = el que menor error logarítmico tiene entre O(1), O(log N), O(N), O(N log N), O(N²) con constante libre "
      "(es evidencia descriptiva, no una prueba).\n")
    filas = []
    for met in ["t_busqueda_s", "t_construccion_s", "t_listado_s"]:
        for est in ESTRUCTURAS:
            for esc in ESCENARIOS:
                d = serie(r1, esc, est, met)
                if len(d) < 3:
                    continue
                p, r2v = pendiente(d["N"], d["media"])
                p2, _ = pendiente(d["N"], d["media"], nmin=5000)
                mm, _ = mejor_modelo(d["N"], d["media"])
                filas.append([NOM_MET[met], est, esc, teoria(est, esc, met), f"{p:.2f}", f"{p2:.2f}", f"{r2v:.3f}", mm])
    w(md_tabla(["Operación", "Estructura", "IDs", "Teoría", "Pendiente (todo N)", f"Pendiente (N ≥ {miles(5000)})", "R²", "Mejor modelo"], filas))

    w("\n## 5. Preguntas del enunciado, con tus datos\n")
    w("### 5.1 ¿Los resultados se comportan como predice la complejidad teórica?\n")
    w("Ver la tabla de la sección 4 y la gráfica `07_tiempo_normalizado_busqueda.png` (una curva plana indica coincidencia con la teoría).\n")

    w("### 5.2 ¿En qué situaciones el ABB deja de comportarse como O(log N)? / ¿Qué pasa con datos ordenados?\n")
    filas = []
    for n in sorted(r1["N"].unique()):
        fila = [miles(n), f"{math.log2(n + 1):.1f}"]
        for esc in ESCENARIOS:
            d = serie(r1, esc, "ABB", "altura")
            d = d[d["N"] == n]
            fila.append("—" if d.empty else f"{d['media'].iloc[0]:.1f}")
        a = serie(r1, "aleatorio", "ABB", "altura")
        a = a[a["N"] == n]
        fila.append("—" if a.empty else f"{a['media'].iloc[0] / math.log2(n + 1):.2f}×")
        filas.append(fila)
    w(md_tabla(["N", "log₂(N+1) (altura mínima posible)", "Altura ABB aleatorio", "Altura ABB ordenado", "Altura aleat. ÷ mínima"], filas))
    w("\nCon IDs ordenados cada inserción agrega el nodo como hijo derecho del último: la altura es exactamente N y el ABB equivale a una lista enlazada.\n")

    w("### 5.3 ¿Qué relación existe entre la altura del árbol y el tiempo de búsqueda?\n")
    if stats_pasos:
        for est, s in stats_pasos.items():
            w(f"- **{est}**: ajuste log-log tiempo por búsqueda vs. pasos medios → exponente = {s['exponente']:.2f} "
              f"(1 = proporcional), r = {s['r_log']:.3f}; costo mediano ≈ {s['us_por_paso_mediana']:.4f} µs por paso.")
    w("\nGráfica: `06_altura_vs_tiempo.png`.\n")

    w("### 5.4 y 5.5 Diferencias entre casos aleatorios y ordenados (tiempo ordenado ÷ tiempo aleatorio)\n")
    filas = []
    for n in sorted(r1["N"].unique()):
        fila = [miles(n)]
        for met in ["t_construccion_s", "t_busqueda_s", "t_listado_s"]:
            for est in ESTRUCTURAS:
                c = _cociente(r1, "ordenado", est, est, met, esc_den="aleatorio")
                fila.append(f"{c[n]:.2f}×" if n in c.index else "—")
        filas.append(fila)
    enc = ["N"] + [f"{NOM_MET[m].split(' ')[0]} · {e}" for m in ["t_construccion_s", "t_busqueda_s", "t_listado_s"] for e in ESTRUCTURAS]
    w(md_tabla(enc, filas))

    nmax = max(n for n in r1["N"].unique() if n in serie(r1, "ordenado", "Lista", "t_busqueda_s")["N"].values)
    pa = serie(r1, "aleatorio", "Lista", "pasos_medios").set_index("N")["media"]
    po = serie(r1, "ordenado", "Lista", "pasos_medios").set_index("N")["media"]
    ta = serie(r1, "aleatorio", "Lista", "t_busqueda_s").set_index("N")["media"]
    to = serie(r1, "ordenado", "Lista", "t_busqueda_s").set_index("N")["media"]
    w(f"\n**Ojo con la Lista:** con N = {miles(nmax)} hace prácticamente los mismos pasos en ambos escenarios "
      f"(pasos ordenado ÷ aleatorio = {po[nmax] / pa[nmax]:.2f}×) pero su tiempo de búsqueda cambia {to[nmax] / ta[nmax]:.2f}×. "
      "La diferencia no viene del algoritmo sino de la **localidad de memoria**: los registros se crean en orden aleatorio, así que recorrer la lista "
      "ordenada por ID salta por direcciones de memoria dispersas (más fallos de caché) mientras que la lista en orden aleatorio recorre registros "
      "creados consecutivamente. Es un ejemplo de cómo el hardware modifica las constantes sin cambiar la complejidad.\n")

    w("\n### 5.6 ¿A partir de qué tamaño de entrada son claramente visibles las diferencias en la búsqueda?\n")
    w("Primer N de la rejilla donde la lista es ≥ k veces más lenta y los intervalos de confianza al 95 % de ambas medias no se solapan:\n")
    filas = []
    for rapida in ("ABB", "B+"):
        for k in (2, 10, 100):
            n = primer_N_visible(r1, "Lista", rapida, "aleatorio", "t_busqueda_s", k)
            filas.append([f"Lista vs {rapida} (IDs aleatorios)", f"≥ {k}×", miles(n) if n else "no se alcanza en la rejilla"])
    n = primer_N_visible(r1, "ABB", "B+", "aleatorio", "t_busqueda_s", 1.5)
    filas.append(["ABB vs B+ (IDs aleatorios)", "≥ 1,5×", miles(n) if n else "no se alcanza en la rejilla"])
    w(md_tabla(["Comparación", "Diferencia", "Primer N"], filas))

    w("\n### 5.7 ¿Hay costos constantes que igualen algoritmos de distinta complejidad con N pequeño?\n")
    filas = []
    for n in sorted(r1["N"].unique())[:4]:
        fila = [miles(n)]
        for est, esc in [("Lista", "aleatorio"), ("ABB", "aleatorio"), ("B+", "aleatorio"), ("ABB", "ordenado")]:
            d = serie(r1, esc, est, "t_busqueda_s")
            d = d[d["N"] == n]
            fila.append("—" if d.empty else f"{d['media'].iloc[0] / cfg['m'] * 1e6:.3g}")
        filas.append(fila)
    w(md_tabla(["N", "Lista (µs/búsq.)", "ABB aleat. (µs/búsq.)", "B+ (µs/búsq.)", "ABB ordenado (µs/búsq.)"], filas))
    ns = sorted(r1["N"].unique())
    def _t(est, esc, n):
        d = serie(r1, esc, est, "t_busqueda_s")
        return d[d["N"] == n]["media"].iloc[0]
    n0, n1 = ns[0], ns[min(3, len(ns) - 1)]
    w(f"\nCon N = {miles(n0)} la lista es {_t('Lista', 'aleatorio', n0) / _t('ABB', 'aleatorio', n0):.1f}× más lenta que el ABB aleatorio y "
      f"{_t('Lista', 'aleatorio', n0) / _t('B+', 'aleatorio', n0):.1f}× más lenta que el B+; con N = {miles(n1)} la brecha ya es de "
      f"{_t('Lista', 'aleatorio', n1) / _t('ABB', 'aleatorio', n1):.1f}× y {_t('Lista', 'aleatorio', n1) / _t('B+', 'aleatorio', n1):.1f}×. "
      "Con N pequeño dominan el costo de llamar a la función, el bucle de consultas y las constantes de cada implementación, "
      "no el número de comparaciones; por eso las diferencias se achican (y a veces se invierten, p. ej. ABB con IDs ordenados vs Lista).\n")

    w("## 6. Gráficas generadas (carpeta `graficas/`)\n")
    w(md_tabla(["Archivo", "Qué muestra"], [
        ["01_busqueda_vs_N.png", "Tiempo de M búsquedas vs N, 3 estructuras, IDs aleatorios y ordenados"],
        ["02_busqueda_aleatorio_vs_ordenado.png", "Lo mismo, pero separado por estructura para ver el efecto del orden"],
        ["03_construccion_vs_N.png", "Tiempo de construir (N inserciones) vs N"],
        ["04_listado_vs_N.png", "Tiempo del listado ordenado vs N"],
        ["05_altura_vs_N.png", "Altura de ABB y B+ vs N y vs log₂(N+1)"],
        ["06_altura_vs_tiempo.png", "Tiempo por búsqueda vs pasos medios (relación altura–tiempo)"],
        ["07_tiempo_normalizado_busqueda.png", "Tiempo ÷ complejidad teórica (¿plano = coincide con la teoría?)"],
        ["08_aceleracion_vs_lista.png", "Cuántas veces la lista es más lenta que ABB/B+ según N"],
        ["09_penalizacion_orden.png", "Cociente tiempo ordenado ÷ aleatorio por operación"],
        ["10_busqueda_vs_M.png", "Experimento 2: tiempo vs número de búsquedas M"],
        ["11_bplus_vs_orden.png", "Experimento 3: B+ según máx. claves por nodo"],
    ]))
    w("\n## 7. Limitaciones que debes poder explicar\n")
    for t in [
        "Las mediciones corresponden a **Python (CPython) en tu equipo**; los valores absolutos no son extrapolables a C/Java ni a otro hardware. Lo que sí es comparable son las **tendencias y proporciones**.",
        "El B+ usa `bisect` (C) dentro de cada nodo si `usar_bisect_bplus=True`, mientras que ABB y Lista son Python puro: parte de la ventaja del B+ en tiempo absoluto puede deberse a eso y no solo al algoritmo.",
        "Todo ocurre en memoria RAM; un B+ real se diseña para minimizar accesos a disco, ventaja que aquí no se mide.",
        f"El ABB con IDs ordenados solo se mide hasta N = {miles(cfg['max_n_abb_ordenado'])} porque construirlo es O(N²).",
        "Las búsquedas son todas **exitosas** (IDs existentes); no se mide el caso de IDs inexistentes.",
        "La Lista no verifica duplicados al insertar (hacerlo costaría O(N) por inserción).",
        "El número de repeticiones es finito: las barras de error describen la variabilidad observada, no garantizan el valor «verdadero».",
    ]:
        w(f"- {t}")
    return "\n".join(L) + "\n"


def _dividir_por_N(res):
    out = res[res["metrica"] == "t_construccion_s"].copy()
    for c in ("media", "std", "mediana", "minimo", "maximo", "media_sin_atipicos", "ic95"):
        out[c] = out[c] / out["N"]
    return out


# ====================================================================== principal
def main():
    d = config.DIR_RESULTADOS
    if not (d / "exp1_crudo.csv").exists():
        sys.exit("No encuentro resultados/exp1_crudo.csv. Primero ejecuta:  python src/experimentos.py")
    cfg = json.loads((d / "config_usada.json").read_text(encoding="utf-8"))
    entorno = json.loads((d / "entorno.json").read_text(encoding="utf-8")) if (d / "entorno.json").exists() else {}
    config.DIR_GRAFICAS.mkdir(exist_ok=True)

    e1 = pd.read_csv(d / "exp1_crudo.csv")
    assert e1["listado_ok"].all() and (e1["encontrados"] == e1["M"]).all(), "hay mediciones con resultados incorrectos"
    r1 = resumir(e1, ["escenario", "estructura", "N"], ["t_busqueda_s", "t_construccion_s", "t_listado_s", "altura", "pasos_medios"])
    r1.to_csv(d / "resumen_exp1.csv", index=False)

    r2 = r3 = None
    if (d / "exp2_crudo.csv").exists():
        e2 = pd.read_csv(d / "exp2_crudo.csv")
        r2 = resumir(e2, ["escenario", "estructura", "N", "M"], ["t_busqueda_s"])
        r2.to_csv(d / "resumen_exp2.csv", index=False)
    if (d / "exp3_crudo.csv").exists():
        e3 = pd.read_csv(d / "exp3_crudo.csv")
        r3 = resumir(e3, ["escenario", "orden", "N"], ["t_busqueda_s", "t_construccion_s", "altura"])
        r3.to_csv(d / "resumen_exp3.csv", index=False)

    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11})
    m = cfg["m"]
    ref_busq = {"aleatorio": [("Lista", 1, "pendiente 1 (O(N))")], "ordenado": [("Lista", 1, "pendiente 1 (O(N))")]}
    fig_dos_paneles(r1, cfg, "t_busqueda_s", f"Tiempo de {miles(m)} búsquedas aleatorias según el tamaño N", "Tiempo total de las M búsquedas (s)",
                    "01_busqueda_vs_N.png", ref_busq)
    fig_escenarios_por_estructura(r1, cfg, "t_busqueda_s", "02_busqueda_aleatorio_vs_ordenado.png",
                                  f"Búsqueda ({miles(m)} consultas): IDs aleatorios vs IDs ordenados")
    ref_cons = {"aleatorio": [("Lista", 1, "pendiente 1 (O(N))")],
                "ordenado": [("Lista", 1, "pendiente 1 (O(N))"), ("ABB", 2, "pendiente 2 (O(N²))")]}
    fig_dos_paneles(r1, cfg, "t_construccion_s", "Tiempo de construir la estructura (insertar N estudiantes)",
                    "Tiempo total de las N inserciones (s)", "03_construccion_vs_N.png", ref_cons)
    fig_dos_paneles(r1, cfg, "t_listado_s", "Tiempo de listar todos los estudiantes ordenados por ID", "Tiempo del listado (s)",
                    "04_listado_vs_N.png", {"aleatorio": [("ABB", 1, "pendiente 1 (O(N))")], "ordenado": [("ABB", 1, "pendiente 1 (O(N))")]})
    fig_altura(r1, cfg, "05_altura_vs_N.png")
    stats_pasos = fig_pasos_vs_tiempo(e1, cfg, "06_altura_vs_tiempo.png")
    fig_normalizada(r1, cfg, "07_tiempo_normalizado_busqueda.png")
    fig_aceleracion(r1, cfg, "08_aceleracion_vs_lista.png")
    fig_penalizacion_orden(r1, cfg, "09_penalizacion_orden.png")
    if r2 is not None:
        fig_exp2(r2, cfg, "10_busqueda_vs_M.png")
    if r3 is not None:
        fig_exp3(r3, cfg, "11_bplus_vs_orden.png")

    (d / "informe_generado.md").write_text(generar_informe(cfg, e1, r1, r2, r3, stats_pasos, entorno), encoding="utf-8")
    print("Listo.")
    print(f"  Gráficas : {config.DIR_GRAFICAS}")
    print(f"  Tablas   : {d}/resumen_exp*.csv")
    print(f"  Informe  : {d / 'informe_generado.md'}")


if __name__ == "__main__":
    main()
