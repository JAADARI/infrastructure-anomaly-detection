from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class SeverityLevel(str, Enum):
    """Anomaly severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ApprovalStatus(str, Enum):
    """Remediation action approval status."""
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"

class Insight(BaseModel):
    """Infrastructure insights."""
    average_latency_ms: float = Field(..., ge=0)
    max_cpu_usage: float = Field(..., ge=0, le=100)
    max_memory_usage: float = Field(..., ge=0, le=100)
    error_rate: float = Field(..., ge=0, le=100)
    uptime_seconds: int = Field(..., ge=0)

class Anomaly(BaseModel):
    """Detected anomaly."""
    metric: str = Field(..., description="Metric name")
    value: float = Field(..., description="Current value")
    threshold: Optional[float] = Field(None, description="Anomaly threshold")
    severity: SeverityLevel = Field(..., description="Severity level")
    description: str = Field(..., description="Detailed description")

class Recommendation(BaseModel):
    """Action recommendation."""
    id: str = Field(..., description="Unique recommendation ID")
    action: str = Field(..., description="Recommended action")
    target: str = Field(..., description="Target component")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    benefit_estimate: str = Field(..., description="Estimated benefit")

class ServiceStatusSummary(BaseModel):
    """Service status summary."""
    online: List[str] = Field(default_factory=list)
    degraded: List[str] = Field(default_factory=list)
    offline: List[str] = Field(default_factory=list)

class RemediationAction(BaseModel):
    """Planned remediation action."""
    id: str = Field(..., description="Unique action ID")
    action_type: str = Field(..., description="Type of remediation action")
    target: str = Field(..., description="Target component")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    status: ApprovalStatus = Field(..., description="Approval status")
    recommendation_id: str = Field(..., description="Associated recommendation ID")

class FinalReport(BaseModel):
    """Final analysis report."""
    timestamp: str = Field(..., description="Report timestamp")
    insights: Insight = Field(..., description="Infrastructure insights")
    anomalies: List[Anomaly] = Field(default_factory=list, description="Detected anomalies")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Recommendations")
    service_status_summary: ServiceStatusSummary = Field(..., description="Service status")
    remediation_actions: List[RemediationAction] = Field(default_factory=list, description="Planned remediation actions")