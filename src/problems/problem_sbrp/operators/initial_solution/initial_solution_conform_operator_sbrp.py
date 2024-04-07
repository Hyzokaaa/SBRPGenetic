from src.operators.initial_construction.initial_construction import InitialConstructionOperator
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.operators.operator_parameters import OperatorParameters
from src.problems.problem_sbrp.operators.initial_solution.route_generation.route_generator import RouteGenerator
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.stop_assigner import StopAssigner


class InitialSolutionOperatorSBRP(InitialConstructionOperator):

    def generate(self, parameters: InitialConstructionParameters):
        stop_assign = StopAssigner()
        route_generator = RouteGenerator()

        stop_assign.generate(parameters=parameters)
        routes = route_generator.generate(parameters=parameters)
        return routes
