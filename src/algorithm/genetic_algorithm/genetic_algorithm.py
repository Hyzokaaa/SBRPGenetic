import random
import time

from src.algorithm.algorithm_parameters import AlgorithmParameters
from src.algorithm.optimization_algorithm import OptimizationAlgorithm

# Intentos de mutación para diferenciar un hijo duplicado antes de aceptarlo
MAX_DUPLICATE_ATTEMPTS = 10


class GeneticAlgorithm(OptimizationAlgorithm):

    def optimize(self, parameters: AlgorithmParameters):
        # Iniciar el cronómetro
        start_time = time.time()

        # Inicializar operadores y parámetros
        self.initialize_operators_and_parameters(parameters)

        # Generar población inicial
        population, best_solution = self.generate_initial_population(parameters)
        best_iteration = 0
        parameters.problem.update_best_solution(0, 0, parameters.objective_max, population)
        self.notify_generation(0, population, parameters)

        # Inicializar variables para el criterio de estancamiento
        best_fitness = None
        stagnation_counter = 0
        stop_reason = "max_iter"  # Razón de detención por defecto

        # Bucle principal del algoritmo
        for i in range(1, parameters.max_iter + 1):
            # Crear nueva población
            population = self.create_new_population(population, parameters)

            # Actualizar la mejor solución
            best_iteration = parameters.problem.update_best_solution(best_iteration, i,
                                                                     parameters.objective_max,
                                                                     population)

            self.notify_generation(i, population, parameters)

            # Obtener el mejor fitness actual
            current_best_fitness = self.best_fitness(parameters.problem)

            # Actualizar contador de estancamiento
            if best_fitness is None or current_best_fitness != best_fitness:
                best_fitness = current_best_fitness
                stagnation_counter = 0
            else:
                stagnation_counter += 1

            # Verificar criterio de parada por estancamiento
            if stagnation_counter >= parameters.max_stagnation_iter:
                stop_reason = "stagnation"
                break

        # Detener el cronómetro y calcular el tiempo total de ejecución
        end_time = time.time()
        execution_time = end_time - start_time

        # Retornar los resultados
        return (
            parameters.problem,  # Problema resuelto
            self.best_fitness(parameters.problem),  # Mejor fitness (None si no hubo solución factible)
            best_iteration,  # Iteración en la que se encontró el mejor fitness
            execution_time,  # Tiempo total de ejecución (en segundos)
            stop_reason,  # Razón de detención ("stagnation" o "max_iter")
            i  # Iteración en la que se detuvo el algoritmo
        )

    def notify_generation(self, generation, population, parameters):
        if parameters.on_generation is not None:
            parameters.on_generation(generation, population, parameters.problem, dict(self.generation_stats))
        self.generation_stats = {'crossovers': 0, 'mutations': 0, 'duplicate_mutations': 0}

    @staticmethod
    def best_fitness(problem):
        return problem.objective_function(problem.best_solution) if problem.best_solution is not None else None

    def generate_initial_population(self, parameters):
        population = []
        best_solution = None
        for _ in range(self.initial_population_size):
            new_solution = self.initial_construction_operator.generate(self.initial_solution_parameters)

            # Reparar las soluciones iniciales infactibles
            if self.repair_operator is not None and parameters.problem.violations(new_solution):
                self.repair_parameters.parents = [new_solution]
                self.repair_parameters.solutions = [new_solution]
                new_solution = self.repair_operator.repair(self.repair_parameters)[0]

            population.append(new_solution)
            best_solution = parameters.problem.compare_solutions(solution1=best_solution,
                                                                 solution2=new_solution,
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

        # Contadores de la generación en curso (se informan mediante on_generation)
        self.generation_stats = {'crossovers': 0, 'mutations': 0, 'duplicate_mutations': 0}

    def create_new_population(self, population, parameters):
        problem = parameters.problem

        # Elitismo: las mejores soluciones pasan intactas a la nueva población
        new_population = self.select_elite(population, parameters)
        signatures = {problem.solution_signature(solution) for solution in new_population}

        while len(new_population) < self.initial_population_size:
            # selection
            self.selection_parameters.solutions = population
            parents = self.selection_operator.selection(self.selection_parameters)

            # crossover
            if random.random() < parameters.crossover_rate:
                self.crossover_parameters.parent1 = parents[0]
                self.crossover_parameters.parent2 = parents[1]
                child1, child2 = self.crossover_operator.crossover(self.crossover_parameters)
                self.generation_stats['crossovers'] += 1

                # repair
                self.repair_parameters.parents = [self.crossover_parameters.parent1, self.crossover_parameters.parent2]
                self.repair_parameters.solutions = [child1, child2]
                child1, child2 = self.repair_operator.repair(self.repair_parameters)
            else:
                # Sin cruce, los hijos son copias de los padres (no los mismos objetos)
                child1, child2 = parents[0].copy(), parents[1].copy()

            for child in [child1, child2]:
                if child is None or len(new_population) >= self.initial_population_size:
                    continue

                # mutation: independiente del cruce, con probabilidad mutation_rate por hijo
                if random.random() < parameters.mutation_rate:
                    self.mutate(child)
                    self.generation_stats['mutations'] += 1

                # Control de duplicados: se muta el hijo mientras sea idéntico a otro de la nueva población
                signature = problem.solution_signature(child)
                attempts = 0
                while signature is not None and signature in signatures and attempts < MAX_DUPLICATE_ATTEMPTS:
                    self.mutate(child)
                    self.generation_stats['duplicate_mutations'] += 1
                    signature = problem.solution_signature(child)
                    attempts += 1

                new_population.append(child)
                signatures.add(signature)

        return new_population

    def mutate(self, solution):
        self.mutation_parameters.solution = solution
        self.mutation_operator.mutate(self.mutation_parameters)

    def select_elite(self, population, parameters):
        """
        Copias de las elitism_size mejores soluciones distintas de la población, según las reglas de
        factibilidad: primero las factibles (menor grado de violación) y, entre ellas, la de mejor aptitud.
        """
        problem = parameters.problem
        ranked = sorted(population, key=lambda solution: (
            problem.constraint_violation(solution),
            -problem.objective_function(solution) if parameters.objective_max else problem.objective_function(solution)))

        elite, signatures = [], set()
        for solution in ranked:
            if len(elite) >= parameters.elitism_size:
                break
            signature = problem.solution_signature(solution)
            if signature is not None and signature in signatures:
                continue
            elite.append(solution.copy())
            signatures.add(signature)
        return elite
