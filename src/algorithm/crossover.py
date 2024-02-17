import random
import copy

from src.model.school import School


class Crossover:
    def __init__(self, sbrp, crossover_rate):
        self.sbrp = sbrp
        self.crossover_rate = crossover_rate

    def crossover(self, parent1, parent2):
        # Genera un punto de cruce aleatorio
        size = min(len(parent1), len(parent2))
        cxpoint = random.randint(1, size)

        # Crea los hijos con las partes de los padres
        child1 = parent1[:cxpoint] + parent2[cxpoint:]
        child2 = parent2[:cxpoint] + parent1[cxpoint:]

        # Asegura que los hijos cumplan con las restricciones del problema
        child1, child2 = self.process_solutions(child1, child2)
        return child1, child2

    def process_solutions(self, solution1, solution2):
        # Paso 1: Crear una lista única de paradas que contienen ambos padres.
        unique_stops = self.unique_stops([solution1, solution2])

        solution1_child = copy.deepcopy(solution1)
        feasible_stops = self.get_feasible_stops(solution1, solution2, solution1_child)
        new_solution1 = self.replace_repeated_stops(solution1_child, unique_stops, feasible_stops)

        solution2_child = copy.deepcopy(solution2)
        feasible_stops = self.get_feasible_stops(solution1, solution2, solution2_child)
        new_solution2 = self.replace_repeated_stops(solution2_child, unique_stops, feasible_stops)

        return new_solution1, new_solution2

    def unique_stops(self, solutions):
        unique_stops = []
        for solution in solutions:
            for route in solution:
                for stop in route.stops:
                    if not isinstance(stop, School) and stop not in unique_stops:
                        unique_stops.append(stop)
        return unique_stops

    def replace_repeated_stops(self, solution, unique_stops, feasible_stops):
        for route in solution:
            for i, stop in enumerate(route.stops):
                # Crear una lista de las paradas actuales
                current_stops = [s for r in solution for s in r.stops]
                # Si la parada está repetida y no es de tipo School
                if current_stops.count(stop) > 1 and not isinstance(stop, School):
                    for feasible_stop in feasible_stops:
                        if feasible_stop not in current_stops:
                            # Sustituir la parada repetida por la parada factible
                            route.stops[i] = feasible_stop
                            # Remover la parada factible de la lista de paradas factibles
                            feasible_stops.remove(feasible_stop)
                            break
        return solution

    def get_feasible_stops(self, parent1, parent2, child):
        feasible_stops = []
        parent_stops = [stop for route in parent1 + parent2 for stop in route.stops if not isinstance(stop, School)]
        child_stops = [stop for route in child for stop in route.stops if not isinstance(stop, School)]
        for stop in parent_stops:
            if stop not in child_stops and stop not in feasible_stops:
                feasible_stops.append(stop)
        return feasible_stops

