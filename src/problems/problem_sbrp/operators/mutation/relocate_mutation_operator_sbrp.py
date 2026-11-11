import random

from src.operators.mutation.mutation_operator import MutationOperator
from src.operators.mutation.mutation_parameters import MutationParameters
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.operators.insertion.cheapest_insertion import CheapestInsertion
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


class RelocateMutationOperatorSBRP(MutationOperator):
    """
    Mueve una parada al azar a otra ruta elegida al azar entre las que tienen capacidad disponible
    (o a una ruta nueva si la flota lo permite), insertándola en la posición de menor costo.
    """

    def mutate(self, parameters: MutationParameters):
        problem: ProblemSBRP = parameters.problem
        solution: SolutionRouteSBRP = parameters.solution
        routes = [[stop for stop in route.stops if not isinstance(stop, School)] for route in solution.get_representation()]
        routes = [stops for stops in routes if stops]
        if not routes:
            return solution

        # Selecciona una parada al azar
        origin = random.choice(routes)
        stop = random.choice(origin)

        # Rutas destino con capacidad disponible; una ruta nueva es una opción si la flota lo permite
        targets = [stops for stops in routes
                   if stops is not origin and CheapestInsertion.load(stops) + stop.num_assigned_students <= problem.bus_capacity]
        if len(routes) < len(problem.vehicles) and len(origin) > 1:
            targets.append([])
        if not targets:
            return solution

        target = random.choice(targets)
        origin.remove(stop)
        CheapestInsertion.insert([target], stop, problem)
        if not any(target is stops for stops in routes):
            routes.append(target)

        solution.set_representation([self._build_route(stops, problem) for stops in routes if stops])
        return solution

    @staticmethod
    def _build_route(stops, problem: ProblemSBRP) -> Route:
        route = Route(stops=[problem.school] + stops + [problem.school])
        route.students = CheapestInsertion.load(stops)
        return route
