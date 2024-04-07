from abc import ABC, abstractmethod

from src.operators.repair.repair_parameters import RepairParameters


class RepairOperator(ABC):
    @abstractmethod
    def repair(self, parameters: RepairParameters):
        pass
