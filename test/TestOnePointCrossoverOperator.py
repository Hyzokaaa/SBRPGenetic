import unittest
from src.operators.crossover.one_point_crossover_operator import OnePointCrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP

class TestOnePointCrossoverOperator(unittest.TestCase):
    def setUp(self):
        self.operator = OnePointCrossoverOperator()
        self.parent1 = SolutionRouteSBRP()
        self.parent2 = SolutionRouteSBRP()
        self.parent1.set_representation([1, 2, 3, 4, 5])
        self.parent2.set_representation([6, 7, 8, 9, 0])
        self.problem = ProblemSBRP()
        self.parameters = CrossoverParameters(parent1=self.parent1, parent2=self.parent2, problem=self.problem)

    def test_crossover(self):
        child1, child2 = self.operator.crossover(self.parameters)
        self.assertIsInstance(child1, SolutionRouteSBRP)
        self.assertIsInstance(child2, SolutionRouteSBRP)
        self.assertNotEqual(child1.get_representation(), self.parent1.get_representation())
        self.assertNotEqual(child2.get_representation(), self.parent2.get_representation())

if __name__ == '__main__':
    unittest.main()