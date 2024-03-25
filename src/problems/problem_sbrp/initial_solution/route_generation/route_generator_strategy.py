from abc import ABC, abstractmethod

from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class RouteGeneratorStrategy(ABC):

    @abstractmethod
    def generate_route(self, problem: ProblemSBRP):
        pass
