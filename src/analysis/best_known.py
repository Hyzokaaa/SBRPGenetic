"""
Mejores valores conocidos de las 120 instancias de Schittekat et al. (data/instances/best_known.csv).

Fuentes:
- Schittekat, Kinable, Sörensen, Sevaux, Spieksma y Springael (2013), "A metaheuristic for the school bus routing
  problem with bus stop selection", EJOR 229(2), Tabla 5: óptimos del MIP (CPLEX, 2 h), cotas inferiores por
  generación de columnas y la solución de su GRASP+VND (instancias 1-112).
- Pérez Pérez (2020), tesis "Una solución para el problema de planificación de rutas de autobuses escolares",
  Tablas 10-12: su escalada de mejor ascenso (ECMA_SSBSR_SpNSFR) y el EDA de Pérez-Rodríguez y
  Hernández-Aguirre (2016). Las instancias 113-120 solo tienen el valor de la escalada.

best_known es el mínimo entre el óptimo del MIP, el GRASP+VND y la escalada; si la cota inferior es entera (LB "(i)")
es el valor óptimo. optimal indica si ese valor está probado: resuelto por el MIP, cota inferior entera o una solución
igual a la cota inferior. El EDA no se usa como referencia porque en 12 instancias queda por debajo de óptimos
probados, por lo que sus valores no son comparables.
"""
import csv
from functools import lru_cache
from pathlib import Path

BEST_KNOWN_FILE = Path(__file__).resolve().parents[2] / "data" / "instances" / "best_known.csv"


@lru_cache(maxsize=1)
def load() -> dict:
    """{nombre de instancia (sin extensión): {"best_known": float, "optimal": bool, "source": str, ...}}"""
    if not BEST_KNOWN_FILE.exists():
        return {}
    with open(BEST_KNOWN_FILE, encoding="utf-8") as file:
        return {row["instance"]: {**row, "best_known": float(row["best_known"]), "optimal": row["optimal"] == "True"}
                for row in csv.DictReader(file)}


def reference(instance: str):
    """Registro de la instancia (nombre o ruta del archivo), o None si no tiene valor conocido."""
    return load().get(Path(str(instance)).stem)


def gap(value, instance):
    """Diferencia relativa (fracción) de value respecto al mejor conocido; None si no hay referencia o valor."""
    record = reference(instance)
    if value is None or record is None or not record["best_known"]:
        return None
    return value / record["best_known"] - 1
