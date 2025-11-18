"""
Pydantic models for the application
"""
from .message import (
    PersonalityType,  # PersonalityType is defined in message.py
    MessageFeedback,
    MessageFeedbackCreate,
    MessageHistory,
    MessageGenRequest,
    MessageGenResponse,
    EmailReplyConversation,
    EmailReplyAnalysis
)

from .user import (
    ScheduleConfig,
    UserProfile,
    LoginRequest,
    VerifyTokenRequest,
    OnboardingRequest,
    UserProfileUpdate,
    UserSession,
    UserAnalytics
)

from .goal import (
    SendTimeWindow,
    GoalSchedule,
    GoalCreateRequest,
    GoalUpdateRequest,
    GoalMessage
)

from .admin import (
    EmailLog,
    BroadcastRequest,
    BulkUserActionRequest,
    BulkEmailRequest,
    AlertConfig,
    Achievement,
    GoalProgress,
    MessageFavorite,
    MessageCollection
)

from .persona import PersonaResearch

from .custom_personality import (
    CustomPersonalityRequest,
    CustomPersonalityConversation,
    CustomPersonalityProfile,
    CustomPersonalityChatRequest,
    CustomPersonalityChatResponse,
    CustomPersonalityResearchRequest,
    CustomPersonalityResearchResponse,
    CustomPersonalityConfirmRequest,
    CustomPersonalityConfirmResponse,
    CustomPersonalityListItem,
    UserCustomPersonalitiesResponse
)

__all__ = [
    # User models
    "PersonalityType",
    "ScheduleConfig",
    "UserProfile",
    "LoginRequest",
    "VerifyTokenRequest",
    "OnboardingRequest",
    "UserProfileUpdate",
    "UserSession",
    "UserAnalytics",
    # Message models
    "MessageFeedback",
    "MessageFeedbackCreate",
    "MessageHistory",
    "MessageGenRequest",
    "MessageGenResponse",
    "EmailReplyConversation",
    "EmailReplyAnalysis",
    # Goal models
    "SendTimeWindow",
    "GoalSchedule",
    "GoalCreateRequest",
    "GoalUpdateRequest",
    "GoalMessage",
    # Admin models
    "EmailLog",
    "BroadcastRequest",
    "BulkUserActionRequest",
    "BulkEmailRequest",
    "AlertConfig",
    "Achievement",
    "GoalProgress",
    "MessageFavorite",
    "MessageCollection",
    # Persona models
    "PersonaResearch",
    # Custom Personality models
    "CustomPersonalityRequest",
    "CustomPersonalityConversation",
    "CustomPersonalityProfile",
    "CustomPersonalityChatRequest",
    "CustomPersonalityChatResponse",
    "CustomPersonalityResearchRequest",
    "CustomPersonalityResearchResponse",
    "CustomPersonalityConfirmRequest",
    "CustomPersonalityConfirmResponse",
    "CustomPersonalityListItem",
    "UserCustomPersonalitiesResponse",
]

