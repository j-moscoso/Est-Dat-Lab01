"""
Parámetros del estudio experimental (un solo lugar para cambiarlos).

Dos perfiles:
  * COMPLETO: el que se usa para el informe final.
  * RAPIDO  : solo para comprobar que todo funciona (dura ~1 minuto). NO usar para el informe.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_RESULTADOS = RAIZ / "resultados"
DIR_GRAFICAS = RAIZ / "graficas"

COMPLETO = dict(
    perfil="completo",
    # Tamaños de entrada N (número de estudiantes). Aprox. equiespaciados en escala log,
    # desde un N muy pequeño (donde dominan costos constantes) hasta 100.000.
    tamanos=[100, 500, 1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000],
    # Número de búsquedas aleatorias M en el experimento 1.
    m=1_000,
    # Número de repeticiones independientes por configuración (datos y consultas nuevos en cada una).
    repeticiones=10,
    minimo_s=1.0,
    # ABB con IDs ordenados es O(N^2) al construirse (20.000 -> ~10 s por repetición; 100.000 -> ~4 min).
    # Se limita N para que el experimento termine en tiempo razonable.
    max_n_abb_ordenado=20_000,
    # Experimento 2: N fijo, se varía M.
    n_fijo_exp2=10_000,
    m_valores_exp2=[10, 100, 1_000, 10_000],
    # Experimento 3: sensibilidad del B+ al "orden" (máx. de claves por nodo), N fijo.
    n_exp3=100_000,
    ordenes_exp3=[4, 8, 16, 32, 64, 128, 256, 512],
    # Parámetros del B+ usados en los experimentos 1 y 2.
    orden_bplus=64,
    usar_bisect_bplus=True,   # True: búsqueda dentro del nodo con bisect (C). False: búsqueda binaria en Python puro.
    # Semilla base: hace reproducible la generación de datos y consultas.
    semilla=2026,
)

RAPIDO = dict(
    COMPLETO,
    perfil="rapido",
    tamanos=[100, 500, 1_000, 2_000, 5_000],
    m=200,
    repeticiones=3,
    minimo_s=0.05,
    max_n_abb_ordenado=5_000,
    n_fijo_exp2=2_000,
    m_valores_exp2=[10, 100, 1_000],
    n_exp3=5_000,
    ordenes_exp3=[4, 16, 64, 256],
)

ESCENARIOS = ["aleatorio", "ordenado"]
ESTRUCTURAS = ["Lista", "ABB", "B+"]
