from src.operators.replacement.replacement_operator import ReplacementOperator
from src.operators.replacement.replacement_parameters import ReplacementParameters


class GenerationalReplacementOperator(ReplacementOperator):
    """
    Reemplazo generacional con elitismo: las elitism_size mejores soluciones distintas pasan intactas y los hijos
    completan la nueva generación en el orden en que se producen.
    """

    def begin(self, population: list, parameters: ReplacementParameters):
        self.new_population = self.select_elite(population, parameters)
        for solution in self.new_population:
            self._register(solution)

    def is_full(self) -> bool:
        return len(self.new_population) >= self.population_size

    def add_child(self, child):
        self.new_population.append(child)
        self._register(child)

    def result(self) -> list:
        return self.new_population

    @classmethod
    def select_elite(cls, population: list, parameters: ReplacementParameters) -> list:
        """
        Copias de las elitism_size mejores soluciones distintas de la población, según las reglas de
        factibilidad: primero las factibles (menor grado de violación) y, entre ellas, la de mejor aptitud.
        """
        problem = parameters.problem
        ranked = sorted(population, key=lambda solution: cls.ranking_key(solution, parameters))

        elite, signatures = [], set()
        for solution in ranked:
            if len(elite) >= parameters.elitism_size:
                break
            signature = problem.solution_signature(solution)
            if signature is not None and signature in signatures:
                continue
            elite.append(solution.copy())
            signatures.add(signature)
        return elite
