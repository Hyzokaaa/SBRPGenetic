import math

from src.analysis.metrics import solution_edges
from src.operators.replacement.replacement_operator import ReplacementOperator
from src.operators.replacement.replacement_parameters import ReplacementParameters


class DeterministicCrowdingReplacementOperatorSBRP(ReplacementOperator):
    """
    Crowding determinista (Mahfoud, 1995): cada hijo compite con el padre más parecido y ocupa su lugar en la
    población si no es peor (reglas de factibilidad de Deb). Como un hijo solo desplaza a su padre más parecido,
    las soluciones buenas pero distintas sobreviven y la población no se llena de variantes de una sola solución.

    La similitud es la distancia de Jaccard entre los conjuntos de aristas de las rutas. Los hijos se emparejan con
    los padres de la forma que minimiza la suma de distancias. La mejor solución nunca se pierde: un lugar solo
    cambia de ocupante por otro que no es peor. Se procesan tantas familias como la mitad de la población, de modo
    que con selección aleatoria cada individuo participa en media una vez por generación.
    """

    def begin(self, population: list, parameters: ReplacementParameters):
        self.slots = list(population)
        self.position = {id(solution): index for index, solution in enumerate(population)}
        self.families = 0
        self.target = math.ceil(len(population) / 2)
        self.children = []
        for solution in self.slots:
            self._register(solution)

    def is_full(self) -> bool:
        return self.families >= self.target

    def wants_child(self) -> bool:
        return True

    def add_child(self, child):
        self.children.append(child)

    def end_family(self, parents: list):
        children, self.children = self.children, []
        self.families += 1
        for parent, child in self.pairs(parents, children):
            index = self.position.get(id(parent))
            if index is None:
                continue
            occupant = self.slots[index]
            if self.ranking_key(child, self.parameters) <= self.ranking_key(occupant, self.parameters):
                self._unregister(occupant)
                self.slots[index] = child
                self._register(child)

    def result(self) -> list:
        return self.slots

    @staticmethod
    def distance(a, b) -> float:
        edges_a, edges_b = solution_edges(a), solution_edges(b)
        union = edges_a | edges_b
        return 1 - len(edges_a & edges_b) / len(union) if union else 0.0

    def pairs(self, parents: list, children: list) -> list:
        """Empareja cada hijo con un padre: con dos y dos, la combinación de menor distancia total."""
        if len(parents) == 2 and len(children) == 2:
            direct = self.distance(parents[0], children[0]) + self.distance(parents[1], children[1])
            crossed = self.distance(parents[0], children[1]) + self.distance(parents[1], children[0])
            return list(zip(parents, children if direct <= crossed else children[::-1]))
        return list(zip(parents, children))
