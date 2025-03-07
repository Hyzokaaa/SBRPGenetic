import json
import os
from typing import List

from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


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

def print_error(self, problem: ProblemSBRP, solutions: List[SolutionRouteSBRP], indicator :str ):
    assignments: list = problem.assign_solution.assignments
    stops: list = problem.stops

    for stop in stops:
        if stop.num_assigned_students > problem.bus_capacity:
            print(f"Error: Capacidad excedida en Stop {stop.name} en indicador {indicator}")

    for assignment in assignments:
        student, stop = assignment
        if stop is None:
            print(f"Error: Estudiante {student} no ha sido asignado a una parada en indicador {indicator}.")

    stops_assigned = []
    seen_stops = []
    for stop in stops:
        if stop.num_assigned_students > 0:
            stops_assigned.append(stop)  # Now this won't cause an error
    for child in solutions:
        for route in child.get_representation():
            seen_stops.extend(route.stops)  # Agrega las paradas de esta ruta a las vistas
    # Verifica que todas las paradas asignadas estén en las rutas vistas
    for stop in stops_assigned:
        if stop not in seen_stops:
            print(
                f"Error: La parada {stop.name} con estudiantes asignados no está en ninguna ruta en indicador {indicator}.")

    for route in child.get_representation():
        students_in_route = sum(stop.num_assigned_students for stop in route.stops)
        if students_in_route > problem.bus_capacity:
            print(f"Error: La ruta: {route} excede la capacidad del autobus en: {students_in_route}")

