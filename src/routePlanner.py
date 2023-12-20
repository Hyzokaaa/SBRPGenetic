import random
from typing import List

from src.stop import Stop


class RoutePlanner:

    @staticmethod
    def generate_route(sbrp):
        # Inicializa una lista vacía para la ruta
        route = []

        # Obtiene una copia de las paradas que tienen al menos un estudiante
        available_stops = [stop for stop in sbrp.stops if stop.num_assigned_students > 0]

        # Inicializa un contador para la capacidad del autobús
        bus_capacity = sbrp.bus_capacity

        # Mientras haya paradas disponibles y capacidad en el autobús
        while available_stops and bus_capacity > 0:
            # Filtra las paradas disponibles para incluir solo aquellas que tienen un número de estudiantes que no excede la capacidad del autobús
            feasible_stops = [stop for stop in available_stops if stop.num_assigned_students <= bus_capacity]

            # Si no hay paradas factibles, rompe el bucle
            if not feasible_stops:
                break

            # Selecciona una parada aleatoria de las paradas factibles
            stop = random.choice(feasible_stops)

            # Agrega la parada a la ruta
            route.append(stop)

            # Actualiza la capacidad del autobús
            bus_capacity -= stop.num_assigned_students

            # Actualiza el número de estudiantes asignados a la parada
            stop.num_assigned_students = 0

            # Elimina la parada de la lista de paradas disponibles
            available_stops.remove(stop)

        # Asegúrate de que la ruta comienza y termina en la escuela
        route.insert(0, sbrp.school)
        route.append(sbrp.school)
        return route

    @staticmethod
    def generate_routes(sbrp):
        # Inicializa una lista vacía para las rutas
        routes = []

        # Para cada autobús en el SBRP
        for _ in sbrp.routes:
            # Genera una ruta
            route = RoutePlanner.generate_route(sbrp)

            # Agrega la ruta generada a la lista de rutas
            routes.append(route)

        return routes