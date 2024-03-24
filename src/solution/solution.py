from abc import ABC, abstractmethod


class Solution(ABC):
    @abstractmethod
    def get_representation(self):
        pass

    @abstractmethod
    def set_representation(self, representation):
        pass
