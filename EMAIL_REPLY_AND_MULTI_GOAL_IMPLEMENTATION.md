# Email Reply & Multi-Goal Implementation Summary

## ✅ Implementation Complete

### Part 1: Email Reply Conversation System

#### 1. Database Models Added
- **`EmailReplyConversation`** - Stores user replies with LLM-extracted insights
- **`EmailReplyAnalysis`** - LLM analysis results structure
- **Updated `MessageHistory`** - Added reply tracking fields
- **Updated `UserProfile`** - Added reply engagement tracking

#### 2. Email Reply Handler (`backend/email_reply_handler.py`)
- **`poll_email_replies()`** - Polls inbox every 10 minutes for user replies
- **`process_user_reply()`** - Analyzes replies using LLM to extract:
  - Sentiment (positive, neutral, struggling, confused, excited)
  - Wins, struggles, questions
  - Preferred tone shifts
  - Continuity notes for next email
  - Urgency level
- **`send_immediate_encouragement()`** - Sends quick supportive email if user is struggling

#### 3. Message Generation Integration
- **Updated `generate_goal_message()`** to:
  - Fetch last 2 user replies
  - Include reply context in LLM prompt
  - Reference user's wins, struggles, and questions naturally
  - Mark replies as used in next message
  - Save conversation context to message history

#### 4. API Endpoints Added
- `GET /users/{email}/replies` - Get all user replies
- `GET /users/{email}/reply-insights` - Get aggregated insights
- `GET /admin/reply-analytics` - Admin analytics across all users

#### 5. Scheduler Integration
- Email reply polling job runs every 10 minutes
- Automatically processes new replies and sends immediate responses if urgent

---

### Part 2: Multiple Goals with Multiple Frequencies

#### 1. Enhanced Goal Schema
- **`GoalSchedule`** now supports:
  - `times: List[str]` - Multiple times per day (e.g., ["07:00", "12:00", "18:00"])
  - `schedule_name` - Optional name for each schedule
  - `id` - Unique identifier for each schedule
- **`GoalCreateRequest`** supports:
  - Up to 10 schedules per goal
  - `category` - Goal categorization
  - `priority` - high/medium/low

#### 2. Enhanced Scheduling Logic
- **`calculate_next_send_times()`** now handles:
  - Multiple times per day for daily schedules
  - Multiple times per day for weekly schedules
  - Multiple times per day for monthly schedules
- **`schedule_goal_jobs_for_goal()`** now:
  - Handles multiple schedules per goal
  - Tracks schedule_id and schedule_name in goal_messages
  - Creates separate jobs for each schedule and time

#### 3. Goal Creation Validation
- Max 10 active goals per user
- Max 10 schedules per goal
- Proper validation for mode-specific fields

#### 4. Database Indexes
- Reply conversation indexes for fast queries
- Enhanced goal indexes for multi-goal support
- Goal message indexes with schedule_id

---

## 🔧 Configuration Required

### Environment Variables

Add these to your `.env` file:

```env
# Email Reply Polling (IMAP)
IMAP_HOST=imap.gmail.com
INBOX_EMAIL=your-inbox@gmail.com
INBOX_PASSWORD=your-app-password
```

**Note:** For Gmail, you'll need to:
1. Enable 2-factor authentication
2. Generate an App Password (not your regular password)
3. Use the app password in `INBOX_PASSWORD`

### Dependencies

Install new dependencies:

```bash
pip install imap-tools beautifulsoup4
```

(httpx should already be installed if you're using OpenAI)

---

## 📊 How It Works

### Email Reply Flow

1. **User receives email** at 7am: "Day 5: Keep pushing forward..."
2. **User replies**: "Managed to do 30 mins. Feeling overwhelmed about next steps."
3. **System (within 10 mins)**:
   - Analyzes reply with LLM
   - Extracts: sentiment=struggling, struggles=["overwhelmed", "next steps unclear"]
   - Stores in `email_reply_conversations` collection
   - If urgent, sends immediate supportive response
4. **Next day's email (7am)**:
   - Includes reply context in prompt
   - References their struggle: "You mentioned feeling overwhelmed yesterday after that 30-minute session..."
   - Provides actionable help
   - Feels like a real conversation!

### Multiple Goals Flow

1. **User creates 3 goals**:
   - Goal 1: "Fitness" - Daily 6am + 12pm + 6pm energetic emails
   - Goal 2: "Career" - Weekly Mon+Fri 9am professional emails
   - Goal 3: "Learning" - Monthly 1st 8am philosophical emails

2. **System schedules all automatically**:
   - Creates separate jobs for each schedule and time
   - Tracks which schedule each message belongs to

3. **User receives**:
   - Every day at 6am, 12pm, 6pm: Fitness motivation
   - Mon+Fri at 9am: Career guidance
   - 1st of month at 8am: Deep learning reflection

4. **Each email is contextual**:
   - References goal-specific content
   - Incorporates any replies for that goal
   - Uses goal-specific personality/tone

---

## 🎯 Key Features

### Email Reply System
- ✅ Automatic reply polling (every 10 minutes)
- ✅ LLM-powered sentiment analysis
- ✅ Win/struggle/question extraction
- ✅ Immediate encouragement for struggling users
- ✅ Reply context in next day's email
- ✅ Conversation continuity tracking
- ✅ Engagement rate calculation

### Multiple Goals System
- ✅ Up to 10 active goals per user
- ✅ Up to 10 schedules per goal
- ✅ Multiple times per day per schedule
- ✅ Different frequencies (daily, weekly, monthly, custom)
- ✅ Goal categories and priorities
- ✅ Schedule names for organization
- ✅ Event-driven scheduling (no polling)

---

## 📝 API Usage Examples

### Create Goal with Multiple Times Per Day

```bash
POST /users/{email}/goals
{
  "title": "Fitness Journey",
  "description": "Daily fitness motivation",
  "mode": "tone",
  "tone": "energetic & enthusiastic",
  "schedules": [
    {
      "type": "daily",
      "times": ["07:00", "12:00", "18:00"],
      "timezone": "America/New_York",
      "active": true,
      "schedule_name": "Morning + Lunch + Evening"
    }
  ],
  "active": true
}
```

### Get User Reply Insights

```bash
GET /users/{email}/reply-insights

Response:
{
  "user_email": "user@example.com",
  "total_replies": 15,
  "sentiment_distribution": {
    "positive": 8,
    "struggling": 4,
    "neutral": 3
  },
  "total_wins_mentioned": 12,
  "total_struggles_mentioned": 6,
  "top_topics": [
    {"topic": "workout consistency", "count": 5},
    {"topic": "time management", "count": 3}
  ],
  "engagement_rate": 45.5
}
```

---

## 🚀 Next Steps

1. **Install dependencies**: `pip install imap-tools beautifulsoup4`
2. **Configure IMAP credentials** in `.env`
3. **Test email reply polling** by sending a test reply
4. **Create goals with multiple schedules** via API
5. **Monitor reply analytics** via admin dashboard

---

## ⚠️ Important Notes

- **IMAP is optional**: If not configured, reply polling will be disabled (graceful degradation)
- **Multiple times per day**: The `times` array takes precedence over single `time` field
- **Backward compatibility**: Single `time` field still works for existing goals
- **Rate limits**: System respects `send_limit_per_day` per goal
- **Reply processing**: Replies are processed asynchronously, may take up to 10 minutes

---

## 🎉 Result

You now have a **TRULY CONVERSATIONAL, HIGHLY PERSONALIZED email experience** where:
- Users can reply and the system learns from feedback
- Multiple goals with multiple frequencies are fully supported
- Each email feels like a real conversation, not a monologue
- The system adapts based on user feedback and engagement

