from typing import Callable

from src.operators.operator_parameters import OperatorParameters


class DiversityParameters(OperatorParameters):
    """
    Estado de la ejecución que necesitan los operadores de diversidad. El algoritmo genético actualiza generation y
    stagnation (generaciones seguidas sin mejorar la mejor solución) antes de cada llamada.
    construct() devuelve una solución nueva (construcción inicial, reparada si hace falta) y mutate(s) muta s en el
    sitio con el operador de mutación de la configuración.
    """

    def __init__(self, problem, objective_max: bool = True, elitism_size: int = 1,
                 construct: Callable = None, mutate: Callable = None):
        super().__init__(problem)
        self.objective_max = objective_max
        self.elitism_size = elitism_size
        self.construct = construct
        self.mutate = mutate
        self.generation = 0
        self.stagnation = 0
