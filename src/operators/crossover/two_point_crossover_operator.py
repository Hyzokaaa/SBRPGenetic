import random

from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.solution.solution import Solution


class TwoPointCrossoverOperator(CrossoverOperator):
    def crossover(self, parameters: CrossoverParameters):
        parent1, parent2 = parameters.parent1.get_representation(), parameters.parent2.get_representation()

        size = min(len(parent1), len(parent2))
        cxpoint1 = random.randint(1, size)
        cxpoint2 = random.randint(1, size)
        if cxpoint2 < cxpoint1:
            cxpoint1, cxpoint2 = cxpoint2, cxpoint1

        child1_repr = parent1[:cxpoint1] + parent2[cxpoint1:cxpoint2] + parent1[cxpoint2:]
        child2_repr = parent2[:cxpoint1] + parent1[cxpoint1:cxpoint2] + parent2[cxpoint2:]

        # Convierte las representaciones de los hijos en instancias de Solution
        child1 = Solution()  # Reemplaza 'Solution' con la clase de solución que estés utilizando
        child1.set_representation(child1_repr)
        child2 = Solution()  # Reemplaza 'Solution' con la clase de solución que estés utilizando
        child2.set_representation(child2_repr)

        return child1, child2
