from typing import List
from src.bus import Bus


class School:
    def __init__(self, id, name, coord_x, coord_y, buses: List[Bus] = None):
        self.id = id
        self.name = name
        self.coord_x = coord_x
        self.coord_y = coord_y
        if buses is None:
            self.buses = []
        else:
            self.buses = buses

