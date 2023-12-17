from src.routePlanner import RoutePlanner
from src.sbrp import SBRP
from src.stopAssigner import StopAssigner
from src.vizualizer import Visualizer


def main():
    # Crear una instancia de SBRP
    sbrp = SBRP.read_instance("data/instances/test/mi_instancia.xpress")
    # Asignar estudiantes a paradas usando student_to_random_stop()
    StopAssigner.student_to_stop_closest_to_centroid(sbrp)
    # Genera las rutas
    RoutePlanner.generate_routes(sbrp)

    # Imprime las rutas generadas

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

    Visualizer.plot_assignments(sbrp)





if __name__ == "__main__":
    main()

