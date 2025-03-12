import os
import re
from datetime import datetime

from shared.presentation.visualizer import Visualizer
from src.algorithm.genetic_algorithm.genetic_algorithm_config import GeneticAlgorithmConfig
from src.algorithm.genetic_algorithm.genetic_algorithm_executor import GeneticAlgorithmExecutor
from src.problems.problem_sbrp.model.school import School
from src.utils.utils import read_instances, get_string_config_data


def execute_all_instances(instances_path: str, config_path: str, instance_name: str, execution_number: int, total_executions: int) -> None:
    """
    Método para ejecutar una instancia específica.
    """
    ag_executor = GeneticAlgorithmExecutor()

    # Extraer número de configuración
    config_filename = os.path.basename(config_path)
    config_number = re.search(r"config(\d+)", config_filename).group(1)

    # Crear carpeta de configuración
    config_dir = f"results/config{config_number}"
    os.makedirs(config_dir, exist_ok=True)
    with open(f"{config_dir}/config_params.txt", "w") as f:
        f.write(get_string_config_data(config_path) + "\n")

    # Procesar la instancia específica
    instance_clean = os.path.splitext(instance_name)[0]
    instance_dir = f"{config_dir}/{instance_clean}"
    os.makedirs(instance_dir, exist_ok=True)

    # Cargar configuración y ejecutar el algoritmo
    config = GeneticAlgorithmConfig()
    config.load_from_file(config_path, instances_path + instance_name)
    data = ag_executor.execute(config)

    # Generar imagen en la carpeta del run
    image_path = f"{instance_dir}/run_{execution_number}_result.png"
    Visualizer.plot_routes(
        routes=data[0].best_solution,
        sbrp=data[0],
        image_path=image_path  # Ruta personalizada
    )

    # Obtener datos extendidos de la solución
    problem = data[0]
    solution = data[0].best_solution

    # 1. Generar mapeo de paradas con estudiantes
    stop_assignments = {}
    for stop in problem.stops:
        if stop.num_assigned_students > 0:
            students = [f"student{s.id}" for s in problem.students if s.assigned_stop == stop]
            stop_assignments[f"Stop{stop.id}"] = students

    # 2. Generar descripción de rutas
    routes_description = []
    for i, route in enumerate(solution.get_representation(), 1):
        stops = [f"Stop{stop.id}" if not isinstance(stop, School) else "School"
                 for stop in route.stops]
        total_students = sum(stop.num_assigned_students for stop in route.stops if not isinstance(stop, School))
        routes_description.append(f"Ruta{i}[{', '.join(stops)}] (Total: {total_students})")

    # Escribir resultados en run_<número>.csv
    output_path = f"{instance_dir}/run_{execution_number}.csv"
    with open(output_path, "w") as f:
        f.write("instance,value,iteration,execution_time,stop_reason,stop_iteration,student_assignments,routes\n")
        f.write(
            f"{instance_clean},"
            f"{data[1]},"
            f"{data[2]},"
            f"{data[3]:.2f},"
            f"{data[4]},"
            f"{data[5]},"
            f"\"{stop_assignments}\","  # Asignaciones entre paradas y estudiantes
            f"\"{'; '.join(routes_description)}\"\n"  # Descripción de rutas
        )
