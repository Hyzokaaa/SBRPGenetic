from src.algorithm.baseline_algorithm import BaselineAlgorithm


class RandomSearchAlgorithm(BaselineAlgorithm):
    """
    Búsqueda aleatoria: genera soluciones independientes con la misma construcción inicial que el GA
    (reparadas si hace falta) y se queda con la mejor factible. Mide cuánto aporta la evolución
    respecto a muestrear el mismo número de soluciones.
    """

    def initial_block(self) -> list:
        return self.next_block()

    def next_block(self) -> list:
        return [self.construct() for _ in range(self.block_size)]
