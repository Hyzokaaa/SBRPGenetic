from src.operators.initial_construction.initial_solution import InitialConstruction
from src.operators.operator_parameters import OperatorParameters
from src.problems.problem_sbrp.initial_solution.stop_assignment.restrictions.stop_assignment_restrictions import \
    StopAssignmentRestrictions
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class HStudentToStopClosestToSchoolStopAssign(InitialConstruction):

    def generate(self, parameters: OperatorParameters):
        problem: ProblemSBRP = parameters.problem
        distance_operator = parameters.distance_operator

        # Para cada estudiante en la lista de estudiantes
        for student in problem.students:
            # Obtiene las paradas válidas
            valid_stops = StopAssignmentRestrictions.get_valid_stops(parameters=parameters, student=student)

            # Si no hay paradas válidas, entonces no se asigna ninguna parada
            if not valid_stops:
                student.assigned_stop = None
            else:
                # Encuentra la parada más cercana entre las paradas válidas
                closest_stop = min(valid_stops,
                                   key=lambda stop: distance_operator.calculate_distance(problem.school.coordinates,
                                                                                         stop.coordinates))

                # Asigna al estudiante a la parada más cercana
                student.assigned_stop = closest_stop

                # Añade al estudiante a la lista de estudiantes asignados a esa parada
                closest_stop.num_assigned_students += 1

