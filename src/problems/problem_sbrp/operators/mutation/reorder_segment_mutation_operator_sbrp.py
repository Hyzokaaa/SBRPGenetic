import itertools
import random
from typing import List

from src.operators.mutation.mutation_operator import MutationOperator
from src.operators.mutation.mutation_parameters import MutationParameters
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


class ReorderSegmentMutationOperatorSBRP(MutationOperator):
    def mutate(self, parameters: MutationParameters):
        problem: ProblemSBRP = parameters.problem
        solution: SolutionRouteSBRP = parameters.solution

        # Filtrar rutas con más de 3 paradas (excluyendo la escuela)
        routes = [route for route in solution.get_representation() if len(route.stops) > 3]
        if routes:
            # Selecciona una ruta al azar
            route = random.choice(routes)

            # Crea una copia de las paradas en la ruta (excluyendo la escuela)
            stops = [stop for stop in route.stops if not isinstance(stop, School)]

            # Si hay más de 5 paradas, selecciona un segmento de 5 paradas
            if len(stops) > 5:
                start = random.randint(0, len(stops) - 5)
                end = start + 5
                segment = stops[start:end]
            else:
                segment = stops

            # Genera todas las permutaciones posibles del segmento
            permutations = list(itertools.permutations(segment))

            # Calcula el costo de cada permutación
            costs = [
                sum(
                    parameters.distance_operator.calculate_distance(segment[i].coordinates, segment[i + 1].coordinates)
                    for i in range(len(segment) - 1)
                )
                for segment in permutations
            ]

            # Encuentra la permutación con el menor costo
            min_cost_index = costs.index(min(costs))
            min_cost_permutation = permutations[min_cost_index]

            # Reordena las paradas en el segmento de la ruta según la permutación con el menor costo
            # Ajusta los índices para tener en cuenta la escuela al inicio
            route_stops = route.stops.copy()
            school_start = route_stops[0]  # Guarda la escuela al inicio
            school_end = route_stops[-1]  # Guarda la escuela al final

            # Reemplaza el segmento en la ruta
            route_stops[1:1 + len(segment)] = min_cost_permutation

            # Asegura que la escuela esté al inicio y al final de la ruta
            route_stops[0] = school_start
            route_stops[-1] = school_end

            # Actualiza las paradas de la ruta
            route.stops = route_stops

        return solution