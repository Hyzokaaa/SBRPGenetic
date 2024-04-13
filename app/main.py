import os

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
    while i < len(instances):
        config = GeneticAlgorithmConfigSbrp1(instances_path+instances[i])
        ag_executor.execute(config)
        i += 1


if __name__ == "__main__":
    execute_all_instances(instances_path='data/instances/real/')



