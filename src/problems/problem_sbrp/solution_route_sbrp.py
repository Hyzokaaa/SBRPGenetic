from src.solution.solution import Solution


class SolutionRouteSBRP(Solution):
    def __init__(self, routes=None):
        self.routes: [] = routes if routes is not None else []

    def get_representation(self):
        return self.routes

    def set_representation(self, routes):
        self.routes = routes

    def copy(self):
        return SolutionRouteSBRP(routes=self.routes.copy())

