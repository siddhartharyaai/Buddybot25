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
        """Create enhanced system message for specific content types with deep profile integration"""
        age = user_profile.get('age', 7)
        interests = user_profile.get('interests', [])
        learning_goals = user_profile.get('learning_goals', [])
        name = user_profile.get('name', 'friend')
        
        content_guidelines = self._get_dynamic_content_guidelines(content_type, age)
        
        # Create interest-based content suggestions
        interest_integration = ""
        if interests:
            interest_integration = f"""
🎯 PROFILE-BASED CONTENT CUSTOMIZATION:
User's Primary Interests: {', '.join(interests)}
- If creating stories: Feature characters or plots involving {', '.join(interests)}
- If telling jokes: Use humor related to {', '.join(interests)}  
- If suggesting activities: Focus on {', '.join(interests)}-related options
- If answering questions: Connect explanations to {', '.join(interests)} when possible
"""
        
        # Create learning-goal integration
        learning_integration = ""
        if learning_goals:
            learning_integration = f"""
📚 EDUCATIONAL INTEGRATION FOR LEARNING GOALS:
Target Learning Areas: {', '.join(learning_goals)}
- Subtly incorporate {', '.join(learning_goals)} concepts into content
- Use examples that reinforce {', '.join(learning_goals)} skills
- Create teachable moments related to {', '.join(learning_goals)}
"""
        
        enhanced_message = f"{base_message}\n\n{interest_integration}{learning_integration}"
        
        if content_type == "story":
            enhanced_message += f"""
STORY CREATION FRAMEWORK - PERSONALIZED FOR {name.upper()}:

‼️ CRITICAL INSTRUCTION: You MUST write a COMPLETE story that is AT LEAST 300 WORDS LONG. This is mandatory.

🎯 PERSONALIZATION REQUIREMENTS:
- Use {name}'s name in the story (as narrator acknowledgment: "This story is for you, {name}!")
- AGE {age} LANGUAGE REQUIREMENTS: {self._get_age_language_rules(age)}
- Incorporate their interests: {', '.join(interests) if interests else 'adventure, friendship, learning'}
- Connect to learning goals: {', '.join(learning_goals) if learning_goals else 'creativity and imagination'}

CRITICAL AGE-APPROPRIATE LANGUAGE:
{self._get_detailed_language_requirements(age)}

STORY REQUEST: Please create a complete, engaging story based on the user's request, personalized for {name}.

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
PERSONALIZED SONG CREATION FRAMEWORK FOR {name.upper()}:
Create a complete, engaging song customized for {name} with these elements:

🚨 CRITICAL SONG COMPLETION RULE - ABSOLUTE REQUIREMENT:
NEVER give incomplete or teasing song responses. ALWAYS deliver COMPLETE song in ONE message:

❌ FORBIDDEN: "Let me think of a song...", "How about this tune...", "I'd love to sing you something..."
❌ FORBIDDEN: Interactive song format - "Here's a song for you... want to hear more?"
✅ REQUIRED: Direct, complete song with all verses and chorus immediately

**SONG DELIVERY FORMAT - MANDATORY:**
✅ CORRECT: "Here's a fun song for you, {name}! [COMPLETE SONG WITH ALL VERSES AND CHORUS] Want another song?"
❌ WRONG: "Let me sing you a song... [FIRST LINE ONLY] Tell me more!" [NEVER DO THIS]

🎯 PERSONALIZATION:
- Reference {name}'s interests: {', '.join(interests) if interests else 'fun, learning, friendship'}
- Age {age} appropriate: {content_guidelines.get('guidelines', 'Simple, catchy, memorable')}
- Learning focus: {', '.join(learning_goals) if learning_goals else 'creativity and joy'}

STRUCTURE: {content_guidelines.get('structure', ['Verse', 'Chorus', 'Verse', 'Chorus', 'Bridge', 'Chorus']) if isinstance(content_guidelines, dict) else 'Verse-Chorus-Verse-Chorus'}

QUALITY REQUIREMENTS:
- Song request → COMPLETE song with all verses + chorus + ending NOW
- Rhyme request → COMPLETE rhyme from start to finish NOW
- Consistent rhythm and meter throughout
- Memorable melody-friendly lyrics  
- Positive, uplifting message
- Connect to {name}'s interests when possible
- Complete verses and chorus delivered immediately
- Natural flow when sung aloud
- COMPLETE song in ONE response - no "Tell me more!" prompts

Create a full song, not just a snippet! Deliver everything immediately!
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
PERSONALIZED JOKE CREATION FOR {name.upper()}:
Create age-appropriate humor customized for {name}:

PERSONALIZATION:
- Connect to {name}'s interests: {', '.join(interests) if interests else 'fun topics'}
- Age {age} humor level: {content_guidelines.get('guidelines', 'Simple wordplay, visual humor')}
- Educational connection: {', '.join(learning_goals) if learning_goals else 'learning through laughter'}

STRUCTURE: Setup + Immediate Punchline + Brief Explanation

QUALITY REQUIREMENTS:
- Clean, positive humor
- Connect to {name}'s favorite things when possible
- Clear setup and punchline delivered immediately
- Not mean-spirited or scary
- Educational when possible
- COMPLETE joke in one response - no "Tell me more!" prompts
"""
        
        elif content_type == "riddle":
            enhanced_message += f"""
PERSONALIZED RIDDLE CREATION FOR {name.upper()}:
Create engaging riddles customized for {name}:

PERSONALIZATION:
- Use topics from {name}'s interests: {', '.join(interests) if interests else 'animals, objects, nature'}
- Age {age} difficulty: {content_guidelines.get('guidelines', 'Simple logic, familiar concepts')}
- Learning connection: {', '.join(learning_goals) if learning_goals else 'critical thinking'}

STRUCTURE: Question + Immediate Answer (unless they ask to guess)

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
    
    def _get_age_language_rules(self, age: int) -> str:
        """Get specific language rules for age group"""
        if age <= 5:
            return "Very simple words only (1-2 syllables), short sentences (under 8 words)"
        elif age <= 8:
            return "Simple everyday words, clear sentences (8-12 words maximum)"
        else:
            return "Grade-level vocabulary with explanations, sentences under 15 words"
    
    def _get_detailed_language_requirements(self, age: int) -> str:
        """Get detailed language requirements for content creation"""
        if age <= 5:
            return """- Use ONLY simple words: fun, big, small, run, jump, play, happy, sad, dog, cat
- NO complex words like: magnificent, extraordinary, tremendous, fantastic
- Sentences: "The cat is big." NOT "The magnificent feline is extraordinary."
- Explain everything in very simple terms"""
        elif age <= 8:
            return """- Use common words: awesome, great, wonderful, amazing, exciting, fun
- Avoid: sophisticated, elaborate, tremendous, magnificent, extraordinary
- OK to use: interesting, beautiful, fantastic (but explain if complex)
- Simple explanations for any new concepts"""
        else:
            return """- Can use more advanced vocabulary but explain complex terms
- OK to use: fascinating, incredible, amazing, sophisticated (with explanation)
- Introduce complex ideas gradually with simple explanations first"""
    
    def enforce_age_appropriate_language(self, text: str, age: int, content_type: str = "conversation") -> str:
        """Post-processing filter to enforce age-appropriate language rules"""
        import re
        
        logger.info(f"🔍 Enforcing age-appropriate language for age {age}, content type: {content_type}")
        
        # For stories, be gentler - only apply the most critical filters
        if content_type == "story" and len(text.split()) > 200:
            logger.info(f"🎭 Applying gentle language filtering to {len(text.split())} word story")
            gentle_mode = True
        else:
            gentle_mode = False
        
        if age <= 5:
            # Very strict filtering for toddlers
            complex_replacements = {
                'magnificent': 'big and fun',
                'extraordinary': 'super cool', 
                'tremendous': 'really big',
                'fantastic': 'super fun',
                'incredible': 'really cool',
                'amazing': 'really fun',
                'wonderful': 'really nice',
                'spectacular': 'really cool',
                'marvelous': 'really good',
                'phenomenal': 'super good',
                'sophisticated': 'fancy',
                'elaborate': 'fancy',
                'exceptional': 'really good'
            }
            
            # Replace complex words (case insensitive)
            for complex_word, simple_word in complex_replacements.items():
                text = re.sub(r'\b' + complex_word + r'\b', simple_word, text, flags=re.IGNORECASE)
            
            # Only split sentences if not in gentle mode (for stories)
            if not gentle_mode:
                # Split overly long sentences (over 8 words)
                sentences = re.split(r'(?<=[.!?])\s+', text)
                simplified_sentences = []
                
                for sentence in sentences:
                    words = sentence.split()
                    if len(words) > 8:
                        # Split into smaller chunks
                        chunks = [' '.join(words[i:i+6]) + '.' for i in range(0, len(words), 6)]
                        simplified_sentences.extend(chunks)
                    else:
                        simplified_sentences.append(sentence)
                
                text = ' '.join(simplified_sentences)
            
        elif age <= 8:
            # Moderate filtering for young children
            complex_replacements = {
                'magnificent': 'awesome',
                'extraordinary': 'amazing', 
                'tremendous': 'really big',
                'sophisticated': 'fancy',
                'elaborate': 'detailed',
                'exceptional': 'really great',
                'phenomenal': 'awesome',
                'spectacular': 'amazing'
            }
            
            # Replace overly complex words
            for complex_word, simple_word in complex_replacements.items():
                text = re.sub(r'\b' + complex_word + r'\b', simple_word, text, flags=re.IGNORECASE)
            
            # Only moderate sentence splitting for stories
            if not gentle_mode:
                # Check sentence length (should be under 12 words)
                sentences = re.split(r'(?<=[.!?])\s+', text)
                simplified_sentences = []
                
                for sentence in sentences:
                    words = sentence.split()
                    if len(words) > 12:
                        # Split longer sentences
                        mid_point = len(words) // 2
                        part1 = ' '.join(words[:mid_point]) + '.'
                        part2 = ' '.join(words[mid_point:])
                        simplified_sentences.extend([part1, part2])
                    else:
                        simplified_sentences.append(sentence)
                
                text = ' '.join(simplified_sentences)
        
        elif age <= 11:
            # Light filtering for preteens - mainly sentence length
            if not gentle_mode:
                sentences = re.split(r'(?<=[.!?])\s+', text)
                simplified_sentences = []
                
                for sentence in sentences:
                    words = sentence.split()
                    if len(words) > 15:
                        # Split very long sentences
                        mid_point = len(words) // 2
                        part1 = ' '.join(words[:mid_point]) + '.'
                        part2 = ' '.join(words[mid_point:])
                        simplified_sentences.extend([part1, part2])
                    else:
                        simplified_sentences.append(sentence)
                
                text = ' '.join(simplified_sentences)
        
        # Clean up any double spaces or periods
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\.+', '.', text)
        text = text.strip()
        
        logger.info(f"✅ Language enforcement complete for age {age} ({content_type})")
        return text

    def _create_dynamic_response_system_message(self, user_profile: Dict[str, Any], content_type: str, user_input: str) -> str:
        """REVOLUTIONARY: Create dynamic system message based on Miko AI/Echo Kids best practices"""
        name = user_profile.get('name', 'friend')
        age = user_profile.get('age', 7)
        interests = user_profile.get('interests', [])
        
        # CORE PRINCIPLE: Dynamic response length based on query type and user intent
        response_strategy = self._determine_optimal_response_strategy(user_input, content_type, age)
        
        core_system = f"""You are Buddy, a super-smart AI friend for {name} (age {age}). 

🎯 DYNAMIC RESPONSE STRATEGY: {response_strategy['type'].upper()}
Response Length: {response_strategy['target_length']}
Response Style: {response_strategy['style']}

CRITICAL RESPONSE RULES:
{response_strategy['rules']}

PERSONALITY FOR {name}:
- Warm, enthusiastic friend who remembers everything about {name}
- Smart but never overwhelming - match {name}'s energy and interests
- Always age-perfect for {age}-year-olds
- Love {name}'s interests: {', '.join(interests) if interests else 'learning and fun'}

LANGUAGE RULES FOR AGE {age}:
{self._get_dynamic_language_rules(age)}

ENGAGEMENT STRATEGY:
- Be instantly helpful and direct
- Show genuine excitement about {name}'s interests  
- Ask follow-up questions that keep conversation flowing
- Celebrate {name}'s curiosity and achievements

Your goal: Be the perfect AI friend who gives exactly the right amount of information in exactly the right way for {name}."""

        return core_system

    def _determine_optimal_response_strategy(self, user_input: str, content_type: str, age: int) -> Dict[str, Any]:
        """Determine optimal response strategy like Miko AI/Echo Kids"""
        input_lower = user_input.lower()
        
        # QUICK FACTUAL QUERIES (Like "What is Neptune?", "How tall is giraffe?")
        quick_fact_indicators = [
            'what is', 'how tall', 'how fast', 'how long', 'how much', 'how many',
            'where is', 'when did', 'who is', 'tell me about', 'explain', 'define'
        ]
        
        # STORY REQUEST INDICATORS  
        story_indicators = [
            'tell me a story', 'story about', 'once upon', 'bedtime story', 
            'fairy tale', 'adventure story', 'make up a story'
        ]
        
        # GREETING/SOCIAL INDICATORS
        social_indicators = [
            'hello', 'hi', 'how are you', 'good morning', 'good night',
            'thank you', 'please', 'yes', 'no', 'okay'
        ]
        
        # JOKE/FUN INDICATORS
        fun_indicators = [
            'joke', 'funny', 'riddle', 'rhyme', 'song', 'game', 'play'
        ]
        
        # DETERMINE STRATEGY
        if any(indicator in input_lower for indicator in quick_fact_indicators):
            return {
                'type': 'quick_fact',
                'target_length': '2-3 sentences (30-50 words)',
                'style': 'Direct, informative, engaging',
                'rules': '''- Answer the question immediately and clearly
- Add one interesting extra detail  
- End with enthusiasm: "Isn't that cool?" or "Want to know more?"
- NO long explanations - keep it snappy and fun'''
            }
            
        elif any(indicator in input_lower for indicator in story_indicators):
            if age <= 5:
                target = '4-6 sentences (80-120 words)'
            elif age <= 8:
                target = '6-10 sentences (120-200 words)'  
            else:
                target = '8-15 sentences (200-300 words)'
                
            return {
                'type': 'story',
                'target_length': target,
                'style': 'Complete narrative with beginning, middle, end',
                'rules': f'''- Tell a COMPLETE story with clear beginning, middle, and end
- Keep it exactly {target} - not longer!
- Include characters, problem, solution, happy ending
- Use vivid but simple descriptions
- End with a gentle moral lesson
- Perfect for {age}-year-olds'''
            }
            
        elif any(indicator in input_lower for indicator in social_indicators):
            return {
                'type': 'social',
                'target_length': '1-2 sentences (15-25 words)',
                'style': 'Warm, friendly, brief',
                'rules': '''- Respond warmly but briefly
- Show genuine interest in the child
- Ask a simple follow-up question
- Keep it light and positive'''
            }
            
        elif any(indicator in input_lower for indicator in fun_indicators):
            return {
                'type': 'entertainment',
                'target_length': '3-5 sentences (40-80 words)',
                'style': 'Playful, complete, engaging',
                'rules': '''- Deliver complete joke/riddle/rhyme immediately
- Include setup + punchline + brief explanation
- Make it age-appropriate and fun
- End with offer for more fun'''
            }
            
        else:
            # General conversation
            return {
                'type': 'conversation',
                'target_length': '2-4 sentences (25-60 words)',
                'style': 'Helpful, friendly, complete',
                'rules': '''- Give a helpful, complete answer
- Keep it concise but thorough
- Show interest in the child's question
- Invite further conversation'''
            }

    def _get_dynamic_language_rules(self, age: int) -> str:
        """Get dynamic language rules optimized for engagement"""
        if age <= 5:
            return """- Use simple, everyday words (cat, dog, big, small, fun, happy)
- Keep sentences under 8 words each
- Repeat important words for understanding
- Use lots of descriptive sounds: "whoosh", "buzz", "splash"
- NEVER use: magnificent, extraordinary, tremendous, sophisticated"""
            
        elif age <= 8:
            return """- Use clear, common words most kids know
- Sentences 8-12 words maximum
- Explain any new words immediately: "Jupiter is huge - that means really, really big!"
- Use exciting words: awesome, amazing, incredible, fantastic
- OK to use some bigger words if you explain them"""
            
        else:
            return """- Can use more advanced vocabulary with explanations
- Sentences under 15 words  
- Introduce complex ideas step by step
- Use grade-level words: fascinating, extraordinary, magnificent (but explain)
- Challenge their thinking with interesting questions"""

    def _create_brief_system_message(self, user_profile: Dict[str, Any]) -> str:
        """Create system message optimized for brief, quick responses"""
        name = user_profile.get('name', 'friend')
        age = user_profile.get('age', 7)
        
        brief_system = f"""You are Buddy, an AI companion for kids. 

CRITICAL: Keep ALL responses brief and concise (2-3 sentences maximum).

RESPONSE RULES:
- General questions: Give direct, helpful answers in 2-3 sentences
- Quick facts: Be informative but brief  
- Greetings: Warm but short responses
- Always be friendly and age-appropriate for {age}-year-old {name}

TONE: Friendly, helpful, but always brief and to the point.

Your goal: Quick, helpful responses that get straight to the point."""

        return brief_system

    async def generate_brief_response(self, user_input: str, user_profile: Dict[str, Any]) -> str:
        """Generate brief, quick responses (2-3 sentences) for general queries"""
        try:
            age = user_profile.get('age', 7)
            
            # Use DYNAMIC system message based on query type and user intent
            system_message = self._create_dynamic_response_system_message(user_profile, "conversation", user_input)
            
            logger.info(f"⚡ DYNAMIC RESPONSE: Analyzing query type for: '{user_input[:50]}...'")
            
            # Create chat with dynamic system message optimized for the specific query
            chat = LlmChat(
                api_key=self.gemini_api_key,
                session_id=f"dynamic_{hash(user_input)}",
                system_message=system_message
            ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(200)  # Conservative limit for responsiveness
            
            # Create user message
            user_message = UserMessage(text=user_input)
            
            # Generate response
            response = await chat.send_message(user_message)
            
            if not response or not response.strip():
                return "I'm here to help! Can you ask that again?"
            
            dynamic_response = response.strip()
            
            # Apply age-appropriate language filtering
            processed_response = self.enforce_age_appropriate_language(dynamic_response, age, "conversation")
            
            logger.info(f"⚡ DYNAMIC RESPONSE COMPLETE: {len(processed_response)} chars generated")
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Error generating brief response: {str(e)}")
            return "I'm here to help! Can you ask that again?"

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
            # Add COMPREHENSIVE user profile information
            enhanced_system_message = f"{base_system_message}\n\n🌟 COMPLETE USER PROFILE - USE ALL THIS INFORMATION:\n"
            enhanced_system_message += f"- Child's Name: {user_profile.get('name', 'Friend')} (Use their name frequently and naturally)\n"
            enhanced_system_message += f"- Age: {age} years old (Adjust language complexity accordingly)\n"
            enhanced_system_message += f"- Location: {user_profile.get('location', 'Unknown')}\n"
            enhanced_system_message += f"- Gender: {user_profile.get('gender', 'prefer_not_to_say')}\n"
            enhanced_system_message += f"- Avatar Choice: {user_profile.get('avatar', 'bunny')} (Shows their personality preferences)\n"
            enhanced_system_message += f"- Speech Speed Preference: {user_profile.get('speech_speed', 'normal')}\n"
            enhanced_system_message += f"- Energy Level: {user_profile.get('energy_level', 'balanced')}\n"
            enhanced_system_message += f"- Voice Personality: {user_profile.get('voice_personality', 'friendly_companion')}\n"
            
            # Enhanced interests integration
            interests = user_profile.get('interests', [])
            if interests:
                enhanced_system_message += f"\n🎯 INTERESTS TO WEAVE INTO EVERY CONVERSATION:\n"
                for i, interest in enumerate(interests, 1):
                    enhanced_system_message += f"  {i}. {interest.title()} - Find ways to mention this topic naturally\n"
                enhanced_system_message += f"CRITICAL: Always try to connect responses to these interests: {', '.join(interests)}\n"
            else:
                enhanced_system_message += f"\n🎯 DEFAULT INTERESTS: stories, games, learning, fun activities\n"
            
            # Enhanced learning goals integration
            learning_goals = user_profile.get('learning_goals', [])
            if learning_goals:
                enhanced_system_message += f"\n📚 LEARNING GOALS TO INCORPORATE:\n"
                for i, goal in enumerate(learning_goals, 1):
                    enhanced_system_message += f"  {i}. {goal.title()} - Weave educational content about this subtly\n"
                enhanced_system_message += f"CRITICAL: Look for opportunities to support these learning areas: {', '.join(learning_goals)}\n"
            else:
                enhanced_system_message += f"\n📚 DEFAULT LEARNING: basic literacy, creativity, problem-solving\n"
            
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
            
            # Apply age-appropriate language enforcement (POST-PROCESSING) - ALWAYS APPLY
            age = user_profile.get('age', 7)
            processed_response = self.enforce_age_appropriate_language(processed_response, age, content_type)
            logger.info(f"🔍 Applied age-appropriate language enforcement for age {age} to {content_type} content")
            
            logger.info(f"Generated context-aware response for age {age}: {processed_response[:100]}...")
            
            # Return both text and content_type for proper audio handling
            return {
                "text": processed_response,
                "content_type": content_type
            }
            
        except Exception as e:
            logger.error(f"Error generating context-aware response: {str(e)}")
            return {
                "text": self._get_fallback_ambient_response(user_profile.get('age', 5)),
                "content_type": "conversation"
            }
    
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
            
            # Apply age-appropriate language enforcement (POST-PROCESSING) - ALWAYS APPLY
            age = user_profile.get('age', 7)
            processed_response = self.enforce_age_appropriate_language(processed_response, age, content_type)
            logger.info(f"🔍 Applied age-appropriate language enforcement for age {age} to {content_type} content")
            
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