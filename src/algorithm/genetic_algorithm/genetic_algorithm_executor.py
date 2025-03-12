from src.algorithm.algorithm_parameters import AlgorithmParameters
from src.algorithm.genetic_algorithm.genetic_algorithm import GeneticAlgorithm
from src.algorithm.genetic_algorithm.genetic_algorithm_config import GeneticAlgorithmConfig
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.operators.mutation.mutation_parameters import MutationParameters
from src.operators.repair.repair_parameters import RepairParameters
from src.operators.selection.selection_parameters import SelectionParameters


class GeneticAlgorithmExecutor:
    def execute(self, config: GeneticAlgorithmConfig):
        problem_parameters = config.data_input.conform()
        problem = config.problem
        problem.construct(problem_parameters=problem_parameters)

        initial_construction_parameters = InitialConstructionParameters(
            problem=problem,
            distance_operator=config.distance_operator,
            stop_assign_strategy=config.stop_assign_strategy,
            route_generator_strategy=config.route_generator_strategy)

        selection_parameters = SelectionParameters(problem=config.problem,
                                                   objective_max=config.objective_max,
                                                   tournament_size=config.tournament_size,
                                                   number_of_selected_solutions=config.number_of_selected_solutions)

        crossover_parameters = CrossoverParameters(problem=config.problem)

        repair_parameters = RepairParameters(problem=config.problem)

        mutation_parameters = MutationParameters(problem=config.problem,
                                                 distance_operator=config.distance_operator)

        algorithm_parameters = AlgorithmParameters(problem=config.problem,
                                                   objective_max=config.objective_max,
                                                   initial_population_size=config.initial_population_size,
                                                   max_iter=config.max_iter,
                                                   max_stagnation_iter=config.max_stagnation_iter,
                                                   mutation_rate=config.mutation_rate,
                                                   crossover_rate=config.crossover_rate,
                                                   initial_construction_operator=config.initial_construction_operator,
                                                   initial_construction_parameters=initial_construction_parameters,
                                                   selection_operator=config.selection_operator,
                                                   selection_parameters=selection_parameters,
                                                   crossover_operator=config.crossover_operator,
                                                   crossover_parameters=crossover_parameters,
                                                   repair_parameters=repair_parameters,
                                                   repair_operator=config.repair_operator,
                                                   mutation_parameters=mutation_parameters,
                                                   mutation_operator=config.mutation_operator
                                                   )
        optimization_algorithm = GeneticAlgorithm()

        data = optimization_algorithm.optimize(algorithm_parameters)
        #print("Mejor ruta:")
        #print(data[0].best_solution.routes)
        #print("Mejor Fitness: " + f'{data[1]}')
        #print("Mejor Iteracion: " + f'{data[2]}')
        return data
