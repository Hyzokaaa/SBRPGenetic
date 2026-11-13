import collections
import random

import pytest

from conftest import CONFIGS, INSTANCES, operator, solution, synthetic_problem
from src.algorithm.genetic_algorithm.genetic_algorithm_config import GeneticAlgorithmConfig
from src.algorithm.genetic_algorithm.genetic_algorithm_executor import GeneticAlgorithmExecutor
from src.operators.distance.distance_euclidean import EuclideanDistance
from src.problems.problem_parameters import ProblemParameters
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP

REMOVAL = "STOP_REMOVAL_ASSIGNMENT_IMPROVEMENT_OPERATOR_SBRP"


def problem_with(stops, students, assignment, routes, capacity, w):
    """Problema sintético con la asignación (índice de parada por estudiante) y las rutas indicadas."""
    problem = ProblemSBRP()
    problem.construct(ProblemParameters(EuclideanDistance(), (0, 0), stops, students, len(stops), capacity, w))
    for student, stop_index in zip(problem.students, assignment):
        stop = problem.stops[stop_index]
        student.assigned_stop = stop
        stop.num_assigned_students += 1
    problem.best_solution = solution(problem, *routes)
    return problem


def consistent(problem):
    counts = collections.Counter(student.assigned_stop.id for student in problem.students)
    return all(stop.num_assigned_students == counts.get(stop.id, 0) for stop in problem.stops)


def test_closes_a_stop_whose_students_can_walk_to_another_visited_stop():
    # A (0, 10) y B (2, 10) en la misma ruta; los estudiantes de B alcanzan A con sitio
    problem = problem_with([(0, 10), (2, 10)], [(0, 9), (2, 9), (1.5, 10)], [0, 1, 1], [[1, 2]], 5, 3)
    before = problem.objective_function(problem.best_solution)
    assert operator(REMOVAL).improve(problem, EuclideanDistance()) == 1
    assert problem.objective_function(problem.best_solution) < before
    assert problem.violations(problem.best_solution) == [] and consistent(problem)


def test_keeps_a_stop_when_a_student_cannot_reach_another():
    # El estudiante de B (12, 0) está demasiado lejos de A (0, 10): B no se puede cerrar ni A tampoco (capacidad)
    problem = problem_with([(0, 10), (12, 0)], [(0, 9), (12, 1)], [0, 1], [[1], [2]], 1, 3)
    assert operator(REMOVAL).improve(problem, EuclideanDistance()) == 0
    assert problem.violations(problem.best_solution) == []


def test_uses_a_reassignment_chain_when_no_direct_move_fits():
    # Paradas A (0, 10), B (4, 10) y C (8, 10), capacidad 2, cada una en su ruta. El estudiante de C solo alcanza B,
    # que está llena: para cerrar C, un estudiante de B que también alcanza A pasa a A y deja sitio en B.
    problem = problem_with([(0, 10), (4, 10), (8, 10)], [(0, 9), (2, 10), (4, 9), (6, 10)], [0, 1, 1, 2],
                           [[1], [2], [3]], 2, 2.5)
    assert operator(REMOVAL).improve(problem, EuclideanDistance()) == 1
    assert [student.assigned_stop.id for student in problem.students] == [1, 1, 2, 2]
    assert problem.violations(problem.best_solution) == [] and consistent(problem)
    assert sorted(len(route.stops) - 2 for route in problem.best_solution.get_representation()) == [1, 1]


@pytest.mark.parametrize("instance", ["inst21-7s5-100-c25-w20", "inst54-7s20-100-c50-w20", "inst102-5s80-400-c50-w20"])
def test_ga_with_stop_removal_is_feasible_and_never_worse(instance):
    results = {}
    for improver in (None, REMOVAL):
        random.seed(2)
        config = GeneticAlgorithmConfig()
        config.load_from_file(str(CONFIGS / "config14.json"), str(INSTANCES / "real" / f"{instance}.xpress"))
        config.initial_population_size, config.max_iter, config.max_stagnation_iter = 30, 5, 6
        config.assignment_improvement_operator = operator(improver) if improver else None
        problem, fitness, *_ = GeneticAlgorithmExecutor().execute(config)
        assert problem.violations(problem.best_solution) == [] and consistent(problem)
        assert fitness == pytest.approx(problem.objective_function(problem.best_solution))
        results[improver] = fitness
    assert results[REMOVAL] <= results[None] + 1e-9
