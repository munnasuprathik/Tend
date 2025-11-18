# Frontend Integration Examples

## Example 1: Single Goal with Multiple Times Per Day

```json
{
  "title": "Fitness Journey",
  "description": "Daily fitness motivation and tracking",
  "mode": "tone",
  "tone": "energetic & enthusiastic",
  "schedules": [
    {
      "type": "daily",
      "times": ["07:00", "12:00", "18:00"],
      "timezone": "America/New_York",
      "active": true,
      "schedule_name": "Morning Boost + Lunch Check-in + Evening Review"
    }
  ],
  "send_limit_per_day": 3,
  "active": true
}
```

## Example 2: Multiple Goals with Different Frequencies

### Goal 1: Daily Workout Motivation

```json
{
  "title": "Workout Motivation",
  "description": "Get pumped for daily workouts",
  "mode": "tone",
  "tone": "energetic & enthusiastic",
  "schedules": [
    {
      "type": "daily",
      "time": "06:00",
      "timezone": "UTC",
      "active": true,
      "schedule_name": "Morning Workout Hype"
    }
  ]
}
```

### Goal 2: Weekly Career Reflection

```json
{
  "title": "Career Development",
  "description": "Weekly reflection on career growth",
  "mode": "personality",
  "personality_id": "satya_nadella_123",
  "schedules": [
    {
      "type": "weekly",
      "weekdays": [0, 4],  // Monday and Friday
      "time": "09:00",
      "timezone": "UTC",
      "active": true,
      "schedule_name": "Week Start + Week End Review"
    }
  ]
}
```

### Goal 3: Monthly Goal Review

```json
{
  "title": "Monthly Goal Review",
  "description": "Deep reflection on monthly progress",
  "mode": "tone",
  "tone": "philosophical & reflective",
  "schedules": [
    {
      "type": "monthly",
      "monthly_dates": [1, 15],  // 1st and 15th of month
      "time": "20:00",
      "timezone": "UTC",
      "active": true,
      "schedule_name": "Monthly Check-in"
    }
  ]
}
```

## Example 3: Single Goal with Multiple Schedule Types

```json
{
  "title": "Complete Transformation",
  "description": "Daily motivation + Weekly review + Monthly planning",
  "mode": "custom",
  "custom_text": "Speak like a wise mentor who balances daily action with long-term vision",
  "schedules": [
    {
      "type": "daily",
      "time": "07:00",
      "timezone": "UTC",
      "active": true,
      "schedule_name": "Daily Morning Motivation"
    },
    {
      "type": "weekly",
      "weekdays": [6],  // Sunday
      "time": "18:00",
      "timezone": "UTC",
      "active": true,
      "schedule_name": "Weekly Reflection"
    },
    {
      "type": "monthly",
      "monthly_dates": [1],
      "time": "09:00",
      "timezone": "UTC",
      "active": true,
      "schedule_name": "Monthly Strategy Session"
    }
  ],
  "send_limit_per_day": 5,
  "active": true
}
```

