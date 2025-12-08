from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import uuid4

from autostack_engine.services.orchestration import BaseService
from autostack_engine.utils.database.mongo_client import DatabaseManager
from autostack_engine.utils.logging.models import LogCategory, LogLevel
from autostack_engine.utils.logging.services import ServiceLog


class LogManagementService(BaseService):
    """Service for managing and querying service logs"""
    
    service_name = "LOG_MANAGEMENT"
    
    async def get_recent_logs(
        self,
        limit: int = 100,
        service_name: Optional[str] = None,
        log_level: Optional[LogLevel] = None,
        project_id: Optional[str] = None,
        category: Optional[LogCategory] = None
    ) -> List[ServiceLog]:
        """
        Get recent logs with filters.
        
        Args:
            limit: Maximum number of logs to return
            service_name: Filter by service (e.g., "PROJECT", "COMPONENT")
            log_level: Filter by log level (INFO, ERROR, etc.)
            project_id: Filter by project ID
            category: Filter by category
            
        Returns:
            List of ServiceLog documents
        """
        try:
            db = DatabaseManager()
            await db.connect([ServiceLog])
            
            query = {}
            
            if service_name:
                query["service_name"] = service_name.upper()
            if log_level:
                query["log_level"] = log_level
            if project_id:
                query["project_id"] = project_id
            if category:
                query["category"] = category
            
            logs = await ServiceLog.find(query).sort("-timestamp").limit(limit).to_list()
            
            self.log_info(f"Retrieved {len(logs)} logs", operation="get_recent_logs")
            return logs
            
        except Exception as e:
            self.log_error(f"Error retrieving logs: {e}", operation="get_recent_logs", error=e)
            return []
    
    async def get_error_logs(
        self,
        limit: int = 50,
        project_id: Optional[str] = None,
        hours: int = 24
    ) -> List[ServiceLog]:
        """
        Get recent error and critical logs.
        
        Args:
            limit: Maximum number of logs
            project_id: Filter by project
            hours: Only get errors from last N hours
            
        Returns:
            List of error logs
        """
        try:
            db = DatabaseManager()
            await db.connect([ServiceLog])
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            query = {
                "log_level": {"$in": [LogLevel.ERROR.value, LogLevel.CRITICAL.value]},
                "timestamp": {"$gte": cutoff_time}
            }
            
            if project_id:
                query["project_id"] = project_id
            
            logs = await ServiceLog.find(query).sort("-timestamp").limit(limit).to_list()
            
            self.log_info(f"Retrieved {len(logs)} error logs", operation="get_error_logs")
            return logs
            
        except Exception as e:
            self.log_error(f"Error retrieving error logs: {e}", operation="get_error_logs", error=e)
            return []
    
    async def get_logs_by_request(self, request_id: str) -> List[ServiceLog]:
        """
        Get all logs for a specific request ID.
        Useful for tracing a complete workflow.
        
        Args:
            request_id: The request ID to trace
            
        Returns:
            List of logs in chronological order
        """
        try:
            db = DatabaseManager()
            await db.connect([ServiceLog])
            
            logs = await ServiceLog.find({"request_id": request_id}).sort("timestamp").to_list()
            
            self.log_info(
                f"Retrieved {len(logs)} logs for request",
                operation="get_logs_by_request",
                request_id=request_id
            )
            return logs
            
        except Exception as e:
            self.log_error(f"Error retrieving request logs: {e}", operation="get_logs_by_request", error=e)
            return []
    
    async def get_project_logs(
        self,
        project_id: str,
        limit: int = 100,
        log_level: Optional[LogLevel] = None
    ) -> List[ServiceLog]:
        """
        Get all logs related to a specific project.
        
        Args:
            project_id: The project ID
            limit: Maximum number of logs
            log_level: Optional level filter
            
        Returns:
            List of project logs
        """
        try:
            db = DatabaseManager()
            await db.connect([ServiceLog])
            
            query = {"project_id": project_id}
            if log_level:
                query["log_level"] = log_level
            
            logs = await ServiceLog.find(query).sort("-timestamp").limit(limit).to_list()
            
            self.log_info(
                f"Retrieved {len(logs)} logs for project",
                operation="get_project_logs",
                project_id=project_id
            )
            return logs
            
        except Exception as e:
            self.log_error(f"Error retrieving project logs: {e}", operation="get_project_logs", error=e)
            return []
    
    async def get_service_statistics(
        self,
        service_name: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get statistics for a service over the last N days.
        
        Args:
            service_name: Service to analyze
            days: Number of days to look back
            
        Returns:
            Dictionary with statistics
        """
        try:
            db = DatabaseManager()
            await db.connect([ServiceLog])
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            logs = await ServiceLog.find({
                "service_name": service_name.upper(),
                "timestamp": {"$gte": cutoff_date}
            }).to_list()
            
            # Calculate statistics
            total_logs = len(logs)
            info_count = sum(1 for log in logs if log.log_level == LogLevel.INFO)
            warning_count = sum(1 for log in logs if log.log_level == LogLevel.WARNING)
            error_count = sum(1 for log in logs if log.log_level == LogLevel.ERROR)
            critical_count = sum(1 for log in logs if log.log_level == LogLevel.CRITICAL)
            
            # Operation statistics
            operations = {}
            durations = []
            for log in logs:
                if log.operation:
                    operations[log.operation] = operations.get(log.operation, 0) + 1
                if log.duration_ms is not None:
                    durations.append(log.duration_ms)
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            min_duration = min(durations) if durations else 0
            
            stats = {
                "service_name": service_name,
                "period_days": days,
                "total_logs": total_logs,
                "by_level": {
                    "info": info_count,
                    "warning": warning_count,
                    "error": error_count,
                    "critical": critical_count
                },
                "error_rate": (error_count + critical_count) / total_logs if total_logs > 0 else 0,
                "operations": operations,
                "performance": {
                    "avg_duration_ms": round(avg_duration, 2),
                    "max_duration_ms": round(max_duration, 2),
                    "min_duration_ms": round(min_duration, 2)
                },
                "top_operations": dict(sorted(operations.items(), key=lambda x: x[1], reverse=True)[:5])
            }
            
            self.log_info(
                f"Generated statistics for {service_name}",
                operation="get_service_statistics",
                total_logs=total_logs
            )
            return stats
            
        except Exception as e:
            self.log_error(f"Error generating statistics: {e}", operation="get_service_statistics", error=e)
            return {}
    
    async def cleanup_old_logs(self, days: int = 30) -> int:
        """
        Delete logs older than specified days.
        
        Args:
            days: Delete logs older than this many days
            
        Returns:
            Number of logs deleted
        """
        try:
            db = DatabaseManager()
            await db.connect([ServiceLog])
            
            deleted_count = await ServiceLog.delete_old_logs(days)
            
            self.log_info(
                f"Deleted {deleted_count} logs older than {days} days",
                operation="cleanup_old_logs",
                deleted_count=deleted_count
            )
            return deleted_count
            
        except Exception as e:
            self.log_error(f"Error cleaning up logs: {e}", operation="cleanup_old_logs", error=e)
            return 0
    
    async def search_logs(
        self,
        search_term: str,
        limit: int = 100,
        service_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ServiceLog]:
        """
        Search logs by message content.
        
        Args:
            search_term: Text to search for in messages
            limit: Maximum number of results
            service_name: Optional service filter
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            List of matching logs
        """
        try:
            db = DatabaseManager()
            await db.connect([ServiceLog])
            
            query = {
                "message": {"$regex": search_term, "$options": "i"}  # Case-insensitive search
            }
            
            if service_name:
                query["service_name"] = service_name.upper()
            
            if start_date or end_date:
                query["timestamp"] = {}
                if start_date:
                    query["timestamp"]["$gte"] = start_date
                if end_date:
                    query["timestamp"]["$lte"] = end_date
            
            logs = await ServiceLog.find(query).sort("-timestamp").limit(limit).to_list()
            
            self.log_info(
                f"Found {len(logs)} logs matching search",
                operation="search_logs",
                search_term=search_term
            )
            return logs
            
        except Exception as e:
            self.log_error(f"Error searching logs: {e}", operation="search_logs", error=e)
            return []
    
    async def get_operation_timeline(
        self,
        project_id: str,
        operation: str,
        limit: int = 50
    ) -> List[ServiceLog]:
        """
        Get timeline of a specific operation for a project.
        Useful for debugging repeated operations.
        
        Args:
            project_id: Project to analyze
            operation: Operation name (e.g., "create_component")
            limit: Maximum number of logs
            
        Returns:
            List of logs for the operation
        """
        try:
            db = DatabaseManager()
            await db.connect([ServiceLog])
            
            logs = await ServiceLog.find({
                "project_id": project_id,
                "operation": operation
            }).sort("-timestamp").limit(limit).to_list()
            
            self.log_info(
                f"Retrieved {len(logs)} logs for operation timeline",
                operation="get_operation_timeline",
                target_operation=operation
            )
            return logs
            
        except Exception as e:
            self.log_error(f"Error retrieving operation timeline: {e}", operation="get_operation_timeline", error=e)
            return []


# Usage example with request tracing
async def example_usage():
    """Example of how to use logging with request context"""
    from autostack_engine.services.orchestration import OrchestrationService
    
    # Set request context for tracing
    request_id = str(uuid4())
    BaseService.set_request_context(request_id=request_id, user_id="user-123")
    
    # Create orchestrator
    orchestrator = OrchestrationService()
    orchestrator.start_operation("create_full_project")
    
    # Execute operation
    project_data = {
        "project": {
            "name": "Test Project",
            "author": "Test User"
        }
    }
    
    success, project_id, error = await orchestrator.orchestrate_full_project(project_data)
    
    # End operation with duration tracking
    await orchestrator.end_operation(
        success=success,
        project_id=project_id,
        message=f"Project creation {'succeeded' if success else 'failed'}"
    )
    
    # Clear request context
    BaseService.clear_request_context()
    
    # Query logs for this request
    log_service = LogManagementService()
    request_logs = await log_service.get_logs_by_request(request_id)
    
    print(f"Found {len(request_logs)} logs for request {request_id}")
    for log in request_logs:
        print(f"  [{log.timestamp}] [{log.log_level.value}] {log.message}")