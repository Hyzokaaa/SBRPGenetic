import random

from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


class OnePointCrossoverOperator(CrossoverOperator):
    def crossover(self, parameters: CrossoverParameters):
        parent1, parent2 = parameters.parent1.get_representation(), parameters.parent2.get_representation()

        # Genera un punto de cruce aleatorio
        size = min(len(parent1), len(parent2))
        cxpoint = random.randint(1, size)

        # Crea los hijos con copias de las rutas de los padres
        child1_repr = [Route(stops=list(route.stops)) for route in parent1[:cxpoint] + parent2[cxpoint:]]
        child2_repr = [Route(stops=list(route.stops)) for route in parent2[:cxpoint] + parent1[cxpoint:]]

        return SolutionRouteSBRP(routes=child1_repr), SolutionRouteSBRP(routes=child2_repr)
