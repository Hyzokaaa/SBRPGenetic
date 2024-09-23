from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP
from src.problems.problem_sbrp.model.route import Route
import random
from collections import defaultdict

class EAXCrossoverOperatorSBRP(CrossoverOperator):
    def crossover(self, parameters: CrossoverParameters):
        parent1, parent2 = parameters.parent1.get_representation(), parameters.parent2.get_representation()
        
        # Paso 1: Crear el grafo unión
        union_graph = self.create_union_graph(parent1, parent2)
        
        # Paso 2: Generar ciclos AB
        ab_cycles = self.generate_ab_cycles(union_graph)
        
        # Paso 3: Seleccionar ciclos aleatoriamente
        selected_cycles = self.select_random_cycles(ab_cycles)
        
        # Paso 4: Crear hijos
        child1 = self.create_child(parent1, selected_cycles)
        child2 = self.create_child(parent2, selected_cycles)
        
        # Convertir las representaciones de los hijos en instancias de SolutionRouteSBRP
        new_child1 = SolutionRouteSBRP()
        new_child1.set_representation(child1)
        new_child2 = SolutionRouteSBRP()
        new_child2.set_representation(child2)
        
        return new_child1, new_child2

    def create_union_graph(self, parent1, parent2):
        union_graph = defaultdict(set)
        for route in parent1 + parent2:
            for i in range(len(route.stops) - 1):
                start, end = route.stops[i].id, route.stops[i+1].id
                union_graph[start].add(end)
                union_graph[end]  # Asegurarse de que el vértice final esté en el grafo
        return union_graph

    def generate_ab_cycles(self, union_graph):
        ab_cycles = []
        visited = set()
        for start in union_graph:
            if start not in visited:
                cycle = self.dfs_cycle(union_graph, start, visited)
                if cycle and len(cycle) > 2:  # Asegurarse de que el ciclo tenga al menos 3 vértices
                    ab_cycles.append(cycle)
        return ab_cycles

    def dfs_cycle(self, graph, start, visited):
        stack = [(start, [start])]
        while stack:
            vertex, path = stack.pop()
            if len(path) > 1 and vertex == start:
                return path
            if vertex not in visited:
                visited.add(vertex)
                for neighbor in graph[vertex]:
                    if neighbor not in visited:
                        stack.append((neighbor, path + [neighbor]))
        return None

    def select_random_cycles(self, ab_cycles):
        if not ab_cycles:
            return []
        return random.sample(ab_cycles, k=random.randint(1, len(ab_cycles)))

    def create_child(self, parent, selected_cycles):
        child = []
        used_stops = set()
        for cycle in selected_cycles:
            for stop_id in cycle:
                used_stops.add(stop_id)
        
        for route in parent:
            new_route = Route(stops=[])
            for stop in route.stops:
                if stop.id not in used_stops:
                    new_route.stops.append(stop)
            if len(new_route.stops) > 1:
                child.append(new_route)
        
        for cycle in selected_cycles:
            new_route = Route(stops=[])
            for stop_id in cycle:
                stop = next((stop for route in parent for stop in route.stops if stop.id == stop_id), None)
                if stop:
                    new_route.stops.append(stop)
            if len(new_route.stops) > 1:
                child.append(new_route)
        
        return child
