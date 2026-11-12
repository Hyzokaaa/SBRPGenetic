from src.analysis.metrics import solution_edges
from src.operators.diversity.diversity_operator import DiversityOperator
from src.operators.diversity.diversity_parameters import DiversityParameters


class ClearingOperatorSBRP(DiversityOperator):
    """
    Clearing (Pétrowski, 1996), aplicado en cada generación: recorre la población de la mejor a la peor solución y
    sustituye por una solución nueva de la construcción inicial a cada individuo demasiado parecido a otro mejor ya
    conservado (distancia de Jaccard entre sus aristas menor que min_distance). Evita que la población se llene de
    variantes de la misma solución. La mejor solución siempre se conserva.
    """

    def __init__(self, min_distance: float = 0.1):
        if not 0 < min_distance <= 1:
            raise ValueError("min_distance debe estar en (0, 1]")
        self.min_distance = min_distance

    def apply(self, population: list, parameters: DiversityParameters) -> list:
        kept_edges = []
        population = list(population)
        elite = self.elite_indices(population, parameters)
        for index in self.ranked_indices(population, parameters):
            edges = solution_edges(population[index])
            if index not in elite and any(self.distance(edges, other) < self.min_distance for other in kept_edges):
                population[index] = parameters.construct()
                continue
            kept_edges.append(edges)
        return population

    @staticmethod
    def distance(edges_a, edges_b) -> float:
        union = edges_a | edges_b
        return 1 - len(edges_a & edges_b) / len(union) if union else 0.0
