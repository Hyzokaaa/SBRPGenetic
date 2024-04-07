from src.algorithm.algorithm_genetic import AlgorithmGenetic
from src.algorithm.algorithm_parameters import AlgorithmParameters
from src.algorithm.hill_climbing import HillClimbing
from src.algorithm.random_search import RandomSearch
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.operators.crossover.one_point_crossover_operator import OnePointCrossoverOperator
from src.operators.distance.distance_euclidean import EuclideanDistance
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.operators.mutation.mutation_parameters import MutationParameters
from src.operators.repair.repair_parameters import RepairParameters
from src.operators.selection.selection_parameters import SelectionParameters
from src.operators.selection.tournament_selection_operator import TournamentSelectionOperator
from src.problems.problem_sbrp.data_io.file_data_input_sbrp import FileDataInputSBRP
from src.problems.problem_sbrp.operators.initial_solution.initial_solution_conform_operator_sbrp import InitialSolutionOperatorSBRP
from src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.random_route_generator_strategy import \
    RandomRouteGeneratorStrategy

from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.strategy.h_student_to_stop_closest_to_school_strategy import \
    HStudentToStopClosestToSchoolStrategy
from src.problems.problem_sbrp.operators.mutation.swap_mutation_operator_sbrp import SwapMutationOperatorSBRP
from src.problems.problem_sbrp.operators.repair.repair_operator_sbrp import RepairOperatorSBRP
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


def test_ag(problem, initial_construction_parameters, initial_construction_operator):
    selection_parameters = SelectionParameters(problem=problem,
                                               objective_max=False,
                                               tournament_size=2,
                                               number_of_selected_solutions=2)
    selection_operator = TournamentSelectionOperator()

    crossover_parameters = CrossoverParameters(problem=problem)
    crossover_operator = OnePointCrossoverOperator()

    repair_parameters = RepairParameters(problem=problem)
    repair_operator = RepairOperatorSBRP()

    mutation_parameters = MutationParameters(problem=problem)
    mutation_operator = SwapMutationOperatorSBRP()

    algorithm_parameters = AlgorithmParameters(problem=problem,
                                               objective_max=False,
                                               initial_population_size=20,
                                               max_iter=1000,
                                               mutation_rate=0.90,
                                               initial_construction_operator=initial_construction_operator,
                                               initial_construction_parameters=initial_construction_parameters,
                                               selection_operator=selection_operator,
                                               selection_parameters=selection_parameters,
                                               crossover_operator=crossover_operator,
                                               crossover_parameters=crossover_parameters,
                                               repair_parameters=repair_parameters,
                                               repair_operator=repair_operator,
                                               mutation_parameters=mutation_parameters,
                                               mutation_operator=mutation_operator)
    optimization_algorithm = AlgorithmGenetic()

    data = optimization_algorithm.optimize(algorithm_parameters)
    print(data[0])
    print(data[1])
    print(data[2])
    return data

def test_hc(problem, initial_construction_parameters, initial_construction_operator):
    mutation_parameters = MutationParameters(problem=problem)
    mutation_operator = SwapMutationOperatorSBRP()

    algorithm_parameters = AlgorithmParameters(problem=problem,
                                               objective_max=False,
                                               max_iter=1000,
                                               mutation_rate=1,
                                               initial_construction_operator=initial_construction_operator,
                                               initial_construction_parameters=initial_construction_parameters,
                                               mutation_parameters=mutation_parameters,
                                               mutation_operator=mutation_operator)
    optimization_algorithm = HillClimbing()

    data = optimization_algorithm.optimize(algorithm_parameters)
    print(data[0])
    print(data[1])
    print(data[2])
    return data

def test_rs(problem, initial_construction_parameters, initial_construction_operator):
    algorithm_parameters = AlgorithmParameters(problem=problem,
                                               objective_max=False,
                                               max_iter=1000,
                                               initial_construction_operator=initial_construction_operator,
                                               initial_construction_parameters=initial_construction_parameters)
    optimization_algorithm = RandomSearch()

    data = optimization_algorithm.optimize(algorithm_parameters)
    print(data[0])
    print(data[1])
    print(data[2])
    return data


import csv

if __name__ == "__main__":
    instances = ["inst60-5s20-200-c50-w10"]
    algorithms = [test_ag, test_hc, test_rs]
    results = []

    for instance in instances:
        data_input = FileDataInputSBRP(f"D:/Git/SBRPGenetic/data/instances/real/{instance}.xpress")
        problem_parameters = data_input.conform()

        problem = ProblemSBRP()
        problem.construct(problem_parameters=problem_parameters)

        initial_construction_parameters = InitialConstructionParameters(
                                                            problem=problem,
                                                            distance_operator=EuclideanDistance(),
                                                            stop_assign_strategy=HStudentToStopClosestToSchoolStrategy(),
                                                            route_generator_strategy=RandomRouteGeneratorStrategy())
        initial_construction_operator = InitialSolutionOperatorSBRP()

        for algorithm in algorithms:
            for i in range(10):
                print(f'Running {algorithm.__name__} iteration {i+1} for {instance}')
                result = algorithm(problem, initial_construction_parameters, initial_construction_operator)
                results.append((instance, algorithm.__name__, i+1, result))

    with open('results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Instance', 'Algorithm', 'Iteration', 'Best Solution', 'Objective Function', 'Best Iteration'])
        for instance, name, iteration, result in results:
            writer.writerow([instance, name, iteration] + list(result))
