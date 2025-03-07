import random

from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.problems.problem_sbrp.model.route import Route
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP
from src.solution.solution import Solution


class StopCrossoverOperatorSBRP(CrossoverOperator):
    def crossover(self, parameters: CrossoverParameters):
        parent1, parent2 = parameters.parent1.get_representation(), parameters.parent2.get_representation()

        new_parent1_repr = []
        new_parent2_repr = []

        # Perform crossover for each pair of corresponding routes
        for route1, route2 in zip(parent1, parent2):
            # If a route only has two stops and both are stop id 0, do not perform crossover
            if len(route1.stops) > 2 and len(route2.stops) > 2:
                stops1 = route1.stops[1:-1]  # Exclude the first and last stop
                stops2 = route2.stops[1:-1]  # Exclude the first and last stop

                size = min(len(stops1), len(stops2))
                cxpoint = random.randint(1, size)

                new_stops1 = stops1[:cxpoint] + stops2[cxpoint:]
                new_stops2 = stops2[:cxpoint] + stops1[cxpoint:]

                # Create new routes with the crossed stops, keeping the first and last stop
                new_route1 = Route(stops=[route1.stops[0]] + new_stops1 + [route1.stops[-1]])
                new_route2 = Route(stops=[route2.stops[0]] + new_stops2 + [route2.stops[-1]])

                new_parent1_repr.append(new_route1)
                new_parent2_repr.append(new_route2)
            else:
                # If a route only has two stops, keep it as is
                new_parent1_repr.append(route1)
                new_parent2_repr.append(route2)

        # Convert the representations of the children into instances of Solution
        new_parent1 = SolutionRouteSBRP()
        new_parent1.set_representation(new_parent1_repr)
        new_parent2 = SolutionRouteSBRP()
        new_parent2.set_representation(new_parent2_repr)

        return new_parent1, new_parent2


    def _ensure_mandatory_stops(self, child: SolutionRouteSBRP, problem: ProblemSBRP):
        """
        Asegura que todas las paradas con estudiantes estén en la solución.
        """
        # Obtener todas las paradas con estudiantes de los padres
        mandatory_stops = [stop for stop in problem.stops if stop.num_assigned_students > 0]

        # Verificar cada parada obligatoria
        for stop in mandatory_stops:
            if not self._is_stop_in_child(child, stop):
                self._force_insert_stop(child, stop, problem.bus_capacity)

    def _force_insert_stop(self, child: SolutionRouteSBRP, stop: Stop, bus_capacity: int):
        """
        Inserta una parada obligatoria en la solución, incluso si es necesario crear una nueva ruta.
        """
        # Intentar insertar en rutas existentes
        for route in child.get_representation():
            if route.students + stop.num_assigned_students <= bus_capacity:
                route.stops.insert(-1, stop)  # Insertar antes de la escuela
                route.students += stop.num_assigned_students
                return

        # Si no hay espacio, crear nueva ruta solo para esta parada
        school = child.get_representation()[0].stops[0]  # La escuela es el primer stop de la primera ruta
        new_route = Route(stops=[school, stop, school])
        new_route.students = stop.num_assigned_students
        child.get_representation().append(new_route)

    def _is_stop_in_child(self, child: SolutionRouteSBRP, stop: Stop) -> bool:
        """
        Verifica si una parada está presente en alguna ruta de la solución.
        """
        for route in child.get_representation():
            if stop in route.stops:
                return True
        return False