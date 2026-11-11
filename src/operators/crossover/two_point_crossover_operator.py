import random

from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


class TwoPointCrossoverOperator(CrossoverOperator):
    def crossover(self, parameters: CrossoverParameters):
        parent1, parent2 = parameters.parent1.get_representation(), parameters.parent2.get_representation()

        # Genera dos puntos de cruce aleatorios
        size = min(len(parent1), len(parent2))
        cxpoint1 = random.randint(1, size)
        cxpoint2 = random.randint(1, size)
        if cxpoint2 < cxpoint1:
            cxpoint1, cxpoint2 = cxpoint2, cxpoint1

        # Crea los hijos con copias de las rutas de los padres
        child1_repr = [Route(stops=list(route.stops))
                       for route in parent1[:cxpoint1] + parent2[cxpoint1:cxpoint2] + parent1[cxpoint2:]]
        child2_repr = [Route(stops=list(route.stops))
                       for route in parent2[:cxpoint1] + parent1[cxpoint1:cxpoint2] + parent2[cxpoint2:]]

        return SolutionRouteSBRP(routes=child1_repr), SolutionRouteSBRP(routes=child2_repr)
