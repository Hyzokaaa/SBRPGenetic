import os

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

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
    def plot_routes(sbrp: SBRP, routes, image_path: str):
        plt.figure(figsize=(14, 10))  # Aumentar tamaño base

        # 1. Crear manualmente los handles para la leyenda estática
        static_handles = [
            plt.Line2D([], [], color='green', marker='o', linestyle='None',
                       markersize=10, label='Colegio'),
            plt.Line2D([], [], color='red', marker='o', linestyle='None',
                       markersize=6, label='Paradas'),
            plt.Line2D([], [], color='blue', marker='o', linestyle='None',
                       markersize=4, label='Estudiantes')
        ]

        # 2. Dibujar elementos sin labels automáticos
        # Escuela
        plt.scatter(sbrp.school.coordinates[0], sbrp.school.coordinates[1],
                    color='green', s=450, zorder=10)

        # Paradas
        plt.scatter([stop.coordinates[0] for stop in sbrp.stops],
                    [stop.coordinates[1] for stop in sbrp.stops],
                    color='red', s=50, zorder=2)

        # Estudiantes
        for student in sbrp.students:
            plt.plot(student.coordinates[0], student.coordinates[1], 'bo',
                     markersize=5, zorder=1)
            if student.assigned_stop:
                plt.plot([student.coordinates[0], student.assigned_stop.coordinates[0]],
                         [student.coordinates[1], student.assigned_stop.coordinates[1]],
                         'k-', linewidth=0.5, alpha=0.3)

        # 3. Dibujar rutas y preparar sus leyendas
        route_handles = []
        for route_idx, route in enumerate(routes.get_representation()):
            color = np.random.rand(3, )
            while np.mean(color) < 0.4 or np.mean(color) > 0.6:  # Mejor rango de contraste
                color = np.random.rand(3, )

            # Dibujar ruta
            stops_x = [stop.coordinates[0] for stop in route.stops]
            stops_y = [stop.coordinates[1] for stop in route.stops]
            line = plt.plot(stops_x, stops_y, color=color, linewidth=2.5,
                            zorder=4, solid_capstyle='round')[0]

            # Crear entrada de leyenda SOLO si tiene estudiantes
            if route.students > 0:  # <--- Condición agregada
                route_handles.append(
                    plt.Line2D([], [], color=color, linewidth=2.5,
                               label=f'Ruta {route_idx + 1}: {route.students} estudiantes')
                )

            # Numeración de paradas
            for i, stop in enumerate(route.stops):
                plt.annotate(str(i + 1), stop.coordinates,
                             color='white' if np.mean(color) < 0.5 else 'black',
                             weight='bold', fontsize=9,
                             ha='center', va='center', zorder=5,
                             bbox=dict(boxstyle="circle,pad=0.3",
                                       fc=color, ec="black", lw=0.5))

        # 4. Configurar leyendas de forma explícita
        fig = plt.gcf()

        # Leyenda estática (derecha superior)
        leg1 = fig.legend(handles=static_handles, loc='upper left',
                          bbox_to_anchor=(0.82, 0.95), frameon=True,
                          title="Elementos:", borderpad=1.2)

        # Leyenda de rutas (derecha central)
        if route_handles:
            leg2 = fig.legend(handles=route_handles, loc='upper left',
                              bbox_to_anchor=(0.82, 0.7), frameon=True,
                              title="Rutas:", borderpad=1.2)

        # 5. Ajustes finales críticos
        plt.tight_layout(rect=[0, 0, 0.78, 1])  # 22% de espacio derecho
        plt.subplots_adjust(top=0.95, right=0.78)  # Ajuste fino

        plt.savefig(image_path, dpi=300, bbox_inches='tight', pad_inches=0.3)
        plt.close()