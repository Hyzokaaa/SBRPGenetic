import logging
from collections import defaultdict, deque
from typing import Dict, List

from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.model.student import Student
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_assignment_sbrp import SolutionAssignmentSBRP


class StopAssignmentRebalancer:
    """
    Completa la asignación de los estudiantes que quedaron sin parada mediante caminos de aumento:
    si las paradas alcanzables por un estudiante están llenas, reasigna en cadena a otros estudiantes
    hacia paradas alcanzables con capacidad. Encuentra una asignación siempre que exista.
    """

    @staticmethod
    def rebalance_unassigned(problem: ProblemSBRP, unassigned: List[Student], distance_operator: DistanceOperator):
        logging.info(f"REBALANCEO: {len(unassigned)} estudiantes pendientes")
        if not unassigned:
            return
        reachable = _ReachableStops(problem, distance_operator)
        students_by_stop = defaultdict(list)
        for student in problem.students:
            if student.assigned_stop is not None:
                students_by_stop[student.assigned_stop.id].append(student)

        for student in unassigned:
            if not StopAssignmentRebalancer._augment(problem, student, reachable, students_by_stop):
                error_msg = f"CRÍTICO: Estudiante {student.id} no pudo ser asignado"
                logging.error(error_msg)
                raise ValueError(error_msg)
            logging.info(f"REBALANCEO: Estudiante {student.id} -> Parada {student.assigned_stop.id}")

    @staticmethod
    def sync_and_validate(problem: ProblemSBRP, solution: SolutionAssignmentSBRP):
        solution.assignments = [(s, s.assigned_stop) for s in problem.students]
        unassigned = [s for s in problem.students if s.assigned_stop is None]
        if unassigned:
            error_msg = f"VALIDACIÓN FALLIDA: {len(unassigned)} estudiantes sin asignar"
            logging.error(error_msg)
            raise RuntimeError(error_msg)
        logging.info("VALIDACIÓN EXITOSA: Todos los estudiantes asignados")

    @staticmethod
    def _augment(problem: ProblemSBRP, student: Student, reachable, students_by_stop) -> bool:
        """
        Busca (en anchura) el camino de aumento más corto desde el estudiante hasta una parada con capacidad
        y aplica las reasignaciones en cadena a lo largo del camino.
        """
        # parent[parada] = (estudiante que se mueve a la parada, parada de la que proviene o None)
        parent = {}
        queue = deque()
        for stop in reachable[student.id]:
            if stop.id not in parent:
                parent[stop.id] = (student, None)
                queue.append(stop)

        while queue:
            stop = queue.popleft()
            if stop.num_assigned_students < problem.bus_capacity:
                StopAssignmentRebalancer._apply_path(stop, parent, students_by_stop)
                return True
            for other in students_by_stop[stop.id]:
                for next_stop in reachable[other.id]:
                    if next_stop.id not in parent:
                        parent[next_stop.id] = (other, stop)
                        queue.append(next_stop)
        return False

    @staticmethod
    def _apply_path(free_stop: Stop, parent, students_by_stop):
        stop = free_stop
        stop.num_assigned_students += 1
        while True:
            moved, previous_stop = parent[stop.id]
            students_by_stop[stop.id].append(moved)
            moved.assigned_stop = stop
            if previous_stop is None:
                return
            students_by_stop[previous_stop.id].remove(moved)
            stop = previous_stop


class _ReachableStops:
    """
    Paradas alcanzables por cada estudiante (ordenadas de la más cercana a la más lejana),
    calculadas solo para los estudiantes que intervienen en el rebalanceo.
    """

    def __init__(self, problem: ProblemSBRP, distance_operator: DistanceOperator):
        self.problem = problem
        self.distance_operator = distance_operator
        self.students = {student.id: student for student in problem.students}
        self.cache: Dict[int, List[Stop]] = {}

    def __getitem__(self, student_id: int) -> List[Stop]:
        if student_id not in self.cache:
            student = self.students[student_id]
            distances = [(self.distance_operator.calculate_distance(student.coordinates, stop.coordinates), stop)
                         for stop in self.problem.stops]
            self.cache[student_id] = [stop for distance, stop in sorted(distances, key=lambda d: d[0])
                                      if distance <= self.problem.w_distance]
        return self.cache[student_id]
