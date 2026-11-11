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
    """
    Genera cada solución completa con la heurística del vecino más cercano (con probabilidad
    closest_neighbor_probability) o de forma aleatoria. La decisión se toma por solución, no por ruta.
    """

    def __init__(self, closest_neighbor_probability: float = 0.02):
        self.closest_neighbor_probability = closest_neighbor_probability
        self.closest_neighbor_strategy = HClosestNeighborRouteGeneratorStrategy()
        self.random_strategy = RandomRouteGeneratorStrategy()
        self.current_strategy: RouteGeneratorStrategy = self.random_strategy

    def start_solution(self):
        if random.random() < self.closest_neighbor_probability:
            self.current_strategy = self.closest_neighbor_strategy
        else:
            self.current_strategy = self.random_strategy

    def generate_route(self, problem: ProblemSBRP, distance_operator: DistanceOperator):
        return self.current_strategy.generate_route(problem, distance_operator)
