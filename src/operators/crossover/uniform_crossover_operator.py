import random

from src.operators.crossover.crossover_operator import CrossoverOperator


class UniformCrossoverOperator(CrossoverOperator):
    def crossover(self, solution1, solution2):
        # Obtiene las representaciones de las soluciones
        parent1 = solution1.get_representation()
        parent2 = solution2.get_representation()

        child1_repr = []
        child2_repr = []
        for gene1, gene2 in zip(parent1, parent2):
            if random.random() < 0.5:
                child1_repr.append(gene1)
                child2_repr.append(gene2)
            else:
                child1_repr.append(gene2)
                child2_repr.append(gene1)

        # Crea nuevas soluciones para los hijos
        child1 = solution1.__class__()
        child1.set_representation(child1_repr)
        child2 = solution2.__class__()
        child2.set_representation(child2_repr)

        return child1, child2
