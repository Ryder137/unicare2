from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class AuditTrailModel:
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None
    username: Optional[str] = None
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)