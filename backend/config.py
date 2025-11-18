"""
Configuration and database connections
"""
import os
import warnings
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncOpenAI
from typing import Dict

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')


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


# MongoDB connection
MONGO_URL = get_env('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = get_env('DB_NAME', 'inbox_inspire')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Export client for cleanup in lifespan
__all__ = ['db', 'openai_client', 'TAVILY_API_KEY', 'TAVILY_SEARCH_URL', 
           'personality_voice_cache', 'get_env', 'client']

# OpenAI client
OPENAI_API_KEY = get_env('OPENAI_API_KEY')
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Tavily research
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
TAVILY_SEARCH_URL = "https://api.tavily.com/search"

# Cache for personality voice descriptions
personality_voice_cache: Dict[str, str] = {}

