import copy
import random
from typing import List

from src.operators.repair.repair_operator import RepairOperator
from src.operators.repair.repair_parameters import RepairParameters
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.operators.insertion.cheapest_insertion import CheapestInsertion
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


class RepairOperatorSBRP(RepairOperator):
    def repair(self, parameters: RepairParameters):
        """
        Repara las soluciones hijas garantizando, siempre que sea posible:
        1. Que cada ruta salga y regrese a la escuela.
        2. Que no existan paradas duplicadas.
        3. Que ninguna ruta exceda la capacidad del autobús.
        4. Que no se utilicen más rutas que vehículos.
        5. Que todas las paradas con estudiantes del problema estén en la solución.
        Las paradas que no puedan reinsertarse quedan fuera y la solución resulta infactible.
        """
        childs: List[SolutionRouteSBRP] = copy.deepcopy(parameters.solutions)
        problem: ProblemSBRP = parameters.problem

        for child in childs:
            # Paso 1: Trabajar solo con las paradas de cada ruta (sin escuela ni paradas nulas)
            routes = self._normalize_routes(child)

            # Paso 2: Eliminar duplicados y reemplazar con paradas faltantes de los padres
            self._handle_duplicates(routes, parameters.parents)

            # Paso 3: Retirar paradas de las rutas que exceden la capacidad
            pending = self._enforce_capacity(routes, problem)

            # Paso 4: Añadir las paradas con estudiantes que no están en la solución
            pending += self._get_missing_mandatory_stops(routes, pending, problem)

            # Paso 5: Ajustar el número de rutas al número de vehículos
            pending += self._enforce_fleet_size(routes, problem)

            # Paso 6: Reinsertar las paradas pendientes en la posición más barata con capacidad disponible
            self._insert_pending_stops(routes, pending, problem)

            child.set_representation([self._build_route(stops, problem) for stops in routes])

        return childs

    def _normalize_routes(self, child: SolutionRouteSBRP) -> List[List[Stop]]:
        """
        Extrae las paradas de cada ruta, descartando la escuela y las paradas nulas.
        """
        return [[stop for stop in route.stops if stop is not None and not isinstance(stop, School)]
                for route in child.get_representation()]

    def _handle_duplicates(self, routes: List[List[Stop]], parents):
        """
        Elimina paradas duplicadas y las reemplaza con paradas faltantes de los padres.
        """
        parent_stops = self._get_unique_parent_stops(parents)
        seen_ids = set()

        for i, stops in enumerate(routes):
            new_stops = []
            for stop in stops:
                # Si la parada ya fue vista, es un duplicado
                if stop.id in seen_ids:
                    # Buscar una parada faltante de los padres para reemplazar
                    feasible_stops = [s for s in parent_stops if s.id not in seen_ids]
                    if feasible_stops:
                        new_stop = random.choice(feasible_stops)
                        new_stops.append(new_stop)
                        seen_ids.add(new_stop.id)
                else:
                    new_stops.append(stop)
                    seen_ids.add(stop.id)
            routes[i] = new_stops

    def _enforce_capacity(self, routes: List[List[Stop]], problem: ProblemSBRP) -> List[Stop]:
        """
        Retira paradas de las rutas que exceden la capacidad (priorizando las menos críticas)
        y las devuelve para reinsertarlas.
        """
        removed = []
        for stops in routes:
            while self._load(stops) > problem.bus_capacity:
                # Priorizar eliminar paradas sin estudiantes (si existen)
                non_mandatory_stops = [stop for stop in stops if stop.num_assigned_students == 0]
                if non_mandatory_stops:
                    removed_stop = non_mandatory_stops[-1]
                else:
                    # Eliminar la parada con menos estudiantes
                    removed_stop = min(stops, key=lambda s: s.num_assigned_students)
                stops.remove(removed_stop)
                removed.append(removed_stop)
        return removed

    def _get_missing_mandatory_stops(self, routes: List[List[Stop]], pending: List[Stop],
                                     problem: ProblemSBRP) -> List[Stop]:
        """
        Obtiene las paradas con estudiantes del problema que no están en las rutas ni pendientes.
        """
        present_ids = {stop.id for stops in routes for stop in stops} | {stop.id for stop in pending}
        return [stop for stop in problem.stops if stop.num_assigned_students > 0 and stop.id not in present_ids]

    def _enforce_fleet_size(self, routes: List[List[Stop]], problem: ProblemSBRP) -> List[Stop]:
        """
        Deja exactamente tantas rutas como vehículos. Si sobran, elimina primero las vacías y luego
        disuelve las de menor carga, devolviendo sus paradas para reinsertarlas. Si faltan, añade rutas vacías.
        """
        removed = []
        fleet_size = len(problem.vehicles)
        while len(routes) > fleet_size:
            empty_routes = [stops for stops in routes if not stops]
            route = empty_routes[0] if empty_routes else min(routes, key=self._load)
            routes.remove(route)
            removed.extend(route)
        while len(routes) < fleet_size:
            routes.append([])
        return removed

    def _insert_pending_stops(self, routes: List[List[Stop]], pending: List[Stop], problem: ProblemSBRP):
        """
        Inserta cada parada pendiente en la posición de menor costo de una ruta con capacidad disponible.
        Se insertan primero las paradas con más estudiantes para facilitar el empaquetado.
        Si una parada no cabe en ninguna ruta, se intenta liberar capacidad reubicando otra parada.
        """
        for stop in sorted(pending, key=lambda s: s.num_assigned_students, reverse=True):
            if not CheapestInsertion.insert(routes, stop, problem):
                self._insert_with_relocation(routes, stop, problem)

    def _insert_with_relocation(self, routes: List[List[Stop]], stop: Stop, problem: ProblemSBRP) -> bool:
        """
        Mueve una parada de una ruta (origen) a otra (destino) para liberar la capacidad necesaria en el origen
        e inserta allí la parada. Elige la combinación de menor costo total. Devuelve False si no es posible.
        """
        best = None
        for i, origin in enumerate(routes):
            for moved in origin:
                if self._load(origin) - moved.num_assigned_students + stop.num_assigned_students > problem.bus_capacity:
                    continue
                for j, target in enumerate(routes):
                    if j == i or self._load(target) + moved.num_assigned_students > problem.bus_capacity:
                        continue
                    candidate = [list(stops) for stops in routes]
                    candidate[i].remove(moved)
                    CheapestInsertion.insert([candidate[j]], moved, problem)
                    CheapestInsertion.insert([candidate[i]], stop, problem)
                    cost = sum(CheapestInsertion.route_cost(stops, problem) for stops in candidate)
                    if best is None or cost < best[0]:
                        best = (cost, candidate)
        if best is None:
            return False
        routes[:] = best[1]
        return True

    def _build_route(self, stops: List[Stop], problem: ProblemSBRP) -> Route:
        route = Route(stops=[problem.school] + stops + [problem.school])
        route.students = self._load(stops)
        return route

    def _get_unique_parent_stops(self, parents):
        """
        Obtiene todas las paradas únicas de las soluciones padres.
        """
        unique_stops = {}
        for parent in parents:
            for route in parent.get_representation():
                for stop in route.stops:
                    if stop is not None and not isinstance(stop, School) and stop.id not in unique_stops:
                        unique_stops[stop.id] = stop
        return list(unique_stops.values())

    @staticmethod
    def _load(stops: List[Stop]) -> int:
        return CheapestInsertion.load(stops)
