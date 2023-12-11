class School:
    def __init__(self, id, name, coordinates):
        self.id = id
        self.name = name
        self.coordinates = coordinates
        self.buses = []  # A list of Bus objects
