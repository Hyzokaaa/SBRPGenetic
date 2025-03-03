import random

from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP
from src.solution.solution import Solution


class UniformCrossoverOperator(CrossoverOperator):
    def crossover(self, parameters: CrossoverParameters):
        parent1, parent2 = parameters.parent1.get_representation(), parameters.parent2.get_representation()

        child1_repr = []
        child2_repr = []
        for gene1, gene2 in zip(parent1, parent2):
            if random.random() < 0.5:
                child1_repr.append(gene1)
                child2_repr.append(gene2)
            else:
                child1_repr.append(gene2)
                child2_repr.append(gene1)

        # Convierte las representaciones de los hijos en instancias de Solution
        child1 = SolutionRouteSBRP()  # Reemplaza 'Solution' con la clase de solución que estés utilizando
        child1.set_representation(child1_repr)
        child2 = SolutionRouteSBRP()  # Reemplaza 'Solution' con la clase de solución que estés utilizando
        child2.set_representation(child2_repr)

        return child1, child2
