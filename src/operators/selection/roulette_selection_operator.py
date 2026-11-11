import random

from src.operators.selection.selection_operator import SelectionOperator
from src.operators.selection.selection_parameters import SelectionParameters

MIN_WEIGHT = 1e-9


class RouletteSelectionOperator(SelectionOperator):
    def selection(self, parameters: SelectionParameters):
        """
        Selección proporcional a la aptitud respetando la factibilidad:
        - Se seleccionan primero soluciones factibles, con probabilidad proporcional a su aptitud.
        - Si no hay suficientes factibles, se completa con infactibles, con probabilidad inversamente
          proporcional a su grado de violación.
        No se selecciona dos veces el mismo individuo.
        """
        problem = parameters.problem
        number = parameters.number_of_selected_solutions
        feasible = [s for s in parameters.solutions if problem.constraint_violation(s) == 0]
        infeasible = [s for s in parameters.solutions if problem.constraint_violation(s) > 0]

        selected_solutions = self._spin(feasible, [self._fitness_weight(s, parameters) for s in feasible], number)
        if len(selected_solutions) < number:
            weights = [1 / (1 + problem.constraint_violation(s)) for s in infeasible]
            selected_solutions += self._spin(infeasible, weights, number - len(selected_solutions))
        return selected_solutions

    @staticmethod
    def _spin(candidates, weights, number):
        candidates, weights = list(candidates), list(weights)
        selected = []
        for _ in range(min(number, len(candidates))):
            index = random.choices(range(len(candidates)), weights=weights)[0]
            selected.append(candidates.pop(index))
            weights.pop(index)
        return selected

    @staticmethod
    def _fitness_weight(solution, parameters: SelectionParameters) -> float:
        fitness = parameters.problem.objective_function(solution)
        if parameters.objective_max:
            return max(fitness, MIN_WEIGHT)
        return 1 / max(fitness, MIN_WEIGHT)
