import json

from conftest import CONFIGS, INSTANCES
from src.algorithm.genetic_algorithm.genetic_algorithm_config import GeneticAlgorithmConfig
from src.problems.problem_sbrp.data_io.file_data_input_sbrp import FileDataInputSBRP
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


def test_walking_distance_can_be_real(tmp_path):
    instance = tmp_path / "w_real.xpress"
    instance.write_text("2 2 1 10 2.5\n0 0\n1 1\n2 2\n1 1.5\n2 2.5\n")
    parameters = FileDataInputSBRP(str(instance)).conform()
    assert parameters.sbrp_walk_distance == 2.5
    assert (len(parameters.sbrp_stops_coordinates), len(parameters.sbrp_student_coordinates)) == (2, 2)


def test_instance_file_is_closed_after_reading():
    data_input = FileDataInputSBRP(str(INSTANCES / "real" / "inst1-1s5-25-c25-w5.xpress"))
    data_input.conform()
    assert data_input.file.closed


def test_distance_matrix_uses_configured_distance(tmp_path):
    config_data = json.loads((CONFIGS / "config8.json").read_text(encoding="utf-8"))
    config_data["distance_operator"] = "MANHATTAN_DISTANCE"
    config_path = tmp_path / "config_manhattan.json"
    config_path.write_text(json.dumps(config_data), encoding="utf-8")

    config = GeneticAlgorithmConfig()
    config.load_from_file(str(config_path), str(INSTANCES / "real" / "inst54-7s20-100-c50-w20.xpress"))
    problem = ProblemSBRP()
    problem.construct(config.data_input.conform())
    a, b = problem.stops[0], problem.stops[1]
    manhattan = sum(abs(x - y) for x, y in zip(a.coordinates, b.coordinates))
    assert abs(problem.distance_matrix[a.id][b.id] - manhattan) < 1e-9


def test_operators_accept_parameters_in_config(tmp_path):
    config_data = json.loads((CONFIGS / "config9.json").read_text(encoding="utf-8"))
    config_data["route_generator_strategy"] = {"name": "H_CLOSEST_NEIGHBOR_AND_RANDOM_ROUTE_GENERATOR_STRATEGY",
                                               "params": {"closest_neighbor_probability": 0.5}}
    config_path = tmp_path / "config_params.json"
    config_path.write_text(json.dumps(config_data), encoding="utf-8")
    config = GeneticAlgorithmConfig()
    config.load_from_file(str(config_path), str(INSTANCES / "real" / "inst1-1s5-25-c25-w5.xpress"))
    assert config.route_generator_strategy.closest_neighbor_probability == 0.5


def test_all_configs_load():
    for path in sorted(CONFIGS.glob("config*.json")):
        config = GeneticAlgorithmConfig()
        config.load_from_file(str(path), str(INSTANCES / "real" / "inst1-1s5-25-c25-w5.xpress"))
        assert config.crossover_operator is not None and config.mutation_operator is not None, path.name
