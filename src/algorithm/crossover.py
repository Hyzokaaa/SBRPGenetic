import random
from typing import List

from src.model.route import Route
from src.model.school import School
from src.model.stop import Stop


class Crossover:
    def __init__(self, sbrp, crossover_rate):
        self.sbrp = sbrp
        self.crossover_rate = crossover_rate

    def crossover(self, parent1, parent2):
        # Se realiza un cruce
        if random.random() < self.crossover_rate:
            # Selecciona un punto de cruce al azar
            crossover_point = random.randint(1, len(parent1) - 1)

            # Crea dos hijos intercambiando las rutas de los padres en el punto de cruce
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
        else:
            # Si no se realiza un cruce los hijos = padres
            child1, child2 = parent1, parent2
        return child1, child2

    def repair_children(self, child1, child2):
        # Asegúrate de que las paradas de 'sbrp' no se eliminen
        for stop in self.sbrp.stops:
            if stop not in child1 and not isinstance(stop, School):
                # Añade la parada a child1 si no está presente
                child1.append(stop)
            if stop not in child2 and not isinstance(stop, School):
                # Añade la parada a child2 si no está presente
                child2.append(stop)

        # Realiza cualquier otra reparación necesaria aquí

        return child1, child2

    def repair(self, child, second_child):
        # Crear copias de las soluciones para no modificar las originales
        child = [route.copy() for route in child]
        second_child = [route.copy() for route in second_child]

        # Crear un conjunto para almacenar las paradas ya visitadas
        seen_stops = set()

        for one_route in child:
            stops_to_remove = []  # Añade esta línea para almacenar las paradas que se van a eliminar
            for i in range(len(one_route.stops[:])):  # Añade [:] para crear una copia de la lista
                # Si la parada ya ha sido visitada, buscar una parada alternativa
                if one_route.stops[i] in seen_stops:
                    for two_route in second_child:
                        for j in range(len(two_route.stops)):
                            # Si la parada alternativa no excede la capacidad máxima y no ha sido visitada, usarla
                            if (two_route.stops[j] not in seen_stops and self.sbrp.bus_capacity >= two_route.stops[j].
                                    num_assigned_students):
                                one_route.stops[i] = two_route.stops[j]
                                break
                        else:
                            continue
                        break
                    else:
                        # Si no se encuentra una parada alternativa, marcar la parada para su eliminación
                        stops_to_remove.append(one_route.stops[i])  # Añade esta línea

                # Añadir la parada a las paradas visitadas
                seen_stops.add(one_route.stops[i])

            # Eliminar las paradas marcadas para su eliminación
            for stop in stops_to_remove:  # Añade este bucle
                one_route.stops.remove(stop)

        # Eliminar las rutas vacías
        child = [route for route in child if route.stops]

        # Devolver las soluciones reparadas
        return child

