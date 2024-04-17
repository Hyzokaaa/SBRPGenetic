from src.algorithm.algorithm_parameters import AlgorithmParameters
from src.algorithm.exhaustive_search.exhaustive_search import ExhaustiveSearch
from src.algorithm.exhaustive_search.exhaustive_search_config import ExhaustiveSearchConfig
from src.operators.exhaustive_search.exhaustive_search_operator import ExhaustiveSearchOperator
from src.operators.exhaustive_search.exhaustive_search_parameters import ExhaustiveSearchParameters
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters


class ExhaustiveSearchExecutor:
    def execute(self, config: ExhaustiveSearchConfig):
        problem_parameters = config.data_input.conform()
        problem = config.problem
        problem.construct(problem_parameters=problem_parameters)

        initial_construction_parameters = InitialConstructionParameters(
            problem=problem,
            distance_operator=config.distance_operator,
            stop_assign_strategy=config.stop_assign_strategy)

        exhaustive_search_parameters = ExhaustiveSearchParameters(problem=config.problem,
                                                                  distance_operator=config.distance_operator,
                                                                  initial_construction_parameters=initial_construction_parameters,
                                                                  stop_assign_strategy=config.stop_assign_strategy,
                                                                  route_generator_strategy=config.route_generator_strategy)

        algorithm_parameters = AlgorithmParameters(problem=config.problem,
                                                   objective_max=config.objective_max,
                                                   initial_construction_operator=config.initial_construction_operator,
                                                   initial_construction_parameters=initial_construction_parameters,
                                                   exhaustive_search_parameters=exhaustive_search_parameters,
                                                   exhaustive_search_operator=config.exhaustive_search_operator
                                                   )
        optimization_algorithm = ExhaustiveSearch()

        data = optimization_algorithm.optimize(algorithm_parameters)
        return data
