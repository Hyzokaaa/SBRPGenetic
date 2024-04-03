from abc import ABC, abstractmethod

from src.operators.selection.selection_parameters import SelectionParameters


class SelectionOperator(ABC):
    @abstractmethod
    def selection(self, parameters: SelectionParameters):
        pass
