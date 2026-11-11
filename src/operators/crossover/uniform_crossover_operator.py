import random

from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


class UniformCrossoverOperator(CrossoverOperator):
    def crossover(self, parameters: CrossoverParameters):
        parent1, parent2 = parameters.parent1.get_representation(), parameters.parent2.get_representation()

        child1_repr = []
        child2_repr = []
        for gene1, gene2 in zip(parent1, parent2):
            if random.random() < 0.5:
                gene1, gene2 = gene2, gene1
            # Copias de las rutas para no compartirlas con los padres
            child1_repr.append(Route(stops=list(gene1.stops)))
            child2_repr.append(Route(stops=list(gene2.stops)))

        return SolutionRouteSBRP(routes=child1_repr), SolutionRouteSBRP(routes=child2_repr)
