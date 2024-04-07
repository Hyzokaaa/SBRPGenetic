from abc import ABC, abstractmethod

from src.operators.mutation.mutation_parameters import MutationParameters


class MutationOperator(ABC):
    @abstractmethod
    def mutate(self, parameters: MutationParameters):
        pass
