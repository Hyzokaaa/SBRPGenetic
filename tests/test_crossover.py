import random

import pytest

from conftest import operator, operator_names, snapshot
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.operators.repair.repair_parameters import RepairParameters
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP

CROSSOVERS = operator_names("CROSSOVER")
PAIRS = 15


def cross(problem, crossover, parent1, parent2):
    return operator(crossover).crossover(CrossoverParameters(problem=problem, parent1=parent1, parent2=parent2))


@pytest.mark.parametrize("crossover", CROSSOVERS)
def test_crossover_contract(crossover, inst54, inst54_population):
    random.seed(3)
    repair = operator("REPAIR_OPERATOR_SBRP")
    for _ in range(PAIRS):
        parent1, parent2 = random.sample(inst54_population, 2)
        before = snapshot(parent1), snapshot(parent2)
        children = cross(inst54, crossover, parent1, parent2)

        assert len(children) == 2 and all(isinstance(c, SolutionRouteSBRP) for c in children)
        assert (snapshot(parent1), snapshot(parent2)) == before, "el cruce modificó a los padres"
        parent_routes = {id(r) for r in parent1.get_representation() + parent2.get_representation()}
        assert not any(id(r) in parent_routes for c in children for r in c.get_representation()), \
            "los hijos comparten rutas con los padres"

        repaired = repair.repair(RepairParameters(problem=inst54, solutions=list(children), parents=[parent1, parent2]))
        assert all(inst54.is_feasible(c) for c in repaired)


def test_eax_respects_shared_edges(inst54, inst54_population):
    parent = inst54_population[0]
    for child in cross(inst54, "EAX_CROSSOVER_OPERATOR_SBRP", parent, parent):
        assert inst54.objective_function(child) == pytest.approx(inst54.objective_function(parent))


def test_eax_builds_alternating_ab_cycles(inst54, inst54_population):
    eax = operator("EAX_CROSSOVER_OPERATOR_SBRP")
    random.seed(5)
    for _ in range(PAIRS):
        parent1, parent2 = random.sample(inst54_population, 2)
        cycles = eax._ab_cycles(eax._edges(parent1), eax._edges(parent2))
        for cycle in cycles:
            assert len(cycle) % 2 == 0 and len(cycle) >= 4
            assert all(cycle[i][1] == cycle[(i + 1) % len(cycle)][0] for i in range(len(cycle))), "ciclo no cerrado"
            assert all(cycle[i][2] != cycle[(i + 1) % len(cycle)][2] for i in range(len(cycle))), "no alterna A/B"
