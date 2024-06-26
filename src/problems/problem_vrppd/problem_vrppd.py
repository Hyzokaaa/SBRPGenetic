from typing import List

from src.problems.problem import Problem
from src.problems.problem_parameters import ProblemParameters


class ProblemVRPPD(Problem):
    def __init__(self):
        self.tasks: List[Task]
    def construct(self, problem_parameters: ProblemParameters):
        pass

    def objective_function(self, solution):
        pass
