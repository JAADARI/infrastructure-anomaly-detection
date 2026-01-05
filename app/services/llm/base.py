from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    @abstractmethod
    def set_parameters(self, **kwargs) -> None:
        pass

    @abstractmethod
    def get_model_info(self) -> dict:
        pass