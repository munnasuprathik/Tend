# InboxInspire - Comprehensive Activity Tracking System

## Overview
InboxInspire now tracks **EVERY user interaction**, system event, and API call in real-time using MongoDB Atlas.

---

## 🔗 MongoDB Atlas Connection

**Status**: ✅ Connected to Production Database

- **Database**: `inboxinspire_production`
- **Cluster**: `inboxinspire.gbxbqqj.mongodb.net`
- **Connection**: Secure MongoDB Atlas cluster with automatic backups

---

## 📊 What's Being Tracked

### 1. **User Activities** (`activity_logs` collection)
Every user action is logged with:
- Action type (login, profile_update, email_sent, etc.)
- User email
- Timestamp (with timezone)
- IP address
- User agent (browser/device info)
- Session ID
- Custom details (JSON object)

**Examples of tracked actions:**
- ✅ Login attempts (successful/failed)
- ✅ Profile updates
- ✅ Personality changes
- ✅ Schedule modifications
- ✅ Feedback submissions
- ✅ Message views
- ✅ Settings changes

### 2. **Admin Activities** (`activity_logs` collection)
All admin actions logged:
- ✅ Admin logins
- ✅ User management (activate/deactivate)
- ✅ Test emails sent
- ✅ Data exports/views
- ✅ Configuration changes

### 3. **System Events** (`system_events` collection)
Background processes tracked:
- ✅ Scheduled email triggers
- ✅ Background job executions
- ✅ Cron job completions
- ✅ System errors/warnings
- ✅ Database operations

### 4. **API Performance** (`api_analytics` collection)
Every API call tracked with:
- ✅ Endpoint path
- ✅ HTTP method (GET/POST/PUT/DELETE)
- ✅ Response time (milliseconds)
- ✅ Status code
- ✅ User email (if authenticated)
- ✅ IP address
- ✅ Error messages (if failed)

### 5. **Page Views** (`page_views` collection)
Frontend navigation tracked:
- ✅ Page URL
- ✅ Referrer
- ✅ Time on page
- ✅ Session ID
- ✅ User email

### 6. **User Sessions** (`user_sessions` collection)
Complete session tracking:
- ✅ Session start/end times
- ✅ Total actions performed
- ✅ Pages visited
- ✅ IP address
- ✅ User agent
- ✅ Session duration

---

## 🎯 Real-Time Analytics Dashboard

### Location
Admin Dashboard → **"🔴 Live Activity"** tab

### Features

#### 1. **Live Stats** (Auto-refreshes every 5 seconds)
- Active users (last 5 minutes)
- Recent activities count
- Average API response time
- Active sessions count

#### 2. **Activity Stream**
Real-time feed of all user actions:
- Color-coded action types
- User details
- Timestamps ("2s ago", "5m ago")
- Action details in JSON

#### 3. **API Performance Monitor**
- Most called endpoints
- Average/min/max response times
- Error rates
- Performance bars (green/yellow/red)

#### 4. **Active Sessions**
Currently active users:
- User email
- Actions performed
- Pages visited
- Session duration

---

## 🔌 API Endpoints

### Analytics Endpoints (Admin Only)

#### Real-Time Stats
```
GET /api/analytics/realtime?minutes=5
```
Get activity from last N minutes

#### User Timeline
```
GET /api/analytics/user-timeline/{email}?limit=100
```
Complete activity history for a user

#### Activity Logs
```
GET /api/analytics/activity-logs?limit=100&action_category=user_action&user_email=user@example.com
```
Filtered activity logs

#### System Events
```
GET /api/analytics/system-events?limit=50
```
Recent system events

#### API Performance
```
GET /api/analytics/api-performance?hours=24
```
API performance metrics

#### Page Views
```
GET /api/analytics/page-views?limit=100
```
Frontend page views

#### Active Sessions
```
GET /api/analytics/active-sessions
```
Currently active sessions (last 30 min)

### Public Tracking Endpoints

#### Track Page View
```
POST /api/tracking/page-view
{
  "page_url": "/dashboard",
  "user_email": "user@example.com",
  "referrer": "/login",
  "session_id": "session-123",
  "time_on_page": 45
}
```

#### Track Custom Action
```
POST /api/tracking/user-action
{
  "action_type": "button_click",
  "user_email": "user@example.com",
  "details": {"button_name": "send_now"},
  "session_id": "session-123"
}
```

#### Start Session
```
POST /api/tracking/session/start
{
  "user_email": "user@example.com"
}
```
Returns: `{session_id": "..."}`

#### Update Session
```
PUT /api/tracking/session/{session_id}
{
  "actions": 5,
  "pages": 3
}
```

---

## 🎨 Frontend Integration

### Automatic Tracking
All API calls are automatically tracked via middleware (no code changes needed)

### Manual Tracking Examples

#### Track Page View
```javascript
await axios.post(`${API}/tracking/page-view`, {
  page_url: window.location.pathname,
  user_email: user.email,
  session_id: sessionStorage.getItem('session_id')
});
```

#### Track Button Click
```javascript
await axios.post(`${API}/tracking/user-action`, {
  action_type: "personality_changed",
  user_email: user.email,
  details: { new_personality: "Elon Musk" }
});
```

---

## 📈 Data Structure Examples

### Activity Log
```json
{
  "id": "uuid",
  "user_email": "user@example.com",
  "action_type": "login_requested",
  "action_category": "user_action",
  "details": {"user_type": "existing"},
  "timestamp": "2025-11-11T17:20:03.145Z",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "session_id": "session-123"
}
```

### API Analytics
```json
{
  "id": "uuid",
  "endpoint": "/api/users/email@example.com",
  "method": "GET",
  "status_code": 200,
  "response_time_ms": 45,
  "user_email": "user@example.com",
  "timestamp": "2025-11-11T17:20:03.145Z",
  "ip_address": "192.168.1.1"
}
```

---

## 🔐 Privacy & Security

- ✅ IP addresses tracked for security (can be disabled if needed)
- ✅ Admin endpoints protected with authentication
- ✅ No sensitive data (passwords, tokens) logged
- ✅ User agent strings stored for analytics
- ✅ All data encrypted at rest (MongoDB Atlas)
- ✅ HTTPS connections only

---

## 📊 MongoDB Collections

| Collection | Purpose | Indexes |
|------------|---------|---------|
| `activity_logs` | All user/admin activities | email, timestamp, action_type |
| `system_events` | Background processes | timestamp, event_type |
| `api_analytics` | API performance | endpoint, timestamp |
| `page_views` | Frontend navigation | user_email, timestamp |
| `user_sessions` | Session tracking | user_email, session_start |

---

## 🚀 Performance

- **Auto-refresh**: Real-time dashboard updates every 5 seconds
- **Lightweight**: Minimal performance impact (<10ms overhead)
- **Scalable**: MongoDB Atlas handles millions of events
- **Indexed**: All queries optimized with proper indexes
- **Async**: Non-blocking background tracking

---

## 🎯 Use Cases

### For Product Development
- Track feature usage
- Identify popular personalities
- Monitor user engagement
- Find pain points

### For Support
- Debug user issues
- View user activity timeline
- Track error patterns
- Monitor system health

### For Business
- User behavior analytics
- Retention metrics
- Growth tracking
- Performance optimization

---

## 🔍 Querying MongoDB Atlas

### Connect via MongoDB Compass:
```
mongodb+srv://inboxinspire:RTNjbhRbwwgrduoZ@inboxinspire.gbxbqqj.mongodb.net/
```

### Example Queries:

**Find all login attempts:**
```javascript
db.activity_logs.find({ action_type: "login_requested" })
```

**Find slow API calls:**
```javascript
db.api_analytics.find({ response_time_ms: { $gt: 1000 } })
```

**Get user activity timeline:**
```javascript
db.activity_logs.find({ user_email: "user@example.com" }).sort({ timestamp: -1 })
```

---

## ✅ Next Steps

1. **View Live Activity**: Go to Admin Dashboard → 🔴 Live Activity
2. **Monitor Performance**: Check API response times
3. **Analyze Users**: View user activity timelines
4. **Set Alerts**: (Future) Configure alerts for errors/slow responses
5. **Export Data**: (Future) Download analytics reports

---

**Everything is tracked. Every action. Every click. Real-time. Forever.** 📊🔥
