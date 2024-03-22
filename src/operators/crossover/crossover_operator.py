from abc import ABC, abstractmethod


class CrossoverOperator(ABC):
    @abstractmethod
    def crossover(self, parent1,  parent2):
        pass
