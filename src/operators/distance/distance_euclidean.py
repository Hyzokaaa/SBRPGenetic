import numpy as np

from src.operators.distance.distance_operator import DistanceOperator


class EuclideanDistance(DistanceOperator):
    def calculate_distance(self, point1, point2):
        return np.sqrt(np.sum((np.array(point1) - np.array(point2))**2))
