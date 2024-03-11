from src.problems.problem_sbrp.domain.model.stop import Stop


class Student:
    def __init__(self, id, name, coord_x, coord_y, assigned_stop: Stop = None):
        self.id = id
        self.name = name
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.assigned_stop = assigned_stop

