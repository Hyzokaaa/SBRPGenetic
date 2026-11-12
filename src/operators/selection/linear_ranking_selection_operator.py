import random

from src.operators.selection.selection_operator import SelectionOperator
from src.operators.selection.selection_parameters import SelectionParameters
from src.operators.selection.tournament_selection_operator import TournamentSelectionOperator


class LinearRankingSelectionOperator(SelectionOperator):
    """
    Selección por ranking lineal (Baker, 1985): la probabilidad de ser elegido depende solo de la posición en el
    ranking (reglas de factibilidad de Deb), no de la diferencia de aptitud. Con N individuos, el mejor tiene
    probabilidad pressure/N y el peor (2 - pressure)/N, variando linealmente entre ambos. pressure en [1, 2]:
    1 = selección uniforme; 2 = máxima presión (el peor nunca es elegido). No repite individuos.
    """

    def __init__(self, pressure: float = 1.5):
        if not 1 <= pressure <= 2:
            raise ValueError("pressure debe estar entre 1 y 2")
        self.pressure = pressure

    def selection(self, parameters: SelectionParameters):
        ranked = sorted(parameters.solutions,
                        key=lambda solution: TournamentSelectionOperator._ranking_key(solution, parameters))
        size = len(ranked)
        if size == 1:
            return ranked[:parameters.number_of_selected_solutions]
        # Posición 0 = el mejor
        weights = [(2 - self.pressure) / size + 2 * (size - 1 - position) * (self.pressure - 1) / (size * (size - 1))
                   for position in range(size)]
        selected = []
        for _ in range(min(parameters.number_of_selected_solutions, size)):
            index = random.choices(range(len(ranked)), weights=weights)[0] if sum(weights) > 0 \
                else random.randrange(len(ranked))
            selected.append(ranked.pop(index))
            weights.pop(index)
        return selected
