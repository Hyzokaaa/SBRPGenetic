import unittest
from src.algorithm.genetic_algorithm.genetic_algorithm_config import GeneticAlgorithmConfig
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP

class TestGeneticAlgorithmConfig(unittest.TestCase):
    def setUp(self):
        self.config = GeneticAlgorithmConfig()

    def test_load_from_file(self):
        # Ruta al archivo de configuración
        config_file_path = '../src/problems/problem_sbrp/algorithm/genetic_algorithm/config4.json'
        instance_path = '../data/instances/test/inst10-1s5-50-c50-w5.xpress'

        # Cargar la configuración desde el archivo
        self.config.load_from_file(config_file_path, instance_path)

        # Verificar que los valores se cargaron correctamente
        self.assertEqual(self.config.instance_path, '../data/instances/test/inst10-1s5-50-c50-w5.xpress')
        self.assertIsInstance(self.config.problem, ProblemSBRP)
        self.assertEqual(self.config.distance_operator.__class__.__name__, 'EuclideanDistance')
        self.assertEqual(self.config.initial_construction_operator.__class__.__name__, 'InitialSolutionOperatorSBRP')
        self.assertEqual(self.config.stop_assign_strategy.__class__.__name__, 'HStudentToStopClosestToSchoolStrategy')
        self.assertEqual(self.config.route_generator_strategy.__class__.__name__, 'RandomRouteGeneratorStrategy')
        self.assertEqual(self.config.selection_operator.__class__.__name__, 'TournamentSelectionOperator')
        self.assertEqual(self.config.crossover_operator.__class__.__name__, 'EAXCrossoverOperatorSBRP')
        self.assertEqual(self.config.repair_operator.__class__.__name__, 'RepairOperatorSBRP')
        self.assertEqual(self.config.mutation_operator.__class__.__name__, 'ReorderSegmentMutationOperatorSBRP')
        self.assertFalse(self.config.objective_max)
        self.assertEqual(self.config.tournament_size, 15)
        self.assertEqual(self.config.number_of_selected_solutions, 2)
        self.assertEqual(self.config.initial_population_size, 100)
        self.assertEqual(self.config.max_iter, 100)
        self.assertEqual(self.config.crossover_rate, 0.5)
        self.assertEqual(self.config.mutation_rate, 0.2)

if __name__ == '__main__':
    unittest.main()