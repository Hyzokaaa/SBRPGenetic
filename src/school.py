class School:
    def __init__(self, id, name, coord_x, coord_y):
        self.id = id
        self.name = name
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.buses = []  # A list of Bus objects
