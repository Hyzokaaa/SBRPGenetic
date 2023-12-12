import random


class SBRP:
    def __init__(self, school, stops, students, routes, max_distance, bus_capacity, stop_cost, student_stop_cost):
        self.school = school
        self.stops = stops
        self.students = students
        self.routes = routes
        self.max_distance = max_distance
        self.bus_capacity = bus_capacity
        self.stop_cost_matrix = stop_cost
        self.student_stop_cost_matrix = student_stop_cost

    def studentToStop(self):
        # Para cada estudiante en la lista de estudiantes
        for student in self.students:
            # Encuentra las paradas que están dentro de la distancia máxima
            valid_stops = [stop for stop in self.stops if
                           self.student_stop_cost_matrix[student.id][stop.id] <= self.max_distance]

            # Si no hay paradas válidas, entonces no asignamos ninguna parada a este estudiante
            if not valid_stops:
                student.assigned_stop = None
            else:
                # Encuentra la parada más cercana entre las paradas válidas
                closest_stop = min(valid_stops, key=lambda stop: self.student_stop_cost_matrix[student.id][stop.id])

                # Asigna al estudiante a la parada más cercana
                student.assigned_stop = closest_stop

                # Añade al estudiante a la lista de estudiantes asignados a esa parada
                closest_stop.num_assigned_students += 1

    def studentToRandomStop(self):
        # Para cada estudiante en la lista de estudiantes
        for student in self.students:
            # Encuentra las paradas que están dentro de la distancia máxima
            valid_stops = [stop for stop in self.stops if
                           self.student_stop_cost_matrix[student.id][stop.id] <= self.max_distance]

            # Si no hay paradas válidas, entonces no asignamos ninguna parada a este estudiante
            if not valid_stops:
                student.assigned_stop = None
            else:
                # Selecciona una parada aleatoria entre las paradas válidas
                random_stop = random.choice(valid_stops)

                # Asigna al estudiante a la parada aleatoria
                student.assigned_stop = random_stop

                # Añade al estudiante a la lista de estudiantes asignados a esa parada
                random_stop.num_assigned_students += 1
