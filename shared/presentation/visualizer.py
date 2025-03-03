import os

import numpy as np
from matplotlib import pyplot as plt
from shared.domain.sbrp import SBRP
import matplotlib

from src.problems.problem_sbrp.model.stop import Stop
from src.problems.problem_sbrp.problem_sbrp import ProblemSBRP
from src.problems.problem_sbrp.solution_route_sbrp import SolutionRouteSBRP

matplotlib.use('TkAgg')  # o 'tkagg' dependiendo del sistema operativo


class Visualizer:
    @staticmethod
    def plot_assignments(sbrp: ProblemSBRP):
        plt.figure()

        # Dibuja las paradas como puntos rojos
        for stop in sbrp.stops:
            plt.plot(stop.coordinates[0], stop.coordinates[1], 'ro')

        # Dibuja los estudiantes como puntos azules y líneas desde cada estudiante a su parada asignada
        for student in sbrp.students:
            plt.plot(student.coordinates[0], student.coordinates[1], 'bo')
            if student.assigned_stop is not None:
                plt.plot([student.coordinates[0], student.assigned_stop.coordinates[0]],
                         [student.coordinates[1], student.assigned_stop.coordinates[1]], 'k-')

        ##plt.show()

    @staticmethod
    def plot_routes(sbrp: SBRP, routes, image_name):
        plt.figure()
        routes: SolutionRouteSBRP = routes
        # Dibuja las paradas como puntos rojos
        for stop in sbrp.stops:
            plt.scatter(stop.coordinates[0], stop.coordinates[1], color='red', s=50)  # Tamaño de los puntos reducido

        plt.scatter(sbrp.school.coordinates[0], sbrp.school.coordinates[1], color='green',
                    s=100)  # Tamaño de los puntos reducido

        # Dibuja los estudiantes como puntos azules y líneas desde cada estudiante a su parada asignada
        for student in sbrp.students:
            plt.plot(student.coordinates[0], student.coordinates[1], 'bo',
                     markersize=5)  # Tamaño de los puntos reducido
            if student.assigned_stop is not None:
                plt.plot([student.coordinates[0], student.assigned_stop.coordinates[0]],
                         [student.coordinates[1], student.assigned_stop.coordinates[1]], 'k-',
                         linewidth=0.5)  # Líneas más finas

        # Dibuja las rutas como líneas de colores aleatorios
        for route in routes.get_representation():
            # Genera un color aleatorio distinto de blanco o negro
            color = np.random.rand(3, )
            while np.all(color < 0.5) or np.all(color > 0.9):  # Evita colores oscuros y claros
                color = np.random.rand(3, )

            for i in range(len(route.stops) - 1):
                stop1: Stop = route.stops[i]
                stop2: Stop = route.stops[i + 1]
                plt.plot([stop1.coordinates[0], stop2.coordinates[0]], [stop1.coordinates[1], stop2.coordinates[1]],
                         color=color,
                         linewidth=1, label=f'Route {i}, Students: {route.students}')  # Líneas más finas

                # Añade anotaciones para indicar el orden de las paradas
                plt.annotate(str(i), (stop1.coordinates[0], stop1.coordinates[1]), color=color, weight='bold',
                             fontsize=12)

        # Añade la leyenda
        plt.legend()

        # Define la ruta de la imagen
        route = "/"
        base_name = image_name
        ext = ".png"
        counter = 1
        file_path = f"{route}{base_name}{ext}"

        # Verifica si el archivo ya existe y, si es así, añade un número al final del nombre del archivo
        while os.path.exists(file_path):
            file_path = f"{route}{base_name}{counter}{ext}"
            counter += 1

        # Guarda la imagen
        plt.savefig(file_path, dpi=1200)
        ##plt.show()
