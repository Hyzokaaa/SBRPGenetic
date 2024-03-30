import random

from src.operators.crossover.crossover_operator import CrossoverOperator


class TwoPointCrossoverOperator(CrossoverOperator):
    def crossover(self, solution1, solution2):
        # Obtiene las representaciones de las soluciones
        parent1 = solution1.get_representation()
        parent2 = solution2.get_representation()

        size = min(len(parent1), len(parent2))
        cxpoint1 = random.randint(1, size)
        cxpoint2 = random.randint(1, size)
        if cxpoint2 < cxpoint1:
            cxpoint1, cxpoint2 = cxpoint2, cxpoint1

        child1_repr = parent1[:cxpoint1] + parent2[cxpoint1:cxpoint2] + parent1[cxpoint2:]
        child2_repr = parent2[:cxpoint1] + parent1[cxpoint1:cxpoint2] + parent2[cxpoint2:]

        # Crea nuevas soluciones para los hijos
        child1 = solution1.__class__()
        child1.set_representation(child1_repr)
        child2 = solution2.__class__()
        child2.set_representation(child2_repr)

        return child1, child2
