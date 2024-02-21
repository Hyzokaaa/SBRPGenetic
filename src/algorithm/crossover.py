import random

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

        # Realiza la reparación de las soluciones

        # Obtiene la lista de las paradas que contienen ambos hijos
        unique_stops = self.unique_stops([child1, child2])

        self.repair_solution(child1, unique_stops)
        self.repair_solution(child2, unique_stops)
        suma = 0
        for route in child1:
            for stop in route.stops:
                if not isinstance(stop, School):
                    suma += 1
        print(suma)
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

    def repair_solution(self, child, unique_stops):
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
                    # Si la parada no se encuentra dentro de la lista de paradas visitadas la agrega a la lista,
                    # en caso contrario sustituye la parada por una aleatoria dentro de la lista de paradas factibles
                    # o la elimina si no hay paradas factibles
                    if stop not in seen_stops:
                        seen_stops.append(stop)
                        i += 1
                    else:
                        if feasible_stops:
                            random_stop = random.choice(feasible_stops)
                            feasible_stops.remove(random_stop)
                            route.stops[i] = random_stop
                            i += 1
                        else:
                            print("no quedan paradas factibles, eliminando parada duplicada")
                            route.stops.pop(i)
                else:
                    i += 1

