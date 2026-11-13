import logging

from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.rebalance.stop_assignment_rebalancer import \
    StopAssignmentRebalancer
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_assignment_sbrp import SolutionAssignmentSBRP

logger = logging.getLogger(__name__)


class HStudentToFewestStopsStrategy:
    """
    Asigna a los estudiantes usando el menor número de paradas posible (recubrimiento voraz con capacidad): en cada
    paso abre la parada que puede recibir a más estudiantes sin asignar que la alcanzan (como máximo la capacidad de
    un bus) y, a igualdad, la más cercana a la escuela. Si a la parada la alcanzan más estudiantes de los que caben,
    entran primero los que tienen menos paradas alternativas. Cuantas menos paradas, menos desvíos deben hacer las rutas.

    school_weight pondera la cercanía a la escuela frente al número de estudiantes cubiertos:
    puntuación = cubiertos / (1 + school_weight · distancia a la escuela / distancia máxima). Con 0 solo cuenta
    el número de estudiantes cubiertos.
    """

    def __init__(self, school_weight: float = 0.0):
        if school_weight < 0:
            raise ValueError("school_weight no puede ser negativo")
        self.school_weight = school_weight

    def generate_stop_assign(self, problem: ProblemSBRP, distance_operator: DistanceOperator) -> SolutionAssignmentSBRP:
        solution = SolutionAssignmentSBRP()
        capacity = problem.bus_capacity

        # Paradas alcanzables por cada estudiante y estudiantes que alcanzan cada parada
        reachable = {student.id: [stop for stop in problem.stops
                                  if distance_operator.calculate_distance(student.coordinates, stop.coordinates)
                                  <= problem.w_distance]
                     for student in problem.students}
        reached_by = {stop.id: [] for stop in problem.stops}
        for student in problem.students:
            for stop in reachable[student.id]:
                reached_by[stop.id].append(student)
        to_school = {stop.id: distance_operator.calculate_distance(stop.coordinates, problem.school.coordinates)
                     for stop in problem.stops}
        farthest = max(to_school.values(), default=0) or 1

        unassigned = {student.id for student in problem.students}
        opened = set()
        while unassigned:
            best = None
            for stop in problem.stops:
                if stop.id in opened:
                    continue
                covered = min(capacity, sum(1 for student in reached_by[stop.id] if student.id in unassigned))
                if covered == 0:
                    continue
                score = covered / (1 + self.school_weight * to_school[stop.id] / farthest)
                key = (score, -to_school[stop.id], -stop.id)
                if best is None or key > best[0]:
                    best = (key, stop)
            if best is None:
                break
            stop = best[1]
            opened.add(stop.id)

            # Entran primero los estudiantes con menos paradas alternativas aún sin abrir
            candidates = sorted((student for student in reached_by[stop.id] if student.id in unassigned),
                                key=lambda student: (sum(1 for s in reachable[student.id] if s.id not in opened),
                                                     student.id))
            for student in candidates[:capacity]:
                student.assigned_stop = stop
                stop.num_assigned_students += 1
                unassigned.discard(student.id)
                logger.debug("Estudiante %s asignado a la parada %s", student.id, stop.id)

        # Los que no tienen parada abierta con sitio se resuelven con caminos de aumento
        pending = [student for student in problem.students if student.id in unassigned]
        StopAssignmentRebalancer.rebalance_unassigned(problem, pending, distance_operator)
        StopAssignmentRebalancer.sync_and_validate(problem, solution)
        logger.debug("Asignación con %d paradas", sum(1 for stop in problem.stops if stop.num_assigned_students))
        return solution
