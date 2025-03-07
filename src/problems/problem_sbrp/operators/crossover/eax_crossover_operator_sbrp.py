from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP
from src.problems.problem_sbrp.model.route import Route
import random
from collections import defaultdict

class EAXCrossoverOperatorSBRP(CrossoverOperator):
    def crossover(self, parameters: CrossoverParameters):
        parent1, parent2 = parameters.parent1.get_representation(), parameters.parent2.get_representation()

        # Paso 1: Crear el grafo unión con etiquetas A/B
        union_graph = self.create_union_graph(parent1, parent2)

        # Paso 2: Generar ciclos AB
        ab_cycles = self.generate_ab_cycles(union_graph)

        # Paso 3: Seleccionar ciclos aleatoriamente
        selected_cycles = self.select_random_cycles(ab_cycles)

        # Paso 4: Crear hijos alternando aristas
        child1 = self.create_child(parent1, selected_cycles, 'B')  # Usar aristas B en ciclos
        child2 = self.create_child(parent2, selected_cycles, 'A')  # Usar aristas A en ciclos

        # Convertir las representaciones de los hijos en instancias de SolutionRouteSBRP
        new_child1 = SolutionRouteSBRP()
        new_child1.set_representation(child1)
        new_child2 = SolutionRouteSBRP()
        new_child2.set_representation(child2)

        return new_child1, new_child2

    def create_union_graph(self, parent1, parent2):
        union_graph = defaultdict(lambda: {'A': set(), 'B': set()})  # Grafo con etiquetas A/B
        for route in parent1:
            for i in range(len(route.stops) - 1):
                start, end = route.stops[i].id, route.stops[i + 1].id
                union_graph[start]['A'].add(end)  # Arista de padre1 (A)
                union_graph[end]['A'].add(start)  # Grafo no dirigido
        for route in parent2:
            for i in range(len(route.stops) - 1):
                start, end = route.stops[i].id, route.stops[i + 1].id
                union_graph[start]['B'].add(end)  # Arista de padre2 (B)
                union_graph[end]['B'].add(start)  # Grafo no dirigido
        return union_graph

    def generate_ab_cycles(self, union_graph):
        ab_cycles = []
        visited = set()
        for start in union_graph:
            if start not in visited:
                cycle = self.bfs_ab_cycle(union_graph, start, visited)
                if cycle and len(cycle) > 2:  # Ciclos con al menos 3 vértices
                    ab_cycles.append(cycle)
        return ab_cycles

    def bfs_ab_cycle(self, graph, start, visited):
        from collections import deque
        queue = deque([(start, 'A', [start])])  # Alternar entre A y B
        while queue:
            vertex, edge_type, path = queue.popleft()
            if len(path) > 1 and vertex == start:
                return path  # Ciclo cerrado
            if vertex not in visited:
                visited.add(vertex)
                for neighbor in graph[vertex][edge_type]:
                    next_edge_type = 'B' if edge_type == 'A' else 'A'  # Alternar A/B
                    queue.append((neighbor, next_edge_type, path + [neighbor]))
        return None

    def select_random_cycles(self, ab_cycles):
        if not ab_cycles:
            return []
        # Priorizar ciclos pequeños
        ab_cycles.sort(key=lambda cycle: len(cycle))
        return random.sample(ab_cycles, k=min(3, len(ab_cycles)))  # Máximo 3 ciclos

    def create_child(self, parent, selected_cycles, edge_type):
        child = []
        used_edges = set()
        for cycle in selected_cycles:
            for i in range(len(cycle) - 1):
                start, end = cycle[i], cycle[i + 1]
                used_edges.add((start, end))  # Marcar aristas usadas en los ciclos

        for route in parent:
            new_route = Route(stops=[])
            for i in range(len(route.stops) - 1):
                start, end = route.stops[i].id, route.stops[i + 1].id
                if (start, end) not in used_edges:  # Conservar aristas no usadas
                    new_route.stops.append(route.stops[i])
            if new_route.stops:
                new_route.stops.append(route.stops[-1])  # Añadir última parada
                child.append(new_route)

        # Añadir aristas de los ciclos (alternando A/B)
        for cycle in selected_cycles:
            new_route = Route(stops=[])
            for i in range(len(cycle) - 1):
                start, end = cycle[i], cycle[i + 1]
                stop = self.get_stop_by_id(parent, start)
                new_route.stops.append(stop)
            if new_route.stops:
                new_route.stops.append(self.get_stop_by_id(parent, cycle[-1]))  # Cerrar ciclo
                child.append(new_route)

        return child

    def get_stop_by_id(self, parent, stop_id):
        for route in parent:
            for stop in route.stops:
                if stop.id == stop_id:
                    return stop
        return None

    def _ensure_mandatory_stops(self, child: SolutionRouteSBRP, problem: ProblemSBRP):
        """
        Asegura que todas las paradas con estudiantes estén en la solución.
        """
        # Obtener todas las paradas con estudiantes de los padres
        mandatory_stops = [stop for stop in problem.stops if stop.num_assigned_students > 0]

        # Verificar cada parada obligatoria
        for stop in mandatory_stops:
            if not self._is_stop_in_child(child, stop):
                self._force_insert_stop(child, stop, problem.bus_capacity)

    def _force_insert_stop(self, child: SolutionRouteSBRP, stop: Stop, bus_capacity: int):
        """
        Inserta una parada obligatoria en la solución, incluso si es necesario crear una nueva ruta.
        """
        # Intentar insertar en rutas existentes
        for route in child.get_representation():
            if route.students + stop.num_assigned_students <= bus_capacity:
                route.stops.insert(-1, stop)  # Insertar antes de la escuela
                route.students += stop.num_assigned_students
                return

        # Si no hay espacio, crear nueva ruta solo para esta parada
        school = child.get_representation()[0].stops[0]  # La escuela es el primer stop de la primera ruta
        new_route = Route(stops=[school, stop, school])
        new_route.students = stop.num_assigned_students
        child.get_representation().append(new_route)

    def _is_stop_in_child(self, child: SolutionRouteSBRP, stop: Stop) -> bool:
        """
        Verifica si una parada está presente en alguna ruta de la solución.
        """
        for route in child.get_representation():
            if stop in route.stops:
                return True
        return False