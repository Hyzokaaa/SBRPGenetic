from abc import ABC, abstractmethod

from src.operators.crossover.crossover_parameters import CrossoverParameters


class CrossoverOperator(ABC):
    @abstractmethod
    def crossover(self, parameters: CrossoverParameters):
        pass
