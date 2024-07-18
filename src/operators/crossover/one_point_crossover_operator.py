import random

from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.operators.operator_parameters import OperatorParameters
from src.solution.solution import Solution


class OnePointCrossoverOperator(CrossoverOperator):
    def crossover(self, parameters: CrossoverParameters):
        parent1, parent2 = parameters.parent1.get_representation(), parameters.parent2.get_representation()

        # Genera un punto de cruce aleatorio
        size = min(len(parent1), len(parent2))
        cxpoint = random.randint(1, size)

        # Crea los hijos con las partes de los padres
        child1_repr = parent1[:cxpoint] + parent2[cxpoint:]
        child2_repr = parent2[:cxpoint] + parent1[cxpoint:]

        # Convierte las representaciones de los hijos en instancias de Solution
        child1 = Solution()  # Reemplaza 'Solution' con la clase de solución que estés utilizando
        child1.set_representation(child1_repr)
        child2 = Solution()  # Reemplaza 'Solution' con la clase de solución que estés utilizando
        child2.set_representation(child2_repr)

        return child1, child2
