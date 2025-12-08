from datetime import datetime
from typing import List, Optional
import strawberry


@strawberry.type
class LogEntry:
    log_id: str
    timestamp: datetime
    service_name: str
    log_level: str
    category: str
    message: str
    operation: Optional[str] = None
    project_id: Optional[str] = None
    component_id: Optional[str] = None
    technology_id: Optional[str] = None
    duration_ms: Optional[float] = None
    error_traceback: Optional[str] = None
    request_id: Optional[str] = None


@strawberry.type
class LogStatisticsResponse:
    service_name: str
    period_days: int
    total_logs: int
    info_count: int
    warning_count: int
    error_count: int
    critical_count: int
    error_rate: float
    avg_duration_ms: float
    max_duration_ms: float
    min_duration_ms: float


@strawberry.type
class LogsResponse:
    logs: List[LogEntry]
    total: int