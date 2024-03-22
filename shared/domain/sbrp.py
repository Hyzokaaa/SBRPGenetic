import random
from typing import List

from src.problems.problem_sbrp.model.bus import Bus
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.model.student import Student
from shared.utils.utils import Utils


class SBRP:
    def __init__(self, school: School, stops: List[Stop] = None, students: List[Student] = None,
                 routes: List[Route] = None, max_distance=0, bus_capacity=0, buses: List[Bus] = None,
                 random_shuffle=True):
        self.school = school
        self.stops = stops
        self.stops.insert(0, school)
        self.students = students
        if random_shuffle:
            random.shuffle(self.students)
        self.id_to_index_students = {student.id: i for i, student in enumerate(students)}
        self.id_to_index_stops = {stop.id: i for i, stop in enumerate(stops)}
        self.routes = routes
        self.max_distance = max_distance
        self.bus_capacity = bus_capacity
        self.stop_cost_matrix = Utils.calculate_cost_matrix(self, self.stops, self.stops)
        self.student_stop_cost_matrix = Utils.calculate_cost_matrix(self, self.students, self.stops)
        self.stops.remove(school)
        self.buses = buses

    def update_index(self):
        self.id_to_index_students = {student.id: i for i, student in enumerate(self.students)}
        self.id_to_index_stops = {self.school.id: 0}
        self.id_to_index_stops.update({stop.id: i + 1 for i, stop in enumerate(self.stops)})

    @staticmethod
    def read_instance(file_path):
        with open(file_path, 'r') as file:
            # Lee los parámetros del problema
            m, n, v, c, w = map(int, file.readline().split())

            # Lee las coordenadas de la escuela
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
            stops = [Stop(id=i + 1, name=f"Stop {i + 1}", coord_x=coord_x, coord_y=coord_y) for i, (coord_x, coord_y) in
                     enumerate(stop_coordinates)]

            # Crea los estudiantes
            students = [Student(id=i, name=f"Student {i}", coord_x=coord_x, coord_y=coord_y) for
                        i, (coord_x, coord_y) in enumerate(student_coordinates)]

            # Crea los autobuses y las rutas
            buses = [Bus(id=i) for i in range(v)]
            routes = [Route(bus=bus) for bus in buses]

            # Crea la instancia de SBRP
            sbrp = SBRP(school=school, stops=stops, students=students, routes=routes, max_distance=w,
                        bus_capacity=c, buses=buses)

            return sbrp
