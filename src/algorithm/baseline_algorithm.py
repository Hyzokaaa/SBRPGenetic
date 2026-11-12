import time
from abc import abstractmethod

from src.algorithm.algorithm_parameters import AlgorithmParameters
from src.algorithm.optimization_algorithm import OptimizationAlgorithm


class BaselineAlgorithm(OptimizationAlgorithm):
    """
    Base de los algoritmos de referencia con los que se compara el algoritmo genético.

    Para que la comparación sea justa usan el mismo presupuesto que el GA: avanzan por "generaciones
    equivalentes" de initial_population_size evaluaciones (generación 0 más max_iter generaciones), con el
    mismo criterio de estancamiento, y devuelven la misma tupla que GeneticAlgorithm.optimize. Las soluciones
    infactibles se reparan y, si siguen siendo infactibles, se descartan.
    """

    def optimize(self, parameters: AlgorithmParameters):
        start_time = time.time()
        self.parameters = parameters
        problem = parameters.problem

        block = self.initial_block()
        best_iteration = problem.update_best_solution(0, 0, parameters.objective_max, block)
        self.notify_generation(0, block)

        best_fitness = None
        stagnation_counter = 0
        stop_reason = "max_iter"
        i = 0
        for i in range(1, parameters.max_iter + 1):
            block = self.next_block()
            best_iteration = problem.update_best_solution(best_iteration, i, parameters.objective_max, block)
            self.notify_generation(i, block)

            current_best_fitness = self.best_fitness()
            if best_fitness is None or current_best_fitness != best_fitness:
                best_fitness = current_best_fitness
                stagnation_counter = 0
            else:
                stagnation_counter += 1
            if stagnation_counter >= parameters.max_stagnation_iter:
                stop_reason = "stagnation"
                break

        return problem, self.best_fitness(), best_iteration, time.time() - start_time, stop_reason, i

    @abstractmethod
    def initial_block(self) -> list:
        """Soluciones evaluadas en la generación 0."""

    @abstractmethod
    def next_block(self) -> list:
        """Soluciones evaluadas en la siguiente generación equivalente."""

    @property
    def block_size(self) -> int:
        return self.parameters.initial_population

    def construct(self):
        """Nueva solución con el operador de construcción inicial, reparada si es infactible."""
        return self.repair(self.parameters.initial_construction_operator.generate(
            self.parameters.initial_construction_parameters))

    def repair(self, solution):
        parameters = self.parameters
        if parameters.repair_operator is not None and parameters.problem.violations(solution):
            parameters.repair_parameters.parents = [solution]
            parameters.repair_parameters.solutions = [solution]
            solution = parameters.repair_operator.repair(parameters.repair_parameters)[0]
        return solution

    def is_better(self, solution, reference) -> bool:
        """Si solution es factible y al menos tan buena como reference."""
        problem = self.parameters.problem
        if not problem.is_feasible(solution):
            return False
        if reference is None:
            return True
        fitness, reference_fitness = problem.objective_function(solution), problem.objective_function(reference)
        return fitness >= reference_fitness if self.parameters.objective_max else fitness <= reference_fitness

    def best_fitness(self):
        problem = self.parameters.problem
        return problem.objective_function(problem.best_solution) if problem.best_solution is not None else None

    def generation_stats(self) -> dict:
        return {}

    def notify_generation(self, generation, block):
        if self.parameters.on_generation is not None:
            self.parameters.on_generation(generation, block, self.parameters.problem, self.generation_stats())
