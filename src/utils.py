from typing import List

import numpy as np

from src.stop import Stop


class Utils:
    @staticmethod
    def calculate_distance(coord1_x, coord1_y, coord2_x, coord2_y):
        return np.sqrt((coord1_x - coord2_x) ** 2 + (coord1_y - coord2_y) ** 2)

    @staticmethod
    def calculate_cost_matrix(entities1, entities2):
        # Inicializa una matriz de ceros con dimensiones (número de entidades1, número de entidades2)
        cost_matrix = np.zeros((len(entities1), len(entities2)))

        # Para cada entidad en entities1
        for i, entity1 in enumerate(entities1):
            # Para cada entidad en entities2
            for j, entity2 in enumerate(entities2):
                # Calcula la distancia entre las dos entidades
                distance = Utils.calculate_distance(entity1.coord_x, entity1.coord_y, entity2.coord_x, entity2.coord_y)

                # Asigna esta distancia a la matriz de costos
                cost_matrix[entity1.id][entity2.id] = distance

        return cost_matrix

    @staticmethod
    def calculate_centroid(stops: List[Stop]):
        sum_x = sum(stop.coord_x for stop in stops)
        sum_y = sum(stop.coord_y for stop in stops)
        centroid_x = sum_x / len(stops)
        centroid_y = sum_y / len(stops)
        return centroid_x, centroid_y

