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
    H_STUDENT_TO_FEWEST_STOPS_STRATEGY = "src.problems.problem_sbrp.operators.initial_solution.stop_assignment.strategy.h_student_to_fewest_stops_strategy.HStudentToFewestStopsStrategy"
    NO_ASSIGNMENT_IMPROVEMENT_OPERATOR = "src.problems.problem_sbrp.operators.assignment_improvement.no_assignment_improvement_operator.NoAssignmentImprovementOperator"
    STOP_REMOVAL_ASSIGNMENT_IMPROVEMENT_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.assignment_improvement.stop_removal_improvement_operator_sbrp.StopRemovalImprovementOperatorSBRP"
    STOP_REPLACEMENT_ASSIGNMENT_IMPROVEMENT_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.assignment_improvement.stop_replacement_improvement_operator_sbrp.StopReplacementImprovementOperatorSBRP"
    COMPOSITE_ASSIGNMENT_IMPROVEMENT_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.assignment_improvement.composite_assignment_improvement_operator_sbrp.CompositeAssignmentImprovementOperatorSBRP"

    H_CLOSEST_NEIGHBOR_AND_RANDOM_ROUTE_GENERATOR_STRATEGY = "src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.h_closest_neighbor_and_random_route_generator_strategy.HClosestNeighborAndRandomRouteGeneratorStrategy"
    H_CLOSEST_NEIGHBOR_ROUTE_GENERATION_STRATEGY = "src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.h_closest_neighbor_route_generator_strategy.HClosestNeighborRouteGeneratorStrategy"
    RANDOM_ROUTE_GENERATION_STRATEGY = "src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.random_route_generator_strategy.RandomRouteGeneratorStrategy"

    TOURNAMENT_SELECTION_OPERATOR = "src.operators.selection.tournament_selection_operator.TournamentSelectionOperator"
    ROULETTE_SELECTION_OPERATOR = "src.operators.selection.roulette_selection_operator.RouletteSelectionOperator"
    RANDOM_SELECTION_OPERATOR = "src.operators.selection.random_selection_operator.RandomSelectionOperator"
    PROBABILISTIC_TOURNAMENT_SELECTION_OPERATOR = "src.operators.selection.probabilistic_tournament_selection_operator.ProbabilisticTournamentSelectionOperator"
    LINEAR_RANKING_SELECTION_OPERATOR = "src.operators.selection.linear_ranking_selection_operator.LinearRankingSelectionOperator"
    GENERATIONAL_REPLACEMENT_OPERATOR = "src.operators.replacement.generational_replacement_operator.GenerationalReplacementOperator"
    DETERMINISTIC_CROWDING_REPLACEMENT_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.replacement.deterministic_crowding_replacement_operator_sbrp.DeterministicCrowdingReplacementOperatorSBRP"
    NO_DIVERSITY_OPERATOR = "src.operators.diversity.no_diversity_operator.NoDiversityOperator"
    RANDOM_IMMIGRANTS_DIVERSITY_OPERATOR = "src.operators.diversity.random_immigrants_operator.RandomImmigrantsOperator"
    TRIGGERED_HYPERMUTATION_DIVERSITY_OPERATOR = "src.operators.diversity.triggered_hypermutation_operator.TriggeredHypermutationOperator"
    CATACLYSMIC_RESTART_DIVERSITY_OPERATOR = "src.operators.diversity.cataclysmic_restart_operator.CataclysmicRestartOperator"
    CLEARING_DIVERSITY_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.diversity.clearing_operator_sbrp.ClearingOperatorSBRP"

    STOP_CROSSOVER_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.crossover.stop_crossover_operator_sbrp.StopCrossoverOperatorSBRP"
    ONE_POINT_CROSSOVER_OPERATOR = "src.operators.crossover.one_point_crossover_operator.OnePointCrossoverOperator"
    TWO_POINT_CROSSOVER_OPERATOR = "src.operators.crossover.two_point_crossover_operator.TwoPointCrossoverOperator"
    UNIFORM_CROSSOVER_OPERATOR = "src.operators.crossover.uniform_crossover_operator.UniformCrossoverOperator"
    EAX_CROSSOVER_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.crossover.eax_crossover_operator_sbrp.EAXCrossoverOperatorSBRP"
    SHARED_EDGE_RUIN_CROSSOVER_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.crossover.shared_edge_ruin_crossover_operator_sbrp.SharedEdgeRuinCrossoverOperatorSBRP"
    BCRC_CROSSOVER_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.crossover.bcrc_crossover_operator_sbrp.BCRCCrossoverOperatorSBRP"

    REORDER_SEGMENT_MUTATION_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.mutation.reorder_segment_mutation_operator_sbrp.ReorderSegmentMutationOperatorSBRP"
    BEST_REORDER_SEGMENT_MUTATION_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.mutation.best_reorder_segment_mutation_operator_sbrp.BestReorderSegmentMutationOperatorSBRP"
    RELOCATE_MUTATION_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.mutation.relocate_mutation_operator_sbrp.RelocateMutationOperatorSBRP"
    EXCHANGE_MUTATION_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.mutation.exchange_mutation_operator_sbrp.ExchangeMutationOperatorSBRP"
    COMPOSITE_MUTATION_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.mutation.composite_mutation_operator_sbrp.CompositeMutationOperatorSBRP"
    SWAP_MUTATION_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.mutation.swap_mutation_operator_sbrp.SwapMutationOperatorSBRP"

    REPAIR_OPERATOR_SBRP = "src.problems.problem_sbrp.operators.repair.repair_operator_sbrp.RepairOperatorSBRP"
