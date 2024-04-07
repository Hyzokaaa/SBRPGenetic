from abc import ABC, abstractmethod

from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.operators.operator_parameters import OperatorParameters


class CrossoverOperator(ABC):
    @abstractmethod
    def crossover(self, parameters: CrossoverParameters):
        pass
