from abc import ABC, abstractmethod

from src.operators.exhaustive_search.exhaustive_search_parameters import ExhaustiveSearchParameters


class ExhaustiveSearchOperator(ABC):
    @abstractmethod
    def generate(self, parameters: ExhaustiveSearchParameters):
        pass
