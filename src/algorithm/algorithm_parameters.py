from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.operators.initial_construction.initial_construction import InitialConstructionOperator
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.operators.mutation.mutation_operator import MutationOperator
from src.operators.mutation.mutation_parameters import MutationParameters
from src.operators.operator_parameters import OperatorParameters
from src.operators.repair.repair_operator import RepairOperator
from src.operators.repair.repair_parameters import RepairParameters
from src.operators.replacement.replacement_operator import ReplacementOperator
from src.operators.selection.selection_operator import SelectionOperator
from src.operators.selection.selection_parameters import SelectionParameters
from src.problems.problem import Problem


class AlgorithmParameters:
    def __init__(self,
                 problem: Problem,
                 initial_construction_parameters: InitialConstructionParameters,
                 max_iter: int = 1000,
                 initial_population_size: int = 100,
                 objective_max: bool = True,

                 mutation_parameters: MutationParameters = None,
                 selection_parameters: SelectionParameters = None,
                 crossover_parameters: CrossoverParameters = None,
                 repair_parameters: RepairParameters = None,


                 initial_construction_operator: InitialConstructionOperator = None,
                 mutation_operator: MutationOperator = None,
                 selection_operator: SelectionOperator = None,
                 crossover_operator: CrossoverOperator = None,
                 replacement_operator: ReplacementOperator = None,

                 crossover_rate: float = 0.9,
                 mutation_rate: float = 0.10,
                 replacement_type='replace',  # 'replace' or 'best_half'

                 repair_operator: RepairOperator = None
                 ):

        # Global Parameters
        self.problem: Problem = problem
        self.max_iter: int = max_iter
        self.objective_max: bool = objective_max

        self.initial_construction_parameters: InitialConstructionParameters = initial_construction_parameters
        self.initial_construction_operator: InitialConstructionOperator = initial_construction_operator
        self.mutation_operator: MutationOperator = mutation_operator
        self.mutation_parameters = mutation_parameters

        # Population-based Parameters
        self.initial_population = initial_population_size
        self.selection_operator: SelectionOperator = selection_operator
        self.crossover_operator: CrossoverOperator = crossover_operator
        self.replacement_operator: ReplacementOperator = replacement_operator
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.crossover_parameters = crossover_parameters
        self.selection_parameters = selection_parameters
        self.replacement_type = replacement_type

        # Extra Parameters
        self.repair_operator: RepairOperator = repair_operator
        self.repair_parameters: RepairParameters = repair_parameters
