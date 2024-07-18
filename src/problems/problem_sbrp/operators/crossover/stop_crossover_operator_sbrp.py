import random

from src.operators.crossover.crossover_operator import CrossoverOperator
from src.operators.crossover.crossover_parameters import CrossoverParameters
from src.problems.problem_sbrp.model.route import Route
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
