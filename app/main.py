from src.algorithm.geneticAlgorithm import GeneticAlgorithm
from src.model.sbrp import SBRP
from src.algorithm.stopAssigner import StopAssigner
from src.utils.visualizer import Visualizer


def main():
    # Lee la instancia
    sbrp = SBRP.read_instance("D:/Git/SBRPGenetic/data/instances/test/inst110-6s80-800-c50-w20.xpress")
    StopAssigner.student_to_better_stop(sbrp)

    genetic = GeneticAlgorithm(population_size=500, mutation_rate=0.1, crossover_rate=0.9, sbrp=sbrp, tournament_size=2)

    print("Inicializando la población...")

    genetic.initialize_population()
    print("Calculando la aptitud de la población inicial...")

    initial_fitness_values = genetic.calculate_fitness()
    print("Valores de aptitud inicial:", initial_fitness_values)

    genetic.run()

    print("Calculando la aptitud de la población final...")
    fitness_values = genetic.calculate_fitness()

    print("La mejor solucion obtiene un resultado de: ")
    print(min(fitness_values))

    print("Valores de aptitud final:", fitness_values)

    genetic.calculate_average(fitness_values=fitness_values, initial_fitness_values= initial_fitness_values)


if __name__ == "__main__":
    main()
