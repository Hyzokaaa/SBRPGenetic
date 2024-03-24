from typing import List

from src.operators.distance.distance_manhattan import ManhattanDistance
from src.operators.operator_parameters import OperatorParameters
from src.problems.problem_sbrp.data_io.file_data_input_sbrp import FileDataInputSBRP
from src.problems.problem_sbrp.initial_solution.stop_assignment.h_student_to_better_stop_stop_assign import \
    HStudentToBetterStopStopAssign
from src.problems.problem_sbrp.initial_solution.stop_assignment.h_student_to_stop_closest_to_centroid_stop_assign import \
    HStudentToStopClosestToCentroidStopAssign
from src.problems.problem_sbrp.initial_solution.stop_assignment.h_student_to_stop_closest_to_school_stop_assign import \
    HStudentToStopClosestToSchoolStopAssign
from src.problems.problem_sbrp.initial_solution.stop_assignment.random_stop_assign import RandomStopAssign
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from shared.aplication.algorithm.crossover_operator import CrossoverOperator
from shared.aplication.algorithm.hill_climbing import HillClimbing
from shared.aplication.algorithm.mutation_operator import MutationOperator
from shared.aplication.pre_algorithm_phases.route_generator import RouteGenerator
from src.problems.problem_sbrp.model.route import Route
from shared.presentation.visualizer import Visualizer
from shared.utils.utils import Utils
from shared.aplication.algorithm.genetic_algorithm import GeneticAlgorithm
from shared.domain.sbrp import SBRP
from shared.aplication.pre_algorithm_phases.student_stop_assigner import StudentStopAssigner


def main():
    # Lee la instancia
    sbrp = SBRP.read_instance("D:/Git/SBRPGenetic/data/instances/real/inst35-10s10-100-c25-w10.xpress")
    StudentStopAssigner.student_to_stop_closest_to_school(sbrp)

    # Inicializa el algoritmo con sus parámetros
    genetic = GeneticAlgorithm(population_size=100, mutation_rate=1, crossover_rate=1, sbrp=sbrp, tournament_size=2,
                               num_generations=1000)

    # Inicializa la población
    genetic.initialize_population()

    # Conserva la mejor solución de la población inicial para posterior análisis estadístico
    initial_best_solution = genetic.get_best_solution(genetic.population)
    # Visualizer.plot_routes(sbrp, initial_best_solution)
    print("La mejor solución obtiene un resultado de: ")
    print(genetic.calculate_individual_fitness(initial_best_solution))

    # Ejecuta el algoritmo
    genetic.run()

    # Guarda en una variable la mejor solución al terminar de ejecutar el algoritmo para análisis posterior
    final_best_solution = genetic.best_solution

    print("La mejor solución obtiene un resultado de: ")
    print(genetic.calculate_individual_fitness(final_best_solution))
    print(f"En la iteración {genetic.generation_best_solution}")
    print(
        f"La mejor mejor solución tiene un total de {genetic.count_stops(final_best_solution)} paradas")
    '''
    if genetic.count_stops(final_best_solution) > 20:
        raise Exception(f'La variable tiene un valor de {genetic.count_stops(final_best_solution)}')
        '''
    print(
        genetic.calculate_average(initial_best_solution=initial_best_solution, final_best_solution=final_best_solution))

    genetic.validate_solution(final_best_solution)

    # Visualizer.plot_routes(sbrp, final_best_solution)


def create_context():
    # Genera un contexto de SBRP con asignación de paradas y lo guarda en un fichero
    sbrp = SBRP.read_instance(file_path="data/instances/real/inst35-10s10-100-c25-w10.xpress")
    StudentStopAssigner.student_to_stop_closest_to_school(sbrp)

    Utils.save_state(sbrp, "T-MH/save_sbrp.pkl")


def generate_solution():
    # Genera una solución luego de cargar un contexto SBRP guardado anteriormente
    sbrp: SBRP = Utils.load_state(file_path="T-MH/save_sbrp.pkl")

    solution = RouteGenerator.generate_routes(sbrp)
    Utils.save_state(solution, "T-MH/save_solution.pkl")
    Visualizer.plot_routes(sbrp, solution, "save_solution")


def crossover():
    # Lee la instancia
    sbrp = Utils.load_state(file_path="T-MH/save_sbrp.pkl")
    solution1: List[Route] = Utils.load_state(file_path="T-MH/save_solution.pkl")
    solution2: List[Route] = Utils.load_state(file_path="T-MH/save_solution1.pkl")

    print(calculate_individual_fitness(sbrp, solution1))
    print(calculate_individual_fitness(sbrp, solution2))

    # Instancia el operador de cruzamiento
    crossover_operator = CrossoverOperator(sbrp, crossover_rate=1)
    child1, child2 = crossover_operator.crossover_uniform(solution1, solution2)
    Visualizer.plot_routes(sbrp, child1, "save_crossover_child")
    Visualizer.plot_routes(sbrp, child2, "save_crossover_child")
    print(calculate_individual_fitness(sbrp, child1))
    print(calculate_individual_fitness(sbrp, child2))


def crossover2():
    # Lee la instancia
    sbrp = Utils.load_state(file_path="T-MH/save_sbrp.pkl")
    solution1: List[Route] = Utils.load_state(file_path="T-MH/save_solution14.pkl")
    solution2: List[Route] = Utils.load_state(file_path="T-MH/save_solution15.pkl")

    print(calculate_individual_fitness(sbrp, solution1))
    print(calculate_individual_fitness(sbrp, solution2))

    # Instancia el operador de cruzamiento
    crossover_operator = CrossoverOperator(sbrp, crossover_rate=1)
    child1, child2 = crossover_operator.crossover_uniform(solution1, solution2)
    Utils.save_state(child1, "T-MH/save_crossover_child.pkl")
    Utils.save_state(child2, "T-MH/save_crossover_child.pkl")
    Visualizer.plot_routes(sbrp, child1, "save_crossover_child")
    Visualizer.plot_routes(sbrp, child2, "save_crossover_child")
    print(calculate_individual_fitness(sbrp, child1))
    print(calculate_individual_fitness(sbrp, child2))


def calculate_individual_fitness(sbrp, individual):
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


def print_solution():
    sbrp = Utils.load_state(file_path="T-MH/save_sbrp.pkl")
    c1 = Utils.load_state(file_path="T-MH/save_crossover_child.pkl")
    c2 = Utils.load_state(file_path="T-MH/save_crossover_child1.pkl")
    c3 = Utils.load_state(file_path="T-MH/save_crossover_child2.pkl")
    c4 = Utils.load_state(file_path="T-MH/save_crossover_child3.pkl")
    c5 = Utils.load_state(file_path="T-MH/save_crossover_child4.pkl")
    c6 = Utils.load_state(file_path="T-MH/save_crossover_child5.pkl")

    a = [c1,c2,c3,c4,c5,c6]

    for i in a:
        print(calculate_individual_fitness(sbrp=sbrp, individual=i))


def mutation():
    # Lee la instancia
    sbrp = Utils.load_state(file_path="T-MH/save_sbrp.pkl")
    solution1: List[Route] = Utils.load_state(file_path="T-MH/save_solution14.pkl")
    copy: List[Route] = Utils.load_state(file_path="T-MH/save_solution14.pkl")

    print(calculate_individual_fitness(sbrp, solution1))

    # Instancia el operador de cruzamiento
    mutation_operator = MutationOperator(sbrp, mutation_rate=1)
    result = mutation_operator.swap_mutation(solution1)
    print(calculate_individual_fitness(sbrp,copy))
    print(calculate_individual_fitness(sbrp, result))
    print("")
    Visualizer.plot_routes(sbrp, copy, "save_mutation_father")
    Visualizer.plot_routes(sbrp, result, "save_mutation_child")


def hill_climbing():
    sbrp = Utils.load_state(file_path="T-MH/save_sbrp.pkl")
    hill_climbing_alg = HillClimbing(sbrp=sbrp, max_iter=1000)
    solution1: List[Route] = Utils.load_state(file_path="T-MH/save_solution14.pkl")
    results = hill_climbing_alg.execute_and_store(5, solution1)
    print(results)


def genetic_algorithm():
    sbrp = Utils.load_state(file_path="T-MH/save_sbrp.pkl")
    genetic = GeneticAlgorithm(population_size=100, mutation_rate=1, crossover_rate=1, sbrp=sbrp, tournament_size=2,
                               num_generations=1000)
    genetic.initialize_population()
    best = (genetic.execute_and_store(num_trial=5))


def test_input():
    # Crea una instancia de FileDataInput con la ruta al archivo
    data_input = FileDataInputSBRP("D:/Git/SBRPGenetic/data/instances/real/inst35-10s10-100-c25-w10.xpress")
    parameters = data_input.conform()


    # Ahora tienes los datos del problema y puedes usarlos para crear una instancia de ProblemSBRP
    problem = ProblemSBRP()
    problem.construct(problem_parameters=parameters)
    #print(problem)

    distance_operator = ManhattanDistance()
    stop_assign_parameters = OperatorParameters(problem=problem, distance_operator=distance_operator)
    initial_stop_assign_operator = HStudentToBetterStopStopAssign()
    initial_stop_assign_operator.generate(stop_assign_parameters)
    print(problem)

if __name__ == "__main__":
    #hill_climbing()
    #genetic_algorithm()
    test_input()


