"""
Ejecución de una corrida del algoritmo genético en un proceso independiente (usado para comparar configuraciones).
"""
import random
import time

import common
from src.algorithm.genetic_algorithm.genetic_algorithm_executor import GeneticAlgorithmExecutor


def run_once(config_name: str, config_path: str, instance_path: str, seed: int, overrides: dict) -> dict:
    """
    Ejecuta el GA con una configuración y una semilla. Devuelve el resultado y la mejor distancia
    encontrada hasta cada generación.
    """
    random.seed(seed)
    config = common.build_config(config_path, instance_path, overrides)
    history = []

    def on_generation(generation, population, problem, stats):
        best = problem.best_solution
        history.append(problem.objective_function(best) if best is not None else None)

    start = time.time()
    problem, fitness, best_iteration, _, stop_reason, stop_iteration = GeneticAlgorithmExecutor().execute(
        config, on_generation=on_generation)
    solution = problem.best_solution
    return {
        "config": config_name, "seed": seed, "fitness": fitness, "best_iteration": best_iteration,
        "time": time.time() - start, "stop_reason": stop_reason, "generations": stop_iteration,
        "feasible": solution is not None and problem.is_feasible(solution),
        "routes": len(solution.get_representation()) if solution is not None else None,
        "history": history,
    }
