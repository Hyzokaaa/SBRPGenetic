from abc import ABC, abstractmethod

from src.problems.problem import Problem


class OptimizationAlgorithm(ABC):

    @abstractmethod
    def optimize(self, problem: Problem):
        pass
