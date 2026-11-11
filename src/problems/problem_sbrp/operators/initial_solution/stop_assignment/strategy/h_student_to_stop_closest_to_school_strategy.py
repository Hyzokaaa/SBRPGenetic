import logging
from typing import List

from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.model.student import Student
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.restrictions.stop_assignment_restrictions import \
    StopAssignmentRestrictions
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_assignment_sbrp import SolutionAssignmentSBRP
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.rebalance.stop_assignment_rebalancer import StopAssignmentRebalancer


class HStudentToStopClosestToSchoolStrategy:
    def generate_stop_assign(self, problem: ProblemSBRP, distance_operator: DistanceOperator) -> SolutionAssignmentSBRP:
        """
        Asigna estudiantes a paradas cumpliendo restricciones duras.
        """
        logging.info("=== INICIO DE ASIGNACIÓN DE PARADAS ===")
        solution = SolutionAssignmentSBRP()
        unassigned_students = []

        # --- Fase 1: Asignación inicial ---
        for student in problem.students:
            valid_stops = StopAssignmentRestrictions.get_valid_stops(problem, distance_operator, student)

            if valid_stops:
                closest_stop = self._find_closest_stop(problem, valid_stops, distance_operator)
                self._assign_student(student, closest_stop, solution)
            else:
                self._track_unassigned(student, unassigned_students, solution)

        # --- Fase 2: Rebalanceo inteligente ---
        StopAssignmentRebalancer.rebalance_unassigned(problem, unassigned_students, distance_operator)

        # --- Fase 3: Sincronización final ---
        StopAssignmentRebalancer.sync_and_validate(problem, solution)

        return solution

    # ------------------------- Métodos auxiliares -------------------------
    def _find_closest_stop(self, problem: ProblemSBRP, valid_stops: List[Stop],
                           distance_operator: DistanceOperator) -> Stop:
        """Encuentra la parada válida más cercana a la escuela."""
        return min(
            valid_stops,
            key=lambda s: distance_operator.calculate_distance(problem.school.coordinates, s.coordinates)
        )

    def _assign_student(self, student: Student, stop: Stop, solution: SolutionAssignmentSBRP):
        """Realiza asignación y registra en log."""
        student.assigned_stop = stop
        stop.num_assigned_students += 1
        solution.assignments.append((student, stop))
        logging.info(f"ASIGNACIÓN: Estudiante {student.id} -> Parada {stop.id}")

    def _track_unassigned(self, student: Student, unassigned: list, solution: SolutionAssignmentSBRP):
        """Registra estudiantes no asignados inicialmente."""
        unassigned.append(student)
        solution.assignments.append((student, None))
        logging.warning(f"FALLO INICIAL: Estudiante {student.id} sin asignación")
