from src.operators.operator_parameters import OperatorParameters


class ReplacementParameters(OperatorParameters):
    def __init__(self, problem, objective_max: bool = True, population_size: int = 100, elitism_size: int = 1):
        super().__init__(problem)
        self.objective_max = objective_max
        self.population_size = population_size
        self.elitism_size = elitism_size
