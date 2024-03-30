from abc import ABC, abstractmethod


class DistanceOperator(ABC):
    @abstractmethod
    def calculate_distance(self, point1, point2):
        pass
