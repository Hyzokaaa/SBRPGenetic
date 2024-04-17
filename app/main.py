import os

from src.algorithm.exhaustive_search.exhaustive_search_config import ExhaustiveSearchConfig
from src.algorithm.exhaustive_search.exhaustive_search_executor import ExhaustiveSearchExecutor
from src.problems.problem_sbrp.algorithm.genetic_algorithm.genetic_algorithm_config_sbrp1 import \
    GeneticAlgorithmConfigSbrp1
from src.algorithm.genetic_algorithm.genetic_algorithm_executor import GeneticAlgorithmExecutor


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
    while i < len(instances):
        instance_name = instances[i]
        config = GeneticAlgorithmConfigSbrp1(instances_path + instance_name)
        data = ag_executor.execute(config)
        save_data = [data[2], f'iteration: {data[3]}']
        # Incluye el nombre de la instancia en los datos
        data_with_instance_name = [instance_name] + list(save_data)
        i += 1
        write_to_file(data_with_instance_name, 'test_crossover.csv')
def test():
    es_executor = ExhaustiveSearchExecutor()
    config = ExhaustiveSearchConfig()
    es_executor.execute(config=config)


if __name__ == "__main__":
    test()
    #execute_all_instances(instances_path='data/instances/test/')


