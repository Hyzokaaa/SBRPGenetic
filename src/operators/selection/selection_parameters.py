from src.operators.operator_parameters import OperatorParameters


class SelectionParameters(OperatorParameters):
    def __init__(self, problem,
                 solutions=None,
                 objective_max=True,
                 number_of_selected_solutions=2,
                 tournament_size=2,):
        super().__init__(problem)
        self.objective_max = objective_max
        self.solutions: [] = solutions
        self.number_of_selected_solutions = number_of_selected_solutions
        self.tournament_size = tournament_size
