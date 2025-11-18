# InboxInspire - Complete Features & Options Reference

## 📋 Table of Contents
1. [Authentication & User Management](#authentication--user-management)
2. [Personality Options](#personality-options)
3. [Schedule & Frequency Options](#schedule--frequency-options)
4. [Goal Management Features](#goal-management-features)
5. [Message Features](#message-features)
6. [Analytics & Tracking](#analytics--tracking)
7. [Achievement System](#achievement-system)
8. [Admin Features](#admin-features)
9. [API Endpoints](#api-endpoints)
10. [Configuration Options](#configuration-options)

---

## 🔐 Authentication & User Management

### Authentication Methods
- **Magic Link Authentication** (Passwordless)
  - Email-based login
  - Secure token verification
  - 1-hour token expiration

### User Profile Options
- **Name**: User's display name
- **Email**: Primary identifier
- **Goals**: Free-form text describing aspirations
- **User Timezone**: IANA timezone string (e.g., "America/New_York", "Asia/Kolkata")
- **Active Status**: Enable/disable account
- **Last Active**: Timestamp tracking

### Onboarding Flow (4 Steps)
1. **Name Collection**
2. **Goals & Aspirations** (Free-form text)
3. **Personality Selection** (Multiple personalities can be selected)
4. **Schedule Configuration** (Frequency, times, timezone)

---

## 🎭 Personality Options

### Personality Types

#### 1. Famous Personalities (19 options)
**Indian Icons (10):**
- A.P.J. Abdul Kalam
- Ratan Tata
- Sadhguru
- M.S. Dhoni
- Swami Vivekananda
- Sudha Murty
- Sachin Tendulkar
- Shah Rukh Khan
- Narayana Murthy
- Kiran Mazumdar-Shaw

**Indian-Origin Tech Leaders (2):**
- Sundar Pichai
- Satya Nadella

**International Icons (7):**
- Elon Musk
- Mark Zuckerberg
- Oprah Winfrey
- Nelson Mandela
- Tony Robbins
- Michelle Obama
- Denzel Washington

#### 2. Tone/Style Options (11 options)
- Funny & Uplifting
- Friendly & Warm
- Tough Love & Real Talk
- Serious & Direct
- Philosophical & Reflective
- Energetic & Enthusiastic
- Calm & Meditative
- Poetic & Artistic
- Sarcastic & Witty
- Coach-Like & Accountability
- Storytelling & Narrative

#### 3. Custom Personalities
- User-defined via AI conversation
- Research-backed personality profiles
- Custom personality profiles stored per user
- Can be assigned to specific goals

### Personality Rotation Modes (6 options)
1. **Sequential**: Rotate through personalities in order
2. **Random**: Randomly select from available personalities
3. **Daily Fixed**: Same personality for entire day
4. **Weekly Rotation**: Different personality each day of week
5. **Favorite Weighted**: Prioritize personalities with higher ratings
6. **Time Based**: Different personality based on time of day

### Personality Management
- Add multiple personalities
- Remove personalities
- Set active personality
- View personality history
- Track personality usage statistics

---

## ⏰ Schedule & Frequency Options

### Schedule Frequency Types (4 options)
1. **Daily**: Every day at specified time(s)
2. **Weekly**: On specific days of the week
3. **Monthly**: On specific dates of the month
4. **Custom**: Every N days with custom interval

### Schedule Configuration Options
- **Times**: Multiple send times per day (e.g., ["09:00", "15:00", "20:00"])
- **Timezone**: IANA timezone string (35+ supported timezones)
- **Weekdays**: Specific days (0-6, Monday=0, Sunday=6)
- **Monthly Dates**: Specific dates of month (1-31)
- **Custom Interval**: Every N days
- **Start Date**: Optional schedule start date
- **End Date**: Optional schedule end date
- **Paused**: Temporarily pause schedule
- **Skip Next**: Skip the next scheduled send

### Time Window Options
- **Send Time Windows**: Up to 5 time windows per schedule
  - Start time (HH:MM format)
  - End time (HH:MM format)
  - Timezone per window
  - Max sends per window (1-50)

### Schedule Actions
- **Pause**: Temporarily stop all scheduled emails
- **Resume**: Restart paused schedule
- **Skip Next**: Skip the next scheduled email
- **Edit Schedule**: Modify frequency, times, timezone
- **View Schedule History**: See past schedule changes

---

## 🎯 Goal Management Features

### Goal Creation Options
- **Title**: Goal name (1-200 characters)
- **Description**: Detailed description (up to 2000 characters)
- **Mode**: 
  - Personality mode (use famous personality)
  - Tone mode (use tone/style)
  - Custom mode (use custom personality or text)
- **Personality Selection**: Choose specific personality for goal
- **Custom Personality ID**: Assign custom personality profile
- **Category**: Goal category (e.g., "Fitness", "Career", "Learning")
- **Priority**: High, Medium, Low
- **Active Status**: Enable/disable goal

### Goal Schedule Options
- **Multiple Schedules**: Up to 10 schedules per goal
- **Schedule Name**: Custom name for each schedule (e.g., "Morning Motivation")
- **Schedule Type**: Daily, Weekly, Monthly, Custom
- **Multiple Times**: Multiple send times per schedule
- **Send Limit Per Day**: 1-20 emails per day
- **Time Windows**: Up to 5 time windows per goal
- **Start/End Dates**: Date range for goal schedule

### Goal Progress Tracking
- **Progress Status**: Track completion status
- **Progress Updates**: Manual progress updates
- **Goal History**: View all messages sent for goal
- **Progress Analytics**: Completion statistics

### Goal Actions
- **Create Goal**: Add new goal with schedules
- **Update Goal**: Modify goal details and schedules
- **Delete Goal**: Remove goal (soft delete)
- **View Goal History**: See all messages for goal
- **View Goal Progress**: Track completion status

---

## 💬 Message Features

### Message Types (6 types)
1. **Motivational Story**: Real examples of overcoming challenges
2. **Action Challenge**: Specific task to accomplish today
3. **Mindset Shift**: Reframe thinking about obstacles
4. **Accountability Prompt**: Check progress and create urgency
5. **Celebration Message**: Recognize recent progress
6. **Real World Example**: Concrete analogies from business/sports/life

### Message Generation Features
- **AI-Powered**: GPT-4o model
- **Anti-Repetition**: Tracks recent messages to avoid repetition
- **Context-Aware**: Uses streak, goals, and message history
- **Personality Voice Matching**: Deep personality research integration
- **Subject Line Generation**: AI-generated compelling subjects
- **Fallback Subject Lines**: Deterministic fallbacks if AI unavailable

### Message Delivery Options
- **Scheduled Delivery**: Automatic based on user schedule
- **Instant Send**: On-demand motivation from dashboard
- **Goal-Based Messages**: Goal-specific content
- **Email Threading**: Proper reply-to headers for conversations

### Message Interaction Features
- **Message History**: View all sent messages
- **Message Feedback**: Rate messages (1-5 stars)
- **Favorite Messages**: Mark messages as favorites
- **Message Collections**: Organize messages into collections
- **Message Export**: Export message history (JSON/CSV)
- **Message Search**: Search through message history

### Message Content Features
- **Interactive Check-In**: Thoughtful questions tied to goals
- **Quick Reply Prompt**: Actionable reply instructions
- **Streak Integration**: Streak count in message header
- **HTML Email Templates**: Beautiful styled emails
- **Plain Text Fallback**: Text version for email clients

---

## 📊 Analytics & Tracking

### User Analytics
- **Streak Count**: Consecutive days of receiving emails
- **Total Messages**: Total messages received
- **Favorite Personality**: Most used personality
- **Average Rating**: Average message rating
- **Last Active**: Last activity timestamp
- **Engagement Rate**: Percentage of emails replied to
- **Personality Stats**: Usage statistics per personality

### Analytics Views
- **Weekly Reports**: 7-day analytics summary
- **Monthly Reports**: 30-day analytics summary
- **Streak Calendar**: GitHub-style contribution calendar
- **Streak Milestones**: Visual milestone tracking
- **Message History**: Complete message log with filters
- **Reply Insights**: Email reply analytics

### Activity Tracking
- **User Actions**: Login, profile updates, message interactions
- **System Events**: Scheduled emails, job executions
- **API Analytics**: Endpoint performance tracking
- **Page Views**: Frontend page view tracking
- **Session Tracking**: User session duration and actions

### Export Options
- **Message History Export**: JSON/CSV format
- **Achievements Export**: Achievement data export
- **Analytics Export**: Analytics data export

---

## 🏆 Achievement System

### Achievement Categories
1. **Streak Achievements**: Based on consecutive days
2. **Message Achievements**: Based on total messages received
3. **Engagement Achievements**: Based on feedback/ratings
4. **Goal Achievements**: Based on goal completion
5. **Consistency Achievements**: Based on consecutive days
6. **Loyalty Achievements**: Based on account age

### Available Achievements (20 total)

#### Streak Achievements
- **Getting Started**: 3-day streak
- **Week Warrior**: 7-day streak
- **Month Master**: 30-day streak
- **Century Club**: 100-day streak
- **Streak Legend**: 365-day streak

#### Message Achievements
- **First Step**: Receive first message
- **Message Collector**: Receive 50 messages
- **Century Messages**: Receive 100 messages
- **Message Milestone**: Receive 250 messages
- **Message Architect**: Receive 500 messages

#### Engagement Achievements
- **Feedback Enthusiast**: Rate 10 messages
- **Feedback Master**: Rate 25 messages
- **Top Rated**: Give 5-star rating to 10 messages

#### Goal Achievements
- **Goal Setter**: Set your first goal
- **Goal Achiever**: Complete a goal
- **Goal Crusher**: Complete 5 goals

#### Consistency Achievements
- **Early Bird**: Receive messages for 5 consecutive days
- **Dedicated Learner**: Receive messages for 14 consecutive days

#### Other Achievements
- **Personality Explorer**: Try 3 different personalities
- **Loyal Member**: Active for 6 months
- **Veteran**: Active for 1 year

### Achievement Features
- **Auto-Unlock**: Automatic achievement detection
- **Achievement History**: Track when achievements were unlocked
- **Achievement Display**: Show on home dashboard
- **Achievement Categories**: Organize by category
- **Achievement Icons**: Visual icons for each achievement

---

## 👨‍💼 Admin Features

### Admin Authentication
- **Bearer Token**: Admin secret token authentication
- **Protected Endpoints**: All admin endpoints require authentication

### User Management
- **View All Users**: List all registered users
- **User Details**: Detailed user profile view
- **User Search**: Search users by email/name
- **User Segments**: Segment users by criteria
- **Bulk User Actions**: 
  - Activate/Deactivate users
  - Pause/Resume schedules
  - Delete users
- **User Journey**: View complete user activity timeline
- **User History**: View profile, schedule, personality history

### Email Management
- **Email Logs**: View all email delivery logs
- **Email Statistics**: Delivery success rates
- **Advanced Email Logs**: Filtered email log views
- **Email Performance**: Email delivery analytics
- **Bulk Email**: Send emails to multiple users
- **Broadcast**: Send broadcast messages

### Analytics & Reporting
- **Platform Statistics**: Total users, active users, emails sent
- **Email Statistics**: Delivery statistics by time period
- **User Activity Summary**: Most active users
- **Content Performance**: Message performance metrics
- **API Costs**: Track API usage costs
- **Real-Time Analytics**: Live platform statistics
- **Trend Analytics**: User and engagement trends
- **System Events**: System-level event logs
- **API Performance**: Endpoint performance metrics

### Achievement Management
- **View All Achievements**: List all achievements
- **Create Achievement**: Add new achievement
- **Update Achievement**: Modify achievement details
- **Delete Achievement**: Remove achievement
- **Assign Achievement**: Manually assign to user
- **Remove Achievement**: Remove from user
- **Bulk Assign**: Assign to all users
- **Bulk Remove**: Remove from all users
- **Initialize Achievements**: Reset achievement database
- **Recalculate Streaks**: Recalculate all user streaks

### Scheduler Management
- **View Jobs**: List all scheduled jobs
- **Trigger Job**: Manually trigger scheduled job
- **Job Status**: Check job execution status

### Database Management
- **Database Health**: Check database connection and indexes
- **Deleted Data**: View soft-deleted data
- **Restore Data**: Restore deleted data
- **Data Preservation**: Version tracking system

### Content Management
- **Persona Research**: View personality research data
- **Refresh Research**: Update personality research
- **Research Logs**: View research activity logs
- **Message History**: Admin view of all messages

### Alert System
- **Alert Configuration**: Configure system alerts
- **Alert History**: View alert logs

### Search & Filter
- **Admin Search**: Search across users, messages, logs
- **Advanced Filters**: Filter by date, status, type

---

## 🔌 API Endpoints

### Authentication Endpoints
- `GET /api/` - Health check
- `POST /api/auth/login` - Send magic link
- `POST /api/auth/verify` - Verify token

### User Endpoints
- `POST /api/onboarding` - Complete onboarding
- `GET /api/users/{email}` - Get user profile
- `PUT /api/users/{email}` - Update user profile
- `GET /api/users/{email}/streak-status` - Get streak status
- `POST /api/users/{email}/recalculate-streak` - Recalculate streak
- `GET /api/users/{email}/analytics` - Get user analytics
- `GET /api/users/{email}/analytics/weekly` - Weekly analytics
- `GET /api/users/{email}/analytics/monthly` - Monthly analytics
- `PUT /api/users/{email}/preferences` - Update preferences
- `GET /api/users/{email}/preferences` - Get preferences

### Personality Endpoints
- `GET /api/famous-personalities` - List famous personalities
- `GET /api/tone-options` - List tone options
- `POST /api/users/{email}/personalities` - Add personality
- `DELETE /api/users/{email}/personalities/{personality_id}` - Remove personality
- `POST /api/users/{email}/custom-personality/start` - Start custom personality creation
- `POST /api/users/{email}/custom-personality/chat` - Custom personality chat
- `POST /api/users/{email}/custom-personality/research` - Research personality
- `POST /api/users/{email}/custom-personality/confirm` - Confirm custom personality
- `GET /api/users/{email}/custom-personalities` - List custom personalities
- `DELETE /api/users/{email}/custom-personalities/{personality_id}` - Delete custom personality

### Schedule Endpoints
- `POST /api/users/{email}/schedule/pause` - Pause schedule
- `POST /api/users/{email}/schedule/resume` - Resume schedule
- `POST /api/users/{email}/schedule/skip-next` - Skip next email
- `POST /api/test-schedule/{email}` - Test schedule

### Goal Endpoints
- `POST /api/users/{email}/goals` - Create goal
- `GET /api/users/{email}/goals` - List goals
- `GET /api/users/{email}/goals/{goal_id}` - Get goal details
- `PUT /api/users/{email}/goals/{goal_id}` - Update goal
- `DELETE /api/users/{email}/goals/{goal_id}` - Delete goal
- `GET /api/users/{email}/goals/{goal_id}/history` - Goal message history
- `POST /api/users/{email}/goals/progress` - Update goal progress
- `GET /api/users/{email}/goals/progress` - Get goal progress

### Message Endpoints
- `POST /api/generate-message` - Generate preview message
- `POST /api/send-now/{email}` - Send instant message
- `GET /api/users/{email}/message-history` - Get message history
- `POST /api/users/{email}/feedback` - Submit message feedback
- `POST /api/users/{email}/messages/{message_id}/favorite` - Favorite message
- `GET /api/users/{email}/messages/favorites` - Get favorite messages
- `GET /api/users/{email}/export/messages` - Export messages

### Message Collections
- `POST /api/users/{email}/collections` - Create collection
- `GET /api/users/{email}/collections` - List collections
- `PUT /api/users/{email}/collections/{collection_id}` - Update collection
- `DELETE /api/users/{email}/collections/{collection_id}` - Delete collection

### Achievement Endpoints
- `GET /api/users/{email}/achievements` - Get user achievements

### Reply Endpoints
- `GET /api/users/{email}/replies` - Get email replies
- `GET /api/users/{email}/reply-insights` - Get reply analytics

### Check-in & Reflection Endpoints
- `POST /api/users/{email}/check-ins` - Submit check-in
- `GET /api/users/{email}/check-ins` - Get check-ins
- `POST /api/users/{email}/reflections` - Submit reflection
- `GET /api/users/{email}/reflections` - Get reflections

### Community Endpoints
- `GET /api/community/stats` - Community statistics
- `GET /api/community/message-insights/{message_id}` - Message insights

### Unsubscribe
- `POST /api/unsubscribe` - Unsubscribe from emails

### Admin Endpoints (All require Bearer token)
- `GET /api/admin/users` - List all users
- `GET /api/admin/users/{email}/details` - User details
- `PUT /api/admin/users/{email}` - Update user (admin)
- `DELETE /api/admin/users/{email}` - Delete user
- `POST /api/admin/users/bulk-update` - Bulk update users
- `GET /api/admin/stats` - Platform statistics
- `GET /api/admin/email-logs` - Email logs
- `GET /api/admin/email-logs/advanced` - Advanced email logs
- `GET /api/admin/email-statistics` - Email statistics
- `GET /api/admin/feedback` - All feedback
- `GET /api/admin/message-history` - All message history
- `GET /api/admin/search` - Admin search
- `GET /api/admin/users/segments` - User segments
- `GET /api/admin/analytics/trends` - Trend analytics
- `GET /api/admin/api-costs` - API costs
- `GET /api/admin/alerts` - Alerts
- `GET /api/admin/scheduler/jobs` - Scheduler jobs
- `POST /api/admin/scheduler/jobs/{job_id}/trigger` - Trigger job
- `GET /api/admin/database/health` - Database health
- `POST /api/admin/broadcast` - Broadcast message
- `POST /api/admin/bulk/users` - Bulk user actions
- `POST /api/admin/bulk/email` - Bulk email
- `GET /api/admin/user-activity-summary` - User activity summary
- `GET /api/admin/content-performance` - Content performance
- `POST /api/admin/persona-research/{persona_id}/refresh` - Refresh research
- `GET /api/admin/persona-research/{persona_id}` - Get research
- `GET /api/admin/persona-research` - List research
- `GET /api/admin/research-logs` - Research logs
- `GET /api/admin/user-journey/{email}` - User journey
- `GET /api/admin/errors` - Error logs
- `GET /api/admin/deleted-data` - Deleted data
- `GET /api/admin/achievements` - List achievements
- `POST /api/admin/achievements` - Create achievement
- `PUT /api/admin/achievements/{achievement_id}` - Update achievement
- `DELETE /api/admin/achievements/{achievement_id}` - Delete achievement
- `POST /api/admin/users/{email}/achievements/{achievement_id}` - Assign achievement
- `DELETE /api/admin/users/{email}/achievements/{achievement_id}` - Remove achievement
- `GET /api/admin/users/{email}/achievements` - User achievements
- `POST /api/admin/achievements/initialize` - Initialize achievements
- `POST /api/admin/achievements/recalculate-streaks` - Recalculate streaks
- `POST /api/admin/achievements/{achievement_id}/assign-all` - Assign to all
- `POST /api/admin/achievements/{achievement_id}/remove-all` - Remove from all
- `POST /api/admin/restore/{deletion_id}` - Restore data
- `GET /api/users/{email}/history/schedule` - Schedule history
- `GET /api/users/{email}/history/personalities` - Personality history
- `GET /api/users/{email}/history/profile` - Profile history
- `GET /api/users/{email}/history/complete` - Complete history
- `POST /api/admin/test-email-polling` - Test email polling
- `GET /api/admin/reply-analytics` - Reply analytics

### Analytics Endpoints (Admin)
- `GET /api/analytics/realtime` - Real-time analytics
- `GET /api/analytics/user-timeline/{email}` - User timeline
- `GET /api/analytics/activity-logs` - Activity logs
- `GET /api/analytics/system-events` - System events
- `GET /api/analytics/api-performance` - API performance
- `GET /api/analytics/page-views` - Page views
- `GET /api/analytics/active-sessions` - Active sessions

### Tracking Endpoints
- `POST /api/tracking/page-view` - Track page view
- `POST /api/tracking/user-action` - Track user action
- `POST /api/tracking/session/start` - Start session
- `PUT /api/tracking/session/{session_id}` - Update session

---

## ⚙️ Configuration Options

### Environment Variables

#### Database Configuration
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name (default: "inbox_inspire")

#### OpenAI Configuration
- `OPENAI_API_KEY` - OpenAI API key (required)

#### Email Configuration (SMTP)
- `SMTP_HOST` - SMTP server hostname
- `SMTP_PORT` - SMTP port (465 for SSL, 587 for STARTTLS)
- `SMTP_USERNAME` - SMTP username
- `SMTP_PASSWORD` - SMTP password
- `SENDER_EMAIL` - From email address

#### Email Reply Configuration (IMAP)
- `IMAP_HOST` - IMAP server hostname
- `INBOX_EMAIL` - Email address to check for replies
- `INBOX_PASSWORD` - Email password for IMAP

#### Research Configuration (Optional)
- `TAVILY_API_KEY` - Tavily API key for personality research

#### Admin Configuration
- `ADMIN_SECRET` - Admin authentication token

#### Frontend Configuration
- `FRONTEND_URL` - Frontend application URL
- `CORS_ORIGINS` - CORS allowed origins (use "*" for all)

### Application Settings

#### Message Generation Settings
- **Model**: GPT-4o
- **Temperature**: 0.9 (high creativity)
- **Max Tokens**: 500
- **Presence Penalty**: 0.6 (avoid repetition)
- **Frequency Penalty**: 0.6 (encourage variety)

#### Email Settings
- **Retry Logic**: 3 attempts with exponential backoff
- **Retry Delays**: 2s, 5s, 10s
- **Connection Timeout**: 30 seconds
- **Email Polling**: Every 1 minute (if IMAP configured)

#### Schedule Settings
- **Max Schedules per Goal**: 10
- **Max Times per Schedule**: Unlimited
- **Max Time Windows**: 5 per schedule
- **Max Sends per Window**: 1-50
- **Send Limit per Day**: 1-20 per goal

#### Streak Settings
- **Streak Calculation**: Backward-counting from most recent email
- **Minimum Streak**: 1 day
- **Streak Reset**: If gap > 1 day

#### Achievement Settings
- **Auto-Unlock**: Enabled
- **Achievement Categories**: 6 categories
- **Total Achievements**: 20 default achievements

---

## 📱 Frontend Features

### Dashboard Tabs
1. **Home**: Overview, streak, recent messages
2. **Goals**: Goal management interface
3. **Messages**: Message history and favorites
4. **Analytics**: User analytics and reports
5. **Settings**: Profile and preferences

### UI Components
- **Shadcn UI**: Complete component library
- **Responsive Design**: Mobile and desktop support
- **Dark Mode**: Theme support (via next-themes)
- **Toast Notifications**: User feedback
- **Loading States**: Skeleton loaders
- **Error Boundaries**: Error handling
- **Network Status**: Connection monitoring

### User Interface Features
- **Streak Calendar**: GitHub-style contribution calendar
- **Achievement Celebrations**: Animated achievement unlocks
- **Message Preview**: Preview before sending
- **Instant Send**: Quick motivation button
- **Personality Manager**: Add/remove personalities
- **Schedule Manager**: Configure schedule settings
- **Goals Manager**: Create and manage goals
- **Analytics Dashboard**: Visual analytics
- **Export Options**: Data export functionality

---

## 🔄 System Features

### Background Jobs
- **Daily Email Scheduler**: Sends scheduled emails
- **Goal Message Scheduler**: Sends goal-based messages
- **Email Reply Polling**: Checks for email replies (every 1 minute)
- **Streak Recalculation**: Admin-triggered streak updates

### Data Management
- **Version Tracking**: Track data changes
- **Soft Deletes**: Preserve deleted data
- **Data Restoration**: Restore deleted data
- **Activity Logging**: Comprehensive activity tracking

### Email Features
- **HTML Templates**: Beautiful email templates
- **Email Threading**: Proper reply-to headers
- **Unsubscribe Links**: Compliance headers
- **Email Logging**: Track all email sends
- **Retry Logic**: Automatic retry on failure

### Security Features
- **Magic Link Tokens**: Cryptographically secure
- **Admin Authentication**: Bearer token protection
- **CORS Configuration**: Configurable origins
- **Data Sanitization**: Input sanitization
- **Error Handling**: Comprehensive error handling

---

## 📈 Statistics & Metrics

### User Metrics
- Total users
- Active users
- Inactive users
- New users (time period)
- User retention rate

### Email Metrics
- Total emails sent
- Successful deliveries
- Failed deliveries
- Success rate percentage
- Emails by personality
- Emails by time period

### Engagement Metrics
- Average rating
- Total feedback submissions
- Reply rate
- Favorite messages count
- Collection count

### Goal Metrics
- Total goals created
- Active goals
- Completed goals
- Goals by category
- Average goals per user

### Streak Metrics
- Average streak length
- Longest streak
- Users with active streaks
- Streak distribution

---

## 🎨 Customization Options

### Content Customization
- **Custom Personalities**: Create via AI conversation
- **Custom Text**: Free-form custom messages
- **Goal-Specific Content**: Tailored to each goal
- **Message Variety**: 6 different message types

### Schedule Customization
- **Multiple Times**: Multiple sends per day
- **Time Windows**: Specific time ranges
- **Custom Frequencies**: Every N days
- **Date Ranges**: Start and end dates

### Display Customization
- **Timezone Display**: User's local timezone
- **Date Formatting**: Timezone-aware formatting
- **Theme Support**: Light/dark mode

---

## 📝 Summary

### Total Counts
- **Personality Options**: 30 (19 famous + 11 tones)
- **Rotation Modes**: 6
- **Schedule Frequencies**: 4
- **Message Types**: 6
- **Achievements**: 20
- **API Endpoints**: 100+
- **Supported Timezones**: 35+
- **Goal Schedules per Goal**: Up to 10
- **Times per Schedule**: Unlimited
- **Time Windows**: Up to 5 per schedule

### Feature Categories
- **User Features**: 15+ major features
- **Admin Features**: 25+ major features
- **Analytics Features**: 10+ features
- **Goal Features**: 10+ features
- **Message Features**: 10+ features

This comprehensive system provides a complete motivational email platform with extensive customization, analytics, and management capabilities.

