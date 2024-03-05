import random
import copy
from typing import List

from src.model.route import Route
from src.model.school import School
from src.model.stop import Stop


class CrossoverOperator:
    def __init__(self, sbrp, crossover_rate):
        self.sbrp = sbrp
        self.crossover_rate = crossover_rate

    def crossover(self, parent1, parent2):
        # Genera un punto de cruce aleatorio
        m1 = self.count_routes_valids(parent1)
        m2 = self.count_routes_valids(parent2)
        size = min(m1, m2)
        cxpoint = random.randint(1, size)

        # Crea los hijos con las partes de los padres
        child1 = parent1[:cxpoint] + parent2[cxpoint:]
        child2 = parent2[:cxpoint] + parent1[cxpoint:]

        # Realiza la reparación de las soluciones

        # 1. Obtiene la lista de las paradas que contienen ambos hijos
        unique_stops = self.unique_stops([child1, child2])

        # 2. Repara los hijos
        child1 = self.repair(child1, unique_stops)
        child2 = self.repair(child2, unique_stops)

        return child1, child2

    def unique_stops(self, solutions):
        unique_stops = []
        for solution in solutions:
            for route in solution:
                for stop in route.stops:
                    if not isinstance(stop, School) and stop not in unique_stops:
                        unique_stops.append(stop)
        return unique_stops

    def get_feasible_stops(self, child, unique_stops):
        feasible_stops = []
        child_stops = []

        # Lista las paradas contenidas en la solución
        for route in child:
            for stop in route.stops:
                if not isinstance(stop, School):
                    child_stops.append(stop)

        # Lista las paradas que se encuentren dentro de unique_stops y no se encuentren dentro de child_stops
        # (Paradas Factibles)
        for stop in unique_stops:
            if stop not in child_stops:
                feasible_stops.append(stop)

        return feasible_stops

    def initial_repair_solution(self, child, unique_stops):
        # Obtiene la lista de posibles paradas que puedan ser utilizadas en la reparación
        feasible_stops = self.get_feasible_stops(child, unique_stops)

        # Inicializa una lista de paradas visitadas
        seen_stops = []

        # Itera sobre cada parada en cada ruta de la solution
        for route in child:
            i = 0
            while i < len(route.stops):
                stop = route.stops[i]
                # Si la parada no es la escuela
                if not isinstance(stop, School):
                    # Si la parada no se encuentra dentro de la lista de paradas visitadas la agrega a la lista
                    if stop not in seen_stops:
                        seen_stops.append(stop)
                        i += 1
                    # si se encuentra en las paradas visitadas, sustituye la parada por una factible
                    else:
                        if feasible_stops:
                            random_stop: Stop = random.choice(feasible_stops)
                            if route.students - stop.num_assigned_students + random_stop.num_assigned_students < self.sbrp.bus_capacity:
                                feasible_stops.remove(random_stop)
                                route.stops[i] = random_stop
                                route.students = route.students - stop.num_assigned_students + random_stop.num_assigned_students
                                i += 1
                            else:
                                route.students -= route.stops[i].num_assigned_students
                                route.stops.pop(i)
                                i += 1
                        else:
                            route.students -= route.stops[i].num_assigned_students
                            route.stops.pop(i)
                            i += 1
                else:
                    i += 1
        return child

    def final_repair_solution(self, child: List[Route], unique_stops):
        # Obtiene la lista de posibles paradas que puedan ser utilizadas en la reparación
        feasible_stops = self.get_feasible_stops(child, unique_stops)

        if len(feasible_stops) > 0:
            for stop in feasible_stops:
                for route in child:
                    if route.students + stop.num_assigned_students <= self.sbrp.bus_capacity and stop not in route.stops:
                        route.stops.insert(len(route.stops) - 1, stop)
                        route.students += stop.num_assigned_students
                        break
        return child

    def repair(self, child, unique_stops):
        child_copy = copy.deepcopy(child)

        child_return = self.initial_repair_solution(child_copy, unique_stops)
        child_return = self.final_repair_solution(child_copy, unique_stops)

        return child_return

    def update_route_students_in_solution(self, solution):
        for route in solution:
            students_sum = 0
            for stop in route.stops:
                students_sum += stop.num_assigned_students
            route.students = students_sum

    def count_routes_valids(self, solution):
        count = 0
        for route in solution:
            if len(route.stops) > 2:
                count += 1
        return count
