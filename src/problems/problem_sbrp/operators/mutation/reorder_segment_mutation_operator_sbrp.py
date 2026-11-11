import random

from src.operators.mutation.mutation_operator import MutationOperator
from src.operators.mutation.mutation_parameters import MutationParameters
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP

SEGMENT_SIZE = 5


class ReorderSegmentMutationOperatorSBRP(MutationOperator):
    def mutate(self, parameters: MutationParameters):
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

            # Reordena aleatoriamente las paradas del segmento
            segment = [route.stops[i] for i in segment_positions]
            random.shuffle(segment)

            # Escribe el segmento reordenado en las mismas posiciones de la ruta
            route_stops = route.stops.copy()
            for position, stop in zip(segment_positions, segment):
                route_stops[position] = stop
            route.stops = route_stops

        return solution
