from abc import ABC, abstractmethod

from src.operators.diversity.diversity_parameters import DiversityParameters


class DiversityOperator(ABC):
    """
    Mantiene la diversidad de la población. Se aplica al final de cada generación y puede sustituir individuos
    (apply) o cambiar la tasa de mutación de la generación siguiente (mutation_rate). Nunca sustituye a la élite.
    """

    @abstractmethod
    def apply(self, population: list, parameters: DiversityParameters) -> list:
        """Devuelve la población, con los individuos sustituidos si corresponde."""

    def mutation_rate(self, base_rate: float) -> float:
        """Tasa de mutación para la siguiente generación (por defecto, la de la configuración)."""
        return base_rate

    @staticmethod
    def ranking_key(solution, parameters: DiversityParameters):
        """Reglas de factibilidad de Deb: menor grado de violación y, a igualdad, mejor aptitud."""
        problem = parameters.problem
        fitness = problem.objective_function(solution)
        return problem.constraint_violation(solution), -fitness if parameters.objective_max else fitness

    @classmethod
    def ranked_indices(cls, population: list, parameters: DiversityParameters) -> list:
        """Índices de la población de la mejor a la peor solución."""
        return sorted(range(len(population)), key=lambda i: cls.ranking_key(population[i], parameters))

    @classmethod
    def elite_indices(cls, population: list, parameters: DiversityParameters) -> set:
        """Índices de las elitism_size mejores soluciones (al menos la mejor), que no se sustituyen."""
        return set(cls.ranked_indices(population, parameters)[:max(1, parameters.elitism_size)])

    @staticmethod
    def triggered(parameters: DiversityParameters, stagnation: int) -> bool:
        """Si toca actuar: cada stagnation generaciones seguidas sin mejora (stagnation, 2·stagnation, ...)."""
        return parameters.stagnation > 0 and parameters.stagnation % stagnation == 0
