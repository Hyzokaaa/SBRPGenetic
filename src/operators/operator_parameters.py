from src.operators.distance.distance_operator import Distance
from src.problems.problem_sbrp.initial_solution.route_generation.route_generator_strategy import RouteGeneratorStrategy
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class OperatorParameters:
    def __init__(self,
                 distance_operator: Distance = None,
                 problem: ProblemSBRP = None,
                 route_generator_strategy: RouteGeneratorStrategy = None):
        self.problem: ProblemSBRP = problem
        self.distance_operator = distance_operator
        self.route_generator_strategy = route_generator_strategy
