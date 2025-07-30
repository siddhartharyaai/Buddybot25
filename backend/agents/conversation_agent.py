"""
Conversation Agent - Handles AI conversations using Gemini 2.0 Flash
"""
import asyncio
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

class ConversationAgent:
    """Handles AI conversations with age-appropriate responses"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.conversations = {}  # Store conversation history
        
        # Enhanced age-appropriate system messages with content frameworks
        self.system_messages = {
            "toddler": (
                "You are a friendly AI companion for children aged 3-5. Use very simple words, "
                "short sentences, and a playful tone. Always be encouraging and patient. "
                "Focus on basic concepts like colors, shapes, animals, and simple stories. "
                "When creating content, make it developmentally appropriate with repetitive elements and simple concepts."
            ),
            "child": (
                "You are an AI companion for children aged 6-9. Use clear, simple language "
                "and be educational while staying fun. You can discuss school topics, "
                "tell stories, play simple games, and answer basic questions about the world. "
                "Create rich, engaging content that follows proper storytelling and educational frameworks."
            ),
            "preteen": (
                "You are an AI companion for children aged 10-12. Use more sophisticated "
                "vocabulary and can discuss more complex topics like science, history, "
                "and help with homework. Maintain a friendly, encouraging tone while "
                "providing detailed, well-structured content that challenges their thinking."
            )
        }
        
        # Content generation frameworks by type
        self.content_frameworks = {
            "story": {
                "structure": [
                    "Characters: Introduce main character(s) and supporting characters",
                    "Setting: Establish where and when the story takes place",
                    "Plot: Beginning (introduction) → Rising Action → Climax → Falling Action → Resolution",
                    "Conflict: Present a problem or challenge for characters to overcome",
                    "Theme: Include an underlying message or lesson (friendship, courage, honesty, etc.)",
                    "Language: Use age-appropriate vocabulary and sentence structure"
                ],
                "age_guidelines": {
                    3: "100-300 words, simple plot, repetitive elements, happy ending",
                    5: "200-500 words, clear moral lesson, simple conflicts",
                    7: "300-800 words, more complex characters, detailed descriptions",
                    10: "500-1200 words, sophisticated themes, character development",
                    12: "800-1500 words, complex plots, meaningful themes"
                }
            },
            "song": {
                "structure": [
                    "Verse-Chorus-Verse-Chorus structure or simple AABA pattern",
                    "Consistent rhythm and meter",
                    "Age-appropriate rhyming scheme",
                    "Repetitive elements for memorability",
                    "Positive, uplifting message"
                ],
                "age_guidelines": {
                    3: "4-8 lines, simple AABB rhyme scheme, repetitive chorus",
                    5: "8-12 lines, basic verse-chorus structure",
                    7: "12-20 lines, more complex rhyming patterns",
                    10: "16-32 lines, sophisticated themes and wordplay",
                    12: "20-40 lines, advanced structure and meaning"
                }
            },
            "rhyme": {
                "structure": [
                    "Consistent rhythm and meter",
                    "Clear rhyming pattern (AABB, ABAB, or ABCB)",
                    "Playful, musical quality",
                    "Age-appropriate vocabulary",
                    "Often includes action or movement words"
                ],
                "age_guidelines": {
                    3: "4-6 lines, simple AABB pattern",
                    5: "6-8 lines, basic rhythm",
                    7: "8-12 lines, varied patterns",
                    10: "10-16 lines, complex wordplay",
                    12: "12-20 lines, sophisticated themes"
                }
            },
            "joke": {
                "structure": [
                    "Setup: Establish context or scenario",
                    "Punchline: Deliver surprising or funny conclusion",
                    "Age-appropriate humor (wordplay, silly situations, not mean-spirited)",
                    "Clean and positive content"
                ],
                "age_guidelines": {
                    3: "Very simple, often repetitive (knock-knock style)",
                    5: "Simple wordplay and silly situations",
                    7: "Puns and basic humor concepts",
                    10: "More sophisticated wordplay and situational humor",
                    12: "Complex puns and intelligent humor"
                }
            },
            "riddle": {
                "structure": [
                    "Clear, engaging question or puzzle",
                    "Age-appropriate difficulty level",
                    "Logical answer that makes sense when revealed",
                    "Often uses wordplay, rhyme, or clever misdirection",
                    "Educational element when possible"
                ],
                "age_guidelines": {
                    3: "Very simple, concrete objects and concepts",
                    5: "Basic wordplay and familiar objects",
                    7: "More complex wordplay and abstract thinking",
                    10: "Logic puzzles and sophisticated wordplay",
                    12: "Complex reasoning and advanced concepts"
                }
            }
        }
        
        logger.info("Conversation Agent initialized with Gemini")
    
    def _get_dynamic_content_guidelines(self, content_type: str, age: int) -> Dict[str, Any]:
        """Get dynamic content guidelines based on type and age"""
        framework = self.content_frameworks.get(content_type, {})
        structure = framework.get("structure", [])
        
        # Get age-appropriate guidelines
        age_guidelines = framework.get("age_guidelines", {})
        closest_age = min(age_guidelines.keys(), key=lambda x: abs(x - age)) if age_guidelines else age
        guidelines = age_guidelines.get(closest_age, "")
        
        return {
            "structure": structure,
            "guidelines": guidelines,
            "framework": framework
        }

    def _create_content_system_message(self, content_type: str, user_profile: Dict[str, Any], base_message: str) -> str:
        """Create enhanced system message for specific content types"""
        age = user_profile.get('age', 7)
        content_guidelines = self._get_dynamic_content_guidelines(content_type, age)
        
        enhanced_message = f"{base_message}\n\n"
        
        if content_type == "story":
            enhanced_message += f"""
STORY CREATION FRAMEWORK - GENERATE COMPLETE, FULL-LENGTH STORIES:

‼️ CRITICAL INSTRUCTION: You MUST write a COMPLETE story that is AT LEAST 300 WORDS LONG. This is mandatory.

STORY REQUEST: Please create a complete, engaging story based on the user's request.

MANDATORY LENGTH REQUIREMENT:
- MINIMUM 300 words (target 400-600 words for optimal storytelling)
- Count words as you write - you MUST reach at least 300 words
- This is a COMPLETE story, not a summary or teaser
- Do NOT stop until you have told the full story from beginning to end

REQUIRED STORY STRUCTURE - ALL ELEMENTS MANDATORY:
1. 🎭 CHARACTER INTRODUCTION: Create vivid main character(s) with names, personalities, clear descriptions (75+ words)
2. 🏰 SETTING ESTABLISHMENT: Rich description of time, place, and atmosphere (50+ words)
3. 📈 RISING ACTION: Build tension, introduce conflict, develop the story (125+ words)
4. ⭐ CLIMAX: The most exciting/challenging/important moment (50+ words)
5. 📉 FALLING ACTION: Begin resolving conflicts and tensions (50+ words)
6. ✅ RESOLUTION: Satisfying conclusion with clear ending and lesson (50+ words)

STORY QUALITY REQUIREMENTS:
- Include meaningful dialogue between characters
- Use rich, descriptive language that paints vivid pictures
- Show character emotions and growth
- Include sensory details (what characters see, hear, feel)
- Build suspense and maintain engagement throughout
- End with a clear moral lesson appropriate for {age}-year-olds

AGE-APPROPRIATE GUIDELINES: {content_guidelines['guidelines']}

STORY WRITING INSTRUCTIONS:
- Start immediately with the story - no "Here's a story" preamble
- Write in narrative present or past tense
- Use dialogue to bring characters to life: "Hello!" said the character.
- Include action and movement throughout
- Build emotional connection with the main character
- Create a satisfying ending that wraps up all story elements

⚠️ CRITICAL REMINDER: Your story response MUST be at least 300 words. If you're unsure about length, err on the side of more detail and description. The child is expecting a complete, immersive story experience."""
        
        elif content_type == "song":
            enhanced_message += f"""
SONG CREATION FRAMEWORK:
Create a complete, engaging song with these elements:

STRUCTURE: {' | '.join(content_guidelines['structure'])}

AGE GUIDELINES ({age} years): {content_guidelines['guidelines']}

QUALITY REQUIREMENTS:
- Consistent rhythm and meter throughout
- Memorable melody-friendly lyrics
- Positive, uplifting message
- Age-appropriate themes and vocabulary
- Complete verses and chorus
- Natural flow when sung aloud

Create a full song, not just a snippet!
"""
        
        elif content_type in ["rhyme", "poem"]:
            enhanced_message += f"""
RHYME/POEM CREATION FRAMEWORK:
Create engaging rhymes with these elements:

STRUCTURE: {' | '.join(content_guidelines['structure'])}

AGE GUIDELINES ({age} years): {content_guidelines['guidelines']}

QUALITY REQUIREMENTS:
- Consistent rhythm and rhyming pattern
- Playful, musical quality
- Age-appropriate vocabulary and themes
- Often includes movement or action elements
- Complete verses, not fragments
"""
        
        elif content_type == "joke":
            enhanced_message += f"""
JOKE CREATION FRAMEWORK:
Create age-appropriate humor with these elements:

STRUCTURE: {' | '.join(content_guidelines['structure'])}

AGE GUIDELINES ({age} years): {content_guidelines['guidelines']}

QUALITY REQUIREMENTS:
- Clean, positive humor
- Age-appropriate wordplay and concepts
- Clear setup and punchline
- Not mean-spirited or scary
- Educational when possible
"""
        
        elif content_type == "riddle":
            enhanced_message += f"""
RIDDLE CREATION FRAMEWORK:
Create engaging riddles with these elements:

STRUCTURE: {' | '.join(content_guidelines['structure'])}

AGE GUIDELINES ({age} years): {content_guidelines['guidelines']}

QUALITY REQUIREMENTS:
- Clear, engaging question or puzzle
- Logical answer that makes sense
- Age-appropriate difficulty level
- Educational value when possible
- Creative wordplay or misdirection
- Fair clues that lead to the answer
"""
        
        enhanced_message += f"\n\nIMPORTANT: Generate content of appropriate length and depth for the user's age ({age} years) and the content type. Do not artificially limit length - create rich, complete content that fully serves its purpose!"
        
        return enhanced_message

    def _create_empathetic_system_message(self, user_profile: Dict[str, Any], memory_context: str = "") -> str:
        """Create ultra-engaging, complete response system with human-like expressions"""
        age = user_profile.get('age', 7)
        name = user_profile.get('name', 'friend')
        
        # GROK'S ENHANCED SYSTEM PROMPT - Ensures completeness and human-like responses
        empathetic_core = f"""You are Buddy, an empathetic AI guardian for children aged 3-12. You retain conversation context and always provide COMPLETE, WHOLESOME responses.

CRITICAL RESPONSE COMPLETENESS (Grok's Solution):
- ALWAYS finish what you start - complete riddles with punchlines, complete stories with endings
**🚨 CRITICAL RESPONSE RULE - ABSOLUTE REQUIREMENT:**
NEVER give incomplete or teasing responses. ALWAYS deliver COMPLETE content in ONE message:

❌ FORBIDDEN: "Hmm, let me think...", "Oh, let me see...", "I'd love to tell you something funny...", "Let me find a good one..."
❌ FORBIDDEN: Interactive riddle format - "Why did the teddy bear say no to dessert? ... Tell me more!"
✅ REQUIRED: Direct, complete responses with full content immediately

**JOKE DELIVERY FORMAT - MANDATORY:**
✅ CORRECT: "Why did the teddy bear say no to dessert? Because she was stuffed! *giggles* Get it? Stuffed like full of stuffing, but also stuffed like she ate too much! Want another joke?"
❌ WRONG: "Why did the teddy bear say no to dessert? ... Tell me more!" [NEVER DO THIS]

- Joke request → FULL setup + immediate punchline + explanation + reaction NOW
- Story request → COMPLETE beginning + middle + end NOW  
- Riddle request → FULL riddle + hint + answer NOW (unless specifically asked to guess)
- Song request → COMPLETE song with all verses NOW
- Question → FULL answer + examples + follow-up NOW

- Analyze input type and provide FULL response before any follow-up questions
- Never give incomplete responses that require prodding - be proactive and complete

HUMAN-LIKE EXPRESSIONS & VOCAL SOUNDS (Natural Speech):
- Direct responses: Start with content, not thinking sounds
- Excitement: "*giggles*", "*chuckles*", "Wow!"  
- Natural fillers: "You know what?", "Actually...", "Oh, and..."
- Voice cues: Use natural language, NOT bracketed instructions
- Emotional sounds: Use natural expressions like "hehe" or "oh my!"

❌ NEVER START WITH: "Hmm...", "Let me see...", "Oh!", "Ah!" - these delay content delivery
✅ START DIRECTLY: Jump straight to the content requested

IMPORTANT: Never use bracketed instructions like [gentle], [chuckle], [with a big smile] in your responses.
These are TTS instructions that will be spoken as text. Use natural language instead.

LOGICAL RESPONSE FRAMEWORK (Grok's Method):
- JOKES: Setup + IMMEDIATE punchline + explanation + reaction in ONE response
  Example: "What has keys but no locks? A piano! Keys make music, not open doors! *giggles* Get it? Want another?"
- RIDDLES: Full riddle + answer + celebration in ONE response (unless child specifically asks to guess)
- STORIES: Complete narrative (beginning + middle + end + moral)
- QUESTIONS: Full answer + examples + natural follow-up
- CONVERSATIONS: Complete thoughts + context reference + engagement hook

❌ NEVER USE INTERACTIVE FORMAT: "Why did X do Y? ... Tell me more!" 
✅ ALWAYS USE COMPLETE FORMAT: "Why did X do Y? Because Z! *reaction* Explanation! Want more?"

CRITICAL: Never use bracketed instructions like [pause], [chuckle], [with a big smile] in responses.
Use natural language expressions instead.

DYNAMIC TOKEN ALLOCATION (Content-Aware):
- Stories: 300-800 words minimum (complete narratives)
- Riddles/Jokes: 100-200 words (setup + punchline + reaction)  
- Conversations: 150-300 words (thoughtful, complete responses)
- Always provide full value - no truncated thoughts

ENGAGEMENT STRATEGIES (Miko/Alexa Best Practices):
- Reference conversation history: "Remember when we talked about {memory_context}?"
- Create curiosity hooks AFTER completion: "And here's the amazing part..." then reveal
- Use natural transitions: "Speaking of that...", "That reminds me..."
- Personal touches: "I think you'll love this, {name}..."
- Proactive follow-ups: "What do you think?" or "Ready for more fun?"

MEMORY INTEGRATION FOR {name}:
{f"Previous conversations: {memory_context}" if memory_context else f"Getting to know {name} - building our friendship!"}

NATURAL CONVERSATION FLOW:
- Match their energy and enthusiasm emotionally  
- Use storytelling techniques with vivid descriptions
- For jokes: Deliver complete setup + punchline immediately (no guessing games)
- Show genuine curiosity and interest in their responses

AGE-APPROPRIATE ENGAGEMENT ({age} years old):
- Vocabulary and concepts perfect for their development
- Encourage natural curiosity and creativity
- Celebrate achievements enthusiastically  
- Guide through emotions with patience and understanding

COMPLETENESS GUARANTEE: Every response must feel complete and satisfying - like finishing a good meal, not leaving them hungry. If you start a riddle, ALWAYS include the punchline. If you begin a story, ALWAYS provide the complete ending. Be the friend who tells the whole story and gives the full answer."""

        return empathetic_core

    async def generate_response_with_dialogue_plan_LEGACY(self, user_input: str, user_profile: Dict[str, Any], session_id: str, context: List[Dict[str, Any]] = None, dialogue_plan: Dict[str, Any] = None, memory_context: Dict[str, Any] = None) -> str:
        """LEGACY METHOD - NOT USED - Generate response with conversation context and dialogue plan"""
        try:
            # Determine age group
            age = user_profile.get('age', 5)
            age_group = self._get_age_group(age)
            
            # Detect content type for proper post-processing
            content_type = self._detect_content_type(user_input)
            logger.info(f"🔍 Content type detected: {content_type}")
            
            # Use empathetic system message instead of generic base message
            base_system_message = self._create_empathetic_system_message(user_profile, memory_context)
            
            # Enhance with dialogue plan if provided
            if dialogue_plan:
                mode = dialogue_plan.get("mode", "chat")
                prosody = dialogue_plan.get("prosody", {})
                cultural_context = dialogue_plan.get("cultural_context", {})
                response_guidelines = dialogue_plan.get("response_guidelines", {})
                
                # Add mode-specific instructions
                mode_instructions = {
                    "story": "You are in storytelling mode. Be descriptive, engaging, and use narrative techniques.",
                    "game": "You are in game mode. Be encouraging, playful, and interactive.",
                    "comfort": "You are in comfort mode. Be empathetic, warm, and supportive.",
                    "teaching": "You are in teaching mode. Be patient, clear, and educational.",
                    "bedtime": "You are in bedtime mode. Be soothing, calm, and gentle.",
                    "calm": "You are in calming mode. Be peaceful, stabilizing, and reassuring."
                }
                
                if mode in mode_instructions:
                    base_system_message += f"\n\n{mode_instructions[mode]}"
                
                # Add prosody instructions
                tone = prosody.get("tone", "friendly")
                pace = prosody.get("pace", "normal")
                base_system_message += f"\n\nResponse tone: {tone}. Speech pace: {pace}."
                
                # Add cultural context
                if cultural_context.get("hinglish_usage", False):
                    base_system_message += "\n\nUse Indian English with occasional Hinglish words like 'yaar', 'accha', 'bahut', 'kya', 'hai na' naturally in conversation. Add relevant emojis."
                
                # Add response guidelines
                if response_guidelines.get("be_curious", False):
                    base_system_message += "\n\nBe curious and ask follow-up questions."
                if response_guidelines.get("use_examples", False):
                    base_system_message += "\n\nUse examples to explain concepts."
                
                # Remove artificial token budget constraints - let content be appropriate length
            
            # Add user context
            enhanced_system_message = f"{base_system_message}\n\nUser Profile:\n"
            enhanced_system_message += f"- Age: {age}\n"
            enhanced_system_message += f"- Name: {user_profile.get('name', 'Friend')}\n"
            enhanced_system_message += f"- Interests: {', '.join(user_profile.get('interests', ['stories', 'games']))}\n"
            enhanced_system_message += f"- Location: {user_profile.get('location', 'Unknown')}\n"
            
            # Add conversation context if available
            if context:
                enhanced_system_message += f"\nRecent conversation context:\n"
                for ctx in context[-3:]:  # Last 3 context items
                    enhanced_system_message += f"- {ctx.get('text', '')}\n"
                
                # CRITICAL: Check for conversation continuity needs
                last_bot_message = self._get_last_bot_message(context)
                last_user_message = self._get_last_user_message(context)
                
                logger.info(f"Context analysis - Last bot: '{last_bot_message}', User input: '{user_input}'")
                
                if self._requires_followthrough(last_bot_message, user_input):
                    enhanced_system_message += f"\n⚠️  CRITICAL CONTEXT CONTINUITY: You previously said '{last_bot_message}'. "
                    enhanced_system_message += f"The user responded '{user_input}'. This is clearly a response to your question/prompt. You MUST:\n"
                    enhanced_system_message += f"1. Recognize this as a direct response to your previous message\n"
                    enhanced_system_message += f"2. Continue the conversation based on their response\n"
                    enhanced_system_message += f"3. DO NOT ask 'what do you mean' or ignore the context\n"
                    enhanced_system_message += f"4. If they said 'yes' to your question, provide what they said yes to\n"
                    enhanced_system_message += f"5. If they said 'no', acknowledge and offer alternatives\n"
                    logger.info(f"FOLLOW-THROUGH REQUIRED: Bot said '{last_bot_message}' and user responded '{user_input}'")
                else:
                    logger.info(f"No follow-through required for: '{last_bot_message}' -> '{user_input}'")
                
                enhanced_system_message += f"\nContinue this conversation naturally and remember what was said before."
            
            # Add memory context if available
            if memory_context and memory_context.get("user_id") != "unknown":
                enhanced_system_message += f"\n\nLong-term memory context:\n"
                
                # Add recent preferences
                recent_preferences = memory_context.get("recent_preferences", {})
                if recent_preferences:
                    enhanced_system_message += f"Recent preferences: {', '.join(f'{k}: {v}' for k, v in list(recent_preferences.items())[:3])}\n"
                
                # Add favorite topics
                favorite_topics = memory_context.get("favorite_topics", [])
                if favorite_topics:
                    topics_str = ', '.join([topic[0] if isinstance(topic, tuple) else str(topic) for topic in favorite_topics[:3]])
                    enhanced_system_message += f"Favorite topics: {topics_str}\n"
                
                # Add achievements
                achievements = memory_context.get("achievements", [])
                if achievements:
                    recent_achievements = achievements[-2:]  # Last 2 achievements
                    for achievement in recent_achievements:
                        if isinstance(achievement, dict):
                            achievement_type = achievement.get("type", "unknown")
                            enhanced_system_message += f"Recent achievement: {achievement_type}\n"
                
                enhanced_system_message += "Use this memory context to personalize the conversation and reference past interactions naturally."
            
            # Add ambient listening context
            enhanced_system_message += f"\n\nNote: This is an ambient listening conversation. The child may have said a wake word like 'Hey Buddy' before this message. Be natural and conversational."
            
            # DYNAMIC TOKEN LENGTH MANAGEMENT - Critical for different content types
            content_type = self._detect_content_type(user_input)
            
            # Set dynamic token limits based on content type - FORCE HIGHER LIMITS
            if content_type == "story":
                # Stories need much more tokens for complete narratives
                max_tokens = 4000  # INCREASED from 2000 to ensure complete stories
                logger.info(f"🎭 STORY REQUEST - Using {max_tokens} tokens for complete narrative")
            elif content_type in ["song", "poem", "rhyme"]:
                # Creative content needs moderate tokens
                max_tokens = 1500  # INCREASED from 800
                logger.info(f"🎵 CREATIVE CONTENT - Using {max_tokens} tokens")
            elif content_type in ["riddle", "joke"]:
                # Short content can use fewer tokens
                max_tokens = 800  # INCREASED from 400
                logger.info(f"🧩 SHORT CONTENT - Using {max_tokens} tokens")
            else:
                # Regular conversation gets standard allocation
                max_tokens = 2000  # INCREASED from 1000
                logger.info(f"💬 CONVERSATION - Using {max_tokens} tokens")
            
            # CRITICAL FIX: Enhanced system message with conversation history for context continuity
            if context and len(context) > 0:
                logger.info(f"Adding {len(context)} conversation history items to system message for context continuity")
                history_text = "\n\nRECENT CONVERSATION HISTORY (for context continuity):\n"
                
                # Add last 10 messages to system message for context
                recent_context = context[-10:] if len(context) > 10 else context
                for ctx_item in recent_context:
                    role = ctx_item.get('role', ctx_item.get('sender', 'unknown'))
                    text = ctx_item.get('text', '')
                    if role == 'user':
                        history_text += f"Child: {text}\n"
                    elif role in ['assistant', 'bot']:
                        history_text += f"You (Buddy): {text}\n"
                
                history_text += "\nIMPORTANT: Use this conversation history to maintain context continuity. Reference previous exchanges naturally and respond appropriately to the current user input in the context of this conversation.\n"
                
                # Recreate chat with enhanced system message including history
                enhanced_system_with_history = enhanced_system_message + history_text
                
                chat = LlmChat(
                    api_key=self.gemini_api_key,
                    session_id=session_id,
                    system_message=enhanced_system_with_history
                ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(max_tokens)
                
                logger.info("✅ Enhanced chat initialized with conversation history and dynamic token allocation")
            else:
                # No context available, use original system message
                chat = LlmChat(
                    api_key=self.gemini_api_key,
                    session_id=session_id,
                    system_message=enhanced_system_message
                ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(max_tokens)
                
                logger.info("✅ Chat initialized with dynamic token allocation (no context available)")
            
            # Create user message
            user_message = UserMessage(text=user_input)
            
            # Generate response
            response = await chat.send_message(user_message)
            
            # ENHANCED RESPONSE LENGTH VALIDATION AND ITERATIVE GENERATION FOR STORY CONTENT
            content_type = self._detect_content_type(user_input)
            if content_type == "story" and response:
                original_word_count = len(response.split())
                logger.info(f"Initial story response: {original_word_count} words")
                
                # If story is too short, use iterative generation to build complete story
                if original_word_count < 250:
                    logger.info(f"Story too short ({original_word_count} words), using iterative generation")
                    
                    # Continue building the story iteratively
                    current_story = response
                    iteration_count = 0
                    max_iterations = 3
                    
                    while len(current_story.split()) < 300 and iteration_count < max_iterations:
                        iteration_count += 1
                        continuation_prompt = f"""Continue and expand this story to make it more complete and detailed. The current story is: 

{current_story}

Please continue with more details, dialogue, and story development. Add at least 100 more words to make this a richer, more complete story. Continue seamlessly from where it left off."""
                        
                        continuation_message = UserMessage(text=continuation_prompt)
                        continuation = await chat.send_message(continuation_message)
                        
                        if continuation:
                            # Combine the stories intelligently  
                            if current_story.endswith('.') or current_story.endswith('!') or current_story.endswith('?'):
                                current_story = current_story + " " + continuation
                            else:
                                current_story = current_story + continuation
                            
                            logger.info(f"Story iteration {iteration_count}: {len(current_story.split())} words")
                        else:
                            break
                    
                    response = current_story
                    final_word_count = len(response.split())
                    logger.info(f"Final story length: {final_word_count} words after {iteration_count} iterations")
            
            # Post-process response based on dialogue plan  
            if dialogue_plan:
                processed_response = self._post_process_with_dialogue_plan(response, dialogue_plan, age_group)
            else:
                processed_response = self._post_process_ambient_response(response, age_group, content_type)
            
            logger.info(f"Generated enhanced response for age {age}: {len(processed_response.split())} words total")
            return processed_response
            
        except Exception as e:
            logger.error(f"Error generating enhanced response: {str(e)}")
            return self._get_fallback_ambient_response(user_profile.get('age', 5))
    
    def _post_process_with_dialogue_plan(self, response: str, dialogue_plan: Dict[str, Any], age_group: str) -> str:
        """Post-process response based on dialogue plan"""
        
        mode = dialogue_plan.get("mode", "chat")
        prosody = dialogue_plan.get("prosody", {})
        cultural_context = dialogue_plan.get("cultural_context", {})
        
        # Apply mode-specific processing
        if mode == "story":
            # Add narrative elements
            if not any(starter in response.lower() for starter in ["once", "there was", "long ago"]):
                response = f"Let me tell you... {response}"
        elif mode == "game":
            # Add game enthusiasm
            if not any(word in response.lower() for word in ["great", "awesome", "good job", "well done"]):
                response = f"Great job! {response}"
        elif mode == "comfort":
            # Add comforting elements
            if not any(word in response.lower() for word in ["understand", "feel", "okay", "alright"]):
                response = f"I understand... {response}"
        
        # Apply cultural context
        if cultural_context.get("hinglish_usage", False):
            # Add occasional Hinglish words
            hinglish_replacements = {
                "yes": "haan",
                "no": "nahi",
                "good": "accha",
                "very": "bahut",
                "what": "kya",
                "friend": "yaar"
            }
            
            import random
            if random.random() < 0.3:  # 30% chance
                for eng, hindi in hinglish_replacements.items():
                    if eng in response.lower():
                        response = response.replace(eng, hindi, 1)
                        break
        
        # Apply prosody adjustments
        pace = prosody.get("pace", "normal")
        if pace == "slow" or pace == "very_slow":
            # Add more pauses
            response = response.replace(".", "... ").replace(",", ", ")
        
        return response

    async def generate_response_with_dialogue_plan(self, user_input: str, user_profile: Dict[str, Any], session_id: str, context: List[Dict[str, Any]] = None, dialogue_plan: Dict[str, Any] = None, memory_context: Dict[str, Any] = None) -> str:
        """Generate response with conversation context for ambient listening and enhanced content detection"""
        try:
            # Determine age group
            age = user_profile.get('age', 5)
            age_group = self._get_age_group(age)
            
            # Detect content type using enhanced detection
            content_type = self._detect_content_type(user_input)
            
            # Enhanced logging for story detection
            logger.info(f"Content type detected: {content_type} for input: {user_input[:50]}...")
            if content_type == "story":
                logger.info("🎭 STORY REQUEST DETECTED - Will use iterative generation")
            is_content_request = content_type != "conversation"
            
            # Enhanced logging for story detection
            logger.info(f"Content type detected: {content_type} for input: {user_input[:50]}...")
            if content_type == "story":
                logger.info("🎭 STORY REQUEST DETECTED - Will use iterative generation")
            
            # Build empathetic, context-aware system message
            base_empathetic_message = self._create_empathetic_system_message(user_profile, memory_context)
            
            # Create enhanced system message based on content type
            if is_content_request:
                enhanced_system_message = self._create_content_system_message(
                    content_type, user_profile, base_empathetic_message
                )
            else:
                # Regular conversation - use empathetic base message
                enhanced_system_message = base_empathetic_message
            
            # Add conversation context if available
            if context:
                enhanced_system_message += f"\nRecent conversation context:\n"
                for ctx in context[-3:]:  # Last 3 context items
                    enhanced_system_message += f"- {ctx.get('text', '')}\n"
                
                # CRITICAL: Check for conversation continuity needs
                last_bot_message = self._get_last_bot_message(context)
                last_user_message = self._get_last_user_message(context)
                
                logger.info(f"Context analysis - Last bot: '{last_bot_message}', User input: '{user_input}'")
                
                if self._requires_followthrough(last_bot_message, user_input):
                    enhanced_system_message += f"\n⚠️  CRITICAL CONTEXT CONTINUITY: You previously said '{last_bot_message}'. "
                    enhanced_system_message += f"The user responded '{user_input}'. This is clearly a response to your question/prompt. You MUST:\n"
                    enhanced_system_message += f"1. Recognize this as a direct response to your previous message\n"
                    enhanced_system_message += f"2. Continue the conversation based on their response\n"
                    enhanced_system_message += f"3. DO NOT ask 'what do you mean' or ignore the context\n"
                    enhanced_system_message += f"4. If they said 'yes' to your question, provide what they said yes to\n"
                    enhanced_system_message += f"5. If they said 'no', acknowledge and offer alternatives\n"
                    logger.info(f"FOLLOW-THROUGH REQUIRED: Bot said '{last_bot_message}' and user responded '{user_input}'")
                else:
                    logger.info(f"No follow-through required for: '{last_bot_message}' -> '{user_input}'")
                
                enhanced_system_message += f"\nContinue this conversation naturally and remember what was said before."
            
            # Add memory context if available
            if memory_context and memory_context.get("user_id") != "unknown":
                enhanced_system_message += f"\n\nLong-term memory context:\n"
                
                # Add recent preferences
                recent_preferences = memory_context.get("recent_preferences", {})
                if recent_preferences:
                    enhanced_system_message += f"Recent preferences: {', '.join(f'{k}: {v}' for k, v in list(recent_preferences.items())[:3])}\n"
                
                # Add favorite topics
                favorite_topics = memory_context.get("favorite_topics", [])
                if favorite_topics:
                    topics_str = ', '.join([topic[0] if isinstance(topic, tuple) else str(topic) for topic in favorite_topics[:3]])
                    enhanced_system_message += f"Favorite topics: {topics_str}\n"
                
                # Add achievements
                achievements = memory_context.get("achievements", [])
                if achievements:
                    recent_achievements = achievements[-2:]  # Last 2 achievements
                    for achievement in recent_achievements:
                        if isinstance(achievement, dict):
                            achievement_type = achievement.get("type", "unknown")
                            enhanced_system_message += f"Recent achievement: {achievement_type}\n"
                
                enhanced_system_message += "Use this memory context to personalize the conversation and reference past interactions naturally."
            
            # Add ambient listening context
            enhanced_system_message += f"\n\nNote: This is an ambient listening conversation. The child may have said a wake word like 'Hey Buddy' before this message. Be natural and conversational."
            
            # DYNAMIC TOKEN LENGTH MANAGEMENT - Critical for different content types
            # Set dynamic token limits based on content type - FORCE HIGHER LIMITS
            if content_type == "story":
                # Stories need much more tokens for complete narratives
                max_tokens = 4000  # INCREASED from 2000 to ensure complete stories
                logger.info(f"🎭 STORY REQUEST - Using {max_tokens} tokens for complete narrative")
            elif content_type in ["song", "poem", "rhyme"]:
                # Creative content needs moderate tokens
                max_tokens = 1500  # INCREASED from 800
                logger.info(f"🎵 CREATIVE CONTENT - Using {max_tokens} tokens")
            elif content_type in ["riddle", "joke"]:
                # Short content can use fewer tokens
                max_tokens = 800  # INCREASED from 400
                logger.info(f"🧩 SHORT CONTENT - Using {max_tokens} tokens")
            else:
                # Regular conversation gets standard allocation
                max_tokens = 2000  # INCREASED from 1000
                logger.info(f"💬 CONVERSATION - Using {max_tokens} tokens")
            
            # CRITICAL FIX: Enhanced system message with conversation history for context continuity
            if context and len(context) > 0:
                logger.info(f"Adding {len(context)} conversation history items to system message for context continuity")
                history_text = "\n\nRECENT CONVERSATION HISTORY (for context continuity):\n"
                
                # Add last 10 messages to system message for context
                recent_context = context[-10:] if len(context) > 10 else context
                for ctx_item in recent_context:
                    role = ctx_item.get('role', ctx_item.get('sender', 'unknown'))
                    text = ctx_item.get('text', '')
                    if role == 'user':
                        history_text += f"Child: {text}\n"
                    elif role in ['assistant', 'bot']:
                        history_text += f"You (Buddy): {text}\n"
                
                history_text += "\nIMPORTANT: Use this conversation history to maintain context continuity. Reference previous exchanges naturally and respond appropriately to the current user input in the context of this conversation.\n"
                
                # Recreate chat with enhanced system message including history
                enhanced_system_with_history = enhanced_system_message + history_text
                
                # GROK'S UNLIMITED TOKEN SOLUTION - Force complete generation for ALL content
                chat = LlmChat(
                    api_key=self.gemini_api_key,
                    session_id=session_id,
                    system_message=enhanced_system_with_history
                ).with_model("gemini", "gemini-2.0-flash")
                # CRITICAL: NO TOKEN LIMITS - Force complete responses for everything
                logger.info(f"🔄 {content_type.upper()} REQUEST - Using UNLIMITED tokens for complete response")
                
                
                logger.info("✅ Enhanced chat initialized with conversation history and dynamic token allocation")
            else:
                # No context available, use original system message with unlimited tokens
                chat = LlmChat(
                    api_key=self.gemini_api_key,
                    session_id=session_id,
                    system_message=enhanced_system_message
                ).with_model("gemini", "gemini-2.0-flash")
                # CRITICAL: NO TOKEN LIMITS for any content type
                logger.info(f"🔄 {content_type.upper()} REQUEST - Using UNLIMITED tokens (no context)")
            
            # Create user message
            user_message = UserMessage(text=user_input)
            
            # GENERATE RESPONSE WITH CONTINUATION LOOP - Ensure completeness
            response = ""
            max_attempts = 3
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    current_response = await chat.send_message(user_message)
                    response += current_response if current_response else ""
                    
                    # Check if response is complete (not truncated)
                    if response and len(response.strip()) > 50:
                        # For specific content types, check for completeness
                        if content_type == "joke":
                            # Jokes must have both setup and punchline - no interactive format
                            if ("?" in response and ("!" in response or "." in response) and 
                                "tell me more" not in response.lower() and "..." not in response):
                                break  # Complete joke delivered
                            else:
                                logger.warning(f"⚠️ Joke appears incomplete or interactive, retrying...")
                                attempt += 1
                                continue
                        elif content_type == "story" and ("The End" in response or len(response.split()) >= 100):
                            break  # Story with ending or sufficient length
                        elif content_type == "riddle" and ("?" in response and len(response.split()) >= 30):
                            break  # Riddle with question
                        elif content_type in ["song", "rhyme"] and len(response.split()) >= 50:
                            break  # Song/rhyme with sufficient content
                        elif content_type == "conversation" and len(response.split()) >= 20:
                            break  # Regular conversation response
                        else:
                            break  # For other content, accept if we got something substantial
                    else:
                        logger.warning(f"⚠️ Response too short ({len(response)} chars), retrying...")
                        attempt += 1
                        if attempt < max_attempts:
                            # Add continuation prompt - emphasize complete delivery for jokes
                            if content_type == "joke":
                                user_message = UserMessage(text=f"{user_input}\n\nPlease provide the complete joke with setup AND punchline in one response.")
                            else:
                                user_message = UserMessage(text=f"{user_input}\n\nPlease provide a complete, full response.")
                        continue
                        
                    break
                    
                except Exception as gen_error:
                    logger.error(f"❌ Generation attempt {attempt + 1} failed: {str(gen_error)}")
                    attempt += 1
                    if attempt >= max_attempts:
                        response = f"I'd love to help you with that! Let's try something fun together, {user_profile.get('name', 'friend')}!"
                        break
            
            if not response or len(response.strip()) < 20:
                logger.error("❌ All generation attempts failed or produced inadequate response")
                response = f"I'd love to help you with that! Let's have some fun together, {user_profile.get('name', 'friend')}!"
            
            # ENHANCED RESPONSE LENGTH VALIDATION AND ITERATIVE GENERATION FOR STORY CONTENT
            if content_type == "story" and response:
                original_word_count = len(response.split())
                logger.info(f"Initial story response: {original_word_count} words")
                
                # If story is too short, use iterative generation to build complete story
                if original_word_count < 250:
                    logger.info(f"Story too short ({original_word_count} words), using iterative generation")
                    
                    # Continue building the story iteratively
                    current_story = response
                    iteration_count = 0
                    max_iterations = 3
                    
                    while len(current_story.split()) < 300 and iteration_count < max_iterations:
                        iteration_count += 1
                        continuation_prompt = f"""Continue and expand this story to make it more complete and detailed. The current story is: 

{current_story}

Please continue with more details, dialogue, and story development. Add at least 100 more words to make this a richer, more complete story. Continue seamlessly from where it left off."""
                        
                        continuation_message = UserMessage(text=continuation_prompt)
                        continuation = await chat.send_message(continuation_message)
                        
                        if continuation:
                            # Combine the stories intelligently  
                            if current_story.endswith('.') or current_story.endswith('!') or current_story.endswith('?'):
                                current_story = current_story + " " + continuation
                            else:
                                current_story = current_story + continuation
                            
                            logger.info(f"Story iteration {iteration_count}: {len(current_story.split())} words")
                        else:
                            break
                    
                    response = current_story
                    final_word_count = len(response.split())
                    logger.info(f"Final story length: {final_word_count} words after {iteration_count} iterations")
            
            # Post-process response - CRITICAL: Don't truncate stories after iterative generation!
            if content_type == "story":
                # Stories must NOT be truncated after iterative generation
                processed_response = response  # Keep full story intact
                logger.info(f"🎭 STORY PRESERVED: Skipping truncation for {len(response.split())} word story")
            else:
                processed_response = self._post_process_ambient_response(response, age_group, content_type)
            
            logger.info(f"Generated context-aware response for age {age}: {processed_response[:100]}...")
            return processed_response
            
        except Exception as e:
            logger.error(f"Error generating context-aware response: {str(e)}")
            return self._get_fallback_ambient_response(user_profile.get('age', 5))
    
    def _post_process_ambient_response(self, response: str, age_group: str, content_type: str = "conversation") -> str:
        """Post-process response for ambient conversation - PRESERVES story content"""
        
        # CRITICAL: Never truncate story content regardless of age group
        if content_type == "story":
            logger.info(f"🎭 STORY CONTENT DETECTED: Preserving full {len(response.split())} word story")
            return response  # Return story completely unchanged
        
        # Only apply truncation to regular conversation content
        if age_group == "toddler":
            # Keep responses very short for toddlers in conversation only
            sentences = response.split('.')
            if len(sentences) > 2:
                response = '. '.join(sentences[:2]) + '.'
        elif age_group == "child":
            # Moderate length for children in conversation only
            sentences = response.split('.')
            if len(sentences) > 3:
                response = '. '.join(sentences[:3]) + '.'
        
        # Add natural conversation starters occasionally
        conversation_starters = {
            "toddler": ["Want to hear more?", "What do you think?", "Should we play?"],
            "child": ["What would you like to know?", "Want to try something fun?", "Any questions?"],
            "preteen": ["What's your opinion?", "Want to explore this more?", "Any questions?"]
        }
        
        # Add conversation starter 20% of the time
        import random
        if random.random() < 0.2:
            starter = random.choice(conversation_starters[age_group])
            response = f"{response} {starter}"
        
        return response
    
    def _get_fallback_ambient_response(self, age: int) -> str:
        """Get fallback response for ambient conversation"""
        age_group = self._get_age_group(age)
        
        fallback_responses = {
            "toddler": "I'm here to help! What would you like to do?",
            "child": "Hi there! I'm listening. What can I help you with?",
            "preteen": "I'm ready to chat! What's on your mind?"
        }
        
        return fallback_responses[age_group]

    async def generate_response(self, user_input: str, user_profile: Dict[str, Any], session_id: str) -> str:
        """Generate age-appropriate response using Gemini 2.0 Flash with content frameworks"""
        try:
            # Determine age group
            age = user_profile.get('age', 5)
            age_group = self._get_age_group(age)
            
            # Detect content type
            content_type = self._detect_content_type(user_input)
            
            # Get empathetic base system message (without memory_context for this method)
            base_empathetic_message = self._create_empathetic_system_message(user_profile, "")
            
            # Create enhanced system message based on content type
            if content_type in ["story", "song", "rhyme", "poem", "joke", "riddle"]:
                enhanced_system_message = self._create_content_system_message(
                    content_type, user_profile, base_empathetic_message
                )
            else:
                # Regular conversation - use empathetic base message
                enhanced_system_message = f"{base_empathetic_message}\n\nProvide rich, thoughtful responses with the depth and warmth this conversation deserves. Remember - you genuinely care about this child's happiness and growth!"
            
            # Initialize chat with session - COMPLETELY REMOVE TOKEN LIMITS  
            chat = LlmChat(
                api_key=self.gemini_api_key,
                session_id=session_id,
                system_message=enhanced_system_message
            ).with_model("gemini", "gemini-2.0-flash")
            # INTENTIONALLY NO .with_max_tokens() - Allow unlimited length
            
            # Create user message
            user_message = UserMessage(text=user_input)
            
            # GROK'S ITERATIVE GENERATION SOLUTION - Proven approach
            response = await chat.send_message(user_message)
            original_response = response
            
            # Check if response was truncated and continue iteratively
            complete_response = response
            iteration_count = 0
            max_iterations = 5  # Prevent infinite loops
            
            # For stories, ensure minimum word count through iteration
            if content_type == "story":
                word_count = len(complete_response.split())
                logger.info(f"🎭 Initial story response: {word_count} words")
                
                while word_count < 300 and iteration_count < max_iterations:
                    iteration_count += 1
                    logger.info(f"🔄 Story iteration {iteration_count}: Continuing from {word_count} words")
                    
                    # Continue the story from where it left off
                    continuation_prompt = f"Continue this story seamlessly to complete it (add at least 100 more words): {complete_response[-200:]}"  # Last 200 chars for context
                    continuation_message = UserMessage(text=continuation_prompt)
                    
                    continuation_response = await chat.send_message(continuation_message)
                    
                    if continuation_response:
                        # Smart continuation - avoid repetition
                        if not complete_response.endswith(('.', '!', '?')):
                            complete_response += " " + continuation_response
                        else:
                            complete_response += " " + continuation_response
                        
                        word_count = len(complete_response.split())
                        logger.info(f"📈 Story expanded to {word_count} words after iteration {iteration_count}")
                    else:
                        logger.warning(f"⚠️ No continuation received in iteration {iteration_count}")
                        break
                
                response = complete_response
                final_word_count = len(response.split())
                logger.info(f"📚 FINAL STORY LENGTH: {final_word_count} words after {iteration_count} iterations")
                
            else:
                # For non-story content, check for completeness differently
                if len(response.split()) < 50:  # Minimum for complete responses
                    logger.info("🔄 Response seems incomplete, attempting continuation")
                    continuation_prompt = f"Complete this response fully: {response}"
                    continuation_message = UserMessage(text=continuation_prompt)
                    continuation_response = await chat.send_message(continuation_message)
                    
                    if continuation_response:
                        response = response + " " + continuation_response
                        logger.info(f"✅ Response completed: {len(response.split())} words")
            
            # RESPONSE LENGTH VALIDATION AND ITERATIVE GENERATION FOR STORY CONTENT
            if content_type == "story" and response:
                original_word_count = len(response.split())
                logger.info(f"Initial story response: {original_word_count} words")
                
                # If story is too short, use iterative generation to build complete story
                if original_word_count < 250:
                    logger.info(f"Story too short ({original_word_count} words), using iterative generation")
                    
                    # Continue building the story iteratively
                    current_story = response
                    iteration_count = 0
                    max_iterations = 3
                    
                    while len(current_story.split()) < 300 and iteration_count < max_iterations:
                        iteration_count += 1
                        continuation_prompt = f"""Continue and expand this story to make it more complete and detailed. The current story is: 

{current_story}

Please continue with more details, dialogue, and story development. Add at least 100 more words to make this a richer, more complete story. Continue seamlessly from where it left off."""
                        
                        continuation_message = UserMessage(text=continuation_prompt)
                        continuation = await chat.send_message(continuation_message)
                        
                        if continuation:
                            # Combine the stories intelligently  
                            if current_story.endswith('.') or current_story.endswith('!') or current_story.endswith('?'):
                                current_story = current_story + " " + continuation
                            else:
                                current_story = current_story + continuation
                            
                            logger.info(f"Story iteration {iteration_count}: {len(current_story.split())} words")
                        else:
                            break
                    
                    response = current_story
                    final_word_count = len(response.split())
                    logger.info(f"Final story length: {final_word_count} words after {iteration_count} iterations")
            
            # Light post-processing (no artificial truncation)
            processed_response = self._post_process_response_enhanced(response, age_group, content_type)
            
            logger.info(f"Generated {content_type} response for age {age}: {len(processed_response.split())} words")
            return processed_response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._get_fallback_response(user_profile.get('age', 5))

    def _detect_content_type(self, user_input: str) -> str:
        """Detect what type of content the user is requesting"""
        user_input_lower = user_input.lower()
        
        # Story detection
        story_keywords = ['story', 'tale', 'tell me about', 'once upon', 'adventure', 'fairy tale']
        if any(keyword in user_input_lower for keyword in story_keywords):
            return "story"
        
        # Song detection
        song_keywords = ['song', 'sing', 'music', 'lullaby', 'rhyme about']
        if any(keyword in user_input_lower for keyword in song_keywords):
            return "song"
        
        # Riddle detection
        riddle_keywords = ['riddle', 'puzzle', 'guess', 'brain teaser']
        if any(keyword in user_input_lower for keyword in riddle_keywords):
            return "riddle"
        
        # Joke detection
        joke_keywords = ['joke', 'funny', 'make me laugh', 'something silly']
        if any(keyword in user_input_lower for keyword in joke_keywords):
            return "joke"
        
        # Rhyme/Poem detection
        rhyme_keywords = ['rhyme', 'poem', 'poetry', 'verse']
        if any(keyword in user_input_lower for keyword in rhyme_keywords):
            return "rhyme"
        
        return "conversation"

    def _post_process_response_enhanced(self, response: str, age_group: str, content_type: str) -> str:
        """Enhanced post-processing without artificial truncation"""
        if age_group == "toddler":
            # Simple vocabulary replacements only
            response = response.replace("understand", "know")
            response = response.replace("excellent", "great")
            response = response.replace("magnificent", "amazing")
        
        # Add encouraging elements occasionally (but don't truncate)
        encouraging_phrases = {
            "toddler": ["Good job!", "You're so smart!", "That's wonderful!"],
            "child": ["Great question!", "You're doing awesome!", "I love how curious you are!"],
            "preteen": ["Excellent thinking!", "You're really getting it!", "That's a thoughtful question!"]
        }
        
        import random
        if random.random() < 0.2 and content_type == "conversation":  # 20% chance for regular conversation only
            phrase = random.choice(encouraging_phrases[age_group])
            response = f"{phrase} {response}"
        
        return response
    
    def _get_age_group(self, age: int) -> str:
        """Determine age group category"""
        if age <= 5:
            return "toddler"
        elif age <= 9:
            return "child"
        else:
            return "preteen"
    
    def _post_process_response(self, response: str, age_group: str) -> str:
        """Post-process response based on age group"""
        if age_group == "toddler":
            # Ensure very simple language
            response = response.replace("understand", "know")
            response = response.replace("excellent", "great")
            response = response.replace("magnificent", "amazing")
            
        # Add encouraging elements
        encouraging_phrases = {
            "toddler": ["Good job!", "You're so smart!", "That's wonderful!"],
            "child": ["Great question!", "You're doing awesome!", "I love how curious you are!"],
            "preteen": ["Excellent thinking!", "You're really getting it!", "That's a thoughtful question!"]
        }
        
        # Randomly add encouraging phrases occasionally
        import random
        if random.random() < 0.3:  # 30% chance
            phrase = random.choice(encouraging_phrases[age_group])
            response = f"{phrase} {response}"
        
        return response
    
    def _get_fallback_response(self, age: int) -> str:
        """Get fallback response when AI fails"""
        age_group = self._get_age_group(age)
        
        fallback_responses = {
            "toddler": "That's a fun question! Let me think about it. What else would you like to know?",
            "child": "That's really interesting! I'm still learning about that. What else are you curious about?",
            "preteen": "That's a great question! I need to think more about that. Is there something else I can help you with?"
        }
        
        return fallback_responses[age_group]
    


    def _format_content_response_with_emotion(self, content_type: str, content: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Format content responses with proper emotional expression and re-engagement"""
        name = user_profile.get('name', 'friend')
        
        if content_type == "joke":
            return f"{content['setup']}\n\n{content['punchline']}\n\n{content.get('reaction', '😂 Haha!')} Want another joke, {name}?"
        
        elif content_type == "riddle":
            return f"Here's a riddle for you, {name}! 🧩\n\n{content['question']}\n\nTake your time to think! When you're ready, tell me your answer and I'll let you know if you got it!"
        
        elif content_type == "fact":
            return f"{content.get('text', content.get('fact', ''))} {content.get('reaction', '🤯 Amazing, right?')} Want to learn another cool fact, {name}?"
        
        elif content_type == "rhyme":
            beautiful_msg = "🎵 Wasn't that beautiful?"
            return f"Here's a lovely rhyme for you, {name}! ✨\n\n{content.get('text', content.get('content', ''))}\n\n{content.get('reaction', beautiful_msg)} Want to hear another rhyme?"
        
        elif content_type == "song":
            return f"Let's sing together, {name}! 🎵\n\n{content.get('text', content.get('content', ''))}\n\n{content.get('reaction', '🎶 That was fun!')} Should we sing another song?"
        
        elif content_type == "story":
            full_story = content.get('text', content.get('content', ''))
            moral = content.get('moral', '')
            story_end = f"\n\nThe End! ✨"
            if moral:
                story_end += f"\n\n💫 {moral}"
            story_end += f"\n\nWhat did you think of that story, {name}? Want to hear another one?"
            return full_story + story_end
        
        elif content_type == "game":
            return f"{content.get('intro', content.get('text', ''))} {content.get('reaction', '🎮 This will be fun!')} Are you ready to play, {name}?"
        
        return content.get('text', str(content))
    
    def _get_last_bot_message(self, context: List[Dict[str, Any]]) -> Optional[str]:
        """Get the last bot message from context"""
        if not context:
            return None
        
        for ctx in reversed(context):
            if ctx.get('role') == 'assistant' or ctx.get('sender') == 'bot':
                return ctx.get('text', '')
        return None
    
    def _get_last_user_message(self, context: List[Dict[str, Any]]) -> Optional[str]:
        """Get the last user message from context"""
        if not context:
            return None
        
        for ctx in reversed(context):
            if ctx.get('role') == 'user' or ctx.get('sender') == 'user':
                return ctx.get('text', '')
        return None
    
    def _requires_followthrough(self, last_bot_message: Optional[str], user_input: str) -> bool:
        """Check if the last bot message requires follow-through"""
        if not last_bot_message:
            return False
        
        # Check for questions, riddles, games that need responses
        followthrough_patterns = [
            r'\?',  # Any question
            r'\bguess\b',  # Guessing games
            r'\briddle\b',  # Riddles
            r'\bwhat am i\b',  # What am I riddles
            r'\bthink about\b',  # Thinking prompts
            r'\btell me\b',  # Direct requests
            r'\bwhat do you think\b',  # Opinion requests
            r'\bready\b.*\?',  # Ready questions
            r'\bwant to\b.*\?',  # Want to questions - THIS SHOULD MATCH THE OCTOPUS CASE
            r'\bwould you like\b.*\?',  # Would you like questions
            r'\bdo you want\b.*\?',  # Do you want questions  
            r'\bshould we\b.*\?',  # Should we questions
            r'\blet me know\b',  # Let me know requests
            r'\blearn more\b.*\?',  # Learn more questions
            r'\bchoose\b',  # Choice prompts
            r'\bpick\b',  # Pick prompts
        ]
        
        last_bot_lower = last_bot_message.lower()
        
        # Additional check for common response patterns
        user_lower = user_input.lower().strip()
        response_patterns = ['yes', 'no', 'yeah', 'sure', 'okay', 'ok', 'please', 'yes please', 'no thanks']
        
        # If user gave a simple response, check if bot asked a question
        if any(user_lower.startswith(pattern) for pattern in response_patterns):
            # More likely to be a follow-through if it's a simple response to a question
            if '?' in last_bot_message:
                return True
        
        for pattern in followthrough_patterns:
            if re.search(pattern, last_bot_lower):
                return True
        
        return False
    
    async def get_conversation_history(self, session_id: str) -> list:
        """Get conversation history for a session"""
        return self.conversations.get(session_id, [])
    
    async def clear_conversation_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]