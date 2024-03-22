from typing import Tuple, List

from src.operators.distance.distance_operator import Distance


class ProblemParameters:
    def __init__(self,
                 distance_operator: Distance = None,
                 sbrp_school_coordinates: Tuple[float, float] = None,
                 sbrp_stops_coordinates: List[Tuple[float, float]] = None,
                 sbrp_student_coordinates: List[Tuple[float, float]] = None,
                 sbrp_vehicles: int = None,
                 sbrp_bus_capacity: int = None,
                 sbrp_walk_distance: float = None):
        self.distance_operator = distance_operator
        self.sbrp_school_coordinates = sbrp_school_coordinates
        self.sbrp_stops_coordinates = sbrp_stops_coordinates
        self.sbrp_student_coordinates = sbrp_student_coordinates
        self.sbrp_vehicles = sbrp_vehicles
        self.sbrp_bus_capacity = sbrp_bus_capacity
        self.sbrp_walk_distance = sbrp_walk_distance

