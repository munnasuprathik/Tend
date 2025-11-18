"""
Helper utility functions for text processing, validation, and safety checks
"""
import re
from typing import Optional, List
from backend.constants import EMOJI_REGEX


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


def redact_sensitive_info(text: str) -> str:
    """Redact sensitive information from text"""
    # Redact email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
    # Redact phone numbers (basic pattern)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]', text)
    # Redact credit card numbers (basic pattern)
    text = re.sub(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[CARD_REDACTED]', text)
    return text


def check_profanity(text: str) -> bool:
    """Check for profanity - returns True if profanity found"""
    profanity_words = ["damn", "hell", "shit", "fuck", "asshole"]  # Add more as needed
    text_lower = text.lower()
    return any(word in text_lower for word in profanity_words)


def check_impersonation(body: str, persona_name: str, confidence: float) -> bool:
    """Check if message contains impersonation claims"""
    body_lower = body.lower()
    # If confidence is low, be more strict
    if confidence < 0.6:
        # Check for direct claims
        claims = [f"i am {persona_name.lower()}", f"this is {persona_name.lower()}", f"i'm {persona_name.lower()}"]
        return any(claim in body_lower for claim in claims)
    return False


def calculate_similarity(text1: str, text2: str) -> float:
    """Simple similarity check - returns 0-1 score"""
    # Simple word overlap check
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union) if union else 0.0

