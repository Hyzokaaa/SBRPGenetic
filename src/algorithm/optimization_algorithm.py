from abc import ABC, abstractmethod

from src.algorithm.algorithm_parameters import AlgorithmParameters
from src.problems.problem import Problem


class OptimizationAlgorithm(ABC):

    @abstractmethod
    def optimize(self, parameters: AlgorithmParameters):
        pass







