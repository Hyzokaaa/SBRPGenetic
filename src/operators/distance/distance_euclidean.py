import math

from src.operators.distance.distance_operator import DistanceOperator


class EuclideanDistance(DistanceOperator):
    def calculate_distance(self, point1, point2):
        # Mismas operaciones y en el mismo orden que la versión con numpy (resultado idéntico), sin crear arrays
        dx, dy = point1[0] - point2[0], point1[1] - point2[1]
        return math.sqrt(dx * dx + dy * dy)
