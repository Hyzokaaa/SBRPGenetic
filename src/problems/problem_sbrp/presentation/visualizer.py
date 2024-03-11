import os

import numpy as np
from matplotlib import pyplot as plt
from src.problems.problem_sbrp.domain.model.sbrp import SBRP
import matplotlib
matplotlib.use('TkAgg')  # o 'tkagg' dependiendo del sistema operativo


class Visualizer:
    @staticmethod
    def plot_assignments(sbrp: SBRP):
        plt.figure()

        # Dibuja las paradas como puntos rojos
        for stop in sbrp.stops:
            plt.plot(stop.coord_x, stop.coord_y, 'ro')

        # Dibuja los estudiantes como puntos azules y líneas desde cada estudiante a su parada asignada
        for student in sbrp.students:
            plt.plot(student.coord_x, student.coord_y, 'bo')
            if student.assigned_stop is not None:
                plt.plot([student.coord_x, student.assigned_stop.coord_x],
                         [student.coord_y, student.assigned_stop.coord_y], 'k-')

        plt.show()

    @staticmethod
    def plot_routes(sbrp: SBRP, routes, image_name):
        plt.figure()

        # Dibuja las paradas como puntos rojos
        for stop in sbrp.stops:
            plt.scatter(stop.coord_x, stop.coord_y, color='red', s=100)

        plt.scatter(sbrp.school.coord_y, sbrp.school.coord_y, color='green', s=200)

        # Dibuja los estudiantes como puntos azules y líneas desde cada estudiante a su parada asignada
        for student in sbrp.students:
            plt.plot(student.coord_x, student.coord_y, 'bo')
            if student.assigned_stop is not None:
                plt.plot([student.coord_x, student.assigned_stop.coord_x],
                         [student.coord_y, student.assigned_stop.coord_y], 'k-')

        # Dibuja las rutas como líneas de colores aleatorios
        for route in routes:
            # Genera un color aleatorio distinto de blanco o negro
            color = np.random.rand(3, )
            while np.all(color < 0.5) or np.all(color > 0.9):  # Evita colores oscuros y claros
                color = np.random.rand(3, )

            for i in range(len(route.stops) - 1):
                stop1 = route.stops[i]
                stop2 = route.stops[i + 1]
                plt.plot([stop1.coord_x, stop2.coord_x], [stop1.coord_y, stop2.coord_y], color=color)

                # Añade anotaciones para indicar el orden de las paradas
                plt.annotate(str(i), (stop1.coord_x, stop1.coord_y), color=color, weight='bold', fontsize=12)

        # Define la ruta de la imagen
        route = "T-MH/"
        base_name = image_name
        ext = ".png"
        counter = 1
        file_path = f"{route}{base_name}{ext}"

        # Verifica si el archivo ya existe y, si es así, añade un número al final del nombre del archivo
        while os.path.exists(file_path):
            file_path = f"{route}{base_name}{counter}{ext}"
            counter += 1

        # Guarda la imagen
        plt.savefig(file_path, dpi=300)
        plt.show()
