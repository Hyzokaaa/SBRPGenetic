import os
from src.problems.problem_sbrp.algorithm.genetic_algorithm.genetic_algorithm_config_sbrp1 import \
    GeneticAlgorithmConfigSbrp1
from src.algorithm.genetic_algorithm.genetic_algorithm_executor import GeneticAlgorithmExecutor
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


def read_instances(path: str):
    # Get the list of file names in the directory
    return os.listdir(path)


def write_to_file(data, filename):
    with open(filename, 'a') as f:
        # Convert each item in data to a string and join them with a comma
        f.write(', '.join(map(str, data)) + '\n')


def execute_all_instances(instances_path):
    instances = read_instances(instances_path)
    ag_executor = GeneticAlgorithmExecutor()
    i = 0
    with open('test_crossover.csv', 'a') as f:
        # Convert each item in data to a string and join them with a comma
        f.write('EXECUTION' + '\n')
        f.write('instance, value, iteration' + '\n')
    while i < len(instances):
        instance_name = instances[i]
        config = GeneticAlgorithmConfigSbrp1(instances_path + instance_name)
        data = ag_executor.execute(config)
        data[0]: ProblemSBRP
        routes = data[0].best_solution.routes
        save_data = [data[1], f'iteration: {data[2]}']
        # Incluye el nombre de la instancia en los datos
        data_with_instance_name = [instance_name] + list(save_data)
        i += 1
        write_to_file(data_with_instance_name, 'test_crossover.csv')


if __name__ == "__main__":
    execute_all_instances(instances_path='data/instances/test/')
