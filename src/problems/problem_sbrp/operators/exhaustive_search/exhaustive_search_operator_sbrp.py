from src.operators.exhaustive_search.exhaustive_search_operator import ExhaustiveSearchOperator
from src.operators.exhaustive_search.exhaustive_search_parameters import ExhaustiveSearchParameters
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.stop_assigner import StopAssigner


class ExhaustiveSearchOperatorSBRP(ExhaustiveSearchOperator):

    def generate(self, parameters: ExhaustiveSearchParameters):
        stop_assign = StopAssigner()

        stop_assign.generate(parameters.initial_construction_parameters)

        routes = parameters.route_generator_strategy.generate_route(distance_operator=parameters.distance_operator,
                                                                    problem=parameters.problem)

        return routes
