from matplotlib import pyplot as plt
from src.model.sbrp import SBRP
import matplotlib
matplotlib.use('TkAgg')  # o 'tkagg' dependiendo del sistema operativo


class Visualizer:
    @staticmethod
    def plot_assignments(sbrp: SBRP):
        # Crea una nueva figura
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

        # Muestra el gráfico
        plt.show()
