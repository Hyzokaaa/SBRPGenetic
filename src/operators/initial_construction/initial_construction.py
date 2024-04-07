from abc import ABC, abstractmethod

from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.operators.operator_parameters import OperatorParameters


class InitialConstructionOperator(ABC):
    @abstractmethod
    def generate(self, parameters: InitialConstructionParameters):
        pass
