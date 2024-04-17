import random

from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.problems.problem_sbrp.model.route import Route


class StopCrossoverOperatorSBRP(CrossoverOperator):
    def crossover(self, parameters: CrossoverParameters):
        parent1, parent2 = parameters.parent1, parameters.parent2

        new_parent1 = []
        new_parent2 = []

        # Realiza el cruce para cada par de rutas correspondientes
        for route1, route2 in zip(parent1, parent2):
            # Si una ruta solo tiene dos paradas y ambas son la parada de id 0, no realiza el cruce
            if len(route1.stops) > 2 and len(route2.stops) > 2:
                stops1 = route1.stops[1:-1]  # Excluye la primera y última parada
                stops2 = route2.stops[1:-1]  # Excluye la primera y última parada

                size = min(len(stops1), len(stops2))
                cxpoint = random.randint(1, size)

                new_stops1 = stops1[:cxpoint] + stops2[cxpoint:]
                new_stops2 = stops2[:cxpoint] + stops1[cxpoint:]

                # Crea nuevas rutas con las paradas cruzadas, manteniendo la primera y última parada
                new_route1 = Route(stops=[route1.stops[0]] + new_stops1 + [route1.stops[-1]])
                new_route2 = Route(stops=[route2.stops[0]] + new_stops2 + [route2.stops[-1]])

                new_parent1.append(new_route1)
                new_parent2.append(new_route2)
            else:
                # Si una ruta solo tiene dos paradas, la mantiene tal cual
                new_parent1.append(route1)
                new_parent2.append(route2)

        return new_parent1, new_parent2