from statistics import mean
from typing import Dict, List, Set, Tuple

from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP

DEPOT = 0  # Identificador de la escuela en la matriz de distancias

Edge = Tuple[int, int]


def edge_key(u: int, v: int) -> Edge:
    return (u, v) if u <= v else (v, u)


def solution_edges(solution) -> Set[Edge]:
    """
    Aristas (no dirigidas) de la solución, tratando cada ruta como un ciclo que sale y regresa a la escuela.
    """
    edges = set()
    for route in solution.get_representation():
        ids = [stop.id for stop in route.stops if stop is not None and not isinstance(stop, School)]
        if ids:
            path = [DEPOT] + ids + [DEPOT]
            edges.update(edge_key(path[i], path[i + 1]) for i in range(len(path) - 1))
    return edges


def edge_origin(child, parent_a, parent_b) -> Dict[Edge, str]:
    """
    Origen de cada arista del hijo: 'AB' (común a ambos padres), 'A', 'B' o 'nueva'.
    """
    edges_a, edges_b = solution_edges(parent_a), solution_edges(parent_b)
    origin = {}
    for edge in solution_edges(child):
        if edge in edges_a and edge in edges_b:
            origin[edge] = 'AB'
        elif edge in edges_a:
            origin[edge] = 'A'
        elif edge in edges_b:
            origin[edge] = 'B'
        else:
            origin[edge] = 'nueva'
    return origin


def inheritance(child, own_parent, other_parent) -> float:
    """
    Fracción de las aristas exclusivas del otro padre que hereda el hijo.
    """
    own, other = solution_edges(own_parent), solution_edges(other_parent)
    exclusive = other - own
    if not exclusive:
        return 0.0
    return len(solution_edges(child) & exclusive) / len(exclusive)


def population_stats(population: List, problem: ProblemSBRP) -> Dict[str, float]:
    """
    Estadísticas de una población: aptitud (mejor, media y peor de las factibles), fracción de factibles
    y diversidad (fracción de soluciones distintas).
    """
    feasible = [problem.objective_function(s) for s in population if problem.is_feasible(s)]
    signatures = {problem.solution_signature(s) for s in population}
    return {
        'best': min(feasible) if feasible else None,
        'mean': mean(feasible) if feasible else None,
        'worst': max(feasible) if feasible else None,
        'feasible': len(feasible) / len(population) if population else 0.0,
        'diversity': len(signatures) / len(population) if population else 0.0,
    }
