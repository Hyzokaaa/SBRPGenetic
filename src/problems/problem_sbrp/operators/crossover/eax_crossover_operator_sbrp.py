import random
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP

DEPOT = 0  # Identificador de la escuela en la matriz de distancias


class EAXCrossoverOperatorSBRP(CrossoverOperator):
    """
    Edge Assembly Crossover para CVRP (Nagata y Bräysy, 2009) con la estrategia de un solo ciclo AB:
    1. Construye el grafo unión de las aristas de ambos padres, descartando las aristas comunes.
    2. Descompone el grafo en ciclos AB (aristas que alternan entre el padre A y el padre B).
    3. Selecciona un ciclo AB al azar (E-set) y lo aplica a cada padre: elimina sus aristas propias
       y añade las del otro padre.
    4. Une los subtours resultantes (ciclos que no pasan por la escuela) a las rutas con el intercambio
       de aristas más barato.
    La capacidad y el tamaño de la flota no se corrigen aquí: se delegan en el operador de reparación
    (simplificación respecto a la búsqueda local con penalización del método original).
    """

    def crossover(self, parameters: CrossoverParameters):
        problem: ProblemSBRP = parameters.problem
        parent1, parent2 = parameters.parent1, parameters.parent2
        stops = self._stops_by_id(parent1, parent2)

        edges1 = self._edges(parent1)
        edges2 = self._edges(parent2)

        # Paso 1 y 2: grafo unión sin aristas comunes y descomposición en ciclos AB
        ab_cycles = self._ab_cycles(edges1, edges2)

        # Paso 3: E-set formado por un único ciclo AB seleccionado al azar
        e_set = random.choice(ab_cycles) if ab_cycles else []

        # Paso 3 y 4: aplicar el E-set a cada padre y eliminar los subtours
        child1 = self._create_child(edges1, e_set, 'A', stops, problem)
        child2 = self._create_child(edges2, e_set, 'B', stops, problem)

        return child1, child2

    # ------------------------- Grafo y ciclos AB -------------------------
    @staticmethod
    def _key(u: int, v: int) -> Tuple[int, int]:
        return (u, v) if u <= v else (v, u)

    def _edges(self, parent: SolutionRouteSBRP) -> List[Tuple[int, int]]:
        """
        Aristas de la solución tratando cada ruta como un ciclo que sale y regresa a la escuela.
        """
        edges = []
        for route in parent.get_representation():
            ids = [stop.id for stop in route.stops if stop is not None and not isinstance(stop, School)]
            if ids:
                path = [DEPOT] + ids + [DEPOT]
                edges.extend((path[i], path[i + 1]) for i in range(len(path) - 1))
        return edges

    def _ab_cycles(self, edges_a, edges_b) -> List[List[Tuple[int, int, str]]]:
        """
        Descompone el grafo unión (sin aristas comunes) en ciclos AB mediante caminatas aleatorias
        que alternan aristas de A y de B. Cada ciclo es una lista de aristas (u, v, etiqueta).
        """
        common = Counter(self._key(u, v) for u, v in edges_a) & Counter(self._key(u, v) for u, v in edges_b)
        adjacency = {'A': self._adjacency(edges_a, common.copy()), 'B': self._adjacency(edges_b, common.copy())}

        cycles = []
        while True:
            starts = [vertex for vertex, neighbors in adjacency['A'].items() if neighbors]
            if not starts:
                break
            path = [random.choice(starts)]
            positions = defaultdict(list)
            positions[path[0]].append(0)

            while True:
                label = 'A' if (len(path) - 1) % 2 == 0 else 'B'
                current = path[-1]
                neighbors = adjacency[label][current]
                if not neighbors:
                    # Camino sin salida (desbalance en la escuela): se descartan sus aristas
                    break
                nxt = random.choice(neighbors)
                self._remove_edge(adjacency[label], current, nxt)
                path.append(nxt)
                n = len(path) - 1

                # Se cierra un ciclo AB si se vuelve a un vértice del camino tras un número par de aristas
                closing = next((j for j in reversed(positions[nxt]) if (n - j) % 2 == 0), None)
                if closing is None:
                    positions[nxt].append(n)
                    continue
                cycles.append([(path[i], path[i + 1], 'A' if i % 2 == 0 else 'B') for i in range(closing, n)])
                for i in range(closing + 1, n):
                    positions[path[i]].remove(i)
                path = path[:closing + 1]
        return cycles

    def _adjacency(self, edges, common: Counter) -> Dict[int, List[int]]:
        adjacency = defaultdict(list)
        for u, v in edges:
            key = self._key(u, v)
            if common[key] > 0:
                common[key] -= 1
                continue
            adjacency[u].append(v)
            adjacency[v].append(u)
        return adjacency

    @staticmethod
    def _remove_edge(adjacency, u: int, v: int):
        adjacency[u].remove(v)
        adjacency[v].remove(u)

    # ------------------------- Construcción del hijo -------------------------
    def _create_child(self, own_edges, e_set, own_label: str, stops: Dict[int, Stop],
                      problem: ProblemSBRP) -> SolutionRouteSBRP:
        # Aplica el E-set: elimina las aristas propias del ciclo y añade las del otro padre
        edges = Counter(self._key(u, v) for u, v in own_edges)
        for u, v, label in e_set:
            edges[self._key(u, v)] += -1 if label == own_label else 1

        adjacency = defaultdict(list)
        for (u, v), count in edges.items():
            for _ in range(count):
                adjacency[u].append(v)
                adjacency[v].append(u)

        routes = self._extract_routes(adjacency)
        subtours = self._extract_subtours(adjacency)

        # Paso 4: unir cada subtour a la ruta con el intercambio de aristas más barato
        for subtour in subtours:
            self._merge_subtour(routes, subtour, problem)

        return SolutionRouteSBRP(routes=[Route(stops=[problem.school] + [stops[i] for i in route] + [problem.school])
                                         for route in routes])

    def _extract_routes(self, adjacency) -> List[List[int]]:
        """
        Extrae las rutas recorriendo desde la escuela hasta regresar a ella.
        """
        routes = []
        while adjacency[DEPOT]:
            current = adjacency[DEPOT][0]
            self._remove_edge(adjacency, DEPOT, current)
            route = []
            while current != DEPOT:
                route.append(current)
                if not adjacency[current]:
                    break
                nxt = adjacency[current][0]
                self._remove_edge(adjacency, current, nxt)
                current = nxt
            routes.append(route)
        return routes

    def _extract_subtours(self, adjacency) -> List[List[int]]:
        """
        Extrae los ciclos que no pasan por la escuela.
        """
        subtours = []
        for start in list(adjacency):
            while adjacency[start]:
                subtour = [start]
                current = start
                nxt = adjacency[current][0]
                self._remove_edge(adjacency, current, nxt)
                while nxt != start:
                    subtour.append(nxt)
                    current = nxt
                    if not adjacency[current]:
                        break
                    nxt = adjacency[current][0]
                    self._remove_edge(adjacency, current, nxt)
                subtours.append(subtour)
        return subtours

    def _merge_subtour(self, routes: List[List[int]], subtour: List[int], problem: ProblemSBRP):
        """
        Rompe una arista (a, b) del subtour y una arista (c, d) de una ruta, y reconecta con
        (c, a) + (b, d) o (c, b) + (a, d), eligiendo la combinación de menor costo.
        """
        if not routes:
            routes.append([])
        distance = problem.distance_matrix
        best = None
        size = len(subtour)
        for i in range(size):
            a, b = subtour[i], subtour[(i + 1) % size]
            for r, route in enumerate(routes):
                path = [DEPOT] + route + [DEPOT]
                for j in range(len(path) - 1):
                    c, d = path[j], path[j + 1]
                    removed = distance[a][b] + distance[c][d]
                    for reverse, added in ((True, distance[c][a] + distance[b][d]),
                                           (False, distance[c][b] + distance[a][d])):
                        delta = added - removed
                        if best is None or delta < best[0]:
                            best = (delta, i, r, j, reverse)

        _, i, r, j, reverse = best
        # Recorrido del subtour que empieza en b y termina en a
        segment = subtour[i + 1:] + subtour[:i + 1]
        if reverse:
            segment = segment[::-1]
        routes[r][j:j] = segment

    @staticmethod
    def _stops_by_id(*parents: SolutionRouteSBRP) -> Dict[int, Stop]:
        stops = {}
        for parent in parents:
            for route in parent.get_representation():
                for stop in route.stops:
                    if stop is not None and not isinstance(stop, School):
                        stops.setdefault(stop.id, stop)
        return stops
