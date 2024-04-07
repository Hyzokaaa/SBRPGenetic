from src.operators.operator_parameters import OperatorParameters


class RepairParameters(OperatorParameters):
    def __init__(self,
                 problem,
                 solutions=None,
                 parents=None):
        super().__init__(problem=problem)
        self.solutions = solutions
        self.parents = parents
