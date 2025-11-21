"""
Validation utilities for backend API
"""
import re
import pytz
from typing import Optional, Tuple
from datetime import datetime

def validate_timezone(timezone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate IANA timezone string
    Returns: (is_valid, error_message)
    """
    if not timezone or not isinstance(timezone, str):
        return False, "Timezone is required and must be a string"
    
    if len(timezone) < 3 or len(timezone) > 50:
        return False, "Timezone must be between 3 and 50 characters"
    
    try:
        # Try to create a timezone object to validate
        pytz.timezone(timezone)
        return True, None
    except pytz.exceptions.UnknownTimeZoneError:
        return False, f"Invalid timezone: {timezone}. Please use a valid IANA timezone (e.g., 'America/New_York', 'UTC')"
    except Exception as e:
        return False, f"Timezone validation error: {str(e)}"

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format
    Returns: (is_valid, error_message)
    """
    if not email or not isinstance(email, str):
        return False, "Email is required and must be a string"
    
    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 254:  # RFC 5321 limit
        return False, "Email address is too long (max 254 characters)"
    
    return True, None

def validate_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate user name
    Returns: (is_valid, error_message)
    """
    if not name or not isinstance(name, str):
        return False, "Name is required and must be a string"
    
    name_trimmed = name.strip()
    if len(name_trimmed) == 0:
        return False, "Name cannot be empty"
    
    if len(name) > 100:
        return False, "Name must be less than 100 characters"
    
    # Check for potentially harmful characters
    if re.search(r'[<>{}[\]\\]', name):
        return False, "Name contains invalid characters"
    
    return True, None

def validate_schedule(schedule: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate schedule configuration
    Returns: (is_valid, error_message)
    """
    if not isinstance(schedule, dict):
        return False, "Schedule must be a dictionary"
    
    # Validate frequency
    valid_frequencies = ["daily", "weekly", "monthly", "custom"]
    frequency = schedule.get("frequency")
    if frequency and frequency not in valid_frequencies:
        return False, f"Invalid frequency. Must be one of: {', '.join(valid_frequencies)}"
    
    # Validate times
    times = schedule.get("times", [])
    if times:
        if not isinstance(times, list):
            return False, "Times must be a list"
        for time_str in times:
            if not isinstance(time_str, str):
                return False, "Each time must be a string"
            # Validate time format (HH:MM)
            if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', time_str):
                return False, f"Invalid time format: {time_str}. Use HH:MM format (e.g., '09:00')"
    
    # Validate timezone if present
    timezone = schedule.get("timezone")
    if timezone:
        is_valid, error = validate_timezone(timezone)
        if not is_valid:
            return False, f"Schedule timezone error: {error}"
    
    # Validate custom_days if present
    custom_days = schedule.get("custom_days")
    if custom_days:
        if not isinstance(custom_days, list):
            return False, "Custom days must be a list"
        valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in custom_days:
            if day.lower() not in valid_days:
                return False, f"Invalid day: {day}. Must be one of: {', '.join(valid_days)}"
    
    # Validate monthly_dates if present
    monthly_dates = schedule.get("monthly_dates")
    if monthly_dates:
        if not isinstance(monthly_dates, list):
            return False, "Monthly dates must be a list"
        for date_str in monthly_dates:
            try:
                date_num = int(date_str)
                if date_num < 1 or date_num > 31:
                    return False, f"Invalid monthly date: {date_str}. Must be between 1 and 31"
            except (ValueError, TypeError):
                return False, f"Invalid monthly date format: {date_str}. Must be a number between 1 and 31"
    
    return True, None

