from copy import deepcopy
from typing import List
from src.problems.problem_sbrp.model.stop import Stop


class Route:
    def __init__(self, stops: List[Stop] = None):
        self.students = 0
        if stops is None:
            self.stops = []
        else:
            self.stops = stops

    def __str__(self):
        return f"Route: {', '.join(str(stop) for stop in self.stops)})"

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return deepcopy(self)