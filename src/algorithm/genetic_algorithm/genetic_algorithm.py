import random

from src.algorithm.algorithm_parameters import AlgorithmParameters
from src.algorithm.optimization_algorithm import OptimizationAlgorithm


class GeneticAlgorithm(OptimizationAlgorithm):
    def optimize(self, parameters: AlgorithmParameters):
        # initialize operators and best solution
        self.initialize_operators_and_parameters(parameters)

        # generate initial population
        population, best_solution = self.generate_initial_population(parameters)
        best_iteration = 0

        for i in range(1, parameters.max_iter + 1):
            print(i)
            population = self.create_new_population(population, parameters)
            best_solution, best_iteration = self.update_best_solution(best_solution, best_iteration, i,
                                                                      parameters.objective_max, population,
                                                                      parameters.problem)

        return (parameters.problem,
                best_solution,
                parameters.problem.objective_function(best_solution),
                best_iteration)

    def generate_initial_population(self, parameters):
        population = []
        best_solution = None
        for _ in range(self.initial_population_size):
            new_solution = self.initial_construction_operator.generate(self.initial_solution_parameters)
            population.append(new_solution)
            best_solution = self.compare_solutions(solution1=best_solution,
                                                   solution2=new_solution,
                                                   problem=parameters.problem,
                                                   objective_max=parameters.objective_max)
        return population, best_solution

    def initialize_operators_and_parameters(self, parameters: AlgorithmParameters):
        self.initial_construction_operator = parameters.initial_construction_operator
        self.initial_population_size = parameters.initial_population
        self.initial_solution_parameters = parameters.initial_construction_parameters

        self.selection_operator = parameters.selection_operator
        self.selection_parameters = parameters.selection_parameters

        self.crossover_operator = parameters.crossover_operator
        self.crossover_parameters = parameters.crossover_parameters

        self.repair_operator = parameters.repair_operator
        self.repair_parameters = parameters.repair_parameters

        self.mutation_operator = parameters.mutation_operator
        self.mutation_parameters = parameters.mutation_parameters

    def create_new_population(self, population, parameters):
        new_population = []
        while len(new_population) < self.initial_population_size:
            # selection
            self.selection_parameters.solutions = population
            parents = self.selection_operator.selection(self.selection_parameters)

            # crossover
            child1, child2 = None, None
            if random.random() < parameters.crossover_rate:
                self.crossover_parameters.parent1 = parents[0]
                self.crossover_parameters.parent2 = parents[1]
                child1, child2 = self.crossover_operator.crossover(self.crossover_parameters)

                # repair
                self.repair_parameters.parents = [self.crossover_parameters.parent1, self.crossover_parameters.parent2]
                self.repair_parameters.solutions = [child1, child2]
                child1, child2 = self.repair_operator.repair(self.repair_parameters)

                # mutation
                if random.random() < parameters.mutation_rate:
                    for solution in [child1, child2]:
                        if solution is not None:
                            self.mutation_parameters.solution = solution
                            self.mutation_operator.mutate(self.mutation_parameters)
                            print('Muté')

            else:
                child1, child2 = parents[0], parents[1]

            for child in [child1, child2]:
                if child is not None and len(new_population) < self.initial_population_size:
                    new_population.append(child)

        return new_population

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

    def update_best_solution(self, best_solution, best_iteration, current_iteration, objective_max, population,
                             problem):
        # Actualiza la mejor solución si se encuentra una mejor
        for new_solution in population:
            updated_solution = self.compare_solutions(solution1=best_solution, solution2=new_solution,
                                                      problem=problem, objective_max=objective_max)
            if updated_solution != best_solution:
                print("encontre mejor solucion hermanao")
                best_solution = updated_solution
                best_iteration = current_iteration
        return best_solution, best_iteration
