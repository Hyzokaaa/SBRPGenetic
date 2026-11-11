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
            # Elige al ganador según las reglas de factibilidad (Deb, 2000)
            winner = min(tournament, key=lambda solution: self._ranking_key(solution, parameters))
            selected_solutions.append(winner)
            population_copy.remove(winner)
        return selected_solutions

    @staticmethod
    def _ranking_key(solution, parameters: SelectionParameters):
        """
        Una solución factible gana a una infactible; entre infactibles gana la de menor grado de violación;
        entre factibles gana la de mejor aptitud (mayor o menor, dependiendo del valor de objective_max).
        """
        fitness = parameters.problem.objective_function(solution)
        return parameters.problem.constraint_violation(solution), -fitness if parameters.objective_max else fitness
