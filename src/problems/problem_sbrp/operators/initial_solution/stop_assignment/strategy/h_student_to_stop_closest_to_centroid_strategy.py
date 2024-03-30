from typing import List

from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.restrictions.stop_assignment_restrictions \
    import \
    StopAssignmentRestrictions
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.strategy.stop_assign_strategy \
    import StopAssignStrategy
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


def calculate_centroid(stops: List[Stop]):
    sum_x = sum(stop.coordinates[0] for stop in stops)
    sum_y = sum(stop.coordinates[1] for stop in stops)
    centroid_x = sum_x / len(stops)
    centroid_y = sum_y / len(stops)
    return [centroid_x, centroid_y]


class HStudentToStopClosestToCentroidStrategy(StopAssignStrategy):
    def generate_stop_assign(self, problem: ProblemSBRP, distance_operator: DistanceOperator):
        centroid = calculate_centroid(problem.stops)

        # Para cada estudiante en la lista de estudiantes
        for student in problem.students:
            # Obtiene las paradas válidas
            valid_stops = StopAssignmentRestrictions.get_valid_stops(problem=problem,
                                                                     distance_operator=distance_operator,
                                                                     student=student)
            # Si no hay paradas válidas, entonces no se asigna ninguna parada
            if not valid_stops:
                student.assigned_stop = None
            else:
                # Encuentra la parada más cercana al centroide entre las paradas válidas
                closest_stop = min(valid_stops,
                                   key=lambda stop: distance_operator.calculate_distance(centroid,
                                                                                         stop.coordinates))

                # Asigna al estudiante a la parada más cercana al centroide
                student.assigned_stop = closest_stop

                # Añade al estudiante a la lista de estudiantes asignados a esa parada
                closest_stop.num_assigned_students += 1

