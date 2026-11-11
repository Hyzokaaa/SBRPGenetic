import random
from typing import List

from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.operators.insertion.cheapest_insertion import CheapestInsertion
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


class BCRCCrossoverOperatorSBRP(CrossoverOperator):
    """
    Best Cost Route Crossover (Ombuki et al., 2006).
    Cada hijo parte de un padre, elimina las paradas de una ruta aleatoria del otro padre
    y las reinserta en la posición de menor costo con capacidad disponible.
    Las paradas que no quepan quedan fuera y las recupera el operador de reparación.
    """

    def crossover(self, parameters: CrossoverParameters):
        problem: ProblemSBRP = parameters.problem
        parent1, parent2 = parameters.parent1, parameters.parent2

        # Selecciona una ruta no vacía de cada padre
        route1 = self._select_route(parent1)
        route2 = self._select_route(parent2)

        # Cada hijo hereda la estructura de su padre y reinserta las paradas de la ruta del otro padre
        child1 = self._create_child(parent1, route2, problem)
        child2 = self._create_child(parent2, route1, problem)

        return child1, child2

    def _select_route(self, parent: SolutionRouteSBRP) -> List[Stop]:
        routes = [self._route_stops(route) for route in parent.get_representation()]
        routes = [stops for stops in routes if stops]
        return random.choice(routes) if routes else []

    def _create_child(self, parent: SolutionRouteSBRP, donor_route: List[Stop],
                      problem: ProblemSBRP) -> SolutionRouteSBRP:
        donor_ids = {stop.id for stop in donor_route}

        # Copia las rutas del padre sin las paradas de la ruta donante
        routes = [[stop for stop in self._route_stops(route) if stop.id not in donor_ids]
                  for route in parent.get_representation()]

        # Reinserta las paradas de la ruta donante en la posición de menor costo
        for stop in donor_route:
            CheapestInsertion.insert(routes, stop, problem)

        return SolutionRouteSBRP(routes=[Route(stops=[problem.school] + stops + [problem.school])
                                         for stops in routes])

    @staticmethod
    def _route_stops(route: Route) -> List[Stop]:
        return [stop for stop in route.stops if stop is not None and not isinstance(stop, School)]
