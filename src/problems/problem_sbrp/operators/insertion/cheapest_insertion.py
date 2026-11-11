from typing import List, Optional

from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class CheapestInsertion:
    @staticmethod
    def insert(routes: List[List[Stop]], stop: Stop, problem: ProblemSBRP, max_routes: Optional[int] = None) -> bool:
        """
        Inserta la parada en la posición de menor costo de una ruta con capacidad disponible.
        Las rutas son listas de paradas sin la escuela. Si se indica max_routes y hay menos rutas
        no vacías que ese máximo, abrir una ruta nueva también es una opción.
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

        # Abrir una ruta nueva si la flota lo permite
        if max_routes is not None and sum(1 for stops in routes if stops) < max_routes:
            delta = 2 * CheapestInsertion.distance(problem, problem.school, stop)
            if best is None or delta < best[0]:
                best = (delta, None, 0)

        if best is None:
            return False
        _, stops, position = best
        if stops is None:
            routes.append([stop])
        else:
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
