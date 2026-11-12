import copy

from src.operators.initial_construction.initial_construction import InitialConstructionOperator
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.operators.operator_parameters import OperatorParameters
from src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.route_generator_strategy import RouteGeneratorStrategy
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


class RouteGenerator(InitialConstructionOperator):

    def generate(self, parameters: InitialConstructionParameters):
        # Copia del problema con sus propias paradas, que las estrategias marcan como asignadas;
        # el resto de datos (escuela, estudiantes, matriz de distancias) se comparte sin copiar
        problem: ProblemSBRP = copy.copy(parameters.problem)
        problem.stops = [copy.copy(stop) for stop in parameters.problem.stops]
        strategy: RouteGeneratorStrategy = parameters.route_generator_strategy
        solution = SolutionRouteSBRP()

        strategy.start_solution()
        for _ in problem.vehicles:
            route = strategy.generate_route(problem=problem, distance_operator=parameters.distance_operator)
            # Solo se representan las rutas que visitan alguna parada
            if len(route.stops) > 2:
                solution.routes.append(route)
        return solution
