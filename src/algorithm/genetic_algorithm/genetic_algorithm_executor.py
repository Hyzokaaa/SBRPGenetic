import time

from src.algorithm.algorithm_parameters import AlgorithmParameters
from src.algorithm.genetic_algorithm.genetic_algorithm import GeneticAlgorithm
from src.algorithm.genetic_algorithm.genetic_algorithm_config import GeneticAlgorithmConfig
from src.algorithm.hill_climbing_algorithm.hill_climbing_algorithm import HillClimbingAlgorithm
from src.algorithm.random_search_algorithm.random_search_algorithm import RandomSearchAlgorithm
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.operators.mutation.mutation_parameters import MutationParameters
from src.operators.repair.repair_parameters import RepairParameters
from src.operators.selection.selection_parameters import SelectionParameters

# Algoritmos que se pueden indicar en la clave "algorithm" de la configuración
ALGORITHMS = {
    "GA": GeneticAlgorithm,
    "RANDOM_SEARCH": RandomSearchAlgorithm,
    "HILL_CLIMBING": HillClimbingAlgorithm,
}


class GeneticAlgorithmExecutor:
    def execute(self, config: GeneticAlgorithmConfig, on_generation=None):
        """
        Ejecuta el algoritmo de la configuración. Con un portafolio de asignaciones (stop_assign_portfolio), lo
        ejecuta una vez por asignación, cada vez sobre un problema nuevo y con el presupuesto completo de la
        configuración, y devuelve el mejor resultado; el tiempo es la suma de todas las ejecuciones. El problema
        devuelto indica la asignación ganadora (assignment_label) y el resultado de cada una (portfolio_results).
        """
        if not config.stop_assign_portfolio:
            return self.execute_rounds(config, config.problem, config.stop_assign_strategy, on_generation)

        best, best_label, results, total_time = None, None, [], 0.0
        for label, strategy in zip(config.stop_assign_portfolio_labels, config.stop_assign_portfolio):
            result = self.execute_rounds(config, type(config.problem)(), strategy, on_generation)
            total_time += result[3]
            results.append((label, result[1]))
            if result[1] is not None and (best is None or best[1] is None or (
                    result[1] > best[1] if config.objective_max else result[1] < best[1])):
                best, best_label = result, label
            elif best is None:
                best = result
        problem = best[0]
        problem.assignment_label = best_label
        problem.portfolio_results = results
        return problem, best[1], best[2], total_time, best[4], best[5]

    def execute_rounds(self, config: GeneticAlgorithmConfig, problem, stop_assign_strategy, on_generation=None):
        """
        Ejecuta el algoritmo y, si la configuración tiene mejora de la asignación, la aplica a la mejor solución y
        vuelve a ejecutar el algoritmo con la nueva asignación, hasta assignment_rounds ejecuciones o hasta que la
        mejora no cambie nada. El problema conserva la mejor solución entre ejecuciones, así que el resultado nunca
        empeora. problem.assignment_changes cuenta los cambios hechos (por ejemplo, paradas cerradas).
        """
        start = time.time()
        result = self.execute_once(config, problem, stop_assign_strategy, on_generation)
        problem.assignment_changes = 0
        improver = config.assignment_improvement_operator
        for round_number in range(1, max(1, config.assignment_rounds or 1) + 1):
            if improver is None or problem.best_solution is None:
                break
            changes = improver.improve(problem, config.distance_operator)
            problem.assignment_changes += changes
            if not changes or round_number >= config.assignment_rounds:
                break
            # La asignación ya está hecha: se ejecuta de nuevo sin reconstruir el problema ni reasignar
            result = self.execute_once(config, problem, None, on_generation, construct=False)
        fitness = problem.objective_function(problem.best_solution) if problem.best_solution is not None else None
        return problem, fitness, result[2], time.time() - start, result[4], result[5]

    def execute_once(self, config: GeneticAlgorithmConfig, problem, stop_assign_strategy, on_generation=None,
                     construct: bool = True):
        if construct:
            problem_parameters = config.data_input.conform()
            problem.construct(problem_parameters=problem_parameters)

        initial_construction_parameters = InitialConstructionParameters(
            problem=problem,
            distance_operator=config.distance_operator,
            stop_assign_strategy=stop_assign_strategy,
            route_generator_strategy=config.route_generator_strategy)

        selection_parameters = SelectionParameters(problem=problem,
                                                   objective_max=config.objective_max,
                                                   tournament_size=config.tournament_size,
                                                   number_of_selected_solutions=config.number_of_selected_solutions)

        crossover_parameters = CrossoverParameters(problem=problem)

        repair_parameters = RepairParameters(problem=problem)

        mutation_parameters = MutationParameters(problem=problem,
                                                 distance_operator=config.distance_operator)

        algorithm_parameters = AlgorithmParameters(problem=problem,
                                                   objective_max=config.objective_max,
                                                   initial_population_size=config.initial_population_size,
                                                   max_iter=config.max_iter,
                                                   max_stagnation_iter=config.max_stagnation_iter,
                                                   mutation_rate=config.mutation_rate,
                                                   crossover_rate=config.crossover_rate,
                                                   elitism_size=config.elitism_size if config.elitism_size is not None else 1,
                                                   on_generation=on_generation,
                                                   initial_construction_operator=config.initial_construction_operator,
                                                   initial_construction_parameters=initial_construction_parameters,
                                                   selection_operator=config.selection_operator,
                                                   selection_parameters=selection_parameters,
                                                   crossover_operator=config.crossover_operator,
                                                   crossover_parameters=crossover_parameters,
                                                   repair_parameters=repair_parameters,
                                                   repair_operator=config.repair_operator,
                                                   mutation_parameters=mutation_parameters,
                                                   mutation_operator=config.mutation_operator,
                                                   replacement_operator=config.replacement_operator,
                                                   diversity_operator=config.diversity_operator
                                                   )
        if config.algorithm not in ALGORITHMS:
            raise ValueError(f"Algoritmo desconocido: {config.algorithm}. Opciones: {', '.join(ALGORITHMS)}")
        optimization_algorithm = ALGORITHMS[config.algorithm]()

        return optimization_algorithm.optimize(algorithm_parameters)
