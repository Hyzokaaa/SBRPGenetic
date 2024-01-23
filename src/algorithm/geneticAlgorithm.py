from src.algorithm.routePlanner import RoutePlanner
import copy
import random


class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate, crossover_rate, sbrp, tournament_size, num_generations = 500):
        self.tournament_size = tournament_size
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.sbrp = sbrp
        self.population = []
        self.num_generations = num_generations

    def initialize_population(self):
        for _ in range(self.population_size):
            sbrp_copy = copy.deepcopy(self.sbrp)
            solution = RoutePlanner.generate_routes(sbrp_copy)
            self.population.append(solution)

    def calculate_individual_fitness_simple(self, individual):
        total_cost = 0
        for route in individual:
            for i in range(len(route.stops) - 1):
                stop1 = route.stops[i]
                stop2 = route.stops[i + 1]
                total_cost += self.sbrp.stop_cost_matrix[self.sbrp.id_to_index_stops[stop1.id]][
                    self.sbrp.id_to_index_stops[stop2. id]]
        fitness = 1.0 / total_cost
        return fitness

    def calculate_individual_fitness(self, individual):
        total_cost = 0
        for route in individual:
            for i in range(len(route.stops) - 1):
                stop1 = route.stops[i]
                stop2 = route.stops[i + 1]
                total_cost += self.sbrp.stop_cost_matrix[self.sbrp.id_to_index_stops[stop1.id]][
                    self.sbrp.id_to_index_stops[stop2. id]]
        fitness = total_cost
        return fitness

    def calculate_fitness(self):
        fitness_values = []
        for individual in self.population:
            fitness = self.calculate_individual_fitness(individual)
            fitness_values.append(fitness)
        return fitness_values

    def selection(self):
        # Selecciona al azar un subconjunto de la población
        tournament = random.sample(self.population, self.tournament_size)

        # Elige al individuo con la mayor aptitud del torneo
        winner = min(tournament, key=self.calculate_individual_fitness)

        return winner

    def crossover(self, parent1, parent2):
        # Se realiza un cruce
        if random.random() < self.crossover_rate:
            # Selecciona un punto de cruce al azar
            crossover_point = random.randint(1, len(parent1) - 1)

            # Crea dos hijos intercambiando las rutas de los padres en el punto de cruce
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
        else:
            # Si no se realiza un cruce los hijos = padres
            child1, child2 = parent1, parent2
        return child1, child2

    def mutation(self):
        # Implementación de la mutación
        pass

    def run(self):
        # Inicializa la población
        self.initialize_population()

        # Ejecuta el algoritmo genético durante num_generaciones
        for _ in range(self.num_generations):
            # Crea una nueva población vacía
            new_population = []

            # Realiza el cruce y la mutación(Pendiente la mutación)
            while len(new_population) < self.population_size:
                # Realiza la selección para obetener los padres
                parent1 = self.selection()
                parent2 = self.selection()

                # Realiza el cruce para generar dos hijos
                child1, child2 = self.crossover(parent1, parent2)

                # Añade los hijos a la nueva población
                new_population.append(child1)
                new_population.append(child2)

            # Reemplaza la población antigua con la nueva
            self.population = new_population[:self.population_size]

    def calculate_average(self, fitness_values, initial_fitness_values):
        # Calcula el porcentaje de mejora para cada individuo
        improvement_percentage = [100 * (f - i) / i for f, i in zip(fitness_values, initial_fitness_values)]

        # Calcula el porcentaje de mejora promedio
        average_improvement_percentage = sum(improvement_percentage) / len(improvement_percentage)

        print("El porcentaje de mejora promedio en la aptitud de la población es del {}%.".format(
            average_improvement_percentage))