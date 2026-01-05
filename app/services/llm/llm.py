import instructor
from app.schemas.output import Recommendation
from app.config.settings import OPENAI_API_KEY

class OOpenAIClient:
    def __init__(self, model: str = "openai/gpt-4o"):
        self.client = None
    def generate_recommendations(self, anomalies, insights, service_status_summary) -> list[Recommendation]:
        prompt = (
            "Given the following infrastructure anomalies, insights, and service status summary:\n"
            f"Anomalies: {anomalies}\n"
            f"Insights: {insights}\n"
            f"Service Status Summary: {service_status_summary}\n"
            "Generate a list of concrete, actionable recommendations (with id, action, target, parameters, benefit_estimate) "
            "to optimize infrastructure performance. Output as a list."
        )
        recommendations = self.client.create(
            response_model=list[Recommendation],
            messages=[{"role": "user", "content": prompt}],
            max_retries=3
        )
        return recommendations
    
import instructor
from typing import List
from app.schemas.output import Recommendation
from app.config.settings import OPENAI_API_KEY, LLM_MODEL
from app.config.logger import setup_logger

logger = setup_logger(__name__)

class OpenAIClient:
    """LLM client for generating infrastructure recommendations."""
    
    def __init__(self, model: str = LLM_MODEL):
        self.model = model
        self.client = None
        logger.info(f"Initialized OpenAIClient with model: {model}")
    
    def generate_recommendations(
        self, 
        anomalies: List[dict], 
        insights: dict, 
        service_status_summary: dict
    ) -> List[Recommendation]:
        """
        Generate infrastructure recommendations based on detected anomalies.
        
        Args:
            anomalies: List of detected anomalies
            insights: System insights and metrics
            service_status_summary: Summary of service statuses
        
        Returns:
            List of Recommendation objects
        """
        try:
            logger.debug(f"Generating recommendations for {len(anomalies)} anomalies")
            
            # Mock LLM that returns hardcoded recommendations
            recommendations = [
                Recommendation(
                    id="rec-001",
                    action="Scale up CPU resources",
                    target="compute_instances",
                    parameters={"cpu_cores": 8, "priority": "high"},
                    benefit_estimate="30% reduction in CPU bottlenecks"
                ),
                Recommendation(
                    id="rec-002",
                    action="Increase memory allocation",
                    target="memory_pool",
                    parameters={"memory_gb": 32, "priority": "high"},
                    benefit_estimate="40% improvement in memory performance"
                ),
                Recommendation(
                    id="rec-003",
                    action="Optimize database queries",
                    target="database",
                    parameters={"enable_caching": True, "query_timeout_ms": 5000},
                    benefit_estimate="50% reduction in latency"
                ),
                Recommendation(
                    id="rec-004",
                    action="Restart degraded services",
                    target="service_manager",
                    parameters={"auto_restart": True},
                    benefit_estimate="100% service availability"
                )
            ]
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}", exc_info=True)
            raise