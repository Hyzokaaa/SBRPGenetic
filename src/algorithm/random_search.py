from src.algorithm.algorithm_parameters import AlgorithmParameters
from src.algorithm.optimization_algorithm import OptimizationAlgorithm
from src.operators.initial_construction.initial_construction import InitialConstructionOperator
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters


class RandomSearch(OptimizationAlgorithm):
    def optimize(self, parameters: AlgorithmParameters):
        # # INITIALIZATION (Operators and parameters)
        # initialize initial construction operator
        initial_construction_operator: InitialConstructionOperator = parameters.initial_construction_operator
        initial_solution_parameters: InitialConstructionParameters = parameters.initial_construction_parameters

        best_solution = None
        best_fitness = None
        best_iteration = None
        # iterar tanto como el parámetro max_iter
        for i in range(parameters.max_iter):
            # Genera una solución aleatoria utilizando el operador de construcción inicial
            random_solution = initial_construction_operator.generate(initial_solution_parameters)
            random_fitness = parameters.problem.objective_function(random_solution)

            # Si la solución aleatoria es mejor (según objective_max), la acepta como la nueva mejor solución
            if best_solution is None or (
                    parameters.objective_max and random_fitness > best_fitness
            ) or (
                    not parameters.objective_max and random_fitness < best_fitness
            ):
                best_solution = random_solution
                best_fitness = random_fitness
                best_iteration = i

        return best_solution, best_fitness, best_iteration
