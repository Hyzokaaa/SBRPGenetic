from src.operators.diversity.diversity_operator import DiversityOperator
from src.operators.diversity.diversity_parameters import DiversityParameters


class CataclysmicRestartOperator(DiversityOperator):
    """
    Reinicio cataclísmico (Eshelman, CHC 1991): cada stagnation generaciones seguidas sin mejora, conserva la élite
    y regenera el resto de la población: una parte como copias de la mejor solución mutadas mutations veces y el resto
    (fraction_new) como soluciones nuevas de la construcción inicial.
    """

    def __init__(self, stagnation: int = 10, mutations: int = 5, fraction_new: float = 0.5):
        if stagnation < 1 or mutations < 1 or not 0 <= fraction_new <= 1:
            raise ValueError("stagnation y mutations deben ser >= 1 y fraction_new estar en [0, 1]")
        self.stagnation = stagnation
        self.mutations = mutations
        self.fraction_new = fraction_new

    def apply(self, population: list, parameters: DiversityParameters) -> list:
        if not self.triggered(parameters, self.stagnation):
            return population
        ranked = self.ranked_indices(population, parameters)
        elite = self.elite_indices(population, parameters)
        best = population[ranked[0]]
        rest = [i for i in range(len(population)) if i not in elite]
        new_count = round(self.fraction_new * len(rest))
        population = list(population)
        for position, index in enumerate(rest):
            if position < new_count:
                population[index] = parameters.construct()
            else:
                mutant = best.copy()
                for _ in range(self.mutations):
                    parameters.mutate(mutant)
                population[index] = mutant
        return population
