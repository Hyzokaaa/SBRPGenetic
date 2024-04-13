from src.algorithm.genetic_algorithm.genetic_algorithm_config import GeneticAlgorithmConfig
from src.operators.crossover.one_point_crossover_operator import OnePointCrossoverOperator
from src.operators.distance.distance_euclidean import EuclideanDistance
from src.operators.selection.tournament_selection_operator import TournamentSelectionOperator
from src.problems.problem_sbrp.data_io.file_data_input_sbrp import FileDataInputSBRP
from src.problems.problem_sbrp.operators.initial_solution.initial_solution_conform_operator_sbrp import \
    InitialSolutionOperatorSBRP
from src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.random_route_generator_strategy import \
    RandomRouteGeneratorStrategy
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.strategy.h_student_to_stop_closest_to_school_strategy import \
    HStudentToStopClosestToSchoolStrategy
from src.problems.problem_sbrp.operators.mutation.swap_mutation_operator_sbrp import SwapMutationOperatorSBRP
from src.problems.problem_sbrp.operators.repair.repair_operator_sbrp import RepairOperatorSBRP
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class GeneticAlgorithmConfigSbrp1(GeneticAlgorithmConfig):
    def __init__(self, instance_path):
        super().__init__()
        self.problem = ProblemSBRP()
        self.instance_path = instance_path
        self.data_input = FileDataInputSBRP(self.instance_path)
        self.distance_operator = EuclideanDistance()
        self.initial_construction_operator = InitialSolutionOperatorSBRP()
        self.selection_operator = TournamentSelectionOperator()
        self.crossover_operator = OnePointCrossoverOperator()
        self.repair_operator = RepairOperatorSBRP()
        self.mutation_operator = SwapMutationOperatorSBRP()
        self.stop_assign_strategy = HStudentToStopClosestToSchoolStrategy()
        self.route_generator_strategy = RandomRouteGeneratorStrategy()
        self.objective_max = False
        self.tournament_size = 10
        self.number_of_selected_solutions = 2
        self.initial_population_size = 400
        self.max_iter = 3
        self.mutation_rate = 0.50
        self.crossover_rate = 0.90
