import random

from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.h_closest_neighbor_route_generator_strategy import \
    HClosestNeighborRouteGeneratorStrategy
from src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.random_route_generator_strategy import \
    RandomRouteGeneratorStrategy
from src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.route_generator_strategy import \
    RouteGeneratorStrategy
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class HClosestNeighborAndRandomRouteGeneratorStrategy(RouteGeneratorStrategy):
    def generate_route(self, problem: ProblemSBRP,  distance_operator: DistanceOperator):
        if random.random() < 0.02:
            return HClosestNeighborRouteGeneratorStrategy().generate_route(problem, distance_operator)
        else:
            return RandomRouteGeneratorStrategy().generate_route(problem, distance_operator)
