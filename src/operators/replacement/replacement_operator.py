from abc import ABC, abstractmethod
from collections import Counter

from src.operators.replacement.replacement_parameters import ReplacementParameters


class ReplacementOperator(ABC):
    """
    Decide qué individuos forman la siguiente generación. El algoritmo genético produce familias (dos padres y sus
    hijos) mientras el operador no esté completo:

        start(población) → mientras no is_full(): por cada hijo, si wants_child(): add_child(hijo);
                           al terminar la familia, end_family(padres) → result()

    contains(firma) permite al algoritmo evitar hijos idénticos a individuos de la nueva población.
    """

    def start(self, population: list, parameters: ReplacementParameters):
        self.population_size = parameters.population_size
        self.parameters = parameters
        self.signatures = Counter()
        self.begin(population, parameters)

    @abstractmethod
    def begin(self, population: list, parameters: ReplacementParameters):
        """Prepara la nueva generación a partir de la población actual."""

    @abstractmethod
    def is_full(self) -> bool:
        """Si la nueva generación está completa."""

    def wants_child(self) -> bool:
        return not self.is_full()

    @abstractmethod
    def add_child(self, child):
        """Recibe un hijo ya mutado de la familia en curso."""

    def end_family(self, parents: list):
        """Se llama al terminar cada familia, con sus padres."""

    @abstractmethod
    def result(self) -> list:
        """La nueva generación."""

    def contains(self, signature) -> bool:
        return signature is not None and self.signatures[signature] > 0

    def _register(self, solution):
        self.signatures[self.parameters.problem.solution_signature(solution)] += 1

    def _unregister(self, solution):
        signature = self.parameters.problem.solution_signature(solution)
        self.signatures[signature] -= 1
        if self.signatures[signature] <= 0:
            del self.signatures[signature]

    @staticmethod
    def ranking_key(solution, parameters: ReplacementParameters):
        """Reglas de factibilidad de Deb: menor grado de violación y, a igualdad, mejor aptitud."""
        problem = parameters.problem
        fitness = problem.objective_function(solution)
        return problem.constraint_violation(solution), -fitness if parameters.objective_max else fitness
