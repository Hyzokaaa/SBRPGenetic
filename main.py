from src.sbrp import SBRP
from src.school import School
from src.stop import Stop
from src.student import Student


def main():
    # Crear una instancia de SBRP
    sbrp = SBRP.read_instance("inst10-1s5-50-c50-w5.xpress")
    # Asignar estudiantes a paradas usando student_to_random_stop()
    sbrp.student_to_random_stop()

    for student in sbrp.students:
        if student.assigned_stop is not None:
            print(
                f"Student {student.id} in {student.coord_x, student.coord_y} assigned to Stop {student.assigned_stop.id} in {student.assigned_stop.coord_x, student.assigned_stop.coord_y}")
        else:
            print(f"Student {student.id} in {student.coord_x, student.coord_y} was not assigned to a stop.")

    print("school coord = " + f"{sbrp.school.coord_x,sbrp.school.coord_y}")
    print("max distance = " + f"{sbrp.max_distance}")
    print("capacity of bus = " f"{sbrp.bus_capacity}")

if __name__ == "__main__":
    main()

