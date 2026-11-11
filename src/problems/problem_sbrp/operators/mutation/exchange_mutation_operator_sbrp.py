import random

from src.operators.mutation.mutation_operator import MutationOperator
from src.operators.mutation.mutation_parameters import MutationParameters
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP

MAX_ATTEMPTS = 10


class ExchangeMutationOperatorSBRP(MutationOperator):
    """
    Intercambia dos paradas de rutas distintas, elegidas al azar, ocupando cada una la posición de la otra.
    Solo se aplica si ambas rutas respetan la capacidad tras el intercambio (hasta MAX_ATTEMPTS intentos).
    """

    def mutate(self, parameters: MutationParameters):
        problem: ProblemSBRP = parameters.problem
        solution: SolutionRouteSBRP = parameters.solution
        routes = [route for route in solution.get_representation()
                  if any(not isinstance(stop, School) for stop in route.stops)]
        if len(routes) < 2:
            return solution

        for _ in range(MAX_ATTEMPTS):
            route1, route2 = random.sample(routes, 2)
            positions1 = [i for i, stop in enumerate(route1.stops) if not isinstance(stop, School)]
            positions2 = [i for i, stop in enumerate(route2.stops) if not isinstance(stop, School)]
            i, j = random.choice(positions1), random.choice(positions2)
            stop1, stop2 = route1.stops[i], route2.stops[j]

            load1 = self._load(route1) - stop1.num_assigned_students + stop2.num_assigned_students
            load2 = self._load(route2) - stop2.num_assigned_students + stop1.num_assigned_students
            if load1 <= problem.bus_capacity and load2 <= problem.bus_capacity:
                route1.stops = route1.stops[:i] + [stop2] + route1.stops[i + 1:]
                route2.stops = route2.stops[:j] + [stop1] + route2.stops[j + 1:]
                route1.students, route2.students = load1, load2
                break

        return solution

    @staticmethod
    def _load(route) -> int:
        return sum(stop.num_assigned_students for stop in route.stops if not isinstance(stop, School))
