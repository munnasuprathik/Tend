"""
Utility functions
"""
from .helpers import (
    strip_emojis,
    extract_interactive_sections,
    redact_sensitive_info,
    check_profanity,
    check_impersonation,
    calculate_similarity
)

from .email_templates import (
    render_email_html,
    _render_list_items,
    generate_interactive_defaults,
    resolve_streak_badge,
    fallback_subject_line,
    derive_goal_theme,
    cleanup_message_text
)

__all__ = [
    "strip_emojis",
    "extract_interactive_sections",
    "redact_sensitive_info",
    "check_profanity",
    "check_impersonation",
    "calculate_similarity",
    "render_email_html",
    "_render_list_items",
    "generate_interactive_defaults",
    "resolve_streak_badge",
    "fallback_subject_line",
    "derive_goal_theme",
    "cleanup_message_text",
]

