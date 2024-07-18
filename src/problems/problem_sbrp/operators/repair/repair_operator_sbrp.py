import copy
import random
from typing import List

from src.operators.repair.repair_operator import RepairOperator
from src.operators.repair.repair_parameters import RepairParameters
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP


class RepairOperatorSBRP(RepairOperator):
    def unique_stops(self, solutions):
        unique_stops = []
        for solution in solutions:
            for route in solution.get_representation():
                for stop in route.stops:
                    if not isinstance(stop, School) and stop not in unique_stops:
                        unique_stops.append(stop)
        return unique_stops

    def get_feasible_stops(self, child, unique_stops):
        feasible_stops = []
        child_stops = []

        # Lista las paradas contenidas en la solución
        for route in child.get_representation():
            for stop in route.stops:
                if not isinstance(stop, School):
                    child_stops.append(stop)

        # Lista las paradas que se encuentren dentro de unique_stops y no se encuentren dentro de child_stops
        # (Paradas Factibles)
        for stop in unique_stops:
            if stop not in child_stops:
                feasible_stops.append(stop)


        return feasible_stops
    def repair(self, parameters: RepairParameters):
            childs: List[SolutionRouteSBRP] = copy.deepcopy(parameters.solutions)
            problem: ProblemSBRP = parameters.problem
            parent1 = parameters.parents[0]
            parent2 = parameters.parents[1]

            unique_stops = self.unique_stops([parent1, parent2])

            for child in childs:
                seen_stops = []


                for route in child.get_representation():
                    route.students = sum(stop.num_assigned_students for stop in route.stops)

                    # elimina de la ruta tantas paradas hasta satisfacer condición de capacidad del autobus
                    if route.students > problem.bus_capacity:
                        while route.students > problem.bus_capacity:
                            min_stop = min((stop for stop in route.stops if not isinstance(stop, School)), key=lambda stop: stop.num_assigned_students)
                            route.stops.remove(min_stop)
                            route.students = sum(stop.num_assigned_students for stop in route.stops)

                    # Itera sobre cada parada en cada ruta de la solution en busca de duplicadas
                    i = 1
                    while i < len(route.stops)-1:
                        stop = route.stops[i]
                        # Si la parada no se encuentra dentro de la lista de paradas visitadas la agrega
                        # a la lista de paradas visitadas
                        if stop not in seen_stops:
                            seen_stops.append(stop)
                            i += 1
                        # si se encuentra en las paradas visitadas, sustituye la parada por una factible
                        else:
                            feasible_stops_for_rute = self.feasible_for_route(child,
                                                                              unique_stops,
                                                                              problem.bus_capacity,
                                                                              route)
                            if feasible_stops_for_rute:
                                random_stop: Stop = random.choice(feasible_stops_for_rute)
                                route.stops[i] = random_stop
                                route.students = sum(stop.num_assigned_students for stop in route.stops)
                                i += 1
                            else:
                                route.stops.pop(i)
                                i += 1
                # agrega las paradas faltantes a rutas factibles
                for stop in self.get_feasible_stops(child,unique_stops):
                    for route in child.get_representation():
                        route.students = sum(stop.num_assigned_students for stop in route.stops)
                        if (route.students + stop.num_assigned_students <= problem.bus_capacity and
                                stop not in route.stops):
                            route.stops.insert(len(route.stops) - 1, stop)
                            route.students = sum(stop.num_assigned_students for stop in route.stops)
                            break
            return childs
    def feasible_for_route(self, child, unique_stops, bus_capacity, route):
        child_stops = [stop for stop in [route.stops for route in child.get_representation()]]

        route.students = sum(stop.num_assigned_students for stop in route.stops)

        feasible_stops = [stop for stop in unique_stops if stop not in child_stops
                          and route.students + stop.num_assigned_students <= bus_capacity]
        return feasible_stops