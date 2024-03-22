from src.problems.problem_sbrp.model.stop import Stop


class Student:
    def __init__(self, id, name, coordinates, assigned_stop: Stop = None):
        self.id = id
        self.name = name
        self.coordinates = coordinates
        self.assigned_stop = assigned_stop

    def __eq__(self, other):
        if isinstance(other, Student):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return f"Student(ID: {self.id})"

