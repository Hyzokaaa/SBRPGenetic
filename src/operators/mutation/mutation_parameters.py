from src.operators.operator_parameters import OperatorParameters


class MutationParameters(OperatorParameters):
    def __init__(self,
                 problem,
                 solution=None,
                 distance_operator=None):
        super().__init__(problem=problem)
        self.solution = solution
        self.distance_operator = distance_operator
