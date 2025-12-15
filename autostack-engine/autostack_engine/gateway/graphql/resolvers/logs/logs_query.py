from bson import Binary
import strawberry
import uuid
import structlog
from typing import Any, Dict, Optional, List
from strawberry.scalars import JSON
from autostack_engine.utils.database.models.activities.models import ActivityLog
from autostack_engine.utils.database.mongo_client import DatabaseManager
from autostack_engine.utils.schema.models.components import JSON

logger = structlog.get_logger()



def serialize_details(details: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Convert Binary and UUID objects to serializable types"""
    if not details:
        return None
    
    def convert_value(value):
        if isinstance(value, Binary):
            # Convert Binary to UUID string
            return str(uuid.UUID(bytes=bytes(value)))
        elif isinstance(value, uuid.UUID):
            return str(value)
        elif isinstance(value, dict):
            return {k: convert_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [convert_value(item) for item in value]
        else:
            return value
    
    return {k: convert_value(v) for k, v in details.items()}

@strawberry.type
class ActivityLogResponse:
    activity_type: Optional[str] = None
    created_at: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    chat_id: Optional[str] = None
    details: Optional[JSON] = None  # type: ignore

@strawberry.type
class ActivityLogQuery:
    @strawberry.field
    async def fetch_all_activity_logs(self) -> List[ActivityLogResponse]:
        try:
            
            db = DatabaseManager()
            await db.connect([ActivityLog])
            result = await ActivityLog.find_all().sort('-created_at').limit(10).to_list()
            
            if result:
                log_infos = []
                
                for log in result:
                    log_info = ActivityLogResponse(
                        activity_type=log.activity_type,
                        created_at=log.created_at,
                        project_id=log.project_id,
                        project_name=log.project_name,
                        chat_id=log.chat_id,
                        details=serialize_details(log.details)
                    )
                    log_infos.append(log_info)
                    
                return log_infos
            else:
                return []
            
        except Exception as e:
            logger.error(f"Error fetching all logs {e}")
            return []
        
            
    