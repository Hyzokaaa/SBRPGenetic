from abc import ABC, abstractmethod


class Problem(ABC):
    def __init__(self,
                 objective_function,
                 maximize=True,
                 num_iterations=100,
                 population_size=100,
                 crossover_probability=0.9,
                 mutation_probability=0.1,
                 crossover_operator=None,
                 mutation_operator=None,
                 selection_operator=None,
                 replacement_operator=None,
                 best_solution=None):

        self.objective_function = objective_function
        self.maximize = maximize
        self.num_iterations = num_iterations
        self.population_size = population_size
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability
        self.crossover_operator = crossover_operator
        self.mutation_operator = mutation_operator
        self.selection_operator = selection_operator
        self.replacement_operator = replacement_operator
        self.best_solution = best_solution

    @abstractmethod
    def initialize_population(self):
        pass

    @abstractmethod
    def selection(self):
        pass

    @abstractmethod
    def crossover(self):
        pass

    @abstractmethod
    def mutation(self):
        pass

    @abstractmethod
    def replacement(self):
        pass

    def solve(self):
        population = self.initialize_population()
        for _ in range(self.num_iterations):
            parents = self.selection(population)
            offspring = self.crossover(parents)
            offspring = self.mutation(offspring)
            population = self.replacement(population, offspring)
        return population
