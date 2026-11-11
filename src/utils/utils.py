import json
import os
from typing import List


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


def get_string_config_data(config_file_path: str) -> str:
    with open(config_file_path, 'r') as file:
        config_data = json.load(file)

    fields = [
        "stop_assign_strategy",
        "route_generator_strategy",
        "crossover_operator",
        "mutation_operator",
        "initial_population_size",
        "max_iter",
        "crossover_rate",
        "mutation_rate"
    ]

    values = [str(config_data[field]) for field in fields]
    return ', '.join(values)
