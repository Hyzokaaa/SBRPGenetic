import copy
import random
from typing import List

from src.operators.repair.repair_operator import RepairOperator
from src.operators.repair.repair_parameters import RepairParameters
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


class RepairOperatorSBRP(RepairOperator):
    def repair(self, parameters: RepairParameters):
        """
        Repara las soluciones hijas garantizando:
        1. Eliminar duplicados.
        2. Incluir todas las paradas con estudiantes del problema.
        """
        childs: List[SolutionRouteSBRP] = copy.deepcopy(parameters.solutions)
        problem: ProblemSBRP = parameters.problem

        for child in childs:
            # Paso 1: Eliminar duplicados y reemplazar con paradas faltantes de los padres
            self._handle_duplicates(child, parameters.parents, problem)

            # Paso 2: Asegurar que TODAS las paradas con estudiantes del problema estén en la solución
            self._ensure_all_mandatory_stops(child, problem)

            # Paso 3: Verificación final de capacidad en todas las rutas
            self._enforce_capacity(child, problem)

        return childs

    def _enforce_capacity(self, child: SolutionRouteSBRP, problem: ProblemSBRP):
        """
        Asegura que ninguna ruta exceda la capacidad del autobús.
        Si excede, elimina paradas (priorizando las menos críticas) hasta cumplir.
        """
        new_routes = []
        for route in child.get_representation():
            current_students = sum(stop.num_assigned_students for stop in route.stops)

            # Si la ruta excede la capacidad, eliminar paradas menos críticas
            while current_students > problem.bus_capacity:
                # Priorizar eliminar paradas sin estudiantes (si existen)
                non_mandatory_stops = [
                    stop for stop in route.stops
                    if not isinstance(stop, School)
                       and stop.num_assigned_students == 0
                ]

                if non_mandatory_stops:
                    # Eliminar la parada sin estudiantes más reciente
                    removed_stop = non_mandatory_stops[-1]
                else:
                    # Eliminar la parada con menos estudiantes
                    removed_stop = min(
                        [stop for stop in route.stops if not isinstance(stop, School)],
                        key=lambda s: s.num_assigned_students
                    )

                route.stops.remove(removed_stop)
                current_students -= removed_stop.num_assigned_students

                # Intentar mover la parada eliminada a otra ruta
                self._relocate_stop(child, removed_stop, problem.bus_capacity)

            new_routes.append(route)

        child.set_representation(new_routes)

    def _relocate_stop(self, child: SolutionRouteSBRP, stop: Stop, bus_capacity: int):
        """
        Intenta mover una parada eliminada a otra ruta con espacio.
        """
        for route in child.get_representation():
            if route.students + stop.num_assigned_students <= bus_capacity:
                route.stops.insert(-1, stop)  # Insertar antes de la escuela
                route.students += stop.num_assigned_students
                return

        # Si no hay espacio, crear nueva ruta
        school = child.get_representation()[0].stops[0] if child.get_representation() else School(id=0,
                                                                                                  name="School",
                                                                                                  coordinates=(
                                                                                                  0, 0))
        new_route = Route(stops=[school, stop, school])
        new_route.students = stop.num_assigned_students
        child.get_representation().append(new_route)

    def _handle_duplicates(self, child: SolutionRouteSBRP, parents, problem: ProblemSBRP):
        """
        Elimina paradas duplicadas y reemplaza con paradas faltantes de los padres.
        """
        # Obtener paradas únicas de los padres
        parent_stops = self._get_unique_parent_stops(parents)
        seen_stops = []

        # Procesar cada ruta del hijo
        new_routes = []
        for route in child.get_representation():
            new_route = Route(stops=[])
            for stop in route.stops:
                if isinstance(stop, School):
                    new_route.stops.append(stop)
                    continue

                # Si la parada ya fue vista, es un duplicado
                if stop in seen_stops:
                    # Buscar una parada faltante de los padres para reemplazar
                    feasible_stops = [s for s in parent_stops if s not in seen_stops]
                    if feasible_stops:
                        new_stop = random.choice(feasible_stops)
                        new_route.stops.append(new_stop)
                        seen_stops.append(new_stop)
                else:
                    new_route.stops.append(stop)
                    seen_stops.append(stop)

            new_route.students = sum(s.num_assigned_students for s in new_route.stops)
            new_routes.append(new_route)

        child.set_representation(new_routes)

    def _ensure_all_mandatory_stops(self, child: SolutionRouteSBRP, problem: ProblemSBRP):
        """
        Asegura que TODAS las paradas con estudiantes del problema estén en la solución.
        """
        # Obtener todas las paradas del problema con estudiantes
        mandatory_stops = [stop for stop in problem.stops if stop.num_assigned_students > 0]

        # Paradas presentes en el hijo
        child_stops = [stop for route in child.get_representation() for stop in route.stops]

        # Para cada parada obligatoria faltante
        for stop in mandatory_stops:
            if stop not in child_stops:
                self._force_insert_stop(child, stop, problem.bus_capacity)

    def _force_insert_stop(self, child: SolutionRouteSBRP, stop: Stop, bus_capacity: int):
        """
        Inserta una parada en la solución, creando una nueva ruta si es necesario.
        """
        # Intentar añadir a rutas existentes
        for route in child.get_representation():
            if route.students + stop.num_assigned_students <= bus_capacity:
                route.stops.insert(-1, stop)  # Insertar antes de la escuela
                route.students += stop.num_assigned_students
                return

        # Crear nueva ruta si no hay espacio
        school = child.get_representation()[0].stops[0] if child.get_representation() else School(id=0, name="School", coordinates=(0,0))
        new_route = Route(stops=[school, stop, school])
        new_route.students = stop.num_assigned_students
        child.get_representation().append(new_route)

    def _get_unique_parent_stops(self, parents):
        """
        Obtiene todas las paradas únicas de las soluciones padres.
        """
        unique_stops = []
        for parent in parents:
            for route in parent.get_representation():
                for stop in route.stops:
                    if not isinstance(stop, School) and stop not in unique_stops:
                        unique_stops.append(stop)
        return unique_stops

