from pydantic import BaseModel, Field
from typing import List

class ServiceStatus(BaseModel):
    """Service status indicator."""
    database: str = Field(..., pattern="^(online|degraded|offline)$")
    api_gateway: str = Field(..., pattern="^(online|degraded|offline)$")
    cache: str = Field(..., pattern="^(online|degraded|offline)$")
    
    class Config:
        description = "Service status for infrastructure components"

class InputData(BaseModel):
    """Infrastructure metrics input data."""
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    latency_ms: float = Field(..., ge=0, description="Latency in milliseconds")
    disk_usage: float = Field(..., ge=0, le=100, description="Disk usage percentage")
    network_in_kbps: float = Field(..., ge=0, description="Incoming network bandwidth")
    network_out_kbps: float = Field(..., ge=0, description="Outgoing network bandwidth")
    io_wait: float = Field(..., ge=0, le=100, description="IO wait percentage")
    thread_count: int = Field(..., gt=0, description="Active thread count")
    active_connections: int = Field(..., ge=0, description="Active connections")
    error_rate: float = Field(..., ge=0, le=100, description="Error rate percentage")
    uptime_seconds: int = Field(..., ge=0, description="System uptime in seconds")
    temperature_celsius: float = Field(..., description="System temperature")
    power_consumption_watts: float = Field(..., ge=0, description="Power consumption")
    service_status: ServiceStatus = Field(..., description="Service status summary")
        
    class Config:
        description = "Infrastructure metrics data point"

class InputDataList(BaseModel):
    """Batch input data container."""
    data: List[InputData] = Field(..., min_items=1)
    
    class Config:
        description = "Batch input data container"