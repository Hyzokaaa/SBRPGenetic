from src.operators.operator_parameters import OperatorParameters


class CrossoverParameters(OperatorParameters):
    def __init__(self, problem,
                 parent1=None,
                 parent2=None
                 ):
        super().__init__(problem=problem)
        self.parent1 = parent1
        self.parent2 = parent2
