from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import uuid4, UUID

from beanie import Document
from pydantic import Field

from autostack_engine.utils.logging.models import LogCategory, LogLevel

class ServiceLog(Document):
    """
    Service log document for MongoDB.
    Stores all service operations, errors, and events.
    """
    
    # Primary identification
    log_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Service information
    service_name: str  # e.g., "PROJECT", "TECHNOLOGY"
    log_level: LogLevel = LogLevel.INFO
    category: LogCategory = LogCategory.SYSTEM
    
    # Log content
    message: str
    operation: Optional[str] = None  # e.g., "create_project", "update_component"
    
    # Context (for relating logs to resources)
    project_id: Optional[str] = None
    component_id: Optional[str] = None
    technology_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Additional data
    metadata: Optional[Dict[str, Any]] = None
    error_traceback: Optional[str] = None
    duration_ms: Optional[float] = None  # Operation duration in milliseconds
    
    # Request context
    request_id: Optional[str] = None  # For tracing related logs
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    class Settings:
        name = "service_logs"
        indexes = [
            "timestamp",
            "service_name",
            "log_level",
            "category",
            "project_id",
            "component_id",
            "technology_id",
            "request_id",
            [("timestamp", -1)],  # Descending index for recent logs
            [("service_name", 1), ("timestamp", -1)],
            [("project_id", 1), ("timestamp", -1)],
            [("log_level", 1), ("timestamp", -1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "service_name": "PROJECT",
                "log_level": "INFO",
                "category": "PROJECT",
                "message": "Project 'My LMS' created successfully",
                "operation": "create_project",
                "project_id": "abc-123",
                "metadata": {
                    "project_name": "My LMS",
                    "author": "John Doe"
                }
            }
        }
    
    def __str__(self) -> str:
        return f"[{self.timestamp.isoformat()}] [{self.log_level.value}] [{self.service_name}] {self.message}"
    
    @classmethod
    async def get_recent_logs(
        cls,
        limit: int = 100,
        service_name: Optional[str] = None,
        log_level: Optional[LogLevel] = None,
        project_id: Optional[str] = None
    ):
        """Get recent logs with optional filters"""
        query = {}
        
        if service_name:
            query["service_name"] = service_name
        if log_level:
            query["log_level"] = log_level
        if project_id:
            query["project_id"] = project_id
        
        return await cls.find(query).sort("-timestamp").limit(limit).to_list()
    
    @classmethod
    async def get_error_logs(cls, limit: int = 50, project_id: Optional[str] = None):
        """Get recent error logs"""
        query = {"log_level": {"$in": [LogLevel.ERROR, LogLevel.CRITICAL]}}
        
        if project_id:
            query["project_id"] = project_id
        
        return await cls.find(query).sort("-timestamp").limit(limit).to_list()
    
    @classmethod
    async def get_logs_by_request(cls, request_id: str):
        """Get all logs for a specific request"""
        return await cls.find({"request_id": request_id}).sort("timestamp").to_list()
    
    @classmethod
    async def get_project_logs(cls, project_id: str, limit: int = 100):
        """Get all logs related to a specific project"""
        return await cls.find({"project_id": project_id}).sort("-timestamp").limit(limit).to_list()
    
    @classmethod
    async def delete_old_logs(cls, days: int = 30):
        """Delete logs older than specified days"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await cls.find({"timestamp": {"$lt": cutoff_date}}).delete()
        return result.deleted_count


class LogStatistics(Document):
    """
    Aggregated log statistics for monitoring and analytics.
    Can be updated periodically via a cron job.
    """
    
    date: datetime = Field(default_factory=lambda: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
    service_name: str
    
    # Counts by level
    info_count: int = 0
    warning_count: int = 0
    error_count: int = 0
    critical_count: int = 0
    
    # Operation counts
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    
    # Performance metrics
    avg_duration_ms: Optional[float] = None
    max_duration_ms: Optional[float] = None
    min_duration_ms: Optional[float] = None
    
    # Top operations
    top_operations: Optional[Dict[str, int]] = None  # operation_name -> count
    
    class Settings:
        name = "log_statistics"
        indexes = [
            [("date", -1)],
            [("service_name", 1), ("date", -1)],
        ]
    
    @classmethod
    async def generate_daily_stats(cls, date: datetime, service_name: str):
        """Generate statistics for a specific day and service"""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day.replace(hour=23, minute=59, second=59)
        
        # Query logs for the day
        logs = await ServiceLog.find({
            "service_name": service_name,
            "timestamp": {"$gte": start_of_day, "$lte": end_of_day}
        }).to_list()
        
        if not logs:
            return None
        
        # Calculate statistics
        info_count = sum(1 for log in logs if log.log_level == LogLevel.INFO)
        warning_count = sum(1 for log in logs if log.log_level == LogLevel.WARNING)
        error_count = sum(1 for log in logs if log.log_level == LogLevel.ERROR)
        critical_count = sum(1 for log in logs if log.log_level == LogLevel.CRITICAL)
        
        # Duration statistics
        durations = [log.duration_ms for log in logs if log.duration_ms is not None]
        avg_duration = sum(durations) / len(durations) if durations else None
        max_duration = max(durations) if durations else None
        min_duration = min(durations) if durations else None
        
        # Top operations
        operations = {}
        for log in logs:
            if log.operation:
                operations[log.operation] = operations.get(log.operation, 0) + 1
        top_operations = dict(sorted(operations.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Create or update statistics
        stats = await cls.find_one({
            "date": start_of_day,
            "service_name": service_name
        })
        
        if stats:
            stats.info_count = info_count
            stats.warning_count = warning_count
            stats.error_count = error_count
            stats.critical_count = critical_count
            stats.total_operations = len(logs)
            stats.avg_duration_ms = avg_duration
            stats.max_duration_ms = max_duration
            stats.min_duration_ms = min_duration
            stats.top_operations = top_operations
            await stats.save()
        else:
            stats = cls(
                date=start_of_day,
                service_name=service_name,
                info_count=info_count,
                warning_count=warning_count,
                error_count=error_count,
                critical_count=critical_count,
                total_operations=len(logs),
                avg_duration_ms=avg_duration,
                max_duration_ms=max_duration,
                min_duration_ms=min_duration,
                top_operations=top_operations
            )
            await stats.insert()
        
        return stats
