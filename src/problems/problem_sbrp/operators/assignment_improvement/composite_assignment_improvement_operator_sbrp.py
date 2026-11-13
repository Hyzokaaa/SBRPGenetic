from src.operators.distance.distance_operator import DistanceOperator
from src.problems.problem_sbrp.operators.assignment_improvement.assignment_improvement_operator import \
    AssignmentImprovementOperator
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class CompositeAssignmentImprovementOperatorSBRP(AssignmentImprovementOperator):
    """
    Aplica varias mejoras de la asignación en orden (por defecto, cierre y sustitución de paradas) y repite mientras
    alguna cambie algo, como un descenso por vecindarios variables. Devuelve el total de cambios.
    """

    def __init__(self, operators=("STOP_REMOVAL_ASSIGNMENT_IMPROVEMENT_OPERATOR_SBRP",
                                  "STOP_REPLACEMENT_ASSIGNMENT_IMPROVEMENT_OPERATOR_SBRP")):
        # Importación diferida: la configuración importa el enumerado, que referencia a esta clase
        from src.algorithm.genetic_algorithm.genetic_algorithm_config import instantiate
        self.operators = [instantiate(operator) for operator in operators]

    def improve(self, problem: ProblemSBRP, distance_operator: DistanceOperator) -> int:
        total = 0
        while True:
            changes = sum(operator.improve(problem, distance_operator) for operator in self.operators)
            total += changes
            if not changes:
                return total
