# Tend - Complete Project Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Authentication Flow](#authentication-flow)
7. [Core Features](#core-features)
8. [AI Prompts & Message Generation](#ai-prompts--message-generation)
9. [Email System](#email-system)
10. [Scheduling System](#scheduling-system)
11. [Activity Tracking & Logging](#activity-tracking--logging)
12. [Admin Dashboard](#admin-dashboard)
13. [User Dashboard](#user-dashboard)
14. [Scalability & Performance](#scalability--performance)
15. [Security](#security)
16. [Deployment](#deployment)
17. [Environment Variables](#environment-variables)

---

## Project Overview

**Tend** is a personalized motivational email service that sends daily inspiration messages to users based on their goals, selected personalities, and preferences. The application uses OpenAI GPT-4o to generate unique, personalized messages and manages email delivery through a sophisticated scheduling system.

### Key Features
- **Personalized Messages**: AI-generated motivational emails tailored to user goals
- **Personality System**: Choose from famous personalities, tones, or create custom personalities
- **Goal Management**: Multi-goal support with individual schedules
- **Streak Tracking**: Track daily engagement and maintain streaks
- **Achievement System**: Unlock achievements based on milestones
- **Email Replies**: Automatic processing of user email replies
- **Admin Dashboard**: Comprehensive monitoring and management tools
- **Activity Tracking**: Complete logging of all user and system events

---

## Architecture

### Backend (FastAPI)
- **Framework**: FastAPI (Python)
- **Database**: MongoDB (Motor async driver)
- **Scheduler**: APScheduler (AsyncIOScheduler)
- **Email**: aiosmtplib (async SMTP)
- **AI**: OpenAI GPT-4o
- **Rate Limiting**: slowapi
- **Authentication**: Clerk (third-party service)

### Frontend (React)
- **Framework**: React 19
- **UI Library**: Shadcn UI + Tailwind CSS
- **Authentication**: Clerk React SDK
- **HTTP Client**: Axios

### Infrastructure
- **Database**: MongoDB Atlas
- **Email Service**: SMTP (configurable)
- **Research API**: Tavily (optional)

---

## Technology Stack

### Backend Dependencies
```
fastapi
motor (MongoDB async driver)
openai
apscheduler
aiosmtplib
slowapi (rate limiting)
pydantic
python-dotenv
pytz
httpx
beautifulsoup4
imap-tools (email reply polling)
```

### Frontend Dependencies
```
react
react-dom
@clerk/clerk-react
axios
sonner (toasts)
lucide-react (icons)
tailwindcss
```

---

## Database Schema

### Collections

#### `users`
```json
{
  "email": "user@example.com",
  "clerk_user_id": "clerk_xxx",
  "name": "User Name",
  "image_url": "https://...",
  "goals": "Build a successful startup",
  "personalities": [
    {
      "id": "uuid",
      "type": "famous|tone|custom",
      "value": "Steve Jobs|inspiring|custom text",
      "active": true
    }
  ],
  "rotation_mode": "sequential|random",
  "current_personality_index": 0,
  "schedule": {
    "frequency": "daily|weekly|monthly",
    "times": ["09:00", "18:00"],
    "timezone": "America/New_York",
    "paused": false,
    "skip_next": false,
    "end_date": null
  },
  "user_timezone": "America/New_York",
  "streak_count": 5,
  "total_messages_received": 10,
  "achievements": ["first_streak", "week_warrior"],
  "active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "last_active": "2024-01-05T00:00:00Z"
}
```

#### `message_history`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "message": "Message content...",
  "subject": "Subject line",
  "personality": {
    "type": "famous",
    "value": "Steve Jobs"
  },
  "message_type": "motivational_story",
  "sent_at": "2024-01-05T09:00:00Z",
  "used_fallback": false,
  "research_snippet": "Optional research insight",
  "goal_id": "optional_goal_id"
}
```

#### `message_feedback`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "message_id": "message_uuid",
  "rating": 5,
  "comment": "Great message!",
  "personality": "Steve Jobs",
  "timestamp": "2024-01-05T10:00:00Z"
}
```

#### `goals`
```json
{
  "id": "uuid",
  "user_email": "user@example.com",
  "title": "Build a startup",
  "description": "Create a successful SaaS product",
  "category": "career",
  "deadline": "2024-12-31",
  "status": "active|completed|paused",
  "mode": "personality|tone|custom",
  "personality_id": "optional",
  "tone": "optional",
  "custom_text": "optional",
  "custom_personality_id": "optional",
  "schedule": {
    "frequency": "daily",
    "times": ["09:00"],
    "timezone": "America/New_York"
  },
  "send_limit_per_day": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-05T00:00:00Z"
}
```

#### `email_logs`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "subject": "Subject line",
  "status": "success|failed",
  "sent_at": "2024-01-05T09:00:00Z",
  "timezone": "America/New_York",
  "error_message": null
}
```

#### `activity_logs`
```json
{
  "id": "uuid",
  "user_email": "user@example.com",
  "action_type": "onboarding_completed|profile_updated|...",
  "action_category": "user_action|admin_action",
  "details": {},
  "timestamp": "2024-01-05T09:00:00Z",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "session_id": "session_uuid"
}
```

#### `system_events`
```json
{
  "id": "uuid",
  "event_type": "scheduled_email_sent|email_job_completed|...",
  "event_category": "scheduler|background_task|api",
  "details": {},
  "timestamp": "2024-01-05T09:00:00Z",
  "duration_ms": 150,
  "status": "success|error|warning"
}
```

#### `api_analytics`
```json
{
  "id": "uuid",
  "endpoint": "/api/users/{email}",
  "method": "GET",
  "status_code": 200,
  "response_time_ms": 50,
  "user_email": "user@example.com",
  "timestamp": "2024-01-05T09:00:00Z",
  "ip_address": "192.168.1.1",
  "error_message": null
}
```

#### Additional Collections
- `achievements` - Achievement definitions
- `goal_messages` - Goal-specific message scheduling
- `schedule_history` - Version history for schedules
- `personality_history` - Version history for personalities
- `profile_history` - Version history for profiles
- `custom_personality_conversations` - Custom personality chat sessions
- `custom_personality_profiles` - Custom personality definitions
- `persona_research` - Cached persona research data
- `email_reply_conversations` - User email replies
- `page_views` - Frontend page view tracking
- `user_sessions` - User session tracking
- `deleted_data` - Soft-deleted items

---

## API Endpoints

### Authentication
- `POST /api/auth/clerk-sync` - Sync Clerk user to database
- `POST /api/auth/login` - **DEPRECATED** (returns 410)
- `POST /api/auth/verify` - **DEPRECATED** (returns 410)

### User Endpoints
- `POST /api/onboarding` - Complete user onboarding
- `GET /api/users/{email}` - Get user profile
- `PUT /api/users/{email}` - Update user profile
- `GET /api/users/{email}/message-history` - Get message history
- `GET /api/users/{email}/analytics` - Get user analytics
- `GET /api/users/{email}/streak-status` - Get streak status
- `POST /api/users/{email}/recalculate-streak` - Recalculate streak
- `POST /api/users/{email}/feedback` - Submit message feedback
- `GET /api/users/{email}/goals` - List user goals
- `POST /api/users/{email}/goals` - Create goal
- `PUT /api/users/{email}/goals/{goal_id}` - Update goal
- `DELETE /api/users/{email}/goals/{goal_id}` - Delete goal
- `GET /api/users/{email}/replies` - Get email replies
- `GET /api/users/{email}/reply-insights` - Get reply insights
- `POST /api/users/{email}/personalities` - Add personality
- `DELETE /api/users/{email}/personalities/{personality_id}` - Remove personality
- `POST /api/generate-message` - Generate test message
- `POST /api/send-now/{email}` - Send immediate message
- `GET /api/famous-personalities` - Get famous personalities list
- `GET /api/tone-options` - Get tone options list

### Admin Endpoints
- `GET /api/admin/users` - List all users (paginated)
- `GET /api/admin/users/{email}` - Get user details
- `POST /api/admin/users/{email}/activate` - Activate user
- `POST /api/admin/users/{email}/deactivate` - Deactivate user
- `GET /api/admin/stats` - Get global statistics
- `GET /api/admin/logs/activity` - Get activity logs
- `GET /api/admin/logs/system-events` - Get system events
- `GET /api/admin/logs/api-analytics` - Get API analytics
- `GET /api/admin/logs/unified` - Get unified logs
- `POST /api/admin/broadcast` - Broadcast message to all users
- `GET /api/admin/search` - Global search
- `GET /api/admin/user-segments` - Get user segments
- `POST /api/admin/recalculate-streaks` - Recalculate all streaks
- `POST /api/admin/test-email` - Send test email

### System Endpoints
- `GET /api/health` - Health check
- `GET /` - Root endpoint

---

## Authentication Flow

### Clerk Integration

1. **User Signs In with Clerk**
   - User clicks "Sign In" on frontend
   - Clerk handles authentication (OAuth, email/password, etc.)
   - Clerk returns user data (ID, email, name, image)

2. **Sync to Database**
   - Frontend calls `POST /api/auth/clerk-sync` with Clerk user data
   - Backend creates/updates user in MongoDB with `clerk_user_id`
   - User record is ready for onboarding or dashboard access

3. **Onboarding**
   - User completes onboarding form
   - Frontend calls `POST /api/onboarding`
   - Backend saves all user preferences (goals, personalities, schedule)
   - User is activated and scheduled

4. **Dashboard Access**
   - User is authenticated via Clerk session
   - Frontend loads user profile from `GET /api/users/{email}`
   - All user data is stored in MongoDB

**Key Points:**
- Only Clerk authentication is supported (magic link deprecated)
- All user data stored in MongoDB
- `clerk_user_id` links Clerk user to database record

---

## Core Features

### 1. Message Generation
- Uses OpenAI GPT-4o for message generation
- Considers user goals, personality, streak count, previous messages
- Includes research snippets from Tavily (optional)
- Generates unique subject lines
- Avoids repetition using message type rotation

### 2. Personality System
- **Famous Personalities**: Pre-defined famous people (Steve Jobs, etc.)
- **Tones**: Emotional tones (inspiring, supportive, etc.)
- **Custom**: User-defined personality descriptions
- **Rotation**: Sequential or random personality rotation
- **Research**: Tavily research for famous/custom personalities

### 3. Goal Management
- Multiple goals per user
- Individual schedules per goal
- Personality/tone/custom mode per goal
- Goal-specific message generation
- Deadline tracking

### 4. Streak Tracking
- Daily streak calculation
- Streak milestones (3, 7, 30, 100 days)
- Automatic streak updates on email send
- Streak recalculation from history

### 5. Achievement System
- Pre-defined achievements (streak-based, message-based, feedback-based)
- Automatic unlocking on milestone
- Achievement display in dashboard

### 6. Email Replies
- IMAP polling for user replies
- Automatic reply processing
- Context-aware response generation
- Urgency detection

---

## AI Prompts & Message Generation

### Main Message Generation Prompt

**System Message:**
```
You are a world-class motivational coach who creates deeply personal, unique messages that inspire real action. You never use cliches, never repeat yourself, and you always sound human - not like an AI summarizer. Every message feels handcrafted.
```

**User Prompt Template:**
```
You are an elite personal coach creating a UNIQUE daily motivation message.

VOICE PROFILE:
[Personality voice profile from research or fallback]

USER'S GOALS: {goals}
STREAK COUNT: {streak_count}
PERSONALITY MODE: {personality.type}
PERSONALITY VALUE: {personality.value}
LAST PERSONA USED: {latest_persona or "unknown"}
LATEST MESSAGE SAMPLE: {latest_message_snippet or "None"}
STREAK CONTEXT: {streak_context}
MESSAGE TYPE: {message_type}
RESEARCH INSIGHT: {research_snippet}

STORY BLUEPRINT: {blueprint}
EMOTIONAL ARC: {emotional_arc}
RECENT THEMES TO AVOID:
{recent_themes_block}

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
10. Close with a crystal-clear micro action.
11. Do NOT use emojis, emoticons, or Unicode pictographs; rely on plain words or ASCII icons (e.g. [*], ->) for emphasis.
12. After the core message, create a section formatted exactly like this:

INTERACTIVE CHECK-IN:
- Provide exactly one bullet beginning with "- " that asks a thoughtful question or challenge tied to the goals and streak.

QUICK REPLY PROMPT:
- Provide exactly one bullet beginning with "- " that gives a precise reply instruction (actionable and time-bound).

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

Write an authentic, powerful message that feels personal and impossible to ignore:
```

**Parameters:**
- Model: `gpt-4o`
- Temperature: `0.9` (high creativity)
- Max Tokens: `500`
- Presence Penalty: `0.6` (avoid repetition)
- Frequency Penalty: `0.6` (encourage variety)

### Subject Line Generation Prompt

**System Message:**
```
You write vivid, human email subject lines for a motivational product. They feel handcrafted, avoid gimmicks, refuse cliches, and never mention tone/persona names.
```

**User Prompt:**
```
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

Return only the subject line.
```

**Parameters:**
- Model: `gpt-4o-mini`
- Temperature: `0.75`
- Max Tokens: `24`

### Goal Message Generation Prompt

**System Message:**
```
You are a world-class motivational coach who creates unique, engaging, and enjoyable emails. Every email must be different, fresh, and delightful to read. You excel at variety, creativity, and making content that users genuinely enjoy. Return ONLY valid JSON with subject and body fields.
```

**User Prompt Structure:**
```
Generate a motivational email for a user working toward a specific goal.

User Context:
- Name: {user_name}
- Goal: {goal_title}
- Goal Description: {goal_description}
- Streak: {streak_count} days
- Timezone: {user_timezone}

Mode: {mode}
[Personality/Tone/Custom instructions based on mode]

Last 3 Emails Context:
{last_3_emails}

Controls:
- Speaking Length: {speaking_length}
- Max Words: {max_words}

Variety Parameters:
- Structure: {structure}
- Angle: {angle}
- Technique: {technique}

Return ONLY valid JSON:
{
  "subject": "Subject line (under 60 chars)",
  "body": "Message body with INTERACTIVE CHECK-IN and QUICK REPLY PROMPT sections"
}
```

### Persona Research Summarization Prompt

**System Message:**
```
You are a communication style analyst. Extract features and return ONLY valid JSON.
```

**User Prompt:**
```
Analyze the following content about {persona_name} and extract communication style features.

Content (excerpts):
{combined_text}

Extract and return ONLY a JSON object with these exact fields:
{
    "style_summary": "1-2 sentence description of communication style",
    "verbosity_score": 0.0-1.0 (0=very concise, 1=verbose),
    "positivity_score": -1.0 to 1.0 (-1=negative, 1=positive),
    "top_phrases": ["phrase1", "phrase2", "phrase3"] (short frequent phrases, NOT verbatim quotes),
    "recent_topics": ["topic1", "topic2"] (3-6 recent topics),
    "engagement_cues": ["cue1", "cue2"] (exclamations, questions, humor patterns),
    "sample_lines": ["paraphrased example 1", "paraphrased example 2"] (safe paraphrased examples, NOT direct quotes),
    "confidence_score": 0.0-1.0 (how confident in the analysis)
}

Return ONLY valid JSON, no other text.
```

**Parameters:**
- Model: `gpt-4o`
- Temperature: `0.3` (low for consistency)
- Max Tokens: `500`
- Response Format: `json_object`

### Email Reply Processing Prompt

**System Message:**
```
You are an intelligent email assistant that processes user replies to motivational emails. Analyze the reply for urgency, sentiment, and actionable insights. Return ONLY valid JSON.
```

**User Prompt:**
```
Analyze this user reply to a motivational email:

User Reply: {reply_text}
Original Message Context: {original_message_context}
User Goals: {goals}
Streak: {streak_count}

Determine:
1. Urgency level (low|medium|high)
2. Sentiment (positive|neutral|negative|mixed)
3. Key topics mentioned
4. Actionable insights
5. Suggested response approach

Return ONLY valid JSON:
{
  "urgency": "low|medium|high",
  "sentiment": "positive|neutral|negative|mixed",
  "topics": ["topic1", "topic2"],
  "insights": ["insight1", "insight2"],
  "response_approach": "encouraging|problem-solving|celebratory|supportive"
}
```

---

## Email System

### Email Sending
- **Library**: `aiosmtplib` (async SMTP)
- **Rate Limiting**: Semaphore (15 concurrent sends max)
- **Retry Logic**: 3 retries with exponential backoff
- **Error Handling**: Comprehensive logging and fallback

### Email Templates
- HTML email templates with inline CSS
- Responsive design
- Interactive check-in sections
- Quick reply prompts
- Streak badges and achievements

### Email Reply Processing
- **IMAP Polling**: Every 1 minute
- **Processing**: Automatic reply analysis
- **Context**: Links replies to original messages
- **Storage**: `email_reply_conversations` collection

---

## Scheduling System

### APScheduler Configuration
- **Scheduler Type**: `AsyncIOScheduler`
- **Time Zone**: UTC (converted per user)
- **Job Storage**: In-memory (logged to database)

### Schedule Types
1. **Daily**: Send at specific times each day
2. **Weekly**: Send on specific days at specific times
3. **Monthly**: Send on specific dates

### Job Creation
- Jobs created per user per send time
- Jobs created per goal per send time
- Jobs rescheduled on schedule changes
- Jobs removed on user deactivation

### Batch Processing
- Processes users in batches of 100
- Pagination for 10k+ users
- Optimized job lookup (O(n) instead of O(n²))

---

## Activity Tracking & Logging

### Activity Types
- **User Actions**: `onboarding_completed`, `profile_updated`, `schedule_updated`, `personality_changed`, `feedback_submitted`, `message_viewed`
- **Admin Actions**: `admin_user_activated`, `admin_broadcast_sent`, `admin_user_deactivated`
- **System Events**: `scheduled_email_sent`, `email_job_completed`, `scheduler_job_started`, `llm_generation_failed`

### Logging Format
```python
logger.info(f"🎯 Action: {action_type} for {user_email}")
logger.debug(f"Details: {details}")
logger.error(f"❌ Error: {error_message}", exc_info=True)
```

### Log Collections
- `activity_logs` - User/admin activities
- `system_events` - System events
- `api_analytics` - API call analytics

---

## Admin Dashboard

### Features
- **Live Monitoring**: Real-time activity, API stats, system events
- **User Management**: View, activate/deactivate users, user details
- **Email History**: All email sends, status, errors
- **Logs Viewer**: Unified log viewer with filtering
- **Feedback Management**: All user feedback and ratings
- **Events Monitor**: System events and errors
- **Scheduler Status**: Job execution monitoring
- **Database Stats**: Collection counts and activity
- **Trends Analysis**: User growth, email trends, engagement
- **Global Search**: Search users, messages, feedback, logs
- **Broadcast**: Send messages to all active users
- **Achievements**: Manage achievement definitions

### Access
- Protected with `Authorization: Bearer {ADMIN_SECRET}` header
- Admin endpoints require `verify_admin` dependency

---

## User Dashboard

### Features
- **Overview**: Streak count, next email countdown, active goals, achievements
- **Analytics**: Average rating, engagement rate, favorite personality, message history
- **History**: All messages, ratings, feedback
- **Settings**: Profile, schedule, personalities, timezone
- **Goals**: Create, edit, delete goals
- **Achievements**: View unlocked achievements

---

## Scalability & Performance

### Optimizations for 10k+ Users
1. **Email Queue**: Semaphore limiting (15 concurrent sends)
2. **Batch Processing**: Process users in batches of 100
3. **Pagination**: All list endpoints support pagination
4. **MongoDB Connection Pool**: `maxPoolSize=100`, `minPoolSize=20`
5. **Optimized Queries**: Indexed fields, aggregation pipelines
6. **Job Lookup Optimization**: O(n) instead of O(n²)

### Performance Metrics
- **Email Send**: ~150ms average
- **Message Generation**: ~2-3s (OpenAI API)
- **Database Queries**: <50ms (indexed)
- **API Response Time**: <100ms average

---

## Security

### Rate Limiting
- Login: 5 requests/minute
- Generate Message: 10 requests/minute
- Send Now: 5 requests/minute
- Health Check: Exempt

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`

### Request Size Limits
- Max request size: 10MB
- Protects against DoS attacks

### Environment Validation
- Required variables validated on startup
- Missing variables cause startup failure
- Optional variables logged as warnings

---

## Deployment

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run build
# Serve build/ directory with web server
```

### Environment Setup
See [Environment Variables](#environment-variables) section

---

## Environment Variables

### Required
```bash
MONGO_URL=mongodb+srv://...
OPENAI_API_KEY=sk-...
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FRONTEND_URL=https://maketend.com
ADMIN_SECRET=your-secure-admin-secret
```

### Optional
```bash
DB_NAME=tend
TAVILY_API_KEY=your-tavily-key (for research)
IMAP_HOST=imap.gmail.com (for email replies)
INBOX_EMAIL=your-inbox@gmail.com
INBOX_PASSWORD=your-app-password
CLERK_PUBLISHABLE_KEY=pk_... (frontend)
CLERK_SECRET_KEY=sk_... (backend, if needed)
```

---

## Constants & Configuration

### Message Types
- `motivational_story`
- `action_challenge`
- `mindset_shift`
- `accountability_prompt`
- `celebration_message`
- `real_world_example`

### Personality Blueprints
- Famous: Scene-based openings, unexpected insights
- Tone: Emotion check-ins, vivid images
- Custom: Heartfelt acknowledgements, fresh metaphors

### Emotional Arcs
- Spark curiosity → Reflect journey → Deliver action
- Recognize win → Surface friction → Offer reframe
- Empathize pace → Surprising observation → Confident move

### Achievement Definitions
- Streak-based: `first_streak` (3 days), `week_warrior` (7 days), `month_master` (30 days), `century_club` (100 days)
- Message-based: `message_milestone_10`, `message_milestone_50`, `message_milestone_100`
- Feedback-based: `feedback_enthusiast` (10 ratings), `feedback_champion` (50 ratings)

---

## Data Flow

### User Onboarding Flow
1. User signs in with Clerk
2. Frontend syncs Clerk data → `POST /api/auth/clerk-sync`
3. User completes onboarding → `POST /api/onboarding`
4. Backend saves user data → `users` collection
5. Backend schedules emails → APScheduler jobs
6. Backend logs activity → `activity_logs` collection

### Message Generation Flow
1. Scheduler triggers job → `send_motivation_to_user(email)`
2. Get user data → `users` collection
3. Get current personality → Rotation logic
4. Generate message → OpenAI GPT-4o
5. Generate subject → OpenAI GPT-4o-mini
6. Send email → SMTP
7. Save to history → `message_history` collection
8. Update streak → `users` collection
9. Log activity → `activity_logs` collection

### Email Reply Flow
1. IMAP polling → `poll_email_replies()` every 1 minute
2. Find unread replies → IMAP inbox
3. Verify user → `users` collection
4. Process reply → Analyze with OpenAI
5. Store conversation → `email_reply_conversations` collection
6. Generate response (optional) → OpenAI
7. Send response (optional) → SMTP

---

## Version History System

### Schedule History
- Every schedule change saved to `schedule_history`
- Version numbers increment
- Only latest version is active
- Complete history preserved

### Personality History
- Every personality change saved to `personality_history`
- Version tracking
- Complete history preserved

### Profile History
- Every profile update saved to `profile_history`
- Change details tracked
- Complete history preserved

---

## Error Handling

### LLM Generation Failures
- Fallback to default message
- Logged to `system_events`
- User receives default message

### Email Send Failures
- 3 retries with exponential backoff
- Logged to `email_logs`
- Error messages stored

### Database Errors
- Comprehensive error logging
- Graceful degradation
- User-friendly error messages

---

## Testing

See `test_all_features.py` for comprehensive testing script.

---

## Support & Maintenance

### Monitoring
- Health check endpoint: `GET /api/health`
- Admin dashboard logs viewer
- System events monitoring

### Debugging
- Comprehensive logging to stdout
- Activity logs in database
- API analytics for performance monitoring

---

**Last Updated**: 2024-01-05
**Version**: 1.0.0
**Status**: Production Ready

