class Stop:
    def __init__(self, id, name, coord_x, coord_y, num_assigned_students=0):
        self.id = id
        self.name = name
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.num_assigned_students = num_assigned_students

    def __eq__(self, other):
        if isinstance(other, Stop):
            return self.coord_x == other.coord_x and self.coord_y == other.coord_y
        return False

    def __hash__(self):
        return hash((self.coord_x, self.coord_y))

    def __str__(self):
        return f"Stop(Coord.x={self.coord_x}, Coord.y={self.coord_y})"
