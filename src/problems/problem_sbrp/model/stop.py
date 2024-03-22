class Stop:
    def __init__(self, id, name, coordinates, num_assigned_students=0):
        self.id = id
        self.name = name
        self.coordinates = coordinates
        self.num_assigned_students = num_assigned_students
        self.is_assigned = False

    def __eq__(self, other):
        if isinstance(other, Stop):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return f"Stop(ID: {self.id})"
