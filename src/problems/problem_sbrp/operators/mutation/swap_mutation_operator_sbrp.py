import random

from src.operators.mutation.mutation_operator import MutationOperator
from src.operators.mutation.mutation_parameters import MutationParameters
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


class SwapMutationOperatorSBRP(MutationOperator):
    def mutate(self, parameters: MutationParameters):
        solution = parameters.solution
        if not isinstance(solution, SolutionRouteSBRP):
            raise TypeError("La solución debe ser de tipo SolutionRouteSBRP")

        routes = solution.get_representation()
        if not routes:
            return  # No hay rutas para mutar

        # Filtra las rutas que tienen al menos 4 paradas
        valid_routes = [route for route in routes if len(route.stops) >= 4]
        
        if not valid_routes:
            return  # No hay rutas válidas para mutar

        # Selecciona una ruta aleatoria de las rutas válidas
        route = random.choice(valid_routes)

        # Selecciona dos índices aleatorios diferentes (excluyendo el primero y el último)
        idx1, idx2 = random.sample(range(1, len(route.stops) - 1), 2)

        # Intercambia las paradas
        route.stops[idx1], route.stops[idx2] = route.stops[idx2], route.stops[idx1]

        # Actualiza la representación de la solución
        solution.set_representation(routes)

