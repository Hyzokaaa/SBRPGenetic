from abc import ABC, abstractmethod

from src.operators.operator_parameters import OperatorParameters


class InitialConstructionOperator(ABC):
    @abstractmethod
    def generate(self, parameters: OperatorParameters):
        pass
