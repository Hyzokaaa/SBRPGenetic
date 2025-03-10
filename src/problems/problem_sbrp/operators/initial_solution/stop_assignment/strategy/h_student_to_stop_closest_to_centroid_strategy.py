import logging
from typing import List

from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_assignment_sbrp import SolutionAssignmentSBRP


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
                logging.info(f"ASIGNACIÓN: Estudiante {student.id} -> Parada {closest_stop.id}")
            else:
                unassigned_students.append(student)
                logging.warning(f"FALLO INICIAL: Estudiante {student.id} sin asignación")

            solution.assignments.append((student, student.assigned_stop))

        # --- Fase 2: Rebalanceo (usar mismo método que en HStudentToClosestStopStrategy) ---
        self._rebalance_unassigned(problem, unassigned_students, distance_operator, solution)

        # --- Sincronización y validación ---
        self._sync_and_validate(problem, solution)
        return solution

    def _calculate_centroid(self, stops: List[Stop]):
        sum_x = sum(stop.coordinates[0] for stop in stops)
        sum_y = sum(stop.coordinates[1] for stop in stops)
        return [sum_x / len(stops), sum_y / len(stops)]

    def _rebalance_unassigned(self, problem, unassigned, distance_operator, solution):
        logging.info(f"REBALANCEO: {len(unassigned)} estudiantes pendientes")
        for student in unassigned.copy():
            success = False
            candidate_stops = [
                stop for stop in problem.stops
                if distance_operator.calculate_distance(student.coordinates, stop.coordinates) <= problem.w_distance
            ]

            for stop in candidate_stops:
                for other_student in problem.students:
                    if other_student.assigned_stop == stop:
                        valid_new_stops = [
                            s for s in problem.stops
                            if s != stop and s.num_assigned_students < problem.bus_capacity
                               and distance_operator.calculate_distance(other_student.coordinates,
                                                                        s.coordinates) <= problem.w_distance
                        ]
                        if valid_new_stops:
                            new_stop = min(valid_new_stops, key=lambda s: distance_operator.calculate_distance(
                                other_student.coordinates, s.coordinates))

                            # Reasignar
                            other_student.assigned_stop = new_stop
                            stop.num_assigned_students -= 1
                            new_stop.num_assigned_students += 1

                            student.assigned_stop = stop
                            stop.num_assigned_students += 1

                            solution.assignments = [(s, s.assigned_stop) for s in problem.students]
                            logging.info(f"REBALANCEO: Estudiante {student.id} -> Parada {stop.id}")
                            success = True
                            break
                if success:
                    break
            if not success:
                raise ValueError(f"CRÍTICO: Estudiante {student.id} no asignado")

    def _sync_and_validate(self, problem, solution):
        solution.assignments = [(s, s.assigned_stop) for s in problem.students]
        unassigned = [s for s in problem.students if s.assigned_stop is None]
        if unassigned:
            logging.error(f"ESTUDIANTES SIN ASIGNAR: {len(unassigned)}")
            raise RuntimeError("Validación fallida")
        logging.info("VALIDACIÓN EXITOSA")