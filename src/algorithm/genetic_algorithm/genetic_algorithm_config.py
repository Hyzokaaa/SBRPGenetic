import json
import importlib

from src.problems.problem_sbrp.algorithm.genetic_algorithm.operators_enum import Operators
from src.problems.problem_sbrp.data_io.file_data_input_sbrp import FileDataInputSBRP

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
        self.stop_assign_strategy = None
        self.route_generator_strategy = None
        self.objective_max = None
        self.tournament_size = None
        self.number_of_selected_solutions = None
        self.initial_population_size = None
        self.max_iter = None
        self.mutation_rate = None
        self.crossover_rate = None

    def load_from_file(self, config_file_path, instance_path):
        with open(config_file_path, 'r') as config_file:
            config_data = json.load(config_file)
            for key, value in config_data.items():
                if key.endswith('_operator') or key.endswith('_strategy') or key == 'problem':
                    try:
                        full_class_path = Operators[value].value
                        module_name, class_name = full_class_path.rsplit('.', 1)
                        module = importlib.import_module(module_name)
                        setattr(self, key, getattr(module, class_name)())
                    except ValueError:
                        raise ValueError(f"Invalid format for {key}: {value}. Expected 'module_name.ClassName'")
                else:
                    setattr(self, key, value)

            # Inicializar data_input después de cargar la configuración
            if instance_path is not None:
                self.instance_path = instance_path
            if self.instance_path:
                self.data_input = FileDataInputSBRP(self.instance_path)

    def __str__(self):
        return (f"{self.instance_path} {self.problem} {self.objective_max} {self.max_iter} "
                f"{self.mutation_rate} {self.crossover_rate}")