import instructor
from typing import List
from app.schemas.output import Recommendation
from app.config.settings import LLM_MODEL, LLM_BASE_URL, LLM_API_KEY
from app.config.logger import setup_logger
from app.services.llm.base import BaseLLMClient

logger = setup_logger(__name__)


class OpenRouterClient(BaseLLMClient):
    """LLM client for generating infrastructure recommendations using Instructor."""

    def __init__(self):
        """
        Initialize OpenAI client with instructor for structured outputs.
        """
        
        self.client = instructor.from_provider(
            model=LLM_MODEL,
            base_url=LLM_BASE_URL,
            async_client=False,
            api_key=LLM_API_KEY,
        )
        logger.info(f"Initialized OpenAIClient with model: {LLM_MODEL}")

    def generate_recommendations(
        self, anomalies: List[dict], insights: dict, service_status_summary: dict
    ) -> List[Recommendation]:
        logger.info(f"Generating recommendations for {len(anomalies)} anomalies")

        prompt = self._build_prompt(anomalies, insights, service_status_summary)
        recommendations = self.client.create(
            response_model=List[Recommendation],
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert infrastructure engineer. Generate concrete, actionable recommendations to optimize infrastructure performance based on detected anomalies.",
                },
                {"role": "user", "content": prompt},
            ],
            max_retries=3,
            temperature=0,
        )

        logger.info(f"Generated {len(recommendations)} recommendations from LLM")
        return recommendations

    def _build_prompt(
        self, anomalies: List[dict], insights: dict, service_status_summary: dict
    ) -> str:
        anomalies_text = "\n".join(
            [
                f"- {a['metric']}: {a['description']} (severity: {a['severity']})"
                for a in anomalies
            ]
        )

        services_text = ", ".join(
            [
                f"{status}: {', '.join(services) if services else 'none'}"
                for status, services in service_status_summary.items()
            ]
        )
        return f"""
                Analyze the following infrastructure state and provide specific, actionable recommendations:

                ## Detected Anomalies ({len(anomalies)} total):
                {anomalies_text}

                ## System Insights:
                - Average Latency: {insights.get('average_latency_ms', 0):.2f}ms
                - Max CPU Usage: {insights.get('max_cpu_usage', 0):.2f}%
                - Max Memory Usage: {insights.get('max_memory_usage', 0):.2f}%
                - Error Rate: {insights.get('error_rate', 0):.2f}%
                - System Uptime: {insights.get('uptime_seconds', 0)} seconds

                ## Service Status Summary:
                {services_text}

                Generate 3-5 concrete, prioritized recommendations tailored to these issues.
                For each recommendation, ensure:
                - id: Unique identifier
                - action: Specific action to take
                - target: Component/system to target
                - parameters: JSON configuration
                - benefit_estimate: Expected improvement
                """
