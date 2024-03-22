from abc import ABC, abstractmethod

from src.problems.problem_parameters import ProblemParameters


class Problem(ABC):
    @abstractmethod
    def construct(self, problem_parameters: ProblemParameters):
        pass

    @abstractmethod
    def objective_function(self, solution):
        pass

    @abstractmethod
    def initial_random_solution(self):
        pass

    @abstractmethod
    def initial_heuristic_solution(self):
        pass
