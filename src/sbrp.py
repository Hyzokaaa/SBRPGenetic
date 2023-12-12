import random

from src import utils
from src.bus import Bus
from src.route import Route
from src.school import School
from src.stop import Stop
from src.student import Student
from src.utils import Utils


class SBRP:
    def __init__(self, school, stops, students, routes, max_distance, bus_capacity, stop_cost, student_stop_cost):
        self.school = school
        self.stops = stops
        self.students = students
        self.routes = routes
        self.max_distance = max_distance
        self.bus_capacity = bus_capacity
        self.stop_cost_matrix = stop_cost
        self.student_stop_cost_matrix = student_stop_cost

    @staticmethod
    def read_instance(filename):
        with open(filename, 'r') as file:
            # Lee los parámetros del problema
            m, n, v, c, w = map(int, file.readline().split())

            # Lee las coordenadas del depósito
            depot_coord_x, depot_coord_y = map(float, file.readline().split())

            # Lee las coordenadas de las paradas
            stop_coordinates = [(float(coord_x), float(coord_y)) for coord_x, coord_y in
                                (file.readline().split() for _ in range(m))]

            # Lee las coordenadas de los estudiantes
            student_coordinates = [(float(coord_x), float(coord_y)) for coord_x, coord_y in
                                   (file.readline().split() for _ in range(n))]

            # Crea la escuela (depósito)
            school = School(id=0, name="School", coord_x=depot_coord_x, coord_y=depot_coord_y)

            # Crea las paradas
            stops = [Stop(id=i, name=f"Stop {i}", coord_x=coord_x, coord_y=coord_y) for i, (coord_x, coord_y) in
                     enumerate(stop_coordinates)]

            # Crea los estudiantes
            students = [Student(id=i, name=f"Student {i}", coord_x=coord_x, coord_y=coord_y) for
                        i, (coord_x, coord_y) in enumerate(student_coordinates)]

            # Crea los autobuses y las rutas
            buses = [Bus(id=i) for i in range(v)]
            routes = [Route(bus=bus) for bus in buses]

            # Crea la instancia de SBRP
            sbrp = SBRP(school=school, stops=stops, students=students, routes=routes, max_distance=w,
                        bus_capacity=c, stop_cost=None, student_stop_cost=None)

            return sbrp

    def student_to_stop(self):
        # Para cada estudiante en la lista de estudiantes
        for student in self.students:
            # Encuentra las paradas que están dentro de la distancia máxima y que no exceden la capacidad del autobús
            valid_stops = [stop for stop in self.stops if
                           self.student_stop_cost_matrix[student.id][stop.id] <= self.max_distance and
                           stop.num_assigned_students < self.bus_capacity]

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

    def student_to_random_stop(self):
        # Para cada estudiante en la lista de estudiantes
        for student in self.students:
            # Encuentra las paradas que están dentro de la distancia máxima y que no exceden la capacidad del autobús
            valid_stops = [stop for stop in self.stops if
                           self.student_stop_cost_matrix[student.id][stop.id] <= self.max_distance and
                           stop.num_assigned_students < self.bus_capacity]

            # Si no hay paradas válidas, entonces no asignamos ninguna parada a este estudiante
            if not valid_stops:
                student.assigned_stop = None
            else:
                # Selecciona una parada aleatoria entre las paradas válidas
                random_stop = random.choice(valid_stops)

                # Asigna al estudiante a la parada aleatoria
                student.assigned_stop = random_stop

                # Añade al estudiante a la lista de estudiantes asignados a esa parada
                random_stop.num_assigned_students += 1

    def student_to_stop_closest_to_school(self):
        # Busca las paradas que están dentro de la distancia máxima desde la escuela y no exceden la capacidad del bus
        valid_stops = [stop for stop in self.stops if
                       Utils.calculate_distance(self.school.coord_x, self.school.coord_y, stop.coord_x,
                                               stop.coord_y) <= self.max_distance and
                       stop.num_assigned_students < self.bus_capacity]

        # Si no hay paradas válidas, entonces no asignamos ninguna parada
        if not valid_stops:
            return None
        else:
            # Encuentra la parada más cercana entre las paradas válidas
            closest_stop = min(valid_stops,
                               key=lambda stop: Utils.calculate_distance(self.school.coord_x, self.school.coord_y,
                                                                        stop.coord_x, stop.coord_y))

            return closest_stop

    def student_to_stop_closest_to_centroid(self):
        centroid_x, centroid_y = self.calculate_centroid()

        # Encuentra las paradas que están dentro de la distancia máxima desde el centroide y que no exceden la capacidad del autobús
        valid_stops = [stop for stop in self.stops if
                       Utils.calculate_distance(centroid_x, centroid_y, stop.coord_x,
                                               stop.coord_y) <= self.max_distance and
                       stop.num_assigned_students < self.bus_capacity]

        # Si no hay paradas válidas, entonces no asignamos ninguna parada
        if not valid_stops:
            return None
        else:
            # Encuentra la parada más cercana entre las paradas válidas
            closest_stop = min(valid_stops,
                               key=lambda stop: Utils.calculate_distance(centroid_x, centroid_y, stop.coord_x,
                                                                        stop.coord_y))

            return closest_stop

    def calculate_centroid(self):
        sum_x = sum(stop.coord_x for stop in self.stops)
        sum_y = sum(stop.coord_y for stop in self.stops)
        centroid_x = sum_x / len(self.stops)
        centroid_y = sum_y / len(self.stops)
        return centroid_x, centroid_y

