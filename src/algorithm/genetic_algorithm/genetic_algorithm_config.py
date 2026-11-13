import json
import importlib

from src.problems.problem_sbrp.algorithm.genetic_algorithm.operators_enum import Operators
from src.problems.problem_sbrp.data_io.file_data_input_sbrp import FileDataInputSBRP

def instantiate(value):
    """Operador indicado por nombre del enumerado o como {"name": ..., "params": {...}}."""
    name, params = (value["name"], value.get("params", {})) if isinstance(value, dict) else (value, {})
    module_name, class_name = Operators[name].value.rsplit('.', 1)
    return getattr(importlib.import_module(module_name), class_name)(**params)


def operator_label(value) -> str:
    """Nombre legible de un operador de la configuración, con sus parámetros."""
    if isinstance(value, dict):
        params = ", ".join(f"{key}={param}" for key, param in value.get("params", {}).items())
        return f"{value['name']}({params})" if params else value["name"]
    return value


class GeneticAlgorithmConfig:
    def __init__(self):
        self.instance_path = None
        self.problem = None
        self.data_input = None
        self.distance_operator = None
        self.initial_construction_operator = None
        self.selection_operator = None
        self.crossover_operator = None
        self.repair_operator = None
        self.mutation_operator = None
        self.replacement_operator = None
        self.diversity_operator = None
        self.stop_assign_strategy = None
        self.route_generator_strategy = None
        self.objective_max = None
        self.tournament_size = None
        self.number_of_selected_solutions = None
        self.initial_population_size = None
        self.max_iter = None
        self.max_stagnation_iter = None
        self.mutation_rate = None
        self.crossover_rate = None
        self.elitism_size = None
        # Algoritmo a ejecutar: GA (por defecto) o una referencia (RANDOM_SEARCH, HILL_CLIMBING)
        self.algorithm = "GA"
        # Portafolio de asignaciones: si se indica, el algoritmo se ejecuta con cada una y se queda con la mejor
        self.stop_assign_portfolio = None
        self.stop_assign_portfolio_labels = None

    def load_from_file(self, config_file_path, instance_path):
        with open(config_file_path, 'r') as config_file:
            config_data = json.load(config_file)
            for key, value in config_data.items():
                if key.endswith('_operator') or key.endswith('_strategy') or key == 'problem':
                    try:
                        # El operador puede indicarse por nombre o como {"name": ..., "params": {...}}
                        setattr(self, key, instantiate(value))
                    except ValueError:
                        raise ValueError(f"Invalid format for {key}: {value}. Expected 'module_name.ClassName'")
                elif key == "stop_assign_portfolio":
                    self.stop_assign_portfolio = [instantiate(item) for item in value]
                    self.stop_assign_portfolio_labels = [operator_label(item) for item in value]
                elif key == "max_stagnation_iter":  # Nueva condición
                    setattr(self, key, int(value))
                else:
                    setattr(self, key, value)

            # Inicializar data_input después de cargar la configuración
            if instance_path is not None:
                self.instance_path = instance_path
            if self.instance_path:
                self.data_input = FileDataInputSBRP(self.instance_path, distance_operator=self.distance_operator)

    def __str__(self):
        return (f"{self.instance_path} {self.problem} {self.objective_max} {self.max_iter} "
                f"{self.mutation_rate} {self.crossover_rate}")