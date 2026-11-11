from abc import ABC, abstractmethod

from src.operators.distance.distance_operator import DistanceOperator


class RouteGeneratorStrategy(ABC):

    def start_solution(self):
        """
        Se invoca antes de generar las rutas de cada nueva solución.
        """
        pass

    @abstractmethod
    def generate_route(self, problem, distance_operator: DistanceOperator):
        pass
