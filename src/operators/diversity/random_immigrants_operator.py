from src.operators.diversity.diversity_operator import DiversityOperator
from src.operators.diversity.diversity_parameters import DiversityParameters


class RandomImmigrantsOperator(DiversityOperator):
    """
    Inmigrantes aleatorios (Grefenstette, 1992): cada stagnation generaciones seguidas sin mejora, sustituye la
    fracción fraction de peores soluciones por soluciones nuevas de la construcción inicial. Aporta material genético
    nuevo sin perder lo bueno: la élite nunca se sustituye.
    """

    def __init__(self, stagnation: int = 5, fraction: float = 0.3):
        if stagnation < 1 or not 0 < fraction <= 1:
            raise ValueError("stagnation debe ser >= 1 y fraction estar en (0, 1]")
        self.stagnation = stagnation
        self.fraction = fraction

    def apply(self, population: list, parameters: DiversityParameters) -> list:
        if not self.triggered(parameters, self.stagnation):
            return population
        elite = self.elite_indices(population, parameters)
        candidates = [i for i in reversed(self.ranked_indices(population, parameters)) if i not in elite]
        population = list(population)
        for index in candidates[:round(self.fraction * len(population))]:
            population[index] = parameters.construct()
        return population
