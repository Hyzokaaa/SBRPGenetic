from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.operators.assignment_improvement.assignment_improvement_operator import \
    AssignmentImprovementOperator
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class NoAssignmentImprovementOperator(AssignmentImprovementOperator):
    """No cambia la asignación."""

    def improve(self, problem: ProblemSBRP, distance_operator: DistanceOperator) -> int:
        return 0
