import random

import pytest

from conftest import operator, solution, synthetic_problem
from src.operators.replacement.replacement_parameters import ReplacementParameters
from test_ga import run_ga


def crowding_setup():
    problem = synthetic_problem([(1, 0), (2, 0), (0, 3), (0, 4)], [2, 2, 2, 2], vehicles=4, capacity=10)
    a = solution(problem, [1, 2], [3, 4])          # rutas cortas
    b = solution(problem, [1, 3], [2, 4])          # rutas cruzadas: más largas
    return problem, a, b


def test_crowding_pairs_each_child_with_the_most_similar_parent():
    problem, a, b = crowding_setup()
    crowding = operator("DETERMINISTIC_CROWDING_REPLACEMENT_OPERATOR_SBRP")
    # Los hijos llegan en orden cruzado: el primero es copia de b y el segundo de a
    pairs = crowding.pairs([a, b], [b.copy(), a.copy()])
    assert [crowding.distance(parent, child) for parent, child in pairs] == [0, 0]


def test_crowding_keeps_size_and_never_replaces_with_a_worse_child():
    problem, a, b = crowding_setup()
    worse = solution(problem, [1, 4], [3, 2])
    assert problem.objective_function(worse) > max(problem.objective_function(a), problem.objective_function(b))
    crowding = operator("DETERMINISTIC_CROWDING_REPLACEMENT_OPERATOR_SBRP")
    crowding.start([a, b], ReplacementParameters(problem=problem, objective_max=False, population_size=2))
    assert not crowding.is_full()
    crowding.add_child(worse)
    crowding.add_child(a.copy())
    crowding.end_family([a, b])
    assert crowding.is_full()
    result = crowding.result()
    # Mismo tamaño, ningún lugar empeora y el hijo peor no entra
    assert len(result) == 2 and worse not in result
    assert all(problem.objective_function(new) <= problem.objective_function(old) for new, old in zip(result, [a, b]))


def test_generational_replacement_keeps_the_elite_first():
    problem, a, b = crowding_setup()
    generational = operator("GENERATIONAL_REPLACEMENT_OPERATOR")
    generational.start([b, a], ReplacementParameters(problem=problem, objective_max=False, population_size=3,
                                                     elitism_size=1))
    elite = generational.result()[0]
    assert elite is not a and problem.solution_signature(elite) == problem.solution_signature(a)
    assert generational.contains(problem.solution_signature(a)) and not generational.contains(None)
    generational.add_child(b.copy())
    generational.add_child(b.copy())
    assert generational.is_full() and len(generational.result()) == 3


@pytest.mark.parametrize("seed", [1, 2])
def test_ga_with_crowding_keeps_size_and_the_best_solution(seed):
    def on_generation(generation, population, problem, stats):
        assert len(population) == 30
        feasible = [problem.objective_function(s) for s in population if problem.is_feasible(s)]
        assert min(feasible) == pytest.approx(problem.objective_function(problem.best_solution))

    problem, fitness, *_ = run_ga(8, seed=seed, on_generation=on_generation, max_iter=8,
                                  replacement_operator=operator("DETERMINISTIC_CROWDING_REPLACEMENT_OPERATOR_SBRP"),
                                  selection_operator=operator("RANDOM_SELECTION_OPERATOR"))
    assert problem.is_feasible(problem.best_solution)


def test_crowding_preserves_more_diversity_than_generational_replacement():
    from src.analysis.metrics import solution_edges

    def diversity_tracker(values):
        def on_generation(generation, population, problem, stats):
            edges = [solution_edges(s) for s in population]
            pairs = [(i, j) for i in range(len(edges)) for j in range(i + 1, len(edges))]
            values.append(sum(1 - len(edges[i] & edges[j]) / len(edges[i] | edges[j]) for i, j in pairs) / len(pairs))
        return on_generation

    generational, crowding = [], []
    run_ga(8, seed=1, on_generation=diversity_tracker(generational), max_iter=15, max_stagnation_iter=15)
    run_ga(8, seed=1, on_generation=diversity_tracker(crowding), max_iter=15, max_stagnation_iter=15,
           replacement_operator=operator("DETERMINISTIC_CROWDING_REPLACEMENT_OPERATOR_SBRP"),
           selection_operator=operator("RANDOM_SELECTION_OPERATOR"))
    assert crowding[-1] > generational[-1]
