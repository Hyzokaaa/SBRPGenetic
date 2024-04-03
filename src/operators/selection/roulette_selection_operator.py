import random

from src.operators.selection.selection_operator import SelectionOperator
from src.operators.selection.selection_parameters import SelectionParameters


class RouletteSelectionOperator(SelectionOperator):
    def selection(self, parameters: SelectionParameters):
        selected_solutions = []
        population_copy = parameters.solutions.copy()
        for _ in range(parameters.number_of_selected_solutions):
            # Invierte los valores de `aptitud si el objetivo es minimizar
            if not parameters.objective_max:
                fitnesses = [1 / parameters.problem.objective_function(individual) for individual in population_copy]
            else:
                fitnesses = [parameters.problem.objective_function(individual) for individual in population_copy]

            # Calcula la aptitud total de la población
            total_fitness = sum(fitnesses)
            # Selecciona un número aleatorio entre 0 y la aptitud total
            random_fitness = random.uniform(0, total_fitness)
            # Encuentra el primer individuo cuya aptitud acumulada es mayor que el número aleatorio
            cumulative_fitness = 0
            for individual, fitness in zip(population_copy, fitnesses):
                cumulative_fitness += fitness
                if cumulative_fitness > random_fitness:
                    selected_solutions.append(individual)
                    population_copy.remove(individual)
                    break
        return selected_solutions

