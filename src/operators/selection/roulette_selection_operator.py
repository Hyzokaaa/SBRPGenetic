import random

from src.operators.selection.selection_operator import SelectionOperator
from src.operators.selection.selection_parameters import SelectionParameters


class RouletteSelectionOperator(SelectionOperator):
    def selection(self, parameters: SelectionParameters):
        selected_solutions = []
        population_copy = parameters.solutions.copy()

        # Calcula la aptitud total de la población una sola vez
        if not parameters.objective_max:
            fitnesses = [1 / parameters.problem.objective_function(individual) for individual in population_copy]
        else:
            fitnesses = [parameters.problem.objective_function(individual) for individual in population_copy]
        total_fitness = sum(fitnesses)

        for _ in range(parameters.number_of_selected_solutions):
            # Selecciona un número aleatorio entre 0 y la aptitud total
            random_fitness = random.uniform(0, total_fitness)
            cumulative_fitness = 0

            for individual, fitness in zip(population_copy, fitnesses):
                cumulative_fitness += fitness
                if cumulative_fitness > random_fitness:
                    selected_solutions.append(individual)
                    break

        return selected_solutions


