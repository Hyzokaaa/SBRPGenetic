import random

from src.model.route import Route


class RoutePlanner:

    @staticmethod
    def generate_route(sbrp):
        # Inicializa una lista vacía para la ruta
        route = Route(bus=None)

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
            route.stops.append(stop)

            # Actualiza la capacidad del autobús
            bus_capacity -= stop.num_assigned_students

            # Actualiza el número de estudiantes asignados a la parada
            stop.num_assigned_students = 0

            # Elimina la parada de la lista de paradas disponibles
            available_stops.remove(stop)

        # Asegúrate de que la ruta comienza y termina en la escuela
        route.stops.insert(0, sbrp.school)
        route.stops.append(sbrp.school)
        return route

    @staticmethod
    def generate_routes(sbrp):
        routes = []
        for _ in sbrp.buses:
            route = RoutePlanner.generate_route(sbrp)
            routes.append(route)
            # Imprime cada parada en la ruta generada
            print("Generated route:")
            for stop in route.stops:
                print(f"Stop ID: {stop.id}, Stop Coords: {stop.coord_x, stop.coord_y}")
        return routes
