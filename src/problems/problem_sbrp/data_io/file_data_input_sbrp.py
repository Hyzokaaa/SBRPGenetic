from src.data_io.data_input import DataInput
from src.operators.distance.distance_euclidean import EuclideanDistance
from src.problems.problem_parameters import ProblemParameters


class FileDataInputSBRP(DataInput):
    def __init__(self, file_path):
        self.file = open(file_path, 'r')

    def read_parameters(self):
        return map(int, self.file.readline().split())

    def read_school_coordinates(self):
        return tuple(map(float, self.file.readline().split()))

    def read_stop_coordinates(self, m):
        return [[float(coordinate) for coordinate in coordinates] for coordinates in
                (self.file.readline().split() for _ in range(m))]

    def read_student_coordinates(self, n):
        return [[float(coordinate) for coordinate in coordinates] for coordinates in
                (self.file.readline().split() for _ in range(n))]

    def conform(self):
        # Lee los parámetros del problema
        m, n, v, c, w = self.read_parameters()

        # Lee las coordenadas de la escuela
        school_coordinates = self.read_school_coordinates()

        # Lee las coordenadas de las paradas
        stop_coordinates = self.read_stop_coordinates(m)

        # Lee las coordenadas de los estudiantes
        student_coordinates = self.read_student_coordinates(n)

        parameters = ProblemParameters(sbrp_school_coordinates=school_coordinates,
                                       sbrp_stops_coordinates=stop_coordinates,
                                       sbrp_student_coordinates=student_coordinates,
                                       sbrp_vehicles=v,
                                       sbrp_bus_capacity=c,
                                       sbrp_walk_distance=w,
                                       distance_operator=EuclideanDistance())

        return parameters
