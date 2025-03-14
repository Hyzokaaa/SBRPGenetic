
from shared.aplication.algorithm.mutation_operator import MutationOperator
from shared.aplication.pre_algorithm_phases.route_generator import RouteGenerator
import copy
import random

from src.operators.crossover.crossover_operator import CrossoverOperator
from src.problems.problem_sbrp.model.school import School
from shared.presentation.visualizer import Visualizer


class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate, crossover_rate, sbrp, tournament_size, num_generations):
        self.tournament_size = tournament_size
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.sbrp = sbrp
        self.population = []
        self.num_generations = num_generations
        self.crossover_operator = CrossoverOperator(sbrp, crossover_rate)
        self.mutation_operator = MutationOperator(sbrp, mutation_rate)
        self.best_solution = None
        self.generation_best_solution = 0

    def initialize_population(self):
        for _ in range(self.population_size):
            sbrp_copy = copy.deepcopy(self.sbrp)
            solution = RouteGenerator.generate_routes(sbrp_copy)
            self.population.append(solution)

        self.best_solution = self.get_best_solution(population=self.population)

    def calculate_individual_fitness(self, individual):
        total_cost = 0
        if individual:
            for route in individual:
                for i in range(len(route.stops) - 1):
                    stop1 = route.stops[i]
                    stop2 = route.stops[i + 1]
                    total_cost += self.sbrp.stop_cost_matrix[self.sbrp.id_to_index_stops[stop1.id]][
                        self.sbrp.id_to_index_stops[stop2.id]]
            fitness = total_cost
            return fitness
        else:
            return 0

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

    def execute(self):
        # Inicializa la población
        self.initialize_population()
        self.run()

    def run(self):
        # Ejecuta el algoritmo genético durante num_generaciones
        for i in range(self.num_generations):
            print(i)
            # Crea una nueva población vacía
            new_population = []

            # Realiza el cruce y la mutación(Pendiente la mutación)
            while len(new_population) < self.population_size:
                # Realiza la selección para obtener los padres
                parent1 = self.selection()
                parent2 = self.selection()

                # Realiza el cruce para generar dos hijos
                if random.random() < self.crossover_rate:
                    child1, child2 = self.crossover_operator.crossover(parent1, parent2)
                else:
                    child1, child2 = parent1, parent2

                # Realiza la mutación si se cumple la probabilidad de mutación
                if random.random() < self.mutation_rate:
                    child1 = self.mutation_operator.swap_mutation(child1)
                    child2 = self.mutation_operator.swap_mutation(child2)

                self.validate_solution(child1)
                self.validate_solution(child2)

                # Añade los hijos a la nueva población
                new_population.append(child1)
                new_population.append(child2)

            self.update_best_solution(new_population, i)


            # Reemplaza la población antigua con la nueva
            self.population = new_population[:self.population_size]

    def update_best_solution(self, population, generation):
        # Busca la mejor solución de esta generación
        new_best_solution = self.get_best_solution(population)
        if self.best_solution is not None:
            if self.calculate_individual_fitness(self.best_solution) > self.calculate_individual_fitness(
                    new_best_solution):
                self.best_solution = new_best_solution
                self.generation_best_solution = generation
        else:
            self.best_solution = new_best_solution
            self.generation_best_solution = generation

    def calculate_average(self, initial_best_solution, final_best_solution):
        # Calcula el porcentaje de mejora del algoritmo
        return ((self.calculate_individual_fitness(initial_best_solution) - self.calculate_individual_fitness(
            final_best_solution)) / self.calculate_individual_fitness(initial_best_solution)) * 100

    def get_best_solution(self, population):
        best_solution = min(population, key=self.calculate_individual_fitness)
        return best_solution

    def validate_solution(self, solution):
        for route in solution:
            # Verifica que no se repita ninguna parada en una ruta
            seen_stops = set()
            for stop in route.stops:
                key = stop.id
                if key in seen_stops and not isinstance(stop, School):
                    return False
                seen_stops.add(key)

            # Verifica que no se exceda la capacidad del autobus
            total = 0
            for stop in route.stops:
                total += stop.num_assigned_students
            if total > self.sbrp.bus_capacity:
                return False
        return True

    def count_stops(self, solution):
        count: int = 0
        for route in solution:

            for stop in route.stops:
                if not isinstance(stop, School):
                    count += 1
        return count

    def execute_and_store(self, num_trial):
        # Inicializa una lista para almacenar los resultados
        results = []

        # Ejecuta el método run tantas veces como num_trial
        for i in range(num_trial):
            self.run()
            # Obtiene la mejor solución y su evaluación
            best_solution = self.best_solution
            evaluation = self.calculate_individual_fitness(best_solution)
            #Visualizer.plot_routes(self.sbrp, best_solution, "mejor solucion")
            # Almacena la iteración, la mejor solución y su evaluación
            results.append({
                'Iteracion': i + 1,
                'Solucion': best_solution,
                'Evaluacion': evaluation
            })

        # Devuelve los resultados
        return results

