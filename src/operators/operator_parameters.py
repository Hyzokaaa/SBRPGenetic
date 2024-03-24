from src.operators.distance.distance_operator import Distance
from src.problems.problem import Problem


class OperatorParameters:
    def __init__(self,
                 distance_operator: Distance,
                 problem: Problem):
        self.problem = problem
        self.distance_operator = distance_operator
