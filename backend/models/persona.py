"""
Persona research Pydantic models
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from datetime import datetime, timezone

class PersonaResearch(BaseModel):
    """Structured persona research data extracted from Tavily and summarized"""
    model_config = ConfigDict(extra="ignore")
    
    persona_id: str
    style_summary: str  # 1-2 lines describing style
    verbosity_score: float = Field(ge=0.0, le=1.0)  # 0 = very concise, 1 = verbose
    positivity_score: float = Field(ge=-1.0, le=1.0)  # -1 = negative, 1 = positive
    top_phrases: List[str] = []  # Frequent short phrases (not verbatim quotes)
    recent_topics: List[str] = []  # Last 3-6 topics
    engagement_cues: List[str] = []  # Exclamations, rhetorical Qs, humor indicators
    sample_lines: List[str] = []  # 1-2 safe paraphrased stylistic examples
    confidence_score: float = Field(ge=0.0, le=1.0)  # How confident we are in the research
    last_refreshed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cache_ttl_hours: int = 24  # Default 24 hours
    summarizer_version: str = "1.0"

