from src.sbrp import SBRP
from src.utils import Utils


def main():
    # Leer la instancia del archivo
    sbrp = SBRP.read_instance('2.xpress')

    # Calcular la matriz de costos
    sbrp.student_stop_cost_matrix = Utils.calculate_cost_matrix(sbrp.students, sbrp.stops)

    # Asignar estudiantes a paradas usando student_to_stop_closest_to_school()
    sbrp.student_to_stop_closest_to_school()

    # Imprimir las paradas asignadas a cada estudiante
    for student in sbrp.students:
        print(f"Student {student.id} =" + f"coord: {student.coord_x, student.coord_y} assigned to Stop {student.assigned_stop.id if student.assigned_stop else None}")

    # Calcular el centroide de las paradas
    centroid_x, centroid_y = sbrp.calculate_centroid()
    print(f"\nCentroid of Stops: ({centroid_x}, {centroid_y})")

    # Encontrar la parada más cercana al centroide
    closest_stop_to_centroid = sbrp.student_to_stop_closest_to_centroid()
    if closest_stop_to_centroid:
        print(f"Stop closest to Centroid: Stop {closest_stop_to_centroid.id}")
    else:
        print("No valid stops found within max distance from centroid.")
        print("la distancia maxima es: " + f"{sbrp.max_distance}")


if __name__ == "__main__":
    main()
