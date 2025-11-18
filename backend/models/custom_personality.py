"""
Custom Personality-related Pydantic models

These models support a conversational, multi-step process for creating
custom personalities through chat, research, and confirmation.
"""
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime, timezone
import uuid


class CustomPersonalityRequest(BaseModel):
    """Initial request to start custom personality creation"""
    email: EmailStr  # Changed from user_id to email to match codebase pattern
    initial_message: Optional[str] = None


class CustomPersonalityConversation(BaseModel):
    """Tracks the conversation for building a custom personality"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str  # Changed from user_id to email
    personality_name: Optional[str] = None
    personality_type: Optional[Literal["movie_character", "book_character", "historical_figure", "sports_icon", "other"]] = None
    source_material: Optional[str] = None
    
    # Conversation tracking
    messages: List[Dict[str, str]] = []  # [{"role": "user/assistant", "content": "..."}]
    current_step: int = 1
    max_steps: int = 7
    
    # Extracted information
    extracted_traits: List[str] = []
    extracted_style: Optional[str] = None
    user_examples: List[str] = []
    
    # Research data
    research_completed: bool = False
    research_sources: List[str] = []
    
    # Status
    status: Literal["in_progress", "researching", "preview_ready", "confirmed", "failed"] = "in_progress"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CustomPersonalityProfile(BaseModel):
    """Complete custom personality profile"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str  # Changed from user_id to email
    conversation_id: str
    
    # Basic info
    personality_name: str
    personality_type: str
    source_material: Optional[str] = None
    
    # Personality details
    core_traits: List[str]
    speaking_style: str
    message_themes: List[str]
    catchphrases: List[str] = []
    vocabulary_patterns: List[str] = []
    
    # Generated content
    personality_summary: str
    example_messages: List[Dict[str, str]]  # [{"tone": "energetic", "message": "..."}]
    do_list: List[str]  # Guidelines for message generation
    dont_list: List[str]  # Things to avoid
    
    # Metadata
    research_sources: List[str] = []
    status: Literal["pending", "confirmed", "active", "archived"] = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    times_used: int = 0
    user_rating: Optional[int] = None  # 1-5 stars
    
    @field_validator('user_rating')
    @classmethod
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('user_rating must be between 1 and 5')
        return v


class CustomPersonalityChatRequest(BaseModel):
    """Continue the custom personality conversation"""
    conversation_id: str
    user_message: str


class CustomPersonalityChatResponse(BaseModel):
    """Response from the custom personality chat"""
    conversation_id: str
    bot_message: str
    current_step: int
    needs_research: bool = False
    extracted_data: Optional[Dict[str, Any]] = None
    status: str


class CustomPersonalityResearchRequest(BaseModel):
    """Trigger research for a custom personality"""
    conversation_id: str
    personality_name: str
    user_context: Dict[str, Any]


class CustomPersonalityResearchResponse(BaseModel):
    """Research results and generated profile"""
    conversation_id: str
    research_results: Dict[str, Any]
    personality_profile: CustomPersonalityProfile
    sample_messages: List[str]
    status: Literal["ready_for_preview", "failed"]


class CustomPersonalityConfirmRequest(BaseModel):
    """Confirm or adjust the custom personality"""
    conversation_id: str
    confirmed: bool
    adjustments: Optional[str] = None


class CustomPersonalityConfirmResponse(BaseModel):
    """Confirmation response"""
    personality_id: str
    status: Literal["active", "needs_adjustment"]
    message: str


class CustomPersonalityListItem(BaseModel):
    """Simplified view for listing user's custom personalities"""
    id: str
    personality_name: str
    personality_type: str
    source_material: Optional[str] = None
    status: str
    created_at: datetime
    times_used: int
    user_rating: Optional[int] = None


class UserCustomPersonalitiesResponse(BaseModel):
    """Response for getting user's custom personalities"""
    email: str  # Changed from user_id to email
    custom_personalities: List[CustomPersonalityListItem]
    total_count: int
    active_personality_id: Optional[str] = None

