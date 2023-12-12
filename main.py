# This is a sample Python script.
from src.sbrp import SBRP
from src.stop import Stop
from src.student import Student
from src.utils import Utils


# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def main():
    # Crear algunos estudiantes y paradas para probar
    students = [Student(id=i, name=f"Student {i}", coord_x=i, coord_y=i) for i in range(10)]
    stops = [Stop(id=i, name=f"Stop {i}", coord_x=10, coord_y=10) for i in range(5)]

    # Crear una instancia de SBRP
    sbrp = SBRP(school=None, stops=stops, students=students, routes=[], max_distance=10, bus_capacity=5, stop_cost=None, student_stop_cost=None)

    # Calcular la matriz de costos
    sbrp.student_stop_cost_matrix = Utils.calculate_cost_matrix(students, stops)

    # Asignar estudiantes a paradas usando studentToStop()
    sbrp.studentToStop()

    # Imprimir las paradas asignadas a cada estudiante
    for student in students:
        print(f"Student {student.id} assigned to better Stop {student.assigned_stop.id if student.assigned_stop else None}")

    print("")

    # Asignar estudiantes a paradas usando studentToRandomStop()
    sbrp.studentToRandomStop()

    # Imprimir las paradas asignadas a cada estudiante
    for student in students:
        print(f"Student {student.id} assigned to random Stop {student.assigned_stop.id if student.assigned_stop else None}")


if __name__ == "__main__":
    main()
