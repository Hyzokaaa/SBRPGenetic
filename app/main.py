from src.algorithm.geneticAlgorithm import GeneticAlgorithm
from src.model.sbrp import SBRP
from src.algorithm.stopAssigner import StopAssigner
from src.utils.visualizer import Visualizer


def main():
    # Lee la instancia
    sbrp = SBRP.read_instance("D:/Git/SBRPGenetic/data/instances/test/inst60-5s20-200-c50-w10.xpress")
    StopAssigner.student_to_stop_closest_to_school(sbrp)

    genetic = GeneticAlgorithm(population_size=100, mutation_rate=0.1, crossover_rate=0.9, sbrp=sbrp, tournament_size=2)
    print("Inicializando la población...")

    genetic.initialize_population()
    print("Calculando la aptitud de la población inicial...")
    Visualizer.plot_routes(sbrp, genetic.get_best_solution())

    initial_fitness_values = genetic.calculate_fitness()
    print("Valores de aptitud inicial:", initial_fitness_values)
    print("La mejor solucion obtiene un resultado de: ")
    print(min(initial_fitness_values))

    genetic.run()

    print("Calculando la aptitud de la población final...")
    fitness_values = genetic.calculate_fitness()

    print("La mejor solucion obtiene un resultado de: ")
    print(min(fitness_values))

    print("Valores de aptitud final:", fitness_values)

    genetic.calculate_average(fitness_values=fitness_values, initial_fitness_values=initial_fitness_values)

    genetic.validate_solution(genetic.get_best_solution())

    Visualizer.plot_routes(sbrp, genetic.get_best_solution())


if __name__ == "__main__":
    main()


"""
    print("Inicializando la población...")

    genetic.initialize_population()
    print("Calculando la aptitud de la población inicial...")
    Visualizer.plot_routes(sbrp, genetic.get_best_solution())

    initial_fitness_values = genetic.calculate_fitness()
    print("Valores de aptitud inicial:", initial_fitness_values)

    genetic.run()

    print("Calculando la aptitud de la población final...")
    fitness_values = genetic.calculate_fitness()

    print("La mejor solucion obtiene un resultado de: ")
    print(min(fitness_values))

    print("Valores de aptitud final:", fitness_values)

    genetic.calculate_average(fitness_values=fitness_values, initial_fitness_values= initial_fitness_values)

    genetic.validate_solution(genetic.get_best_solution())

    count = 0
    for route in genetic.get_best_solution():
        print(f"Route {count}:\n")
        for stop in route.stops:
            print(f"Stop: {stop.id}")
        count += 1
        print(f"RouteCapacity: {route.students}")
"""