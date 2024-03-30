from src.operators.initial_construction.initial_solution import InitialConstructionOperator
from src.operators.operator_parameters import OperatorParameters
from src.problems.problem_sbrp.operators.initial_solution.route_generation.route_generator import RouteGenerator
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.stop_assigner import StopAssigner


class InitialSolutionConformOperator(InitialConstructionOperator):

    def generate(self, parameters: OperatorParameters):
        stop_assign = StopAssigner()
        route_generator = RouteGenerator()

        stop_assign.generate(parameters=parameters)
        routes = route_generator.generate(parameters=parameters)
        return routes
