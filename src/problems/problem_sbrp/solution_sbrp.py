from src.solution.solution import Solution


class SolutionSBRP(Solution):
    def __init__(self, representation=None):
        self.representation = representation

    def get_representation(self):
        return self.representation

    def set_representation(self, representation):
        self.representation = representation
