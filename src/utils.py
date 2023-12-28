from typing import List

import numpy as np

from src.stop import Stop
from src.student import Student


class Utils:
    @staticmethod
    def calculate_distance(coord1_x, coord1_y, coord2_x, coord2_y):
        return np.sqrt((coord1_x - coord2_x) ** 2 + (coord1_y - coord2_y) ** 2)

    @staticmethod
    def calculate_cost_matrix(sbrp, entities1, entities2):
        cost_matrix = np.zeros((len(entities1), len(entities2)))

        if isinstance(entities1[0], Student):
            id_to_index1 = sbrp.id_to_index_students
        else:
            id_to_index1 = sbrp.id_to_index_stops

        if isinstance(entities2[0], Student):
            id_to_index2 = sbrp.id_to_index_students
        else:
            id_to_index2 = sbrp.id_to_index_stops

        for entity1 in entities1:
            for entity2 in entities2:
                distance = Utils.calculate_distance(entity1.coord_x, entity1.coord_y, entity2.coord_x, entity2.coord_y)
                cost_matrix[id_to_index1[entity1.id]][id_to_index2[entity2.id]] = distance

        return cost_matrix

    @staticmethod
    def calculate_centroid(stops: List[Stop]):
        sum_x = sum(stop.coord_x for stop in stops)
        sum_y = sum(stop.coord_y for stop in stops)
        centroid_x = sum_x / len(stops)
        centroid_y = sum_y / len(stops)
        return centroid_x, centroid_y

