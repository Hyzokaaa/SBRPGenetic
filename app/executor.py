import os
import re
from datetime import datetime

from shared.presentation.visualizer import Visualizer
from src.algorithm.genetic_algorithm.genetic_algorithm_config import GeneticAlgorithmConfig
from src.algorithm.genetic_algorithm.genetic_algorithm_executor import GeneticAlgorithmExecutor
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

    # Escribir resultados en run_<número>.csv
    output_path = f"{instance_dir}/run_{execution_number}.csv"
    with open(output_path, "w") as f:
        f.write("instance,value,iteration,execution_time,stop_reason,stop_iteration\n")
        f.write(f"{instance_clean},{data[1]},{data[2]},{data[3]:.2f},{data[4]},{data[5]}\n")