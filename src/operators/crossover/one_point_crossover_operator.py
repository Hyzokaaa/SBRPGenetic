import random

from src.operators.crossover.crossover_operator import CrossoverOperator


class OnePointCrossoverOperator(CrossoverOperator):
    def crossover(self, solution1, solution2):
        # Obtiene las representaciones de las soluciones
        parent1 = solution1.get_representation()
        parent2 = solution2.get_representation()

        # Genera un punto de cruce aleatorio
        size = min(len(parent1), len(parent2))
        cxpoint = random.randint(1, size)

        # Crea los hijos con las partes de los padres
        child1_repr = parent1[:cxpoint] + parent2[cxpoint:]
        child2_repr = parent2[:cxpoint] + parent1[cxpoint:]

        # Crea nuevas soluciones para los hijos
        child1 = solution1.__class__()  # Crea una nueva instancia de la misma clase que solution1
        child1.set_representation(child1_repr)
        child2 = solution2.__class__()  # Crea una nueva instancia de la misma clase que solution2
        child2.set_representation(child2_repr)

        return child1, child2
