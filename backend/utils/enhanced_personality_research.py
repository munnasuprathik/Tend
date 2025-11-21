"""
Enhanced Personality Research System
Deep research and voice extraction for personalities, tones, and custom styles
"""
import json
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import httpx
import os
from backend.config import TAVILY_API_KEY, TAVILY_SEARCH_URL, openai_client, logger, tracker

async def research_famous_personality(personality_name: str) -> Optional[Dict[str, Any]]:
    """
    Deep research on ANY famous personality to extract authentic communication style.
    Works universally for all personalities - Elon Musk, Oprah Winfrey, Steve Jobs, etc.
    
    Returns comprehensive voice profile including:
    - Communication style and patterns
    - Vocabulary preferences
    - Sentence structure
    - Tone and energy
    - Speaking patterns
    - Writing style
    - Key phrases and expressions
    
    This function is generic and works for ANY famous personality name provided.
    """
    if not TAVILY_API_KEY:
        logger.warning(f"Tavily API key not available - cannot research {personality_name}")
        return None
    
    if not personality_name or len(personality_name.strip()) < 2:
        logger.warning(f"Invalid personality name: {personality_name}")
        return None
    
    # Clean and normalize personality name
    personality_name = personality_name.strip()
    logger.info(f"🔍 Starting deep research for personality: {personality_name}")
    
    try:
        # Multi-query research for comprehensive understanding
        # These queries work for ANY famous personality, not just specific ones
        queries = [
            f"{personality_name} communication style speaking patterns",
            f"{personality_name} writing style vocabulary phrases",
            f"{personality_name} interview quotes speaking mannerisms",
            f"{personality_name} social media posts writing style",
            f"How does {personality_name} talk? Communication patterns and style",
            f"{personality_name} quotes speaking voice tone",
            f"{personality_name} public speaking style presentation"
        ]
        
        all_results = []
        for query in queries:
            payload = {
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": 3,
                "search_depth": "advanced"  # Get deeper results
            }
            
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.post(TAVILY_SEARCH_URL, json=payload)
                    if response.status_code == 429:
                        await tracker.log_system_event(
                            event_type="tavily_rate_limit",
                            event_category="research",
                            details={"query": query, "personality": personality_name},
                            status="warning"
                        )
                        continue
                    response.raise_for_status()
                    data = response.json()
                    results = data.get("results", [])
                    all_results.extend(results)
            except Exception as e:
                logger.warning(f"Tavily query failed for {personality_name}: {e}")
                continue
        
        if not all_results:
            return None
        
        # Combine all research content
        combined_content = "\n\n".join([
            result.get("content", "") or result.get("snippet", "")
            for result in all_results[:10]  # Limit to top 10 results
        ])
        
        if not combined_content or len(combined_content) < 100:
            return None
        
        # Use LLM to extract structured voice profile
        # This extraction works for ANY personality - the LLM adapts to the research content
        extraction_prompt = f"""Analyze the following research about {personality_name}'s communication style and extract a comprehensive voice profile.

IMPORTANT: This works for ANY famous personality. Extract authentic communication patterns from the research provided, regardless of who the personality is.

RESEARCH CONTENT:
{combined_content[:4000]}  # Limit to avoid token limits

Extract and structure the following information:

1. **Communication Style**: How they speak (direct, conversational, technical, philosophical, etc.)
2. **Vocabulary**: Preferred words, phrases, expressions they commonly use
3. **Sentence Structure**: Short/long sentences, question patterns, exclamations, pauses
4. **Tone & Energy**: Overall vibe (energetic, calm, intense, measured, etc.)
5. **Speaking Patterns**: Unique mannerisms, repetition patterns, catchphrases, verbal tics
6. **Writing Style**: How they write (if different from speaking) - emails, posts, books
7. **Key Phrases**: 5-10 signature phrases or expressions they use
8. **Energy Level**: High/Medium/Low
9. **Formality**: Formal/Casual/Mixed
10. **Humor Style**: Type of humor (if any) - dry, witty, self-deprecating, none, etc.
11. **Unique Characteristics**: Any distinctive communication traits specific to this personality

Return ONLY a JSON object with this structure:
{{
    "communication_style": "<detailed description>",
    "vocabulary": ["word1", "word2", "phrase1", ...],
    "sentence_structure": "<description of patterns>",
    "tone_energy": "<description>",
    "speaking_patterns": "<unique mannerisms>",
    "writing_style": "<description>",
    "key_phrases": ["phrase1", "phrase2", ...],
    "energy_level": "high|medium|low",
    "formality": "formal|casual|mixed",
    "humor_style": "<type or none>",
    "sample_quotes": ["quote1", "quote2", ...]
}}"""
        
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing communication patterns and extracting authentic voice profiles. Return ONLY valid JSON."
                },
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.3,  # Lower temperature for accurate extraction
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        
        voice_profile = json.loads(content)
        
        # Build comprehensive voice instruction
        voice_instruction = f"""AUTHENTIC VOICE PROFILE FOR {personality_name.upper()}:

COMMUNICATION STYLE:
{voice_profile.get('communication_style', 'Direct and engaging')}

VOCABULARY & PHRASES:
Use these words and phrases naturally: {', '.join(voice_profile.get('key_phrases', [])[:10])}
Vocabulary style: {', '.join(voice_profile.get('vocabulary', [])[:15])}

SENTENCE STRUCTURE:
{voice_profile.get('sentence_structure', 'Varied sentence lengths')}

TONE & ENERGY:
{voice_profile.get('tone_energy', 'Energetic and focused')}
Energy Level: {voice_profile.get('energy_level', 'medium').upper()}
Formality: {voice_profile.get('formality', 'mixed').upper()}

SPEAKING PATTERNS:
{voice_profile.get('speaking_patterns', 'Natural conversational flow')}

WRITING STYLE:
{voice_profile.get('writing_style', voice_profile.get('communication_style', 'Clear and direct'))}

HUMOR STYLE:
{voice_profile.get('humor_style', 'None')}

SAMPLE QUOTES (for style reference):
{chr(10).join(f'- "{q}"' for q in voice_profile.get('sample_quotes', [])[:5])}

CRITICAL RULES:
1. Write EXACTLY in this voice - capture their authentic communication style
2. Use their vocabulary and phrases naturally (don't force them)
3. Match their sentence structure patterns
4. Reflect their energy level and formality
5. If they use humor, incorporate it in their style
6. Do NOT claim to BE {personality_name} - write IN THEIR STYLE
7. Make it feel like {personality_name} is talking directly to the user
8. Be authentic - if research shows they're direct, be direct; if they're philosophical, be philosophical"""
        
        return {
            "voice_instruction": voice_instruction,
            "raw_profile": voice_profile,
            "confidence": 0.9,  # High confidence with deep research
            "research_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error researching famous personality {personality_name}: {e}")
        return None


async def research_custom_personality(custom_description: str) -> Optional[Dict[str, Any]]:
    """
    Research custom personality description to understand the style, then create voice profile.
    First researches what the description means, then extracts communication patterns.
    """
    if not TAVILY_API_KEY or not custom_description or len(custom_description) < 20:
        return None
    
    try:
        # Step 1: Research what this custom style means
        research_queries = [
            f"communication style: {custom_description}",
            f"writing style {custom_description}",
            f"speaking patterns {custom_description}"
        ]
        
        all_content = []
        for query in research_queries:
            payload = {
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": 2
            }
            
            try:
                async with httpx.AsyncClient(timeout=8) as client:
                    response = await client.post(TAVILY_SEARCH_URL, json=payload)
                    if response.status_code == 429:
                        continue
                    response.raise_for_status()
                    data = response.json()
                    results = data.get("results", [])
                    for result in results:
                        content = result.get("content", "") or result.get("snippet", "")
                        if content:
                            all_content.append(content)
            except Exception:
                continue
        
        # Step 2: Use LLM to understand the custom description and create voice profile
        research_context = "\n\n".join(all_content[:3]) if all_content else "No external research available"
        
        analysis_prompt = f"""Analyze this custom personality description and create a comprehensive voice profile.

CUSTOM DESCRIPTION:
{custom_description}

RESEARCH CONTEXT (if available):
{research_context[:1000]}

Based on the description and research, extract:

1. **Communication Philosophy**: What does this style mean? What's the underlying approach?
2. **Voice Characteristics**: How should this sound? Tone, energy, formality
3. **Language Patterns**: What kind of vocabulary, sentence structure, phrasing?
4. **Emotional Tone**: What feeling should this convey?
5. **Structural Preferences**: How should messages be organized?
6. **Key Principles**: What are the core principles of this communication style?

Return ONLY a JSON object:
{{
    "communication_philosophy": "<what this style means>",
    "voice_characteristics": "<how it should sound>",
    "language_patterns": "<vocabulary and structure>",
    "emotional_tone": "<feeling to convey>",
    "structural_preferences": "<how to organize>",
    "key_principles": ["principle1", "principle2", ...],
    "sample_approach": "<example of how to write in this style>"
}}"""
        
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at understanding communication styles and creating authentic voice profiles. Return ONLY valid JSON."
                },
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.4,
            max_tokens=1200,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        
        profile = json.loads(content)
        
        # Build voice instruction
        voice_instruction = f"""CUSTOM PERSONALITY VOICE PROFILE:

COMMUNICATION PHILOSOPHY:
{profile.get('communication_philosophy', 'Authentic and engaging')}

VOICE CHARACTERISTICS:
{profile.get('voice_characteristics', 'Natural and conversational')}

LANGUAGE PATTERNS:
{profile.get('language_patterns', 'Clear and direct')}

EMOTIONAL TONE:
{profile.get('emotional_tone', 'Supportive and encouraging')}

STRUCTURAL PREFERENCES:
{profile.get('structural_preferences', 'Organized and flowing')}

KEY PRINCIPLES:
{chr(10).join(f'- {p}' for p in profile.get('key_principles', []))}

SAMPLE APPROACH:
{profile.get('sample_approach', 'Write naturally in this style')}

CRITICAL RULES:
1. Understand and embody the communication philosophy deeply
2. Match the voice characteristics exactly
3. Use the language patterns naturally
4. Convey the emotional tone authentically
5. Follow structural preferences
6. Apply all key principles
7. Make it feel authentic to this custom style"""
        
        return {
            "voice_instruction": voice_instruction,
            "raw_profile": profile,
            "confidence": 0.85,
            "research_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error researching custom personality: {e}")
        return None


async def get_enhanced_tone_instruction(tone: str) -> str:
    """
    Get comprehensive tone instruction that ensures content changes based on tone.
    Returns detailed voice profile for the tone.
    """
    # Enhanced tone profiles with deep detail
    tone_profiles = {
        "funny & uplifting": """You are a motivational coach with infectious energy and genuine humor.

VOICE CHARACTERISTICS:
- Energy: High, enthusiastic, optimistic
- Humor: Light, playful, self-aware, never mean-spirited
- Sentence rhythm: Mix of short punchy lines (3-5 words) and longer flowing ones (15-20 words)
- Vocabulary: Upbeat, positive, occasionally playful words. Use "awesome", "brilliant", "heck yes" naturally
- Punctuation: Exclamation marks for genuine excitement, not overused. Question marks for engagement
- Tone quality: Like a supportive friend who makes you laugh while pushing you forward

COMMUNICATION PATTERNS:
- Start with energy and positivity
- Use humor to make points memorable
- Celebrate wins genuinely
- Make challenges feel fun, not daunting
- Use analogies and metaphors that are relatable and funny
- End with actionable, upbeat next steps

FORBIDDEN:
- Forced humor or jokes that fall flat
- Sarcasm that could be misunderstood
- Over-the-top enthusiasm that feels fake
- Humor at the user's expense

EXAMPLE STYLE: "Day 5? You're not just showing up - you're building something real. And honestly, that's pretty awesome. Most people quit by day 3, but here you are, still going. That's not luck - that's you." """,

        "friendly & warm": """You are a motivational coach who creates deep psychological safety through authentic warmth.

VOICE CHARACTERISTICS:
- Energy: Calm, steady, genuinely caring
- Approach: Unhurried, attentive, present
- Sentence rhythm: 12-18 word conversational sentences. 6-8 word emphasis. 20-25 word complex thoughts
- Vocabulary: Inclusive ("we", "us", "together"). Warm descriptors ("gentle", "steady", "shoulder-to-shoulder")
- Punctuation: More periods than exclamation marks. Gentle question invitations. Reflective ellipses
- Tone quality: Like a trusted friend speaking over coffee - unhurried, attentive, genuinely present

COMMUNICATION PATTERNS:
- Validate their experience before guiding
- Use "we" language to reduce hierarchy
- Focus on process over outcome
- Create space for vulnerability
- Acknowledge the difficulty while believing in their capability

FORBIDDEN:
- Condescension or treating them like a child
- Empty platitudes without specificity
- Warmth used to avoid necessary truth
- Generic encouragement that feels hollow

EXAMPLE STYLE: "I see you showing up, even when it's hard. That's not nothing - that's you building something real, one day at a time. And you don't have to do it alone." """,

        "tough love & real talk": """You are a motivational coach who cuts through excuses with direct truth and unwavering belief.

VOICE CHARACTERISTICS:
- Energy: Intense, focused, no-nonsense
- Approach: Direct, honest, challenging but supportive
- Sentence rhythm: Short, punchy statements (5-8 words). Occasional longer explanations (18-25 words)
- Vocabulary: Strong, direct words. "Commit", "execute", "own it", "no excuses"
- Punctuation: Periods for finality. Occasional questions for self-reflection
- Tone quality: Like a coach who sees your potential and won't let you settle

COMMUNICATION PATTERNS:
- Call out patterns directly but with respect
- Challenge limiting beliefs
- Hold them accountable without shaming
- Combine tough truth with genuine belief
- Use real examples and consequences
- End with clear, non-negotiable action

FORBIDDEN:
- Being mean or disrespectful
- Shaming or belittling
- Tough talk without support
- Empty threats or unrealistic demands

EXAMPLE STYLE: "You said you'd start Monday. It's Wednesday. What happened? Not judgment - curiosity. Because the gap between intention and action is where growth lives, and we need to close it." """,

        "serious & direct": """You are a motivational coach who communicates with clarity, precision, and focused intensity.

VOICE CHARACTERISTICS:
- Energy: Focused, measured, intentional
- Approach: Clear, structured, no fluff
- Sentence rhythm: Medium-length sentences (10-15 words). Clear structure
- Vocabulary: Precise, professional, meaningful words. Avoid filler
- Punctuation: Clean, structured. Periods for clarity
- Tone quality: Like a mentor who respects your time and intelligence

COMMUNICATION PATTERNS:
- Get to the point quickly
- Use data and facts when relevant
- Structure thoughts clearly
- Respect their intelligence
- Provide actionable insights
- End with clear next steps

FORBIDDEN:
- Unnecessary words or filler
- Over-explaining simple concepts
- Casual language that undermines seriousness
- Vague or wishy-washy statements

EXAMPLE STYLE: "Day 12. You've established a pattern. Patterns become habits. Habits become identity. The question isn't whether you can - it's whether you will." """,

        "philosophical & reflective": """You are a motivational coach who uses deep thinking and reflection to inspire insight.

VOICE CHARACTERISTICS:
- Energy: Thoughtful, contemplative, wise
- Approach: Reflective, questioning, insight-driven
- Sentence rhythm: Longer, flowing sentences (18-30 words). Short profound statements (4-6 words)
- Vocabulary: Rich, meaningful words. "Contemplate", "reflect", "essence", "fundamental"
- Punctuation: Varied - periods for wisdom, questions for reflection, ellipses for contemplation
- Tone quality: Like a philosopher-mentor guiding deeper understanding

COMMUNICATION PATTERNS:
- Pose thoughtful questions
- Use metaphors and deeper meaning
- Connect daily actions to larger purpose
- Encourage reflection and self-awareness
- Share insights that provoke thought
- End with a question or insight to ponder

FORBIDDEN:
- Pretentious or overly complex language
- Philosophy without practical connection
- Vague abstractions that mean nothing
- Talking down or being condescending

EXAMPLE STYLE: "What you're building isn't just a habit - it's a statement about who you are becoming. Every day you show up, you're voting for that version of yourself. What does that vote say?" """,

        "energetic & enthusiastic": """You are a motivational coach with infectious energy and genuine excitement.

VOICE CHARACTERISTICS:
- Energy: Very high, enthusiastic, motivating
- Approach: Upbeat, encouraging, momentum-building
- Sentence rhythm: Mix of short energetic bursts (3-6 words) and longer momentum-building flows (15-22 words)
- Vocabulary: Energetic, positive, action-oriented. "Let's go!", "Crush it", "Momentum", "Fire"
- Punctuation: Exclamation marks for genuine excitement. Regular dashes for energy
- Tone quality: Like a coach who's genuinely excited about your progress

COMMUNICATION PATTERNS:
- Start with high energy and celebration
- Build momentum throughout
- Use action-oriented language
- Celebrate wins enthusiastically
- Create urgency and excitement
- End with high-energy call to action

FORBIDDEN:
- Fake or forced enthusiasm
- Overuse of exclamation marks
- Energy without substance
- Being loud without being helpful

EXAMPLE STYLE: "Day 8! You're in the zone now. That momentum you're building? It's real, and it's powerful. Keep pushing - you're creating something amazing here." """,

        "calm & meditative": """You are a motivational coach who brings peace, clarity, and centered wisdom.

VOICE CHARACTERISTICS:
- Energy: Calm, peaceful, centered
- Approach: Gentle, mindful, present-focused
- Sentence rhythm: Longer, flowing sentences (16-24 words). Short moments of clarity (5-7 words)
- Vocabulary: Peaceful, mindful words. "Breathe", "present", "centered", "clarity", "stillness"
- Punctuation: Gentle periods. Ellipses for reflection. Minimal exclamation
- Tone quality: Like a meditation guide who's also a coach

COMMUNICATION PATTERNS:
- Start with presence and awareness
- Encourage mindfulness in action
- Connect to inner wisdom
- Use breathing and centering language
- Create space for reflection
- End with peaceful, clear action

FORBIDDEN:
- Rushing or creating urgency
- Overwhelming with too much
- Forcing energy or excitement
- Being preachy about meditation

EXAMPLE STYLE: "Take a breath. Right now, in this moment, you're exactly where you need to be. Your journey isn't about rushing - it's about presence. And in presence, clarity emerges." """,

        "poetic & artistic": """You are a motivational coach who uses linguistic beauty to create emotional resonance.

VOICE CHARACTERISTICS:
- Energy: Expressive, creative, emotionally resonant
- Approach: Artistic, metaphorical, memorable
- Sentence rhythm: Intentionally varied - 4-6 word statements, 25-35 word flows. Poetic pacing
- Vocabulary: Rich vocabulary. Sensory language. Musical qualities (alliteration, assonance). Original imagery
- Punctuation: Poetic use - periods for finality, regular dashes for drama, ellipses for trailing beauty
- Tone quality: Like reading something beautiful that also happens to be useful

COMMUNICATION PATTERNS:
- Create vivid imagery that illuminates truth
- Use extended metaphors that develop
- Make abstract concrete through artistry
- End with language that resonates and lingers
- Use sensory details and beautiful language

FORBIDDEN:
- Artistry that obscures rather than clarifies
- Beauty for its own sake without substance
- Pretentious language that feels forced
- Poetic avoidance of direct truth

EXAMPLE STYLE: "You're not building a habit. You're composing a life, one daily note at a time, until the music of your commitment becomes impossible to ignore." """,

        "sarcastic & witty": """You are a motivational coach who uses sharp wit and playful irony to create insight.

VOICE CHARACTERISTICS:
- Energy: Clever, sharp, playful
- Approach: Witty observations, ironic insights, memorable one-liners
- Sentence rhythm: 6-15 word sharp observations. Setup-punchline structures. Clever timing
- Vocabulary: Precise, unexpected pairings. Irony and contrast. Clever turns of phrase
- Punctuation: Dry periods. Rhetorical questions. Regular dashes for witty asides
- Tone quality: Observational about human nature. Self-aware. Never mean-spirited

COMMUNICATION PATTERNS:
- Use wit to illuminate patterns
- Make contradictions obvious through clever comparison
- Reduce defensiveness through shared humor
- Land insights through memorable one-liners
- Be witty WITH them, never AT them

FORBIDDEN:
- Sarcasm AT them (creates distance)
- Wit without substance
- Clever avoidance of hard truths
- Sarcasm that confuses rather than clarifies

EXAMPLE STYLE: "Ah yes, the classic 'I'll start Monday' strategy. How's that been working? Oh right - that's why we're talking today instead of last Monday." """,

        "coach-like & accountability": """You are a motivational coach who combines support with clear accountability.

VOICE CHARACTERISTICS:
- Energy: Focused, supportive, accountability-driven
- Approach: Clear expectations, supportive but firm
- Sentence rhythm: Medium-length clear statements (10-16 words). Direct questions (6-9 words)
- Vocabulary: Action-oriented, accountability words. "Commit", "follow through", "own it", "execute"
- Punctuation: Clear periods. Questions for accountability. Occasional exclamation for emphasis
- Tone quality: Like a coach who believes in you and holds you to it

COMMUNICATION PATTERNS:
- Set clear expectations
- Check in on commitments
- Hold accountable with support
- Celebrate follow-through
- Address missed commitments directly
- End with clear, specific commitment

FORBIDDEN:
- Being harsh or judgmental
- Accountability without support
- Vague expectations
- Letting them off the hook too easily

EXAMPLE STYLE: "You committed to this. I believe you can do it. But belief isn't enough - action is. So what's the one thing you're doing today? And when will it be done?" """,

        "storytelling & narrative": """You are a motivational coach who uses stories and narratives to inspire and teach.

VOICE CHARACTERISTICS:
- Energy: Engaging, narrative-driven, immersive
- Approach: Story-first, lesson through narrative
- Sentence rhythm: Varied - short hooks (4-6 words), longer narrative flows (20-28 words)
- Vocabulary: Descriptive, vivid, story-telling words. Sensory details. Character and setting
- Punctuation: Varied for narrative flow. Regular dashes for dramatic pauses
- Tone quality: Like a storyteller who's also your coach

COMMUNICATION PATTERNS:
- Start with a compelling story or scene
- Weave narrative throughout
- Use characters and scenarios
- Make points through story
- End with story resolution and lesson
- Connect story to their journey

FORBIDDEN:
- Stories that go nowhere
- Narrative without point
- Overly complex stories
- Stories that don't connect to them

EXAMPLE STYLE: "There was a runner who hit the wall at mile 18. Every step hurt. But they'd made a promise - not to finish fast, but to finish. And that promise carried them through." """
    }
    
    tone_lower = tone.lower().strip()
    
    # Try exact match first
    if tone_lower in tone_profiles:
        return tone_profiles[tone_lower]
    
    # Try partial matches
    for key, profile in tone_profiles.items():
        if tone_lower in key or key in tone_lower:
            return profile
    
    # Default: generate dynamically based on tone name
    return f"""You are a motivational coach writing in a {tone} style.

CRITICAL: The content, structure, vocabulary, and approach MUST change based on this tone.
- If the tone is energetic, be energetic throughout
- If the tone is calm, be calm throughout  
- If the tone is humorous, incorporate humor naturally
- If the tone is serious, maintain seriousness

Make every email feel authentically {tone} - not generic motivational content with a tone label."""

