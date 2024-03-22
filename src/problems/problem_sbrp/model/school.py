from typing import List
from src.problems.problem_sbrp.model.bus import Bus
from src.problems.problem_sbrp.model.stop import Stop


class School(Stop):
    def __init__(self, id, name, coordinates):
        super().__init__(id, name, coordinates)
        self.id = id
        self.name = name
        self.coordinates = coordinates
        self.num_assigned_students = 0

