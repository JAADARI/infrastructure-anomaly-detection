from abc import ABC, abstractmethod

class AnomalyDetector(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def detect(self, data):
        raise NotImplementedError("Subclasses should implement this method")
