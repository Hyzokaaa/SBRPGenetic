from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.restrictions.stop_assignment_restrictions \
    import StopAssignmentRestrictions
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.strategy.stop_assign_strategy \
    import StopAssignStrategy
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP

import random

from src.problems.problem_sbrp.solution_assignment_sbrp import SolutionAssignmentSBRP


class StudentToRandomStopStrategy(StopAssignStrategy):

    def generate_stop_assign(self, problem: ProblemSBRP, distance_operator: DistanceOperator):
        # Crea una nueva solución
        solution = SolutionAssignmentSBRP()

        # Para cada estudiante en la lista de estudiantes
        for student in problem.students:
            # Obtiene las paradas válidas
            valid_stops = StopAssignmentRestrictions.get_valid_stops(problem=problem,
                                                                     distance_operator=distance_operator,
                                                                     student=student)

            # Si no hay paradas válidas, entonces no se asigna parada a este estudiante
            if not valid_stops:
                student.assigned_stop = None
            else:
                # Selecciona una parada aleatoria entre las paradas válidas
                random_stop: Stop = random.choice(valid_stops)
                # Asigna al estudiante a la parada aleatoria
                student.assigned_stop = random_stop

                # Añade al estudiante a la lista de estudiantes asignados a esa parada
                random_stop.num_assigned_students += 1

            # Añade la asignación del estudiante a la solución
            solution.assignments.append((student, student.assigned_stop))

        return solution
