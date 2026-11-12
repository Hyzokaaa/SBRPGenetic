import csv
import os
import random
import time

from shared.presentation.visualizer import Visualizer
from src.algorithm.genetic_algorithm.genetic_algorithm_config import GeneticAlgorithmConfig
from src.algorithm.genetic_algorithm.genetic_algorithm_executor import GeneticAlgorithmExecutor
from src.problems.problem_sbrp.model.school import School

CSV_COLUMNS = ["instance", "config", "run", "seed", "value", "iteration", "execution_time", "stop_reason",
               "stop_iteration", "feasible", "violations", "student_assignments", "routes"]


def run_single(config_name: str, config_path: str, instance_path: str, run_number: int, seed: int,
               output_dir: str, save_image: bool = True) -> dict:
    """
    Ejecuta una corrida del algoritmo genético con una semilla y guarda el resultado en
    <output_dir>/<config_name>/<instancia>/run_<run_number>.csv (y la imagen de las rutas).
    Devuelve los datos principales de la corrida.
    """
    instance_name = os.path.splitext(os.path.basename(instance_path))[0]
    instance_dir = os.path.join(output_dir, config_name, instance_name)
    os.makedirs(instance_dir, exist_ok=True)

    # La semilla fija toda la aleatoriedad de la corrida (construcción inicial y operadores)
    random.seed(seed)
    config = GeneticAlgorithmConfig()
    config.load_from_file(config_path, instance_path)
    start = time.time()
    problem, fitness, best_iteration, execution_time, stop_reason, stop_iteration = GeneticAlgorithmExecutor().execute(config)
    solution = problem.best_solution

    # Generar imagen en la carpeta de la corrida (solo si se encontró una solución factible)
    if save_image and solution is not None:
        Visualizer.plot_routes(routes=solution, sbrp=problem,
                               image_path=os.path.join(instance_dir, f"run_{run_number}_result.png"))

    # Validar la solución antes de registrarla
    violations = problem.violations(solution) if solution is not None else ["No se encontró ninguna solución factible"]

    # Asignaciones entre paradas y estudiantes
    stop_assignments = {}
    for stop in problem.stops:
        if stop.num_assigned_students > 0:
            stop_assignments[f"Stop{stop.id}"] = [f"student{s.id}" for s in problem.students if s.assigned_stop == stop]

    # Descripción de rutas
    routes_description = []
    for i, route in enumerate(solution.get_representation() if solution is not None else [], 1):
        stops = [f"Stop{stop.id}" if not isinstance(stop, School) else "School" for stop in route.stops]
        total_students = sum(stop.num_assigned_students for stop in route.stops if not isinstance(stop, School))
        routes_description.append(f"Ruta{i}[{', '.join(stops)}] (Total: {total_students})")

    record = {
        "instance": instance_name, "config": config_name, "run": run_number, "seed": seed, "value": fitness,
        "iteration": best_iteration, "execution_time": round(execution_time, 2), "stop_reason": stop_reason,
        "stop_iteration": stop_iteration, "feasible": not violations, "violations": "; ".join(violations),
        "student_assignments": str(stop_assignments), "routes": "; ".join(routes_description),
    }
    with open(os.path.join(instance_dir, f"run_{run_number}.csv"), "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerow(record)

    record["wall_time"] = round(time.time() - start, 2)
    return record
