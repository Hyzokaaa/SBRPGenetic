from src.operators.initial_construction.initial_solution import InitialConstruction
from src.operators.operator_parameters import OperatorParameters
from src.problems.problem_sbrp.initial_solution.route_generation.route_generator_strategy import RouteGeneratorStrategy
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class RouteGenerator(InitialConstruction):

    def generate(self, parameters: OperatorParameters):
        problem: ProblemSBRP = parameters.problem
        strategy: RouteGeneratorStrategy = parameters.route_generator_strategy

        routes = []
        for _ in problem.vehicles:
            route = strategy.generate_route(problem=problem)
            routes.append(route)
        return routes
