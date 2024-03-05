import random

from src.model.route import Route
from src.model.sbrp import SBRP


class RouteGenerator:

    @staticmethod
    def generate_route(sbrp: SBRP):
        # Inicializa una ruta compuesta por una lista vacía de stops
        route = Route(bus=None)

        # Obtiene una copia de las paradas que tienen al menos un estudiante y no han sido asignadas
        available_stops = [stop for stop in sbrp.stops if stop.num_assigned_students > 0 and stop.is_assigned is False]
        # Inicializa un contador para la capacidad del autobús
        bus_capacity = sbrp.bus_capacity

        # Mientras haya paradas disponibles y capacidad en el autobús
        while available_stops and bus_capacity > 0:
            # Filtra las paradas disponibles para incluir solo aquellas que tienen un número de estudiantes que no excede la capacidad del autobús
            feasible_stops = [stop for stop in available_stops if stop.num_assigned_students <= bus_capacity]

            # Si no hay paradas factibles, rompe el bucle
            if not feasible_stops:
                break

            # Selecciona una parada aleatoria de las paradas disponibles
            stop = random.choice(feasible_stops)

            # Agrega la parada a la ruta
            route.stops.append(stop)
            route.students += stop.num_assigned_students

            # Actualiza la capacidad del autobús
            bus_capacity -= stop.num_assigned_students

            # Actualiza el estado de la parada
            stop.is_assigned = True

            # Elimina la parada de la lista de paradas disponibles
            available_stops.remove(stop)

        # Asegura de que la ruta comienza y termina en la escuela
        route.stops.insert(0, sbrp.school)
        route.stops.append(sbrp.school)
        return route

    @staticmethod
    def generate_routes(sbrp):
        routes = []
        for _ in sbrp.buses:
            route = RouteGenerator.generate_route(sbrp)
            routes.append(route)

        return routes
