import numpy as np

from src.operators.distance.distance_operator import DistanceOperator


class ManhattanDistance(DistanceOperator):
    def calculate_distance(self, point1, point2):
        return np.sum(np.abs(np.array(point1) - np.array(point2)))