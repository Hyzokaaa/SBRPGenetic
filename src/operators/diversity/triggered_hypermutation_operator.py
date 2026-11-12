from src.operators.diversity.diversity_operator import DiversityOperator
from src.operators.diversity.diversity_parameters import DiversityParameters


class TriggeredHypermutationOperator(DiversityOperator):
    """
    Hipermutación activada (Cobb, 1990): cada stagnation generaciones seguidas sin mejora, multiplica la tasa de
    mutación por factor durante duration generaciones (o hasta que la mejor solución mejore). Explora alrededor de la
    población actual sin descartarla.
    """

    def __init__(self, stagnation: int = 5, factor: float = 4.0, duration: int = 3):
        if stagnation < 1 or factor < 1 or duration < 1:
            raise ValueError("stagnation y duration deben ser >= 1 y factor >= 1")
        self.stagnation = stagnation
        self.factor = factor
        self.duration = duration
        self.remaining = 0

    def apply(self, population: list, parameters: DiversityParameters) -> list:
        if parameters.stagnation == 0:
            self.remaining = 0                      # la mejor solución mejoró: vuelve la tasa normal
        elif self.remaining > 0:
            self.remaining -= 1
        if self.triggered(parameters, self.stagnation):
            self.remaining = self.duration
        return population

    @property
    def active(self) -> bool:
        return self.remaining > 0

    def mutation_rate(self, base_rate: float) -> float:
        return min(1.0, base_rate * self.factor) if self.active else base_rate
