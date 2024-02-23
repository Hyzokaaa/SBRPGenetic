from src.utils.utils import Utils
from src.algorithm.geneticAlgorithm import GeneticAlgorithm
from src.model.sbrp import SBRP
from src.algorithm.stopAssigner import StopAssigner
from src.utils.visualizer import Visualizer
import os;


def main():
    # Lee la instancia
    sbrp = SBRP.read_instance("D:/Git/SBRPGenetic/data/instances/test/inst60-5s20-200-c50-w10.xpress")
    StopAssigner.student_to_stop_closest_to_school(sbrp)

    genetic = GeneticAlgorithm(population_size=2, mutation_rate=0.1, crossover_rate=0.9, sbrp=sbrp, tournament_size=2,
                               num_generations=1)

    print("Inicializando la población...")

    genetic.initialize_population()

    print("Calculando la aptitud de la población inicial...")
    Visualizer.plot_routes(sbrp, genetic.get_best_solution())

    initial_fitness_values = genetic.calculate_fitness()
    print("Valores de aptitud inicial:", initial_fitness_values)
    print("La mejor solucion obtiene un resultado de: ")
    print(min(initial_fitness_values))
    print(f"La mejor mejor solucion tiene un total de {genetic.count_stops(genetic.get_best_solution())} paradas")

    genetic.run()

    print("Calculando la aptitud de la población final...")
    fitness_values = genetic.calculate_fitness()

    print("La mejor solucion obtiene un resultado de: ")
    print(min(fitness_values))
    print(f"La mejor mejor solucion tiene un total de {genetic.count_stops(genetic.get_best_solution())} paradas")

    print("Valores de aptitud final:", fitness_values)

    genetic.calculate_average(fitness_values=fitness_values, initial_fitness_values=initial_fitness_values)

    genetic.validate_solution(genetic.get_best_solution())

    Visualizer.plot_routes(sbrp, genetic.get_best_solution())


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
    sbrp = Utils.load_state(file_path="save_sbrp.pkl")
    genetic = Utils.load_state(file_path="save_genetic.pkl")
    print("Calculando la aptitud de la población inicial...")
    Visualizer.plot_routes(sbrp, genetic.get_best_solution())

    initial_fitness_values = genetic.calculate_fitness()
    print("Valores de aptitud inicial:", initial_fitness_values)
    print("La mejor solucion obtiene un resultado de: ")
    print(min(initial_fitness_values))
    print(f"La mejor mejor solucion tiene un total de {genetic.count_stops(genetic.get_best_solution())} paradas")

    genetic.run()

    print("Calculando la aptitud de la población final...")
    fitness_values = genetic.calculate_fitness()

    print("La mejor solucion obtiene un resultado de: ")
    print(min(fitness_values))
    print(f"La mejor mejor solucion tiene un total de {genetic.count_stops(genetic.get_best_solution())} paradas")

    print("Valores de aptitud final:", fitness_values)

    genetic.calculate_average(fitness_values=fitness_values, initial_fitness_values=initial_fitness_values)

    genetic.validate_solution(genetic.get_best_solution())

    Visualizer.plot_routes(sbrp, genetic.get_best_solution())

if __name__ == "__main__":
    testing_scenario()
