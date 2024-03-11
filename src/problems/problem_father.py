from abc import ABC, abstractmethod


class ProblemFather(ABC):
    @abstractmethod
    def objective_function(self, solution):
        pass
