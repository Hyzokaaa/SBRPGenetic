from abc import ABC, abstractmethod


class SelectionOperator(ABC):
    @abstractmethod
    def selection(self, solutions: []):
        pass
