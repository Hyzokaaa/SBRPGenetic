import numpy as np


class Utils:
    @staticmethod
    def calculate_distance(coord1, coord2):
        return np.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

    @staticmethod
    def calculate_cost_matrix(entities1, entities2):
        # Inicializa una matriz de ceros con dimensiones (número de entidades1, número de entidades2)
        cost_matrix = np.zeros((len(entities1), len(entities2)))

        # Para cada entidad en entities1
        for i, entity1 in enumerate(entities1):
            # Para cada entidad en entities2
            for j, entity2 in enumerate(entities2):
                # Calcula la distancia entre las dos entidades
                distance = Utils.calculate_distance(entity1.coordinates, entity2.coordinates)

                # Asigna esta distancia a la matriz de costos
                cost_matrix[i][j] = distance

        return cost_matrix