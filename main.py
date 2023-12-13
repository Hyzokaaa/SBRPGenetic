from src.sbrp import SBRP
from src.utils import Utils


def main():
    sbrp = SBRP.read_instance('2.xpress')

    # Asignar estudiantes a paradas usando cercanía()
    sbrp.student_to_stop_closest_to_centroid()

    for student in sbrp.students:
        print(f"Student {student.id} " + f"in {student.coord_x, student.coord_y} assigned to Stop "
                                         f"{student.assigned_stop.id if student.assigned_stop else None} ")

    print(f"{sbrp.school.coord_y}" + " " + f"{sbrp.school.coord_y}")
    print(sbrp.max_distance)
    print(sbrp.bus_capacity)


if __name__ == "__main__":
    main()
