from src.sbrp import SBRP
from src.utils import Utils


def main():
    sbrp = SBRP.read_instance('10.xpress')

    # Calcular la matriz de costos
    sbrp.student_stop_cost_matrix = Utils.calculate_cost_matrix(sbrp.students, sbrp.stops)

    # Asignar estudiantes a paradas usando cercanía()
    sbrp.student_to_stop_closest_to_school()

    for student in sbrp.students:
        print(f"Student {student.id} " + f"in {student.coord_x, student.coord_y} assigned to Stop "
                                         f"{student.assigned_stop.id if student.assigned_stop else None} " +
                                         f"in {student.assigned_stop.coord_x, student.assigned_stop.coord_y}")

    print(f"{sbrp.school.coord_y}" + " " + f"{sbrp.school.coord_y}")
    print(sbrp.max_distance)


if __name__ == "__main__":
    main()
