"""
Admin-related Pydantic models
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime, timezone
import uuid

class EmailLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    subject: str
    status: str
    error_message: Optional[str] = None
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    timezone: Optional[str] = None
    local_sent_at: Optional[str] = None

class BroadcastRequest(BaseModel):
    message: str
    subject: Optional[str] = None

class BulkUserActionRequest(BaseModel):
    user_emails: List[str]
    action: Literal["activate", "deactivate", "pause_schedule", "resume_schedule", "delete"]

class BulkEmailRequest(BaseModel):
    user_emails: List[str]
    subject: str
    message: str

class AlertConfig(BaseModel):
    alert_type: Literal["error_rate", "api_failure", "rate_limit", "low_engagement"]
    threshold: float
    enabled: bool = True
    email_notification: bool = False

class Achievement(BaseModel):
    id: str
    name: str
    description: str
    icon: str  # Emoji or icon identifier
    category: str  # "streak", "messages", "engagement", "goals"
    requirement: Dict[str, Any]  # Conditions to unlock
    unlocked_at: Optional[datetime] = None

class GoalProgress(BaseModel):
    goal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal_text: str
    target_date: Optional[datetime] = None
    progress_percentage: float = 0.0
    milestones: List[Dict[str, Any]] = []
    completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MessageFavorite(BaseModel):
    message_id: str
    favorited_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MessageCollection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    message_ids: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

