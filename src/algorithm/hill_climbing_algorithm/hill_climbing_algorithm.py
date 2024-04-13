from src.algorithm.algorithm_parameters import AlgorithmParameters
from src.algorithm.optimization_algorithm import OptimizationAlgorithm
from src.operators.initial_construction.initial_construction import InitialConstructionOperator
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.operators.mutation.mutation_operator import MutationOperator
from src.operators.mutation.mutation_parameters import MutationParameters


class HillClimbingAlgorithm(OptimizationAlgorithm):
    def optimize(self, parameters: AlgorithmParameters):
        # # INITIALIZATION (Operators and parameters)
        # initialize initial construction operator
        initial_construction_operator: InitialConstructionOperator = parameters.initial_construction_operator
        initial_solution_parameters: InitialConstructionParameters = parameters.initial_construction_parameters

        # initialize mutation operator
        mutation_operator: MutationOperator = parameters.mutation_operator
        mutation_parameters: MutationParameters = parameters.mutation_parameters

        current_solution = initial_construction_operator.generate(initial_solution_parameters)
        current_fitness = parameters.problem.objective_function(current_solution)
        best_iteration = None
        for i in range(parameters.max_iter):
            # Genera una solución vecina utilizando el operador de mutación
            mutation_parameters.solution = current_solution.copy()
            neighbor_solution = mutation_operator.mutate(mutation_parameters)
            neighbor_fitness = parameters.problem.objective_function(neighbor_solution)

            # Si la solución vecina es mejor, la acepta como la nueva solución actual
            if (parameters.objective_max and neighbor_fitness > current_fitness) or \
                    (not parameters.objective_max and neighbor_fitness < current_fitness):
                current_solution = neighbor_solution
                current_fitness = neighbor_fitness
                best_iteration = i

        return current_solution, current_fitness, best_iteration
