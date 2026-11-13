"""
Cálculos del informe de resultados (app/report.py): calidad respecto al mejor valor conocido, comparación con los
trabajos anteriores y entre configuraciones, por tipo de instancia.

Las referencias son las de data/instances/best_known.csv: Schittekat et al. (2013) (GRASP+VND y óptimos del MIP),
la tesis de Pérez Pérez (2020) y el EDA de Pérez-Rodríguez y Hernández-Aguirre (2016).
"""
import math
import re
from pathlib import Path

import pandas as pd

from src.analysis import best_known

# Diferencias relativas menores que esto se consideran empates (los valores publicados tienen 2 decimales)
TIE = 5e-4
REFERENCES = {"grasp_vnd": "Schittekat et al. (2013), GRASP+VND",
              "hill_climbing_2020": "Pérez Pérez (2020), escalada",
              "eda_2016": "Pérez-Rodríguez y Hernández-Aguirre (2016), EDA",
              "mip": "Óptimos del MIP de Schittekat et al. (2013)"}
INSTANCE_PATTERN = re.compile(r"inst(\d+)-\d+s(\d+)-(\d+)-c(\d+)-w(\d+)")
GROUPS = {"w": "Distancia a pie (w)", "paradas": "Paradas", "estudiantes": "Estudiantes", "capacidad": "Capacidad"}


def load_runs(folders) -> pd.DataFrame:
    """Corridas de uno o varios lanzamientos (su summary.csv), con una etiqueta única por configuración."""
    frames = []
    for folder in folders:
        folder = Path(folder)
        runs = pd.read_csv(folder / "summary.csv")
        runs["lanzamiento"] = folder.name
        frames.append(runs)
    runs = pd.concat(frames, ignore_index=True)
    names = runs.groupby("config")["lanzamiento"].nunique()
    runs["etiqueta"] = [config if names[config] == 1 else f"{config} ({launch})"
                        for config, launch in zip(runs["config"], runs["lanzamiento"])]
    return runs


def per_instance(runs: pd.DataFrame) -> pd.DataFrame:
    """Por configuración e instancia: mejor valor y media de las semillas, tiempo, referencias y características."""
    table = runs.groupby(["etiqueta", "instance"]).agg(
        mejor=("value", "min"), media=("value", "mean"), corridas=("value", "size"),
        factibles=("feasible", lambda s: s.astype(str).eq("True").mean()),
        tiempo=("execution_time", "mean")).reset_index()
    references = pd.DataFrame.from_dict(best_known.load(), orient="index")
    for column in ["best_known", "lower_bound", *REFERENCES]:
        references[column] = pd.to_numeric(references[column], errors="coerce")
    table = table.join(references[["best_known", "optimal", "lower_bound", *REFERENCES]], on="instance")
    features = table["instance"].str.extract(INSTANCE_PATTERN).astype(float)
    features.columns = ["número", "paradas", "estudiantes", "capacidad", "w"]
    table = pd.concat([table, features.astype("Int64")], axis=1)
    table["gap_mejor"] = table["mejor"] / table["best_known"] - 1
    table["gap_media"] = table["media"] / table["best_known"] - 1
    return table.sort_values(["etiqueta", "número"]).reset_index(drop=True)


def wilcoxon(a: pd.Series, b: pd.Series) -> float:
    """
    p-valor bilateral de la prueba de rangos con signo de Wilcoxon (aproximación normal), descartando las
    diferencias nulas. Con todas las diferencias nulas devuelve 1.
    """
    differences = (pd.Series(a).reset_index(drop=True) - pd.Series(b).reset_index(drop=True)).dropna()
    differences = differences[differences.abs() > 1e-12]
    n = len(differences)
    if n == 0:
        return 1.0
    ranks = differences.abs().rank()
    positive = ranks[differences > 0].sum()
    mean, deviation = n * (n + 1) / 4, math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    return math.erfc(abs(positive - mean) / deviation / math.sqrt(2))


def outcome(values: pd.Series, reference: pd.Series) -> dict:
    """Instancias en que values es mejor, igual o peor que reference, diferencia relativa media y Wilcoxon."""
    data = pd.DataFrame({"v": values.values, "r": reference.values}).dropna()
    difference = data["v"] / data["r"] - 1
    return {"instancias": len(data), "mejor": int((difference < -TIE).sum()), "igual": int((difference.abs() <= TIE).sum()),
            "peor": int((difference > TIE).sum()), "diferencia_media": difference.mean() if len(data) else float("nan"),
            "p_wilcoxon": wilcoxon(data["v"], data["r"]) if len(data) else float("nan")}


def quality(table: pd.DataFrame) -> pd.DataFrame:
    """Resumen de calidad por configuración."""
    rows = []
    for label, data in table.groupby("etiqueta", sort=False):
        optimal = data[data["optimal"] == True]  # noqa: E712 (columna de objetos)
        rows.append({"configuración": label, "instancias": len(data), "corridas": int(data["corridas"].sum()),
                     "factibles": (data["factibles"] * data["corridas"]).sum() / data["corridas"].sum(),
                     "gap_medio_mejor": data["gap_mejor"].mean(), "gap_mediano_mejor": data["gap_mejor"].median(),
                     "gap_medio_media": data["gap_media"].mean(),
                     "igualan_mejor_conocido": int((data["gap_mejor"].abs() <= TIE).sum()),
                     "nuevos_mejores": int((data["gap_mejor"] < -TIE).sum()),
                     "óptimos_alcanzados": int((optimal["gap_mejor"] <= TIE).sum()), "óptimos_probados": len(optimal),
                     "tiempo_medio": data["tiempo"].mean()})
    return pd.DataFrame(rows)


def against_references(table: pd.DataFrame) -> pd.DataFrame:
    """Comparación de cada configuración (mejor de las semillas y media) con cada trabajo anterior."""
    rows = []
    for label, data in table.groupby("etiqueta", sort=False):
        for column, name in REFERENCES.items():
            for kind in ("mejor", "media"):
                rows.append({"configuración": label, "referencia": name, "valor": f"{kind} de las semillas",
                             **outcome(data[kind], data[column])})
    return pd.DataFrame(rows)


def new_best_known(table: pd.DataFrame) -> pd.DataFrame:
    """Instancias en que se mejora el mejor valor conocido, comprobando que no baje de la cota inferior."""
    better = table[table["gap_mejor"] < -TIE].copy()
    better["respeta_cota"] = better["lower_bound"].isna() | (better["mejor"] >= better["lower_bound"] - 0.005)
    return better[["etiqueta", "instance", "mejor", "best_known", "gap_mejor", "lower_bound", "respeta_cota"]]


def by_group(table: pd.DataFrame, key: str) -> pd.DataFrame:
    """Gap y diferencia con Schittekat y con la tesis por grupo de instancias (w, paradas, ...)."""
    rows = []
    for (label, value), data in table.groupby(["etiqueta", key], sort=False):
        rows.append({"configuración": label, GROUPS[key]: value, "instancias": len(data),
                     "gap_medio_mejor": data["gap_mejor"].mean(),
                     "vs_schittekat": (data["mejor"] / data["grasp_vnd"] - 1).mean(),
                     "vs_tesis": (data["mejor"] / data["hill_climbing_2020"] - 1).mean(),
                     "tiempo_medio": data["tiempo"].mean()})
    return pd.DataFrame(rows).sort_values(["configuración", GROUPS[key]]).reset_index(drop=True)


def worst(table: pd.DataFrame, count: int = 10) -> pd.DataFrame:
    """Las instancias con mayor gap (mejor de las semillas) de cada configuración."""
    return (table.sort_values("gap_mejor", ascending=False).groupby("etiqueta", sort=False).head(count)
            [["etiqueta", "instance", "mejor", "best_known", "gap_mejor", "optimal", "w"]])


def between_configs(table: pd.DataFrame) -> pd.DataFrame:
    """Comparación por pares de configuraciones sobre sus instancias comunes (mejor de las semillas)."""
    labels = list(dict.fromkeys(table["etiqueta"]))
    wide = table.pivot_table(index="instance", columns="etiqueta", values="mejor")
    rows = []
    for i, first in enumerate(labels):
        for second in labels[i + 1:]:
            pair = wide[[first, second]].dropna()
            rows.append({"configuración": first, "frente_a": second, **outcome(pair[first], pair[second])})
    return pd.DataFrame(rows)
