import random

import pytest

from conftest import groupings, operator, operator_names, visited_stops
from src.operators.distance.distance_euclidean import EuclideanDistance
from src.operators.mutation.mutation_parameters import MutationParameters

MUTATIONS = operator_names("MUTATION")
INTRA_ROUTE = ["SWAP_MUTATION_OPERATOR_SBRP", "REORDER_SEGMENT_MUTATION_OPERATOR_SBRP",
               "BEST_REORDER_SEGMENT_MUTATION_OPERATOR_SBRP"]
INTER_ROUTE = ["RELOCATE_MUTATION_OPERATOR_SBRP", "EXCHANGE_MUTATION_OPERATOR_SBRP"]


def mutate(problem, mutation, sol):
    return operator(mutation).mutate(MutationParameters(problem=problem, solution=sol, distance_operator=EuclideanDistance()))


@pytest.mark.parametrize("mutation", MUTATIONS)
def test_mutation_contract(mutation, inst54, inst54_population):
    random.seed(7)
    for original in inst54_population:
        sol = original.copy()
        result = mutate(inst54, mutation, sol)
        assert result is sol, "la mutación debe devolver la solución mutada"
        assert visited_stops(sol) == visited_stops(original), "la mutación perdió o duplicó paradas"
        for route in sol.get_representation():
            assert route.stops[0].id == 0 and route.stops[-1].id == 0 and len(route.stops) > 2
        assert inst54.is_feasible(sol)


@pytest.mark.parametrize("mutation", INTRA_ROUTE)
def test_intra_route_mutations_keep_groupings(mutation, inst54, inst54_population):
    random.seed(7)
    for original in inst54_population:
        sol = original.copy()
        mutate(inst54, mutation, sol)
        assert groupings(sol) == groupings(original)


@pytest.mark.parametrize("mutation", INTER_ROUTE)
def test_inter_route_mutations_change_groupings(mutation, inst54, inst54_population):
    random.seed(7)
    changed = 0
    for original in inst54_population:
        sol = original.copy()
        mutate(inst54, mutation, sol)
        changed += groupings(sol) != groupings(original)
    assert changed > 0


def test_best_reorder_never_worsens(inst54, inst54_population):
    random.seed(7)
    for original in inst54_population:
        sol = original.copy()
        mutate(inst54, "BEST_REORDER_SEGMENT_MUTATION_OPERATOR_SBRP", sol)
        assert inst54.objective_function(sol) <= inst54.objective_function(original) + 1e-9


def test_inter_route_mutations_respect_tight_capacity(tight):
    from conftest import population
    random.seed(7)
    for original in population(tight, "RANDOM_ROUTE_GENERATION_STRATEGY", 10):
        for mutation in INTER_ROUTE:
            sol = original.copy()
            mutate(tight, mutation, sol)
            assert tight.is_feasible(sol)
