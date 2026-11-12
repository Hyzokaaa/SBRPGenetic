import pytest

from conftest import operator
from src.operators.diversity.diversity_parameters import DiversityParameters
from test_ga import run_ga


class Immigrant:
    """Marca las soluciones creadas por construct() para poder contarlas."""


def setup(inst54, inst54_population, stagnation, elitism_size=1):
    best = min(inst54_population, key=inst54.objective_function)
    created = []

    def construct():
        solution = best.copy()
        solution.immigrant = Immigrant()
        created.append(solution)
        return solution

    parameters = DiversityParameters(problem=inst54, objective_max=False, elitism_size=elitism_size,
                                     construct=construct, mutate=lambda s: None)
    parameters.stagnation = stagnation
    return parameters, created, best


def is_immigrant(solution):
    return isinstance(getattr(solution, "immigrant", None), Immigrant)


def worst_first(problem, population):
    return sorted(population, key=problem.objective_function, reverse=True)


def test_no_diversity_changes_nothing(inst54, inst54_population):
    parameters, created, _ = setup(inst54, inst54_population, stagnation=7)
    no_diversity = operator("NO_DIVERSITY_OPERATOR")
    assert no_diversity.apply(inst54_population, parameters) is inst54_population
    assert no_diversity.mutation_rate(0.2) == 0.2 and not created


@pytest.mark.parametrize("stagnation, acts", [(0, False), (3, False), (5, True), (7, False), (10, True)])
def test_random_immigrants_replace_the_worst_every_k_generations(inst54, inst54_population, stagnation, acts):
    parameters, created, best = setup(inst54, inst54_population, stagnation)
    population = operator("RANDOM_IMMIGRANTS_DIVERSITY_OPERATOR", stagnation=5, fraction=0.3).apply(
        inst54_population, parameters)
    assert len(population) == len(inst54_population)
    assert len(created) == (6 if acts else 0)                 # 30 % de 20
    if acts:
        replaced = {id(s) for s in inst54_population} - {id(s) for s in population}
        assert replaced == {id(s) for s in worst_first(inst54, inst54_population)[:6]}
        assert best in population


def test_hypermutation_raises_the_rate_for_a_few_generations():
    hypermutation = operator("TRIGGERED_HYPERMUTATION_DIVERSITY_OPERATOR", stagnation=2, factor=4, duration=2)
    parameters = DiversityParameters(problem=None)
    rates = []
    for stagnation in [0, 1, 2, 3, 4, 5, 0, 1]:
        parameters.stagnation = stagnation
        hypermutation.apply([], parameters)
        rates.append(hypermutation.mutation_rate(0.2))
    # Se activa con 2 y 4 generaciones sin mejora, dura 2 generaciones y se apaga al mejorar (0)
    assert rates == pytest.approx([0.2, 0.2, 0.8, 0.8, 0.8, 0.8, 0.2, 0.2])
    assert hypermutation.mutation_rate(0.5) <= 1.0


def test_cataclysmic_restart_keeps_the_elite_and_regenerates_the_rest(inst54, inst54_population):
    mutated = []
    parameters, created, best = setup(inst54, inst54_population, stagnation=10, elitism_size=2)
    parameters.mutate = mutated.append
    population = operator("CATACLYSMIC_RESTART_DIVERSITY_OPERATOR", stagnation=10, mutations=3,
                          fraction_new=0.5).apply(inst54_population, parameters)
    survivors = [s for s in population if any(s is old for old in inst54_population)]
    assert len(population) == 20 and len(survivors) == 2 and best in survivors
    assert len(created) == 9 and len(mutated) == 9 * 3      # 18 sustituidos: mitad nuevos, mitad mutados ×3


def test_clearing_replaces_near_duplicates_but_keeps_the_best(inst54, inst54_population):
    parameters, created, best = setup(inst54, inst54_population, stagnation=0)
    population = [best] + [best.copy() for _ in range(3)] + list(inst54_population[:5])
    cleared = operator("CLEARING_DIVERSITY_OPERATOR_SBRP", min_distance=0.05).apply(population, parameters)
    assert cleared[0] is best and len(cleared) == len(population)
    assert sum(is_immigrant(s) for s in cleared[1:4]) == 3     # las tres copias de la mejor


@pytest.mark.parametrize("name, params", [
    ("RANDOM_IMMIGRANTS_DIVERSITY_OPERATOR", {"stagnation": 2}),
    ("TRIGGERED_HYPERMUTATION_DIVERSITY_OPERATOR", {"stagnation": 2}),
    ("CATACLYSMIC_RESTART_DIVERSITY_OPERATOR", {"stagnation": 3}),
    ("CLEARING_DIVERSITY_OPERATOR_SBRP", {"min_distance": 0.2}),
])
def test_ga_with_each_diversity_operator_keeps_size_and_the_best(name, params):
    best_so_far = []

    def on_generation(generation, population, problem, stats):
        assert len(population) == 30
        best_so_far.append(problem.objective_function(problem.best_solution))

    problem, fitness, *_ = run_ga(8, seed=2, on_generation=on_generation, max_iter=12, max_stagnation_iter=12,
                                  diversity_operator=operator(name, **params))
    assert problem.is_feasible(problem.best_solution)
    assert best_so_far == sorted(best_so_far, reverse=True)       # la mejor solución nunca empeora


@pytest.mark.parametrize("name, params", [
    ("RANDOM_IMMIGRANTS_DIVERSITY_OPERATOR", {"fraction": 0}),
    ("TRIGGERED_HYPERMUTATION_DIVERSITY_OPERATOR", {"factor": 0.5}),
    ("CATACLYSMIC_RESTART_DIVERSITY_OPERATOR", {"mutations": 0}),
    ("CLEARING_DIVERSITY_OPERATOR_SBRP", {"min_distance": 0}),
])
def test_diversity_parameters_are_validated(name, params):
    with pytest.raises(ValueError):
        operator(name, **params)
