import random

from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.operators.initial_solution.route_generation.restrictions.route_generator_restriction import \
    RouteGeneratorRestriction
from src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.route_generator_strategy import \
    RouteGeneratorStrategy
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class HClosestNeighborRouteGeneratorStrategy(RouteGeneratorStrategy):
    def generate_route(self, problem: ProblemSBRP,  distance_operator: DistanceOperator):
        # Inicializa una ruta compuesta por una lista vacía de stops
        route = Route()

        # Obtiene una copia de las paradas que no han sido asignadas
        non_assign_stops = RouteGeneratorRestriction.get_non_assign_stops(problem)

        # Inicializa un contador para la capacidad del autobús
        bus_capacity = problem.bus_capacity

        # Selecciona una parada aleatoria de las paradas disponibles como primera parada
        if not non_assign_stops:
            route.stops.insert(0, problem.school)
            route.stops.append(problem.school)
            return route
        first_stop = random.choice(non_assign_stops)
        route.stops.append(first_stop)
        route.students += first_stop.num_assigned_students
        bus_capacity -= first_stop.num_assigned_students
        first_stop.is_assigned = True
        non_assign_stops.remove(first_stop)

        # Mientras haya paradas disponibles y capacidad en el autobús
        while non_assign_stops and bus_capacity > 0:
            # Filtra las paradas disponibles para incluir solo aquellas que tienen un número de estudiantes que no
            # excede la capacidad del autobús
            feasible_stops = RouteGeneratorRestriction.get_non_exceed_bus_capacity(non_assign_stops, bus_capacity)

            # Si no hay paradas factibles, rompe el bucle
            if not feasible_stops:
                break

            # Selecciona la parada más cercana a la última parada de la ruta
            stop = min(feasible_stops, key=lambda s: distance_operator.calculate_distance(route.stops[-1].coordinates,
                                                                                          s.coordinates))

            # Agrega la parada a la ruta
            route.stops.append(stop)
            route.students += stop.num_assigned_students

            # Actualiza la capacidad del autobús
            bus_capacity -= stop.num_assigned_students

            # Actualiza el estado de la parada
            stop.is_assigned = True

            # Elimina la parada de la lista de paradas disponibles
            non_assign_stops.remove(stop)

        # Asegura de que la ruta comienza y termina en la escuela
        route.stops.insert(0, problem.school)
        route.stops.append(problem.school)
        return route
