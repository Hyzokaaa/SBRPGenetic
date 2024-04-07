from src.operators.operator_parameters import OperatorParameters


class MutationParameters(OperatorParameters):
    def __init__(self,
                 problem,
                 solution=None):
        super().__init__(problem=problem)
        self.solution = solution
