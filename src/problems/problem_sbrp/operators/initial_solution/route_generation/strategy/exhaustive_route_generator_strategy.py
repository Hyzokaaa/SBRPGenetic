import itertools

from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.operators.initial_solution.route_generation.restrictions.route_generator_restriction import \
    RouteGeneratorRestriction
from src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.route_generator_strategy import \
    RouteGeneratorStrategy
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class ExhaustiveRouteGeneratorStrategy(RouteGeneratorStrategy):
    def generate_route(self, problem: ProblemSBRP,  distance_operator: DistanceOperator):
        # Inicializa una lista para almacenar todas las rutas factibles
        all_feasible_routes = []

        # Obtiene una copia de las paradas que no han sido asignadas
        non_assign_stops = RouteGeneratorRestriction.get_non_assign_stops_with_students(problem)

        # Inicializa un contador para la capacidad del autobús
        bus_capacity = problem.bus_capacity

        # Genera todas las posibles combinaciones de paradas que no exceden la capacidad del autobús
        all_combinations = self.generate_all_combinations(non_assign_stops, bus_capacity)

        # Itera sobre todas las combinaciones posibles
        for stops in all_combinations:
            # Crea una ruta con las paradas de la combinación actual
            temp_route = Route(stops=stops)

            # Si la ruta es factible (i.e., no excede la capacidad del autobús), la agrega a la lista de rutas factibles
            if self.is_route_feasible(temp_route, bus_capacity):
                all_feasible_routes.append(temp_route)

        return all_feasible_routes

    @staticmethod
    def generate_all_combinations(stops, bus_capacity):
        # Genera todas las posibles combinaciones de paradas que no exceden la capacidad del autobús
        all_combinations = []
        for r in range(1, len(stops) + 1):
            for permutations in itertools.permutations(stops, r):
                if sum(stop.num_assigned_students for stop in permutations) <= bus_capacity:
                    all_combinations.append(list(permutations))
        return all_combinations

    @staticmethod
    def is_route_feasible(route, bus_capacity):
        # Verifica si la ruta es factible (i.e., no excede la capacidad del autobús)
        return sum(stop.num_assigned_students for stop in route.stops) <= bus_capacity
