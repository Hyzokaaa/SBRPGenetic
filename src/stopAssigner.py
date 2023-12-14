import random
import time

from src.stop import Stop
from src.utils import Utils


class StopAssigner:
    @staticmethod
    def get_valid_stops(self, student):
        # Encuentra las paradas que están dentro de la distancia máxima y que no exceden la capacidad del autobús
        valid_stops = [stop for stop in self.stops if
                       self.student_stop_cost_matrix[student.id][stop.id] <= self.max_distance and
                       stop.num_assigned_students < self.bus_capacity]
        return valid_stops

    @staticmethod
    def student_to_better_stop(self):
        # Para cada estudiante en la lista de estudiantes
        for student in self.students:
            # Obtiene las paradas válidas
            valid_stops = self.get_valid_stops(student)

            # Si no hay paradas válidas, entonces no asignamos ninguna parada a este estudiante
            if not valid_stops:
                student.assigned_stop = None
            else:
                # Encuentra la parada más cercana entre las paradas válidas
                closest_stop = min(valid_stops, key=lambda stop: self.student_stop_cost_matrix[student.id][stop.id])

                # Asigna al estudiante a la parada más cercana
                student.assigned_stop = closest_stop

                # Añade al estudiante a la lista de estudiantes asignados a esa parada
                closest_stop.num_assigned_students += 1

    @staticmethod
    def student_to_random_stop(self):
        random.seed(time.time())
        # Para cada estudiante en la lista de estudiantes
        for student in self.students:
            # Obtiene las paradas válidas
            valid_stops = self.get_valid_stops(student)

            # Si no hay paradas válidas, entonces no asignamos ninguna parada a este estudiante
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
    def student_to_stop_closest_to_school(self):
        # Para cada estudiante en la lista de estudiantes
        for student in self.students:
            # Obtiene las paradas válidas
            valid_stops = self.get_valid_stops(student)

            # Si no hay paradas válidas, entonces no asignamos ninguna parada
            if not valid_stops:
                student.assigned_stop = None
            else:
                # Encuentra la parada más cercana entre las paradas válidas
                closest_stop = min(valid_stops,
                                   key=lambda stop: Utils.calculate_distance(self.school.coord_x, self.school.coord_y,
                                                                             stop.coord_x, stop.coord_y))

                # Asigna al estudiante a la parada más cercana
                student.assigned_stop = closest_stop

                # Añade al estudiante a la lista de estudiantes asignados a esa parada
                closest_stop.num_assigned_students += 1

    @staticmethod
    def student_to_stop_closest_to_centroid(self):
        centroid_x, centroid_y = self.calculate_centroid()

        # Para cada estudiante en la lista de estudiantes
        for student in self.students:
            # Obtiene las paradas válidas
            valid_stops = self.get_valid_stops(student)
            # Si no hay paradas válidas, entonces no asignamos ninguna parada
            if not valid_stops:
                student.assigned_stop = None
            else:
                # Encuentra la parada más cercana al centroide entre las paradas válidas
                closest_stop = min(valid_stops,
                                   key=lambda stop: Utils.calculate_distance(centroid_x, centroid_y, stop.coord_x,
                                                                             stop.coord_y))

                # Asigna al estudiante a la parada más cercana al centroide
                student.assigned_stop = closest_stop

                # Añade al estudiante a la lista de estudiantes asignados a esa parada
                closest_stop.num_assigned_students += 1