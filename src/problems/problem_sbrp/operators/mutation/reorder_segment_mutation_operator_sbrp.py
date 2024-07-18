import itertools
import random
from typing import List

from src.operators.mutation.mutation_operator import MutationOperator
from src.operators.mutation.mutation_parameters import MutationParameters
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


class ReorderSegmentMutationOperator(MutationOperator):
    def mutate(self, parameters: MutationParameters):
        problem: ProblemSBRP = parameters.problem
        routes: SolutionRouteSBRP = parameters.solution

        routes = [route for route in routes.get_representation() if len(route.stops) > 3]
        if routes:
            # Selecciona una ruta al azar
            route = random.choice(routes)

            # Crea una copia de las paradas en la ruta para poder iterar sobre ellas
            stops = [stop for stop in route.stops if not isinstance(stop, School)]

            # Define 'start' y 'end' antes del bloque 'if'
            start = 0
            end = len(stops)

            # Si hay más de 5 paradas, selecciona un segmento de 5 paradas
            if len(stops) > 5:
                start = random.randint(0, len(stops) - 5)
                end = start + 5
                stops: List[Stop] = stops[start:end]

            # Genera todas las permutaciones posibles del segmento
            permutations = list(itertools.permutations(stops))

            # Calcula el costo de cada permutación
            costs = [sum(parameters.distance_operator.calculate_distance(stops[i].coordinates, stops[i+1].coordinates)
                         for i in range(len(stops)-1)) for stops in permutations]

            # Encuentra la permutación con el menor costo
            min_cost_index = costs.index(min(costs))
            min_cost_permutation = permutations[min_cost_index]

            # Reordena las paradas en el segmento de la ruta según la permutación con el menor costo
            for i, stop in enumerate(min_cost_permutation):
                route.stops[start+i+1] = stop  # +1 para dejar la escuela al inicio

            # Asegura que la escuela esté al inicio y al final de la ruta
            school = [stop for stop in route.stops if isinstance(stop, School)][0]
            route.stops = [school] + route.stops[1:-1] + [school]

        return routes
