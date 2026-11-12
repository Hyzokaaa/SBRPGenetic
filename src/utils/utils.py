import json


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
