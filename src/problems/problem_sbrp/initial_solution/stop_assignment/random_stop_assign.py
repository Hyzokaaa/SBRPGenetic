from src.operators.initial_construction.initial_solution import InitialConstruction
from src.operators.operator_parameters import OperatorParameters
from src.problems.problem_sbrp.initial_solution.stop_assignment.restrictions.stop_assignment_restrictions import \
    StopAssignmentRestrictions
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP

import random


class RandomStopAssign(InitialConstruction):

    def generate(self, parameters: OperatorParameters):
        distance_operator = parameters.distance_operator
        problem: ProblemSBRP = parameters.problem
        # Para cada estudiante en la lista de estudiantes
        for student in problem.students:
            # Obtiene las paradas válidas
            valid_stops = StopAssignmentRestrictions.get_valid_stops(parameters=parameters, student=student)

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

