import random

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
