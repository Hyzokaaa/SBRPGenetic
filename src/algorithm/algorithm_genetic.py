from src.algorithm.algorithm_parameters import AlgorithmParameters
from src.algorithm.optimization_algorithm import OptimizationAlgorithm
from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.initial_construction.initial_solution import InitialConstructionOperator
from src.problems.problem import Problem


class AlgorithmGenetic(OptimizationAlgorithm):

    def optimize(self, parameters: AlgorithmParameters):
        problem: Problem = parameters.problem
        initial_construction_operator: InitialConstructionOperator = parameters.initial_construction_operator
        initial_construction_operator_final: InitialConstructionOperator = parameters.initial_construction_operator_final
        crossover_operator: CrossoverOperator = parameters.crossover_operator
