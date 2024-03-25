from typing import List

from src.problems.problem import Problem
from src.problems.problem_parameters import ProblemParameters
from src.problems.problem_sbrp.model.bus import Bus
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.model.student import Student


class ProblemSBRP(Problem):
    def __init__(self):
        self.distance_calculator = None
        self.school: School = None
        self.stops: List[Stop] = None
        self.students: List[Student] = None
        self.vehicles: List[Bus] = None
        self.bus_capacity = None
        self.w_distance = None

    def construct(self, problem_parameters: ProblemParameters):
        self.distance_calculator = problem_parameters.distance_operator
        self.school = School(id=0, name='School', coordinates=problem_parameters.sbrp_school_coordinates)
        self.    stops = [Stop(id=i + 1, name=f"Stop {i + 1}", coordinates=coordinates)
                          for i, (coordinates) in enumerate(problem_parameters.sbrp_stops_coordinates)]
        self.students = [Student(id=i, name=f"Student {i}", coordinates=coordinates)
                         for i, (coordinates) in enumerate(problem_parameters.sbrp_student_coordinates)]
        self.vehicles = [Bus(id=i, name=f"Bus{i}")for i in range(problem_parameters.sbrp_vehicles)]
        self.bus_capacity = problem_parameters.sbrp_bus_capacity
        self.w_distance = problem_parameters.sbrp_walk_distance

    def objective_function(self, solution):
        fitness = 0
        if solution:
            for route in solution:
                for i in range(len(route.stops) - 1):
                    stop1 = route.stops[i]
                    stop2 = route.stops[i + 1]
                    location1 = stop1.coordintates
                    location2 = stop2.coordintates
                    fitness += self.distance_calculator.calculate_distance(location1, location2)
            return fitness
        else:
            return None

    def initial_random_solution(self):
        pass

    def initial_heuristic_solution(self):
        pass
