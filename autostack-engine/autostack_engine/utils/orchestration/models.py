from contextvars import ContextVar
from datetime import datetime
import structlog
from abc import ABC
from typing import Any, Dict, Optional
import traceback as tb
import time

from autostack_engine.utils.database.mongo_client import DatabaseManager
from autostack_engine.utils.logging.models import LogCategory, LogLevel
from autostack_engine.utils.logging.services import ServiceLog

logger = structlog.get_logger()

request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


class BaseService(ABC):
    """
    Base class for all services. Provides common functionality and logging.
    Automatically logs to both console (structlog) and MongoDB (ServiceLog).
    """
    
    service_name: Optional[str] = None
    
    def __init__(self):
        if not self.service_name:
            raise ValueError("service_name must be defined in the subclass")
        self.logger = structlog.get_logger().bind(service=self.service_name)
        self._current_operation: Optional[str] = None
        self._operation_start_time: Optional[float] = None
    
    def _get_log_category(self) -> LogCategory:
        """Map service name to log category"""
        category_map = {
            "PROJECT": LogCategory.PROJECT,
            "TECHNOLOGY": LogCategory.TECHNOLOGY,
            "COMPONENT": LogCategory.COMPONENT,
            "PRODUCTION": LogCategory.PRODUCTION,
            "ORCHESTRATION": LogCategory.ORCHESTRATION,
        }
        return category_map.get(self.service_name.upper(), LogCategory.SYSTEM)
    
    async def _persist_log(
        self,
        message: str,
        log_level: LogLevel,
        operation: Optional[str] = None,
        project_id: Optional[str] = None,
        component_id: Optional[str] = None,
        technology_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error_traceback: Optional[str] = None,
        duration_ms: Optional[float] = None
    ):
        """Persist log to MongoDB"""
        try:
            db = DatabaseManager()
            await db.connect([ServiceLog])
            
            log_entry = ServiceLog(
                service_name=self.service_name.upper(),
                log_level=log_level,
                category=self._get_log_category(),
                message=message,
                operation=operation or self._current_operation,
                project_id=project_id,
                component_id=component_id,
                technology_id=technology_id,
                metadata=metadata,
                error_traceback=error_traceback,
                duration_ms=duration_ms,
                request_id=request_id_var.get(),
                user_id=user_id_var.get(),
                timestamp=datetime.now()
            )
            await log_entry.insert()
        except Exception as e:
            # Don't let logging failures break the application
            self.logger.error(f"Failed to persist log to MongoDB: {e}")
    
    def log_info(self, message: str, operation: Optional[str] = None, **kwargs):
        """Log info message to console and MongoDB"""
        formatted_msg = f"[{self.service_name.upper()}] {message}"
        self.logger.info(formatted_msg, **kwargs)
        
        # Async log to MongoDB (non-blocking)
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self._persist_log(
                message=message,
                log_level=LogLevel.INFO,
                operation=operation,
                metadata=kwargs if kwargs else None
            ))
        except RuntimeError:
            # No event loop available, skip MongoDB logging
            pass
    
    def log_error(self, message: str, operation: Optional[str] = None, error: Optional[Exception] = None, **kwargs):
        """Log error message to console and MongoDB"""
        formatted_msg = f"[{self.service_name.upper()}] {message}"
        self.logger.error(formatted_msg, **kwargs)
        
        # Capture traceback if error provided
        error_traceback = None
        if error:
            error_traceback = ''.join(tb.format_exception(type(error), error, error.__traceback__))
        elif kwargs.get('exc_info'):
            error_traceback = tb.format_exc()
        
        # Async log to MongoDB
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self._persist_log(
                message=message,
                log_level=LogLevel.ERROR,
                operation=operation,
                metadata=kwargs if kwargs else None,
                error_traceback=error_traceback
            ))
        except RuntimeError:
            pass
    
    def log_warning(self, message: str, operation: Optional[str] = None, **kwargs):
        """Log warning message to console and MongoDB"""
        formatted_msg = f"[{self.service_name.upper()}] {message}"
        self.logger.warning(formatted_msg, **kwargs)
        
        # Async log to MongoDB
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self._persist_log(
                message=message,
                log_level=LogLevel.WARNING,
                operation=operation,
                metadata=kwargs if kwargs else None
            ))
        except RuntimeError:
            pass
    
    def log_debug(self, message: str, operation: Optional[str] = None, **kwargs):
        """Log debug message to console and MongoDB"""
        formatted_msg = f"[{self.service_name.upper()}] {message}"
        self.logger.debug(formatted_msg, **kwargs)
        
        # Async log to MongoDB
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self._persist_log(
                message=message,
                log_level=LogLevel.DEBUG,
                operation=operation,
                metadata=kwargs if kwargs else None
            ))
        except RuntimeError:
            pass
    
    def start_operation(self, operation_name: str):
        """Start tracking an operation for duration logging"""
        self._current_operation = operation_name
        self._operation_start_time = time.time()
        self.log_info(f"Started operation: {operation_name}", operation=operation_name)
    
    async def end_operation(
        self,
        success: bool,
        message: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ):
        """End operation tracking and log with duration"""
        if self._operation_start_time:
            duration_ms = (time.time() - self._operation_start_time) * 1000
        else:
            duration_ms = None
        
        final_message = message or f"Completed operation: {self._current_operation}"
        
        if success:
            self.log_info(
                final_message,
                operation=self._current_operation,
                duration_ms=duration_ms,
                **kwargs
            )
        else:
            self.log_error(
                final_message,
                operation=self._current_operation,
                **kwargs
            )
        
        # Persist with duration
        await self._persist_log(
            message=final_message,
            log_level=LogLevel.INFO if success else LogLevel.ERROR,
            operation=self._current_operation,
            project_id=project_id,
            duration_ms=duration_ms,
            metadata=kwargs if kwargs else None
        )
        
        # Reset operation tracking
        self._current_operation = None
        self._operation_start_time = None
    
    @staticmethod
    def set_request_context(request_id: str, user_id: Optional[str] = None):
        """Set request context for log correlation"""
        request_id_var.set(request_id)
        if user_id:
            user_id_var.set(user_id)
    
    @staticmethod
    def clear_request_context():
        """Clear request context"""
        request_id_var.set(None)
        user_id_var.set(None)