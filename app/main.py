from src.algorithm.geneticAlgorithm import GeneticAlgorithm
from src.model.sbrp import SBRP
from src.algorithm.stopAssigner import StopAssigner

def main():
    # Lee la instancia de SBRP desde un archivo
    sbrp = SBRP.read_instance("../data/instances/test/mi_instancia.xpress")
    StopAssigner.student_to_better_stop(sbrp)

    # Crea una instancia de GeneticAlgorithm con la instancia de SBRP
    genetic = GeneticAlgorithm(population_size=100, mutation_rate=0.1, crossover_rate=0.9, sbrp=sbrp, tournament_size=2)

    # Inicializa la población
    genetic.initialize_population()

    # Calcula la aptitud de la población
    fitness_values = genetic.calculate_fitness()

    # Imprime los valores de aptitud
    print("Fitness values:", fitness_values)

    # Realiza la selección por torneo
    winner = genetic.selection()

    # Imprime el ganador del torneo
    print("Winner of the tournament:", winner)


if __name__ == "__main__":
    main()
