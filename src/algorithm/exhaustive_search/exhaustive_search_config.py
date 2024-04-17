from src.operators.distance.distance_euclidean import EuclideanDistance
from src.operators.exhaustive_search.exhaustive_search_operator import ExhaustiveSearchOperator
from src.problems.problem_sbrp.data_io.file_data_input_sbrp import FileDataInputSBRP
from src.problems.problem_sbrp.operators.exhaustive_search.exhaustive_search_operator_sbrp import \
    ExhaustiveSearchOperatorSBRP
from src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.exhaustive_route_generator_strategy import \
    ExhaustiveRouteGeneratorStrategy
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.stop_assigner import StopAssigner
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.strategy.h_student_to_stop_closest_to_school_strategy import \
    HStudentToStopClosestToSchoolStrategy
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class ExhaustiveSearchConfig:
    def __init__(self):
        self.instance_path = 'data/instances/real/inst1-1s5-25-c25-w5.xpress'  # Path to the instance file
        self.problem = ProblemSBRP()  # Problem object to be solved
        self.data_input = FileDataInputSBRP(self.instance_path)
        self.distance_operator = EuclideanDistance()
        self.initial_construction_operator = StopAssigner()  # Operator for initial solution construction
        self.exhaustive_search_operator = ExhaustiveSearchOperatorSBRP()
        self.stop_assign_strategy = HStudentToStopClosestToSchoolStrategy()
        self.route_generator_strategy = ExhaustiveRouteGeneratorStrategy()
        self.objective_max = False

