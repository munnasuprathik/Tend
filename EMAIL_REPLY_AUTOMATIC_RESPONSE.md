# Email Reply Automatic Response System

## Overview
The system now automatically responds to every user reply and uses reply context to refine the next scheduled email.

## Complete Flow

### 1. User Replies to Email
- User receives a motivational email
- User replies to that email
- Reply is sent to the configured inbox

### 2. Email Reply Polling (Every 10 minutes)
- System polls inbox using IMAP
- Finds unread replies from registered users
- Extracts and cleans reply text (removes HTML, quoted text, signatures)

### 3. Reply Processing
- **LLM Analysis**: Reply is analyzed using GPT-4o to extract:
  - Sentiment (positive, neutral, struggling, confused, excited)
  - Extracted wins (good things mentioned)
  - Extracted struggles (challenges mentioned)
  - Extracted questions (questions asked)
  - Key topics
  - Urgency level
  - Suggested focus for next email

### 4. Database Storage
- Reply is stored in `email_reply_conversations` collection with:
  - `linked_message_id`: Links to the original email they replied to
  - `linked_goal_id`: Links to the goal (if applicable)
  - All extracted insights
  - Reply timestamp
  - Processing status

### 5. Automatic Response (ALWAYS SENT)
- **Immediate Response**: System ALWAYS sends an automatic response (not just when urgent)
- Response is generated using GPT-4o with:
  - Context about what they replied to
  - Their actual reply text
  - Extracted wins, struggles, questions
  - Goal context (if applicable)
  - User's name and streak
- Response is personalized based on sentiment:
  - Struggling → Supportive, empathetic
  - Excited → Celebratory, energetic
  - Questions → Direct answers or promise to address
  - Neutral → Acknowledgment and encouragement
- Response is saved to:
  - `email_reply_conversations` (marked as `immediate_response_sent: true`)
  - `message_history` (as `message_type: "reply_response"`)

### 6. Enhanced Logging
- Replies are prominently logged with:
  ```
  ================================================================================
  📧 EMAIL REPLY RECEIVED from user@example.com
     Sentiment: positive
     Linked to message: msg_123
     Linked to goal: goal_456
     Wins mentioned: 2
     Struggles mentioned: 1
     Questions asked: 0
     Reply preview: Thank you for this message...
  ================================================================================
  ```

### 7. Next Email Generation (Uses Reply Context)
When generating the next scheduled email:

**IF USER HAS REPLIED:**
- System fetches most recent reply linked to the goal
- Builds `reply_context` with:
  - User's actual reply text
  - Extracted wins, struggles, questions
  - Sentiment
- Includes `reply_context` in LLM prompt
- LLM generates email that:
  - References their feedback naturally
  - Acknowledges what they shared
  - Addresses their struggles (if any)
  - Celebrates their wins (if any)
  - Answers their questions (if any)
- Creates conversational continuity

**IF USER HAS NOT REPLIED:**
- `reply_context` remains empty string
- System uses preset formula (standard motivational email)
- No reply context is included in prompt

### 8. Message History Tracking
- All replies are shown in message history
- Replies are grouped with their original messages
- Visual indicators show which messages have replies
- Reply responses are also shown in history

## Key Features

### ✅ Automatic Response
- **Every reply gets an immediate response** (not just urgent ones)
- Response is contextual and personalized
- Sent within minutes of receiving the reply

### ✅ Reply Context in Next Email
- Next scheduled email incorporates user's feedback
- Creates true conversational flow
- References specific things user mentioned

### ✅ Fallback to Preset Formula
- If no reply exists, uses standard motivational email
- No reply context = normal email generation
- Seamless fallback

### ✅ Enhanced Logging
- Prominent log entries for all replies
- Easy to track reply activity
- Includes all relevant details

### ✅ Database Storage
- All replies stored with full context
- Linked to original messages and goals
- Tracks response status

## Example Flow

1. **Day 1, 9:00 AM**: System sends email "Day 1: Let's start your journey!"
2. **Day 1, 2:30 PM**: User replies "Thanks! I'm excited but also nervous about starting"
3. **Day 1, 2:35 PM**: System processes reply, extracts:
   - Sentiment: excited + nervous
   - Wins: excited about starting
   - Struggles: nervous about starting
4. **Day 1, 2:36 PM**: System sends automatic response:
   - "Hi [Name], I hear that mix of excitement and nerves - that's totally normal when starting something new! The fact that you're excited shows you're ready. Let's channel that energy into your first small step today. I'll follow up tomorrow with more support. You've got this!"
5. **Day 2, 9:00 AM**: System generates next email:
   - References their nervousness from yesterday
   - Acknowledges their excitement
   - Provides specific support for starting
   - Creates continuity: "Yesterday you mentioned feeling both excited and nervous - that's a sign you're taking this seriously..."

## Configuration

### Email Polling
- Runs every 10 minutes (configurable in `lifespan` function)
- Polls inbox using IMAP
- Processes unread replies

### Response Generation
- Uses GPT-4o for quality responses
- Temperature: 0.8 (for natural, conversational tone)
- Max tokens: 250 (keeps responses brief)

### Next Email Context
- Looks for replies within last 24 hours
- Prioritizes goal-specific replies
- Falls back to any recent reply if no goal-specific one

## Database Collections

### `email_reply_conversations`
- Stores all user replies
- Links to original messages
- Tracks response status
- Contains extracted insights

### `message_history`
- Stores all sent messages (including reply responses)
- Tracks conversation context
- Links replies to messages

## API Endpoints

- `GET /users/{email}/replies` - Get all replies from a user
- `GET /users/{email}/reply-insights` - Get aggregated insights
- `GET /admin/reply-analytics` - Admin analytics for replies

## Logging

All reply activity is logged with:
- Reply received timestamp
- User email
- Sentiment analysis
- Linked message/goal IDs
- Extracted insights count
- Reply preview text

