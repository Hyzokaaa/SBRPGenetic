from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.operators.assignment_improvement.stop_removal_improvement_operator_sbrp import \
    StopRemovalImprovementOperatorSBRP
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP

EPSILON = 1e-9


class StopReplacementImprovementOperatorSBRP(StopRemovalImprovementOperatorSBRP):
    """
    Sustitución de paradas (como el vecindario Replace de Schittekat et al., 2013): con las rutas de la mejor solución,
    prueba a cambiar cada parada visitada por una de las neighbors paradas no visitadas más cercanas a ella, insertada
    en la posición más barata de la misma ruta. Acepta el cambio si la ruta se acorta y todos los estudiantes de la
    parada sustituida pueden caminar a las paradas visitadas (incluida la nueva), con reasignaciones en cadena y
    respetando la capacidad de cada parada y de cada bus. Nunca empeora la solución.
    """

    def __init__(self, neighbors: int = 5):
        if neighbors < 1:
            raise ValueError("neighbors debe ser >= 1")
        self.neighbors = neighbors

    def improve(self, problem: ProblemSBRP, distance_operator: DistanceOperator) -> int:
        if problem.best_solution is None:
            return 0
        routes, students, reachable = self.prepare(problem, distance_operator)
        matrix = problem.distance_matrix
        replaced = 0
        changed = True
        while changed:
            changed = False
            visited = {stop.id for stops in routes for stop in stops}
            for stop in self.by_saving(routes, problem):
                route = next(stops for stops in routes if stop in stops)
                old_cost = self.route_cost(route, problem)
                others = [s for s in route if s is not stop]
                candidates = sorted((s for s in problem.stops if s.id not in visited),
                                    key=lambda s: (matrix[stop.id][s.id], s.id))[:self.neighbors]
                for candidate in candidates:
                    position, new_cost = self.cheapest_position(others, candidate, problem)
                    if new_cost >= old_cost - EPSILON:
                        continue
                    # La nueva parada entra en la ruta y la sustituida se cierra si sus estudiantes caben
                    route.insert(route.index(stop) if position is None else self.insert_index(route, others, position),
                                 candidate)
                    if self.close(stop, routes, students, reachable, problem):
                        self.reorder(route, others, candidate, position)
                        replaced += 1
                        changed = True
                        break
                    route.remove(candidate)
                if changed:
                    break
        if replaced:
            self.finish(problem, routes, students)
        return replaced

    @staticmethod
    def route_cost(stops, problem: ProblemSBRP) -> float:
        path = [problem.school.id] + [stop.id for stop in stops] + [problem.school.id]
        return sum(problem.distance_matrix[path[i]][path[i + 1]] for i in range(len(path) - 1))

    def cheapest_position(self, stops, candidate, problem: ProblemSBRP):
        """Posición de menor coste para insertar la parada en la ruta y el coste resultante de la ruta."""
        best = None
        for position in range(len(stops) + 1):
            cost = self.route_cost(stops[:position] + [candidate] + stops[position:], problem)
            if best is None or cost < best[1]:
                best = (position, cost)
        return best

    @staticmethod
    def insert_index(route, others, position):
        """Índice en la ruta actual (que aún contiene la parada sustituida) equivalente a la posición en others."""
        return len(route) if position >= len(others) else route.index(others[position])

    @staticmethod
    def reorder(route, others, candidate, position):
        """Deja la ruta en el orden de menor coste calculado (la parada sustituida ya se quitó)."""
        route[:] = others[:position] + [candidate] + others[position:]
