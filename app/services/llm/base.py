from abc import ABC, abstractmethod

from app.schemas.output import Recommendation

class BaseLLMClient(ABC):
    @abstractmethod
    def generate_recommendations(self, anomalies: list[dict],
                                  insights: dict, 
                                  service_status_summary: dict
    ) -> list[Recommendation]:
        pass
