"""
Email Reply Handler
Collects and processes user replies to motivational emails
"""
import os
import json
import re
import uuid
import logging
from datetime import datetime, timezone, date, timedelta
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Try to import imap_tools, but make it optional
try:
    from imap_tools import MailBox, AND, MailMessageFlags
    IMAP_AVAILABLE = True
except ImportError:
    IMAP_AVAILABLE = False
    logger.warning("imap-tools not installed. Email reply polling will be disabled. Install with: pip install imap-tools")


async def poll_email_replies():
    """
    Poll email inbox for user replies.
    Called by scheduler every 1 minute for near real-time processing.
    """
    if not IMAP_AVAILABLE:
        logger.warning("IMAP not available - skipping email reply polling")
        return
    
    # Import here to avoid circular imports
    from backend.config import get_env
    from backend.server import db, openai_client, tracker
    
    imap_host = get_env("IMAP_HOST")
    inbox_email = get_env("INBOX_EMAIL")
    inbox_password = get_env("INBOX_PASSWORD")
    
    if not all([imap_host, inbox_email, inbox_password]):
        logger.warning("Email reply polling disabled - missing IMAP credentials")
        return
    
    try:
        logger.info(f"📧 Starting email reply polling - Connecting to {imap_host}...")
        # Connect to email inbox
        with MailBox(imap_host).login(inbox_email, inbox_password) as mailbox:
            logger.info(f"✅ Connected to inbox: {inbox_email}")
            
            # Fetch unread messages from last 24 hours
            # Use date_gte to get messages from today and yesterday (to catch late-night replies)
            yesterday = date.today() - timedelta(days=1)
            messages = list(mailbox.fetch(AND(seen=False, date_gte=yesterday)))
            logger.info(f"📬 Found {len(messages)} unread message(s) in inbox")
            
            for msg in messages:
                try:
                    sender_email = msg.from_
                    logger.debug(f"📨 Checking email from: {sender_email}")
                    
                    # Verify sender is a registered user
                    user = await db.users.find_one({"email": sender_email})
                    if not user:
                        logger.debug(f"   ⏭️ Skipping - not a registered user: {sender_email}")
                        # Mark as read to avoid checking again
                        mailbox.flag(msg.uid, [MailMessageFlags.SEEN], True)
                        continue
                    
                    logger.info(f"   ✅ Found reply from registered user: {sender_email}")
                    
                    # Extract and clean reply text
                    reply_text = msg.text or msg.html
                    if msg.html:
                        reply_text = strip_html_tags(reply_text)
                    reply_text = clean_email_reply(reply_text)
                    
                    # Validate reply length
                    if len(reply_text.strip()) < 10:
                        logger.info(f"Reply too short from {sender_email}")
                        # Still mark as read to avoid reprocessing
                        mailbox.flag(msg.uid, [MailMessageFlags.SEEN], True)
                        continue
                    
                    # Check for duplicate reply (prevent processing same reply twice)
                    reply_hash = str(hash(reply_text.strip()[:500] + str(msg.date)))  # Hash of content + timestamp
                    existing_reply = await db.email_reply_conversations.find_one(
                        {
                            "user_email": sender_email,
                            "reply_text": {"$regex": f"^{re.escape(reply_text.strip()[:100])}"},  # Check first 100 chars
                            "reply_timestamp": {
                                "$gte": (msg.date - timedelta(minutes=5)).isoformat() if msg.date else None,
                                "$lte": (msg.date + timedelta(minutes=5)).isoformat() if msg.date else None
                            }
                        }
                    )
                    
                    if existing_reply:
                        logger.info(f"⚠️ Duplicate reply detected from {sender_email}, skipping (already processed at {existing_reply.get('reply_timestamp')})")
                        # Mark as read to avoid reprocessing
                        mailbox.flag(msg.uid, [MailMessageFlags.SEEN], True)
                        continue
                    
                    # Process the reply
                    try:
                        await process_user_reply(
                            user_email=sender_email,
                            reply_text=reply_text,
                            reply_timestamp=msg.date or datetime.now(timezone.utc),
                            email_uid=msg.uid  # Pass UID for tracking
                        )
                        
                        # Mark as read only after successful processing
                        mailbox.flag(msg.uid, [MailMessageFlags.SEEN], True)
                        logger.info(f"✅ Processed reply from {sender_email} (UID: {msg.uid})")
                    except Exception as process_error:
                        logger.error(f"❌ Failed to process reply from {sender_email}: {process_error}", exc_info=True)
                        # Don't mark as read if processing failed - allow retry on next poll
                        # But log the failure for monitoring
                    
                except Exception as e:
                    logger.error(f"Error processing email from {sender_email}: {e}", exc_info=True)
                    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Error polling email replies: {error_msg}", exc_info=True)
        
        # Provide helpful error messages
        if "authentication failed" in error_msg.lower() or "login failed" in error_msg.lower():
            logger.error("   💡 TIP: Check your INBOX_PASSWORD - for Gmail, use an App Password, not your regular password")
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            logger.error("   💡 TIP: Check your IMAP_HOST and ensure IMAP is enabled in your email provider settings")
        elif "ssl" in error_msg.lower() or "tls" in error_msg.lower():
            logger.error("   💡 TIP: Some email providers require specific SSL/TLS settings")


def strip_html_tags(html: str) -> str:
    """Remove HTML tags and extract plain text"""
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


def clean_email_reply(text: str) -> str:
    """
    Remove quoted text, signatures, and email artifacts
    """
    lines = text.split('\n')
    clean_lines = []
    
    for line in lines:
        line_stripped = line.strip()
        
        # Skip quoted text
        if line_stripped.startswith('>'):
            continue
        
        # Skip common email signatures/footers
        if any(footer in line.lower() for footer in [
            'sent from', 'get outlook', 'unsubscribe',
            'this email was sent', 'original message',
            'forwarded message', 'reply above this line'
        ]):
            break
        
        clean_lines.append(line)
    
    # Remove excessive whitespace
    cleaned = '\n'.join(clean_lines).strip()
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    return cleaned


async def process_user_reply(
    user_email: str,
    reply_text: str,
    reply_timestamp: datetime,
    email_uid: Optional[str] = None  # Email UID for tracking
):
    """
    Process user's email reply using LLM to extract insights
    """
    try:
        from backend.config import get_env
        from backend.server import db, openai_client, tracker
        from backend.models.message import EmailReplyConversation
        
        # Get user data
        user = await db.users.find_one({"email": user_email})
        if not user:
            return
        
        # Get the MOST RECENT message for this user (to link the reply)
        last_message = await db.message_history.find_one(
            {"email": user_email},
            {"_id": 0, "id": 1, "message": 1, "subject": 1, "sent_at": 1, "goal_id": 1, "goal_title": 1},
            sort=[("sent_at", -1)]
        )
        
        # Build simple LLM analysis prompt - focus on feedback extraction
        analysis_prompt = f"""Analyze this user's reply to their motivational email. Extract feedback simply and clearly.

LAST EMAIL SENT:
Subject: {last_message.get('subject', 'N/A') if last_message else 'N/A'}
Content: {last_message.get('message', 'N/A')[:200] if last_message else 'N/A'}

USER'S REPLY:
\"\"\"{reply_text}\"\"\"

EXTRACT FEEDBACK AND RETURN JSON:
{{
    "sentiment": "positive" | "neutral" | "struggling" | "confused" | "excited",
    "extracted_wins": ["specific good things they mentioned"],
    "extracted_struggles": ["specific problems or difficulties"],
    "extracted_questions": ["any questions they asked"],
    "key_topics": ["main points in their reply"],
    "preferred_tone_shift": "more_direct" | "more_supportive" | "more_humor" | "no_change",
    "suggested_focus": "celebrate_wins" | "address_obstacle" | "answer_question" | "maintain_momentum",
    "continuity_note": "Brief note for next email (max 50 words) - what to reference from their reply",
    "urgency_level": "low" | "medium" | "high",
    "needs_immediate_response": true | false
}}

KEEP IT SIMPLE:
- Extract what they actually said
- Note their sentiment honestly
- Create a brief continuity note for the next email
- Mark urgent if they need immediate help
"""

        # Call LLM for analysis
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You analyze user feedback to extract insights for personalized coaching. Return ONLY valid JSON."
                },
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.3,
            max_tokens=600,
            response_format={"type": "json_object"}
        )
        
        # Parse analysis
        analysis_raw = response.choices[0].message.content.strip()
        analysis = json.loads(analysis_raw)
        
        # Create conversation record
        conversation_id = str(uuid.uuid4())
        thread_id = user.get("conversation_thread_id") or str(uuid.uuid4())
        
        # Link reply to the most recent message (if available)
        linked_message_id = last_message.get("id") if last_message else None
        linked_goal_id = last_message.get("goal_id") if last_message else None
        
        conversation = EmailReplyConversation(
            id=conversation_id,
            user_email=user_email,
            conversation_thread_id=thread_id,
            reply_text=reply_text,
            reply_timestamp=reply_timestamp,
            reply_sentiment=analysis.get("sentiment", "neutral"),
            extracted_topics=analysis.get("key_topics", []),
            extracted_wins=analysis.get("extracted_wins", []),
            extracted_struggles=analysis.get("extracted_struggles", []),
            extracted_questions=analysis.get("extracted_questions", []),
            preferred_tone_shift=analysis.get("preferred_tone_shift"),
            suggested_focus=analysis.get("suggested_focus"),
            continuity_note=analysis.get("continuity_note"),
            urgency_level=analysis.get("urgency_level", "low"),
            needs_immediate_response=analysis.get("needs_immediate_response", False),
            processed=True
        )
        
        # Add email UID for tracking (if provided)
        conversation_dict = conversation.model_dump()
        if email_uid:
            conversation_dict["email_uid"] = email_uid
        
        # Add link to the message this reply is responding to
        if linked_message_id:
            conversation_dict["linked_message_id"] = linked_message_id
        if linked_goal_id:
            conversation_dict["linked_goal_id"] = linked_goal_id
        
        # Save to database
        await db.email_reply_conversations.insert_one(conversation_dict)
        
        # Update user profile
        total_emails = user.get("total_messages_received", 1)
        total_replies = user.get("total_replies", 0) + 1
        engagement_rate = (total_replies / total_emails * 100) if total_emails > 0 else 0
        
        await db.users.update_one(
            {"email": user_email},
            {
                "$set": {
                    "last_active": reply_timestamp.isoformat(),
                    "last_reply_at": reply_timestamp.isoformat(),
                    "conversation_thread_id": thread_id,
                    "reply_engagement_rate": round(engagement_rate, 2)
                },
                "$inc": {"total_replies": 1}
            }
        )
        
        # ALWAYS send automatic response to user's reply (not just when urgent)
        await send_immediate_encouragement(
            user_email=user_email,
            analysis=analysis,
            reply_text=reply_text,
            user_data=user,
            linked_message_id=linked_message_id,
            linked_goal_id=linked_goal_id,
            conversation_id=conversation_id  # Pass conversation_id
        )
        
        # Enhanced logging - show reply prominently
        logger.info("=" * 80)
        logger.info(f"📧 EMAIL REPLY RECEIVED from {user_email}")
        logger.info(f"   Sentiment: {analysis.get('sentiment')}")
        logger.info(f"   Linked to message: {linked_message_id or 'None'}")
        logger.info(f"   Linked to goal: {linked_goal_id or 'None'}")
        logger.info(f"   Wins mentioned: {len(analysis.get('extracted_wins', []))}")
        logger.info(f"   Struggles mentioned: {len(analysis.get('extracted_struggles', []))}")
        logger.info(f"   Questions asked: {len(analysis.get('extracted_questions', []))}")
        logger.info(f"   Reply preview: {reply_text[:100]}...")
        logger.info("=" * 80)
        
        # Log activity
        await tracker.log_user_activity(
            action_type="email_reply_received",
            user_email=user_email,
            details={
                "sentiment": analysis.get("sentiment"),
                "has_wins": len(analysis.get("extracted_wins", [])) > 0,
                "has_struggles": len(analysis.get("extracted_struggles", [])) > 0,
                "has_questions": len(analysis.get("extracted_questions", [])) > 0,
                "urgency": analysis.get("urgency_level"),
                "linked_message_id": linked_message_id,
                "linked_goal_id": linked_goal_id,
                "reply_length": len(reply_text)
            }
        )
        
        logger.info(f"✅ Processed and responded to reply from {user_email}: {analysis.get('sentiment')}")
        
    except Exception as e:
        logger.error(f"Error processing reply from {user_email}: {e}", exc_info=True)


async def send_immediate_encouragement(
    user_email: str,
    analysis: dict,
    reply_text: str,
    user_data: dict,
    linked_message_id: Optional[str] = None,
    linked_goal_id: Optional[str] = None,
    conversation_id: Optional[str] = None
):
    """
    ========================================================================
    AUTOMATIC REPLY EMAIL (ONLY TRIGGERED BY USER REPLY)
    ========================================================================
    This function ONLY runs when a user replies to an email.
    It sends a personalized automatic response based on:
    - User's reply content
    - User's selected personality/tone/custom settings
    - The original email they replied to
    
    This is SEPARATE from scheduled emails and does NOT affect them.
    Scheduled emails continue to work normally using the preset formula.
    ========================================================================
    """
    try:
        from backend.server import openai_client, send_email, db
        
        # Get context about what they replied to
        original_message_context = ""
        goal_context = ""
        
        if linked_message_id:
            original_msg = await db.message_history.find_one(
                {"id": linked_message_id},
                {"_id": 0, "subject": 1, "message": 1, "goal_title": 1}
            )
            if original_msg:
                original_message_context = f"""
ORIGINAL EMAIL THEY REPLIED TO:
Subject: {original_msg.get('subject', 'N/A')}
Content preview: {original_msg.get('message', '')[:200]}...
"""
        
        goal = None  # Initialize for later use
        if linked_goal_id:
            goal = await db.goals.find_one(
                {"id": linked_goal_id},
                {"_id": 0, "title": 1, "description": 1}
            )
            if goal:
                goal_context = f"""
RELATED GOAL:
Title: {goal.get('title', 'N/A')}
Description: {goal.get('description', '')[:150]}...
"""
        
        # Get user's personality/tone settings for personalized response
        user_personality = None
        user_tone = None
        
        # Check if this is a goal-specific reply
        if linked_goal_id and goal:
            goal_mode = goal.get("mode", "personality")
            if goal_mode == "personality":
                personality_id = goal.get("personality_id")
                personalities = user_data.get("personalities", [])
                user_personality = next((p for p in personalities if p.get("id") == personality_id or p.get("value") == personality_id), None)
            elif goal_mode == "tone":
                user_tone = goal.get("tone")
        else:
            # For main goal, use user's current personality
            personalities = user_data.get("personalities", [])
            if personalities:
                current_index = user_data.get("current_personality_index", 0)
                if current_index < len(personalities):
                    user_personality = personalities[current_index]
        
        # Build personality/tone context for prompt
        personality_context = ""
        if user_personality:
            persona_name = user_personality.get("value", "")
            persona_type = user_personality.get("type", "famous")
            if persona_type == "famous":
                personality_context = f"""
PERSONALITY STYLE: Write as {persona_name} would respond. Use their speaking style, tone, and perspective. Make it feel authentic to their voice.
"""
            elif persona_type == "custom":
                personality_context = f"""
PERSONALITY STYLE: {persona_name}
Write in this custom personality's style and voice.
"""
        elif user_tone:
            from backend.server import get_tone_system_prompt
            tone_prompt = get_tone_system_prompt(user_tone)
            personality_context = f"""
TONE STYLE: {tone_prompt[:200]}...
Write in this tone style - match the energy, voice, and approach described above.
"""
        
        # Build personalized response prompt
        wins_text = ', '.join(analysis.get('extracted_wins', [])[:3]) or 'None mentioned'
        struggles_text = ', '.join(analysis.get('extracted_struggles', [])[:3]) or 'None mentioned'
        questions_text = ', '.join(analysis.get('extracted_questions', [])[:2]) or 'None'
        user_name = user_data.get('name', 'Friend')
        
        prompt = f"""You are a supportive coach responding to a user's email reply. Generate a warm, genuine, conversational response (60-100 words).

{personality_context}
USER'S REPLY:
\"\"\"{reply_text[:400]}\"\"\"

ANALYSIS:
- Sentiment: {analysis.get('sentiment')}
- Wins they mentioned: {wins_text}
- Struggles they mentioned: {struggles_text}
- Questions they asked: {questions_text}

{original_message_context}
{goal_context}
USER CONTEXT:
- Name: {user_name}
- Current streak: {user_data.get('streak_count', 0)} days

WRITE A RESPONSE THAT:
1. Start with ONE greeting using their name: "{user_name}" (do NOT repeat the name)
2. Acknowledge what they shared specifically (reference their actual words)
3. If they mentioned wins: Celebrate them genuinely
4. If they mentioned struggles: Offer brief, actionable support
5. If they asked questions: Answer directly or promise to address in next email
6. Keep it conversational and warm (like texting a friend)
7. End with: "I'll catch up with you in your next scheduled email. Keep going!"

CRITICAL RULES:
- Use their name ONCE at the start, then refer to them naturally (you, your, etc.)
- Do NOT say "Hi {user_name}" and then "Hey {user_name}" - only ONE greeting
- Do NOT include "[Your Name]" or any placeholder - sign as "Your Tend Coach"
- Be genuine, not robotic
- Reference their specific words when possible
- Keep it brief but meaningful (60-100 words)
- Match their energy (if excited, be excited; if struggling, be supportive)
- Follow the personality/tone style if provided above"""

        response = await openai_client.chat.completions.create(
            model="gpt-4o",  # Use full model for better quality responses
            messages=[
                {"role": "system", "content": "You are a warm, supportive coach who writes genuine, conversational responses. You acknowledge what users share and provide brief, actionable encouragement."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=250
        )
        
        message_text = response.choices[0].message.content.strip()
        
        # Generate subject line based on reply sentiment
        if analysis.get('sentiment') == 'struggling':
            subject = f"Re: I hear you, {user_data.get('name', 'there')}"
        elif analysis.get('sentiment') == 'excited':
            subject = f"Re: That's amazing, {user_data.get('name', 'there')}!"
        elif len(analysis.get('extracted_questions', [])) > 0:
            subject = f"Re: Quick response to your question"
        else:
            subject = f"Re: Thanks for sharing, {user_data.get('name', 'there')}"
        
        # Clean up message_text - remove any duplicate greetings or placeholders
        cleaned_message = message_text
        user_name = user_data.get('name', 'Friend')
        
        # Remove duplicate greetings if LLM added them
        if f"Hi {user_name}" in cleaned_message and f"Hey {user_name}" in cleaned_message:
            # Keep only the first greeting
            cleaned_message = cleaned_message.replace(f"Hey {user_name},", "").replace(f"Hey {user_name}", "")
        
        # Remove any placeholder text
        cleaned_message = cleaned_message.replace("[Your Name]", "Tend")
        cleaned_message = cleaned_message.replace("Your Name", "Tend")
        
        # Ensure it ends with proper signature (remove if LLM added wrong one)
        if "Your Tend Coach" not in cleaned_message and "Tend" not in cleaned_message[-50:]:
            # Add signature if missing
            cleaned_message = cleaned_message.rstrip() + "\n\nYour Tend Coach"
        
        # Send email with better formatting
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; line-height: 1.6;">
            <div style="margin: 20px 0;">
                {cleaned_message.replace(chr(10), '<br>')}
            </div>
        </body>
        </html>
        """
        
        # Get original message's Message-ID for email threading (if available)
        in_reply_to = None
        references = None
        if linked_message_id:
            original_msg = await db.message_history.find_one(
                {"id": linked_message_id},
                {"_id": 0, "message_id": 1, "subject": 1}
            )
            if original_msg and original_msg.get("message_id"):
                # Use stored Message-ID or generate one from message ID
                in_reply_to = original_msg.get("message_id") or f"<msg-{linked_message_id}@maketend.com>"
                references = in_reply_to
        
        success, error = await send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content,
            in_reply_to=in_reply_to,  # NEW: Thread the email
            references=references  # NEW: Reference original message
        )
        
        if success:
            # Mark as sent and store response in database
            await db.email_reply_conversations.update_one(
                {"user_email": user_email, "id": conversation_id},
                {
                    "$set": {
                        "immediate_response_sent": True,
                        "immediate_response_text": message_text,
                        "immediate_response_subject": subject,
                        "immediate_response_sent_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            # Also save this response as a message in message_history for tracking
            response_message_id = str(uuid.uuid4())
            await db.message_history.insert_one({
                "id": response_message_id,
                "email": user_email,
                "message": message_text,
                "subject": subject,
                "personality": {
                    "type": "system",
                    "value": "Reply Response",
                    "active": True
                },
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "message_type": "reply_response",
                "goal_id": linked_goal_id,
                "goal_title": goal.get('title') if linked_goal_id and goal else None,
                "conversation_context": {
                    "is_reply_response": True,
                    "original_reply_id": conversation_id,
                    "original_reply_sentiment": analysis.get('sentiment')
                },
                "used_fallback": False
            })
            
            logger.info(f"✅ Sent automatic response to {user_email} (reply to their message)")
            logger.info(f"   Response subject: {subject}")
            logger.info(f"   Response preview: {message_text[:100]}...")
        else:
            logger.error(f"❌ Failed to send automatic response to {user_email}: {error}")
        
    except Exception as e:
        logger.error(f"Error sending immediate encouragement: {e}", exc_info=True)

