from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem import Problem
from src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.route_generator_strategy import RouteGeneratorStrategy
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.strategy.stop_assign_strategy import StopAssignStrategy


class OperatorParameters:
    def __init__(self, problem: Problem = None):
        self.problem: Problem = problem
