import itertools

from src.algorithm.algorithm_parameters import AlgorithmParameters
from src.algorithm.optimization_algorithm import OptimizationAlgorithm
from src.operators.exhaustive_search.exhaustive_search_operator import ExhaustiveSearchOperator
from src.operators.exhaustive_search.exhaustive_search_parameters import ExhaustiveSearchParameters
from src.operators.initial_construction.initial_construction import InitialConstructionOperator
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.stop_assigner import StopAssigner


class ExhaustiveSearch(OptimizationAlgorithm):

    def optimize(self, parameters: AlgorithmParameters):
        # # INITIALIZATION (Operators and parameters)
        # initialize exhaustive search operator
        exhaustive_search_operator: ExhaustiveSearchOperator = parameters.exhaustive_search_operator
        exhaustive_search_parameters: ExhaustiveSearchParameters = parameters.exhaustive_search_parameters

        best_solution = None
        best_fitness = None

        # Generate all feasible routes
        all_feasible_routes = exhaustive_search_operator.generate(parameters=exhaustive_search_parameters)

        # Generate all possible combinations of routes
        all_route_combinations = self.generate_all_combinations(all_feasible_routes, parameters.problem.vehicles)

        # Iterate over all route combinations
        for route_combination in all_route_combinations:
            # Check if the route combination covers all stops
            if self.covers_all_stops(route_combination, parameters.problem.stops):
                # Calculate the fitness of the route combination
                combination_fitness = parameters.problem.objective_function(route_combination)

                # If the route combination is better (according to objective_max), accept it as the new best solution
                if best_solution is None or (
                        parameters.objective_max and combination_fitness > best_fitness
                ) or (
                        not parameters.objective_max and combination_fitness < best_fitness
                ):
                    best_solution = route_combination
                    best_fitness = combination_fitness

        return best_solution, best_fitness

    @staticmethod
    def generate_all_combinations(routes, num_buses):
        # Generate all possible combinations of routes that do not exceed the number of buses
        all_combinations = []
        for r in range(1, len(num_buses) + 1):  # Modifica esta línea
            for combination in itertools.combinations(routes, r):
                all_combinations.append(list(combination))
        return all_combinations

    @staticmethod
    def covers_all_stops(route_combination, stops):
        # Check if the route combination covers all stops
        covered_stops = set(stop for route in route_combination for stop in route.stops)
        return covered_stops == stops

