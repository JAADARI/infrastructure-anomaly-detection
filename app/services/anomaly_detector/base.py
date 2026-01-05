from abc import ABC, abstractmethod

class AnanomalyDetector(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def detect(self, data):
        raise NotImplementedError("Subclasses should implement this method")
