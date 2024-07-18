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
    def compare_solutions(self, solution1, solution2, objective_max):
        pass

    @abstractmethod
    def update_best_solution(self, best_iteration, current_iteration, objective_max, population):
        pass
