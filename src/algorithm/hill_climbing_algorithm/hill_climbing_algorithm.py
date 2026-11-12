from src.algorithm.baseline_algorithm import BaselineAlgorithm


class HillClimbingAlgorithm(BaselineAlgorithm):
    """
    Escalada estocástica: parte de la mejor solución de una población inicial del mismo tamaño que la del GA
    y, en cada paso, genera un vecino con el operador de mutación (reparado si hace falta). Lo acepta si es
    factible y no empeora la solución actual; aceptar vecinos de igual distancia permite moverse por mesetas.
    Mide cuánto aportan la población y el cruce respecto a mejorar una única solución.
    """

    def initial_block(self) -> list:
        block = [self.construct() for _ in range(self.block_size)]
        self.current = None
        for solution in block:
            if self.is_better(solution, self.current):
                self.current = solution
        # Sin ninguna solución factible se parte de la de menor grado de violación
        if self.current is None:
            self.current = min(block, key=self.parameters.problem.constraint_violation)
        self.accepted = 0
        return block

    def next_block(self) -> list:
        mutation_parameters = self.parameters.mutation_parameters
        block = []
        self.accepted = 0
        for _ in range(self.block_size):
            neighbor = self.current.copy()
            mutation_parameters.solution = neighbor
            self.parameters.mutation_operator.mutate(mutation_parameters)
            neighbor = self.repair(neighbor)
            block.append(neighbor)
            if self.is_better(neighbor, self.current) or self.reduces_violation(neighbor):
                self.current = neighbor
                self.accepted += 1
        return block

    def reduces_violation(self, neighbor) -> bool:
        """Mientras la solución actual es infactible, se acepta el vecino que no aumenta el grado de violación."""
        problem = self.parameters.problem
        return (not problem.is_feasible(self.current)
                and problem.constraint_violation(neighbor) <= problem.constraint_violation(self.current))

    def generation_stats(self) -> dict:
        return {'mutations': self.block_size, 'accepted': self.accepted}
