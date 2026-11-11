from typing import List

from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class CheapestInsertion:
    @staticmethod
    def insert(routes: List[List[Stop]], stop: Stop, problem: ProblemSBRP) -> bool:
        """
        Inserta la parada en la posición de menor costo de una ruta con capacidad disponible.
        Las rutas son listas de paradas sin la escuela; las rutas vacías también son candidatas.
        Devuelve False si la parada no cabe en ninguna ruta.
        """
        best = None
        for stops in routes:
            if CheapestInsertion.load(stops) + stop.num_assigned_students > problem.bus_capacity:
                continue
            path = [problem.school] + stops + [problem.school]
            for position in range(len(path) - 1):
                delta = (CheapestInsertion.distance(problem, path[position], stop)
                         + CheapestInsertion.distance(problem, stop, path[position + 1])
                         - CheapestInsertion.distance(problem, path[position], path[position + 1]))
                if best is None or delta < best[0]:
                    best = (delta, stops, position)
        if best is None:
            return False
        _, stops, position = best
        stops.insert(position, stop)
        return True

    @staticmethod
    def route_cost(stops: List[Stop], problem: ProblemSBRP) -> float:
        path = [problem.school] + stops + [problem.school]
        return sum(CheapestInsertion.distance(problem, path[i], path[i + 1]) for i in range(len(path) - 1))

    @staticmethod
    def load(stops: List[Stop]) -> int:
        return sum(stop.num_assigned_students for stop in stops)

    @staticmethod
    def distance(problem: ProblemSBRP, stop1: Stop, stop2: Stop) -> float:
        return problem.distance_matrix[stop1.id][stop2.id]
