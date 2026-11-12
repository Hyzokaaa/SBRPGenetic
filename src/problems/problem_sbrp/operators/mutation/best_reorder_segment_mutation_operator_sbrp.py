import itertools
import random

from src.operators.mutation.mutation_operator import MutationOperator
from src.operators.mutation.mutation_parameters import MutationParameters
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP

SEGMENT_SIZE = 5


class BestReorderSegmentMutationOperatorSBRP(MutationOperator):
    """
    Mejora local: selecciona un segmento de una ruta al azar y lo reordena según la permutación
    de menor costo, considerando también los tramos que lo enlazan con el resto de la ruta.
    Como el orden original es una de las permutaciones evaluadas, nunca empeora la ruta.

    No es una mutación en sentido estricto sino una búsqueda local: usado como operador de mutación,
    convierte el algoritmo genético en un algoritmo memético. Al no poder empeorar la ruta tampoco
    aporta diversidad, por lo que conviene combinarlo con una mutación aleatoria (p. ej. en el compuesto).
    """

    def mutate(self, parameters: MutationParameters):
        problem: ProblemSBRP = parameters.problem
        solution: SolutionRouteSBRP = parameters.solution

        # Filtrar rutas con más de 3 paradas (incluyendo la escuela)
        routes = [route for route in solution.get_representation() if len(route.stops) > 3]
        if routes:
            # Selecciona una ruta al azar
            route = random.choice(routes)

            # Posiciones de las paradas en la ruta (excluyendo la escuela)
            positions = [i for i, stop in enumerate(route.stops) if not isinstance(stop, School)]

            # Si hay más paradas que el tamaño del segmento, selecciona un segmento al azar
            start = random.randint(0, len(positions) - SEGMENT_SIZE) if len(positions) > SEGMENT_SIZE else 0
            segment_positions = positions[start:start + SEGMENT_SIZE]
            segment = [route.stops[i] for i in segment_positions]

            # Paradas que enlazan el segmento con el resto de la ruta (la escuela si está en un extremo)
            first, last = segment_positions[0], segment_positions[-1]
            previous_stop = route.stops[first - 1] if first > 0 else problem.school
            next_stop = route.stops[last + 1] if last + 1 < len(route.stops) else problem.school

            # Encuentra la permutación de menor costo, incluyendo los tramos de enlace
            best_permutation = min(
                itertools.permutations(segment),
                key=lambda permutation: self._path_cost(problem, [previous_stop, *permutation, next_stop])
            )

            # Escribe el segmento reordenado en las mismas posiciones de la ruta
            route_stops = route.stops.copy()
            for position, stop in zip(segment_positions, best_permutation):
                route_stops[position] = stop
            route.stops = route_stops

        return solution

    @staticmethod
    def _path_cost(problem: ProblemSBRP, stops):
        return sum(problem.distance_matrix[stops[i].id][stops[i + 1].id] for i in range(len(stops) - 1))
