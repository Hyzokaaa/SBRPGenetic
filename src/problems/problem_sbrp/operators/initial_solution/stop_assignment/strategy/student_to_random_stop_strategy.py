import logging

from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_assignment_sbrp import SolutionAssignmentSBRP
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.rebalance.stop_assignment_rebalancer import StopAssignmentRebalancer
import random

logger = logging.getLogger(__name__)


class StudentToRandomStopStrategy:
    def generate_stop_assign(self, problem: ProblemSBRP, distance_operator: DistanceOperator) -> SolutionAssignmentSBRP:
        solution = SolutionAssignmentSBRP()
        unassigned_students = []

        # --- Fase 1: Asignación inicial ---
        for student in problem.students:
            valid_stops = [
                stop for stop in problem.stops
                if (distance_operator.calculate_distance(student.coordinates, stop.coordinates) <= problem.w_distance
                    and stop.num_assigned_students < problem.bus_capacity)
            ]

            if valid_stops:
                random_stop = random.choice(valid_stops)
                student.assigned_stop = random_stop
                random_stop.num_assigned_students += 1
                logger.debug("Estudiante %s asignado a la parada %s", student.id, random_stop.id)
            else:
                unassigned_students.append(student)
                logger.debug("Estudiante %s sin parada libre en la primera pasada", student.id)

            solution.assignments.append((student, student.assigned_stop))

        # --- Fase 2: Rebalanceo (usar mismo método que en HStudentToClosestStopStrategy) ---
        StopAssignmentRebalancer.rebalance_unassigned(problem, unassigned_students, distance_operator)

        # --- Sincronización y validación ---
        StopAssignmentRebalancer.sync_and_validate(problem, solution)
        return solution
