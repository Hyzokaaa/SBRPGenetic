import datetime

from executor import execute_all_instances

if __name__ == "__main__":
    total_configuration = 5
    total_executions = 20
    total_runs = total_configuration * total_executions  # 5 configuraciones, cada una ejecutada 20 veces
    current_run = 0
    start_time = datetime.datetime.now()
    print(f"Inicio de la ejecución: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - Progreso: 0%")

    for config_number in range(1, total_configuration + 1):
        for i in range(total_executions):
            config_path = f'src/problems/problem_sbrp/algorithm/genetic_algorithm/config{config_number}.json'
            execute_all_instances(instances_path='data/instances/test/', config_path=config_path)
            current_run += 1
            progress = (current_run / total_runs) * 100
            current_time = datetime.datetime.now()
            print(f"Progreso: {progress:.2f}% - Hora actual: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")