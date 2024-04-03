from abc import ABC, abstractmethod

from src.operators.initial_construction.initial_solution_parameters import InitialSolutionParameters
from src.operators.operator_parameters import OperatorParameters


class InitialConstructionOperator(ABC):
    @abstractmethod
    def generate(self, parameters: InitialSolutionParameters):
        pass
