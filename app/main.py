import datetime
import os
import re
from executor import execute_all_instances

def print_progress(current_run, total_runs, start_time, config_number, instance_name, execution, total_executions):
    """
    Muestra el progreso de la ejecución en la consola.
    """
    # Calcular el progreso porcentual
    progress = (current_run / total_runs) * 100

    # Calcular el tiempo transcurrido
    elapsed_time = datetime.datetime.now() - start_time

    # Calcular el tiempo estimado restante
    if current_run > 0:
        estimated_total_time = elapsed_time * (total_runs / current_run)
        remaining_time = estimated_total_time - elapsed_time
    else:
        remaining_time = datetime.timedelta(0)

    # Mostrar el progreso
    print(
        f"Progreso: {progress:.2f}% | "
        f"Config {config_number} | "
        f"Instancia: {instance_name} | "
        f"Ejecución {execution + 1}/{total_executions} | "
        f"Tiempo transcurrido: {elapsed_time} | "
        f"Tiempo restante: {remaining_time}"
    )

if __name__ == "__main__":
    # Parámetros de ejecución
    total_configurations = 2  # Config1 a Config5
    total_executions = 2      # 20 ejecuciones por configuración
    instances_path = 'data/instances/test/'
    configs_base_path = 'src/problems/problem_sbrp/algorithm/genetic_algorithm/'

    # Obtener la lista de instancias
    instances = os.listdir(instances_path)
    total_instances = len(instances)

    # Calcular el número total de ejecuciones
    total_runs = total_configurations * total_executions * total_instances
    current_run = 0

    # Iniciar el cronómetro
    start_time = datetime.datetime.now()
    print(f"Inicio de la ejecución: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total de instancias: {total_instances}")
    print(f"Total de configuraciones: {total_configurations}")
    print(f"Total de ejecuciones por instancia/configuración: {total_executions}")
    print(f"Total de ejecuciones: {total_runs}")
    print("-" * 80)

    # Ejecutar todas las configuraciones
    for config_number in range(1, total_configurations + 1):
        config_path = os.path.join(configs_base_path, f'config{config_number}.json')

        # Verificar que el archivo de configuración existe
        if not os.path.exists(config_path):
            print(f"⚠️ ¡Config{config_number}.json no encontrado! Saltando...")
            continue

        # Ejecutar todas las instancias para esta configuración
        for instance_name in instances:
            # Ejecutar 20 veces para esta instancia y configuración
            for execution in range(total_executions):
                execute_all_instances(
                    instances_path=instances_path,
                    config_path=config_path,
                    instance_name=instance_name,  # Pasar el nombre de la instancia
                    execution_number=execution + 1,  # Pasar el número de ejecución
                    total_executions=total_executions
                )

                # Actualizar el contador de ejecuciones
                current_run += 1

                # Mostrar el progreso
                print_progress(current_run, total_runs, start_time, config_number, instance_name, execution, total_executions)

    # Mostrar el tiempo total de ejecución
    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    print("-" * 80)
    print(f"Ejecución finalizada: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tiempo total de ejecución: {total_time}")