import matplotlib.pyplot as plt
from typing import List

from src.bus import Bus
from src.route import Route
from src.school import School
from src.stop import Stop
from src.student import Student
from src.utils import Utils


class SBRP:
    def __init__(self, school: School, stops: List[Stop] = None, students: List[Student] = None,
                 routes: List[Route] = None, max_distance=0, bus_capacity=0):
        self.school = school
        self.stops = stops
        self.students = students
        self.routes = routes
        self.max_distance = max_distance
        self.bus_capacity = bus_capacity
        self.stop_cost_matrix = 0
        self.student_stop_cost_matrix = Utils.calculate_cost_matrix(self.students, self.stops)

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
                        bus_capacity=c)

            return sbrp
