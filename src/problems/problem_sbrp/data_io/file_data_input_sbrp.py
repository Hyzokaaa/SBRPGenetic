from src.data_io.data_input import DataInput
from src.operators.distance.distance_euclidean import EuclideanDistance
from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_parameters import ProblemParameters


class FileDataInputSBRP(DataInput):
    def __init__(self, file_path, distance_operator: DistanceOperator = None):
        self.file_path = file_path
        # Distancia con la que se construye la matriz de distancias del problema
        self.distance_operator = distance_operator if distance_operator is not None else EuclideanDistance()
        self.file = None

    def read_parameters(self):
        m, n, v, c, w = self.file.readline().split()
        return int(m), int(n), int(v), int(c), float(w)

    def read_school_coordinates(self):
        return tuple(map(float, self.file.readline().split()))

    def read_stop_coordinates(self, m):
        return [[float(coordinate) for coordinate in coordinates] for coordinates in
                (self.file.readline().split() for _ in range(m))]

    def read_student_coordinates(self, n):
        return [[float(coordinate) for coordinate in coordinates] for coordinates in
                (self.file.readline().split() for _ in range(n))]

    def conform(self):
        with open(self.file_path, 'r') as self.file:
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
                                       distance_operator=self.distance_operator)

        return parameters
