from abc import ABC, abstractmethod

from src.problems.problem_parameters import ProblemParameters


class Problem(ABC):
    @abstractmethod
    def construct(self, problem_parameters: ProblemParameters):
        pass

    @abstractmethod
    def objective_function(self, solution):
        pass

    @abstractmethod
    def violations(self, solution):
        pass

    def constraint_violation(self, solution):
        """
        Grado de violación de restricciones (0 si la solución es factible).
        Por defecto el problema no tiene restricciones.
        """
        return 0

    def solution_signature(self, solution):
        """
        Representación canónica de la solución para detectar duplicados en la población.
        None desactiva el control de duplicados.
        """
        return None

    def freeze(self, solution, signature=None):
        """
        Indica que la solución ya no se modificará (por ejemplo, porque entró en la población), para que el problema
        pueda guardar su evaluación con ella. Por defecto no hace nada.
        """

    @abstractmethod
    def compare_solutions(self, solution1, solution2, objective_max):
        pass

    @abstractmethod
    def update_best_solution(self, best_iteration, current_iteration, objective_max, population):
        pass
