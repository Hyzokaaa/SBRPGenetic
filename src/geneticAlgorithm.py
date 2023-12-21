from src.routePlanner import RoutePlanner


class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate, crossover_rate, sbrp):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.sbrp = sbrp
        self.population = []

    def initialize_population(self):
        for _ in range(self.population_size):
            solution = RoutePlanner.generate_routes(self.sbrp)
            self.population.append(solution)

    def calculate_fitness(self):
        # Calcula la aptitud de cada solución en la población
        fitness_values = []
        for solution in self.population:
            # Calcula el costo total de las rutas en la solución
            total_cost = 0
            for route in solution:
                for i in range(len(route.stops) - 1):
                    stop1 = route.stops[i]
                    stop2 = route.stops[i + 1]
                    total_cost += self.sbrp.stop_cost_matrix[self.sbrp.id_to_index_stops[stop1.id]][self.sbrp.id_to_index_stops[stop2.id]]
            # La aptitud es el inverso del costo total (asumiendo que queremos minimizar el costo)
            fitness = 1.0 / total_cost
            fitness_values.append(fitness)
        return fitness_values

    def selection(self):
        # Implementación de la selección
        pass

    def crossover(self):
        # Implementación del cruce
        pass

    def mutation(self):
        # Implementación de la mutación
        pass

    def run(self):
        # Implementación de la ejecución del algoritmo genético
        pass