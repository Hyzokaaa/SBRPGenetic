from src.problems.problem_sbrp.model.route import Route
from src.solution.solution import Solution


class SolutionRouteSBRP(Solution):
    def __init__(self, routes=None):
        self.routes: [] = routes if routes is not None else []

    def get_representation(self):
        return self.routes

    def set_representation(self, routes):
        self.routes = routes

    def copy(self):
        """
        Copia independiente de las rutas (las paradas se comparten, ya que no se modifican).
        """
        routes = []
        for route in self.routes:
            new_route = Route(stops=list(route.stops))
            new_route.students = route.students
            routes.append(new_route)
        return SolutionRouteSBRP(routes=routes)
