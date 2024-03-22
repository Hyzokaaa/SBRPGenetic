from abc import ABC, abstractmethod
import numpy as np


class Distance(ABC):
    @abstractmethod
    def calculate_distance(self, point1, point2):
        pass


class EuclideanDistance(Distance):
    def calculate_distance(self, point1, point2):
        return np.sqrt(np.sum((np.array(point1) - np.array(point2))**2))


class ManhattanDistance(Distance):
    def calculate_distance(self, point1, point2):
        return np.sum(np.abs(np.array(point1) - np.array(point2)))
