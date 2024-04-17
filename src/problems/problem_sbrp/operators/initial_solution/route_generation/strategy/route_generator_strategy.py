from abc import ABC, abstractmethod

from src.operators.distance.distance_operator import DistanceOperator


class RouteGeneratorStrategy(ABC):

    @abstractmethod
    def generate_route(self, problem, distance_operator: DistanceOperator):
        pass
