from src.utils.utils import Utils
from src.algorithm.geneticAlgorithm import GeneticAlgorithm
from src.model.sbrp import SBRP
from src.algorithm.stopAssigner import StopAssigner
from src.utils.visualizer import Visualizer


def main():
    # Lee la instancia
    sbrp = SBRP.read_instance("D:/Git/SBRPGenetic/data/instances/test/inst60-5s20-200-c50-w10.xpress")
    StopAssigner.student_to_stop_closest_to_school(sbrp)

    # Inicializa el algoritmo con sus parámetros
    genetic = GeneticAlgorithm(population_size=1000, mutation_rate=0.1, crossover_rate=0.95, sbrp=sbrp, tournament_size=2,
                               num_generations=100)

    # Inicializa la población
    genetic.initialize_population()

    # Conserva la mejor solución de la población inicial para posterior análisis estadístico
    initial_best_solution = genetic.get_best_solution(genetic.population)
    print("La mejor solución obtiene un resultado de: ")
    print(genetic.calculate_individual_fitness(initial_best_solution))

    # Ejecuta el algoritmo
    genetic.run()

    # Guarda en una variable la mejor solución al terminar de ejecutar el algoritmo para análisis posterior
    final_best_solution = genetic.best_solution

    print("La mejor solucón obtiene un resultado de: ")
    print(genetic.calculate_individual_fitness(final_best_solution))
    print(f"En la iteracion {genetic.generation_best_solution}")
    print(
        f"La mejor mejor solución tiene un total de {genetic.count_stops(final_best_solution)} paradas")
    if genetic.count_stops(final_best_solution) > 20:
        raise Exception(f'La variable tiene un valor de {genetic.count_stops(final_best_solution)}')
    print(
        genetic.calculate_average(initial_best_solution=initial_best_solution, final_best_solution=final_best_solution))

    genetic.validate_solution(final_best_solution)

    # Visualizer.plot_routes(sbrp, final_best_solution)


def save_status():
    sbrp = SBRP.read_instance(file_path="data/instances/real/inst60-5s20-200-c50-w10.xpress")
    StopAssigner.student_to_stop_closest_to_school(sbrp)
    genetic = GeneticAlgorithm(population_size=2, mutation_rate=0.1, crossover_rate=0.9, sbrp=sbrp, tournament_size=2,
                               num_generations=1)
    genetic.initialize_population()

    Utils.save_state(sbrp, "save_sbrp.pkl")
    Utils.save_state(genetic, "save_genetic.pkl")


def testing_scenario():
    # Lee la instancia
    sbrp: SBRP = Utils.load_state(file_path="save_sbrp.pkl")
    genetic: GeneticAlgorithm = Utils.load_state(file_path="save_genetic.pkl")

    solution1 = genetic.population[0]
    solution2 = genetic.population[1]
    child1, child2 = genetic.crossover_operator.crossover(solution1, solution2)

    genetic.population.append(child1)
    genetic.population.append(child2)

    print(
        f"La mejor mejor solución tiene un total de {genetic.count_stops(genetic.get_best_solution(genetic.population))} paradas")

    print("asd")


if __name__ == "__main__":
    main()
