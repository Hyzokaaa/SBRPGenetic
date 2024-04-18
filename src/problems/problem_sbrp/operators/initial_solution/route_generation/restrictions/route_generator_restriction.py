from typing import List

from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class RouteGeneratorRestriction:
    @staticmethod
    def get_non_assign_stops_with_students(problem: ProblemSBRP):
        return [stop for stop in problem.stops if stop.is_assigned is False and stop.num_assigned_students > 0]

    @staticmethod
    def get_non_exceed_bus_capacity(non_assign: List[Stop], actual_capacity, problem: ProblemSBRP):
        return [stop for stop in non_assign if ((stop.num_assigned_students + actual_capacity) <= problem.bus_capacity)]
