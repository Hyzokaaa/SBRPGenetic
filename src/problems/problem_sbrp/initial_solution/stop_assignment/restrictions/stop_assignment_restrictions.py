from src.operators.operator_parameters import OperatorParameters
from src.problems.problem_sbrp.model.student import Student
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class StopAssignmentRestrictions:
    @staticmethod
    def get_valid_stops(parameters: OperatorParameters, student: Student):
        problem: ProblemSBRP = parameters.problem
        distance_operator = parameters.distance_operator
        # Encuentra las paradas que están dentro de la distancia máxima y que no exceden la capacidad del autobús
        valid_stops = [stop for stop in problem.stops if
                       distance_operator.calculate_distance(stop.coordinates, student.coordinates) <= problem.w_distance
                       and stop.num_assigned_students < problem.bus_capacity]
        return valid_stops
