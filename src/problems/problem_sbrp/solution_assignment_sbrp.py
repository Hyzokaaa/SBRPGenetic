from src.solution.solution import Solution


class SolutionAssignmentSBRP(Solution):
    def __init__(self, assignments=None):
        self.assignments = assignments if assignments is not None else []

    def get_representation(self):
        return self.assignments

    def set_representation(self, assignments):
        self.assignments = assignments
