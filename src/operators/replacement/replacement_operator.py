from abc import ABC, abstractmethod


class ReplacementOperator(ABC):
    @abstractmethod
    def replacement(self, solutions: []):
        pass
