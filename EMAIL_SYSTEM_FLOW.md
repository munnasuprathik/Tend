# Email System Flow - Complete Overview

## 🎯 **Core Principle**

**Scheduled emails and automatic reply emails are COMPLETELY SEPARATE systems.**

---

## 📧 **1. SCHEDULED EMAILS (Core Functionality)**

### **How It Works:**
- Scheduled emails are generated based on:
  - User's selected **personality/tone/custom** settings
  - Goal information
  - Streak count
  - Last message context (for variety)
  - **NOT affected by user replies**

### **When They're Sent:**
- Based on user's schedule (daily, weekly, monthly, custom)
- At specific times set by the user
- Automatically scheduled days/weeks in advance

### **Generation Process:**
1. System calculates next send times based on schedule
2. Creates `goal_messages` records with `status: "pending"`
3. Schedules APScheduler jobs for each send time
4. When time arrives, `send_goal_message_at_time()` is called
5. Generates email using `generate_goal_message()` with:
   - Personality/tone/custom settings
   - Goal context
   - Streak information
   - **NO reply context** (always empty)

### **Key Features:**
- ✅ Consistent quality using preset formula
- ✅ Personalized based on personality/tone/custom
- ✅ Varied content (avoids repetition)
- ✅ **NOT affected by user replies**
- ✅ Works independently of reply system

---

## 💬 **2. AUTOMATIC REPLY EMAILS (Reply-Triggered Only)**

### **How It Works:**
- **ONLY** triggered when a user replies to an email
- Polls inbox every 1 minute for unread emails
- If email is from a registered user, processes it
- Sends automatic personalized response

### **When They're Sent:**
- **ONLY** when user replies to an email
- Within 1 minute of receiving the reply
- Uses email threading (In-Reply-To header)

### **Generation Process:**
1. User replies to an email
2. `poll_email_replies()` detects unread email (runs every 1 min)
3. `process_user_reply()` analyzes the reply with LLM
4. Extracts sentiment, wins, struggles, questions
5. `send_immediate_encouragement()` generates response using:
   - User's reply content
   - User's personality/tone/custom settings (from goal or main)
   - Original email context
   - Analysis results

### **Key Features:**
- ✅ Only sent when user replies
- ✅ Personalized based on reply content
- ✅ Uses user's personality/tone/custom settings
- ✅ Immediate response (within 1 minute)
- ✅ **Does NOT affect scheduled emails**

---

## 🔄 **Complete Flow Example**

### **Day 1:**
1. **9:00 AM** - Scheduled email sent (personality: Elon Musk, tone: energetic)
2. **9:15 AM** - User replies: "Thanks! I'm making progress on my MVP"
3. **9:16 AM** - Automatic reply sent (personalized, using Elon Musk style)
4. **9:00 PM** - Scheduled email sent (normal, not affected by reply)

### **Day 2:**
1. **9:00 AM** - Scheduled email sent (normal, using preset formula)
2. **No reply** - No automatic email sent
3. **9:00 PM** - Scheduled email sent (normal)

### **Day 3:**
1. **9:00 AM** - Scheduled email sent (normal)
2. **10:00 AM** - User replies: "I'm struggling with motivation"
3. **10:01 AM** - Automatic reply sent (supportive, personalized)
4. **9:00 PM** - Scheduled email sent (normal, NOT affected by morning reply)

---

## ✅ **Guarantees**

1. **Scheduled emails always work:**
   - Use preset formula
   - Based on personality/tone/custom
   - Consistent quality
   - **Never affected by replies**

2. **Automatic replies only when needed:**
   - Only sent when user replies
   - Personalized based on reply
   - Uses same personality/tone/custom settings
   - **Never affects scheduled emails**

3. **Next day emails work perfectly:**
   - `schedule_next_goal_send()` creates next scheduled email
   - Uses same preset formula
   - Not affected by any replies

---

## 🔧 **Technical Implementation**

### **Scheduled Email Generation:**
```python
# backend/server.py - generate_goal_message()
reply_context = ""  # Always empty
conversation_context = None  # Always None
# Uses personality/tone/custom settings
# Uses preset formula
```

### **Automatic Reply Generation:**
```python
# backend/email_reply_handler.py - send_immediate_encouragement()
# Only called from process_user_reply()
# Uses user's reply content
# Uses personality/tone/custom settings
# Does NOT affect scheduled emails
```

### **Scheduling:**
```python
# backend/server.py - schedule_goal_jobs_for_goal()
# Creates goal_messages records
# Schedules APScheduler jobs
# Each job calls send_goal_message_at_time()
# After sending, calls schedule_next_goal_send() for next email
```

---

## 📋 **Summary**

| Feature | Scheduled Emails | Automatic Replies |
|---------|-----------------|-------------------|
| **Trigger** | Schedule/time-based | User reply only |
| **Frequency** | Based on schedule | Only when user replies |
| **Content** | Preset formula | Based on reply content |
| **Personality** | User's selected | User's selected |
| **Affected by replies?** | ❌ NO | ✅ YES (uses reply) |
| **Affects scheduled?** | N/A | ❌ NO |

---

## 🎯 **Result**

✅ **Scheduled emails work perfectly** - consistent, high-quality, based on personality/tone/custom  
✅ **Next day emails work perfectly** - automatically scheduled, same quality  
✅ **Automatic replies only when user replies** - personalized, immediate  
✅ **Core email functionality never impacted** - scheduled emails always use preset formula

