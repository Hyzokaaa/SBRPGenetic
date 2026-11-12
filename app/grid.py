"""
Experimento de rejilla: ejecuta todas las combinaciones de operadores sobre un conjunto de instancias.

Cada combinación parte de una configuración base y cambia solo los operadores (asignación, generación de rutas,
selección, cruce y mutación). Todas usan el mismo presupuesto: la misma población y el mismo número de generaciones,
sin parada por estancamiento. Las corridas de una misma instancia y número de corrida usan la misma semilla en todas
las combinaciones (números aleatorios comunes), lo que reduce la variabilidad al compararlas.

El lanzamiento se guarda como cualquier otro de app/main.py (results/<fecha_hora>/), más grid.csv con los operadores
de cada configuración. Se puede reanudar con: python app/main.py --resume results/<fecha_hora>

Ejemplos (desde la raíz del proyecto):
    python app/grid.py --pattern "inst27-*" "inst54-*" --runs 2 --workers 14
    python app/grid.py --dry-run
"""
import argparse
import csv
import itertools
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import CONFIGS_DIR, create_session, execute_session, find_instances, relative_to_root, \
    resolve  # noqa: E402
from src.problems.problem_sbrp.algorithm.genetic_algorithm.operators_enum import Operators  # noqa: E402

# Factores de la rejilla: clave de la configuración y niveles (nombres del enumerado de operadores)
OPERATOR_NAMES = [operator.name for operator in Operators]
FACTORS = {
    "stop_assign_strategy": [n for n in OPERATOR_NAMES if n.endswith("_STRATEGY") and "STUDENT" in n],
    "route_generator_strategy": [n for n in OPERATOR_NAMES if "ROUTE_GENERAT" in n],
    "selection_operator": [n for n in OPERATOR_NAMES if "SELECTION" in n],
    "crossover_operator": [n for n in OPERATOR_NAMES if "CROSSOVER" in n],
    "mutation_operator": [n for n in OPERATOR_NAMES if "MUTATION" in n and "DIVERSITY" not in n],
}


def grid_configs(base: dict, factors: dict) -> tuple:
    """{config<N>: datos} con una configuración por combinación de operadores, y {config<N>: niveles}."""
    configs, levels = {}, {}
    for number, combination in enumerate(itertools.product(*factors.values()), 1):
        name = f"config{number}"
        levels[name] = dict(zip(factors, combination))
        configs[name] = {**base, **levels[name]}
    return configs, levels


def restrict(factors: dict, only: list) -> dict:
    """Limita los niveles de los factores indicados como FACTOR=NIVEL[,NIVEL...] (p. ej. crossover_operator=X,Y)."""
    factors = dict(factors)
    for item in only or []:
        key, _, values = item.partition("=")
        if key not in factors:
            sys.exit(f"Factor desconocido: {key}. Factores: {', '.join(factors)}")
        unknown = [v for v in values.split(",") if v not in factors[key]]
        if unknown:
            sys.exit(f"Niveles desconocidos para {key}: {', '.join(unknown)}")
        factors[key] = values.split(",")
    return factors


def main():
    args = parse_args()
    factors = restrict(FACTORS, args.only)
    with open(resolve(args.configs_dir) / f"config{args.base}.json", encoding="utf-8") as file:
        base = json.load(file)
    base.update({"initial_population_size": args.population, "max_iter": args.max_iter,
                 # Sin parada por estancamiento: todas las combinaciones evalúan el mismo número de soluciones
                 "max_stagnation_iter": args.max_iter + 1})
    configs, levels = grid_configs(base, factors)
    instances = find_instances(args.instances, args.pattern)

    # Números aleatorios comunes: la semilla depende de la instancia y la corrida, no de la configuración
    jobs = [{"config": name, "instance": instance.stem, "run": run,
             "seed": args.seed + index * args.runs + run - 1}
            for name in configs for index, instance in enumerate(instances) for run in range(1, args.runs + 1)]

    sizes = " × ".join(f"{len(values)} {key.split('_')[0]}" for key, values in factors.items())
    print(f"{len(configs)} combinaciones ({sizes}) × {len(instances)} instancias × {args.runs} corridas = "
          f"{len(jobs)} ejecuciones con {args.workers} procesos")
    print(f"Presupuesto: población {args.population} × {args.max_iter} generaciones, base config{args.base}")
    if args.dry_run:
        for instance in instances:
            print(f"  {relative_to_root(instance)}")
        return

    session, manifest = create_session(args, configs, instances, jobs,
                                       extra={"grid": {"base": f"config{args.base}", "factors": factors}})
    with open(session / "grid.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["config", *factors])
        writer.writeheader()
        writer.writerows({"config": name, **values} for name, values in levels.items())
    print(f"Resultados en {relative_to_root(session)} (reanudable con app/main.py --resume)")
    execute_session(session, manifest, jobs, args)


def parse_args():
    parser = argparse.ArgumentParser(description="Rejilla de combinaciones de operadores del algoritmo genético.")
    parser.add_argument("--base", type=int, default=8, help="Configuración base (config<N>.json)")
    parser.add_argument("--configs-dir", default=str(CONFIGS_DIR), help="Carpeta de las configuraciones")
    parser.add_argument("--population", type=int, default=100, help="Tamaño de población de todas las combinaciones")
    parser.add_argument("--max-iter", type=int, default=50, help="Generaciones de todas las combinaciones")
    parser.add_argument("--instances", default="data/instances/real", help="Carpeta de instancias")
    parser.add_argument("--pattern", nargs="+", action="extend", help="Patrones de nombres de instancia")
    parser.add_argument("--runs", type=int, default=2, help="Corridas por combinación e instancia")
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1), help="Procesos en paralelo")
    parser.add_argument("--seed", type=int, default=1, help="Semilla base")
    parser.add_argument("--output", default="results", help="Carpeta donde se crea la carpeta del lanzamiento")
    parser.add_argument("--log-level", default="WARNING", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--images", dest="no_images", action="store_false",
                        help="Guardar la imagen de cada corrida (por defecto no, por el número de corridas)")
    parser.add_argument("--only", nargs="+", metavar="FACTOR=NIVELES",
                        help="Limitar niveles de un factor, p. ej. crossover_operator=BCRC_CROSSOVER_OPERATOR_SBRP")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar el plan sin ejecutar")
    return parser.parse_args()


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    main()
