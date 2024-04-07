import random

from src.operators.mutation.mutation_operator import MutationOperator
from src.operators.mutation.mutation_parameters import MutationParameters
from src.problems.problem_sbrp.model.school import School
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP


class SwapMutationOperatorSBRP(MutationOperator):
    def mutate(self, parameters: MutationParameters):
        problem: ProblemSBRP = parameters.problem
        # Crea una copia de las rutas para poder iterar sobre ellas
        solution = parameters.solution
        routes = parameters.solution.copy()

        # Mezcla las rutas para intentar con ellas en un orden aleatorio
        random.shuffle(routes)

        for route1 in routes:
            for route2 in routes:
                if route1 != route2:
                    # Crea una copia de las paradas en la primera ruta para poder iterar sobre ellas
                    stops1 = [stop for stop in route1.stops if not isinstance(stop, School)]

                    # Mezcla las paradas para intentar con ellas en un orden aleatorio
                    random.shuffle(stops1)

                    for stop1 in stops1:
                        # Encuentra todas las paradas en la segunda ruta que podrían ser intercambiadas
                        # sin exceder la capacidad del autobús
                        feasible_stops = [stop for stop in route2.stops if not isinstance(stop, School) and
                                          route1.students - stop1.num_assigned_students + stop.num_assigned_students <=
                                          problem.bus_capacity and route2.students - stop.num_assigned_students +
                                          stop1.num_assigned_students <= problem.bus_capacity]

                        # Si hay paradas factibles, selecciona una al azar
                        if feasible_stops:
                            stop2 = random.choice(feasible_stops)

                            # Encuentra los índices de las paradas seleccionadas
                            index1 = route1.stops.index(stop1)
                            index2 = route2.stops.index(stop2)

                            # Intercambia las paradas
                            route1.stops[index1], route2.stops[index2] = route2.stops[index2], route1.stops[index1]
                            route1.students = route1.students - stop1.num_assigned_students + stop2.num_assigned_students
                            route2.students = route2.students - stop2.num_assigned_students + stop1.num_assigned_students

                            # Si se ha realizado un intercambio factible, termina la mutación
                            return solution

        # Si no se ha encontrado ningún intercambio factible después de probar todas las paradas,
        # devuelve la solución sin modificar
        return solution

