import logging
from typing import List

from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_assignment_sbrp import SolutionAssignmentSBRP
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.rebalance.stop_assignment_rebalancer import StopAssignmentRebalancer

logger = logging.getLogger(__name__)


class HStudentToStopClosestToCentroidStrategy:
    def generate_stop_assign(self, problem: ProblemSBRP, distance_operator: DistanceOperator) -> SolutionAssignmentSBRP:
        solution = SolutionAssignmentSBRP()
        unassigned_students = []
        centroid = self._calculate_centroid(problem.stops)

        # --- Fase 1: Asignación inicial ---
        for student in problem.students:
            valid_stops = [
                stop for stop in problem.stops
                if (distance_operator.calculate_distance(student.coordinates, stop.coordinates) <= problem.w_distance
                    and stop.num_assigned_students < problem.bus_capacity)
            ]

            if valid_stops:
                closest_stop = min(valid_stops, key=lambda s: distance_operator.calculate_distance(
                    centroid, s.coordinates))
                student.assigned_stop = closest_stop
                closest_stop.num_assigned_students += 1
                logger.debug("Estudiante %s asignado a la parada %s", student.id, closest_stop.id)
            else:
                unassigned_students.append(student)
                logger.debug("Estudiante %s sin parada libre en la primera pasada", student.id)

            solution.assignments.append((student, student.assigned_stop))

        # --- Fase 2: Rebalanceo (usar mismo método que en HStudentToClosestStopStrategy) ---
        StopAssignmentRebalancer.rebalance_unassigned(problem, unassigned_students, distance_operator)

        # --- Sincronización y validación ---
        StopAssignmentRebalancer.sync_and_validate(problem, solution)
        return solution

    def _calculate_centroid(self, stops: List[Stop]):
        sum_x = sum(stop.coordinates[0] for stop in stops)
        sum_y = sum(stop.coordinates[1] for stop in stops)
        return [sum_x / len(stops), sum_y / len(stops)]
