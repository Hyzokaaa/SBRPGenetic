from src.problems.problem_sbrp.data_io.datainput import DataInput


class FileDataInput(DataInput):
    def __init__(self, file_path):
        self.file = open(file_path, 'r')

    def read_parameters(self):
        return map(int, self.file.readline().split())

    def read_school_coordinates(self, arg=None):
        return map(float, self.file.readline().split())

    def read_stop_coordinates(self, m=None):
        return [(float(coord_x), float(coord_y)) for coord_x, coord_y in
                (self.file.readline().split() for _ in range(m))]

    def read_student_coordinates(self, n=None):
        return [(float(coord_x), float(coord_y)) for coord_x, coord_y in
                (self.file.readline().split() for _ in range(n))]
