import random

from src.operators.selection.selection_operator import SelectionOperator
from src.operators.selection.selection_parameters import SelectionParameters


class RandomSelectionOperator(SelectionOperator):
    """
    Selección uniforme al azar, sin presión de selección y sin repetir individuos. Pensada para combinarse con un
    reemplazo que ya aplica la presión, como el crowding determinista (Mahfoud, 1995).
    """

    def selection(self, parameters: SelectionParameters):
        number = min(parameters.number_of_selected_solutions, len(parameters.solutions))
        return random.sample(parameters.solutions, number)
