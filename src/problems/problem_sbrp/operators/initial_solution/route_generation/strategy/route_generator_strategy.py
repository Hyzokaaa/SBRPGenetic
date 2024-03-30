from abc import ABC, abstractmethod


class RouteGeneratorStrategy(ABC):

    @abstractmethod
    def generate_route(self, problem):
        pass
