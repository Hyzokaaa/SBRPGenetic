from typing import List
from src.problems.problem_sbrp.domain.model.bus import Bus
from src.problems.problem_sbrp.domain.model.stop import Stop


class School(Stop):
    def __init__(self, id, name, coord_x, coord_y, buses: List[Bus] = None):
        self.id = id
        self.name = name
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.num_assigned_students = 0
        if buses is None:
            self.buses = []
        else:
            self.buses = buses

