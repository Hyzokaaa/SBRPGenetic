from conftest import solution, synthetic_problem
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


def problem_abc(vehicles=2):
    # Paradas 1, 2 y 3 con 2, 3 y 4 estudiantes; buses de capacidad 5
    return synthetic_problem([(1, 0), (2, 0), (0, 3)], [2, 3, 4], vehicles=vehicles, capacity=5)


def test_feasible_solution_has_no_violations():
    problem = problem_abc()
    feasible = solution(problem, [1, 2], [3])
    assert problem.violations(feasible) == []
    assert problem.constraint_violation(feasible) == 0
    assert problem.is_feasible(feasible)


def test_missing_stop_counts_unpicked_students():
    problem = problem_abc()
    missing = solution(problem, [1, 2])
    assert any("sin visitar: [3]" in v for v in problem.violations(missing))
    assert problem.constraint_violation(missing) == 4


def test_duplicate_and_capacity_violations():
    problem = problem_abc()
    duplicated = solution(problem, [1, 2], [3, 1])
    violations = problem.violations(duplicated)
    assert any("más de una vez: [1]" in v for v in violations)
    assert any("excede la capacidad: 6 > 5" in v for v in violations)
    assert problem.constraint_violation(duplicated) == 2


def test_fleet_size_is_enforced():
    problem = problem_abc(vehicles=2)
    too_many = solution(problem, [1], [2], [3])
    assert any("exceden la flota: 3 > 2" in v for v in problem.violations(too_many))
    assert problem.constraint_violation(too_many) == 1


def test_routes_must_start_and_end_at_school():
    problem = problem_abc()
    stops = {stop.id: stop for stop in problem.stops}
    without_school = SolutionRouteSBRP([Route([stops[1], stops[2]]), Route([problem.school, stops[3], problem.school])])
    assert any("no sale y regresa a la escuela" in v for v in problem.violations(without_school))


def test_null_stops_are_reported():
    problem = problem_abc()
    stops = {stop.id: stop for stop in problem.stops}
    with_null = SolutionRouteSBRP([Route([problem.school, stops[1], None, stops[2], problem.school]),
                                   Route([problem.school, stops[3], problem.school])])
    assert any("paradas nulas" in v for v in problem.violations(with_null))


def test_signature_ignores_route_order_and_direction():
    problem = problem_abc()
    a = solution(problem, [1, 2], [3])
    b = solution(problem, [3], [2, 1])
    c = solution(problem, [1, 3], [2])
    assert problem.solution_signature(a) == problem.solution_signature(b)
    assert problem.solution_signature(a) != problem.solution_signature(c)
