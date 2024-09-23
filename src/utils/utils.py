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
