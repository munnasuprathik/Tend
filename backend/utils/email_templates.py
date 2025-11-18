"""
Email template and formatting utilities
"""
import html
import re
import secrets
import random
from typing import List
# Note: derive_goal_theme is defined in this file, not imported


def _render_list_items(lines: List[str]) -> str:
    if not lines:
        return ""
    items = "".join(f"<li>{html.escape(line)}</li>" for line in lines)
    return f"<ul>{items}</ul>"


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


def generate_interactive_defaults(streak_count: int, goals: str) -> tuple[List[str], List[str]]:
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

