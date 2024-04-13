import random

from src.algorithm.algorithm_parameters import AlgorithmParameters
from src.algorithm.optimization_algorithm import OptimizationAlgorithm
from src.operators.initial_construction.initial_construction import InitialConstructionOperator
from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.operators.mutation.mutation_operator import MutationOperator
from src.operators.mutation.mutation_parameters import MutationParameters
from src.operators.repair.repair_operator import RepairOperator
from src.operators.repair.repair_parameters import RepairParameters
from src.operators.selection.selection_operator import SelectionOperator


class GeneticAlgorithm(OptimizationAlgorithm):

    def optimize(self, parameters: AlgorithmParameters):
        # # INITIALIZATION (Operators and parameters)
        # initialize initial construction operator
        initial_construction_operator: InitialConstructionOperator = parameters.initial_construction_operator
        initial_population_size = parameters.initial_population
        initial_solution_parameters: InitialConstructionParameters = parameters.initial_construction_parameters

        # initialize selection operator
        selection_operator: SelectionOperator = parameters.selection_operator
        selection_parameters = parameters.selection_parameters

        # initialize crossover operator
        crossover_operator: CrossoverOperator = parameters.crossover_operator
        crossover_parameters = parameters.crossover_parameters

        repair_operator: RepairOperator = parameters.repair_operator
        repair_parameters: RepairParameters = parameters.repair_parameters

        # initialize mutation operator
        mutation_operator: MutationOperator = parameters.mutation_operator
        mutation_parameters: MutationParameters = parameters.mutation_parameters

        # # INITIALIZATION (Variables)
        population = []
        best_solution = None

        # # EXECUTION (Initialize population)
        # genera la población inicial
        # itera generando soluciones como el tamaño de initial_population, agregándolas a la
        # variable population, a su vez analiza cada solución en busca de la mejor solución actual
        for _ in range(initial_population_size):
            new_solution = initial_construction_operator.generate(initial_solution_parameters)
            population.append(new_solution)

            best_solution = self.compare_solutions(best_solution, new_solution, parameters, )

        # Inicializa la variable para almacenar la iteración en la que se encontró la mejor solución
        best_iteration = -1

        # iterar tanto como el parámetro max_iter
        for i in range(parameters.max_iter):
            # Crear una nueva población para almacenar las soluciones hijas
            new_population = []
            print(i)
            while len(new_population) < initial_population_size:
                # selection
                selection_parameters.solutions = population
                parents = selection_operator.selection(selection_parameters)

                # crossover
                child1, child2 = None, None
                if random.random() < parameters.crossover_rate:
                    crossover_parameters.parent1 = parents[0]
                    crossover_parameters.parent2 = parents[1]
                    child1, child2 = crossover_operator.crossover(crossover_parameters)

                    # repair
                    repair_parameters.parents = [crossover_parameters.parent1, crossover_parameters.parent2]
                    repair_parameters.solutions = [child1, child2]
                    child1, child2 = repair_operator.repair(repair_parameters)

                    # mutation
                    for j in [child1, child2]:
                        if j is not None and random.random() < parameters.mutation_rate:
                            mutation_parameters.solution = j
                            mutation_operator.mutate(mutation_parameters)

                else:
                    child1, child2 = crossover_parameters.parent1, crossover_parameters.parent2

                # Agregar las soluciones hijas a la nueva población
                for child in [child1, child2]:
                    if child is not None and len(new_population) < initial_population_size:
                        new_population.append(child)

            population = new_population

            best_iteration, best_solution = self.update_best_solution(best_iteration, best_solution, i,
                                                                      parameters.objective_max, population,
                                                                      parameters.problem)

        return best_solution, parameters.problem.objective_function(best_solution), best_iteration, parameters.problem

    def compare_solutions(self, solution1, solution2, problem, objective_max):
        best_solution = solution1
        if best_solution is None or (
                objective_max and problem.objective_function(solution2) >
                problem.objective_function(best_solution)
        ) or (
                not objective_max and problem.objective_function(solution2) <
                problem.objective_function(best_solution)
        ):
            best_solution = solution2
        return best_solution

    def update_best_solution(self, best_iteration, best_solution, i, objective_max, population, problem):
        # Actualiza la mejor solución si se encuentra una mejor
        for new_solution in population:
            best_solution = self.compare_solutions(solution1=best_solution, solution2=new_solution,
                                                   problem=problem, objective_max=objective_max)
            best_iteration = i
        return best_iteration, best_solution
