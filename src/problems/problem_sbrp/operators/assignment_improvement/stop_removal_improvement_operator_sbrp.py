from collections import defaultdict, deque

from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.operators.assignment_improvement.assignment_improvement_operator import \
    AssignmentImprovementOperator
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.rebalance.stop_assignment_rebalancer import \
    StopAssignmentRebalancer
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


class StopRemovalImprovementOperatorSBRP(AssignmentImprovementOperator):
    """
    Cierre de paradas (como el vecindario Remove de Schittekat et al., 2013): con las rutas de la mejor solución,
    recorre las paradas visitadas de la que más desvío ahorra a la que menos y cierra cada una cuyos estudiantes pueden
    caminar a otras paradas visitadas. Los estudiantes se recolocan con caminos de aumento (un estudiante puede ocupar
    el sitio de otro que a su vez se mueve) respetando la distancia a pie y la capacidad de cada parada y de cada bus.
    Quitar una parada de una ruta nunca la alarga (desigualdad triangular), así que la solución nunca empeora.
    """

    def improve(self, problem: ProblemSBRP, distance_operator: DistanceOperator) -> int:
        if problem.best_solution is None:
            return 0
        routes, students, reachable = self.prepare(problem, distance_operator)
        closed = 0
        changed = True
        while changed:
            changed = False
            for stop in self.by_saving(routes, problem):
                if self.close(stop, routes, students, reachable, problem):
                    closed += 1
                    changed = True
                    break
        if closed:
            self.finish(problem, routes, students)
        return closed

    @staticmethod
    def prepare(problem: ProblemSBRP, distance_operator: DistanceOperator):
        """Rutas de la mejor solución (con las paradas del problema), estudiantes por parada y paradas alcanzables."""
        school = problem.school.id
        # Las rutas pueden contener copias de las paradas: se trabaja siempre con las paradas del problema
        stops_by_id = {stop.id: stop for stop in problem.stops}
        routes = [[stops_by_id[stop.id] for stop in route.stops if stop.id != school]
                  for route in problem.best_solution.get_representation()]
        routes = [stops for stops in routes if stops]
        students = defaultdict(list)
        for student in problem.students:
            students[student.assigned_stop.id].append(student)
        reach = {}

        def reachable(student):
            if student.id not in reach:
                reach[student.id] = {stop.id for stop in problem.stops
                                     if distance_operator.calculate_distance(student.coordinates, stop.coordinates)
                                     <= problem.w_distance}
            return reach[student.id]

        return routes, students, reachable

    def finish(self, problem: ProblemSBRP, routes, students):
        """Aplica la nueva asignación y las nuevas rutas al problema."""
        for stop in problem.stops:
            stop.num_assigned_students = len(students[stop.id])
        problem.best_solution = SolutionRouteSBRP(routes=[self.build_route(stops, problem) for stops in routes
                                                          if stops])
        problem.clear_evaluation_cache()
        if problem.assign_solution is not None:
            StopAssignmentRebalancer.sync_and_validate(problem, problem.assign_solution)

    @staticmethod
    def by_saving(routes, problem: ProblemSBRP) -> list:
        """Paradas visitadas, de la que más acorta su ruta al quitarla a la que menos."""
        matrix, school = problem.distance_matrix, problem.school.id
        savings = []
        for stops in routes:
            path = [school] + [stop.id for stop in stops] + [school]
            for position, stop in enumerate(stops, 1):
                a, s, b = path[position - 1], path[position], path[position + 1]
                savings.append((matrix[a][s] + matrix[s][b] - matrix[a][b], -stop.id, stop))
        return [stop for *_, stop in sorted(savings, key=lambda item: item[:2], reverse=True)]

    def close(self, stop, routes, students, reachable, problem: ProblemSBRP) -> bool:
        """Recoloca a todos los estudiantes de la parada en otras visitadas y la quita de su ruta, si es posible."""
        capacity = problem.bus_capacity
        route_of = {s.id: index for index, stops in enumerate(routes) for s in stops}
        visited = {s.id: s for stops in routes for s in stops}
        stop_load = {stop_id: len(students[stop_id]) for stop_id in visited}
        route_load = [sum(stop_load[s.id] for s in stops) for stops in routes]
        origin_route = route_of[stop.id]
        moves = []                                          # (estudiante, parada de origen, parada de destino)

        for student in list(students[stop.id]):
            path = self.augmenting_path(student, stop.id, visited, students, reachable, stop_load, route_load,
                                        route_of, origin_route, capacity)
            if path is None:
                for moved, source, target in reversed(moves):  # deshace los movimientos ya hechos
                    students[target].remove(moved)
                    students[source].append(moved)
                    moved.assigned_stop = visited[source] if source in visited else stop
                return False
            for moved, source, target in path:
                students[source].remove(moved)
                students[target].append(moved)
                moved.assigned_stop = visited[target]
                moves.append((moved, source, target))
            final = path[-1][2]
            stop_load[final] += 1
            route_load[route_of[final]] += 1
            route_load[origin_route] -= 1
            stop_load[stop.id] -= 1

        routes[origin_route].remove(stop)
        stop.num_assigned_students = 0
        return True

    @staticmethod
    def augmenting_path(student, closing, visited, students, reachable, stop_load, route_load, route_of,
                        origin_route, capacity):
        """
        Camino más corto (en anchura) para sacar al estudiante de la parada que se cierra: cada paso mueve a un
        estudiante a otra parada visitada alcanzable; termina en una parada con sitio cuyo bus también tiene sitio
        (o es el mismo bus que la parada que se cierra, que pierde un estudiante).
        """
        parent = {}
        queue = deque()
        for target in reachable(student):
            if target in visited and target != closing and target not in parent:
                parent[target] = (student, closing)
                queue.append(target)
        while queue:
            current = queue.popleft()
            route = route_of[current]
            if stop_load[current] < capacity and (route == origin_route or route_load[route] < capacity):
                path = []
                while True:
                    moved, source = parent[current]
                    path.append((moved, source, current))
                    if source == closing:
                        return list(reversed(path))
                    current = source
            for other in students[current]:
                for target in reachable(other):
                    if target in visited and target != closing and target not in parent:
                        parent[target] = (other, current)
                        queue.append(target)
        return None

    @staticmethod
    def build_route(stops, problem: ProblemSBRP) -> Route:
        route = Route(stops=[problem.school] + list(stops) + [problem.school])
        route.students = sum(stop.num_assigned_students for stop in stops)
        return route
