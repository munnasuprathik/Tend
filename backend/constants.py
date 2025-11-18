"""
Constants used throughout the application
"""
from typing import Dict, List
import re

# Message types for variety
MESSAGE_TYPES = [
    "motivational_story",
    "action_challenge",
    "mindset_shift",
    "accountability_prompt",
    "celebration_message",
    "real_world_example"
]

# Personality blueprints for message generation
PERSONALITY_BLUEPRINTS: Dict[str, List[str]] = {
    "famous": [
        "Open with a quick scene that person would comment on, deliver an unexpected insight in their voice, finish with a decisive micro-challenge.",
        "Share a short true-to-life anecdote the person would tell, highlight the lesson in their trademark style, close with an energizing promise."
    ],
    "tone": [
        "Begin with an emotion check-in that matches the tone, offer one vivid image, end with a grounded next step.",
        "Start with empathy, transition into a clear observation, and close with a gentle but firm call to action."
    ],
    "custom": [
        "Start with a heartfelt acknowledgement, reinforce their values with a fresh metaphor, end with a conversational nudge.",
        "Kick off with an encouraging statement, weave in a relatable micro-story, wrap up with one specific challenge."
    ]
}

# Emotional arcs for message structure
EMOTIONAL_ARCS = [
    "Spark curiosity → Reflect on their journey → Deliver a laser-focused action.",
    "Recognize a recent win → Surface a friction point → Offer a bold reframe.",
    "Empathize with their current pace → Introduce a surprising observation → Issue a confident next move."
]

# Analogy prompts for creative messaging
ANALOGY_PROMPTS = [
    "Connect their current sprint to an unexpected domain such as jazz improvisation, space exploration, or world-class cuisine.",
    "Compare their progress to a craftsperson honing a single stroke - keep it vivid but concise.",
    "Use a metaphor from sports or art that aligns with their goals, but do not mention the word metaphor."
]

# Friendly dares for engagement
FRIENDLY_DARES = [
    "When you complete today's action, reply with a single-word headline for the feeling.",
    "Shoot back two words tonight: one win, one obstacle.",
    "Drop me a note with the headline of your day once you execute.",
    "When you're done, tell me the song that was playing in your head."
]

# Emoji regex for stripping emojis
EMOJI_REGEX = re.compile(
    "["
    "\U0001F300-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "]+"
)

# Achievement definitions - stored in DB, initialized on startup
DEFAULT_ACHIEVEMENTS = [
    {
        "id": "first_streak",
        "name": "Getting Started",
        "description": "Maintain a 3-day streak",
        "icon_name": "Sprout",
        "category": "streak",
        "requirement": {"type": "streak", "value": 3},
        "priority": 1,
        "show_on_home": True
    },
    {
        "id": "week_warrior",
        "name": "Week Warrior",
        "description": "Maintain a 7-day streak",
        "icon_name": "Flame",
        "category": "streak",
        "requirement": {"type": "streak", "value": 7},
        "priority": 2,
        "show_on_home": True
    },
    {
        "id": "month_master",
        "name": "Month Master",
        "description": "Maintain a 30-day streak",
        "icon_name": "Zap",
        "category": "streak",
        "requirement": {"type": "streak", "value": 30},
        "priority": 3,
        "show_on_home": True
    },
    {
        "id": "century_club",
        "name": "Century Club",
        "description": "Maintain a 100-day streak",
        "icon_name": "Trophy",
        "category": "streak",
        "requirement": {"type": "streak", "value": 100},
        "priority": 4,
        "show_on_home": True
    },
    {
        "id": "first_message",
        "name": "First Step",
        "description": "Receive your first message",
        "icon_name": "Mail",
        "category": "messages",
        "requirement": {"type": "messages", "value": 1},
        "priority": 1,
        "show_on_home": True
    },
    {
        "id": "message_collector",
        "name": "Message Collector",
        "description": "Receive 50 messages",
        "icon_name": "BookOpen",
        "category": "messages",
        "requirement": {"type": "messages", "value": 50},
        "priority": 2,
        "show_on_home": False
    },
    {
        "id": "century_messages",
        "name": "Century Messages",
        "description": "Receive 100 messages",
        "icon_name": "Book",
        "category": "messages",
        "requirement": {"type": "messages", "value": 100},
        "priority": 3,
        "show_on_home": False
    },
    {
        "id": "feedback_enthusiast",
        "name": "Feedback Enthusiast",
        "description": "Rate 10 messages",
        "icon_name": "Star",
        "category": "engagement",
        "requirement": {"type": "feedback_count", "value": 10},
        "priority": 2,
        "show_on_home": False
    },
    {
        "id": "goal_setter",
        "name": "Goal Setter",
        "description": "Set your first goal",
        "icon_name": "Target",
        "category": "goals",
        "requirement": {"type": "has_goal", "value": True},
        "priority": 1,
        "show_on_home": True
    },
    {
        "id": "goal_achiever",
        "name": "Goal Achiever",
        "description": "Complete a goal",
        "icon_name": "CheckCircle",
        "category": "goals",
        "requirement": {"type": "goal_completed", "value": 1},
        "priority": 2,
        "show_on_home": True
    },
    {
        "id": "early_bird",
        "name": "Early Bird",
        "description": "Receive messages for 5 consecutive days",
        "icon_name": "Clock",
        "category": "consistency",
        "requirement": {"type": "consecutive_days", "value": 5},
        "priority": 1,
        "show_on_home": True
    },
    {
        "id": "dedicated_learner",
        "name": "Dedicated Learner",
        "description": "Receive messages for 14 consecutive days",
        "icon_name": "BookOpen",
        "category": "consistency",
        "requirement": {"type": "consecutive_days", "value": 14},
        "priority": 2,
        "show_on_home": True
    },
    {
        "id": "feedback_master",
        "name": "Feedback Master",
        "description": "Rate 25 messages",
        "icon_name": "Star",
        "category": "engagement",
        "requirement": {"type": "feedback_count", "value": 25},
        "priority": 3,
        "show_on_home": False
    },
    {
        "id": "message_milestone_250",
        "name": "Message Milestone",
        "description": "Receive 250 messages",
        "icon_name": "Mail",
        "category": "messages",
        "requirement": {"type": "messages", "value": 250},
        "priority": 4,
        "show_on_home": False
    },
    {
        "id": "streak_legend",
        "name": "Streak Legend",
        "description": "Maintain a 365-day streak",
        "icon_name": "Flame",
        "category": "streak",
        "requirement": {"type": "streak", "value": 365},
        "priority": 5,
        "show_on_home": True
    },
    {
        "id": "personality_explorer",
        "name": "Personality Explorer",
        "description": "Try 3 different personalities",
        "icon_name": "Sparkles",
        "category": "engagement",
        "requirement": {"type": "personality_count", "value": 3},
        "priority": 2,
        "show_on_home": True
    },
    {
        "id": "goal_crusher",
        "name": "Goal Crusher",
        "description": "Complete 5 goals",
        "icon_name": "Target",
        "category": "goals",
        "requirement": {"type": "goal_completed", "value": 5},
        "priority": 3,
        "show_on_home": True
    },
    {
        "id": "top_rated",
        "name": "Top Rated",
        "description": "Give 5-star rating to 10 messages",
        "icon_name": "Star",
        "category": "engagement",
        "requirement": {"type": "five_star_ratings", "value": 10},
        "priority": 2,
        "show_on_home": False
    },
    {
        "id": "loyal_member",
        "name": "Loyal Member",
        "description": "Active for 6 months",
        "icon_name": "Award",
        "category": "loyalty",
        "requirement": {"type": "account_age_days", "value": 180},
        "priority": 3,
        "show_on_home": True
    },
    {
        "id": "veteran",
        "name": "Veteran",
        "description": "Active for 1 year",
        "icon_name": "Trophy",
        "category": "loyalty",
        "requirement": {"type": "account_age_days", "value": 365},
        "priority": 4,
        "show_on_home": True
    },
    {
        "id": "message_architect",
        "name": "Message Architect",
        "description": "Receive 500 messages",
        "icon_name": "Book",
        "category": "messages",
        "requirement": {"type": "messages", "value": 500},
        "priority": 5,
        "show_on_home": False
    }
]

