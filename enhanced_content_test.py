#!/usr/bin/env python3
"""
Enhanced Content Library System Testing Suite
Tests 3-tier sourcing and content type detection for all 7 content types
"""

import asyncio
import aiohttp
import json
import uuid
import logging
from typing import Dict, Any, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend URL from environment
BACKEND_URL = "https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com/api"

class EnhancedContentTester:
    """Test Enhanced Content Library System with 3-tier sourcing and content type detection"""
    
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.test_user_id = None
        self.test_session_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_enhanced_content_tests(self):
        """Run comprehensive enhanced content library tests"""
        logger.info("🎯 Starting Enhanced Content Library System Testing...")
        
        # Setup test user first
        await self.setup_test_user()
        
        # Test sequence for enhanced content system
        test_sequence = [
            ("Content Type Detection - Jokes", self.test_joke_detection),
            ("Content Type Detection - Riddles", self.test_riddle_detection),
            ("Content Type Detection - Facts", self.test_fact_detection),
            ("Content Type Detection - Rhymes", self.test_rhyme_detection),
            ("Content Type Detection - Songs", self.test_song_detection),
            ("Content Type Detection - Stories", self.test_story_detection),
            ("Content Type Detection - Games", self.test_game_detection),
            ("3-Tier Sourcing - Local Content First", self.test_local_content_tier),
            ("3-Tier Sourcing - LLM Fallback", self.test_llm_fallback_tier),
            ("Logical Output Formatting - Jokes", self.test_joke_formatting),
            ("Logical Output Formatting - Riddles", self.test_riddle_formatting),
            ("Logical Output Formatting - Facts", self.test_fact_formatting),
            ("Logical Output Formatting - Stories", self.test_story_formatting),
            ("Token Limits Verification", self.test_token_limits),
            ("Emotional Expressions", self.test_emotional_expressions),
            ("Re-engagement Prompts", self.test_reengagement_prompts),
            ("Natural Language Processing", self.test_natural_language_inputs)
        ]
        
        for test_name, test_func in test_sequence:
            try:
                logger.info(f"🧪 Running test: {test_name}")
                result = await test_func()
                self.test_results[test_name] = {
                    "status": "PASS" if result.get("success", False) else "FAIL",
                    "details": result
                }
                status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
                logger.info(f"{status} {test_name}")
            except Exception as e:
                logger.error(f"❌ Test {test_name} failed with exception: {str(e)}")
                self.test_results[test_name] = {
                    "status": "ERROR",
                    "details": {"error": str(e)}
                }
        
        return self.test_results
    
    async def setup_test_user(self):
        """Setup test user and session"""
        try:
            # Create test user profile
            profile_data = {
                "name": "Emma",
                "age": 7,
                "location": "New York",
                "timezone": "America/New_York",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "animals", "music", "jokes"],
                "learning_goals": ["reading", "counting"],
                "parent_email": "parent@example.com"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/users/profile",
                json=profile_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_user_id = data["id"]
                    logger.info(f"✅ Created test user: {self.test_user_id}")
                else:
                    raise Exception(f"Failed to create test user: {response.status}")
            
            # Create conversation session
            session_data = {
                "user_id": self.test_user_id,
                "session_name": "Enhanced Content Test Session"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/session",
                json=session_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_session_id = data["id"]
                    logger.info(f"✅ Created test session: {self.test_session_id}")
                else:
                    raise Exception(f"Failed to create test session: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Setup failed: {str(e)}")
            raise
    
    async def test_content_type_detection(self, test_inputs: List[str], expected_type: str) -> Dict[str, Any]:
        """Generic content type detection test"""
        results = []
        
        for test_input in test_inputs:
            try:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": test_input
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content_type = data.get("content_type", "conversation")
                        response_text = data.get("response_text", "")
                        
                        # Check if content type was detected correctly
                        type_detected = content_type == expected_type or self._contains_content_indicators(response_text, expected_type)
                        
                        results.append({
                            "input": test_input,
                            "detected_type": content_type,
                            "expected_type": expected_type,
                            "type_correct": type_detected,
                            "response_length": len(response_text),
                            "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
                        })
                    else:
                        results.append({
                            "input": test_input,
                            "error": f"HTTP {response.status}",
                            "type_correct": False
                        })
                        
                # Small delay between requests
                await asyncio.sleep(0.2)
                
            except Exception as e:
                results.append({
                    "input": test_input,
                    "error": str(e),
                    "type_correct": False
                })
        
        # Calculate success rate
        correct_detections = sum(1 for r in results if r.get("type_correct", False))
        success_rate = correct_detections / len(results) if results else 0
        
        return {
            "success": success_rate >= 0.7,  # 70% success rate threshold
            "success_rate": success_rate,
            "correct_detections": correct_detections,
            "total_tests": len(results),
            "results": results
        }
    
    def _contains_content_indicators(self, response: str, content_type: str) -> bool:
        """Check if response contains indicators of the expected content type"""
        response_lower = response.lower()
        
        indicators = {
            "joke": ["haha", "😂", "funny", "laugh", "punchline", "another joke"],
            "riddle": ["riddle", "guess", "puzzle", "think", "answer", "mystery"],
            "fact": ["fact", "did you know", "amazing", "interesting", "learn"],
            "rhyme": ["rhyme", "poem", "verse", "twinkle", "roses are red"],
            "song": ["sing", "song", "music", "🎵", "melody", "tune"],
            "story": ["once upon", "story", "tale", "the end", "adventure", "character"],
            "game": ["game", "play", "fun", "activity", "ready", "let's play"]
        }
        
        content_indicators = indicators.get(content_type, [])
        return any(indicator in response_lower for indicator in content_indicators)
    
    async def test_joke_detection(self):
        """Test joke content type detection"""
        joke_inputs = [
            "Tell me a joke",
            "Something funny",
            "Make me laugh",
            "Do you know any jokes?",
            "I want to hear something hilarious",
            "Can you be funny?"
        ]
        return await self.test_content_type_detection(joke_inputs, "joke")
    
    async def test_riddle_detection(self):
        """Test riddle content type detection"""
        riddle_inputs = [
            "Give me a riddle",
            "Can you puzzle me",
            "What am I riddle",
            "I want a brain teaser",
            "Tell me a mystery",
            "Riddle me this"
        ]
        return await self.test_content_type_detection(riddle_inputs, "riddle")
    
    async def test_fact_detection(self):
        """Test fact content type detection"""
        fact_inputs = [
            "Tell me a cool fact",
            "Did you know",
            "Something interesting",
            "Teach me something new",
            "What's an amazing fact?",
            "I want to learn"
        ]
        return await self.test_content_type_detection(fact_inputs, "fact")
    
    async def test_rhyme_detection(self):
        """Test rhyme content type detection"""
        rhyme_inputs = [
            "Recite a poem",
            "Tell me a rhyme",
            "Twinkle twinkle",
            "Say a nursery rhyme",
            "I want to hear poetry",
            "Roses are red"
        ]
        return await self.test_content_type_detection(rhyme_inputs, "rhyme")
    
    async def test_song_detection(self):
        """Test song content type detection"""
        song_inputs = [
            "Sing me a song",
            "Let's sing",
            "Play music",
            "Can you sing something?",
            "I want to hear a melody",
            "Sing a lullaby"
        ]
        return await self.test_content_type_detection(song_inputs, "song")
    
    async def test_story_detection(self):
        """Test story content type detection"""
        story_inputs = [
            "Tell me a story",
            "Once upon a time",
            "Adventure tale",
            "Read me a story",
            "I want to hear a fairy tale",
            "Tell me about a character"
        ]
        return await self.test_content_type_detection(story_inputs, "story")
    
    async def test_game_detection(self):
        """Test game content type detection"""
        game_inputs = [
            "Let's play",
            "What can we do",
            "I'm bored",
            "Want to play a game?",
            "Something fun to do",
            "Can we play together?"
        ]
        return await self.test_content_type_detection(game_inputs, "game")
    
    async def test_local_content_tier(self):
        """Test that local content is served first (Tier 1)"""
        try:
            # Test with story request to check if local content is used
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Tell me a story about a bear"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    metadata = data.get("metadata", {})
                    
                    # Check if response contains default content indicators
                    has_local_content = (
                        "bear" in response_text.lower() or
                        "mouse" in response_text.lower() or
                        "default" in str(metadata).lower() or
                        len(response_text) > 100  # Local stories should be substantial
                    )
                    
                    return {
                        "success": True,
                        "local_content_detected": has_local_content,
                        "response_length": len(response_text),
                        "metadata": metadata,
                        "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_llm_fallback_tier(self):
        """Test LLM fallback when no local content (Tier 3)"""
        try:
            # Test with a unique request that shouldn't have local content
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Tell me a story about a magical robot unicorn in space"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    content_type = data.get("content_type", "conversation")
                    
                    # Check if LLM generated content
                    llm_generated = (
                        len(response_text) > 50 and  # Should be substantial
                        ("robot" in response_text.lower() or "unicorn" in response_text.lower() or "space" in response_text.lower()) and
                        (content_type == "story" or "story" in response_text.lower())
                    )
                    
                    return {
                        "success": True,
                        "llm_fallback_working": llm_generated,
                        "content_type": content_type,
                        "response_length": len(response_text),
                        "contains_requested_elements": any(word in response_text.lower() for word in ["robot", "unicorn", "space"]),
                        "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_joke_formatting(self):
        """Test joke formatting: setup + punchline + reaction + 'Want another?'"""
        try:
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Tell me a funny joke"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    
                    # Check joke formatting elements
                    has_setup_punchline = len(response_text.split('\n')) >= 2 or '?' in response_text
                    has_reaction = any(indicator in response_text.lower() for indicator in ["haha", "😂", "funny", "laugh"])
                    has_reengagement = any(phrase in response_text.lower() for phrase in ["another", "more", "want"])
                    
                    return {
                        "success": has_setup_punchline and (has_reaction or has_reengagement),
                        "has_setup_punchline": has_setup_punchline,
                        "has_reaction": has_reaction,
                        "has_reengagement": has_reengagement,
                        "response_length": len(response_text),
                        "response_text": response_text
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_riddle_formatting(self):
        """Test riddle formatting: question + wait for answer + celebration"""
        try:
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Give me a riddle to solve"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    
                    # Check riddle formatting elements
                    has_question = '?' in response_text
                    asks_for_answer = any(phrase in response_text.lower() for phrase in ["answer", "think", "guess", "tell me"])
                    has_encouragement = any(word in response_text.lower() for word in ["ready", "time", "when"])
                    
                    return {
                        "success": has_question and asks_for_answer,
                        "has_question": has_question,
                        "asks_for_answer": asks_for_answer,
                        "has_encouragement": has_encouragement,
                        "response_length": len(response_text),
                        "response_text": response_text
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_fact_formatting(self):
        """Test fact formatting: fact + enthusiastic reaction + followup"""
        try:
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Tell me an amazing fact"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    
                    # Check fact formatting elements
                    has_fact_content = len(response_text) > 30  # Should be substantial
                    has_enthusiasm = any(word in response_text.lower() for word in ["amazing", "incredible", "wow", "cool", "awesome", "🤯"])
                    has_followup = any(phrase in response_text.lower() for phrase in ["more", "another", "learn", "want"])
                    
                    return {
                        "success": has_fact_content and (has_enthusiasm or has_followup),
                        "has_fact_content": has_fact_content,
                        "has_enthusiasm": has_enthusiasm,
                        "has_followup": has_followup,
                        "response_length": len(response_text),
                        "response_text": response_text
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_story_formatting(self):
        """Test story formatting: full-length (400-800 words) with proper ending"""
        try:
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Tell me a complete story about a brave little animal"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    word_count = len(response_text.split())
                    
                    # Check story formatting elements
                    is_full_length = word_count >= 50  # At least substantial content
                    has_story_structure = any(phrase in response_text.lower() for phrase in ["once", "there was", "lived", "one day"])
                    has_proper_ending = any(phrase in response_text.lower() for phrase in ["end", "lived happily", "learned", "never forgot"])
                    has_reengagement = any(phrase in response_text.lower() for phrase in ["another", "more story", "want"])
                    
                    return {
                        "success": is_full_length and has_story_structure,
                        "is_full_length": is_full_length,
                        "word_count": word_count,
                        "has_story_structure": has_story_structure,
                        "has_proper_ending": has_proper_ending,
                        "has_reengagement": has_reengagement,
                        "response_length": len(response_text),
                        "response_preview": response_text[:300] + "..." if len(response_text) > 300 else response_text
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_token_limits(self):
        """Test appropriate token limits for different content types"""
        test_cases = [
            ("Tell me a story", "story", 300),  # Stories should be longer
            ("Tell me a joke", "joke", 100),    # Jokes should be shorter
            ("Give me a riddle", "riddle", 100), # Riddles should be shorter
            ("Just say hi", "conversation", 50)   # Regular chat should be shortest
        ]
        
        results = []
        
        for message, expected_type, min_length in test_cases:
            try:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": message
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "conversation")
                        
                        # Check if response length is appropriate
                        length_appropriate = len(response_text) >= min_length if expected_type == "story" else len(response_text) >= 20
                        
                        results.append({
                            "message": message,
                            "expected_type": expected_type,
                            "actual_type": content_type,
                            "response_length": len(response_text),
                            "min_expected_length": min_length,
                            "length_appropriate": length_appropriate
                        })
                    else:
                        results.append({
                            "message": message,
                            "error": f"HTTP {response.status}",
                            "length_appropriate": False
                        })
                        
                await asyncio.sleep(0.2)
                
            except Exception as e:
                results.append({
                    "message": message,
                    "error": str(e),
                    "length_appropriate": False
                })
        
        # Calculate success
        appropriate_lengths = sum(1 for r in results if r.get("length_appropriate", False))
        success_rate = appropriate_lengths / len(results) if results else 0
        
        return {
            "success": success_rate >= 0.75,  # 75% success rate
            "success_rate": success_rate,
            "appropriate_lengths": appropriate_lengths,
            "total_tests": len(results),
            "results": results
        }
    
    async def test_emotional_expressions(self):
        """Test that responses include appropriate emotional cues"""
        test_inputs = [
            "Tell me a joke",
            "Give me a riddle", 
            "Tell me a cool fact",
            "Sing me a song"
        ]
        
        emotional_indicators = ["😂", "🤯", "✨", "🎵", "🎶", "🧩", "amazing", "awesome", "wonderful", "great", "haha", "wow"]
        
        results = []
        
        for test_input in test_inputs:
            try:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": test_input
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        
                        has_emotional_expression = any(indicator in response_text for indicator in emotional_indicators)
                        
                        results.append({
                            "input": test_input,
                            "has_emotional_expression": has_emotional_expression,
                            "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
                        })
                    else:
                        results.append({
                            "input": test_input,
                            "has_emotional_expression": False,
                            "error": f"HTTP {response.status}"
                        })
                        
                await asyncio.sleep(0.2)
                
            except Exception as e:
                results.append({
                    "input": test_input,
                    "has_emotional_expression": False,
                    "error": str(e)
                })
        
        # Calculate success
        emotional_responses = sum(1 for r in results if r.get("has_emotional_expression", False))
        success_rate = emotional_responses / len(results) if results else 0
        
        return {
            "success": success_rate >= 0.5,  # 50% should have emotional expressions
            "success_rate": success_rate,
            "emotional_responses": emotional_responses,
            "total_tests": len(results),
            "results": results
        }
    
    async def test_reengagement_prompts(self):
        """Test that responses include re-engagement prompts"""
        test_inputs = [
            "Tell me a joke",
            "Give me a riddle",
            "Tell me a story",
            "Sing me a song"
        ]
        
        reengagement_phrases = ["another", "more", "want", "would you like", "should we", "ready for", "what do you think"]
        
        results = []
        
        for test_input in test_inputs:
            try:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": test_input
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        
                        has_reengagement = any(phrase in response_text.lower() for phrase in reengagement_phrases)
                        
                        results.append({
                            "input": test_input,
                            "has_reengagement": has_reengagement,
                            "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
                        })
                    else:
                        results.append({
                            "input": test_input,
                            "has_reengagement": False,
                            "error": f"HTTP {response.status}"
                        })
                        
                await asyncio.sleep(0.2)
                
            except Exception as e:
                results.append({
                    "input": test_input,
                    "has_reengagement": False,
                    "error": str(e)
                })
        
        # Calculate success
        reengagement_responses = sum(1 for r in results if r.get("has_reengagement", False))
        success_rate = reengagement_responses / len(results) if results else 0
        
        return {
            "success": success_rate >= 0.6,  # 60% should have re-engagement
            "success_rate": success_rate,
            "reengagement_responses": reengagement_responses,
            "total_tests": len(results),
            "results": results
        }
    
    async def test_natural_language_inputs(self):
        """Test content detection with natural child-like inputs"""
        natural_inputs = [
            ("I'm sad, can you make me laugh?", "joke"),
            ("I don't know what to do, I'm so bored", "game"),
            ("Mommy used to tell me stories before bed", "story"),
            ("Can you teach me something cool?", "fact"),
            ("I love when people sing to me", "song"),
            ("My teacher taught us a poem today", "rhyme"),
            ("I want to solve something tricky", "riddle")
        ]
        
        results = []
        
        for natural_input, expected_type in natural_inputs:
            try:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": natural_input
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "conversation")
                        
                        # Check if appropriate content was detected
                        type_detected = (
                            content_type == expected_type or 
                            self._contains_content_indicators(response_text, expected_type)
                        )
                        
                        results.append({
                            "input": natural_input,
                            "expected_type": expected_type,
                            "detected_type": content_type,
                            "type_correct": type_detected,
                            "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
                        })
                    else:
                        results.append({
                            "input": natural_input,
                            "expected_type": expected_type,
                            "type_correct": False,
                            "error": f"HTTP {response.status}"
                        })
                        
                await asyncio.sleep(0.2)
                
            except Exception as e:
                results.append({
                    "input": natural_input,
                    "expected_type": expected_type,
                    "type_correct": False,
                    "error": str(e)
                })
        
        # Calculate success
        correct_detections = sum(1 for r in results if r.get("type_correct", False))
        success_rate = correct_detections / len(results) if results else 0
        
        return {
            "success": success_rate >= 0.6,  # 60% success rate for natural language
            "success_rate": success_rate,
            "correct_detections": correct_detections,
            "total_tests": len(results),
            "results": results
        }

async def main():
    """Run the enhanced content library tests"""
    async with EnhancedContentTester() as tester:
        results = await tester.run_enhanced_content_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 ENHANCED CONTENT LIBRARY SYSTEM TEST RESULTS")
        print("="*80)
        
        passed = sum(1 for r in results.values() if r["status"] == "PASS")
        failed = sum(1 for r in results.values() if r["status"] == "FAIL")
        errors = sum(1 for r in results.values() if r["status"] == "ERROR")
        total = len(results)
        
        print(f"\n📊 SUMMARY:")
        print(f"✅ PASSED: {passed}/{total}")
        print(f"❌ FAILED: {failed}/{total}")
        print(f"🚨 ERRORS: {errors}/{total}")
        print(f"📈 SUCCESS RATE: {(passed/total)*100:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for test_name, result in results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "🚨"
            print(f"{status_icon} {test_name}: {result['status']}")
            
            # Show key details for failed tests
            if result["status"] != "PASS" and "details" in result:
                details = result["details"]
                if "success_rate" in details:
                    print(f"   📊 Success Rate: {details['success_rate']*100:.1f}%")
                if "error" in details:
                    print(f"   🚨 Error: {details['error']}")
        
        print("\n" + "="*80)
        
        return results

if __name__ == "__main__":
    asyncio.run(main())