from src.operators.initial_construction.initial_construction import InitialConstructionOperator
from src.operators.initial_construction.initial_construction_parameters import InitialConstructionParameters
from src.operators.operator_parameters import OperatorParameters
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.strategy.stop_assign_strategy \
    import StopAssignStrategy


class StopAssigner(InitialConstructionOperator):

    def generate(self, parameters: InitialConstructionParameters):
        problem = parameters.problem
        distance_operator = parameters.distance_operator
        strategy: StopAssignStrategy = parameters.stop_assign_strategy

        if strategy is not None:
            print('asigne estudiantes')
            strategy.generate_stop_assign(problem, distance_operator)
            parameters.stop_assign_strategy = None
