import random
from types import SimpleNamespace

import pytest

from conftest import CONFIGS, INSTANCES
from src.algorithm.genetic_algorithm.genetic_algorithm_config import GeneticAlgorithmConfig
from src.algorithm.genetic_algorithm.genetic_algorithm_executor import GeneticAlgorithmExecutor
from src.algorithm.hill_climbing_algorithm.hill_climbing_algorithm import HillClimbingAlgorithm
from src.operators.replacement.generational_replacement_operator import GenerationalReplacementOperator


def run_ga(config_number=8, seed=1, instance="real/inst54-7s20-100-c50-w20.xpress", on_generation=None, **overrides):
    random.seed(seed)
    config = GeneticAlgorithmConfig()
    config.load_from_file(str(CONFIGS / f"config{config_number}.json"), str(INSTANCES / instance))
    config.initial_population_size, config.max_iter, config.max_stagnation_iter = 30, 6, 6
    for key, value in overrides.items():
        setattr(config, key, value)
    return GeneticAlgorithmExecutor().execute(config, on_generation=on_generation)


@pytest.mark.parametrize("config_number", range(1, 20))
def test_every_config_returns_a_feasible_best_solution(config_number):
    problem, fitness, *_ = run_ga(config_number)
    assert problem.best_solution is not None
    assert problem.is_feasible(problem.best_solution)
    assert fitness == problem.objective_function(problem.best_solution)


def test_same_seed_gives_same_result():
    first, second, other = run_ga(seed=3), run_ga(seed=3), run_ga(seed=4)
    assert first[1:3] == second[1:3]
    assert first[0].solution_signature(first[0].best_solution) == second[0].solution_signature(second[0].best_solution)
    assert other[0].best_solution is not None


def test_select_elite_returns_copies_of_the_best_distinct_solutions(inst54, inst54_population):
    parameters = SimpleNamespace(problem=inst54, elitism_size=2, objective_max=False)
    elite = GenerationalReplacementOperator.select_elite(inst54_population, parameters)
    ranked = sorted(inst54_population, key=inst54.objective_function)
    assert [inst54.objective_function(s) for s in elite] == [inst54.objective_function(s) for s in ranked[:2]]
    assert all(e is not s for e in elite for s in inst54_population)


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_elitism_keeps_the_best_solution_in_the_population(seed):
    # Con cruce y mutación en todos los hijos, la mejor solución solo sobrevive gracias al elitismo
    def on_generation(generation, population, problem, stats):
        feasible = [problem.objective_function(s) for s in population if problem.is_feasible(s)]
        assert min(feasible) == pytest.approx(problem.objective_function(problem.best_solution))

    run_ga(seed=seed, on_generation=on_generation, crossover_rate=1.0, mutation_rate=1.0, max_iter=10)


def test_population_has_no_duplicates():
    def on_generation(generation, population, problem, stats):
        signatures = {problem.solution_signature(s) for s in population}
        assert len(signatures) >= 0.9 * len(population)

    run_ga(on_generation=on_generation)


@pytest.mark.parametrize("config_number", [10, 11])
def test_baselines_use_the_same_budget_as_the_ga(config_number):
    # Cada generación equivalente evalúa tantas soluciones como la población del GA
    sizes = []
    problem, fitness, _, _, stop_reason, stop_iteration = run_ga(
        config_number, on_generation=lambda generation, block, problem, stats: sizes.append(len(block)))
    assert sizes == [30] * 7 and (stop_reason, stop_iteration) == ("max_iter", 6)
    assert problem.is_feasible(problem.best_solution)


@pytest.mark.parametrize("config_number", [10, 11])
def test_baselines_are_reproducible(config_number):
    first, second = run_ga(config_number, seed=5), run_ga(config_number, seed=5)
    assert first[1:3] == second[1:3]


def test_hill_climbing_never_worsens_its_current_solution(monkeypatch):
    current = []
    next_block = HillClimbingAlgorithm.next_block

    def recording_next_block(self):
        block = next_block(self)
        current.append(self.parameters.problem.objective_function(self.current))
        return block

    monkeypatch.setattr(HillClimbingAlgorithm, "next_block", recording_next_block)
    problem, fitness, *_ = run_ga(11, max_iter=15, max_stagnation_iter=15)
    assert current == sorted(current, reverse=True) and current[-1] < current[0]
    assert fitness == current[-1]


def test_unknown_algorithm_is_rejected():
    with pytest.raises(ValueError, match="Algoritmo desconocido"):
        run_ga(8, algorithm="TABU")


PORTFOLIO = ["H_STUDENT_TO_STOP_CLOSEST_TO_SCHOOL_STRATEGY",
             {"name": "H_STUDENT_TO_FEWEST_STOPS_STRATEGY", "params": {"school_weight": 3.0}}]


def run_portfolio(seed=1, instance="real/inst32-6s10-50-c50-w40.xpress"):
    from src.algorithm.genetic_algorithm.genetic_algorithm_config import instantiate, operator_label
    random.seed(seed)
    config = GeneticAlgorithmConfig()
    config.load_from_file(str(CONFIGS / "config14.json"), str(INSTANCES / instance))
    config.initial_population_size, config.max_iter, config.max_stagnation_iter = 30, 6, 7
    config.stop_assign_portfolio = [instantiate(item) for item in PORTFOLIO]
    config.stop_assign_portfolio_labels = [operator_label(item) for item in PORTFOLIO]
    return GeneticAlgorithmExecutor().execute(config)


def test_portfolio_returns_the_best_assignment():
    problem, fitness, _, execution_time, *_ = run_portfolio()
    results = dict(problem.portfolio_results)
    assert set(results) == {"H_STUDENT_TO_STOP_CLOSEST_TO_SCHOOL_STRATEGY",
                            "H_STUDENT_TO_FEWEST_STOPS_STRATEGY(school_weight=3.0)"}
    assert fitness == min(results.values()) == results[problem.assignment_label]
    # En inst32 (w = 40) concentrar a los estudiantes en pocas paradas es mucho mejor
    assert problem.assignment_label.startswith("H_STUDENT_TO_FEWEST_STOPS_STRATEGY")
    assert problem.is_feasible(problem.best_solution) and fitness == problem.objective_function(problem.best_solution)


def test_portfolio_is_reproducible():
    first, second = run_portfolio(seed=4), run_portfolio(seed=4)
    assert first[1] == second[1] and first[0].portfolio_results == second[0].portfolio_results
