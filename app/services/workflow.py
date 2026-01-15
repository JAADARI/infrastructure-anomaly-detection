from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph, START, END
from app.schemas.input import InputData
from app.schemas.output import FinalReport, Anomaly, Recommendation, Insight, ServiceStatusSummary, RemediationAction, ApprovalStatus
from app.services.anomaly_detector.factory import create_anomaly_detector
from app.services.llm.llm import OpenAIClient
from app.config.logger import setup_logger
import pandas as pd
from datetime import datetime, timezone

logger = setup_logger(__name__)

class InfraState(TypedDict, total=False):
    input_data_list: List[dict]
    df: pd.DataFrame
    anomalies: List[dict]
    insights: dict
    recommendations: List[dict]
    service_status_summary: dict
    remediation_actions: List[dict]
    final_report: dict

class InfraWorkflow:
    """Orchestrate infrastructure anomaly detection and recommendation workflow."""
    
    def __init__(self, anomaly_config: dict, llm_client=None):
        self.anomaly_detector = create_anomaly_detector(anomaly_config)
        self.llm_client = llm_client or OpenAIClient()
        self.graph = self._build_graph()
        logger.info(f"Initialized InfraWorkflow with config: {anomaly_config}")

    def _validate_and_parse(self, state: InfraState) -> InfraState:
        """Validate input data and convert to DataFrame."""
        try:
            logger.info(f"Validating {len(state['input_data_list'])} input records")
            validated = [InputData(**item) for item in state["input_data_list"]]
            df = pd.DataFrame([item.model_dump() for item in validated])
            state["df"] = df
            logger.info(f"Successfully validated and parsed {len(df)} records")
            return state
        except Exception as e:
            logger.error(f"Validation error: {str(e)}", exc_info=True)
            raise

    def _detect_anomalies_and_extract(self, state: InfraState) -> InfraState:
        """Detect anomalies and extract insights."""
        try:
            logger.info("Starting anomaly detection")
            result = self.anomaly_detector.detect(state["df"])
            state["anomalies"] = result["anomalies"]
            state["insights"] = result["insights"]
            state["service_status_summary"] = result["service_status_summary"]
            logger.info(f"Detected {len(state['anomalies'])} anomalies")
            return state
        except Exception as e:
            logger.error(f"Anomaly detection error: {str(e)}", exc_info=True)
            raise

    def _generate_recommendations(self, state: InfraState) -> InfraState:
        """Generate recommendations based on detected anomalies."""
        try:
            logger.info("Generating recommendations")
            recommendations = self.llm_client.generate_recommendations(
                state["anomalies"], 
                state["insights"], 
                state["service_status_summary"]
            )
            print("recommendations:", recommendations)
            state["recommendations"] = recommendations
            logger.info(f"Generated {len(recommendations)} recommendations")
            return state
        except Exception as e:
            logger.error(f"Recommendation generation error: {str(e)}", exc_info=True)
            raise

    def _plan_remediation(self, state: InfraState) -> InfraState:
        """Transform recommendations into structured remediation actions."""
        try:
            logger.info("Planning remediation actions")
            remediation_actions = []
            
            for idx, rec in enumerate(state.get("recommendations", [])):
                # Convert Recommendation to dict if necessary
                rec_dict = rec if isinstance(rec, dict) else rec.model_dump()
                
                action = {
                    "id": f"action_{idx + 1}",
                    "action_type": rec_dict.get("action", "unknown"),
                    "target": rec_dict.get("target", "unknown"),
                    "parameters": rec_dict.get("parameters", {}),
                    "status": ApprovalStatus.PENDING_APPROVAL.value,
                    "recommendation_id": rec_dict.get("id", f"rec_{idx + 1}")
                }
                remediation_actions.append(action)
            
            state["remediation_actions"] = remediation_actions
            logger.info(f"Planned {len(remediation_actions)} remediation actions")
            return state
        except Exception as e:
            logger.error(f"Remediation planning error: {str(e)}", exc_info=True)
            raise

    def _human_approval_stub(self, state: InfraState) -> InfraState:
        """Human-in-the-loop approval stub - marks actions as pending approval."""
        try:
            logger.info("Processing human approval stub")
            # This is a stub - in production, this would integrate with an approval system
            # For now, we just ensure all actions are marked as pending_approval
            for action in state.get("remediation_actions", []):
                action["status"] = ApprovalStatus.PENDING_APPROVAL.value
            
            logger.info(f"Marked {len(state.get('remediation_actions', []))} actions as pending approval")
            return state
        except Exception as e:
            logger.error(f"Approval stub error: {str(e)}", exc_info=True)
            raise

    def _final_report(self, state: InfraState) -> InfraState:
        """Generate final report."""
        try:
            logger.info("Generating final report")
            timestamp = datetime.now(timezone.utc).isoformat()
            insights_obj = Insight(**state["insights"])
            anomaly_objs = [Anomaly(**a) for a in state.get("anomalies", [])]
            rec_objs = [
                r if isinstance(r, Recommendation) else Recommendation(**r)
                for r in state.get("recommendations", [])
            ]
            service_status_obj = ServiceStatusSummary(**state["service_status_summary"])
            remediation_objs = [
                RemediationAction(**ra) for ra in state.get("remediation_actions", [])
            ]
            
            report = FinalReport(
                timestamp=timestamp,
                insights=insights_obj,
                anomalies=anomaly_objs,
                recommendations=rec_objs,
                service_status_summary=service_status_obj,
                remediation_actions=remediation_objs
            )
            state["final_report"] = report
            logger.info("Final report generated successfully")
            return state
        except Exception as e:
            logger.error(f"Report generation error: {str(e)}", exc_info=True)
            raise

    def _should_generate_recommendations(self, state: InfraState) -> Literal["generate_recommendations", "final_report"]:
        """Conditional routing based on anomalies."""
        has_anomalies = bool(state.get("anomalies"))
        logger.debug(f"Routing: has_anomalies={has_anomalies}")
        return "generate_recommendations" if has_anomalies else "final_report"

    def _build_graph(self):
        """Build the workflow graph."""
        builder = StateGraph(InfraState)
        builder.add_node("validate_and_parse", self._validate_and_parse)
        builder.add_node("detect_anomalies_and_extract", self._detect_anomalies_and_extract)
        builder.add_node("generate_recommendations", self._generate_recommendations)
        builder.add_node("plan_remediation", self._plan_remediation)
        builder.add_node("human_approval_stub", self._human_approval_stub)
        builder.add_node("final_report", self._final_report)

        builder.add_edge(START, "validate_and_parse")
        builder.add_edge("validate_and_parse", "detect_anomalies_and_extract")
        builder.add_conditional_edges(
            "detect_anomalies_and_extract",
            self._should_generate_recommendations,
            ["generate_recommendations", "final_report"]
        )
        builder.add_edge("generate_recommendations", "plan_remediation")
        builder.add_edge("plan_remediation", "human_approval_stub")
        builder.add_edge("human_approval_stub", "final_report")
        builder.add_edge("final_report", END)
        return builder.compile()

    def process(self, input_data_list: List[dict]) -> FinalReport:
        """Execute the workflow."""
        logger.info(f"Processing {len(input_data_list)} input records")
        state = {"input_data_list": input_data_list}
        result = self.graph.invoke(state)
        return result["final_report"]