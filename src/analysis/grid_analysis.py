"""
Análisis de un lanzamiento de app/grid.py: ranking de combinaciones de operadores y efecto de cada factor.

Las comparaciones usan el gap sobre el mejor conocido de cada instancia, para que instancias de distinta escala pesen
igual. Cada bloque es una instancia y un número de corrida: como la rejilla usa la misma semilla para todas las
combinaciones en un bloque, las combinaciones se comparan dentro de cada bloque (prueba de Friedman), igual que en la
tesis de Pérez Pérez (2020) siguiendo a Derrac et al. (2011).
"""
import csv
import math
from pathlib import Path

import numpy as np
import pandas as pd

from src.analysis import best_known

BLOCK = ["instance", "run"]


def is_grid_launch(folder) -> bool:
    return (Path(folder) / "grid.csv").exists()


def load(folder) -> tuple:
    """
    (corridas, factores) de un lanzamiento de la rejilla. Las corridas incluyen los niveles de cada factor y el gap.
    Si el lanzamiento no terminó (sin summary.csv), se leen las corridas terminadas una a una.
    """
    folder = Path(folder)
    grid = pd.read_csv(folder / "grid.csv")
    factors = [column for column in grid.columns if column != "config"]
    if (folder / "summary.csv").exists():
        runs = pd.read_csv(folder / "summary.csv")
    else:
        rows = []
        for path in folder.glob("config*/*/run_*.csv"):
            with open(path, encoding="utf-8") as file:
                rows.extend(csv.DictReader(file))
        runs = pd.DataFrame(rows)
    if runs.empty:
        return runs, factors
    runs["value"] = pd.to_numeric(runs["value"], errors="coerce")
    runs["run"] = runs["run"].astype(int)
    runs["execution_time"] = pd.to_numeric(runs["execution_time"], errors="coerce")
    reference = runs["instance"].map(lambda i: (best_known.reference(i) or {}).get("best_known"))
    runs["best_known"] = pd.to_numeric(reference, errors="coerce")
    runs["gap"] = runs["value"] / runs["best_known"] - 1
    return runs.merge(grid, on="config", how="left"), factors


def complete_blocks(runs: pd.DataFrame) -> pd.DataFrame:
    """Corridas de los bloques (instancia, corrida) en los que terminaron todas las combinaciones."""
    configs = runs["config"].nunique()
    sizes = runs.dropna(subset=["gap"]).groupby(BLOCK)["config"].nunique()
    blocks = sizes[sizes == configs].index
    return runs.set_index(BLOCK).loc[blocks].reset_index() if len(blocks) else runs.iloc[0:0]


def friedman_ranks(runs: pd.DataFrame) -> pd.Series:
    """Rango medio de cada combinación (1 = la mejor) sobre los bloques completos; empates con rango medio."""
    ranks = runs.groupby(BLOCK)["gap"].rank(method="average")
    return ranks.groupby(runs["config"]).mean()


def friedman_test(mean_ranks: pd.Series, blocks: int) -> dict:
    """Estadístico de Friedman y su p-valor (aproximación chi-cuadrado), a partir de los rangos medios."""
    k, n = len(mean_ranks), blocks
    if k < 2 or n < 2:
        return {"statistic": None, "p_value": None, "blocks": n}
    statistic = 12 * n / (k * (k + 1)) * (float((mean_ranks ** 2).sum()) - k * (k + 1) ** 2 / 4)
    return {"statistic": statistic, "p_value": chi2_sf(statistic, k - 1), "blocks": n}


def holm_vs_best(mean_ranks: pd.Series, blocks: int) -> pd.Series:
    """
    p-valor ajustado por Holm de la comparación de cada combinación con la de mejor rango medio
    (z = diferencia de rangos / sqrt(k(k+1)/(6N)), Demšar 2006). La mejor tiene p = NaN.
    """
    k = len(mean_ranks)
    best = mean_ranks.idxmin()
    if k < 2 or blocks < 1:
        return pd.Series(np.nan, index=mean_ranks.index)
    se = math.sqrt(k * (k + 1) / (6 * blocks))
    z = (mean_ranks.drop(best) - mean_ranks[best]) / se
    p = z.map(lambda value: math.erfc(value / math.sqrt(2)))     # bilateral
    order = p.sort_values().index
    adjusted, running = {}, 0.0
    for position, config in enumerate(order):
        running = max(running, min(1.0, (len(order) - position) * p[config]))
        adjusted[config] = running
    return pd.Series(adjusted).reindex(mean_ranks.index)


def ranking(runs: pd.DataFrame, factors: list) -> tuple:
    """Tabla de combinaciones ordenada por rango medio de Friedman, y el resultado de la prueba de Friedman."""
    complete = complete_blocks(runs)
    blocks = complete.groupby(BLOCK).ngroups
    data = complete if blocks else runs
    mean_ranks = friedman_ranks(data) if blocks else pd.Series(dtype=float)
    table = data.groupby("config").agg(
        gap_medio=("gap", "mean"), gap_mediano=("gap", "median"), mejor_gap=("gap", "min"), peor_gap=("gap", "max"),
        corridas=("gap", "size"), tiempo_medio=("execution_time", "mean"))
    table["rango_medio"] = mean_ranks
    table["p_holm"] = holm_vs_best(mean_ranks, blocks) if blocks else np.nan
    levels = runs.drop_duplicates("config").set_index("config")[factors]
    table = table.join(levels)
    sort = ["rango_medio", "gap_medio"] if blocks else ["gap_medio"]
    table = table.sort_values(sort).reset_index()
    table.insert(0, "posición", range(1, len(table) + 1))
    return table, friedman_test(mean_ranks, blocks)


def factor_effects(runs: pd.DataFrame, factor: str, mean_ranks: pd.Series = None) -> pd.DataFrame:
    """
    Efecto principal de un factor: para cada nivel, el gap medio sobre todas las combinaciones que lo usan, el mejor
    gap medio de una combinación con ese nivel y, si se indican, el rango medio de sus combinaciones.
    """
    per_config = runs.groupby(["config", factor])["gap"].mean().reset_index()
    effects = runs.groupby(factor).agg(gap_medio=("gap", "mean"), tiempo_medio=("execution_time", "mean"))
    effects["mejor_combinación"] = per_config.groupby(factor)["gap"].min()
    if mean_ranks is not None and len(mean_ranks):
        effects["rango_medio"] = per_config.assign(rank=per_config["config"].map(mean_ranks)).groupby(factor)["rank"].mean()
    return effects.sort_values("gap_medio")


def interaction(runs: pd.DataFrame, rows: str, columns: str) -> pd.DataFrame:
    """Gap medio por cada par de niveles de dos factores."""
    return runs.pivot_table(index=rows, columns=columns, values="gap", aggfunc="mean")


def chi2_sf(x: float, df: int) -> float:
    """P(X >= x) para X ~ chi-cuadrado(df): función gamma incompleta regularizada superior Q(df/2, x/2)."""
    if x <= 0:
        return 1.0
    a, z = df / 2, x / 2
    if z < a + 1:
        # Serie de la gamma incompleta inferior
        term = total = 1 / a
        n = 0
        while abs(term) > abs(total) * 1e-15 and n < 100000:
            n += 1
            term *= z / (a + n)
            total += term
        return max(0.0, 1 - total * math.exp(-z + a * math.log(z) - math.lgamma(a)))
    # Fracción continua de la gamma incompleta superior (Lentz)
    tiny = 1e-300
    b = z + 1 - a
    c, d = 1 / tiny, 1 / b
    h = d
    for i in range(1, 100000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return min(1.0, h * math.exp(-z + a * math.log(z) - math.lgamma(a)))
