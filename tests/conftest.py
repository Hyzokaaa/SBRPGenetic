"""
Utilidades y datos compartidos por las pruebas.
"""
import collections
import importlib
import logging
import random
from pathlib import Path

import pytest

from src.operators.distance.distance_euclidean import EuclideanDistance
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.operators.repair.repair_parameters import RepairParameters
from src.problems.problem_parameters import ProblemParameters
from src.problems.problem_sbrp.algorithm.genetic_algorithm.operators_enum import Operators
from src.problems.problem_sbrp.data_io.file_data_input_sbrp import FileDataInputSBRP
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.operators.initial_solution.initial_solution_conform_operator_sbrp import \
    InitialSolutionOperatorSBRP
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP

logging.disable(logging.CRITICAL)

ROOT = Path(__file__).resolve().parents[1]
INSTANCES = ROOT / "data" / "instances"
CONFIGS = ROOT / "src" / "problems" / "problem_sbrp" / "algorithm" / "genetic_algorithm"


def operator(name: str, **params):
    """Instancia un operador del enumerado por su nombre."""
    module_name, class_name = Operators[name].value.rsplit('.', 1)
    return getattr(importlib.import_module(module_name), class_name)(**params)


def operator_names(fragment: str):
    return [op.name for op in Operators if fragment in op.name]


def load_problem(relative_path: str, strategy: str = "H_STUDENT_TO_CLOSEST_STOP_STRATEGY") -> ProblemSBRP:
    """Problema de una instancia de data/instances con los estudiantes ya asignados a paradas."""
    problem = ProblemSBRP()
    problem.construct(FileDataInputSBRP(str(INSTANCES / relative_path)).conform())
    operator(strategy).generate_stop_assign(problem, EuclideanDistance())
    return problem


def synthetic_problem(stop_coordinates, loads, vehicles, capacity, school=(0, 0)) -> ProblemSBRP:
    """Problema pequeño con las cargas de cada parada fijadas directamente (sin estudiantes)."""
    problem = ProblemSBRP()
    problem.construct(ProblemParameters(EuclideanDistance(), school, list(stop_coordinates), [], vehicles, capacity, 5))
    for stop, load in zip(problem.stops, loads):
        stop.num_assigned_students = load
    problem.clear_evaluation_cache()
    return problem


def solution(problem: ProblemSBRP, *routes) -> SolutionRouteSBRP:
    """Solución a partir de listas de identificadores de paradas (la escuela se añade en los extremos)."""
    stops = {stop.id: stop for stop in problem.stops}
    return SolutionRouteSBRP([Route([problem.school] + [stops[i] for i in ids] + [problem.school]) for ids in routes])


def population(problem: ProblemSBRP, generator: str, size: int, seed: int = 1):
    """Población inicial factible (se reparan las soluciones infactibles, como en el GA)."""
    random.seed(seed)
    parameters = InitialConstructionParameters(problem=problem, distance_operator=EuclideanDistance(),
                                               route_generator_strategy=operator(generator))
    repair = operator("REPAIR_OPERATOR_SBRP")
    result = []
    for _ in range(size):
        candidate = InitialSolutionOperatorSBRP().generate(parameters)
        if problem.violations(candidate):
            candidate = repair.repair(RepairParameters(problem=problem, solutions=[candidate], parents=[candidate]))[0]
        result.append(candidate)
    return result


def snapshot(sol):
    """Secuencia de identificadores de paradas de cada ruta (para detectar modificaciones)."""
    return [tuple(stop.id for stop in route.stops) for route in sol.get_representation()]


def visited_stops(sol):
    """Multiconjunto de paradas visitadas (sin la escuela)."""
    return collections.Counter(stop.id for route in sol.get_representation()
                               for stop in route.stops if not isinstance(stop, School))


def groupings(sol):
    """Agrupación de paradas en rutas, sin importar el orden."""
    return sorted(sorted(stop.id for stop in route.stops if not isinstance(stop, School))
                  for route in sol.get_representation())


@pytest.fixture(scope="module")
def inst54():
    return load_problem("real/inst54-7s20-100-c50-w20.xpress")


@pytest.fixture(scope="module")
def inst54_population(inst54):
    return population(inst54, "RANDOM_ROUTE_GENERATION_STRATEGY", 20)


@pytest.fixture(scope="module")
def tight():
    """Instancia ajustada: 2 buses de capacidad 5 y cargas 4, 3, 2 y 1."""
    return load_problem("MH/mi_instancia.xpress")
