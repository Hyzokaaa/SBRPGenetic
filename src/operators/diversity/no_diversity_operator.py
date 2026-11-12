from src.operators.diversity.diversity_operator import DiversityOperator
from src.operators.diversity.diversity_parameters import DiversityParameters


class NoDiversityOperator(DiversityOperator):
    """No actúa: la diversidad solo depende de la selección, el cruce, la mutación y el reemplazo."""

    def apply(self, population: list, parameters: DiversityParameters) -> list:
        return population
