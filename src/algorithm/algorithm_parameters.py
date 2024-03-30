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
                 objective_max: bool = True,
                 initial_construction_operator: InitialConstructionOperator = None,
                 mutation_operator: MutationOperator = None,

                 selection_operator: SelectionOperator = None,
                 crossover_operator: CrossoverOperator = None,
                 replacement_operator: ReplacementOperator = None,
                 crossover_rate: float = 0.90,
                 mutation_rate: float = 0.10,

                 repair_operator: RepairOperator = None
                 ):

        # Global Parameters
        self.problem: Problem = problem
        self.max_iter: int = max_iter
        self.objective_max: bool = objective_max
        self.initial_construction_operator: InitialConstructionOperator = initial_construction_operator
        self.mutation_operator: MutationOperator = mutation_operator

        # Population-based Parameters
        self.selection_operator: SelectionOperator = selection_operator
        self.crossover_operator: CrossoverOperator = crossover_operator
        self.replacement_operator: ReplacementOperator = replacement_operator
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate

        # Extra Parameters
        self.repair_operator: RepairOperator = repair_operator
