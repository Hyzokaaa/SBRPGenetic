import importlib
import random
from typing import List

from src.operators.mutation.mutation_operator import MutationOperator
from src.operators.mutation.mutation_parameters import MutationParameters

DEFAULT_OPERATORS = [
    "SWAP_MUTATION_OPERATOR_SBRP",
    "REORDER_SEGMENT_MUTATION_OPERATOR_SBRP",
    "RELOCATE_MUTATION_OPERATOR_SBRP",
    "EXCHANGE_MUTATION_OPERATOR_SBRP",
]


class CompositeMutationOperatorSBRP(MutationOperator):
    """
    Aplica en cada mutación uno de los operadores indicados, elegido al azar.
    Permite combinar mutaciones dentro de una ruta y entre rutas.
    """

    def __init__(self, operators: List[str] = None):
        # Importación diferida para evitar dependencias circulares con el enumerado de operadores
        from src.problems.problem_sbrp.algorithm.genetic_algorithm.operators_enum import Operators

        self.operators = []
        for name in operators if operators is not None else DEFAULT_OPERATORS:
            module_name, class_name = Operators[name].value.rsplit('.', 1)
            self.operators.append(getattr(importlib.import_module(module_name), class_name)())

    def mutate(self, parameters: MutationParameters):
        return random.choice(self.operators).mutate(parameters)
