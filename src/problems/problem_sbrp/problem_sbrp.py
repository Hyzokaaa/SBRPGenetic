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
        self.assign_solution = None
        self.best_solution = None

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
            for route in solution.get_representation():
                for i in range(len(route.stops) - 1):
                    stop1 = route.stops[i]
                    stop2 = route.stops[i + 1]
                    location1 = stop1.coordinates
                    location2 = stop2.coordinates
                    fitness += self.distance_calculator.calculate_distance(location1, location2)
            return fitness
        else:
            return None

    def compare_solutions(self, solution1, solution2, objective_max):
        best_solution = solution1
        if best_solution is None or (
                objective_max and self.objective_function(solution2) >
                self.objective_function(best_solution)
        ) or (
                not objective_max and self.objective_function(solution2) <
                self.objective_function(best_solution)
        ):
            best_solution = solution2
        return best_solution

    def update_best_solution(self, best_iteration, current_iteration, objective_max, population):
        for new_solution in population:
            updated_solution = self.compare_solutions(solution1=self.best_solution, solution2=new_solution,
                                                      objective_max=objective_max)

            if updated_solution != self.best_solution:
                best_iteration = current_iteration
                self.best_solution = updated_solution
        return best_iteration

    def __str__(self):
        return 'ProblemSBRP'
