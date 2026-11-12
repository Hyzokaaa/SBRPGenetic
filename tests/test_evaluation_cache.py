import pytest

from conftest import operator, population
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


def test_frozen_solution_reuses_its_evaluation_until_the_assignment_changes(inst54):
    sol = population(inst54, "RANDOM_ROUTE_GENERATION_STRATEGY", 1)[0]
    inst54.freeze(sol)
    assert inst54._frozen(sol) is not None
    assert inst54.solution_signature(sol) == inst54._frozen(sol)[3]
    # Una copia no está congelada y se puede modificar
    assert inst54._frozen(sol.copy()) is None
    # Si cambia la asignación, la caché se vacía y lo congelado deja de valer
    inst54.clear_evaluation_cache()
    assert inst54._frozen(sol) is None


@pytest.mark.parametrize("overrides", [
    {},
    {"replacement_operator": "DETERMINISTIC_CROWDING_REPLACEMENT_OPERATOR_SBRP",
     "selection_operator": "RANDOM_SELECTION_OPERATOR"},
    {"diversity_operator": ("CATACLYSMIC_RESTART_DIVERSITY_OPERATOR", {"stagnation": 2})},
    {"diversity_operator": ("RANDOM_IMMIGRANTS_DIVERSITY_OPERATOR", {"stagnation": 2})},
    {"diversity_operator": ("CLEARING_DIVERSITY_OPERATOR_SBRP", {"min_distance": 0.2})},
])
def test_population_individuals_never_change_after_being_frozen(overrides):
    from test_ga import run_ga

    def on_generation(generation, population, problem, stats):
        for solution in population:
            frozen = problem._frozen(solution)
            assert frozen is not None, "individuo de la población sin congelar"
            assert problem.evaluation_key(solution) == frozen[1], "individuo congelado modificado"

    params = {key: operator(value[0], **value[1]) if isinstance(value, tuple) else operator(value)
              for key, value in overrides.items()}
    run_ga(8, seed=3, on_generation=on_generation, max_iter=10, max_stagnation_iter=10, **params)
