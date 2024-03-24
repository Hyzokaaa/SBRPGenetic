from abc import ABC, abstractmethod


class DataInput(ABC):
    @abstractmethod
    def conform(self):
        pass
