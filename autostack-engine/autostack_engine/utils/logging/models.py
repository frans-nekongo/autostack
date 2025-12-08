from typing import Optional, Dict, Any
from uuid import uuid4, UUID
from beanie import Document
from pydantic import Field
from datetime import datetime
from enum import Enum
import structlog


class LogLevel(str, Enum):
    """Log severity levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(str, Enum):
    """Log categories for filtering"""
    PROJECT = "PROJECT"
    TECHNOLOGY = "TECHNOLOGY"
    COMPONENT = "COMPONENT"
    PRODUCTION = "PRODUCTION"
    ORCHESTRATION = "ORCHESTRATION"
    SYSTEM = "SYSTEM"
    