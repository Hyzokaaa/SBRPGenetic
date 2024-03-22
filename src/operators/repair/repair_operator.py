from abc import ABC, abstractmethod


class RepairOperator(ABC):
    @abstractmethod
    def repair(self, parent1,  parent2):
        pass
