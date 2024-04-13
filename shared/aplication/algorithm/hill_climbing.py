from shared.aplication.algorithm.mutation_operator import MutationOperator


class HillClimbing:
    def __init__(self, sbrp, max_iter):
        self.sbrp = sbrp
        self.max_iter = max_iter
        self.mutation_operator = MutationOperator(sbrp=sbrp, mutation_rate=1)


    def optimize(self, solution):
        current_solution = solution.copy()
        current_fitness = self.calculate_individual_fitness(self.sbrp, current_solution)

        for i in range(self.max_iter):
            # Genera una solución vecina utilizando el operador de mutación
            neighbor_solution = self.mutation_operator.swap_mutation(current_solution.copy())
            neighbor_fitness = self.calculate_individual_fitness(self.sbrp, neighbor_solution)

            # Si la solución vecina es mejor (tiene mayor fitness), la acepta como la nueva solución actual
            if neighbor_fitness > current_fitness:
                current_solution = neighbor_solution
                current_fitness = neighbor_fitness

        return current_solution

    def calculate_individual_fitness(self, sbrp, individual):
        total_cost = 0
        if individual:
            for route in individual:
                for i in range(len(route.stops) - 1):
                    stop1 = route.stops[i]
                    stop2 = route.stops[i + 1]
                    total_cost += sbrp.stop_cost_matrix[sbrp.id_to_index_stops[stop1.id]][
                        sbrp.id_to_index_stops[stop2.id]]
            fitness = total_cost
            return fitness
        else:
            return 0


    def execute_and_store(self, num_trial, solution):
        # Inicializa una lista para almacenar los resultados
        results = []

        # Ejecuta el método run tantas veces como num_trial
        for i in range(num_trial):

            # Obtiene la mejor solución y su evaluación
            best_solution = self.optimize(solution)
            evaluation = self.calculate_individual_fitness(self.sbrp, best_solution)

            # Almacena la iteración, la mejor solución y su evaluación
            results.append({
                'Iteracion': i + 1,
                'Solucion': best_solution,
                'Evaluacion': evaluation
            })

        # Devuelve los resultados
        return results