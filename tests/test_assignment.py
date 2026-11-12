import collections

import pytest

from conftest import load_problem, operator, operator_names
from src.operators.distance.distance_euclidean import EuclideanDistance
from src.problems.problem_parameters import ProblemParameters
from src.problems.problem_sbrp.operators.initial_solution.stop_assignment.rebalance.stop_assignment_rebalancer import \
    InfeasibleAssignmentError
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP

STRATEGIES = [name for name in operator_names("_STRATEGY") if "STUDENT" in name]
INSTANCES = ["real/inst1-1s5-25-c25-w5.xpress", "real/inst54-7s20-100-c50-w20.xpress",
             "real/inst91-4s40-800-c25-w10.xpress", "MH/mi_instancia.xpress"]


@pytest.mark.parametrize("strategy", STRATEGIES)
@pytest.mark.parametrize("instance", INSTANCES)
def test_assignment_respects_walking_distance_and_capacity(strategy, instance):
    problem = load_problem(instance, strategy)
    distance = EuclideanDistance()
    counts = collections.Counter(student.assigned_stop.id for student in problem.students)
    assert all(student.assigned_stop is not None for student in problem.students)
    assert all(distance.calculate_distance(s.coordinates, s.assigned_stop.coordinates) <= problem.w_distance + 1e-9
               for s in problem.students)
    assert all(stop.num_assigned_students == counts.get(stop.id, 0) <= problem.bus_capacity for stop in problem.stops)


def test_rebalance_follows_reassignment_chains():
    # Paradas A(0,0), B(10,0), C(20,0) de capacidad 1 y w = 6. La asignación voraz deja a s3 sin parada;
    # la única solución es la cadena s3 -> A, s1 -> B, s2 -> C.
    problem = ProblemSBRP()
    problem.construct(ProblemParameters(EuclideanDistance(), (0, 5), [(0, 0), (10, 0), (20, 0)],
                                        [(4, 0), (14, 0), (-1, 0)], 3, 1, 6))
    operator("H_STUDENT_TO_CLOSEST_STOP_STRATEGY").generate_stop_assign(problem, EuclideanDistance())
    assert [student.assigned_stop.id for student in problem.students] == [2, 3, 1]
    assert [stop.num_assigned_students for stop in problem.stops] == [1, 1, 1]


def test_student_without_reachable_stop_raises_clear_error():
    with pytest.raises(InfeasibleAssignmentError, match="no tiene ninguna parada a una distancia máxima"):
        load_problem("MH/2.xpress")


def test_full_reachable_stops_raise_clear_error():
    # Una única parada de capacidad 1 alcanzable por dos estudiantes
    problem = ProblemSBRP()
    problem.construct(ProblemParameters(EuclideanDistance(), (0, 5), [(0, 0)], [(1, 0), (-1, 0)], 2, 1, 6))
    with pytest.raises(InfeasibleAssignmentError, match=r"alcanzables por el estudiante \d+ \(1\) están llenas"):
        operator("H_STUDENT_TO_CLOSEST_STOP_STRATEGY").generate_stop_assign(problem, EuclideanDistance())
