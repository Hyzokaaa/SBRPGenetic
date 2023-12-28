from src.geneticAlgorithm import GeneticAlgorithm
from src.routePlanner import RoutePlanner
from src.sbrp import SBRP
from src.stopAssigner import StopAssigner
from src.visualizer import Visualizer


def main():
    # Lee la instancia de SBRP desde un archivo
    sbrp = SBRP.read_instance("../data/instances/test/inst60-5s20-200-c50-w10.xpress")
    StopAssigner.student_to_better_stop(sbrp)

    # Crea una instancia de GeneticAlgorithm con la instancia de SBRP
    genetic = GeneticAlgorithm(population_size=10, mutation_rate=0.1, crossover_rate=0.9, sbrp=sbrp)

    # Inicializa la población
    genetic.initialize_population()

    # Calcula la aptitud de la población
    fitness_values = genetic.calculate_fitness()

    # Imprime los valores de aptitud
    print(fitness_values)


if __name__ == "__main__":
    main()


