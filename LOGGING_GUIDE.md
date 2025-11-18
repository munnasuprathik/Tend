# 📋 Comprehensive Logging Guide - Tend Application

## 🎯 **Overview**

The Tend application now includes **comprehensive logging** for all important operations, making debugging and monitoring significantly easier.

---

## 📊 **Logging Configuration**

### **Format**
```
%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s
```

### **Log Levels**
- **INFO**: Normal operations, successful actions
- **DEBUG**: Detailed information for debugging
- **WARNING**: Potential issues, non-critical errors
- **ERROR**: Errors that need attention

### **Output**
- All logs are written to **stdout** (console)
- Can be redirected to files using standard shell redirection

---

## 🔍 **What's Being Logged**

### **1. Authentication & User Management** ✅

#### **Login Requests**
```
🔐 Login request received for: user@example.com (IP: 192.168.1.1)
✅ Existing user found: user@example.com
📧 Magic link email queued for: user@example.com
✅ Login request completed for user@example.com in 45.23ms
```

#### **Onboarding**
```
🎯 Onboarding started for: newuser@example.com
📝 Saving version history for: newuser@example.com
📅 Scheduling emails for new user: newuser@example.com
✅ Onboarding complete for newuser@example.com in 1.23s
   - User created
   - Version history saved
   - Emails scheduled
```

#### **User Updates**
```
📝 User update request for: user@example.com
Fields to update: ['schedule', 'personalities']
📅 Schedule/active changed for user@example.com - rescheduling emails
✅ User update completed for user@example.com in 0.45s
```

---

### **2. Email Operations** ✅

#### **Scheduled Email Jobs**
```
⏰ Scheduler job started for: user@example.com
📧 Scheduled email job triggered for: user@example.com
User found: user@example.com, active: True
Using personality: coach for user@example.com
Generated subject line for user@example.com: Day 5: Keep Going...
📤 Sending email to user@example.com (streak: 5, personality: coach)
✅ Email sent successfully to user@example.com
✅ Email sent to user@example.com - Streak updated to 5 days
⏱️ Email job completed for user@example.com in 2.34s
✅ Scheduler job completed for user@example.com in 2.35s
```

#### **Email Sending Errors**
```
❌ Failed to send email to user@example.com: SMTP timeout after 30s
❌ Error sending email to user@example.com after 2.45s: Connection refused
```

#### **Email Queue**
- Logs when emails are queued
- Logs when semaphore limits are reached
- Logs retry attempts

---

### **3. Scheduler Operations** ✅

#### **Email Scheduling**
```
🔄 Starting email scheduling for all active users...
📋 Found 150 existing scheduled jobs
📊 Scheduled 1000 users so far...
📊 Scheduled 2000 users so far...
✅ Completed scheduling emails for 10,234 users in 45.67s
📊 Average: 224.1 users/second
```

#### **Job Execution**
```
⏰ Scheduler job started for: user@example.com
✅ Scheduler job completed for user@example.com in 2.35s
```

#### **Job Errors**
```
❌ Error in scheduler job for user@example.com after 1.23s: User not found
```

---

### **4. API Operations** ✅

#### **API Requests**
```
🌐 API Request: POST /api/auth/login (IP: 192.168.1.1)
⏱️ API call: POST /api/auth/login took 234ms
```

#### **Slow API Calls**
```
⚠️ Slow API call: POST /api/generate-message took 1234ms
```

#### **API Errors**
```
⚠️ API Error: GET /api/users/invalid@example.com returned 404
❌ API Exception: POST /api/send-now failed after 456ms: Connection timeout
```

---

### **5. Admin Operations** ✅

#### **Broadcast Messages**
```
📢 Broadcast message initiated: 'Important Update from Tend'
Message length: 1234 characters
📊 Broadcast progress: 1000 users processed (950 success, 50 failed)...
✅ Broadcast completed in 123.45s
   - Total users: 10,234
   - Success: 9,850 (96.2%)
   - Failed: 384 (3.8%)
```

#### **Database Health**
- Collection counts logged
- Recent activity logged
- Error rates logged

---

### **6. Database Operations** ✅

#### **Index Creation**
```
✅ Database indexes created (including reply conversations and multi-goal support)
```

#### **Query Performance**
- Slow queries logged (if > 500ms)
- Large result sets logged
- Pagination progress logged

---

### **7. Startup & Shutdown** ✅

#### **Application Startup**
```
============================================================
🚀 Starting Tend API...
============================================================
🔍 Validating environment variables...
✅ Environment validation passed
✅ Database indexes created
✅ Achievements initialized
✅ Email reply polling job scheduled (every 1 minute)
Scheduled goal jobs for 234 active goals
✅ Scheduler started
✅ User email schedules initialized
🚀 Application startup completed in 12.34s
============================================================
✅ Tend API is ready and running!
============================================================
```

#### **Application Shutdown**
```
============================================================
🛑 Application shutdown initiated...
Stopping scheduler...
✅ Scheduler stopped
Closing database connection...
✅ Database connection closed
✅ Application shutdown completed in 0.45s
============================================================
```

---

### **8. Error Tracking** ✅

#### **Exception Logging**
All exceptions include:
- Full stack trace (`exc_info=True`)
- Context information
- Duration/timing
- User/request details

Example:
```
❌ Error sending email to user@example.com after 2.45s: Connection refused
Traceback (most recent call last):
  File "server.py", line 1234, in send_email
    await aiosmtplib.send(msg, **smtp_kwargs)
  ...
```

---

## 📈 **Performance Metrics**

### **Timing Information**
All operations log their duration:
- Login requests: `in 45.23ms`
- Email sending: `in 2.34s`
- Onboarding: `in 1.23s`
- API calls: `took 234ms`

### **Throughput Metrics**
- Users processed per second
- Emails sent per second
- API requests per second

---

## 🔧 **Using Logs for Debugging**

### **1. Find User Issues**
```bash
# Search for a specific user
grep "user@example.com" logs.txt

# Find errors for a user
grep "user@example.com" logs.txt | grep "❌"
```

### **2. Monitor Email Sending**
```bash
# Find all email sending operations
grep "📧\|📤\|✅ Email sent" logs.txt

# Find email failures
grep "❌.*email\|Failed to send" logs.txt
```

### **3. Track Performance**
```bash
# Find slow operations
grep "Slow\|took.*[0-9]{4}ms" logs.txt

# Find scheduler performance
grep "Scheduled.*users\|Average:" logs.txt
```

### **4. Monitor Errors**
```bash
# Find all errors
grep "❌\|ERROR" logs.txt

# Find API errors
grep "API.*Error\|API Exception" logs.txt
```

### **5. Track Admin Operations**
```bash
# Find broadcast operations
grep "📢 Broadcast\|Broadcast.*completed" logs.txt

# Find admin activities
grep "admin.*activity" logs.txt
```

---

## 📝 **Log File Management**

### **Redirect Logs to File**
```bash
# Run with log redirection
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 > app.log 2>&1

# Or use nohup for background
nohup python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

### **Rotate Logs**
```bash
# Use logrotate or similar tools
# Example logrotate config:
/path/to/app.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

### **View Logs in Real-Time**
```bash
# Tail logs
tail -f app.log

# Tail with filtering
tail -f app.log | grep "ERROR\|❌"

# Tail with color highlighting
tail -f app.log | grep --color=always "ERROR\|❌\|✅"
```

---

## 🎯 **Logging Best Practices**

### **1. Use Appropriate Log Levels**
- **INFO**: Normal operations
- **DEBUG**: Detailed debugging info
- **WARNING**: Potential issues
- **ERROR**: Actual errors

### **2. Include Context**
- User email
- Operation duration
- Success/failure status
- Error messages

### **3. Use Emojis for Quick Scanning**
- ✅ Success
- ❌ Error
- ⚠️ Warning
- 📧 Email
- 🔐 Auth
- 📅 Schedule
- ⏱️ Timing
- 📊 Stats

### **4. Log Performance Metrics**
- Always include duration for operations
- Log throughput for batch operations
- Alert on slow operations

---

## 🔍 **Example Log Output**

```
2024-01-15 10:23:45 - backend.server - INFO - [server.py:1739] - 🔐 Login request received for: user@example.com (IP: 192.168.1.1)
2024-01-15 10:23:45 - backend.server - INFO - [server.py:1749] - ✅ Existing user found: user@example.com
2024-01-15 10:23:45 - backend.server - INFO - [server.py:1812] - 📧 Magic link email queued for: user@example.com
2024-01-15 10:23:45 - backend.server - INFO - [server.py:1815] - ✅ Login request completed for user@example.com in 45.23ms
2024-01-15 10:24:12 - backend.server - INFO - [server.py:7891] - ⏰ Scheduler job started for: user@example.com
2024-01-15 10:24:12 - backend.server - INFO - [server.py:1293] - 📧 Scheduled email job triggered for: user@example.com
2024-01-15 10:24:12 - backend.server - DEBUG - [server.py:1329] - Using personality: coach for user@example.com
2024-01-15 10:24:14 - backend.server - INFO - [server.py:1475] - 📤 Sending email to user@example.com (streak: 5, personality: coach)
2024-01-15 10:24:16 - backend.server - INFO - [server.py:1480] - ✅ Email sent successfully to user@example.com
2024-01-15 10:24:16 - backend.server - INFO - [server.py:1506] - ⏱️ Email job completed for user@example.com in 2.34s
2024-01-15 10:24:16 - backend.server - INFO - [server.py:7888] - ✅ Scheduler job completed for user@example.com in 2.35s
```

---

## ✅ **Summary**

**All critical operations are now logged with:**
- ✅ User identification
- ✅ Operation timing
- ✅ Success/failure status
- ✅ Error details with stack traces
- ✅ Performance metrics
- ✅ Context information

**This makes debugging and monitoring significantly easier!** 🎉

---

## 📚 **Related Documentation**

- `FINAL_READINESS_STATUS.md` - Production readiness
- `SCALABILITY_FIXES_IMPLEMENTED.md` - Scalability improvements
- `README_10K_TESTING.md` - Testing guide

