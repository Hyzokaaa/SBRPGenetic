from abc import ABC, abstractmethod


class Distance(ABC):
    @abstractmethod
    def calculate_distance(self, point1, point2):
        pass
