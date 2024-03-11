from src.operators.distance.distance import EuclideanDistance
from src.problems.problem_father import ProblemFather


class ProblemSBRP(ProblemFather):
    def __init__(self):
        self.distance_calculator = EuclideanDistance()

    def objective_function(self, solution):
        total_cost = 0
        if solution:
            for route in solution:
                for i in range(len(route.stops) - 1):
                    stop1 = route.stops[i]
                    stop2 = route.stops[i + 1]
                    location1 = (stop1.coord_x, stop1.coord_y)
                    location2 = (stop2.coord_x, stop2.coord_y)
                    total_cost += self.distance_calculator.calculate_distance(location1, location2)
            fitness = total_cost
            return fitness
        else:
            return None
