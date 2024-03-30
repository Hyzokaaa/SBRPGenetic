from abc import ABC, abstractmethod

from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem import Problem


class StopAssignStrategy(ABC):

    @abstractmethod
    def generate_stop_assign(self, problem: Problem, distance_operator: DistanceOperator):
        pass
