from abc import ABC, abstractmethod

from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class AssignmentImprovementOperator(ABC):
    """
    Mejora la asignación de estudiantes a paradas a partir de la mejor solución encontrada (sus rutas). Se aplica
    entre ejecuciones del algoritmo genético, nunca dentro: durante una ejecución la asignación es fija, porque todos
    los individuos de la población se evalúan con ella.
    """

    @abstractmethod
    def improve(self, problem: ProblemSBRP, distance_operator: DistanceOperator) -> int:
        """
        Cambia la asignación del problema y sustituye problem.best_solution por una solución factible que no es peor.
        Devuelve el número de cambios hechos (0 si no encontró ninguna mejora).
        """
