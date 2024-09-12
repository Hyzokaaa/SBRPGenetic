import os
from typing import List

from src.algorithm.genetic_algorithm.genetic_algorithm_config import GeneticAlgorithmConfig
from src.algorithm.genetic_algorithm.genetic_algorithm_executor import GeneticAlgorithmExecutor
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


def read_instances(path: str) -> List[str]:
    """
    Lee los nombres de los archivos en un directorio.

    Args:
        path (str): Ruta al directorio que contiene las instancias.

    Returns:
        List[str]: Lista de nombres de archivos en el directorio.
    """
    return os.listdir(path)


def write_to_file(data: List, filename: str) -> None:
    """
    Escribe datos en un archivo CSV.

    Args:
        data (List): Lista de datos a escribir en el archivo.
        filename (str): Nombre del archivo donde se escribirán los datos.

    Returns:
        None
    """
    with open(filename, 'a') as f:
        f.write(', '.join(map(str, data)) + '\n')


def execute_all_instances(instances_path):
    """
    Método para ejecutar todas las instancias de un directorio determinado

    Args:
        instances_path(str): Ruta al directorio que contiene las instancias
    Returns:
        None
     """
    # Se leen las instancias e inicializa el executor
    instances = read_instances(instances_path)
    ag_executor = GeneticAlgorithmExecutor()

    # Se abre el archivo csv y se define la nueva ejecución asi como los encabezados
    i = 0
    with open('test_crossover.csv', 'a') as f:
        # Convert each item in data to a string and join them with a comma
        f.write('EXECUTION' + '\n')
        f.write('instance, value, iteration' + '\n')

    # Se itera sobre cada instancia, se carga la configuración y se resuelve la misma
    while i < len(instances):
        instance_name = instances[i]
        config = GeneticAlgorithmConfig()
        config.load_from_file('src/problems/problem_sbrp/algorithm/genetic_algorithm/config1.json',
                              instances_path + instance_name)
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
