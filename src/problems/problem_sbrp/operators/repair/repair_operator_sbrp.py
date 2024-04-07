import copy
import random

from src.operators.repair.repair_operator import RepairOperator
from src.operators.repair.repair_parameters import RepairParameters
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class RepairOperatorSBRP(RepairOperator):

    def repair(self, parameters: RepairParameters):
        childs = copy.deepcopy(parameters.solutions)
        problem: ProblemSBRP = parameters.problem
        parent1 = parameters.parents[0]
        parent2 = parameters.parents[1]

        unique_stops = self.unique_stops([parent1, parent2])

        for child in childs:
            feasible_stops = self.get_feasible_stops(child, unique_stops)

            seen_stops = []

            # Itera sobre cada parada en cada ruta de la solution
            for route in child:
                i = 0
                while i < len(route.stops):
                    stop = route.stops[i]
                    # Si la parada no es la escuela
                    if not isinstance(stop, School):
                        # Si la parada no se encuentra dentro de la lista de paradas visitadas la agrega a la lista
                        if stop not in seen_stops:
                            seen_stops.append(stop)
                            i += 1
                        # si se encuentra en las paradas visitadas, sustituye la parada por una factible
                        else:
                            if feasible_stops:
                                random_stop: Stop = random.choice(feasible_stops)
                                if (route.students - stop.num_assigned_students + random_stop.num_assigned_students <
                                        problem.bus_capacity):
                                    feasible_stops.remove(random_stop)
                                    route.stops[i] = random_stop
                                    route.students = (route.students - stop.num_assigned_students +
                                                      random_stop.num_assigned_students)
                                    i += 1
                                else:
                                    route.students -= route.stops[i].num_assigned_students
                                    route.stops.pop(i)
                                    i += 1
                            else:
                                route.students -= route.stops[i].num_assigned_students
                                route.stops.pop(i)
                                i += 1
                    else:
                        i += 1

            # Segunda parte
            if len(feasible_stops) > 0:
                for stop in feasible_stops:
                    for route in child:
                        if route.students + stop.num_assigned_students <= problem.bus_capacity and stop not in route.stops:
                            route.stops.insert(len(route.stops) - 1, stop)
                            route.students += stop.num_assigned_students
                            break

        return childs

    def unique_stops(self, solutions):
        unique_stops = []
        for solution in solutions:
            for route in solution:
                for stop in route.stops:
                    if not isinstance(stop, School) and stop not in unique_stops:
                        unique_stops.append(stop)
        return unique_stops

    def get_feasible_stops(self, child, unique_stops):
        feasible_stops = []
        child_stops = []

        # Lista las paradas contenidas en la solución
        for route in child:
            for stop in route.stops:
                if not isinstance(stop, School):
                    child_stops.append(stop)

        # Lista las paradas que se encuentren dentro de unique_stops y no se encuentren dentro de child_stops
        # (Paradas Factibles)
        for stop in unique_stops:
            if stop not in child_stops:
                feasible_stops.append(stop)

        return feasible_stops
