from collections import Counter, OrderedDict
from typing import List, Tuple

import numpy as np

from src.problems.problem import Problem
from src.problems.problem_parameters import ProblemParameters
from src.problems.problem_sbrp.model.bus import Bus
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.model.student import Student

# Número máximo de soluciones distintas cuya evaluación se conserva en caché
EVALUATION_CACHE_SIZE = 50000


class ProblemSBRP(Problem):
    def __init__(self):
        self.distance_calculator = None
        self.school: School = None
        self.stops: List[Stop] = None
        self.students: List[Student] = None
        self.vehicles: List[Bus] = None
        self.bus_capacity = None
        self.w_distance = None
        self.assign_solution = None
        self.best_solution = None
        self.distance_matrix = None
        # Caché de evaluaciones (distancia y restricciones) indexada por la secuencia de paradas de las rutas
        self._evaluation_cache = OrderedDict()

    def construct(self, problem_parameters: ProblemParameters):
        self.distance_calculator = problem_parameters.distance_operator
        self.school = School(id=0, name='School', coordinates=problem_parameters.sbrp_school_coordinates)
        self.    stops = [Stop(id=i + 1, name=f"Stop {i + 1}", coordinates=coordinates)
                          for i, (coordinates) in enumerate(problem_parameters.sbrp_stops_coordinates)]
        self.students = [Student(id=i, name=f"Student {i}", coordinates=coordinates)
                         for i, (coordinates) in enumerate(problem_parameters.sbrp_student_coordinates)]
        self.vehicles = [Bus(id=i, name=f"Bus{i}")for i in range(problem_parameters.sbrp_vehicles)]
        self.bus_capacity = problem_parameters.sbrp_bus_capacity
        self.w_distance = problem_parameters.sbrp_walk_distance
        # Precalcular distancias entre todas las paradas
        self.distance_matrix = self._build_distance_matrix()
        self.clear_evaluation_cache()

    def clear_evaluation_cache(self):
        """
        Vacía la caché de evaluaciones. Debe llamarse si cambia la asignación de estudiantes a paradas,
        ya que las restricciones dependen de ella.
        """
        self._evaluation_cache = OrderedDict()
        # Invalida las evaluaciones guardadas en las soluciones congeladas (ver freeze)
        self._cache_version = getattr(self, "_cache_version", 0) + 1

    def freeze(self, solution, signature=None):
        """
        Guarda en la solución su clave de caché, su entrada y su firma, para no recorrer sus rutas en cada consulta.
        Solo debe usarse con soluciones que ya no se modificarán (las de la población): una copia (solution.copy())
        no conserva lo guardado y se puede modificar sin problema. signature evita recalcular una firma ya conocida.
        """
        if self._frozen(solution) is not None:
            return
        key = self.evaluation_key(solution)
        signature = self.solution_signature(solution) if signature is None else signature
        solution._frozen_evaluation = (self._cache_version, key, self._entry_for_key(key), signature)

    def _frozen(self, solution):
        frozen = getattr(solution, "_frozen_evaluation", None)
        return frozen if frozen is not None and frozen[0] == self._cache_version else None

    @staticmethod
    def evaluation_key(solution) -> tuple:
        """Clave de la caché: la secuencia de identificadores de paradas de cada ruta."""
        return tuple(tuple(-1 if stop is None else stop.id for stop in route.stops)
                     for route in solution.get_representation())

    def _cache_entry(self, solution) -> dict:
        """
        Entrada de la caché de la solución. La clave es la secuencia de identificadores de paradas de cada ruta,
        por lo que cualquier cambio en las rutas (por ejemplo, una mutación) da lugar a otra entrada. Las soluciones
        congeladas guardan su entrada y no recalculan la clave.
        """
        frozen = self._frozen(solution)
        if frozen is not None:
            return frozen[2]
        return self._entry_for_key(self.evaluation_key(solution))

    def _entry_for_key(self, key) -> dict:
        entry = self._evaluation_cache.get(key)
        if entry is None:
            entry = {}
            self._evaluation_cache[key] = entry
            if len(self._evaluation_cache) > EVALUATION_CACHE_SIZE:
                self._evaluation_cache.popitem(last=False)
        else:
            self._evaluation_cache.move_to_end(key)
        return entry

    def _build_distance_matrix(self):
        stops = [self.school] + self.stops
        n = len(stops)
        matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                matrix[i][j] = self.distance_calculator.calculate_distance(stops[i].coordinates, stops[j].coordinates)
        return matrix

    def objective_function(self, solution):
        entry = self._cache_entry(solution)
        if "fitness" not in entry:
            entry["fitness"] = self._compute_fitness(solution)
        return entry["fitness"]

    def _compute_fitness(self, solution):
        fitness = 0
        for route in solution.get_representation():
            stops = [self.school] + route.stops + [self.school]  # Asume que las rutas incluyen la escuela
            for i in range(len(stops) - 1):
                fitness += self.distance_matrix[stops[i].id][stops[i + 1].id]
        return fitness

    def compare_solutions(self, solution1, solution2, objective_max):
        best_solution = solution1
        if best_solution is None or (
                objective_max and self.objective_function(solution2) >
                self.objective_function(best_solution)
        ) or (
                not objective_max and self.objective_function(solution2) <
                self.objective_function(best_solution)
        ):
            best_solution = solution2
        return best_solution

    def violations(self, solution) -> List[str]:
        """
        Devuelve la lista de restricciones que incumple la solución (vacía si es factible).
        """
        return list(self._cached_constraints(solution)[0])

    def constraint_violation(self, solution) -> int:
        """
        Grado de violación de la solución (0 si es factible). Suma los estudiantes sin recoger,
        los estudiantes que exceden la capacidad, las visitas repetidas, las rutas que exceden
        la flota y las rutas mal formadas. Se usa para comparar soluciones infactibles en la selección.
        """
        return self._cached_constraints(solution)[1]

    def _cached_constraints(self, solution) -> Tuple[Tuple[str, ...], int]:
        entry = self._cache_entry(solution)
        if "constraints" not in entry:
            violations, degree = self._evaluate_constraints(solution)
            entry["constraints"] = (tuple(violations), degree)
        return entry["constraints"]

    def _evaluate_constraints(self, solution) -> Tuple[List[str], int]:
        routes = solution.get_representation()
        loads = {stop.id: stop.num_assigned_students for stop in self.stops}
        mandatory = {stop_id for stop_id, load in loads.items() if load > 0}
        visits = Counter()
        violations = []
        degree = 0

        for i, route in enumerate(routes):
            if any(stop is None for stop in route.stops):
                violations.append(f"Ruta {i} contiene paradas nulas")
                degree += 1
                continue
            if (len(route.stops) < 2 or not isinstance(route.stops[0], School)
                    or not isinstance(route.stops[-1], School)
                    or any(isinstance(stop, School) for stop in route.stops[1:-1])):
                violations.append(f"Ruta {i} no sale y regresa a la escuela")
                degree += 1
            route_stops = [stop for stop in route.stops if not isinstance(stop, School)]
            visits.update(stop.id for stop in route_stops)
            load = sum(loads.get(stop.id, 0) for stop in route_stops)
            if load > self.bus_capacity:
                violations.append(f"Ruta {i} excede la capacidad: {load} > {self.bus_capacity}")
                degree += load - self.bus_capacity

        used_routes = sum(1 for route in routes if any(
            stop is not None and not isinstance(stop, School) for stop in route.stops))
        if used_routes > len(self.vehicles):
            violations.append(f"Rutas utilizadas exceden la flota: {used_routes} > {len(self.vehicles)}")
            degree += used_routes - len(self.vehicles)

        missing = sorted(mandatory - set(visits))
        if missing:
            violations.append(f"Paradas con estudiantes sin visitar: {missing}")
            degree += sum(loads[stop_id] for stop_id in missing)
        duplicated = sorted(stop_id for stop_id, count in visits.items() if count > 1)
        if duplicated:
            violations.append(f"Paradas visitadas más de una vez: {duplicated}")
            degree += sum(visits[stop_id] - 1 for stop_id in duplicated)

        return violations, degree

    def solution_signature(self, solution):
        """
        Conjunto de rutas como secuencias de paradas; una ruta y su recorrido inverso son la misma ruta.
        """
        frozen = self._frozen(solution)
        if frozen is not None:
            return frozen[3]
        routes = []
        for route in solution.get_representation():
            ids = tuple(stop.id for stop in route.stops if stop is not None and not isinstance(stop, School))
            if ids:
                routes.append(min(ids, ids[::-1]))
        return tuple(sorted(routes))

    def is_feasible(self, solution) -> bool:
        return not self.violations(solution)

    def update_best_solution(self, best_iteration, current_iteration, objective_max, population):
        for new_solution in population:
            # Solo las soluciones factibles pueden convertirse en la mejor solución
            if not self.is_feasible(new_solution):
                continue
            updated_solution = self.compare_solutions(solution1=self.best_solution, solution2=new_solution,
                                                      objective_max=objective_max)

            if updated_solution != self.best_solution:
                best_iteration = current_iteration
                self.best_solution = updated_solution
        return best_iteration

    def __str__(self):
        return 'ProblemSBRP'
