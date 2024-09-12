from enum import Enum

import src.problems.problem_sbrp.problem_sbrp


class Operators(Enum):
    PROBLEM_SBRP = "src.problems.problem_sbrp.problem_sbrp.ProblemSBRP"

    EUCLIDEAN_DISTANCE = "src.operators.distance.distance_euclidean.EuclideanDistance"
    MANHATTAN_DISTANCE = "src.operators.distance.distance_manhattan.ManhattanDistance"

    INITIAL_SOLUTION_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.initial_solution.initial_solution_conform_operator_sbrp.InitialSolutionOperatorSBRP"

    H_STUDENT_TO_STOP_CLOSEST_TO_SCHOOL_STRATEGY = "src.problems.problem_sbrp.operators.initial_solution.stop_assignment.strategy.h_student_to_stop_closest_to_school_strategy.HStudentToStopClosestToSchoolStrategy"
    H_STUDENT_TO_STOP_CLOSEST_TO_CENTROID_STRATEGY = "src.problems.problem_sbrp.operators.initial_solution.stop_assignment.strategy.h_student_to_stop_closest_to_centroid_strategy.HStudentToStopClosestToCentroidStrategy"
    H_STUDENT_TO_CLOSEST_STOP_STRATEGY = "src.problems.problem_sbrp.operators.initial_solution.stop_assignment.strategy.h_student_to_closest_stop_strategy.HStudentToClosestStopStrategy"
    STUDENT_TO_RANDOM_STOP_STRATEGY = "src.problems.problem_sbrp.operators.initial_solution.stop_assignment.strategy.student_to_random_stop_strategy.StudentToRandomStopStrategy"

    H_CLOSEST_NEIGHBOR_AND_RANDOM_ROUTE_GENERATOR_STRATEGY = "src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.h_closest_neighbor_and_random_route_generator_strategy.HClosestNeighborAndRandomRouteGeneratorStrategy"
    H_CLOSEST_NEIGHBOR_ROUTE_GENERATION_STRATEGY = "src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.h_closest_neighbor_route_generator_strategy.HClosestNeighborRouteGeneratorStrategy"
    RANDOM_ROUTE_GENERATION_STRATEGY = "src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.random_route_generator_strategy.RandomRouteGeneratorStrategy"

    TOURNAMENT_SELECTION_OPERATOR = "src.operators.selection.tournament_selection_operator.TournamentSelectionOperator"
    ROULETTE_SELECTION_OPERATOR = "src.operators.selection.roulette_selection_operator.RouletteSelectionOperator"

    STOP_CROSSOVER_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.crossover.stop_crossover_operator_sbrp.StopCrossoverOperatorSBRP"
    ONE_POINT_CROSSOVER_OPERATOR = "src.operators.crossover.one_point_crossover_operator.OnePointCrossoverOperator"
    TWO_POINT_CROSSOVER_OPERATOR = "src.operators.crossover.two_point_crossover_operator.TwoPointCrossoverOperator"
    UNIFORM_CROSSOVER_OPERATOR = "src.operators.crossover.uniform_crossover_operator.UniformCrossoverOperator"

    REORDER_SEGMENT_MUTATION_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.mutation.reorder_segment_mutation_operator_sbrp.ReorderSegmentMutationOperatorSBRP"
    SWAP_MUTATION_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.mutation.swap_mutation_operator_sbrp.SwapMutationOperatorSBRP"

    REPAIR_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.repair.repair_operator_sbrp.RepairOperatorSBRP"
