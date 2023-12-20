from src.routePlanner import RoutePlanner
from src.sbrp import SBRP
from src.stopAssigner import StopAssigner
from src.vizualizer import Visualizer


def main():
    print("iniciando ejecucion")
    # Crear una instancia de SBRP
    sbrp = SBRP.read_instance("../data/instances/test/inst60-5s20-200-c50-w10.xpress")
    # Asignar estudiantes a paradas usando student_to_random_stop()
    StopAssigner.student_to_better_stop(sbrp)

    for student in sbrp.students:
        if student.assigned_stop is not None:
            print(
                f"Student {student.id} in {student.coord_x, student.coord_y} assigned to Stop {student.assigned_stop.id} in {student.assigned_stop.coord_x, student.assigned_stop.coord_y}")
        else:
            print(f"Student {student.id} in {student.coord_x, student.coord_y} was not assigned to a stop.")

    print("school coord = " + f"{sbrp.school.coord_x,sbrp.school.coord_y}")
    print("max distance = " + f"{sbrp.max_distance}")
    print("capacity of bus = " f"{sbrp.bus_capacity}")
    print("buses: "f"{len(sbrp.buses)}")

    # Generar rutas
    routes = RoutePlanner.generate_routes(sbrp)

    # Imprimir las rutas generadas
    for i, route in enumerate(routes):
        print(f"Ruta {i+1}:")
        for stop in route:
            print(f"Parada ID: {stop.id}, Coordenadas: ({stop.coord_x}, {stop.coord_y})")

    Visualizer.plot_assignments(sbrp)


if __name__ == "__main__":
    main()
