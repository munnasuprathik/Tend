from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Depends, Header, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Literal, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import AsyncOpenAI
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import pytz
import secrets
import time
import sys
from pathlib import Path

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from activity_tracker import ActivityTracker
from version_tracker import VersionTracker
import warnings
from contextlib import asynccontextmanager
from functools import lru_cache
import re
import html

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')


def get_env(key: str, default: Optional[str] = None) -> str:
    """
    Fetch an environment variable, optionally falling back to a provided default.

    If no value is present and no default is given, a RuntimeError is raised with
    guidance for local development.
    """
    value = os.getenv(key)
    if value:
        return value

    if default is not None:
        warnings.warn(
            f"Environment variable '{key}' not set. Falling back to default value.",
            RuntimeWarning,
            stacklevel=2,
        )
        return default

    raise RuntimeError(
        f"Missing required environment variable '{key}'. "
        "Set it in your shell or define it in backend/.env before starting the server."
    )


# MongoDB connection
mongo_url = get_env('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[get_env('DB_NAME', 'inbox_inspire')]

# OpenAI client
openai_client = AsyncOpenAI(api_key=get_env('OPENAI_API_KEY'))

# Tavily research
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
TAVILY_SEARCH_URL = "https://api.tavily.com/search"

# Cache for personality voice descriptions
personality_voice_cache: Dict[str, str] = {}

message_types = [
    "motivational_story",
    "action_challenge",
    "mindset_shift",
    "accountability_prompt",
    "celebration_message",
    "real_world_example"
]

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

EMOTIONAL_ARCS = [
    "Spark curiosity → Reflect on their journey → Deliver a laser-focused action.",
    "Recognize a recent win → Surface a friction point → Offer a bold reframe.",
    "Empathize with their current pace → Introduce a surprising observation → Issue a confident next move."
]

ANALOGY_PROMPTS = [
    "Connect their current sprint to an unexpected domain such as jazz improvisation, space exploration, or world-class cuisine.",
    "Compare their progress to a craftsperson honing a single stroke - keep it vivid but concise.",
    "Use a metaphor from sports or art that aligns with their goals, but do not mention the word metaphor."
]

FRIENDLY_DARES = [
    "When you complete today's action, reply with a single-word headline for the feeling.",
    "Shoot back two words tonight: one win, one obstacle.",
    "Drop me a note with the headline of your day once you execute.",
    "When you're done, tell me the song that was playing in your head."
]

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


def strip_emojis(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None
    return EMOJI_REGEX.sub("", text)


def extract_interactive_sections(message: str) -> tuple[str, List[str], List[str]]:
    """Split the LLM output into core message, interactive questions, and quick reply prompts."""
    header = "INTERACTIVE CHECK-IN:"
    quick_header = "QUICK REPLY PROMPT:"

    core_message = message
    check_in_lines: List[str] = []
    quick_reply_lines: List[str] = []

    if header in message:
        core_message, remainder = message.split(header, 1)
        core_message = core_message.strip()
        remainder = remainder.strip()

        if quick_header in remainder:
            check_in_block, quick_block = remainder.split(quick_header, 1)
        else:
            check_in_block, quick_block = remainder, ""

        check_in_lines = [
            strip_emojis(line.strip(" -*\t"))
            for line in check_in_block.strip().splitlines()
            if line.strip()
        ]
        quick_reply_lines = [
            strip_emojis(line.strip(" -*\t"))
            for line in quick_block.strip().splitlines()
            if line.strip()
        ]
    else:
        core_message = message.strip()

    return core_message, check_in_lines, quick_reply_lines


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

async def initialize_achievements():
    """Initialize achievements in database if not exists, and add any missing ones"""
    try:
        existing = await db.achievements.find_one({})
        if not existing:
            # First time initialization - add all achievements
            logger.info(f"Initializing achievements: No existing achievements found. Adding {len(DEFAULT_ACHIEVEMENTS)} achievements...")
            for achievement in DEFAULT_ACHIEVEMENTS:
                achievement_copy = achievement.copy()
                achievement_copy["created_at"] = datetime.now(timezone.utc).isoformat()
                achievement_copy["updated_at"] = datetime.now(timezone.utc).isoformat()
                achievement_copy["active"] = True
                await db.achievements.insert_one(achievement_copy)
            logger.info(f"✅ Achievements initialized in database: {len(DEFAULT_ACHIEVEMENTS)} achievements added")
        else:
            # Database exists - check for missing achievements and add them
            existing_ids = await db.achievements.distinct("id")
            logger.info(f"Found {len(existing_ids)} existing achievements in database")
            missing_achievements = [ach for ach in DEFAULT_ACHIEVEMENTS if ach["id"] not in existing_ids]
            if missing_achievements:
                logger.info(f"Adding {len(missing_achievements)} missing achievements...")
                for achievement in missing_achievements:
                    achievement_copy = achievement.copy()
                    achievement_copy["created_at"] = datetime.now(timezone.utc).isoformat()
                    achievement_copy["updated_at"] = datetime.now(timezone.utc).isoformat()
                    achievement_copy["active"] = True
                    await db.achievements.insert_one(achievement_copy)
                logger.info(f"✅ Added {len(missing_achievements)} missing achievements to database")
            else:
                logger.info(f"✅ All {len(DEFAULT_ACHIEVEMENTS)} achievements already exist in database")
        
        # Verify final count
        total_count = await db.achievements.count_documents({})
        active_count = await db.achievements.count_documents({"active": True})
        logger.info(f"📊 Achievement database status: {total_count} total, {active_count} active")
    except Exception as e:
        logger.error(f"❌ Error initializing achievements: {e}", exc_info=True)
        raise

async def get_achievements_from_db():
    """Get all active achievements from database"""
    achievements = await db.achievements.find({"active": True}, {"_id": 0}).to_list(100)
    return {ach["id"]: ach for ach in achievements}

async def check_and_unlock_achievements(email: str, user_data: dict, feedback_count: int = 0):
    """Check and unlock achievements based on user progress"""
    unlocked = []
    current_achievements = user_data.get("achievements", [])
    
    # Get achievements from database
    achievements_dict = await get_achievements_from_db()
    
    for achievement_id, achievement in achievements_dict.items():
        if achievement_id in current_achievements:
            continue  # Already unlocked
        
        req = achievement.get("requirement", {})
        req_type = req.get("type")
        req_value = req.get("value")
        
        unlocked_this = False
        
        if req_type == "streak":
            if user_data.get("streak_count", 0) >= req_value:
                unlocked_this = True
        elif req_type == "messages":
            if user_data.get("total_messages_received", 0) >= req_value:
                unlocked_this = True
        elif req_type == "feedback_count":
            if feedback_count >= req_value:
                unlocked_this = True
        elif req_type == "has_goal":
            if user_data.get("goals") and len(user_data.get("goals", "").strip()) > 0:
                unlocked_this = True
        elif req_type == "goal_completed":
            goal_progress = user_data.get("goal_progress", {})
            completed_count = sum(1 for g in goal_progress.values() if isinstance(g, dict) and g.get("completed", False))
            if completed_count >= req_value:
                unlocked_this = True
        elif req_type == "consecutive_days":
            # Check consecutive days based on last_email_sent
            last_email = user_data.get("last_email_sent")
            if last_email:
                try:
                    last_date = datetime.fromisoformat(last_email.replace('Z', '+00:00'))
                    days_since = (datetime.now(timezone.utc) - last_date).days
                    if days_since <= req_value:
                        unlocked_this = True
                except:
                    pass
        elif req_type == "personality_count":
            personalities = user_data.get("personalities", [])
            if len(personalities) >= req_value:
                unlocked_this = True
        elif req_type == "five_star_ratings":
            # This would need to be tracked separately or calculated from feedback
            # For now, we'll check feedback_count as a proxy
            if feedback_count >= req_value:
                unlocked_this = True
        elif req_type == "account_age_days":
            created_at = user_data.get("created_at")
            if created_at:
                try:
                    created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    account_age = (datetime.now(timezone.utc) - created_date).days
                    if account_age >= req_value:
                        unlocked_this = True
                except:
                    pass
        
        if unlocked_this:
            unlocked.append(achievement_id)
            # Update user achievements with unlock timestamp
            achievement_unlock = {
                "achievement_id": achievement_id,
                "unlocked_at": datetime.now(timezone.utc).isoformat()
            }
            await db.users.update_one(
                {"email": email},
                {
                    "$addToSet": {"achievements": achievement_id},
                    "$push": {"achievement_history": achievement_unlock}
                }
            )
            # Log achievement unlock
            await tracker.log_user_activity(
                email=email,
                action_type="achievement_unlocked",
                action_category="user_action",
                details={
                    "achievement_id": achievement_id,
                    "achievement_name": achievement.get("name", ""),
                    "category": achievement.get("category", "")
                }
            )
    
    return unlocked

def resolve_streak_badge(streak_count: int) -> tuple[str, str]:
    """Return streak icon label and message without emojis."""
    if streak_count >= 100:
        return "[LEGEND]", f"{streak_count} Days - Legendary Consistency"
    if streak_count >= 30:
        return "[ELITE]", f"{streak_count} Days - Elite Momentum"
    if streak_count >= 7:
        return "[FOCUS]", f"{streak_count} Days - Locked In"
    if streak_count == 1:
        return "[DAY 1]", "Day 1 - Let's Build This"
    if streak_count == 0:
        return "[RESET]", "Fresh Start Today"
    return "[STREAK]", f"{streak_count} Day Streak"


def _render_list_items(lines: List[str]) -> str:
    if not lines:
        return ""
    items = "".join(f"<li>{html.escape(line)}</li>" for line in lines)
    return f"<ul>{items}</ul>"


def generate_interactive_defaults(streak_count: int, goals: str) -> tuple[List[str], List[str]]:
    import random

    theme = derive_goal_theme(goals) or (goals.splitlines()[0][:50] if goals else "today")
    theme = theme.strip().rstrip(".") or "today"

    check_templates = [
        f"What small win moves {theme.lower()} forward before the day ends?",
        f"Which move will keep your momentum alive on {theme.lower()}?",
        f"What must happen next so {theme.lower()} doesn't stall?",
    ]

    reply_templates = [
        "Reply with the first action you'll take in the next hour.",
        "Send back the single task you'll finish tonight.",
        "Share the exact move you'll start as soon as you close this email.",
    ]

    check_line = random.choice(check_templates)
    reply_line = random.choice(reply_templates)

    if streak_count and "streak" not in check_line.lower():
        check_line = f"Day {streak_count}: {check_line}"

    return [check_line], [reply_line]


def render_email_html(
    streak_count: int,
    streak_icon: str,
    streak_message: str,
    core_message: str,
    check_in_lines: List[str],
    quick_reply_lines: List[str],
) -> str:
    """Return a clean and concise HTML email body."""
    safe_core = html.escape(core_message).replace("\n", "<br />")
    check_in_block = _render_list_items(check_in_lines)
    quick_reply_block = _render_list_items(quick_reply_lines)

    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6fb; margin: 0; padding: 0; color: #1f2933; }}
            .wrapper {{ max-width: 600px; margin: 32px auto; background: #ffffff; border-radius: 12px; padding: 28px 32px; box-shadow: 0 12px 30px rgba(40,52,71,0.08); }}
            .streak {{ font-size: 13px; letter-spacing: 0.05em; text-transform: uppercase; color: #516070; margin-bottom: 20px; }}
            .streak strong {{ color: #1b3a61; }}
            .message {{ font-size: 16px; line-height: 1.6; margin: 0 0 24px 0; }}
            .panel {{ border-top: 1px solid #e4e8f0; padding-top: 20px; margin-top: 12px; }}
            .panel-title {{ font-size: 13px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: #394966; margin: 0 0 10px 0; }}
            .panel ul {{ margin: 0; padding-left: 18px; color: #1f2933; font-size: 15px; line-height: 1.5; }}
            .panel ul li {{ margin-bottom: 8px; }}
            .signature {{ margin-top: 28px; font-size: 13px; color: #5a687d; }}
            .footer {{ margin-top: 28px; font-size: 11px; color: #8b97aa; text-align: center; }}
            @media (max-width: 520px) {{ .wrapper {{ padding: 24px; }} }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <p class="streak"><strong>{html.escape(streak_icon)}</strong> {html.escape(streak_message)} · {streak_count} day{'s' if streak_count != 1 else ''}</p>
            <div class="message">{safe_core}</div>
            <div class="panel">
                <p class="panel-title">Interactive Check-In</p>
                {check_in_block or "<p style='margin:0;color:#3d4a5c;'>Share what today looks like.</p>"}
            </div>
            <div class="panel">
                <p class="panel-title">Quick Reply Prompt</p>
                {quick_reply_block or "<p style='margin:0;color:#3d4a5c;'>Reply with the first action you'll take next.</p>"}
            </div>
            <div class="signature">
                <span>With you in this,</span>
                <span>InboxInspire Coach</span>
            </div>
            <div class="footer">
                You are receiving this email because you subscribed to InboxInspire updates.
            </div>
        </div>
    </body>
    </html>
    """


def fallback_subject_line(streak: int, goals: str) -> str:
    """Deterministic fallback subject when the LLM is unavailable."""
    options = [
        "Fresh spark for your next win",
        "Your momentum note for today",
        "A quick ignition for progress",
        "Plan the move before the day ends",
        "Clear the runway and launch",
    ]

    if streak > 0:
        options.extend(
            [
                f"Day {streak} and climbing higher",
                f"{streak} days in - keep the cadence",
                f"{streak} mornings of moving forward",
            ]
        )

    goal_theme = derive_goal_theme(goals)
    if goal_theme:
        options.extend(
            [
                f"Shape the next move on {goal_theme}",
                f"Sketch the blueprint for {goal_theme}",
                "Sharpen the idea before it sleeps",
                "Draft the next chapter of the vision",
            ]
        )

    return secrets.choice(options)[:60]


def derive_goal_theme(goals: str) -> str:
    """Extract a short, rephrased theme from the user's goals."""
    if not goals:
        return ""

    primary_line = ""
    for line in goals.splitlines():
        cleaned = line.strip()
        if cleaned:
            primary_line = cleaned
            break

    if not primary_line:
        return ""

    lowered = primary_line.lower()
    for phrase in [
        "i want to",
        "i need to",
        "i'm going to",
        "i will",
        "my goal is to",
        "my goal is",
        "the goal is to",
        "goal:",
        "goal is to",
    ]:
        if lowered.startswith(phrase):
            primary_line = primary_line[len(phrase) :].strip()
            break

    primary_line = re.sub(r"\b(my|our|i|me|mine)\b", "", primary_line, flags=re.IGNORECASE).strip()
    primary_line = re.sub(r"\s{2,}", " ", primary_line)
    return primary_line[:80]


def cleanup_message_text(message: str) -> str:
    """Remove boilerplate lines and keep the message concise."""
    if not message:
        return ""

    filtered_lines = []
    for raw_line in message.splitlines():
        line = raw_line.strip()
        if not line:
            filtered_lines.append("")
            continue
        if "this line was generated by ai" in line.lower():
            continue
        filtered_lines.append(line)

    collapsed = []
    previous_blank = False
    for line in filtered_lines:
        if line == "":
            if not previous_blank:
                collapsed.append("")
            previous_blank = True
        else:
            collapsed.append(line)
            previous_blank = False

    text = "\n".join(collapsed).strip()
    if not text:
        return ""

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paragraphs) > 3:
        paragraphs = paragraphs[:3]
    return "\n\n".join(paragraphs)


async def record_email_log(
    email: str,
    subject: str,
    status: str,
    *,
    sent_dt: Optional[datetime] = None,
    timezone_value: Optional[str] = None,
    error_message: Optional[str] = None,
) -> None:
    if sent_dt is None:
        sent_dt = datetime.now(timezone.utc)

    tz_name = None
    local_sent_at = None
    if timezone_value:
        try:
            tz_obj = pytz.timezone(timezone_value)
            tz_name = timezone_value
            local_sent_at = sent_dt.astimezone(tz_obj).isoformat()
        except Exception:
            tz_name = None
            local_sent_at = None

    log_doc = EmailLog(
        email=email,
        subject=subject,
        status=status,
        error_message=error_message,
        sent_at=sent_dt,
        timezone=tz_name,
        local_sent_at=local_sent_at,
    )
    await db.email_logs.insert_one(log_doc.model_dump())

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize scheduler
scheduler = AsyncIOScheduler()

# Initialize Activity Tracker
tracker = ActivityTracker(db)

# Initialize Version Tracker  
version_tracker = VersionTracker(db)

# Define Models
class PersonalityType(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal["famous", "tone", "custom"]
    value: str
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ScheduleConfig(BaseModel):
    frequency: Literal["daily", "weekly", "monthly", "custom"]
    times: List[str] = ["09:00"]  # Multiple times support
    custom_days: Optional[List[str]] = None  # ["monday", "wednesday", "friday"]
    custom_interval: Optional[int] = None  # For custom frequency: every N days
    monthly_dates: Optional[List[str]] = None  # ["1", "15", "30"] - days of month
    timezone: str = "UTC"
    paused: bool = False
    skip_next: bool = False

class UserProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    goals: str
    personalities: List[PersonalityType] = []  # Multiple personalities support
    rotation_mode: Literal["sequential", "random", "daily_fixed", "weekly_rotation", "favorite_weighted", "time_based"] = "sequential"
    current_personality_index: int = 0
    schedule: ScheduleConfig
    magic_link_token: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True
    last_email_sent: Optional[datetime] = None
    streak_count: int = 0
    total_messages_received: int = 0
    last_active: Optional[datetime] = None
    achievements: List[str] = []  # List of achievement IDs unlocked
    favorite_messages: List[str] = []  # List of message IDs marked as favorite
    message_collections: Dict[str, List[str]] = {}  # Collection name -> message IDs
    goal_progress: Dict[str, Any] = {}  # Goal tracking data
    content_preferences: Dict[str, Any] = {}  # User content preferences

class LoginRequest(BaseModel):
    email: EmailStr

class VerifyTokenRequest(BaseModel):
    email: EmailStr
    token: str

class OnboardingRequest(BaseModel):
    email: EmailStr
    name: str
    goals: str
    personalities: List[PersonalityType]
    rotation_mode: Literal["sequential", "random", "daily_fixed", "weekly_rotation", "favorite_weighted", "time_based"] = "sequential"
    schedule: ScheduleConfig

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    goals: Optional[str] = None
    personalities: Optional[List[PersonalityType]] = None
    rotation_mode: Optional[Literal["sequential", "random", "daily_fixed", "weekly_rotation", "favorite_weighted", "time_based"]] = None
    schedule: Optional[ScheduleConfig] = None
    active: Optional[bool] = None

class MessageFeedback(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    message_id: Optional[str] = None
    personality: PersonalityType
    rating: int  # 1-5 stars
    feedback_text: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MessageFeedbackCreate(BaseModel):
    message_id: Optional[str] = None
    rating: int
    feedback_text: Optional[str] = None
    personality: Optional[PersonalityType] = None

class UserSession(BaseModel):
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MessageHistory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    message: str
    personality: PersonalityType
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    rating: Optional[int] = None
    used_fallback: Optional[bool] = False

class UserAnalytics(BaseModel):
    email: str
    streak_count: int
    total_messages: int
    favorite_personality: Optional[str] = None
    avg_rating: Optional[float] = None
    last_active: Optional[datetime] = None
    engagement_rate: float = 0.0
    personality_stats: dict = {}

class MessageGenRequest(BaseModel):
    goals: str
    personality: PersonalityType
    user_name: Optional[str] = None

class MessageGenResponse(BaseModel):
    message: str
    used_fallback: bool = False

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

# Admin auth
def verify_admin(authorization: str = Header(None)):
    if not authorization or authorization != f"Bearer {os.getenv('ADMIN_SECRET')}":
        raise HTTPException(status_code=403, detail="Unauthorized")
    return True

# SMTP Email Service with connection timeout
async def send_email(to_email: str, subject: str, html_content: str) -> tuple[bool, Optional[str]]:
    subject_line = None
    sent_dt = None
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = os.getenv('SENDER_EMAIL')
        msg['To'] = to_email
        msg['Subject'] = subject
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        await aiosmtplib.send(
            msg,
            hostname=os.getenv('SMTP_HOST'),
            port=int(os.getenv('SMTP_PORT')),
            username=os.getenv('SMTP_USERNAME'),
            password=os.getenv('SMTP_PASSWORD'),
            use_tls=True,
            timeout=10  # 10 second timeout
        )
        
        return True, None
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Email send error: {error_msg}")
        
        return False, error_msg

# Enhanced LLM Service with deep personality matching
async def generate_unique_motivational_message(
    goals: str, 
    personality: PersonalityType, 
    name: Optional[str] = None,
    streak_count: int = 0,
    previous_messages: list = None
) -> tuple[str, str, bool, Optional[str]]:
    """Generate UNIQUE, engaging motivational message with questions - never repeat"""
    try:
        # Get previous message types to avoid repetition
        recent_types = []
        if previous_messages:
            recent_types = [msg.get('message_type', '') for msg in previous_messages[:5]]
        
        # Choose a message type we haven't used recently
        available_types = [t for t in message_types if t not in recent_types]
        if not available_types:
            available_types = message_types
        
        import random
        message_type = random.choice(available_types)
        blueprint_pool = PERSONALITY_BLUEPRINTS.get(personality.type, PERSONALITY_BLUEPRINTS["custom"])
        blueprint = random.choice(blueprint_pool)
        emotional_arc = random.choice(EMOTIONAL_ARCS)
        recent_themes_block = build_recent_themes(previous_messages)
        include_analogy = random.random() < 0.6
        analogy_instruction = random.choice(ANALOGY_PROMPTS) if include_analogy else ""
        dare_instruction = random.choice(FRIENDLY_DARES) if random.random() < 0.5 else ""
        # Personality style via research
        voice_profile = await fetch_personality_voice(personality)
        if voice_profile:
            personality_prompt = f"""VOICE PROFILE:
    {voice_profile}
    RULES:
    - Write exactly in this voice.
    - Do not mention these notes, the personality name, or that you researched it.
    - Use natural, human language - no AI phrasing."""
        else:
            fallback_voice = personality.value if personality.value else "warm, encouraging mentor"
            personality_prompt = f"""VOICE PROFILE:
Sound like a {fallback_voice}.
RULES:
- Capture their energy and mannerisms authentically.
- Do not say you are copying anyone or mention tone explicitly.
- Keep the language human and grounded."""
        
        # Streak milestone messages
        streak_context = ""
        if streak_count >= 100:
            streak_context = f"[LEGEND] {streak_count} days of consistency. You're in the top 1%."
        elif streak_count >= 30:
            streak_context = f"[ELITE] {streak_count} day streak! You've built a real habit here."
        elif streak_count >= 7:
            streak_context = f"[STRONG] {streak_count} days locked in. The hardest part is behind you."
        elif streak_count >= 1:
            streak_context = f"[DAY {streak_count}] Every journey starts with a single step."
        else:
            streak_context = "[LAUNCH] Starting fresh. Let's build momentum."
        
        research_snippet = await fetch_research_snippet(goals, personality)
        insights_block = f"RESEARCH INSIGHT: {research_snippet}\n" if research_snippet else ""

        latest_message_snippet = ""
        if previous_messages:
            latest_raw = previous_messages[0].get("message", "").strip()
            if latest_raw:
                latest_message_snippet = latest_raw.split("\n")[0][:220]
            latest_persona = previous_messages[0].get("personality", {}).get("value")
        else:
            latest_persona = None
        
        prompt = f"""You are an elite personal coach creating a UNIQUE daily motivation message.

{personality_prompt}

USER'S GOALS: {goals}
STREAK COUNT: {streak_count}
PERSONALITY MODE: {personality.type}
PERSONALITY VALUE: {personality.value}
LAST PERSONA USED: {latest_persona or "unknown"}
LATEST MESSAGE SAMPLE: {latest_message_snippet or "None"}
STREAK CONTEXT: {streak_context}
MESSAGE TYPE: {message_type}
{insights_block}
STORY BLUEPRINT: {blueprint}
EMOTIONAL ARC: {emotional_arc}
{("RECENT THEMES TO AVOID:\n" + recent_themes_block) if recent_themes_block else ""}
{analogy_instruction}

CRITICAL RULES:
1. NEVER copy/paste the user's goals - reference them creatively and naturally
2. Make it COMPLETELY UNIQUE - no generic phrases
3. Be SPECIFIC and ACTIONABLE - not vague platitudes
4. Keep it tight - no more than TWO short paragraphs and one single-sentence closing action line.
5. Make it CONVERSATIONAL - like texting a friend who cares.
6. If a research insight is provided, weave it naturally into the story without sounding like a summary or citing the source.
7. Do not repeat ideas from recent themes. Never mention that you are avoiding repetition.
8. Vary sentence length - mix short punchy lines with longer flowing ones.
9. Sound undeniably human; use tactile details and sensory language.
10. Close with a crystal-clear micro action. {("Then add: " + dare_instruction) if dare_instruction else ""}
11. Do NOT use emojis, emoticons, or Unicode pictographs; rely on plain words or ASCII icons (e.g. [*], ->) for emphasis.
12. After the core message, create a section formatted exactly like this:

INTERACTIVE CHECK-IN:
- Provide exactly one bullet beginning with "- " that asks a thoughtful question or challenge tied to the goals and streak.

QUICK REPLY PROMPT:
- Provide exactly one bullet beginning with "- " that gives a precise reply instruction (actionable and time-bound).

Make both bullets unique to this user and today's message.


MESSAGE TYPE GUIDELINES:
- motivational_story: Share a brief, real example of someone who overcame similar challenges
- action_challenge: Give ONE specific task to accomplish today
- mindset_shift: Reframe their thinking about obstacles
- accountability_prompt: Check in on progress and create urgency
- celebration_message: Recognize recent progress and build confidence
- real_world_example: Use concrete analogies from business/sports/life

STRUCTURE:
1. Hook with the streak celebration or surprising insight
2. Core message (2-3 paragraphs) - tie to their goals WITHOUT quoting them
3. Call to action or mindset shift
4. DO NOT include a question - it will be added separately

Write an authentic, powerful message that feels personal and impossible to ignore:"""

        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a world-class motivational coach who creates deeply personal, unique messages that inspire real action. You never use cliches, never repeat yourself, and you always sound human - not like an AI summarizer. Every message feels handcrafted."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,  # Higher for more creativity
            max_tokens=500,
            presence_penalty=0.6,  # Avoid repetition
            frequency_penalty=0.6   # Encourage variety
        )
        
        message = strip_emojis(response.choices[0].message.content.strip())
        message = cleanup_message_text(message)
        
        return message, message_type, False, research_snippet
        
    except Exception as e:
        logger.error(f"Error generating message: {str(e)}")
        try:
            await tracker.log_system_event(
                event_type="llm_generation_failed",
                event_category="llm",
                details={
                    "personality": personality.value if personality else None,
                    "error": str(e)
                },
                status="error"
            )
        except Exception:
            pass
        ci_defaults, qr_defaults = generate_interactive_defaults(streak_count, goals)
        default_msg = (
            f"Day {streak_count} of your journey.\n\n"
            "You already know the lever that moves the day—choose it and commit.\n\n"
            "INTERACTIVE CHECK-IN:\n"
            + "\n".join(f"- {line}" for line in ci_defaults)
            + "\n\nQUICK REPLY PROMPT:\n"
            + "\n".join(f"- {line}" for line in qr_defaults)
        )
        default_msg = strip_emojis(default_msg)
        default_msg = cleanup_message_text(default_msg)
        return default_msg, "default", True, None

# Backward compatibility wrapper
async def generate_motivational_message(goals: str, personality: PersonalityType, name: Optional[str] = None) -> str:
    """Wrapper for backward compatibility"""
    message, _, _, _ = await generate_unique_motivational_message(goals, personality, name, 0, [])
    return message

# Get current personality for user based on rotation mode
async def fetch_research_snippet(goals: str, personality: PersonalityType) -> Optional[str]:
    """
    Fetch a short, fresh insight using Tavily to keep emails feeling researched.
    Returns a one or two sentence snippet or None.
    """
    if not TAVILY_API_KEY or not goals:
        return None

    query_parts = [goals.strip()]
    if personality and personality.value:
        query_parts.append(f'{personality.value} style inspiration')
    query = " ".join(query_parts)

    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": 3,
    }

    try:
        async with httpx.AsyncClient(timeout=6) as client:
            response = await client.post(TAVILY_SEARCH_URL, json=payload)
            if response.status_code == 429:
                try:
                    await tracker.log_system_event(
                        event_type="tavily_rate_limit",
                        event_category="research",
                        details={"query": query},
                        status="warning"
                    )
                except Exception:
                    pass
                return None
            response.raise_for_status()
            data = response.json()

        results = data.get("results") or []
        for result in results:
            content = result.get("content") or result.get("snippet")
            if content:
                trimmed = content.strip()
                if len(trimmed) > 300:
                    trimmed = trimmed[:297].rsplit(" ", 1)[0] + "..."
                return trimmed

    except Exception as e:
        logger.warning(f"Tavily research failed: {e}")
        try:
            await tracker.log_system_event(
                event_type="tavily_error",
                event_category="research",
                details={"query": query, "error": str(e)},
                status="warning"
            )
        except Exception:
            pass

    return None


async def fetch_personality_voice(personality: PersonalityType) -> Optional[str]:
    """
    Fetch a concise description of how the requested personality or tone speaks.
    Results are cached to avoid repeated lookups.
    """
    if personality is None:
        return None

    cache_key = f"{personality.type}:{personality.value}"
    if cache_key in personality_voice_cache:
        return personality_voice_cache[cache_key]

    if personality.type == "custom":
        personality_voice_cache[cache_key] = personality.value
        return personality.value

    if not TAVILY_API_KEY:
        return None

    if personality.type == "famous":
        query = f"What is the communication style of {personality.value}? Describe tone, pacing, vocabulary, and attitude."
    elif personality.type == "tone":
        query = f"Describe how to communicate in a {personality.value.lower()} tone. Focus on voice, energy, and sentence structure."
    else:
        query = f"Describe the communication style called {personality.value}. Focus on how it sounds."

    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": 2,
    }

    try:
        async with httpx.AsyncClient(timeout=6) as client:
            response = await client.post(TAVILY_SEARCH_URL, json=payload)
            if response.status_code == 429:
                try:
                    await tracker.log_system_event(
                        event_type="tavily_rate_limit",
                        event_category="research",
                        details={"query": query},
                        status="warning"
                    )
                except Exception:
                    pass
                return None
            response.raise_for_status()
            data = response.json()

        results = data.get("results") or []
        for result in results:
            content = result.get("content") or result.get("snippet")
            if content:
                trimmed = content.strip()
                if len(trimmed) > 400:
                    trimmed = trimmed[:397].rsplit(" ", 1)[0] + "..."
                personality_voice_cache[cache_key] = trimmed
                return trimmed
    except Exception as e:
        logger.warning(f"Tavily personality research failed: {e}")
        try:
            await tracker.log_system_event(
                event_type="tavily_error",
                event_category="research",
                details={"query": query, "error": str(e)},
                status="warning"
            )
        except Exception:
            pass

    return None


def build_recent_themes(previous_messages: List[dict]) -> str:
    """Create a brief list of themes from previous emails to reduce repetition."""
    if not previous_messages:
        return ""

    themes = []
    for msg in previous_messages[:5]:
        text = msg.get("message", "")
        if not text:
            continue
        snippet = text.strip().split("\n")[0]
        snippet = snippet[:140].rsplit(" ", 1)[0] if len(snippet) > 140 else snippet
        message_type = msg.get("message_type")
        if message_type:
            themes.append(f"- ({message_type}) {snippet}")
        else:
            themes.append(f"- {snippet}")

    return "\n".join(themes[:5])


def build_subject_line(
    personality: PersonalityType,
    message_type: str,
    user_data: dict,
    research_snippet: Optional[str],
    used_fallback: bool
) -> str:
    import random

    streak = user_data.get("streak_count", 0)
    raw_goal = user_data.get("goals") or ""
    goal_line = raw_goal.split("\n")[0][:80]
    goal_theme = derive_goal_theme(raw_goal)

    momentum_words = [
        "spark",
        "stride",
        "pulse",
        "tempo",
        "heartbeat",
        "rhythm",
        "signal",
        "sparkline",
    ]
    action_words = [
        "takes shape",
        "moves forward",
        "kicks off",
        "gains traction",
        "locks in",
        "hits the runway",
        "winds up",
        "comes alive",
    ]

    goal_phrase = (goal_theme or goal_line or "").strip()
    templates = [
        f"Today's {random.choice(momentum_words)} {random.choice(action_words)}",
        f"Keep the {random.choice(momentum_words)} moving",
        f"{random.choice(momentum_words).capitalize()} fuels your next stride",
        f"Plot the next {random.choice(momentum_words)} move",
    ]

    if goal_phrase:
        trimmed_goal = goal_phrase[:50]
        templates.extend(
            [
                f"{trimmed_goal} gets new {random.choice(momentum_words)}",
                f"Steps toward {trimmed_goal} today",
                f"Edge closer on {trimmed_goal}",
            ]
        )

    if streak > 0:
        templates.extend(
            [
                f"{streak} days in - stay on tempo",
                f"{streak} mornings and momentum rising",
            ]
        )

    if research_snippet:
        snippet = research_snippet.strip().split(".")[0][:40]
        templates.extend(
            [
                f"Insight to try: {snippet}",
                f"Research spark: {snippet}",
            ]
        )

    if used_fallback:
        templates.extend(
            [
                "Momentum stays with you today",
                "Another nudge is in your inbox",
            ]
        )

    templates = [t for t in templates if t]
    if not templates:
        templates = ["Your daily momentum note"]

    subject = random.choice(templates).strip()
    return strip_emojis(subject)[:60]


async def compose_subject_line(
    personality: PersonalityType,
    message_type: str,
    user_data: dict,
    used_fallback: bool,
    research_snippet: Optional[str]
) -> str:
    goals = (user_data.get("goals") or "").strip()
    goal_theme = derive_goal_theme(goals)
    streak = user_data.get("streak_count", 0)
    fallback_subject = fallback_subject_line(streak, goals)

    try:
        prompt = f"""
You are crafting an email subject line for a motivational newsletter.

REQUIREMENTS:
- Keep it under 60 characters.
- Do NOT mention any personality, persona, or tone names.
- Make it fresh, human, and emotionally resonant.
- Do NOT copy the user's goal wording; paraphrase or imply it instead.
- Use the goal theme as a springboard but phrase it in new words.
- Hint at today's message theme without sounding clickbait or repeating prior subjects.
- If a streak count exists, acknowledge progress without repeating the word "streak".
- If a research insight is provided, allude to it without sounding academic.

INPUTS:
- Streak count: {streak}
- Message type: {message_type}
- Goal theme: {goal_theme or "None supplied"}
- Research snippet: {research_snippet or "None"}
- Previous fallback used: {"Yes" if used_fallback else "No"}

Return only the subject line."""  # noqa: E501

        response = await openai_client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "You write vivid, human email subject lines for a motivational product. "
                        "They feel handcrafted, avoid gimmicks, refuse cliches, and never mention tone/persona names."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.75,
            max_output_tokens=24,
        )

        subject = response.output_text.strip().strip('"\'')
        subject = strip_emojis(subject)
        return subject if subject else fallback_subject

    except Exception as e:
        logger.warning(f"Subject line generation failed: {e}")
        try:
            await tracker.log_system_event(
                event_type="subject_generation_failed",
                event_category="llm",
                details={
                    "user_email": user_data.get("email"),
                    "message_type": message_type,
                    "error": str(e),
                },
                status="warning",
            )
        except Exception:
            pass

        return fallback_subject


def get_current_personality(user_data):
    personalities = user_data.get('personalities', [])
    if not personalities:
        return PersonalityType(
            type="custom",
            value=user_data.get("custom_personality_description", "a warm, encouraging mentor"),
        )
    
    rotation_mode = user_data.get('rotation_mode', 'sequential')
    current_index = user_data.get('current_personality_index', 0)
    
    if rotation_mode == "random":
        import random
        return PersonalityType(**random.choice(personalities))
    
    elif rotation_mode == "daily_fixed":
        # Each personality gets a specific day
        from datetime import datetime
        day_index = datetime.now().weekday()
        personality_index = day_index % len(personalities)
        return PersonalityType(**personalities[personality_index])
    
    elif rotation_mode == "weekly_rotation":
        # Rotate weekly - same personality all week
        from datetime import datetime
        week_number = datetime.now().isocalendar()[1]
        personality_index = week_number % len(personalities)
        return PersonalityType(**personalities[personality_index])
    
    elif rotation_mode == "time_based":
        # Morning vs Evening personalities
        from datetime import datetime
        hour = datetime.now().hour
        if hour < 12:  # Morning - first half
            personality_index = 0 if len(personalities) == 1 else 0
        else:  # Afternoon/Evening - second half
            personality_index = (len(personalities) // 2) if len(personalities) > 1 else 0
        return PersonalityType(**personalities[min(personality_index, len(personalities) - 1)])
    
    elif rotation_mode == "favorite_weighted":
        # TODO: Implement weighted selection based on ratings
        # For now, fall back to sequential
        return PersonalityType(**personalities[current_index])
    
    else:  # sequential
        personality = PersonalityType(**personalities[current_index])
        return personality

async def update_streak(email: str, sent_timestamp: Optional[datetime] = None):
    """Update user streak count based on consecutive days of receiving emails"""
    user = await db.users.find_one({"email": email})
    if not user:
        return
    
    if sent_timestamp is None:
        sent_timestamp = datetime.now(timezone.utc)
    
    last_sent = user.get('last_email_sent')
    current_streak = user.get('streak_count', 0)
    
    if last_sent:
        if isinstance(last_sent, str):
            try:
                last_sent = datetime.fromisoformat(last_sent.replace('Z', '+00:00'))
            except:
                last_sent = datetime.fromisoformat(last_sent)
        
        # Normalize to dates (ignore time)
        last_sent_date = last_sent.date()
        current_date = sent_timestamp.date()
        
        # Calculate days difference
        days_diff = (current_date - last_sent_date).days
        
        if days_diff == 0:
            # Same day - don't increment, keep current streak
            new_streak = current_streak
        elif days_diff == 1:
            # Consecutive day - increment streak
            new_streak = current_streak + 1
        else:
            # Gap of more than 1 day - reset to 1
            new_streak = 1
    else:
        # First email ever - start at 1
        new_streak = 1
    
    # Update streak in database
    await db.users.update_one(
        {"email": email},
        {"$set": {"streak_count": new_streak}}
    )
    
    logger.info(f"Updated streak for {email}: {current_streak} -> {new_streak} (last_sent: {last_sent}, days_diff: {(sent_timestamp.date() - (last_sent.date() if last_sent else sent_timestamp.date())).days if last_sent else 'N/A'})")
    
    return new_streak

# Send email to a SPECIFIC user (called by scheduler)
async def send_motivation_to_user(email: str):
    """Send motivation email to a specific user - called by their scheduled job"""
    subject_line: Optional[str] = None
    sent_dt: Optional[datetime] = None
    schedule: Optional[dict] = None
    try:
        # Get the specific user
        user_data = await db.users.find_one({"email": email, "active": True}, {"_id": 0})
        
        if not user_data:
            logger.warning(f"User {email} not found or inactive")
            return
        
        # Check if paused or skip next
        schedule = user_data.get('schedule', {})
        if schedule.get('paused', False):
            logger.info(f"Skipping {email} - schedule paused")
            return
        
        if schedule.get('skip_next', False):
            # Reset skip_next flag
            await db.users.update_one(
                {"email": email},
                {"$set": {"schedule.skip_next": False}}
            )
            logger.info(f"Skipped {email} - skip_next was set")
            return
        
        # Get user data (we'll update streak after sending email)
        user_data = await db.users.find_one({"email": email}, {"_id": 0})
        
        # Get current personality
        personality = get_current_personality(user_data)
        if not personality:
            logger.warning(f"No personality found for {email}")
            return
        
        # Calculate streak FIRST (before generating message) to use correct streak in email
        sent_dt = datetime.now(timezone.utc)
        sent_timestamp = sent_dt.isoformat()
        
        # Calculate what the streak will be after sending this email
        current_streak = user_data.get('streak_count', 0)
        last_sent = user_data.get('last_email_sent')
        
        if last_sent:
            if isinstance(last_sent, str):
                try:
                    last_sent_dt = datetime.fromisoformat(last_sent.replace('Z', '+00:00'))
                except:
                    last_sent_dt = datetime.fromisoformat(last_sent)
            else:
                last_sent_dt = last_sent
                
            last_sent_date = last_sent_dt.date()
            current_date = sent_dt.date()
            days_diff = (current_date - last_sent_date).days
            
            if days_diff == 0:
                # Same day - keep current streak (don't increment)
                streak_count = current_streak if current_streak > 0 else 1
                logger.info(f"Streak calculation for {email}: Same day ({current_date}), keeping streak at {streak_count}")
            elif days_diff == 1:
                # Consecutive day - increment streak
                streak_count = current_streak + 1
                logger.info(f"Streak calculation for {email}: Consecutive day ({last_sent_date} -> {current_date}), incrementing {current_streak} -> {streak_count}")
            else:
                # Gap of more than 1 day - reset to 1
                streak_count = 1
                logger.info(f"Streak calculation for {email}: Gap of {days_diff} days ({last_sent_date} -> {current_date}), resetting to {streak_count}")
        else:
            # First email ever - start at 1
            streak_count = 1
            logger.info(f"Streak calculation for {email}: First email ever, starting at {streak_count}")
        
        # Get previous messages to avoid repetition
        previous_messages = await db.message_history.find(
            {"email": email},
            {"_id": 0}
        ).sort("created_at", -1).limit(10).to_list(10)
        
        # Generate UNIQUE message with questions using the CALCULATED streak
        message, message_type, used_fallback, research_snippet = await generate_unique_motivational_message(
            user_data['goals'],
            personality,
            user_data.get('name'),
            streak_count,  # Use calculated streak, not old one
            previous_messages
        )
        
        if used_fallback:
            try:
                await tracker.log_system_event(
                    event_type="llm_generation_fallback",
                    event_category="llm",
                    details={
                        "user_email": email,
                        "personality": personality.value if personality else None
                    },
                    status="warning"
                )
            except Exception:
                pass
        
        # Save to message history with message type for tracking
        message_id = str(uuid.uuid4())
        history_doc = {
            "id": message_id,
            "email": email,
            "message": message,
            "personality": personality.model_dump(),
            "message_type": message_type,
            "created_at": sent_timestamp,
            "sent_at": sent_timestamp,
            "streak_at_time": streak_count,
            "used_fallback": used_fallback
        }
        await db.message_history.insert_one(history_doc)
        
        streak_icon, streak_message = resolve_streak_badge(streak_count)
        core_message, check_in_lines, quick_reply_lines = extract_interactive_sections(message)
        ci_defaults, qr_defaults = generate_interactive_defaults(
            streak_count,
            user_data.get('goals', ''),
        )
        check_in_lines = check_in_lines or ci_defaults
        quick_reply_lines = quick_reply_lines or qr_defaults

        html_content = render_email_html(
            streak_count=streak_count,
            streak_icon=streak_icon,
            streak_message=streak_message,
            core_message=core_message,
            check_in_lines=check_in_lines,
            quick_reply_lines=quick_reply_lines,
        )

        # Create updated user_data with new streak for subject line generation
        updated_user_data = user_data.copy()
        updated_user_data['streak_count'] = streak_count

        subject_line = await compose_subject_line(
            personality,
            message_type,
            updated_user_data,  # Use updated user_data with new streak
            used_fallback,
            research_snippet
        )

        success, error = await send_email(email, subject_line, html_content)
        
        if success:
            # Update streak and last email sent time
            # Rotate personality if sequential
            personalities = user_data.get('personalities', [])
            update_data = {
                "last_email_sent": sent_timestamp,
                "last_active": sent_timestamp,
                "streak_count": streak_count
            }
            
            if user_data.get('rotation_mode') == 'sequential' and len(personalities) > 1:
                current_index = user_data.get('current_personality_index', 0)
                next_index = (current_index + 1) % len(personalities)
                update_data["current_personality_index"] = next_index
            
            await db.users.update_one(
                {"email": email},
                {
                    "$set": update_data,
                    "$inc": {"total_messages_received": 1}
                }
            )
            
            logger.info(f"✅ Email sent to {email} - Streak updated to {streak_count} days")
            
            await record_email_log(
                email=email,
                subject=subject_line,
                status="success",
                sent_dt=sent_dt,
                timezone_value=schedule.get("timezone"),
            )
            logger.info(f"✓ Sent motivation to {email}")
        else:
            await record_email_log(
                email=email,
                subject=subject_line,
                status="failed",
                sent_dt=sent_dt,
                timezone_value=schedule.get("timezone"),
                error_message=error,
            )
            logger.error(f"✗ Failed to send to {email}: {error}")
            
    except Exception as e:
        logger.error(f"Error sending to {email}: {str(e)}")
        await record_email_log(
            email=email,
            subject=subject_line or "Motivation Delivery",
            status="failed",
            sent_dt=sent_dt,
            timezone_value=schedule.get("timezone") if isinstance(schedule, dict) else None,
            error_message=str(e),
        )

# Background job to send scheduled emails (DEPRECATED - keeping for backwards compatibility)
async def send_scheduled_motivations():
    """DEPRECATED: This function is no longer used. Each user has their own scheduled job."""
    logger.warning("send_scheduled_motivations called - this function is deprecated")
    try:
        users = await db.users.find({"active": True}, {"_id": 0}).to_list(1000)
        
        for user_data in users:
            try:
                # Check if paused or skip next
                schedule = user_data.get('schedule', {})
                if schedule.get('paused', False):
                    continue
                
                if schedule.get('skip_next', False):
                    # Reset skip_next flag
                    await db.users.update_one(
                        {"email": user_data['email']},
                        {"$set": {"schedule.skip_next": False}}
                    )
                    continue
                
                # Get current personality
                personality = get_current_personality(user_data)
                if not personality:
                    continue
                
                # Generate message
                message = await generate_motivational_message(
                    user_data['goals'],
                    personality,
                    user_data.get('name')
                )
                
                # Create HTML email
                # Save to message history
                message_id = str(uuid.uuid4())
                history = MessageHistory(
                    id=message_id,
                    email=user_data['email'],
                    message=message,
                    personality=personality
                )
                await db.message_history.insert_one(history.model_dump())
                
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: 'Georgia', serif; line-height: 1.8; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; }}
                        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; }}
                        .header h1 {{ color: white; margin: 0; font-size: 28px; font-weight: 600; }}
                        .content {{ background: #ffffff; padding: 40px 30px; }}
                        .message {{ font-size: 16px; line-height: 1.8; color: #2d3748; white-space: pre-wrap; }}
                        .signature {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #e2e8f0; font-style: italic; color: #718096; }}
                        .footer {{ text-align: center; padding: 20px; color: #a0aec0; font-size: 12px; }}
                        .streak {{ background: #f7fafc; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; }}
                        .streak-count {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Your Daily Inspiration</h1>
                        </div>
                        <div class="content">
                            <p style="font-size: 18px; color: #4a5568; margin-bottom: 25px;">Hello {user_data.get('name', 'there')},</p>
                            
                            <div class="streak">
                                <div>[STREAK] Your Progress</div>
                                <div class="streak-count">{user_data.get('streak_count', 0)} Days</div>
                            </div>
                            
                            <div class="message">{message}</div>
                            <div class="signature">
                                - Inspired by {personality.value}
                            </div>
                        </div>
                        <div class="footer">
                            <p>You're receiving this because you subscribed to InboxInspire</p>
                            <p>Keep pushing towards your goals!</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                success, error = await send_email(
                    user_data['email'],
                    f"Your Daily Motivation from {personality.value}",
                    html_content
                )
                
                if success:
                    # Calculate and update streak
                    sent_dt = datetime.now(timezone.utc)
                    sent_timestamp = sent_dt.isoformat()
                    new_streak = await update_streak(user_data['email'], sent_dt)
                    
                    # Rotate personality if sequential
                    personalities = user_data.get('personalities', [])
                    update_data = {
                        "last_email_sent": sent_timestamp,
                        "last_active": sent_timestamp,
                        "streak_count": new_streak
                    }
                    
                    if user_data.get('rotation_mode') == 'sequential' and len(personalities) > 1:
                        current_index = user_data.get('current_personality_index', 0)
                        next_index = (current_index + 1) % len(personalities)
                        update_data["current_personality_index"] = next_index
                    
                    await db.users.update_one(
                        {"email": user_data['email']},
                        {
                            "$set": update_data,
                            "$inc": {"total_messages_received": 1}
                        }
                    )
                    
                    logging.info(f"Sent motivation to {user_data['email']}")
                else:
                    logging.error(f"Failed to send to {user_data['email']}: {error}")
                    
            except Exception as e:
                logging.error(f"Error processing {user_data.get('email', 'unknown')}: {str(e)}")
        
    except Exception as e:
        logging.error(f"Scheduled job error: {str(e)}")

# Routes
@api_router.get("/")
async def root():
    return {"message": "InboxInspire API", "version": "2.0"}

@api_router.post("/auth/login")
async def login(request: LoginRequest, background_tasks: BackgroundTasks, req: Request):
    """Send magic link to email"""
    # Track login attempt
    ip_address = req.client.host if req.client else None
    user_agent = req.headers.get("user-agent")
    
    # Generate magic link token
    token = secrets.token_urlsafe(32)
    
    # Check if user exists
    user = await db.users.find_one({"email": request.email}, {"_id": 0})
    
    if user:
        # Update existing user with new token
        await db.users.update_one(
            {"email": request.email},
            {"$set": {"magic_link_token": token}}
        )
        user_exists = True
        
        # Track login request for existing user
        await tracker.log_user_activity(
            action_type="login_requested",
            user_email=request.email,
            details={"user_type": "existing"},
            ip_address=ip_address,
            user_agent=user_agent
        )
    else:
        # Store pending login
        await db.pending_logins.update_one(
            {"email": request.email},
            {"$set": {"token": token, "created_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )
        user_exists = False
        
        # Track login request for new user
        await tracker.log_user_activity(
            action_type="login_requested",
            user_email=request.email,
            details={"user_type": "new"},
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    # Prepare magic link email
    magic_link = f"https://aipep.preview.emergentagent.com/?token={token}&email={request.email}"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: 600; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Welcome to InboxInspire!</h2>
            <p>Click the button below to access your account:</p>
            <p><a href="{magic_link}" class="button">Access My Account</a></p>
            <p style="color: #666; font-size: 12px;">Or copy this link: {magic_link}</p>
            <p style="color: #666; font-size: 12px;">This link expires in 1 hour.</p>
        </div>
    </body>
    </html>
    """
    
    # Send email in background - immediate response to user
    background_tasks.add_task(send_email, request.email, "Your InboxInspire Login Link", html_content)
    
    return {"status": "success", "message": "Login link sent to your email", "user_exists": user_exists}

@api_router.post("/auth/verify")
async def verify_token(request: VerifyTokenRequest):
    """Verify magic link token"""
    # Check existing user
    user = await db.users.find_one({"email": request.email, "magic_link_token": request.token}, {"_id": 0})
    
    if user:
        # Clear token after use
        await db.users.update_one(
            {"email": request.email},
            {"$set": {"magic_link_token": None}}
        )
        
        if isinstance(user.get('created_at'), str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
        if isinstance(user.get('last_email_sent'), str):
            user['last_email_sent'] = datetime.fromisoformat(user['last_email_sent'])
        
        return {"status": "success", "user_exists": True, "user": user}
    
    # Check pending login
    pending = await db.pending_logins.find_one({"email": request.email, "token": request.token})
    
    if pending:
        # Valid token for new user
        return {"status": "success", "user_exists": False}
    
    raise HTTPException(status_code=401, detail="Invalid or expired token")

@api_router.post("/onboarding")
async def complete_onboarding(request: OnboardingRequest, req: Request):
    """Complete onboarding for new user"""
    # Check if user already exists
    existing = await db.users.find_one({"email": request.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    profile = UserProfile(**request.model_dump())
    doc = profile.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.users.insert_one(doc)
    
    # Save initial version history
    await version_tracker.save_schedule_version(
        user_email=request.email,
        schedule_data=request.schedule.model_dump(),
        changed_by="user",
        change_reason="Initial onboarding"
    )
    
    await version_tracker.save_personality_version(
        user_email=request.email,
        personalities=[p.model_dump() for p in request.personalities],
        rotation_mode=request.rotation_mode,
        changed_by="user"
    )
    
    await version_tracker.save_profile_version(
        user_email=request.email,
        name=request.name,
        goals=request.goals,
        changed_by="user",
        change_details={"event": "onboarding_complete"}
    )
    
    # Track onboarding completion
    ip_address = req.client.host if req.client else None
    await tracker.log_user_activity(
        action_type="onboarding_completed",
        user_email=request.email,
        details={
            "personalities_count": len(request.personalities),
            "schedule_frequency": request.schedule.frequency
        },
        ip_address=ip_address
    )
    
    # Clean up pending login
    await db.pending_logins.delete_one({"email": request.email})
    
    # Schedule emails for this new user
    await schedule_user_emails()
    logger.info(f"✅ Onboarding complete + history saved for: {request.email}")
    
    return {"status": "success", "user": profile}

@api_router.get("/users/{email}")
async def get_user(email: str):
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if isinstance(user.get('created_at'), str):
        user['created_at'] = datetime.fromisoformat(user['created_at'])
    if isinstance(user.get('last_email_sent'), str):
        user['last_email_sent'] = datetime.fromisoformat(user['last_email_sent'])
    
    return user

@api_router.put("/users/{email}")
async def update_user(email: str, updates: UserProfileUpdate):
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    
    if update_data:
        # Save version history BEFORE updating
        if 'schedule' in update_data:
            await version_tracker.save_schedule_version(
                user_email=email,
                schedule_data=update_data['schedule'],
                changed_by="user",
                change_reason="User updated schedule"
            )
        
        if 'personalities' in update_data or 'rotation_mode' in update_data:
            await version_tracker.save_personality_version(
                user_email=email,
                personalities=update_data.get('personalities', user.get('personalities', [])),
                rotation_mode=update_data.get('rotation_mode', user.get('rotation_mode', 'sequential')),
                changed_by="user"
            )
        
        if 'name' in update_data or 'goals' in update_data:
            await version_tracker.save_profile_version(
                user_email=email,
                name=update_data.get('name', user.get('name')),
                goals=update_data.get('goals', user.get('goals')),
                changed_by="user",
                change_details=update_data
            )
        
        # Now update the user
        await db.users.update_one({"email": email}, {"$set": update_data})
        
        # Track activity
        await tracker.log_user_activity(
            action_type="profile_updated",
            user_email=email,
            details={"fields_updated": list(update_data.keys())}
        )
    
    updated_user = await db.users.find_one({"email": email}, {"_id": 0})
    if isinstance(updated_user.get('created_at'), str):
        updated_user['created_at'] = datetime.fromisoformat(updated_user['created_at'])
    if isinstance(updated_user.get('last_email_sent'), str):
        updated_user['last_email_sent'] = datetime.fromisoformat(updated_user['last_email_sent'])
    
    # Reschedule if schedule was updated
    if 'schedule' in update_data or 'active' in update_data:
        await schedule_user_emails()
        logger.info(f"Rescheduled emails for {email}")
    
    return updated_user

@api_router.post("/generate-message")
async def generate_message(request: MessageGenRequest):
    message, _, used_fallback, _ = await generate_unique_motivational_message(
        request.goals, 
        request.personality,
        request.user_name,
        0,
        []
    )
    return MessageGenResponse(message=message, used_fallback=used_fallback)

@api_router.post("/test-schedule/{email}")
async def test_schedule(email: str):
    """Test if email scheduling is working for a user"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    schedule = user.get('schedule', {})
    job_id = f"user_{email.replace('@', '_at_').replace('.', '_')}"
    
    # Check if job exists
    job_exists = False
    next_run = None
    try:
        job = scheduler.get_job(job_id)
        if job:
            job_exists = True
            next_run = job.next_run_time.isoformat() if job.next_run_time else None
    except:
        pass
    
    return {
        "email": email,
        "schedule": schedule,
        "job_exists": job_exists,
        "job_id": job_id,
        "next_run": next_run,
        "active": user.get('active', False),
        "paused": schedule.get('paused', False)
    }

@api_router.post("/send-now/{email}")
async def send_motivation_now(email: str):
    """Send motivation email immediately"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get current personality
    personality = get_current_personality(user)
    if not personality:
        raise HTTPException(status_code=400, detail="No personality configured")
    
    # Calculate streak FIRST (before generating message) to use correct streak in email
    sent_dt = datetime.now(timezone.utc)
    current_streak = user.get('streak_count', 0)
    last_sent = user.get('last_email_sent')
    
    if last_sent:
        if isinstance(last_sent, str):
            try:
                last_sent_dt = datetime.fromisoformat(last_sent.replace('Z', '+00:00'))
            except:
                last_sent_dt = datetime.fromisoformat(last_sent)
        else:
            last_sent_dt = last_sent
            
        last_sent_date = last_sent_dt.date()
        current_date = sent_dt.date()
        days_diff = (current_date - last_sent_date).days
        
        if days_diff == 0:
            streak_count = current_streak if current_streak > 0 else 1
            logger.info(f"Streak calculation (send-now) for {email}: Same day, keeping streak at {streak_count}")
        elif days_diff == 1:
            streak_count = current_streak + 1
            logger.info(f"Streak calculation (send-now) for {email}: Consecutive day, incrementing {current_streak} -> {streak_count}")
        else:
            streak_count = 1
            logger.info(f"Streak calculation (send-now) for {email}: Gap of {days_diff} days, resetting to {streak_count}")
    else:
        streak_count = 1
        logger.info(f"Streak calculation (send-now) for {email}: First email ever, starting at {streak_count}")
    
    # Generate message using the CALCULATED streak
    message, message_type, used_fallback, research_snippet = await generate_unique_motivational_message(
        user['goals'],
        personality,
        user.get('name'),
        streak_count,  # Use calculated streak, not old one
        []
    )
    if used_fallback:
        try:
            await tracker.log_system_event(
                event_type="llm_generation_fallback",
                event_category="llm",
                details={
                    "user_email": email,
                    "personality": personality.value if personality else None
                },
                status="warning"
            )
        except Exception:
            pass
    
    # Save to history
    message_id = str(uuid.uuid4())
    history = MessageHistory(
        id=message_id,
        email=email,
        message=message,
        personality=personality,
        used_fallback=used_fallback,
        sent_at=sent_dt
    ).model_dump()
    history["message_type"] = message_type
    history["created_at"] = history.get("sent_at")
    history["streak_at_time"] = streak_count  # Store the streak at time of sending
    await db.message_history.insert_one(history)
    
    streak_icon, streak_message = resolve_streak_badge(streak_count)
    core_message, check_in_lines, quick_reply_lines = extract_interactive_sections(message)
    ci_defaults, qr_defaults = generate_interactive_defaults(streak_count, user.get('goals', ''))
    check_in_lines = check_in_lines or ci_defaults
    quick_reply_lines = quick_reply_lines or qr_defaults

    html_content = render_email_html(
        streak_count=streak_count,
        streak_icon=streak_icon,
        streak_message=streak_message,
        core_message=core_message,
        check_in_lines=check_in_lines,
        quick_reply_lines=quick_reply_lines,
    )
    
    # Create updated user with new streak for subject line generation
    updated_user = user.copy()
    updated_user['streak_count'] = streak_count
    
    subject_line = await compose_subject_line(
        personality,
        "instant_boost",
        updated_user,  # Use updated user with new streak
        used_fallback,
        research_snippet=research_snippet
    )

    success, error = await send_email(email, subject_line, html_content)
    
    if success:
        await db.users.update_one(
            {"email": email},
            {
                "$set": {
                    "last_email_sent": sent_dt.isoformat(),
                    "last_active": sent_dt.isoformat(),
                    "streak_count": streak_count
                },
                "$inc": {"total_messages_received": 1}
            }
        )
        logger.info(f"✅ Email sent to {email} (send-now) - Streak updated to {streak_count} days")
        await record_email_log(
            email=email,
            subject=subject_line,
            status="success",
            sent_dt=sent_dt,
            timezone_value=user.get("schedule", {}).get("timezone"),
        )
        return {"status": "success", "message": "Email sent successfully", "message_id": message_id}
    else:
        await record_email_log(
            email=email,
            subject=subject_line,
            status="failed",
            sent_dt=sent_dt,
            timezone_value=user.get("schedule", {}).get("timezone"),
            error_message=error,
        )
        raise HTTPException(status_code=500, detail=f"Failed to send email: {error}")

@api_router.get("/famous-personalities")
async def get_famous_personalities():
    return {
        "personalities": [
            "Elon Musk", "Steve Jobs", "A.P.J. Abdul Kalam", "Oprah Winfrey",
            "Nelson Mandela", "Maya Angelou", "Tony Robbins", "Brené Brown",
            "Simon Sinek", "Michelle Obama", "Warren Buffett", "Richard Branson"
        ]
    }

@api_router.get("/tone-options")
async def get_tone_options():
    return {
        "tones": [
            "Funny & Uplifting", "Friendly & Warm", "Roasting (Tough Love)",
            "Serious & Direct", "Philosophical & Deep", "Energetic & Enthusiastic",
            "Calm & Meditative", "Poetic & Artistic"
        ]
    }

# Message History & Feedback Routes
@api_router.get("/users/{email}/message-history")
async def get_message_history(email: str, limit: int = 50):
    """Get user's message history"""
    messages = await db.message_history.find(
        {"email": email}, 
        {"_id": 0}
    ).sort("sent_at", -1).to_list(limit)
    
    # Ensure all datetime objects are timezone-aware (UTC) and convert to ISO format
    for msg in messages:
        sent_at = msg.get('sent_at')
        if sent_at:
            if isinstance(sent_at, str):
                try:
                    dt = datetime.fromisoformat(sent_at.replace('Z', '+00:00'))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    msg['sent_at'] = dt.isoformat()
                except Exception:
                    pass
            elif isinstance(sent_at, datetime):
                # Ensure timezone-aware
                if sent_at.tzinfo is None:
                    sent_at = sent_at.replace(tzinfo=timezone.utc)
                msg['sent_at'] = sent_at.isoformat()
    
    return {"messages": messages, "total": len(messages)}

@api_router.get("/users/{email}/streak-status")
async def get_streak_status(email: str):
    """Get current streak status and last email sent date"""
    try:
        user = await db.users.find_one({"email": email}, {"_id": 0, "streak_count": 1, "last_email_sent": 1, "total_messages_received": 1})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get most recent message
        last_message = await db.message_history.find_one(
            {"email": email},
            {"sent_at": 1, "created_at": 1, "streak_at_time": 1},
            sort=[("sent_at", -1)]
        )
        
        last_message_streak = None
        last_message_date = None
        if last_message:
            last_message_streak = last_message.get("streak_at_time")
            last_message_date = last_message.get("sent_at") or last_message.get("created_at")
            # Convert to ISO string if datetime
            if isinstance(last_message_date, datetime):
                last_message_date = last_message_date.isoformat()
        
        return {
            "current_streak": user.get("streak_count", 0),
            "last_email_sent": user.get("last_email_sent"),
            "total_messages": user.get("total_messages_received", 0),
            "last_message_streak": last_message_streak,
            "last_message_date": last_message_date
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting streak status for {email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving streak status: {str(e)}")

@api_router.post("/users/{email}/recalculate-streak")
async def recalculate_streak_from_history(email: str):
    """Recalculate streak count based on message history (useful for fixing data issues)"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all messages sorted by date (most recent first, then we'll reverse)
    messages = await db.message_history.find(
        {"email": email},
        {"sent_at": 1, "created_at": 1, "streak_at_time": 1}
    ).sort("sent_at", -1).to_list(1000)  # Most recent first
    
    if not messages:
        # No messages - reset streak to 0
        await db.users.update_one(
            {"email": email},
            {"$set": {"streak_count": 0, "last_email_sent": None}}
        )
        return {"streak_count": 0, "message": "No messages found, streak reset to 0"}
    
    # Calculate streak from message history dates (more reliable than streak_at_time)
    # The streak_at_time might be incorrect from previous bugs, so we recalculate from dates
    most_recent = messages[0]
    
    # Check if we should use streak_at_time (only if it seems reasonable)
    # If all messages have streak_at_time=1, it's likely wrong, so recalculate from dates
    use_streak_at_time = False
    if most_recent.get('streak_at_time') is not None:
        # Check if streak_at_time values are consistent and make sense
        # If most recent is 1 but we have messages on different days, recalculate
        recent_streak = most_recent.get('streak_at_time', 0)
        if recent_streak > 1:  # Only trust if it's > 1
            use_streak_at_time = True
    
    if use_streak_at_time:
        # Use the streak_at_time from the most recent message
        streak_count = most_recent.get('streak_at_time', 0)
        logger.info(f"Using streak_at_time from most recent message: {streak_count}")
    else:
        # Calculate streak from message history dates
        # Reverse to process chronologically
        messages_chrono = list(reversed(messages))
        streak_count = 0
        last_date = None
        consecutive_days = 0
        
        for msg in messages_chrono:
            sent_at = msg.get('sent_at') or msg.get('created_at')
            if not sent_at:
                continue
                
            if isinstance(sent_at, str):
                try:
                    msg_date = datetime.fromisoformat(sent_at.replace('Z', '+00:00')).date()
                except:
                    try:
                        # Try alternative format
                        msg_date = datetime.fromisoformat(sent_at).date()
                    except:
                        logger.warning(f"Could not parse date: {sent_at}")
                        continue
            elif isinstance(sent_at, datetime):
                msg_date = sent_at.date()
            else:
                continue
            
            if last_date is None:
                # First message
                last_date = msg_date
                consecutive_days = 1
                streak_count = 1
            else:
                days_diff = (msg_date - last_date).days
                if days_diff == 0:
                    # Same day - don't increment, keep the higher streak if available
                    if msg.get('streak_at_time') and msg.get('streak_at_time') > streak_count:
                        streak_count = msg.get('streak_at_time')
                    continue
                elif days_diff == 1:
                    # Consecutive day
                    consecutive_days += 1
                    streak_count = consecutive_days
                    last_date = msg_date
                else:
                    # Gap - reset
                    consecutive_days = 1
                    streak_count = 1
                    last_date = msg_date
        
        logger.info(f"Calculated streak from dates: {streak_count}")
    
    # Get the most recent message date
    last_message = messages[0]  # Most recent (already sorted)
    last_sent = last_message.get('sent_at') or last_message.get('created_at')
    if isinstance(last_sent, str):
        try:
            last_sent_dt = datetime.fromisoformat(last_sent.replace('Z', '+00:00'))
        except:
            try:
                last_sent_dt = datetime.fromisoformat(last_sent)
            except:
                last_sent_dt = None
    elif isinstance(last_sent, datetime):
        last_sent_dt = last_sent
    else:
        last_sent_dt = None
    
    # Update user with recalculated streak
    update_data = {"streak_count": streak_count}
    if last_sent_dt:
        update_data["last_email_sent"] = last_sent_dt.isoformat()
    
    await db.users.update_one(
        {"email": email},
        {"$set": update_data}
    )
    
    logger.info(f"✅ Recalculated streak for {email}: {streak_count} days (from {len(messages)} messages)")
    
    return {
        "streak_count": streak_count,
        "total_messages": len(messages),
        "last_email_sent": last_sent_dt.isoformat() if last_sent_dt else None,
        "message": f"Streak recalculated from message history",
        "method": "streak_at_time" if use_streak_at_time else "date_calculation"
    }

@api_router.post("/users/{email}/feedback")
async def submit_feedback(email: str, feedback: MessageFeedbackCreate):
    """Submit feedback for a message"""
    import json
    
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    message_personality = None
    if feedback.message_id:
        message_doc = await db.message_history.find_one(
            {"id": feedback.message_id},
            {"personality": 1},
        )
        if message_doc and message_doc.get("personality"):
            try:
                message_personality = PersonalityType(**message_doc["personality"])
            except Exception:
                message_personality = None

    personality = feedback.personality or message_personality or get_current_personality(user)
    
    feedback_doc = MessageFeedback(
        email=email,
        message_id=feedback.message_id,
        personality=personality,
        rating=feedback.rating,
        feedback_text=feedback.feedback_text
    )
    
    feedback_dict = feedback_doc.model_dump()
    await db.message_feedback.insert_one(feedback_dict)
    
    # Update message history with rating
    if feedback.message_id:
        update_fields = {"rating": feedback.rating}
        if feedback.feedback_text:
            update_fields["feedback_text"] = feedback.feedback_text
        await db.message_history.update_one(
            {"id": feedback.message_id},
            {"$set": update_fields}
        )
    
    # Update last active
    await db.users.update_one(
        {"email": email},
        {"$set": {"last_active": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Prepare response
    response_data = {
        "status": "success",
        "message": "Feedback submitted",
        "feedback_id": feedback_dict.get("id"),
        "rating": feedback.rating,
        "has_feedback_text": bool(feedback.feedback_text)
    }
    
    # Log activity with full JSON response
    try:
        raw_response_json = json.dumps(response_data, default=str, indent=2)
        await tracker.log_user_activity(
            action_type="feedback_submitted",
            user_email=email,
            details={
                "message_id": feedback.message_id,
                "rating": feedback.rating,
                "personality": personality.model_dump() if personality else None,
                "has_feedback_text": bool(feedback.feedback_text),
                "feedback_text_length": len(feedback.feedback_text) if feedback.feedback_text else 0,
                "raw_response": raw_response_json
            }
        )
        
        # Also log as system event with full JSON
        await tracker.log_system_event(
            event_type="feedback_received",
            event_category="user_feedback",
            details={
                "user_email": email,
                "message_id": feedback.message_id,
                "rating": feedback.rating,
                "personality": personality.model_dump() if personality else None,
                "feedback_text": feedback.feedback_text,
                "raw_feedback_json": json.dumps(feedback_dict, default=str, indent=2),
                "raw_response_json": raw_response_json
            },
            status="success"
        )
    except Exception as e:
        logger.warning(f"Failed to log feedback activity: {str(e)}")
    
    return response_data

@api_router.get("/users/{email}/analytics")
async def get_user_analytics(email: str):
    """Get user analytics"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get feedback stats
    feedbacks = await db.message_feedback.find({"email": email}).to_list(1000)
    
    # Calculate average rating
    ratings = [f['rating'] for f in feedbacks if 'rating' in f]
    avg_rating = sum(ratings) / len(ratings) if ratings else None
    
    # Find favorite personality
    personality_counts = {}
    personality_ratings = {}
    
    for feedback in feedbacks:
        pers_value = feedback.get('personality', {}).get('value', 'Unknown')
        rating = feedback.get('rating', 0)
        
        if pers_value not in personality_counts:
            personality_counts[pers_value] = 0
            personality_ratings[pers_value] = []
        
        personality_counts[pers_value] += 1
        personality_ratings[pers_value].append(rating)
    
    # Calculate avg rating per personality
    personality_stats = {}
    for pers, ratings in personality_ratings.items():
        personality_stats[pers] = {
            "count": personality_counts[pers],
            "avg_rating": sum(ratings) / len(ratings) if ratings else 0
        }
    
    # Find favorite (highest avg rating)
    favorite_personality = None
    highest_rating = 0
    for pers, stats in personality_stats.items():
        if stats['avg_rating'] > highest_rating:
            highest_rating = stats['avg_rating']
            favorite_personality = pers
    
    # Calculate engagement rate
    total_messages = user.get('total_messages_received', 0)
    total_feedback = len(feedbacks)
    engagement_rate = (total_feedback / total_messages * 100) if total_messages > 0 else 0
    
    # Check for new achievements
    unlocked = await check_and_unlock_achievements(email, user, total_feedback)
    
    # Get user achievements
    user_achievements = user.get("achievements", [])
    achievements_dict = await get_achievements_from_db()
    achievements_list = []
    for ach_id in user_achievements:
        if ach_id in achievements_dict:
            achievements_list.append({
                **achievements_dict[ach_id],
                "unlocked": True
            })
    
    analytics = UserAnalytics(
        email=email,
        streak_count=user.get('streak_count', 0),
        total_messages=total_messages,
        favorite_personality=favorite_personality,
        avg_rating=round(avg_rating, 2) if avg_rating else None,
        last_active=user.get('last_active'),
        engagement_rate=round(engagement_rate, 2),
        personality_stats=personality_stats
    )
    
    # Convert to dict and add achievements
    result = analytics.model_dump()
    result["achievements"] = achievements_list
    result["new_achievements"] = unlocked
    
    return result

# Personality Management Routes
@api_router.post("/users/{email}/personalities")
async def add_personality(email: str, personality: PersonalityType):
    """Add a new personality to user"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    personalities = user.get('personalities', [])
    personalities.append(personality.model_dump())
    
    await db.users.update_one(
        {"email": email},
        {"$set": {"personalities": personalities}}
    )
    
    return {"status": "success", "message": "Personality added"}

@api_router.delete("/users/{email}/personalities/{personality_id}")
async def remove_personality(email: str, personality_id: str):
    """Remove a personality from user"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    personalities = user.get('personalities', [])
    personalities = [p for p in personalities if p.get('id') != personality_id]
    
    if not personalities:
        raise HTTPException(status_code=400, detail="Cannot remove last personality")
    
    await db.users.update_one(
        {"email": email},
        {"$set": {"personalities": personalities}}
    )
    
    return {"status": "success", "message": "Personality removed"}

# ============================================================================
# FEATURE 1: GAMIFICATION & ACHIEVEMENTS
# ============================================================================

@api_router.get("/users/{email}/achievements")
async def get_user_achievements(email: str):
    """Get all achievements for a user"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_achievements = user.get("achievements", [])
    achievements_dict = await get_achievements_from_db()
    unlocked = []
    locked = []
    
    for ach_id, achievement in achievements_dict.items():
        ach_data = {**achievement, "unlocked": ach_id in user_achievements}
        if ach_id in user_achievements:
            unlocked.append(ach_data)
        else:
            locked.append(ach_data)
    
    return {
        "unlocked": unlocked,
        "locked": locked,
        "total_unlocked": len(unlocked),
        "total_available": len(achievements_dict)
    }

# ============================================================================
# FEATURE 3: MESSAGE ENHANCEMENTS (Favorites, Collections)
# ============================================================================

@api_router.post("/users/{email}/messages/{message_id}/favorite")
async def toggle_message_favorite(email: str, message_id: str):
    """Toggle favorite status for a message"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify message exists
    message = await db.message_history.find_one({"id": message_id, "email": email})
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    favorites = user.get("favorite_messages", [])
    is_favorite = message_id in favorites
    
    if is_favorite:
        favorites.remove(message_id)
        action = "removed"
    else:
        favorites.append(message_id)
        action = "added"
    
    await db.users.update_one(
        {"email": email},
        {"$set": {"favorite_messages": favorites}}
    )
    
    await tracker.log_user_activity(
        email=email,
        action_type="message_favorite_toggled",
        action_category="user_action",
        details={"message_id": message_id, "action": action}
    )
    
    return {"status": "success", "is_favorite": not is_favorite, "action": action}

@api_router.get("/users/{email}/messages/favorites")
async def get_favorite_messages(email: str):
    """Get all favorite messages"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    favorites = user.get("favorite_messages", [])
    messages = await db.message_history.find(
        {"id": {"$in": favorites}, "email": email},
        {"_id": 0}
    ).sort("sent_at", -1).to_list(100)
    
    return {"messages": messages, "count": len(messages)}

@api_router.post("/users/{email}/collections")
async def create_collection(email: str, collection: dict):
    """Create a new message collection"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    collections = user.get("message_collections", {})
    collection_id = str(uuid.uuid4())
    collection_name = collection.get("name", "Untitled Collection")
    
    collections[collection_id] = {
        "id": collection_id,
        "name": collection_name,
        "description": collection.get("description", ""),
        "message_ids": collection.get("message_ids", []),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.update_one(
        {"email": email},
        {"$set": {"message_collections": collections}}
    )
    
    return {"status": "success", "collection_id": collection_id, "collection": collections[collection_id]}

@api_router.get("/users/{email}/collections")
async def get_collections(email: str):
    """Get all message collections"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    collections = user.get("message_collections", {})
    return {"collections": list(collections.values())}

@api_router.put("/users/{email}/collections/{collection_id}")
async def update_collection(email: str, collection_id: str, collection: dict):
    """Update a message collection"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    collections = user.get("message_collections", {})
    if collection_id not in collections:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    if "name" in collection:
        collections[collection_id]["name"] = collection["name"]
    if "description" in collection:
        collections[collection_id]["description"] = collection["description"]
    if "message_ids" in collection:
        collections[collection_id]["message_ids"] = collection["message_ids"]
    
    await db.users.update_one(
        {"email": email},
        {"$set": {"message_collections": collections}}
    )
    
    return {"status": "success", "collection": collections[collection_id]}

@api_router.delete("/users/{email}/collections/{collection_id}")
async def delete_collection(email: str, collection_id: str):
    """Delete a message collection"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    collections = user.get("message_collections", {})
    if collection_id not in collections:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    del collections[collection_id]
    
    await db.users.update_one(
        {"email": email},
        {"$set": {"message_collections": collections}}
    )
    
    return {"status": "success", "message": "Collection deleted"}

# ============================================================================
# FEATURE 2: GOAL PROGRESS TRACKING
# ============================================================================

@api_router.post("/users/{email}/goals/progress")
async def update_goal_progress(email: str, goal_data: dict):
    """Update or create goal progress"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    goal_progress = user.get("goal_progress", {})
    goal_id = goal_data.get("goal_id") or str(uuid.uuid4())
    
    goal_progress[goal_id] = {
        "goal_id": goal_id,
        "goal_text": goal_data.get("goal_text", ""),
        "target_date": goal_data.get("target_date"),
        "progress_percentage": goal_data.get("progress_percentage", 0.0),
        "milestones": goal_data.get("milestones", []),
        "completed": goal_data.get("completed", False),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Check if goal completed (for achievement)
    if goal_data.get("completed") and not goal_progress[goal_id].get("was_completed", False):
        await check_and_unlock_achievements(email, user, 0)
        goal_progress[goal_id]["was_completed"] = True
    
    await db.users.update_one(
        {"email": email},
        {"$set": {"goal_progress": goal_progress}}
    )
    
    return {"status": "success", "goal": goal_progress[goal_id]}

@api_router.get("/users/{email}/goals/progress")
async def get_goal_progress(email: str):
    """Get all goal progress"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    goal_progress = user.get("goal_progress", {})
    return {"goals": list(goal_progress.values())}

# ============================================================================
# FEATURE 4: EXPORT & SHARING
# ============================================================================

@api_router.get("/users/{email}/export/messages")
async def export_messages(email: str, format: str = "json"):
    """Export messages in various formats"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    messages = await db.message_history.find(
        {"email": email},
        {"_id": 0}
    ).sort("sent_at", -1).to_list(1000)
    
    if format == "json":
        return {"messages": messages, "count": len(messages)}
    elif format == "csv":
        import csv
        import io
        output = io.StringIO()
        if messages:
            writer = csv.DictWriter(output, fieldnames=["id", "email", "message", "subject", "sent_at", "personality"])
            writer.writeheader()
            for msg in messages:
                writer.writerow({
                    "id": msg.get("id", ""),
                    "email": msg.get("email", ""),
                    "message": msg.get("message", "").replace("\n", " "),
                    "subject": msg.get("subject", ""),
                    "sent_at": msg.get("sent_at", ""),
                    "personality": msg.get("personality", {}).get("value", "") if msg.get("personality") else ""
                })
        return {"content": output.getvalue(), "format": "csv"}
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use 'json' or 'csv'")

# ============================================================================
# FEATURE 7: CONTENT PERSONALIZATION
# ============================================================================

@api_router.put("/users/{email}/preferences")
async def update_content_preferences(email: str, preferences: dict):
    """Update user content preferences"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    content_prefs = user.get("content_preferences", {})
    content_prefs.update(preferences)
    
    await db.users.update_one(
        {"email": email},
        {"$set": {"content_preferences": content_prefs}}
    )
    
    return {"status": "success", "preferences": content_prefs}

@api_router.get("/users/{email}/preferences")
async def get_content_preferences(email: str):
    """Get user content preferences"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"preferences": user.get("content_preferences", {})}

# ============================================================================
# FEATURE 5: ADVANCED ANALYTICS (Weekly/Monthly Reports)
# ============================================================================

@api_router.get("/users/{email}/analytics/weekly")
async def get_weekly_analytics(email: str, weeks: int = 4):
    """Get weekly analytics report"""
    from datetime import timedelta
    
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(weeks=weeks)
    
    messages = await db.message_history.find({
        "email": email,
        "sent_at": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}
    }).to_list(1000)
    
    feedbacks = await db.message_feedback.find({
        "email": email,
        "created_at": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}
    }).to_list(1000)
    
    return {
        "period": f"{weeks} weeks",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_messages": len(messages),
        "total_feedback": len(feedbacks),
        "avg_rating": sum(f['rating'] for f in feedbacks) / len(feedbacks) if feedbacks else None,
        "streak_count": user.get("streak_count", 0)
    }

@api_router.get("/users/{email}/analytics/monthly")
async def get_monthly_analytics(email: str, months: int = 6):
    """Get monthly analytics report"""
    from datetime import timedelta
    
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=months * 30)
    
    messages = await db.message_history.find({
        "email": email,
        "sent_at": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}
    }).to_list(1000)
    
    return {
        "period": f"{months} months",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_messages": len(messages),
        "streak_count": user.get("streak_count", 0)
    }

# ============================================================================
# FEATURE 6: ENGAGEMENT FEATURES (Daily Check-ins, Reflection Journal)
# ============================================================================

@api_router.post("/users/{email}/check-ins")
async def create_check_in(email: str, check_in: dict):
    """Create a daily check-in"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    check_in_id = str(uuid.uuid4())
    check_in_data = {
        "id": check_in_id,
        "email": email,
        "date": check_in.get("date", datetime.now(timezone.utc).isoformat()),
        "mood": check_in.get("mood"),
        "energy_level": check_in.get("energy_level"),
        "reflection": check_in.get("reflection", ""),
        "gratitude": check_in.get("gratitude", []),
        "goals_today": check_in.get("goals_today", []),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.check_ins.insert_one(check_in_data)
    
    return {"status": "success", "check_in": check_in_data}

@api_router.get("/users/{email}/check-ins")
async def get_check_ins(email: str, limit: int = 30):
    """Get user check-ins"""
    check_ins = await db.check_ins.find(
        {"email": email},
        {"_id": 0}
    ).sort("date", -1).to_list(limit)
    
    return {"check_ins": check_ins, "count": len(check_ins)}

@api_router.post("/users/{email}/reflections")
async def create_reflection(email: str, reflection: dict):
    """Create a reflection entry"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    reflection_id = str(uuid.uuid4())
    reflection_data = {
        "id": reflection_id,
        "email": email,
        "message_id": reflection.get("message_id"),
        "content": reflection.get("content", ""),
        "tags": reflection.get("tags", []),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.reflections.insert_one(reflection_data)
    
    return {"status": "success", "reflection": reflection_data}

@api_router.get("/users/{email}/reflections")
async def get_reflections(email: str, limit: int = 50):
    """Get user reflections"""
    reflections = await db.reflections.find(
        {"email": email},
        {"_id": 0}
    ).sort("created_at", -1).to_list(limit)
    
    return {"reflections": reflections, "count": len(reflections)}

# ============================================================================
# FEATURE 9: SOCIAL FEATURES (Anonymous Insights, Community Stats)
# ============================================================================

@api_router.get("/community/stats")
async def get_community_stats():
    """Get anonymous community statistics"""
    total_users = await db.users.count_documents({"active": True})
    total_messages = await db.message_history.count_documents({})
    total_feedback = await db.message_feedback.count_documents({})
    
    # Get average streak
    users = await db.users.find({"active": True}, {"streak_count": 1}).to_list(1000)
    avg_streak = sum(u.get("streak_count", 0) for u in users) / len(users) if users else 0
    
    # Get most popular personalities
    feedbacks = await db.message_feedback.find({}).to_list(1000)
    personality_counts = {}
    for fb in feedbacks:
        pers = fb.get("personality", {}).get("value", "Unknown")
        personality_counts[pers] = personality_counts.get(pers, 0) + 1
    
    popular_personalities = sorted(personality_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_active_users": total_users,
        "total_messages_sent": total_messages,
        "total_feedback_given": total_feedback,
        "average_streak": round(avg_streak, 1),
        "popular_personalities": [{"name": name, "count": count} for name, count in popular_personalities]
    }

@api_router.get("/community/message-insights/{message_id}")
async def get_message_insights(message_id: str):
    """Get anonymous insights for a specific message"""
    feedbacks = await db.message_feedback.find({"message_id": message_id}).to_list(100)
    
    if not feedbacks:
        return {"message": "No feedback available for this message"}
    
    ratings = [f.get("rating", 0) for f in feedbacks]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    return {
        "total_ratings": len(feedbacks),
        "average_rating": round(avg_rating, 1),
        "rating_distribution": {
            "5": sum(1 for r in ratings if r == 5),
            "4": sum(1 for r in ratings if r == 4),
            "3": sum(1 for r in ratings if r == 3),
            "2": sum(1 for r in ratings if r == 2),
            "1": sum(1 for r in ratings if r == 1)
        }
    }

# ============================================================================
# FEATURE 10: ADMIN ENHANCEMENTS (A/B Testing, Content Performance)
# ============================================================================

@api_router.get("/admin/content-performance", dependencies=[Depends(verify_admin)])
async def get_content_performance(admin_token: str):
    """Get content performance analytics"""
    messages = await db.message_history.find({}).to_list(1000)
    feedbacks = await db.message_feedback.find({}).to_list(1000)
    
    # Group by personality
    personality_performance = {}
    for msg in messages:
        pers = msg.get("personality", {}).get("value", "Unknown") if msg.get("personality") else "Unknown"
        if pers not in personality_performance:
            personality_performance[pers] = {"total": 0, "ratings": []}
        personality_performance[pers]["total"] += 1
    
    # Add ratings
    for fb in feedbacks:
        pers = fb.get("personality", {}).get("value", "Unknown") if fb.get("personality") else "Unknown"
        if pers in personality_performance:
            personality_performance[pers]["ratings"].append(fb.get("rating", 0))
    
    # Calculate averages
    for pers in personality_performance:
        ratings = personality_performance[pers]["ratings"]
        personality_performance[pers]["avg_rating"] = sum(ratings) / len(ratings) if ratings else 0
        personality_performance[pers]["feedback_count"] = len(ratings)
    
    return {"personality_performance": personality_performance}

@api_router.get("/admin/user-journey/{email}", dependencies=[Depends(verify_admin)])
async def get_user_journey(email: str, admin_token: str):
    """Get user journey mapping"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all activities
    activities = await db.activity_logs.find(
        {"user_email": email},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(1000)
    
    # Get messages
    messages = await db.message_history.find(
        {"email": email},
        {"_id": 0}
    ).sort("sent_at", 1).to_list(1000)
    
    # Get feedback
    feedbacks = await db.message_feedback.find(
        {"email": email},
        {"_id": 0}
    ).sort("created_at", 1).to_list(1000)
    
    return {
        "user": {
            "email": email,
            "created_at": user.get("created_at"),
            "last_active": user.get("last_active"),
            "streak_count": user.get("streak_count", 0),
            "total_messages": user.get("total_messages_received", 0)
        },
        "timeline": {
            "activities": activities,
            "messages": messages,
            "feedbacks": feedbacks
        }
    }
    
    personalities = user.get('personalities', [])
    for i, p in enumerate(personalities):
        if p.get('id') == personality_id:
            personalities[i].update(updates)
            break
    
    await db.users.update_one(
        {"email": email},
        {"$set": {"personalities": personalities}}
    )
    
    return {"status": "success", "message": "Personality updated"}

# Schedule Management Routes
@api_router.post("/users/{email}/schedule/pause")
async def pause_schedule(email: str):
    """Pause user's email schedule"""
    await db.users.update_one(
        {"email": email},
        {"$set": {"schedule.paused": True}}
    )
    return {"status": "success", "message": "Schedule paused"}

@api_router.post("/users/{email}/schedule/resume")
async def resume_schedule(email: str):
    """Resume user's email schedule"""
    await db.users.update_one(
        {"email": email},
        {"$set": {"schedule.paused": False}}
    )
    return {"status": "success", "message": "Schedule resumed"}

@api_router.post("/users/{email}/schedule/skip-next")
async def skip_next_email(email: str):
    """Skip the next scheduled email"""
    await db.users.update_one(
        {"email": email},
        {"$set": {"schedule.skip_next": True}}
    )
    return {"status": "success", "message": "Next email will be skipped"}

# Admin Routes
@api_router.get("/admin/users", dependencies=[Depends(verify_admin)])
async def admin_get_all_users():
    users = await db.users.find({}, {"_id": 0}).to_list(1000)
    for user in users:
        if isinstance(user.get('created_at'), str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
        if isinstance(user.get('last_email_sent'), str):
            user['last_email_sent'] = datetime.fromisoformat(user['last_email_sent'])
    return {"users": users, "total": len(users)}

@api_router.get("/admin/email-logs", dependencies=[Depends(verify_admin)])
async def admin_get_email_logs(limit: int = 100):
    logs = await db.email_logs.find({}, {"_id": 0}).sort("sent_at", -1).to_list(limit)
    for log in logs:
        sent_at = log.get('sent_at')
        if isinstance(sent_at, datetime):
            log['sent_at'] = sent_at.isoformat()
        elif isinstance(sent_at, str):
            # ensure ISO formatting
            try:
                log['sent_at'] = datetime.fromisoformat(sent_at).isoformat()
            except Exception:
                pass
    return {"logs": logs}

@api_router.get("/admin/stats", dependencies=[Depends(verify_admin)])
async def admin_get_stats():
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"active": True})
    total_emails = await db.email_logs.count_documents({})
    failed_emails = await db.email_logs.count_documents({"status": "failed"})
    total_messages = await db.message_history.count_documents({})
    total_feedback = await db.message_feedback.count_documents({})
    
    # Calculate average streak
    users = await db.users.find({}, {"streak_count": 1, "_id": 0}).to_list(1000)
    streaks = [u.get('streak_count', 0) for u in users]
    avg_streak = sum(streaks) / len(streaks) if streaks else 0
    
    # Get feedback ratings
    feedbacks = await db.message_feedback.find({}, {"rating": 1, "_id": 0}).to_list(10000)
    ratings = [f.get('rating', 0) for f in feedbacks]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "total_emails_sent": total_emails,
        "failed_emails": failed_emails,
        "success_rate": round((total_emails - failed_emails) / total_emails * 100, 2) if total_emails > 0 else 0,
        "total_messages": total_messages,
        "total_feedback": total_feedback,
        "avg_streak": round(avg_streak, 1),
        "avg_rating": round(avg_rating, 2),
        "engagement_rate": round((total_feedback / total_messages * 100), 2) if total_messages > 0 else 0
    }

@api_router.get("/admin/feedback", dependencies=[Depends(verify_admin)])
async def admin_get_feedback(limit: int = 100):
    """Get all feedback with full details including feedback_text"""
    feedbacks = await db.message_feedback.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    for fb in feedbacks:
        if isinstance(fb.get('created_at'), str):
            try:
                fb['created_at'] = datetime.fromisoformat(fb['created_at'])
            except Exception:
                pass
        # Ensure feedback_text is always present (even if None)
        if 'feedback_text' not in fb:
            fb['feedback_text'] = None
    return {"feedbacks": feedbacks}

@api_router.put("/admin/users/{email}", dependencies=[Depends(verify_admin)])
async def admin_update_user(email: str, updates: dict):
    """Admin update any user field"""
    await db.users.update_one(
        {"email": email},
        {"$set": updates}
    )
    updated_user = await db.users.find_one({"email": email}, {"_id": 0})
    
    # Track admin update
    await tracker.log_admin_activity(
        action_type="user_updated",
        admin_email="admin",
        details={"target_user": email, "updates": updates}
    )
    
    return {"status": "success", "user": updated_user}

@api_router.get("/admin/users/{email}/details", dependencies=[Depends(verify_admin)])
async def admin_get_user_details(email: str):
    """Get complete user details including all history and analytics"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's message history
    messages = await db.message_history.find(
        {"email": email}, {"_id": 0}
    ).sort("sent_at", -1).limit(100).to_list(100)
    
    # Get user's feedback
    feedbacks = await db.message_feedback.find(
        {"email": email}, {"_id": 0}
    ).sort("created_at", -1).limit(100).to_list(100)
    
    # Get user's email logs
    email_logs = await db.email_logs.find(
        {"email": email}, {"_id": 0}
    ).sort("sent_at", -1).limit(100).to_list(100)
    
    # Get user's activity timeline
    activities = await db.activity_logs.find(
        {"user_email": email}, {"_id": 0}
    ).sort("timestamp", -1).limit(200).to_list(200)
    
    # Get user analytics
    analytics = await get_user_analytics(email)
    
    # Get complete history
    complete_history = await version_tracker.get_all_user_history(email)
    
    return {
        "user": user,
        "messages": messages,
        "feedbacks": feedbacks,
        "email_logs": email_logs,
        "activities": activities,
        "analytics": analytics,
        "history": complete_history
    }

@api_router.get("/admin/email-logs/advanced", dependencies=[Depends(verify_admin)])
async def admin_get_email_logs_advanced(
    limit: int = 100,
    status: Optional[str] = None,
    email: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Advanced email logs with filtering"""
    query = {}
    if status:
        query["status"] = status
    if email:
        query["email"] = email
    
    if start_date or end_date:
        query["sent_at"] = {}
        if start_date:
            query["sent_at"]["$gte"] = datetime.fromisoformat(start_date)
        if end_date:
            query["sent_at"]["$lte"] = datetime.fromisoformat(end_date)
    
    logs = await db.email_logs.find(query, {"_id": 0}).sort("sent_at", -1).limit(limit).to_list(limit)
    for log in logs:
        sent_at = log.get('sent_at')
        if isinstance(sent_at, datetime):
            log['sent_at'] = sent_at.isoformat()
        elif isinstance(sent_at, str):
            try:
                log['sent_at'] = datetime.fromisoformat(sent_at).isoformat()
            except Exception:
                pass
    return {"logs": logs, "total": len(logs)}

@api_router.get("/admin/errors", dependencies=[Depends(verify_admin)])
async def admin_get_errors(limit: int = 100):
    """Get all error logs from system events and API analytics"""
    # Get system errors
    system_errors = await db.system_events.find(
        {"status": {"$ne": "success"}}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    # Get API errors
    api_errors = await db.api_analytics.find(
        {"status_code": {"$gte": 400}}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    # Get email failures
    email_errors = await db.email_logs.find(
        {"status": "failed"}, {"_id": 0}
    ).sort("sent_at", -1).limit(limit).to_list(limit)
    
    return {
        "system_errors": system_errors,
        "api_errors": api_errors,
        "email_errors": email_errors,
        "total": len(system_errors) + len(api_errors) + len(email_errors)
    }

@api_router.post("/admin/users/bulk-update", dependencies=[Depends(verify_admin)])
async def admin_bulk_update_users(emails: list, updates: dict):
    """Bulk update multiple users"""
    result = await db.users.update_many(
        {"email": {"$in": emails}},
        {"$set": updates}
    )
    
    await tracker.log_admin_activity(
        action_type="bulk_user_update",
        admin_email="admin",
        details={"target_users": emails, "updates": updates, "modified_count": result.modified_count}
    )
    
    return {
        "status": "success",
        "modified_count": result.modified_count,
        "matched_count": result.matched_count
    }

@api_router.delete("/admin/users/{email}", dependencies=[Depends(verify_admin)])
async def admin_delete_user(email: str, soft_delete: bool = True):
    """Delete a user (soft delete by default)"""
    if soft_delete:
        await db.users.update_one(
            {"email": email},
            {"$set": {"active": False, "deleted_at": datetime.now(timezone.utc)}}
        )
        await tracker.log_admin_activity(
            action_type="user_deleted",
            admin_email="admin",
            details={"target_user": email, "soft_delete": True}
        )
        return {"status": "soft_deleted", "email": email}
    else:
        # Hard delete - remove all related data
        await db.users.delete_one({"email": email})
        await db.message_history.delete_many({"email": email})
        await db.message_feedback.delete_many({"email": email})
        await db.email_logs.delete_many({"email": email})
        await tracker.log_admin_activity(
            action_type="user_hard_deleted",
            admin_email="admin",
            details={"target_user": email}
        )
        return {"status": "hard_deleted", "email": email}

@api_router.get("/admin/scheduler/jobs", dependencies=[Depends(verify_admin)])
async def admin_get_scheduler_jobs():
    """Get all scheduled jobs"""
    jobs = scheduler.get_jobs()
    job_list = []
    for job in jobs:
        job_list.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "func": job.func.__name__ if hasattr(job.func, '__name__') else str(job.func),
            "trigger": str(job.trigger) if job.trigger else None
        })
    return {"jobs": job_list, "total": len(job_list)}

@api_router.post("/admin/scheduler/jobs/{job_id}/trigger", dependencies=[Depends(verify_admin)])
async def admin_trigger_job(job_id: str):
    """Manually trigger a scheduled job"""
    try:
        job = scheduler.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        job.modify(next_run_time=datetime.now(timezone.utc))
        await tracker.log_admin_activity(
            action_type="job_triggered",
            admin_email="admin",
            details={"job_id": job_id}
        )
        return {"status": "triggered", "job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/admin/database/health", dependencies=[Depends(verify_admin)])
async def admin_get_database_health():
    """Get database health and collection statistics"""
    collections = {
        "users": await db.users.count_documents({}),
        "message_history": await db.message_history.count_documents({}),
        "message_feedback": await db.message_feedback.count_documents({}),
        "email_logs": await db.email_logs.count_documents({}),
        "activity_logs": await db.activity_logs.count_documents({}),
        "system_events": await db.system_events.count_documents({}),
        "api_analytics": await db.api_analytics.count_documents({}),
        "page_views": await db.page_views.count_documents({}),
        "user_sessions": await db.user_sessions.count_documents({}),
    }
    
    # Get recent activity counts
    from datetime import timedelta
    last_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_activity = {
        "messages_24h": await db.message_history.count_documents({"sent_at": {"$gte": last_24h}}),
        "emails_24h": await db.email_logs.count_documents({"sent_at": {"$gte": last_24h}}),
        "activities_24h": await db.activity_logs.count_documents({"timestamp": {"$gte": last_24h}}),
        "errors_24h": await db.email_logs.count_documents({"status": "failed", "sent_at": {"$gte": last_24h}}),
    }
    
    return {
        "collections": collections,
        "recent_activity": recent_activity,
        "total_documents": sum(collections.values())
    }

class BroadcastRequest(BaseModel):
    message: str
    subject: Optional[str] = None

@api_router.post("/admin/broadcast", dependencies=[Depends(verify_admin)])
async def admin_broadcast_message(request: BroadcastRequest):
    """Send a message to all active users"""
    message = request.message
    subject = request.subject
    active_users = await db.users.find({"active": True}, {"email": 1, "_id": 0}).to_list(1000)
    emails = [u["email"] for u in active_users]
    
    success_count = 0
    failed_count = 0
    broadcast_subject = subject or "Important Update from InboxInspire"
    
    for email in emails:
        try:
            success, error = await send_email(
                to_email=email,
                subject=broadcast_subject,
                html_content=message
            )
            if success:
                success_count += 1
                await record_email_log(
                    email=email,
                    subject=broadcast_subject,
                    status="success",
                    sent_dt=datetime.now(timezone.utc)
                )
            else:
                failed_count += 1
                await record_email_log(
                    email=email,
                    subject=broadcast_subject,
                    status="failed",
                    sent_dt=datetime.now(timezone.utc),
                    error_message=error
                )
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send broadcast to {email}: {str(e)}")
    
    await tracker.log_admin_activity(
        action_type="broadcast_sent",
        admin_email="admin",
        details={"total_users": len(emails), "success": success_count, "failed": failed_count}
    )
    
    return {
        "status": "completed",
        "total_users": len(emails),
        "success": success_count,
        "failed": failed_count
    }

@api_router.get("/admin/analytics/trends", dependencies=[Depends(verify_admin)])
async def admin_get_analytics_trends(days: int = 30):
    """Get analytics trends over time"""
    from datetime import timedelta
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Daily user registrations
    pipeline_users = [
        {"$match": {"created_at": {"$gte": start_date, "$lte": end_date}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    user_trends = await db.users.aggregate(pipeline_users).to_list(100)
    
    # Daily emails sent
    pipeline_emails = [
        {"$match": {"sent_at": {"$gte": start_date, "$lte": end_date}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$sent_at"}},
            "count": {"$sum": 1},
            "success": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
            "failed": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}}
        }},
        {"$sort": {"_id": 1}}
    ]
    email_trends = await db.email_logs.aggregate(pipeline_emails).to_list(100)
    
    # Daily feedback
    pipeline_feedback = [
        {"$match": {"created_at": {"$gte": start_date, "$lte": end_date}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
            "count": {"$sum": 1},
            "avg_rating": {"$avg": "$rating"}
        }},
        {"$sort": {"_id": 1}}
    ]
    feedback_trends = await db.message_feedback.aggregate(pipeline_feedback).to_list(100)
    
    return {
        "user_trends": user_trends,
        "email_trends": email_trends,
        "feedback_trends": feedback_trends,
        "period_days": days
    }

@api_router.get("/admin/search", dependencies=[Depends(verify_admin)])
async def admin_global_search(query: str, limit: int = 50):
    """Global search across all collections"""
    results = {
        "users": [],
        "messages": [],
        "feedback": [],
        "logs": []
    }
    
    # Search users
    users = await db.users.find({
        "$or": [
            {"email": {"$regex": query, "$options": "i"}},
            {"name": {"$regex": query, "$options": "i"}},
            {"goals": {"$regex": query, "$options": "i"}}
        ]
    }, {"_id": 0}).limit(limit).to_list(limit)
    results["users"] = users
    
    # Search messages
    messages = await db.message_history.find({
        "$or": [
            {"email": {"$regex": query, "$options": "i"}},
            {"message": {"$regex": query, "$options": "i"}},
            {"subject": {"$regex": query, "$options": "i"}}
        ]
    }, {"_id": 0}).limit(limit).to_list(limit)
    results["messages"] = messages
    
    # Search feedback
    feedbacks = await db.message_feedback.find({
        "$or": [
            {"email": {"$regex": query, "$options": "i"}},
            {"feedback_text": {"$regex": query, "$options": "i"}}
        ]
    }, {"_id": 0}).limit(limit).to_list(limit)
    results["feedback"] = feedbacks
    
    # Search email logs
    logs = await db.email_logs.find({
        "$or": [
            {"email": {"$regex": query, "$options": "i"}},
            {"subject": {"$regex": query, "$options": "i"}},
            {"error_message": {"$regex": query, "$options": "i"}}
        ]
    }, {"_id": 0}).limit(limit).to_list(limit)
    results["logs"] = logs
    
    total_results = len(results["users"]) + len(results["messages"]) + len(results["feedback"]) + len(results["logs"])
    
    return {
        "query": query,
        "results": results,
        "total": total_results
    }

@api_router.get("/admin/message-history", dependencies=[Depends(verify_admin)])
async def admin_get_all_message_history(
    limit: int = 200,
    email: Optional[str] = None,
    personality: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get all message history across all users with filtering"""
    query = {}
    
    if email:
        query["email"] = email
    if personality:
        query["personality.value"] = personality
    
    if start_date or end_date:
        query["sent_at"] = {}
        if start_date:
            try:
                query["sent_at"]["$gte"] = datetime.fromisoformat(start_date)
            except Exception:
                pass
        if end_date:
            try:
                query["sent_at"]["$lte"] = datetime.fromisoformat(end_date)
            except Exception:
                pass
    
    messages = await db.message_history.find(query, {"_id": 0}).sort("sent_at", -1).limit(limit).to_list(limit)
    
    # Ensure all datetime objects are timezone-aware (UTC) and convert to ISO format
    for msg in messages:
        sent_at = msg.get('sent_at')
        if sent_at:
            if isinstance(sent_at, str):
                try:
                    dt = datetime.fromisoformat(sent_at.replace('Z', '+00:00'))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    msg['sent_at'] = dt.isoformat()
                except Exception:
                    pass
            elif isinstance(sent_at, datetime):
                # Ensure timezone-aware
                if sent_at.tzinfo is None:
                    sent_at = sent_at.replace(tzinfo=timezone.utc)
                msg['sent_at'] = sent_at.isoformat()
    
    return {
        "messages": messages,
        "total": len(messages),
        "filters": {
            "email": email,
            "personality": personality,
            "start_date": start_date,
            "end_date": end_date
        }
    }

@api_router.get("/admin/email-statistics", dependencies=[Depends(verify_admin)])
async def admin_get_email_statistics(days: int = 30):
    """Get comprehensive email delivery statistics"""
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Total emails sent
    total_sent = await db.email_logs.count_documents({"sent_at": {"$gte": cutoff}})
    successful = await db.email_logs.count_documents({"status": "success", "sent_at": {"$gte": cutoff}})
    failed = await db.email_logs.count_documents({"status": "failed", "sent_at": {"$gte": cutoff}})
    
    # Emails by personality
    personality_pipeline = [
        {"$match": {"sent_at": {"$gte": cutoff}}},
        {"$lookup": {
            "from": "message_history",
            "localField": "email",
            "foreignField": "email",
            "as": "messages"
        }},
        {"$unwind": {"path": "$messages", "preserveNullAndEmptyArrays": True}},
        {"$match": {"messages.sent_at": {"$gte": cutoff}}},
        {"$group": {
            "_id": "$messages.personality.value",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    personality_stats = await db.email_logs.aggregate(personality_pipeline).to_list(10)
    
    # Daily breakdown
    daily_pipeline = [
        {"$match": {"sent_at": {"$gte": cutoff}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$sent_at"}},
            "total": {"$sum": 1},
            "success": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
            "failed": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}}
        }},
        {"$sort": {"_id": -1}},
        {"$limit": days}
    ]
    daily_stats = await db.email_logs.aggregate(daily_pipeline).to_list(days)
    
    # Top users by email count
    user_pipeline = [
        {"$match": {"sent_at": {"$gte": cutoff}}},
        {"$group": {
            "_id": "$email",
            "count": {"$sum": 1},
            "success_count": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
            "failed_count": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    top_users = await db.email_logs.aggregate(user_pipeline).to_list(20)
    
    return {
        "summary": {
            "total_sent": total_sent,
            "successful": successful,
            "failed": failed,
            "success_rate": round((successful / total_sent * 100), 2) if total_sent > 0 else 0,
            "period_days": days
        },
        "personality_stats": personality_stats,
        "daily_stats": daily_stats,
        "top_users": top_users
    }

@api_router.get("/admin/user-activity-summary", dependencies=[Depends(verify_admin)])
async def admin_get_user_activity_summary(limit: int = 50):
    """Get summary of user activities"""
    from datetime import timedelta
    last_7d = datetime.now(timezone.utc) - timedelta(days=7)
    
    # Most active users
    active_users_pipeline = [
        {"$match": {"timestamp": {"$gte": last_7d}}},
        {"$group": {
            "_id": "$user_email",
            "action_count": {"$sum": 1},
            "last_activity": {"$max": "$timestamp"}
        }},
        {"$sort": {"action_count": -1}},
        {"$limit": limit}
    ]
    active_users = await db.activity_logs.aggregate(active_users_pipeline).to_list(limit)
    
    # Action type breakdown
    action_pipeline = [
        {"$match": {"timestamp": {"$gte": last_7d}}},
        {"$group": {
            "_id": "$action_type",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    action_breakdown = await db.activity_logs.aggregate(action_pipeline).to_list(20)
    
    return {
        "most_active_users": active_users,
        "action_breakdown": action_breakdown,
        "period_days": 7
    }

# ============================================================================
# BULK OPERATIONS
# ============================================================================

class BulkUserActionRequest(BaseModel):
    user_emails: List[str]
    action: Literal["activate", "deactivate", "pause_schedule", "resume_schedule", "delete"]

@api_router.post("/admin/bulk/users", dependencies=[Depends(verify_admin)])
async def admin_bulk_user_action(request: BulkUserActionRequest):
    """Perform bulk actions on multiple users"""
    results = {"success": [], "failed": []}
    
    for email in request.user_emails:
        try:
            user = await db.users.find_one({"email": email}, {"_id": 0})
            if not user:
                results["failed"].append({"email": email, "error": "User not found"})
                continue
            
            update_data = {}
            if request.action == "activate":
                update_data["active"] = True
            elif request.action == "deactivate":
                update_data["active"] = False
            elif request.action == "pause_schedule":
                update_data["schedule.paused"] = True
            elif request.action == "resume_schedule":
                update_data["schedule.paused"] = False
            elif request.action == "delete":
                # Soft delete
                update_data["active"] = False
                await version_tracker.soft_delete(
                    collection="users",
                    document_id=user.get("id"),
                    document_data=user,
                    deleted_by="admin",
                    reason="Bulk delete operation"
                )
            
            if update_data:
                await db.users.update_one({"email": email}, {"$set": update_data})
            
            results["success"].append({"email": email, "action": request.action})
            
            # Log activity
            await tracker.log_admin_activity(
                action_type="bulk_user_action",
                details={
                    "email": email,
                    "action": request.action,
                    "bulk_count": len(request.user_emails)
                }
            )
        except Exception as e:
            results["failed"].append({"email": email, "error": str(e)})
    
    # Reschedule emails if schedule was changed
    if request.action in ["pause_schedule", "resume_schedule"]:
        await schedule_user_emails()
    
    return {
        "total": len(request.user_emails),
        "success_count": len(results["success"]),
        "failed_count": len(results["failed"]),
        "results": results
    }

class BulkEmailRequest(BaseModel):
    user_emails: List[str]
    subject: str
    message: str

@api_router.post("/admin/bulk/email", dependencies=[Depends(verify_admin)])
async def admin_bulk_send_email(request: BulkEmailRequest):
    """Send email to multiple users"""
    results = {"success": [], "failed": []}
    
    for email in request.user_emails:
        try:
            success, error = await send_email(
                to_email=email,
                subject=request.subject,
                html_content=request.message
            )
            if success:
                results["success"].append({"email": email})
                await record_email_log(
                    email=email,
                    subject=request.subject,
                    status="success",
                    sent_dt=datetime.now(timezone.utc)
                )
            else:
                results["failed"].append({"email": email, "error": error})
                await record_email_log(
                    email=email,
                    subject=request.subject,
                    status="failed",
                    sent_dt=datetime.now(timezone.utc),
                    error_message=error
                )
        except Exception as e:
            results["failed"].append({"email": email, "error": str(e)})
    
    await tracker.log_admin_activity(
        action_type="bulk_email_send",
        details={
            "total_recipients": len(request.user_emails),
            "success_count": len(results["success"]),
            "failed_count": len(results["failed"])
        }
    )
    
    return {
        "total": len(request.user_emails),
        "success_count": len(results["success"]),
        "failed_count": len(results["failed"]),
        "results": results
    }

# ============================================================================
# USER SEGMENTATION
# ============================================================================

@api_router.get("/admin/users/segments", dependencies=[Depends(verify_admin)])
async def admin_get_user_segments(
    engagement_level: Optional[Literal["high", "medium", "low"]] = None,
    min_streak: Optional[int] = None,
    max_streak: Optional[int] = None,
    min_rating: Optional[float] = None,
    personality: Optional[str] = None,
    active_only: bool = True
):
    """Get segmented users based on various criteria"""
    query = {}
    
    if active_only:
        query["active"] = True
    
    if min_streak is not None or max_streak is not None:
        query["streak_count"] = {}
        if min_streak is not None:
            query["streak_count"]["$gte"] = min_streak
        if max_streak is not None:
            query["streak_count"]["$lte"] = max_streak
    
    if personality:
        query["personalities.value"] = personality
    
    users = await db.users.find(query, {"_id": 0}).to_list(1000)
    
    # Filter by engagement level
    if engagement_level:
        segmented_users = []
        for user in users:
            total_messages = user.get("total_messages_received", 0)
            feedback_count = await db.message_feedback.count_documents({"email": user["email"]})
            engagement_rate = (feedback_count / total_messages * 100) if total_messages > 0 else 0
            
            if engagement_level == "high" and engagement_rate >= 50:
                segmented_users.append(user)
            elif engagement_level == "medium" and 20 <= engagement_rate < 50:
                segmented_users.append(user)
            elif engagement_level == "low" and engagement_rate < 20:
                segmented_users.append(user)
        users = segmented_users
    
    # Filter by rating
    if min_rating is not None:
        rated_users = []
        for user in users:
            feedbacks = await db.message_feedback.find({"email": user["email"]}).to_list(100)
            if feedbacks:
                avg_rating = sum(f.get("rating", 0) for f in feedbacks) / len(feedbacks)
                if avg_rating >= min_rating:
                    rated_users.append(user)
        users = rated_users
    
    # Add engagement metrics to each user
    for user in users:
        total_messages = user.get("total_messages_received", 0)
        feedback_count = await db.message_feedback.count_documents({"email": user["email"]})
        user["engagement_rate"] = round((feedback_count / total_messages * 100), 2) if total_messages > 0 else 0
        
        feedbacks = await db.message_feedback.find({"email": user["email"]}).to_list(100)
        if feedbacks:
            user["avg_rating"] = round(sum(f.get("rating", 0) for f in feedbacks) / len(feedbacks), 2)
        else:
            user["avg_rating"] = None
    
    return {
        "total": len(users),
        "users": users,
        "filters": {
            "engagement_level": engagement_level,
            "min_streak": min_streak,
            "max_streak": max_streak,
            "min_rating": min_rating,
            "personality": personality,
            "active_only": active_only
        }
    }

# ============================================================================
# API COST TRACKING
# ============================================================================

@api_router.get("/admin/api-costs", dependencies=[Depends(verify_admin)])
async def admin_get_api_costs(days: int = 30):
    """Get API usage and estimated costs"""
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    # OpenAI API usage
    openai_events = await db.system_events.find({
        "event_category": {"$in": ["llm", "openai"]},
        "timestamp": {"$gte": cutoff}
    }).to_list(10000)
    
    # Estimate costs (rough estimates)
    # GPT-4: ~$0.03 per 1K input tokens, $0.06 per 1K output tokens
    # GPT-3.5: ~$0.0015 per 1K input tokens, $0.002 per 1K output tokens
    openai_cost = 0
    openai_calls = len(openai_events)
    
    # Tavily API usage
    tavily_events = await db.system_events.find({
        "event_category": "tavily",
        "timestamp": {"$gte": cutoff}
    }).to_list(10000)
    
    # Tavily: ~$0.10 per search (estimate)
    tavily_cost = len(tavily_events) * 0.10
    tavily_calls = len(tavily_events)
    
    # Daily breakdown
    daily_costs = {}
    for event in openai_events + tavily_events:
        event_date = event.get("timestamp", datetime.now(timezone.utc))
        if isinstance(event_date, str):
            event_date = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
        date_key = event_date.strftime("%Y-%m-%d")
        
        if date_key not in daily_costs:
            daily_costs[date_key] = {"openai": 0, "tavily": 0, "total": 0}
        
        if event.get("event_category") in ["llm", "openai"]:
            # Rough estimate: $0.01 per call
            daily_costs[date_key]["openai"] += 0.01
        elif event.get("event_category") == "tavily":
            daily_costs[date_key]["tavily"] += 0.10
        
        daily_costs[date_key]["total"] = daily_costs[date_key]["openai"] + daily_costs[date_key]["tavily"]
    
    total_cost = openai_calls * 0.01 + tavily_cost
    
    return {
        "period_days": days,
        "openai": {
            "calls": openai_calls,
            "estimated_cost": round(openai_calls * 0.01, 2),
            "cost_per_call": 0.01
        },
        "tavily": {
            "calls": tavily_calls,
            "estimated_cost": round(tavily_cost, 2),
            "cost_per_call": 0.10
        },
        "total_cost": round(total_cost, 2),
        "daily_breakdown": daily_costs
    }

# ============================================================================
# ALERTS & NOTIFICATIONS
# ============================================================================

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

@api_router.get("/admin/alerts", dependencies=[Depends(verify_admin)])
async def admin_get_alerts():
    """Get current alert status"""
    from datetime import timedelta
    last_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    
    # Error rate alert
    total_emails = await db.email_logs.count_documents({"sent_at": {"$gte": last_24h}})
    failed_emails = await db.email_logs.count_documents({
        "status": "failed",
        "sent_at": {"$gte": last_24h}
    })
    error_rate = (failed_emails / total_emails * 100) if total_emails > 0 else 0
    
    # API failures
    api_failures = await db.system_events.count_documents({
        "event_category": {"$in": ["llm", "tavily", "openai"]},
        "status": "failure",
        "timestamp": {"$gte": last_24h}
    })
    
    # Rate limit hits
    rate_limits = await db.system_events.count_documents({
        "event_type": {"$regex": "rate_limit", "$options": "i"},
        "timestamp": {"$gte": last_24h}
    })
    
    alerts = []
    
    if error_rate > 10:
        alerts.append({
            "type": "error_rate",
            "severity": "high" if error_rate > 20 else "medium",
            "message": f"Email error rate is {error_rate:.1f}% (threshold: 10%)",
            "value": error_rate,
            "threshold": 10
        })
    
    if api_failures > 5:
        alerts.append({
            "type": "api_failure",
            "severity": "high" if api_failures > 10 else "medium",
            "message": f"{api_failures} API failures in last 24 hours",
            "value": api_failures,
            "threshold": 5
        })
    
    if rate_limits > 0:
        alerts.append({
            "type": "rate_limit",
            "severity": "high",
            "message": f"{rate_limits} rate limit hits detected",
            "value": rate_limits,
            "threshold": 0
        })
    
    return {
        "alerts": alerts,
        "total_alerts": len(alerts),
        "critical_alerts": len([a for a in alerts if a["severity"] == "high"]),
        "metrics": {
            "error_rate": round(error_rate, 2),
            "api_failures": api_failures,
            "rate_limits": rate_limits
        }
    }

# ============================================================================
# REAL-TIME ANALYTICS & ACTIVITY TRACKING ENDPOINTS
# ============================================================================

@api_router.get("/analytics/realtime", dependencies=[Depends(verify_admin)])
async def get_realtime_analytics(minutes: int = 5):
    """Get real-time activity statistics for admin dashboard"""
    stats = await tracker.get_realtime_stats(minutes=minutes)
    return stats

@api_router.get("/analytics/user-timeline/{email}", dependencies=[Depends(verify_admin)])
async def get_user_timeline(email: str, limit: int = 100):
    """Get complete activity timeline for a specific user"""
    activities = await tracker.get_user_activity_timeline(email, limit)
    return {"email": email, "activities": activities}

@api_router.get("/analytics/activity-logs", dependencies=[Depends(verify_admin)])
async def get_activity_logs(
    limit: int = 100,
    action_category: Optional[str] = None,
    user_email: Optional[str] = None
):
    """Get filtered activity logs"""
    query = {}
    if action_category:
        query["action_category"] = action_category
    if user_email:
        query["user_email"] = user_email
    
    logs = await db.activity_logs.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"logs": logs, "total": len(logs)}

@api_router.get("/analytics/system-events", dependencies=[Depends(verify_admin)])
async def get_system_events(limit: int = 50):
    """Get recent system events"""
    events = await db.system_events.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"events": events}

@api_router.get("/analytics/api-performance", dependencies=[Depends(verify_admin)])
async def get_api_performance(hours: int = 24):
    """Get API performance metrics"""
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    # Aggregate API stats
    pipeline = [
        {"$match": {"timestamp": {"$gte": cutoff}}},
        {"$group": {
            "_id": "$endpoint",
            "total_calls": {"$sum": 1},
            "avg_response_time": {"$avg": "$response_time_ms"},
            "max_response_time": {"$max": "$response_time_ms"},
            "min_response_time": {"$min": "$response_time_ms"},
            "error_count": {
                "$sum": {"$cond": [{"$gte": ["$status_code", 400]}, 1, 0]}
            }
        }},
        {"$sort": {"total_calls": -1}},
        {"$limit": 20}
    ]
    
    stats = await db.api_analytics.aggregate(pipeline).to_list(20)
    return {"api_stats": stats, "time_window_hours": hours}

@api_router.get("/analytics/page-views", dependencies=[Depends(verify_admin)])
async def get_page_views(limit: int = 100):
    """Get recent page views"""
    views = await db.page_views.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"page_views": views}

@api_router.get("/analytics/active-sessions", dependencies=[Depends(verify_admin)])
async def get_active_sessions():
    """Get currently active user sessions"""
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
    
    sessions = await db.user_sessions.find(
        {
            "session_start": {"$gte": cutoff},
            "$or": [
                {"session_end": None},
                {"session_end": {"$gte": cutoff}}
            ]
        },
        {"_id": 0}
    ).to_list(1000)
    
    return {"active_sessions": sessions, "count": len(sessions)}

@api_router.post("/tracking/page-view")
async def track_page_view(
    page_url: str,
    user_email: Optional[str] = None,
    referrer: Optional[str] = None,
    session_id: Optional[str] = None,
    time_on_page: Optional[int] = None
):
    """Track frontend page views"""
    view_id = await tracker.log_page_view(
        page_url=page_url,
        user_email=user_email,
        referrer=referrer,
        session_id=session_id,
        time_on_page_seconds=time_on_page
    )
    return {"status": "tracked", "view_id": view_id}

@api_router.post("/tracking/user-action")
async def track_user_action(
    action_type: str,
    user_email: Optional[str] = None,
    details: Optional[Dict] = None,
    session_id: Optional[str] = None,
    request: Request = None
):
    """Track any custom user action from frontend"""
    ip_address = request.client.host if request and request.client else None
    user_agent = request.headers.get("user-agent") if request else None
    
    activity_id = await tracker.log_user_activity(
        action_type=action_type,
        user_email=user_email,
        details=details or {},
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id
    )
    return {"status": "tracked", "activity_id": activity_id}

@api_router.post("/tracking/session/start")
async def start_tracking_session(
    user_email: Optional[str] = None,
    request: Request = None
):
    """Start a new tracking session"""
    ip_address = request.client.host if request and request.client else None
    user_agent = request.headers.get("user-agent") if request else None
    
    session_id = await tracker.start_session(
        user_email=user_email,
        ip_address=ip_address,
        user_agent=user_agent
    )
    return {"session_id": session_id}

@api_router.put("/tracking/session/{session_id}")
async def update_tracking_session(
    session_id: str,
    actions: int = 0,
    pages: int = 0
):
    """Update session statistics"""
    await tracker.update_session(session_id, actions=actions, pages=pages)
    return {"status": "updated", "session_id": session_id}

# Activity Tracking Middleware
@app.middleware("http")
async def track_api_calls(request: Request, call_next):
    """Middleware to track all API calls"""
    start_time = time.time()
    
    # Get client info
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    try:
        response = await call_next(request)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Track API call
        if request.url.path.startswith("/api"):
            await tracker.log_api_call(
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                ip_address=client_ip
            )
        
        return response
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Track failed API call
        if request.url.path.startswith("/api"):
            await tracker.log_api_call(
                endpoint=request.url.path,
                method=request.method,
                status_code=500,
                response_time_ms=response_time_ms,
                ip_address=client_ip,
                error_message=str(e)
            )
        
        raise

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def create_email_job(user_email: str):
    """Scheduled job executed by AsyncIOScheduler within the main event loop."""
    try:
        await send_motivation_to_user(user_email)
        
        await tracker.log_system_event(
            event_type="scheduled_email_sent",
            event_category="scheduler",
            details={"user_email": user_email},
            status="success"
        )
    except Exception as e:
        logger.error(f"Error in email job for {user_email}: {str(e)}")

async def schedule_user_emails():
    """Schedule emails for all active users based on their preferences"""
    try:
        users = await db.users.find({"active": True}, {"_id": 0}).to_list(1000)
        
        for user_data in users:
            try:
                schedule = user_data.get('schedule', {})
                if schedule.get('paused', False):
                    continue
                
                email = user_data['email']
                times = schedule.get('times', ['09:00'])
                frequency = schedule.get('frequency', 'daily')
                user_timezone = schedule.get('timezone', 'UTC')
                
                # Parse time
                time_parts = times[0].split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                
                # Get timezone object
                try:
                    tz = pytz.timezone(user_timezone)
                except:
                    tz = pytz.UTC
                    logger.warning(f"Invalid timezone {user_timezone} for {email}, using UTC")
                
                # Create job ID
                job_id = f"user_{email.replace('@', '_at_').replace('.', '_')}"
                
                # Remove all existing jobs for this user (handles multiple times/days/dates)
                try:
                    # Remove main job
                    scheduler.remove_job(job_id)
                except:
                    pass
                # Remove any sub-jobs (for multiple times/days/dates)
                for existing_job in scheduler.get_jobs():
                    if existing_job.id.startswith(job_id + "_"):
                        try:
                            scheduler.remove_job(existing_job.id)
                        except:
                            pass
                
                # Add new job based on frequency with timezone
                # FIXED: Now properly executes async function from scheduler
                if frequency == 'daily':
                    # Handle multiple times per day
                    for time_idx, time_str in enumerate(times):
                        time_parts = time_str.split(':')
                        t_hour = int(time_parts[0])
                        t_minute = int(time_parts[1])
                        job_id_with_time = f"{job_id}_time_{time_idx}" if len(times) > 1 else job_id
                        scheduler.add_job(
                            create_email_job,
                            CronTrigger(hour=t_hour, minute=t_minute, timezone=tz),
                            args=[email],
                            id=job_id_with_time,
                            replace_existing=True
                        )
                elif frequency == 'weekly':
                    # Use custom_days if specified, otherwise default to Monday
                    custom_days = schedule.get('custom_days', [])
                    if custom_days:
                        # Map day names to cron day_of_week (0=Monday, 6=Sunday)
                        day_map = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 
                                  'friday': 4, 'saturday': 5, 'sunday': 6}
                        for day_name in custom_days:
                            day_num = day_map.get(day_name.lower(), 0)
                            job_id_with_day = f"{job_id}_day_{day_num}" if len(custom_days) > 1 else job_id
                            scheduler.add_job(
                                create_email_job,
                                CronTrigger(day_of_week=day_num, hour=hour, minute=minute, timezone=tz),
                                args=[email],
                                id=job_id_with_day,
                                replace_existing=True
                            )
                    else:
                        # Default to Monday
                        scheduler.add_job(
                            create_email_job,
                            CronTrigger(day_of_week=0, hour=hour, minute=minute, timezone=tz),
                            args=[email],
                            id=job_id,
                            replace_existing=True
                        )
                elif frequency == 'monthly':
                    # Use monthly_dates if specified, otherwise default to 1st
                    monthly_dates = schedule.get('monthly_dates', [])
                    valid_dates = []
                    if monthly_dates:
                        for date_str in monthly_dates:
                            try:
                                day_of_month = int(date_str)
                                if 1 <= day_of_month <= 31:
                                    valid_dates.append(day_of_month)
                            except (ValueError, TypeError):
                                logger.warning(f"Invalid monthly date {date_str} for {email}, skipping")
                    
                    if valid_dates:
                        for day_of_month in valid_dates:
                            job_id_with_date = f"{job_id}_date_{day_of_month}" if len(valid_dates) > 1 else job_id
                            scheduler.add_job(
                                create_email_job,
                                CronTrigger(day=day_of_month, hour=hour, minute=minute, timezone=tz),
                                args=[email],
                                id=job_id_with_date,
                                replace_existing=True
                            )
                    else:
                        # Default to 1st of month if no valid dates
                        scheduler.add_job(
                            create_email_job,
                            CronTrigger(day=1, hour=hour, minute=minute, timezone=tz),
                            args=[email],
                            id=job_id,
                            replace_existing=True
                        )
                elif frequency == 'custom':
                    # Custom interval: every N days
                    interval = schedule.get('custom_interval', 1)
                    if interval < 1:
                        interval = 1
                    # Use IntervalTrigger for custom intervals
                    scheduler.add_job(
                        create_email_job,
                        IntervalTrigger(days=interval, start_date=datetime.now(tz).replace(hour=hour, minute=minute, second=0)),
                        args=[email],
                        id=job_id,
                        replace_existing=True
                    )
                
                logger.info(f"✅ Scheduled emails for {email} at {hour}:{minute:02d} {user_timezone} ({frequency})")
                
                # Save schedule version history
                await version_tracker.save_schedule_version(
                    user_email=email,
                    schedule_data=schedule,
                    changed_by="system",
                    change_reason="Schedule initialization"
                )
                
            except Exception as e:
                logger.error(f"Error scheduling for {user_data.get('email', 'unknown')}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in schedule_user_emails: {str(e)}")

# ============================================================================
# VERSION HISTORY & DATA PRESERVATION ENDPOINTS
# ============================================================================

@api_router.get("/users/{email}/history/schedule", dependencies=[Depends(verify_admin)])
async def get_user_schedule_history(email: str, limit: int = 50):
    """Get complete schedule change history for a user"""
    history = await version_tracker.get_schedule_history(email, limit)
    return {"user_email": email, "versions": len(history), "history": history}

@api_router.get("/users/{email}/history/personalities", dependencies=[Depends(verify_admin)])
async def get_user_personality_history(email: str, limit: int = 50):
    """Get complete personality change history for a user"""
    history = await version_tracker.get_personality_history(email, limit)
    return {"user_email": email, "versions": len(history), "history": history}

@api_router.get("/users/{email}/history/profile", dependencies=[Depends(verify_admin)])
async def get_user_profile_history(email: str, limit: int = 50):
    """Get complete profile change history for a user"""
    history = await version_tracker.get_profile_history(email, limit)
    return {"user_email": email, "versions": len(history), "history": history}

@api_router.get("/users/{email}/history/complete", dependencies=[Depends(verify_admin)])
async def get_complete_user_history(email: str):
    """Get ALL change history for a user"""
    history = await version_tracker.get_all_user_history(email)
    return history

@api_router.get("/admin/deleted-data", dependencies=[Depends(verify_admin)])
async def get_deleted_data(limit: int = 100):
    """View all soft-deleted data that can be restored"""
    deleted = await db.deleted_data.find(
        {"can_restore": True},
        {"_id": 0}
    ).sort("deleted_at", -1).limit(limit).to_list(limit)
    return {"deleted_items": deleted, "count": len(deleted)}

# ============================================================================
# ADMIN ACHIEVEMENT MANAGEMENT
# ============================================================================

@api_router.get("/admin/achievements", dependencies=[Depends(verify_admin)])
async def admin_get_all_achievements(include_inactive: bool = False):
    """Get all achievements (admin only)"""
    try:
        query = {} if include_inactive else {"active": True}
        achievements = await db.achievements.find(query, {"_id": 0}).sort("priority", 1).to_list(200)
        
        logger.info(f"Admin achievements request: include_inactive={include_inactive}, found {len(achievements)} achievements")
        
        return {
            "achievements": achievements,
            "total": len(achievements),
            "active": len([a for a in achievements if a.get("active", True)])
        }
    except Exception as e:
        logger.error(f"Error fetching admin achievements: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch achievements: {str(e)}")

@api_router.post("/admin/achievements", dependencies=[Depends(verify_admin)])
async def admin_create_achievement(achievement: dict):
    """Create a new achievement (admin only)"""
    # Validate required fields
    required_fields = ["id", "name", "description", "icon_name", "category", "requirement"]
    for field in required_fields:
        if field not in achievement:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Check if achievement ID already exists
    existing = await db.achievements.find_one({"id": achievement["id"]})
    if existing:
        raise HTTPException(status_code=400, detail=f"Achievement with ID '{achievement['id']}' already exists")
    
    # Add metadata
    achievement["created_at"] = datetime.now(timezone.utc).isoformat()
    achievement["updated_at"] = datetime.now(timezone.utc).isoformat()
    achievement["active"] = achievement.get("active", True)
    achievement["priority"] = achievement.get("priority", 1)
    achievement["show_on_home"] = achievement.get("show_on_home", False)
    
    await db.achievements.insert_one(achievement)
    
    await tracker.log_admin_activity(
        action_type="achievement_created",
        admin_email="admin",
        details={"achievement_id": achievement["id"], "name": achievement["name"]}
    )
    
    return {"status": "success", "message": "Achievement created", "achievement": achievement}

@api_router.put("/admin/achievements/{achievement_id}", dependencies=[Depends(verify_admin)])
async def admin_update_achievement(achievement_id: str, achievement_data: dict):
    """Update an existing achievement (admin only)"""
    existing = await db.achievements.find_one({"id": achievement_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    # Don't allow changing the ID
    if "id" in achievement_data and achievement_data["id"] != achievement_id:
        raise HTTPException(status_code=400, detail="Cannot change achievement ID")
    
    # Update fields
    update_data = {
        "$set": {
            **achievement_data,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    }
    
    await db.achievements.update_one({"id": achievement_id}, update_data)
    
    updated = await db.achievements.find_one({"id": achievement_id}, {"_id": 0})
    
    await tracker.log_admin_activity(
        action_type="achievement_updated",
        admin_email="admin",
        details={"achievement_id": achievement_id, "changes": list(achievement_data.keys())}
    )
    
    return {"status": "success", "message": "Achievement updated", "achievement": updated}

@api_router.delete("/admin/achievements/{achievement_id}", dependencies=[Depends(verify_admin)])
async def admin_delete_achievement(achievement_id: str, hard_delete: bool = False):
    """Delete or deactivate an achievement (admin only)"""
    existing = await db.achievements.find_one({"id": achievement_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    if hard_delete:
        # Permanently delete
        await db.achievements.delete_one({"id": achievement_id})
        action = "deleted"
    else:
        # Soft delete (deactivate)
        await db.achievements.update_one(
            {"id": achievement_id},
            {"$set": {"active": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        action = "deactivated"
    
    await tracker.log_admin_activity(
        action_type="achievement_deleted",
        admin_email="admin",
        details={"achievement_id": achievement_id, "hard_delete": hard_delete}
    )
    
    return {"status": "success", "message": f"Achievement {action}", "achievement_id": achievement_id}

@api_router.post("/admin/users/{email}/achievements/{achievement_id}", dependencies=[Depends(verify_admin)])
async def admin_assign_achievement_to_user(email: str, achievement_id: str):
    """Assign an achievement to a specific user (admin only)"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify achievement exists
    achievement = await db.achievements.find_one({"id": achievement_id, "active": True})
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found or inactive")
    
    # Get current achievements
    user_achievements = user.get("achievements", [])
    
    # Check if already has this achievement
    if achievement_id in user_achievements:
        return {"status": "already_assigned", "message": "User already has this achievement"}
    
    # Add achievement with timestamp
    achievement_unlock = {
        "achievement_id": achievement_id,
        "unlocked_at": datetime.now(timezone.utc).isoformat(),
        "unlocked_by": "admin"
    }
    
    # Update user
    await db.users.update_one(
        {"email": email},
        {
            "$push": {"achievements": achievement_id},
            "$set": {"last_active": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    await tracker.log_admin_activity(
        action_type="achievement_assigned",
        admin_email="admin",
        details={"user_email": email, "achievement_id": achievement_id}
    )
    
    return {
        "status": "success",
        "message": "Achievement assigned to user",
        "achievement": achievement,
        "unlocked_at": achievement_unlock["unlocked_at"]
    }

@api_router.delete("/admin/users/{email}/achievements/{achievement_id}", dependencies=[Depends(verify_admin)])
async def admin_remove_achievement_from_user(email: str, achievement_id: str):
    """Remove an achievement from a specific user (admin only)"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_achievements = user.get("achievements", [])
    
    if achievement_id not in user_achievements:
        raise HTTPException(status_code=404, detail="User does not have this achievement")
    
    # Remove achievement
    await db.users.update_one(
        {"email": email},
        {"$pull": {"achievements": achievement_id}}
    )
    
    await tracker.log_admin_activity(
        action_type="achievement_removed",
        admin_email="admin",
        details={"user_email": email, "achievement_id": achievement_id}
    )
    
    return {"status": "success", "message": "Achievement removed from user"}

@api_router.get("/admin/users/{email}/achievements", dependencies=[Depends(verify_admin)])
async def admin_get_user_achievements(email: str):
    """Get all achievements for a specific user (admin only)"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_achievements = user.get("achievements", [])
    achievements_dict = await get_achievements_from_db()
    
    unlocked = []
    for ach_id in user_achievements:
        if ach_id in achievements_dict:
            unlocked.append(achievements_dict[ach_id])
    
    return {
        "user_email": email,
        "unlocked_achievements": unlocked,
        "total_unlocked": len(unlocked),
        "achievement_ids": user_achievements
    }

@api_router.post("/admin/achievements/initialize", dependencies=[Depends(verify_admin)])
async def admin_initialize_achievements():
    """Manually trigger achievement initialization (admin only)"""
    await initialize_achievements()
    count = await db.achievements.count_documents({"active": True})
    return {
        "status": "success",
        "message": "Achievements initialized",
        "total_active_achievements": count
    }

@api_router.post("/admin/achievements/recalculate-streaks", dependencies=[Depends(verify_admin)])
async def admin_recalculate_streaks(email: Optional[str] = None):
    """Recalculate streaks for all users or a specific user based on message history"""
    try:
        if email:
            users = [await db.users.find_one({"email": email}, {"_id": 0})]
            if not users[0]:
                raise HTTPException(status_code=404, detail="User not found")
        else:
            users = await db.users.find({"active": True}, {"_id": 0, "email": 1}).to_list(1000)
        
        updated_count = 0
        results = []
        
        for user in users:
            user_email = user["email"]
            
            # Get all messages for this user, sorted by date
            messages = await db.message_history.find(
                {"email": user_email},
                {"_id": 0, "sent_at": 1, "created_at": 1}
            ).sort("sent_at", 1).to_list(1000)
            
            if not messages:
                continue
            
            # Extract unique dates when emails were sent
            email_dates = set()
            for msg in messages:
                sent_at = msg.get("sent_at") or msg.get("created_at")
                if sent_at:
                    if isinstance(sent_at, str):
                        try:
                            dt = datetime.fromisoformat(sent_at.replace('Z', '+00:00'))
                        except:
                            dt = datetime.fromisoformat(sent_at)
                    else:
                        dt = sent_at
                    email_dates.add(dt.date())
            
            # Calculate longest consecutive streak
            if not email_dates:
                continue
            
            sorted_dates = sorted(email_dates)
            today = datetime.now(timezone.utc).date()
            
            # Calculate current active streak (from most recent date backwards)
            most_recent_date = sorted_dates[-1]
            days_since_last = (today - most_recent_date).days
            
            # If email was sent today or yesterday, calculate active streak
            if days_since_last <= 1:
                # Calculate streak backwards from most recent date
                # Start from the most recent date and count backwards
                current_streak = 0
                expected_date = most_recent_date
                
                # Convert sorted_dates to a set for O(1) lookup
                date_set = set(sorted_dates)
                
                # Count consecutive days backwards from most recent
                while expected_date in date_set:
                    current_streak += 1
                    expected_date = expected_date - timedelta(days=1)
                
                # Ensure minimum streak of 1
                current_streak = max(1, current_streak)
            else:
                # Gap of more than 1 day - streak is broken
                current_streak = 1
            
            # Update user's streak
            await db.users.update_one(
                {"email": user_email},
                {"$set": {"streak_count": current_streak}}
            )
            
            # Calculate max streak for reporting
            max_streak = 1
            temp_streak = 1
            for i in range(1, len(sorted_dates)):
                days_diff = (sorted_dates[i] - sorted_dates[i-1]).days
                if days_diff == 1:
                    temp_streak += 1
                    max_streak = max(max_streak, temp_streak)
                else:
                    temp_streak = 1
            
            results.append({
                "email": user_email,
                "old_streak": user.get("streak_count", 0),
                "new_streak": current_streak,
                "total_email_days": len(sorted_dates),
                "max_streak": max_streak
            })
            updated_count += 1
        
        await tracker.log_admin_activity(
            action_type="streaks_recalculated",
            admin_email="admin",
            details={"users_updated": updated_count, "email_filter": email}
        )
        
        return {
            "status": "success",
            "message": f"Recalculated streaks for {updated_count} user(s)",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error recalculating streaks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to recalculate streaks: {str(e)}")

@api_router.post("/admin/achievements/{achievement_id}/assign-all", dependencies=[Depends(verify_admin)])
async def admin_assign_achievement_to_all_users(achievement_id: str):
    """Assign an achievement to all active users (admin only)"""
    # Verify achievement exists
    achievement = await db.achievements.find_one({"id": achievement_id, "active": True})
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found or inactive")
    
    # Get all active users
    users = await db.users.find({"active": True}, {"_id": 0, "email": 1, "achievements": 1}).to_list(1000)
    
    assigned_count = 0
    already_had_count = 0
    updated_count = 0
    
    for user in users:
        user_achievements = user.get("achievements", [])
        
        if achievement_id in user_achievements:
            already_had_count += 1
            continue
        
        # Add achievement
        await db.users.update_one(
            {"email": user["email"]},
            {
                "$push": {"achievements": achievement_id},
                "$set": {"last_active": datetime.now(timezone.utc).isoformat()}
            }
        )
        assigned_count += 1
        updated_count += 1
    
    await tracker.log_admin_activity(
        action_type="achievement_bulk_assigned",
        admin_email="admin",
        details={
            "achievement_id": achievement_id,
            "assigned_to": assigned_count,
            "already_had": already_had_count,
            "total_users": len(users)
        }
    )
    
    return {
        "status": "success",
        "message": f"Achievement assigned to {assigned_count} users",
        "achievement": achievement,
        "stats": {
            "total_users": len(users),
            "newly_assigned": assigned_count,
            "already_had": already_had_count
        }
    }

@api_router.post("/admin/achievements/{achievement_id}/remove-all", dependencies=[Depends(verify_admin)])
async def admin_remove_achievement_from_all_users(achievement_id: str):
    """Remove an achievement from all users (admin only)"""
    # Verify achievement exists
    achievement = await db.achievements.find_one({"id": achievement_id})
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    # Remove from all users
    result = await db.users.update_many(
        {},
        {"$pull": {"achievements": achievement_id}}
    )
    
    await tracker.log_admin_activity(
        action_type="achievement_bulk_removed",
        admin_email="admin",
        details={
            "achievement_id": achievement_id,
            "removed_from": result.modified_count
        }
    )
    
    return {
        "status": "success",
        "message": f"Achievement removed from {result.modified_count} users",
        "achievement_id": achievement_id,
        "users_affected": result.modified_count
    }

@api_router.post("/admin/restore/{deletion_id}", dependencies=[Depends(verify_admin)])
async def restore_deleted_data(deletion_id: str):
    """Restore soft-deleted data"""
    success = await version_tracker.restore_deleted(deletion_id)
    if success:
        return {"status": "restored", "deletion_id": deletion_id}
    else:
        raise HTTPException(status_code=404, detail="Cannot restore - data not found or already restored")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        try:
            await db.users.create_index("email", unique=True)
            await db.pending_logins.create_index("email")
            await db.message_history.create_index("email")
            await db.message_feedback.create_index("email")
            await db.email_logs.create_index([("email", 1), ("sent_at", -1)])
            logger.info("Database indexes created")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")

        await initialize_achievements()
        logger.info("Achievements initialized")
        
        scheduler.start()
        logger.info("Scheduler started")

        await schedule_user_emails()
        logger.info("User email schedules initialized")

        yield
    finally:
        try:
            scheduler.shutdown()
        except Exception as e:
            logger.warning(f"Scheduler shutdown warning: {e}")
        client.close()

app.router.lifespan_context = lifespan