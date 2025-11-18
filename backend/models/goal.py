"""
Goal-related Pydantic models
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime, timezone
import uuid

class SendTimeWindow(BaseModel):
    """Time window for sending emails with timezone"""
    start_time: str = Field(..., pattern=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")  # HH:MM format
    end_time: str = Field(..., pattern=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")  # HH:MM format
    timezone: str = "UTC"
    max_sends: int = Field(1, ge=1, le=50)  # Max sends allowed in this window per day

class GoalSchedule(BaseModel):
    """Schedule configuration for a goal - Enhanced with multiple times support"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal["daily", "weekly", "monthly", "custom"]
    time: str = Field("09:00", pattern=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")  # HH:MM format (backward compat)
    timezone: str = "UTC"
    
    # NEW: Multiple times per day support
    times: List[str] = Field(default_factory=lambda: ["09:00"], min_length=1)  # Multiple times ["09:00", "15:00", "20:00"]
    
    @model_validator(mode='after')
    def ensure_times_from_time(self):
        """Ensure times array is populated from time if times is default/empty"""
        # If times is default ["09:00"] but time is different, use time
        # This handles cases where frontend sends time but not times
        if self.times == ["09:00"] and self.time and self.time != "09:00":
            self.times = [self.time]
        # If times is empty or not set, use time
        elif not self.times or len(self.times) == 0:
            self.times = [self.time] if self.time else ["09:00"]
        # Ensure times array always has at least one valid time
        if not self.times or len(self.times) == 0 or all(not t or not t.strip() for t in self.times):
            self.times = [self.time] if self.time else ["09:00"]
        return self
    
    # Frequency controls
    weekdays: Optional[List[int]] = None  # 0-6, Monday=0, Sunday=6
    monthly_dates: Optional[List[int]] = None  # Days of month (1-31)
    custom_interval: Optional[int] = None  # Every N days
    
    # Date range
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Schedule metadata
    active: bool = True
    schedule_name: Optional[str] = None  # NEW: "Morning Motivation", "Evening Check-in"
    
    custom_personality_id: Optional[str] = None  # ID of custom personality profile to use
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GoalCreateRequest(BaseModel):
    """Request model for creating a goal - Enhanced with multiple schedules"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    mode: Literal["personality", "tone", "custom"]
    personality_id: Optional[str] = None
    tone: Optional[str] = None
    custom_text: Optional[str] = None
    custom_personality_id: Optional[str] = None  # ID of custom personality profile to use
    
    # NEW: Multiple schedules per goal (up to 10)
    schedules: List[GoalSchedule] = Field(..., min_items=1, max_items=10)
    
    # Limits
    send_limit_per_day: Optional[int] = Field(None, ge=1, le=20)
    send_time_windows: Optional[List[SendTimeWindow]] = Field(None, max_length=5)  # Max 5 time windows
    active: bool = True
    
    # NEW: Goal categories for organization
    category: Optional[str] = None  # "Fitness", "Career", "Learning", etc.
    priority: Literal["high", "medium", "low"] = "medium"

class GoalUpdateRequest(BaseModel):
    """Request model for updating a goal"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    mode: Optional[Literal["personality", "tone", "custom"]] = None
    personality_id: Optional[str] = None
    tone: Optional[str] = None
    custom_text: Optional[str] = None
    custom_personality_id: Optional[str] = None  # ID of custom personality profile to use
    schedules: Optional[List[GoalSchedule]] = None
    send_limit_per_day: Optional[int] = Field(None, ge=1, le=50)
    send_time_windows: Optional[List[SendTimeWindow]] = Field(None, max_length=5)  # Max 5 time windows
    active: Optional[bool] = None

class GoalMessage(BaseModel):
    """Message entry for goal-based emails"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal_id: str
    user_email: str
    scheduled_for: datetime
    status: Literal["pending", "sent", "failed", "skipped"] = "pending"
    generated_subject: Optional[str] = None
    generated_body: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivery_response: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

