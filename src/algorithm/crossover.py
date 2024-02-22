import random

from src.model.school import School
from src.model.stop import Stop


class Crossover:
    def __init__(self, sbrp, crossover_rate):
        self.sbrp = sbrp
        self.crossover_rate = crossover_rate

    def crossover(self, parent1, parent2):
        # Genera un punto de cruce aleatorio
        size = min(len(parent1), len(parent2))
        cxpoint = random.randint(1, size)
        cxpoint = 1

        # Crea los hijos con las partes de los padres
        child1 = parent1[:cxpoint] + parent2[cxpoint:]
        child2 = parent2[:cxpoint] + parent1[cxpoint:]

        # Recalcula la cantidad de estudiantes por ruta en cada solución
        self.update_route_students_in_solution(child1)
        self.update_route_students_in_solution(child2)

        # Realiza la reparación de las soluciones

        # Obtiene la lista de las paradas que contienen ambos hijos
        unique_stops = self.unique_stops([child1, child2])

        self.initial_repair_solution(child1, unique_stops)
        self.initial_repair_solution(child2, unique_stops)

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
                    # si se encuentra de las paradas visitadas, sustituye la parada por una aleatoria dentro
                    # de la lista de paradas factibles
                    else:
                        if feasible_stops:
                            random_stop: Stop = random.choice(feasible_stops)
                            if route.students + random_stop.num_assigned_students < self.sbrp.bus_capacity:
                                feasible_stops.remove(random_stop)
                                route.stops[i] = random_stop
                                i += 1
                            else:
                                route.stops.pop(i)
                        # elimina la parada analizada en caso de que no haya paradas factibles para agregar
                        else:
                            route.stops.pop(i)
                else:
                    i += 1

    def final_repair_solution(self, child, unique_stops):
        # Obtiene la lista de posibles paradas que puedan ser utilizadas en la reparación
        feasible_stops = self.get_feasible_stops(child, unique_stops)

        if len(feasible_stops) > 0:
            for stop in feasible_stops:
                for route in child:
                    print("ass")

    def update_route_students_in_solution(self, solution):
        for route in solution:
            i = 0
            students_sum = 0
            while i < len(route.stops):
                if not isinstance(route.stops[i], School):
                    route.stops[i].num_assigned_students = self.get_stop_students_sbrp(route.stops[i])
                    students_sum = students_sum + route.stops[i].num_assigned_students
                i = i + 1
            route.students = students_sum

    def get_stop_students_sbrp(self, stop: Stop):
        id = stop.id
        returned_stop: Stop
        for s in self.sbrp.stops:
            if s.id == id:
                returned_stop = s
                return returned_stop.num_assigned_students
        return None
