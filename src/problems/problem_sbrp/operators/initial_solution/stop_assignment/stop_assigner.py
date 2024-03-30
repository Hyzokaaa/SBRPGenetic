from src.operators.initial_construction.initial_solution import InitialConstructionOperator
from src.operators.operator_parameters import OperatorParameters
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.strategy.stop_assign_strategy \
    import StopAssignStrategy


class StopAssigner(InitialConstructionOperator):

    def generate(self, parameters: OperatorParameters):
        problem = parameters.problem
        distance_operator = parameters.distance_operator
        strategy: StopAssignStrategy = parameters.stop_assign_strategy

        strategy.generate_stop_assign(problem, distance_operator)
