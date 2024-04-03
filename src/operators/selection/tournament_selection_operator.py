import random

from src.operators.selection.selection_operator import SelectionOperator
from src.operators.selection.selection_parameters import SelectionParameters


class TournamentSelectionOperator(SelectionOperator):
    def selection(self, parameters: SelectionParameters):
        selected_solutions = []
        population_copy = parameters.solutions.copy()
        for _ in range(parameters.number_of_selected_solutions):
            # Selecciona al azar un subconjunto de la población
            tournament = random.sample(population_copy, parameters.tournament_size)
            # Elige al individuo con la mayor o menor aptitud del torneo, dependiendo del valor de objective_max
            if parameters.objective_max:
                winner = max(tournament, key=parameters.problem.objective_function)
            else:
                winner = min(tournament, key=parameters.problem.objective_function)
            selected_solutions.append(winner)
            population_copy.remove(winner)
        return selected_solutions
