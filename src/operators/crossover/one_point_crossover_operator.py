import random

from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.operators.operator_parameters import OperatorParameters


class OnePointCrossoverOperator(CrossoverOperator):
    def crossover(self, parameters: CrossoverParameters):
        parent1, parent2 = parameters.parent1, parameters.parent2

        # Genera un punto de cruce aleatorio
        size = min(len(parent1), len(parent2))
        cxpoint = random.randint(1, size)

        # Crea los hijos con las partes de los padres
        child1 = parent1[:cxpoint] + parent2[cxpoint:]
        child2 = parent2[:cxpoint] + parent1[cxpoint:]

        return child1, child2
