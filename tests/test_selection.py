import collections
import random

import pytest

import src.operators.selection.tournament_selection_operator as tournament_module
from conftest import operator, solution, synthetic_problem
from src.operators.selection.selection_parameters import SelectionParameters


def mixed_population():
    problem = synthetic_problem([(1, 0), (2, 0), (0, 3)], [2, 3, 4], vehicles=3, capacity=5)
    # Dos soluciones factibles con distancias distintas
    feasible = [solution(problem, [1, 2], [3]), solution(problem, [1], [2], [3])]
    infeasible = [solution(problem, [1, 2]),          # falta la parada 3: grado 4 y distancia mínima
                  solution(problem, [1, 2, 3])]       # sobrecapacidad: grado 4
    return problem, feasible, infeasible


def test_tournament_prefers_feasible_then_best_fitness(monkeypatch):
    problem, feasible, infeasible = mixed_population()
    monkeypatch.setattr(tournament_module.random, "sample", lambda population, k: list(population))
    for objective_max in (False, True):
        selected = operator("TOURNAMENT_SELECTION_OPERATOR").selection(SelectionParameters(
            problem=problem, solutions=feasible + infeasible, objective_max=objective_max,
            number_of_selected_solutions=2, tournament_size=2))
        ranked = sorted(feasible, key=problem.objective_function, reverse=objective_max)
        assert selected[0] is ranked[0] and selected[1] is ranked[1]


def test_tournament_among_infeasible_prefers_lower_violation(monkeypatch):
    problem = synthetic_problem([(1, 0), (2, 0), (0, 3)], [2, 3, 4], vehicles=2, capacity=5)
    worse = solution(problem, [1])        # faltan 3 y 4 estudiantes: grado 7
    better = solution(problem, [1, 2])    # faltan 4 estudiantes: grado 4
    monkeypatch.setattr(tournament_module.random, "sample", lambda population, k: list(population))
    selected = operator("TOURNAMENT_SELECTION_OPERATOR").selection(SelectionParameters(
        problem=problem, solutions=[worse, better], objective_max=False, number_of_selected_solutions=1,
        tournament_size=2))
    assert selected == [better]


def test_roulette_never_repeats_and_prefers_feasible():
    problem, feasible, infeasible = mixed_population()
    random.seed(1)
    roulette = operator("ROULETTE_SELECTION_OPERATOR")
    for objective_max in (False, True):
        for _ in range(300):
            selected = roulette.selection(SelectionParameters(problem=problem, solutions=feasible + infeasible,
                                                              objective_max=objective_max))
            assert len(selected) == 2 and selected[0] is not selected[1]
            assert all(problem.is_feasible(s) for s in selected)


def test_roulette_completes_with_least_violating():
    problem, feasible, infeasible = mixed_population()
    random.seed(1)
    selected = operator("ROULETTE_SELECTION_OPERATOR").selection(SelectionParameters(
        problem=problem, solutions=[feasible[0]] + infeasible, objective_max=False))
    assert len(selected) == 2 and selected[0] is feasible[0]


def ranked_population():
    problem, feasible, infeasible = mixed_population()
    population = feasible + infeasible
    key = lambda s: (problem.constraint_violation(s), problem.objective_function(s))
    return problem, sorted(population, key=key)


def first_pick_frequencies(name, problem, population, draws=4000, **params):
    selector = operator(name, **params)
    counts = collections.Counter()
    for _ in range(draws):
        first = selector.selection(SelectionParameters(problem=problem, solutions=population, objective_max=False,
                                                       number_of_selected_solutions=2,
                                                       tournament_size=len(population)))[0]
        counts[population.index(first)] += 1
    return [counts[i] / draws for i in range(len(population))]


def test_random_selection_is_uniform_and_never_repeats():
    problem, population = ranked_population()
    random.seed(2)
    frequencies = first_pick_frequencies("RANDOM_SELECTION_OPERATOR", problem, population)
    assert all(f == pytest.approx(0.25, abs=0.03) for f in frequencies)
    selected = operator("RANDOM_SELECTION_OPERATOR").selection(SelectionParameters(
        problem=problem, solutions=population, number_of_selected_solutions=4))
    assert len({id(s) for s in selected}) == 4


def test_probabilistic_tournament_occasionally_picks_at_random():
    problem, population = ranked_population()
    random.seed(3)
    # Torneo con toda la población: sin azar elige siempre al mejor; con p = 0.4, el resto aparece en 0.4·3/4
    assert first_pick_frequencies("PROBABILISTIC_TOURNAMENT_SELECTION_OPERATOR", problem, population, draws=500,
                                  random_probability=0.0)[0] == 1.0
    frequencies = first_pick_frequencies("PROBABILISTIC_TOURNAMENT_SELECTION_OPERATOR", problem, population,
                                         random_probability=0.4)
    assert 1 - frequencies[0] == pytest.approx(0.4 * 3 / 4, abs=0.03)


def test_linear_ranking_matches_its_probabilities():
    problem, population = ranked_population()
    random.seed(4)
    # N = 4, presión 1.5: probabilidades 1.5/4, ..., 0.5/4 de mejor a peor
    expected = [(0.5 + 2 * (3 - i) * 0.5 / 3) / 4 for i in range(4)]
    frequencies = first_pick_frequencies("LINEAR_RANKING_SELECTION_OPERATOR", problem, population, pressure=1.5)
    assert frequencies == pytest.approx(expected, abs=0.03)
    # Presión máxima: el peor no se elige nunca entre los dos primeros
    assert first_pick_frequencies("LINEAR_RANKING_SELECTION_OPERATOR", problem, population, draws=500,
                                  pressure=2.0)[3] == 0


@pytest.mark.parametrize("name, params", [("PROBABILISTIC_TOURNAMENT_SELECTION_OPERATOR", {"random_probability": 1.5}),
                                          ("LINEAR_RANKING_SELECTION_OPERATOR", {"pressure": 0.5})])
def test_selection_parameters_are_validated(name, params):
    with pytest.raises(ValueError):
        operator(name, **params)
