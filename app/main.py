import multiprocessing
import datetime
import os
import re
from executor import execute_all_instances


def run_instance(args):
    """
    Función para ejecutar una instancia en un proceso separado.
    """
    config_path, instances_path, instance_name, execution, total_executions, config_number = args
    execute_all_instances(
        instances_path=instances_path,
        config_path=config_path,
        instance_name=instance_name,
        execution_number=execution + 1,
        total_executions=total_executions
    )


if __name__ == "__main__":
    # Parámetros de ejecución
    total_configurations = 3
    total_executions = 5
    instances_path = 'data/instances/test/'
    configs_base_path = 'src/problems/problem_sbrp/algorithm/genetic_algorithm/'

    # Obtener la lista de instancias
    instances = os.listdir(instances_path)
    total_instances = len(instances)

    # Calcular el número total de ejecuciones
    total_runs = total_configurations * total_executions * total_instances

    # Crear lista de argumentos para cada ejecución
    args_list = []
    for config_number in range(1, total_configurations + 1):
        config_path = os.path.join(configs_base_path, f'config{config_number}.json')
        if not os.path.exists(config_path):
            print(f"⚠️ ¡Config{config_number}.json no encontrado! Saltando...")
            continue
        for instance_name in instances:
            for execution in range(total_executions):
                args_list.append(
                    (config_path, instances_path, instance_name, execution, total_executions, config_number))

    # Iniciar Pool con 4 procesos (ajusta según tu CPU)
    num_cores = 4
    with multiprocessing.Pool(processes=num_cores) as pool:
        start_time = datetime.datetime.now()
        print(f"Inicio de la ejecución: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Ejecutar en paralelo con gestión de progreso
        for i, _ in enumerate(pool.imap_unordered(run_instance, args_list), 1):
            elapsed_time = datetime.datetime.now() - start_time
            progress = (i / total_runs) * 100

            # Calcular el tiempo restante estimado
            if i > 0:  # Evitar división por cero
                avg_time_per_run = elapsed_time / i
                remaining_runs = total_runs - i
                remaining_time = avg_time_per_run * remaining_runs
            else:
                remaining_time = datetime.timedelta(0)

            # Mostrar el progreso y el tiempo restante
            print(
                f"Progreso: {progress:.2f}% | "
                f"Tiempo transcurrido: {elapsed_time} | "
                f"Tiempo restante: {remaining_time}"
            )

        # Mostrar el tiempo total de ejecución
        total_time = datetime.datetime.now() - start_time
        print(f"Tiempo total: {total_time}")