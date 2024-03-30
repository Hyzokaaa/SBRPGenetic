from shared.aplication.algorithm.mutation_operator import MutationOperator
from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.initial_construction.initial_solution import InitialConstructionOperator
from src.operators.repair.repair_operator import RepairOperator
from src.operators.replacement.replacement_operator import ReplacementOperator
from src.operators.selection.selection_operator import SelectionOperator
from src.problems.problem import Problem


class AlgorithmParameters:
    def __init__(self,
                 problem: Problem,
                 max_iter: int,
                 initial_construction_operator: InitialConstructionOperator = None,
                 selection_operator: SelectionOperator = None,
                 crossover_operator: CrossoverOperator = None,
                 mutation_operator: MutationOperator = None,
                 repair_operator: RepairOperator = None,
                 replacement_operator: ReplacementOperator = None):

        #GlobalParameters
        self.max_iter: int = max_iter
        self.problem: Problem = problem
        self.initial_construction_operator: InitialConstructionOperator = initial_construction_operator
        self.mutation_operator: MutationOperator = mutation_operator

        #ExtraParameters
        self.repair_operator: RepairOperator = repair_operator

        #PoblationalParameters
        self.selection_operator: SelectionOperator = selection_operator
        self.crossover_operator: CrossoverOperator = crossover_operator
        self.replacement_operator: ReplacementOperator = replacement_operator


