from abc import ABC, abstractmethod


class DataInput(ABC):
    @abstractmethod
    def read_parameters(self):
        pass

    @abstractmethod
    def read_school_coordinates(self, arg=None):
        pass

    @abstractmethod
    def read_stop_coordinates(self, m=None):
        pass

    @abstractmethod
    def read_student_coordinates(self, n=None):
        pass
