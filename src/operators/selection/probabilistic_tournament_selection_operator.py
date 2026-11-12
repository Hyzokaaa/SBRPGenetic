import random

from src.operators.selection.selection_parameters import SelectionParameters
from src.operators.selection.tournament_selection_operator import TournamentSelectionOperator


class ProbabilisticTournamentSelectionOperator(TournamentSelectionOperator):
    """
    Torneo que, con probabilidad random_probability, elige el padre al azar en lugar de por torneo. Así entran
    ocasionalmente individuos que un torneo grande no elegiría nunca, lo que reduce la presión de selección sin
    renunciar a ella. Con random_probability = 0 es el torneo normal; con 1, la selección aleatoria.
    """

    def __init__(self, random_probability: float = 0.2):
        if not 0 <= random_probability <= 1:
            raise ValueError("random_probability debe estar entre 0 y 1")
        self.random_probability = random_probability

    def selection(self, parameters: SelectionParameters):
        selected_solutions = []
        population_copy = parameters.solutions.copy()
        for _ in range(min(parameters.number_of_selected_solutions, len(population_copy))):
            if random.random() < self.random_probability:
                winner = random.choice(population_copy)
            else:
                tournament = random.sample(population_copy, min(parameters.tournament_size, len(population_copy)))
                winner = min(tournament, key=lambda solution: self._ranking_key(solution, parameters))
            selected_solutions.append(winner)
            population_copy.remove(winner)
        return selected_solutions
