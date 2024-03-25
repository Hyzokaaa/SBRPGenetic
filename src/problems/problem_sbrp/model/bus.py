from src.problems.problem_sbrp.model.route import Route


class Bus:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.route: Route = None

    def __str__(self):
        return f"Bus(ID: {self.id})"


