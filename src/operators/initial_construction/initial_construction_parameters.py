from src.operators.distance.distance_operator import DistanceOperator
from src.operators.operator_parameters import OperatorParameters
from src.problems.problem_sbrp.operators.initial_solution.route_generation.strategy.route_generator_strategy import \
    RouteGeneratorStrategy
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.strategy.stop_assign_strategy import \
    StopAssignStrategy


class InitialConstructionParameters(OperatorParameters):
    def __init__(self,
                 problem,
                 distance_operator: DistanceOperator = None,
                 route_generator_strategy: RouteGeneratorStrategy = None,
                 stop_assign_strategy: StopAssignStrategy = None):
        super().__init__(problem)
        self.distance_operator = distance_operator
        self.route_generator_strategy = route_generator_strategy
        self.stop_assign_strategy = stop_assign_strategy


