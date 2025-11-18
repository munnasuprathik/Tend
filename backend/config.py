"""
Configuration and database connections
"""
import os
import warnings
import logging
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncOpenAI
from typing import Dict

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

def get_env(key: str, default: str = None) -> str:
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


# Required environment variables (must be set)
REQUIRED_ENV_VARS = [
    "MONGO_URL",
    "OPENAI_API_KEY",
    "SMTP_HOST",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "ADMIN_SECRET"
]

# Optional environment variables (warnings only)
OPTIONAL_ENV_VARS = [
    "TAVILY_API_KEY",
    "IMAP_HOST",
    "INBOX_EMAIL",
    "INBOX_PASSWORD",
    "CORS_ORIGINS",
    "FRONTEND_URL",
    "DB_NAME"
]


def validate_environment():
    """
    Validate all required environment variables on startup.
    Raises RuntimeError if any required variables are missing.
    Logs warnings for missing optional variables.
    """
    missing_required = []
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        error_msg = f"Missing required environment variables: {', '.join(missing_required)}"
        logger.error(error_msg)
        raise RuntimeError(
            f"{error_msg}\n"
            "Please set these variables in your .env file or environment before starting the server."
        )
    
    missing_optional = []
    for var in OPTIONAL_ENV_VARS:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_optional:
        logger.warning("Optional environment variables not set:")
        for var in missing_optional:
            logger.warning(f"  - {var} (optional)")
        logger.info("These are optional and the application will use defaults if available.")
    
    logger.info("✅ Environment variable validation passed")


# Validate environment on import
try:
    validate_environment()
except RuntimeError as e:
    # Only raise if we're actually starting the server
    # This allows imports to work even if env vars aren't set yet
    import sys
    if 'uvicorn' in sys.modules or 'server' in sys.modules:
        raise


# MongoDB connection
MONGO_URL = get_env('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = get_env('DB_NAME', 'tend')

# Configure MongoDB connection with pooling (increased for 10k+ users)
client = AsyncIOMotorClient(
    MONGO_URL,
    maxPoolSize=100,  # Increased from 50 for higher concurrency
    minPoolSize=20,   # Increased from 10 for better connection management
    serverSelectionTimeoutMS=5000
)
db = client[DB_NAME]

# Export client for cleanup in lifespan
__all__ = ['db', 'openai_client', 'TAVILY_API_KEY', 'TAVILY_SEARCH_URL', 
           'personality_voice_cache', 'get_env', 'client', 'validate_environment']

# OpenAI client
OPENAI_API_KEY = get_env('OPENAI_API_KEY')
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Tavily research
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
TAVILY_SEARCH_URL = "https://api.tavily.com/search"

# Cache for personality voice descriptions
personality_voice_cache: Dict[str, str] = {}

