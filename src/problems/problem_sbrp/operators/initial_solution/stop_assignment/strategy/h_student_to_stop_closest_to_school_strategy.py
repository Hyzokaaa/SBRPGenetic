import logging
from typing import List

from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.model.student import Student
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.restrictions.stop_assignment_restrictions import \
    StopAssignmentRestrictions
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_assignment_sbrp import SolutionAssignmentSBRP


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
        self._rebalance_unassigned(problem, unassigned_students, distance_operator, solution)

        # --- Fase 3: Sincronización final ---
        self._sync_solution_with_problem(problem, solution)
        self._validate_final_assignments(problem)

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

    def _rebalance_unassigned(self, problem: ProblemSBRP, unassigned: List[Student],
                              distance_operator: DistanceOperator, solution: SolutionAssignmentSBRP):
        """Reasigna estudiantes no asignados modificando la solución."""
        logging.info(f"INICIANDO REBALANCEO: {len(unassigned)} estudiantes pendientes")

        for student in unassigned.copy():
            success = self._rebalance_student(problem, student, distance_operator, solution)
            if not success:
                self._handle_rebalance_failure(student)

    def _rebalance_student(self, problem: ProblemSBRP, student: Student,
                           distance_operator: DistanceOperator, solution: SolutionAssignmentSBRP) -> bool:
        """Intenta reasignar un estudiante mediante rebalanceo."""
        candidate_stops = self._get_candidate_stops(problem, student, distance_operator)

        for stop in candidate_stops:
            if self._try_liberate_space(problem, student, stop, distance_operator, solution):
                return True
        return False

    def _get_candidate_stops(self, problem: ProblemSBRP, student: Student,
                             distance_operator: DistanceOperator) -> List[Stop]:
        """Obtiene paradas candidatas para rebalanceo."""
        return [
            stop for stop in problem.stops
            if distance_operator.calculate_distance(student.coordinates, stop.coordinates) <= problem.w_distance
        ]

    def _try_liberate_space(self, problem: ProblemSBRP, student: Student, stop: Stop,
                            distance_operator: DistanceOperator, solution: SolutionAssignmentSBRP) -> bool:
        """Intenta liberar espacio en una parada reasignando otro estudiante."""
        for other_student in problem.students:
            if other_student.assigned_stop == stop:
                new_stop = self._find_replacement_stop(problem, other_student, stop, distance_operator)
                if new_stop:
                    self._execute_reassignment(problem, student, other_student, stop, new_stop, solution)
                    return True
        return False

    def _find_replacement_stop(self, problem: ProblemSBRP, student: Student,
                               original_stop: Stop, distance_operator: DistanceOperator) -> Stop:
        """Busca parada alternativa para un estudiante."""
        valid_stops = [
            stop for stop in problem.stops
            if (stop != original_stop
                and distance_operator.calculate_distance(student.coordinates, stop.coordinates) <= problem.w_distance
                and stop.num_assigned_students < problem.bus_capacity)
        ]
        return min(valid_stops, key=lambda s: distance_operator.calculate_distance(
            student.coordinates, s.coordinates)) if valid_stops else None

    def _execute_reassignment(self, problem: ProblemSBRP, target_student: Student,
                              moved_student: Student, old_stop: Stop, new_stop: Stop,
                              solution: SolutionAssignmentSBRP):
        """Ejecuta la reasignación y actualiza todas las estructuras."""
        # Actualizar estudiante movido
        moved_student.assigned_stop = new_stop
        old_stop.num_assigned_students -= 1
        new_stop.num_assigned_students += 1

        # Actualizar estudiante objetivo
        target_student.assigned_stop = old_stop
        old_stop.num_assigned_students += 1

        # Actualizar solución
        self._update_solution_assignments(solution, moved_student, new_stop)
        self._update_solution_assignments(solution, target_student, old_stop)

        logging.info(f"REBALANCEO EXITOSO: "
                     f"Estudiante {target_student.id} -> Parada {old_stop.id} "
                     f"(vía Est. {moved_student.id}: {old_stop.id}->{new_stop.id})")

    def _update_solution_assignments(self, solution: SolutionAssignmentSBRP, student: Student, new_stop: Stop):
        """Actualiza asignaciones en la solución."""
        # Eliminar entrada antigua
        solution.assignments = [(s, stop) for (s, stop) in solution.assignments if s.id != student.id]
        # Agregar nueva entrada
        solution.assignments.append((student, new_stop))

    def _handle_rebalance_failure(self, student: Student):
        """Maneja errores críticos de rebalanceo."""
        error_msg = f"CRÍTICO: Estudiante {student.id} no pudo ser asignado"
        logging.error(error_msg)
        raise ValueError(error_msg)

    def _sync_solution_with_problem(self, problem: ProblemSBRP, solution: SolutionAssignmentSBRP):
        """Garantiza coherencia entre problem.students y solution.assignments."""
        solution.assignments = [(s, s.assigned_stop) for s in problem.students]

    def _validate_final_assignments(self, problem: ProblemSBRP):
        """Valida que todos los estudiantes tengan asignación."""
        unassigned = [s for s in problem.students if s.assigned_stop is None]
        if unassigned:
            error_msg = f"VALIDACIÓN FALLIDA: {len(unassigned)} estudiantes sin asignar"
            logging.error(error_msg)
            raise RuntimeError(error_msg)
        logging.info("VALIDACIÓN EXITOSA: Todos los estudiantes asignados")