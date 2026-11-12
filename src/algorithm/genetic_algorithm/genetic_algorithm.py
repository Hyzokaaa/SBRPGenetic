import random
import time

from src.algorithm.algorithm_parameters import AlgorithmParameters
from src.algorithm.optimization_algorithm import OptimizationAlgorithm
from src.operators.diversity.diversity_parameters import DiversityParameters
from src.operators.diversity.no_diversity_operator import NoDiversityOperator
from src.operators.replacement.generational_replacement_operator import GenerationalReplacementOperator
from src.operators.replacement.replacement_parameters import ReplacementParameters

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

            # Mantenimiento de la diversidad (por defecto no actúa)
            self.diversity_parameters.generation = i
            self.diversity_parameters.stagnation = stagnation_counter
            diversified = self.diversity_operator.apply(population, self.diversity_parameters)
            if diversified is not population:
                population = diversified
                best_iteration = parameters.problem.update_best_solution(best_iteration, i, parameters.objective_max,
                                                                         population)

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

    def construct_solution(self):
        """Solución nueva de la construcción inicial, reparada si es infactible."""
        new_solution = self.initial_construction_operator.generate(self.initial_solution_parameters)
        if self.repair_operator is not None and self.initial_solution_parameters.problem.violations(new_solution):
            self.repair_parameters.parents = [new_solution]
            self.repair_parameters.solutions = [new_solution]
            new_solution = self.repair_operator.repair(self.repair_parameters)[0]
        return new_solution

    def generate_initial_population(self, parameters):
        population = []
        best_solution = None
        for _ in range(self.initial_population_size):
            new_solution = self.construct_solution()
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

        self.diversity_operator = parameters.diversity_operator or NoDiversityOperator()
        self.diversity_parameters = DiversityParameters(
            problem=parameters.problem, objective_max=parameters.objective_max, elitism_size=parameters.elitism_size,
            construct=self.construct_solution, mutate=self.mutate)

        self.replacement_operator = parameters.replacement_operator or GenerationalReplacementOperator()
        self.replacement_parameters = ReplacementParameters(
            problem=parameters.problem, objective_max=parameters.objective_max,
            population_size=parameters.initial_population, elitism_size=parameters.elitism_size)

        # Contadores de la generación en curso (se informan mediante on_generation)
        self.generation_stats = {'crossovers': 0, 'mutations': 0, 'duplicate_mutations': 0}

    def create_new_population(self, population, parameters):
        problem = parameters.problem

        # El operador de reemplazo decide qué individuos forman la nueva generación (por defecto, la élite y los hijos)
        replacement = self.replacement_operator
        replacement.start(population, self.replacement_parameters)

        while not replacement.is_full():
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
                if child is None or not replacement.wants_child():
                    continue

                # mutation: independiente del cruce, con probabilidad mutation_rate por hijo
                if random.random() < self.diversity_operator.mutation_rate(parameters.mutation_rate):
                    self.mutate(child)
                    self.generation_stats['mutations'] += 1

                # Control de duplicados: se muta el hijo mientras sea idéntico a otro de la nueva población
                signature = problem.solution_signature(child)
                attempts = 0
                while replacement.contains(signature) and attempts < MAX_DUPLICATE_ATTEMPTS:
                    self.mutate(child)
                    self.generation_stats['duplicate_mutations'] += 1
                    signature = problem.solution_signature(child)
                    attempts += 1

                replacement.add_child(child)
            replacement.end_family(parents)

        return replacement.result()

    def mutate(self, solution):
        self.mutation_parameters.solution = solution
        self.mutation_operator.mutate(self.mutation_parameters)
