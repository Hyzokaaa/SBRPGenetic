from typing import List
from src.stop import Stop


class Route:
    def __init__(self, bus, stops: List[Stop] = None):
        self.bus = bus
        if stops is None:
            self.stops = []
        else:
            self.stops = stops

