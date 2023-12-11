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
