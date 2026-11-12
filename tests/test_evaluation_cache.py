from conftest import operator
from src.operators.distance.distance_euclidean import EuclideanDistance
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.stop_assigner import StopAssigner


def test_cached_values_match_direct_computation(inst54, inst54_population):
    for sol in inst54_population:
        assert inst54.objective_function(sol) == inst54._compute_fitness(sol)
        violations, degree = inst54._evaluate_constraints(sol)
        assert inst54.violations(sol) == violations
        assert inst54.constraint_violation(sol) == degree
        # Segunda llamada (desde la caché): mismos valores
        assert inst54.objective_function(sol) == inst54._compute_fitness(sol)


def test_modified_solution_is_reevaluated(inst54, inst54_population):
    sol = inst54_population[0].copy()
    route = next(r for r in sol.get_representation() if len(r.stops) >= 4)
    before = inst54.objective_function(sol)
    route.stops[1], route.stops[2] = route.stops[2], route.stops[1]
    after = inst54.objective_function(sol)
    assert after == inst54._compute_fitness(sol)
    assert after != before


def test_returned_violations_cannot_corrupt_the_cache(inst54, inst54_population):
    sol = inst54_population[0]
    inst54.violations(sol).append("modificación externa")
    assert inst54.violations(sol) == []


def test_assignment_clears_the_cache(inst54, inst54_population):
    inst54.objective_function(inst54_population[0])
    assert len(inst54._evaluation_cache) > 0
    parameters = InitialConstructionParameters(problem=inst54, distance_operator=EuclideanDistance(),
                                               stop_assign_strategy=operator("H_STUDENT_TO_CLOSEST_STOP_STRATEGY"))
    for stop in inst54.stops:
        stop.num_assigned_students = 0
    for student in inst54.students:
        student.assigned_stop = None
    StopAssigner().generate(parameters)
    assert len(inst54._evaluation_cache) == 0
