import random
import time

from shared.domain.sbrp import SBRP
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.model.student import Student
from shared.utils.utils import Utils


class StudentStopAssigner:
    @staticmethod
    def get_valid_stops(sbrp: SBRP, student: Student):
        # Encuentra las paradas que están dentro de la distancia máxima y que no exceden la capacidad del autobús
        valid_stops = [stop for stop in sbrp.stops if
                       sbrp.student_stop_cost_matrix[sbrp.id_to_index_students[student.id]][
                           sbrp.id_to_index_stops[stop.id]] <= sbrp.max_distance and
                       stop.num_assigned_students < sbrp.bus_capacity]
        return valid_stops

    @staticmethod
    def student_to_better_stop(sbrp: SBRP):
        # Para cada estudiante en la lista de estudiantes
        for student in sbrp.students:
            # Obtiene las paradas válidas
            valid_stops = StudentStopAssigner.get_valid_stops(sbrp, student)

            # Si no hay paradas válidas, entonces no se asigna parada a este estudiante
            if not valid_stops:
                student.assigned_stop = None
            else:
                # Encuentra la parada más cercana entre las paradas válidas
                closest_stop = min(valid_stops,
                                   key=lambda stop:
                                   sbrp.student_stop_cost_matrix[sbrp.id_to_index_students[student.id]][
                                       sbrp.id_to_index_stops[stop.id]])

                # Asigna al estudiante a la parada más cercana
                student.assigned_stop = closest_stop

                # Añade al estudiante a la lista de estudiantes asignados a esa parada
                closest_stop.num_assigned_students += 1

    @staticmethod
    def student_to_random_stop(sbrp: SBRP):
        random.seed(time.time())
        # Para cada estudiante en la lista de estudiantes
        for student in sbrp.students:
            # Obtiene las paradas válidas
            valid_stops = StudentStopAssigner.get_valid_stops(sbrp, student)

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

    @staticmethod
    def student_to_stop_closest_to_school(sbrp: SBRP):
        # Para cada estudiante en la lista de estudiantes
        for student in sbrp.students:
            # Obtiene las paradas válidas
            valid_stops = StudentStopAssigner.get_valid_stops(sbrp, student)

            # Si no hay paradas válidas, entonces no se asigna ninguna parada
            if not valid_stops:
                student.assigned_stop = None
            else:
                # Encuentra la parada más cercana entre las paradas válidas
                closest_stop = min(valid_stops,
                                   key=lambda stop: Utils.calculate_distance_euclidian(sbrp.school.coord_x, sbrp.school.coord_y,
                                                                                       stop.coord_x, stop.coord_y))

                # Asigna al estudiante a la parada más cercana
                student.assigned_stop = closest_stop

                # Añade al estudiante a la lista de estudiantes asignados a esa parada
                closest_stop.num_assigned_students += 1

    @staticmethod
    def student_to_stop_closest_to_centroid(sbrp: SBRP):
        centroid_x, centroid_y = Utils.calculate_centroid(sbrp.stops)

        # Para cada estudiante en la lista de estudiantes
        for student in sbrp.students:
            # Obtiene las paradas válidas
            valid_stops = StudentStopAssigner.get_valid_stops(sbrp, student)
            # Si no hay paradas válidas, entonces no se asigna ninguna parada
            if not valid_stops:
                student.assigned_stop = None
            else:
                # Encuentra la parada más cercana al centroide entre las paradas válidas
                closest_stop = min(valid_stops,
                                   key=lambda stop: Utils.calculate_distance_euclidian(centroid_x, centroid_y, stop.coord_x,
                                                                                       stop.coord_y))

                # Asigna al estudiante a la parada más cercana al centroide
                student.assigned_stop = closest_stop

                # Añade al estudiante a la lista de estudiantes asignados a esa parada
                closest_stop.num_assigned_students += 1
