from src.algorithm.crossover import Crossover
from src.algorithm.routePlanner import RoutePlanner
import copy
import random

from src.model.school import School


class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate, crossover_rate, sbrp, tournament_size, num_generations):
        self.tournament_size = tournament_size
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.sbrp = sbrp
        self.population = []
        self.num_generations = num_generations
        self.crossover_operator = Crossover(sbrp, crossover_rate)

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
                # Realiza la selección para obtener los padres
                parent1 = self.selection()
                parent2 = self.selection()

                # Realiza el cruce para generar dos hijos
                child1, child2 = self.crossover_operator.crossover(parent1, parent2)
                self.validate_solution(child1)
                self.validate_solution(child2)

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

    def get_best_solution(self):
        best_solution = min(self.population, key=self.calculate_individual_fitness)
        return best_solution

    def validate_solution(self, solution):
        """
        Verifica que una solución satisfaga todas las condiciones del problema.
        """
        for route in solution:
            # Verifica que la capacidad del autobús no se exceda en ninguna ruta
            if sum([stop.num_assigned_students for stop in route.stops]) > self.sbrp.bus_capacity:
                print("tengo mas estudiantes que la capacidad del bus")
                return False

            # Verifica que no se repita ninguna parada en una ruta
            seen_stops = set()
            for stop in route.stops:
                key = (stop.coord_x, stop.coord_y)
                if key in seen_stops and not isinstance(stop, School):
                    print("se me repite alguna parada")
                    return False
                seen_stops.add(key)

        # Si la solución pasa todas las verificaciones, es válida
        return True

    def count_stop(self, solution):
        count = 0
        for route in solution:
            for stop in route.stops:
                if not isinstance(stop, School):
                    count += 1
        return count