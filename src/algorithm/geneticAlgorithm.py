from src.algorithm.routePlanner import RoutePlanner
import copy
import random


class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate, crossover_rate, sbrp, tournament_size):
        self.tournament_size = tournament_size
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.sbrp = sbrp
        self.population = []

    def initialize_population(self):
        for _ in range(self.population_size):
            sbrp_copy = copy.deepcopy(self.sbrp)
            solution = RoutePlanner.generate_routes(sbrp_copy)
            self.population.append(solution)

    def calculate_individual_fitness(self, individual):
        total_cost = 0
        for route in individual:
            for i in range(len(route.stops) - 1):
                stop1 = route.stops[i]
                stop2 = route.stops[i + 1]
                total_cost += self.sbrp.stop_cost_matrix[self.sbrp.id_to_index_stops[stop1.id]][
                    self.sbrp.id_to_index_stops[stop2.id]]
        fitness = 1.0 / total_cost
        return fitness

    def calculate_fitness(self):
        fitness_values = []
        for individual in self.population:
            fitness = self.calculate_individual_fitness(individual)
            fitness_values.append(fitness)
        return fitness_values

    def selection(self):
        # Selecciona al azar un subconjunto de individuos de la población
        tournament = random.sample(self.population, self.tournament_size)

        # Elige al individuo con la mayor aptitud del torneo
        winner = max(tournament, key=self.calculate_individual_fitness)

        return winner

    def crossover(self):
        # Implementación del cruce
        pass

    def mutation(self):
        # Implementación de la mutación
        pass

    def run(self):
        # Implementación de la ejecución del algoritmo genético
        pass