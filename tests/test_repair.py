import random

from conftest import operator, snapshot, solution, synthetic_problem
from src.operators.repair.repair_parameters import RepairParameters
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


def repair(problem, sol, parents=None):
    return operator("REPAIR_OPERATOR_SBRP").repair(
        RepairParameters(problem=problem, solutions=[sol], parents=parents or [sol]))[0]


def test_garbage_inputs_become_feasible(inst54, inst54_population):
    random.seed(11)
    for _ in range(100):
        parent1, parent2 = random.sample(inst54_population, 2)
        stops = [s for r in parent1.get_representation() for s in r.stops if not isinstance(s, School)]
        random.shuffle(stops)
        stops += random.sample(stops, min(3, len(stops)))   # duplicadas
        stops = stops[random.randint(0, 2):]                  # faltantes
        k = random.randint(1, len(inst54.vehicles) + 3)       # rutas de más, sobrecapacidad y sin escuela
        garbage = SolutionRouteSBRP([Route(stops=stops[i::k]) for i in range(k)])
        assert inst54.is_feasible(repair(inst54, garbage, [parent1, parent2]))


def test_repair_returns_new_solutions_without_modifying_input(inst54, inst54_population):
    original = inst54_population[0]
    before = snapshot(original)
    repaired = repair(inst54, original)
    assert repaired is not original
    assert snapshot(original) == before
    assert inst54.objective_function(repaired) == inst54.objective_function(original)


def test_relocation_frees_capacity():
    # 2 buses de capacidad 5 y paradas con 4, 3, 2 y 1 estudiantes: solo {4, 1} y {3, 2} es factible
    problem = synthetic_problem([(1, 0), (2, 0), (0, 3), (0, 4)], [4, 3, 2, 1], vehicles=2, capacity=5)
    for routes in ([[2, 4], [3]], [[3, 4], [2]], [[1], [2]]):
        repaired = repair(problem, solution(problem, *routes))
        assert problem.is_feasible(repaired), routes
        loads = sorted(sorted(s.num_assigned_students for s in r.stops[1:-1]) for r in repaired.get_representation())
        assert loads == [[1, 4], [2, 3]]


def test_impossible_fleet_is_reported():
    # 3 paradas llenas y solo 2 buses: una parada queda sin visitar
    problem = synthetic_problem([(1, 0), (2, 0), (0, 3)], [5, 5, 5], vehicles=2, capacity=5)
    repaired = repair(problem, solution(problem, [1, 2], [3]))
    assert any("sin visitar" in v for v in problem.violations(repaired))
    assert len(repaired.get_representation()) == 2
