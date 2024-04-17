import copy

from src.operators.initial_construction.initial_construction import InitialConstructionOperator
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.operators.operator_parameters import OperatorParameters
from src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.route_generator_strategy import RouteGeneratorStrategy
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class RouteGenerator(InitialConstructionOperator):

    def generate(self, parameters: InitialConstructionParameters):
        problem: ProblemSBRP = copy.deepcopy(parameters.problem)
        strategy: RouteGeneratorStrategy = parameters.route_generator_strategy

        routes = []
        for _ in problem.vehicles:
            route = strategy.generate_route(problem=problem, distance_operator=parameters.distance_operator)
            routes.append(route)
        return routes
