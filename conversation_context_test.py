#!/usr/bin/env python3
"""
CRITICAL CONVERSATION CONTEXT CONTINUITY TESTING - COMPREHENSIVE VALIDATION
Tests the conversation context loss issue and dynamic token allocation system
"""

import asyncio
import aiohttp
import json
import base64
import uuid
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend URL from environment
BACKEND_URL = "https://ac3a5a48-4dec-498e-8545-e5993602e42f.preview.emergentagent.com/api"

class ConversationContextTester:
    """Comprehensive conversation context continuity tester"""
    
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.test_user_id = None
        self.test_session_id = None
        self.conversation_history = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_all_tests(self):
        """Run all conversation context continuity tests"""
        logger.info("🎯 Starting CRITICAL CONVERSATION CONTEXT CONTINUITY TESTING...")
        
        # Test sequence focusing on context continuity
        test_sequence = [
            # SETUP TESTS
            ("Setup - Health Check", self.test_health_check),
            ("Setup - Create Test User", self.test_create_user_profile),
            ("Setup - Create Conversation Session", self.test_create_conversation_session),
            
            # CRITICAL CONVERSATION CONTINUITY TESTS
            ("CRITICAL - Multi-Turn Conversation Flow (4 exchanges)", self.test_multi_turn_conversation),
            ("CRITICAL - Question-Answer Sequence Context", self.test_question_answer_sequence),
            ("CRITICAL - Story Follow-up Questions", self.test_story_followup_questions),
            ("CRITICAL - Memory Reference Test", self.test_memory_reference),
            ("CRITICAL - Session Persistence", self.test_session_persistence),
            
            # DYNAMIC TOKEN ALLOCATION TESTS
            ("TOKEN - Story Generation (2000 tokens)", self.test_story_generation_tokens),
            ("TOKEN - Creative Content (800 tokens)", self.test_creative_content_tokens),
            ("TOKEN - Regular Conversation (1000 tokens)", self.test_regular_conversation_tokens),
            ("TOKEN - Short Content (400 tokens)", self.test_short_content_tokens),
            
            # SPECIFIC CONVERSATION TEST SCENARIOS
            ("SCENARIO - Multi-turn Elephant Test", self.test_multi_turn_elephant),
            ("SCENARIO - Color Preference Follow-up", self.test_color_preference_followup),
            ("SCENARIO - Story Continuation", self.test_story_continuation),
            ("SCENARIO - Context Reference", self.test_context_reference),
            
            # STORY GENERATION VALIDATION (CRITICAL ISSUE)
            ("STORY - Complete Story Generation Test", self.test_complete_story_generation),
            ("STORY - Story Length Validation", self.test_story_length_validation),
            ("STORY - Story Structure Validation", self.test_story_structure_validation),
            ("STORY - Iterative Story Generation", self.test_iterative_story_generation),
            
            # CONVERSATION FLOW VALIDATION
            ("FLOW - Context Preservation", self.test_context_preservation),
            ("FLOW - Natural Response Flow", self.test_natural_response_flow),
            ("FLOW - No Context Loss Detection", self.test_no_context_loss),
            
            # CLEANUP
            ("Cleanup - Test Summary", self.test_summary)
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
                logger.info(f"{status} Test {test_name}")
                
                # Add delay between tests to avoid rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ Test {test_name} failed with exception: {str(e)}")
                self.test_results[test_name] = {
                    "status": "ERROR",
                    "details": {"error": str(e)}
                }
        
        return self.test_results
    
    async def test_health_check(self):
        """Test health check endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "status": data["status"],
                        "agents_initialized": data["agents"]["orchestrator"],
                        "gemini_configured": data["agents"]["gemini_configured"],
                        "deepgram_configured": data["agents"]["deepgram_configured"]
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_create_user_profile(self):
        """Create test user profile"""
        try:
            profile_data = {
                "name": "Context Test Child",
                "age": 8,
                "location": "Test City",
                "timezone": "America/New_York",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "animals", "adventures"],
                "learning_goals": ["reading", "creativity"],
                "parent_email": "test@example.com"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/users/profile",
                json=profile_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_user_id = data["id"]
                    return {
                        "success": True,
                        "user_id": data["id"],
                        "name": data["name"]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_create_conversation_session(self):
        """Create conversation session"""
        try:
            session_data = {
                "user_id": self.test_user_id,
                "session_name": "Context Continuity Test Session"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/session",
                json=session_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_session_id = data["id"]
                    return {
                        "success": True,
                        "session_id": data["id"]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_message(self, message: str, expected_context: str = None):
        """Send a message and track conversation history"""
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
                    
                    # Track conversation history
                    conversation_entry = {
                        "user_message": message,
                        "bot_response": data.get("response_text", ""),
                        "content_type": data.get("content_type", ""),
                        "response_length": len(data.get("response_text", "")),
                        "has_audio": bool(data.get("response_audio")),
                        "metadata": data.get("metadata", {}),
                        "timestamp": datetime.now().isoformat()
                    }
                    self.conversation_history.append(conversation_entry)
                    
                    # Check for context awareness if expected
                    context_aware = True
                    if expected_context:
                        response_text = data.get("response_text", "").lower()
                        context_aware = expected_context.lower() in response_text
                    
                    return {
                        "success": True,
                        "response_text": data.get("response_text", ""),
                        "response_length": len(data.get("response_text", "")),
                        "content_type": data.get("content_type", ""),
                        "has_audio": bool(data.get("response_audio")),
                        "context_aware": context_aware,
                        "metadata": data.get("metadata", {})
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_multi_turn_conversation(self):
        """Test 4-message exchange to verify context is maintained"""
        try:
            logger.info("🔄 Testing multi-turn conversation flow...")
            
            # Turn 1: Initial greeting
            result1 = await self.send_message("Hi Buddy!")
            if not result1["success"]:
                return {"success": False, "error": "Turn 1 failed", "details": result1}
            
            await asyncio.sleep(1)
            
            # Turn 2: Ask about elephants
            result2 = await self.send_message("Tell me about elephants")
            if not result2["success"]:
                return {"success": False, "error": "Turn 2 failed", "details": result2}
            
            await asyncio.sleep(1)
            
            # Turn 3: Follow-up question (should reference elephants)
            result3 = await self.send_message("Are they bigger than cars?", expected_context="elephant")
            if not result3["success"]:
                return {"success": False, "error": "Turn 3 failed", "details": result3}
            
            await asyncio.sleep(1)
            
            # Turn 4: Another follow-up (should maintain context)
            result4 = await self.send_message("What do they eat?", expected_context="elephant")
            if not result4["success"]:
                return {"success": False, "error": "Turn 4 failed", "details": result4}
            
            # Analyze context continuity
            context_maintained = (
                result3["context_aware"] and 
                result4["context_aware"] and
                all(r["response_length"] > 10 for r in [result1, result2, result3, result4])
            )
            
            return {
                "success": context_maintained,
                "turns_completed": 4,
                "context_maintained": context_maintained,
                "turn_results": {
                    "turn_1": {"length": result1["response_length"], "type": result1["content_type"]},
                    "turn_2": {"length": result2["response_length"], "type": result2["content_type"]},
                    "turn_3": {"length": result3["response_length"], "context_aware": result3["context_aware"]},
                    "turn_4": {"length": result4["response_length"], "context_aware": result4["context_aware"]}
                },
                "conversation_flow": "Multi-turn context maintained" if context_maintained else "Context lost"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_question_answer_sequence(self):
        """Test bot asks question, user responds, bot remembers"""
        try:
            logger.info("❓ Testing question-answer sequence...")
            
            # Bot asks a question
            result1 = await self.send_message("Ask me a question about my favorite things")
            if not result1["success"]:
                return {"success": False, "error": "Question request failed", "details": result1}
            
            await asyncio.sleep(1)
            
            # User responds with preference
            result2 = await self.send_message("My favorite color is blue and I love dogs")
            if not result2["success"]:
                return {"success": False, "error": "Answer failed", "details": result2}
            
            await asyncio.sleep(1)
            
            # Test if bot remembers the preference
            result3 = await self.send_message("What did I just tell you about my favorites?", expected_context="blue")
            if not result3["success"]:
                return {"success": False, "error": "Memory test failed", "details": result3}
            
            # Check if bot acknowledges the preference
            remembers_preference = (
                "blue" in result3["response_text"].lower() or 
                "dog" in result3["response_text"].lower() or
                "favorite" in result3["response_text"].lower()
            )
            
            return {
                "success": remembers_preference,
                "question_asked": len(result1["response_text"]) > 10,
                "answer_processed": len(result2["response_text"]) > 10,
                "preference_remembered": remembers_preference,
                "memory_response": result3["response_text"][:100] + "..." if len(result3["response_text"]) > 100 else result3["response_text"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_story_followup_questions(self):
        """Test story request followed by questions about the story"""
        try:
            logger.info("📚 Testing story follow-up questions...")
            
            # Request a story about a cat
            result1 = await self.send_message("Tell me a story about a brave cat")
            if not result1["success"]:
                return {"success": False, "error": "Story request failed", "details": result1}
            
            story_text = result1["response_text"]
            story_length = len(story_text)
            
            await asyncio.sleep(1)
            
            # Ask about the cat's name
            result2 = await self.send_message("What was the cat's name in that story?", expected_context="cat")
            if not result2["success"]:
                return {"success": False, "error": "Name question failed", "details": result2}
            
            await asyncio.sleep(1)
            
            # Ask about the cat's friends
            result3 = await self.send_message("Did the cat have any friends?", expected_context="cat")
            if not result3["success"]:
                return {"success": False, "error": "Friends question failed", "details": result3}
            
            # Analyze story continuity
            story_continuity = (
                result2["context_aware"] and 
                result3["context_aware"] and
                story_length > 50  # Story should be substantial
            )
            
            return {
                "success": story_continuity,
                "story_generated": story_length > 50,
                "story_length": story_length,
                "story_word_count": len(story_text.split()),
                "name_question_context": result2["context_aware"],
                "friends_question_context": result3["context_aware"],
                "story_continuity": story_continuity,
                "content_type": result1["content_type"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_memory_reference(self):
        """Test that bot references previous conversation points"""
        try:
            logger.info("🧠 Testing memory reference...")
            
            # Establish a topic (dogs)
            result1 = await self.send_message("I really love golden retriever dogs")
            if not result1["success"]:
                return {"success": False, "error": "Topic establishment failed", "details": result1}
            
            await asyncio.sleep(1)
            
            # Talk about something else
            result2 = await self.send_message("What's the weather like?")
            if not result2["success"]:
                return {"success": False, "error": "Topic change failed", "details": result2}
            
            await asyncio.sleep(1)
            
            # Ask bot to remember previous conversation
            result3 = await self.send_message("Remember what we talked about earlier?", expected_context="dog")
            if not result3["success"]:
                return {"success": False, "error": "Memory reference failed", "details": result3}
            
            # Check if bot references the dog conversation
            references_dogs = (
                "dog" in result3["response_text"].lower() or
                "golden retriever" in result3["response_text"].lower() or
                "earlier" in result3["response_text"].lower() or
                "talked about" in result3["response_text"].lower()
            )
            
            return {
                "success": references_dogs,
                "topic_established": len(result1["response_text"]) > 10,
                "topic_changed": len(result2["response_text"]) > 10,
                "memory_referenced": references_dogs,
                "memory_response": result3["response_text"][:150] + "..." if len(result3["response_text"]) > 150 else result3["response_text"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_session_persistence(self):
        """Test conversation history is maintained throughout session"""
        try:
            logger.info("💾 Testing session persistence...")
            
            # Check if we have conversation history from previous tests
            history_count = len(self.conversation_history)
            
            if history_count < 3:
                # Create some conversation history
                await self.send_message("Let's talk about space")
                await asyncio.sleep(0.5)
                await self.send_message("Tell me about the moon")
                await asyncio.sleep(0.5)
                await self.send_message("How far is it from Earth?")
                history_count = len(self.conversation_history)
            
            # Test if bot can reference the session history
            result = await self.send_message("What have we been talking about in this conversation?")
            if not result["success"]:
                return {"success": False, "error": "Session reference failed", "details": result}
            
            # Analyze if response shows awareness of conversation history
            response_text = result["response_text"].lower()
            shows_awareness = (
                "we" in response_text or
                "talked" in response_text or
                "discussed" in response_text or
                "conversation" in response_text or
                len(response_text) > 50  # Substantial response indicating awareness
            )
            
            return {
                "success": shows_awareness,
                "conversation_history_count": history_count,
                "session_awareness": shows_awareness,
                "response_length": len(result["response_text"]),
                "session_response": result["response_text"][:100] + "..." if len(result["response_text"]) > 100 else result["response_text"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_story_generation_tokens(self):
        """Test story generation gets 2000 tokens and generates complete narratives"""
        try:
            logger.info("📖 Testing story generation token allocation...")
            
            result = await self.send_message("Please tell me a complete story about a brave little mouse who goes on an adventure")
            if not result["success"]:
                return {"success": False, "error": "Story generation failed", "details": result}
            
            story_text = result["response_text"]
            word_count = len(story_text.split())
            char_count = len(story_text)
            
            # Check if story meets length requirements (300+ words for 2000 tokens)
            meets_length_requirement = word_count >= 300
            has_complete_structure = all(keyword in story_text.lower() for keyword in ["once", "adventure", "mouse"])
            
            return {
                "success": meets_length_requirement,
                "story_word_count": word_count,
                "story_char_count": char_count,
                "meets_300_word_requirement": meets_length_requirement,
                "has_complete_structure": has_complete_structure,
                "content_type": result["content_type"],
                "token_allocation": "2000 tokens" if meets_length_requirement else "Insufficient tokens",
                "story_preview": story_text[:200] + "..." if len(story_text) > 200 else story_text
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_creative_content_tokens(self):
        """Test songs/poems get 800 tokens for full content"""
        try:
            logger.info("🎵 Testing creative content token allocation...")
            
            result = await self.send_message("Please write me a song about friendship")
            if not result["success"]:
                return {"success": False, "error": "Creative content failed", "details": result}
            
            content_text = result["response_text"]
            word_count = len(content_text.split())
            char_count = len(content_text)
            
            # Check if creative content meets expected length (100+ words for 800 tokens)
            meets_length_requirement = word_count >= 100
            has_creative_structure = any(keyword in content_text.lower() for keyword in ["verse", "chorus", "song", "friendship"])
            
            return {
                "success": meets_length_requirement,
                "content_word_count": word_count,
                "content_char_count": char_count,
                "meets_100_word_requirement": meets_length_requirement,
                "has_creative_structure": has_creative_structure,
                "content_type": result["content_type"],
                "token_allocation": "800 tokens" if meets_length_requirement else "Insufficient tokens",
                "content_preview": content_text[:150] + "..." if len(content_text) > 150 else content_text
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_regular_conversation_tokens(self):
        """Test normal chat gets 1000 tokens appropriately"""
        try:
            logger.info("💬 Testing regular conversation token allocation...")
            
            result = await self.send_message("How are you doing today? Tell me about yourself.")
            if not result["success"]:
                return {"success": False, "error": "Regular conversation failed", "details": result}
            
            response_text = result["response_text"]
            word_count = len(response_text.split())
            char_count = len(response_text)
            
            # Regular conversation should be substantial but not as long as stories
            appropriate_length = 50 <= word_count <= 200
            conversational_tone = any(keyword in response_text.lower() for keyword in ["i", "today", "doing", "great", "good"])
            
            return {
                "success": appropriate_length and conversational_tone,
                "response_word_count": word_count,
                "response_char_count": char_count,
                "appropriate_length": appropriate_length,
                "conversational_tone": conversational_tone,
                "content_type": result["content_type"],
                "token_allocation": "1000 tokens" if appropriate_length else "Token allocation issue",
                "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_short_content_tokens(self):
        """Test riddles/jokes get 400 tokens efficiently"""
        try:
            logger.info("😄 Testing short content token allocation...")
            
            result = await self.send_message("Tell me a riddle")
            if not result["success"]:
                return {"success": False, "error": "Short content failed", "details": result}
            
            content_text = result["response_text"]
            word_count = len(content_text.split())
            char_count = len(content_text)
            
            # Short content should be concise but complete
            appropriate_length = 20 <= word_count <= 80
            has_riddle_structure = any(keyword in content_text.lower() for keyword in ["what", "riddle", "answer", "guess", "?"])
            
            return {
                "success": appropriate_length and has_riddle_structure,
                "content_word_count": word_count,
                "content_char_count": char_count,
                "appropriate_length": appropriate_length,
                "has_riddle_structure": has_riddle_structure,
                "content_type": result["content_type"],
                "token_allocation": "400 tokens" if appropriate_length else "Token allocation issue",
                "content_preview": content_text
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_multi_turn_elephant(self):
        """Test specific multi-turn elephant scenario"""
        try:
            logger.info("🐘 Testing multi-turn elephant scenario...")
            
            # Exact scenario from review request
            result1 = await self.send_message("Hi Buddy!")
            await asyncio.sleep(0.5)
            result2 = await self.send_message("Tell me about elephants")
            await asyncio.sleep(0.5)
            result3 = await self.send_message("Are they bigger than cars?")
            await asyncio.sleep(0.5)
            result4 = await self.send_message("What do they eat?")
            
            # Check context continuity
            context_maintained = (
                "elephant" in result3["response_text"].lower() and
                "elephant" in result4["response_text"].lower()
            )
            
            return {
                "success": context_maintained,
                "scenario": "Multi-turn elephant test",
                "context_maintained": context_maintained,
                "all_responses_received": all(r["success"] for r in [result1, result2, result3, result4]),
                "response_lengths": [len(r["response_text"]) for r in [result1, result2, result3, result4]]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_color_preference_followup(self):
        """Test color preference follow-up scenario"""
        try:
            logger.info("🎨 Testing color preference follow-up...")
            
            # Bot asks about favorite color (simulated)
            result1 = await self.send_message("What's your favorite color?")
            await asyncio.sleep(0.5)
            
            # User responds with blue
            result2 = await self.send_message("Blue")
            await asyncio.sleep(0.5)
            
            # Check if bot acknowledges blue preference
            result3 = await self.send_message("Do you remember what I said?")
            
            acknowledges_blue = "blue" in result3["response_text"].lower()
            
            return {
                "success": acknowledges_blue,
                "scenario": "Color preference follow-up",
                "blue_acknowledged": acknowledges_blue,
                "response_text": result3["response_text"][:100] + "..." if len(result3["response_text"]) > 100 else result3["response_text"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_story_continuation(self):
        """Test story continuation scenario"""
        try:
            logger.info("📚 Testing story continuation...")
            
            result1 = await self.send_message("Tell me a story about a cat")
            await asyncio.sleep(0.5)
            result2 = await self.send_message("What was the cat's name?")
            await asyncio.sleep(0.5)
            result3 = await self.send_message("Did the cat have friends?")
            
            story_continuity = (
                "cat" in result2["response_text"].lower() and
                "cat" in result3["response_text"].lower()
            )
            
            return {
                "success": story_continuity,
                "scenario": "Story continuation",
                "story_continuity": story_continuity,
                "story_length": len(result1["response_text"]),
                "context_maintained": story_continuity
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_context_reference(self):
        """Test context reference scenario"""
        try:
            logger.info("🔗 Testing context reference...")
            
            # Talk about dogs
            result1 = await self.send_message("I love dogs, they're amazing pets")
            await asyncio.sleep(0.5)
            
            # Later ask about previous conversation
            result2 = await self.send_message("Remember what we talked about?")
            
            references_dogs = "dog" in result2["response_text"].lower()
            
            return {
                "success": references_dogs,
                "scenario": "Context reference",
                "references_previous_topic": references_dogs,
                "response_text": result2["response_text"][:100] + "..." if len(result2["response_text"]) > 100 else result2["response_text"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_complete_story_generation(self):
        """Test complete story generation (addressing critical issue)"""
        try:
            logger.info("📖 Testing complete story generation...")
            
            result = await self.send_message("Tell me a complete story about a brave little mouse adventure")
            if not result["success"]:
                return {"success": False, "error": "Story generation failed", "details": result}
            
            story_text = result["response_text"]
            word_count = len(story_text.split())
            
            # Check story completeness
            has_beginning = any(word in story_text.lower() for word in ["once", "there was", "long ago"])
            has_middle = any(word in story_text.lower() for word in ["adventure", "journey", "went"])
            has_end = any(word in story_text.lower() for word in ["end", "finally", "lived happily"])
            
            complete_story = word_count >= 300 and has_beginning and has_middle
            
            return {
                "success": complete_story,
                "story_word_count": word_count,
                "meets_300_word_requirement": word_count >= 300,
                "has_beginning": has_beginning,
                "has_middle": has_middle,
                "has_end": has_end,
                "complete_narrative": complete_story,
                "content_type": result["content_type"],
                "story_preview": story_text[:300] + "..." if len(story_text) > 300 else story_text
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_story_length_validation(self):
        """Test story length validation (critical issue)"""
        try:
            logger.info("📏 Testing story length validation...")
            
            # Test multiple story requests
            story_tests = [
                "Tell me a story about a brave dragon",
                "I want a story about magical friendship", 
                "Can you tell me a story about a robot who learns to love?"
            ]
            
            story_results = []
            
            for story_request in story_tests:
                result = await self.send_message(story_request)
                if result["success"]:
                    word_count = len(result["response_text"].split())
                    story_results.append({
                        "request": story_request[:30] + "...",
                        "word_count": word_count,
                        "meets_requirement": word_count >= 300,
                        "content_type": result["content_type"]
                    })
                await asyncio.sleep(0.5)
            
            # Calculate success rate
            successful_stories = [s for s in story_results if s["meets_requirement"]]
            success_rate = len(successful_stories) / len(story_results) if story_results else 0
            
            return {
                "success": success_rate >= 0.8,  # 80% success rate required
                "stories_tested": len(story_results),
                "successful_stories": len(successful_stories),
                "success_rate": f"{success_rate*100:.1f}%",
                "average_word_count": sum(s["word_count"] for s in story_results) // len(story_results) if story_results else 0,
                "story_results": story_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_story_structure_validation(self):
        """Test story structure validation"""
        try:
            logger.info("🏗️ Testing story structure validation...")
            
            result = await self.send_message("Tell me a complete story with beginning, middle, and end about a girl who talks to animals")
            if not result["success"]:
                return {"success": False, "error": "Story structure test failed", "details": result}
            
            story_text = result["response_text"].lower()
            
            # Check narrative structure elements
            structure_elements = {
                "opening": any(word in story_text for word in ["once", "there was", "long ago", "in a"]),
                "character": any(word in story_text for word in ["girl", "she", "her"]),
                "conflict": any(word in story_text for word in ["problem", "trouble", "challenge", "difficult"]),
                "resolution": any(word in story_text for word in ["solved", "helped", "saved", "happy", "end"])
            }
            
            structure_score = sum(structure_elements.values())
            complete_structure = structure_score >= 3  # At least 3 out of 4 elements
            
            return {
                "success": complete_structure,
                "structure_score": f"{structure_score}/4",
                "structure_elements": structure_elements,
                "complete_structure": complete_structure,
                "story_word_count": len(result["response_text"].split()),
                "content_type": result["content_type"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_iterative_story_generation(self):
        """Test iterative story generation system"""
        try:
            logger.info("🔄 Testing iterative story generation...")
            
            # Test the iterative system with explicit request
            result = await self.send_message("Please generate a complete, full-length story about a magical adventure with at least 300 words")
            if not result["success"]:
                return {"success": False, "error": "Iterative story generation failed", "details": result}
            
            story_text = result["response_text"]
            word_count = len(story_text.split())
            
            # Check if iterative generation worked
            iterative_success = word_count >= 300
            has_magical_elements = any(word in story_text.lower() for word in ["magic", "magical", "adventure", "quest"])
            
            return {
                "success": iterative_success,
                "iterative_generation": "Working" if iterative_success else "Failed",
                "story_word_count": word_count,
                "meets_300_word_requirement": iterative_success,
                "has_magical_elements": has_magical_elements,
                "content_type": result["content_type"],
                "story_preview": story_text[:200] + "..." if len(story_text) > 200 else story_text
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_context_preservation(self):
        """Test context preservation across multiple interactions"""
        try:
            logger.info("🔒 Testing context preservation...")
            
            # Establish context
            result1 = await self.send_message("My name is Alex and I'm 8 years old")
            await asyncio.sleep(0.5)
            
            # Add more context
            result2 = await self.send_message("I love playing with my pet hamster named Fluffy")
            await asyncio.sleep(0.5)
            
            # Test context preservation
            result3 = await self.send_message("What do you know about me?")
            
            response_text = result3["response_text"].lower()
            preserves_name = "alex" in response_text
            preserves_age = "8" in response_text or "eight" in response_text
            preserves_pet = "hamster" in response_text or "fluffy" in response_text
            
            context_preservation_score = sum([preserves_name, preserves_age, preserves_pet])
            
            return {
                "success": context_preservation_score >= 2,
                "context_preservation_score": f"{context_preservation_score}/3",
                "preserves_name": preserves_name,
                "preserves_age": preserves_age,
                "preserves_pet": preserves_pet,
                "response_text": result3["response_text"][:150] + "..." if len(result3["response_text"]) > 150 else result3["response_text"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_natural_response_flow(self):
        """Test natural response flow without context-ignoring responses"""
        try:
            logger.info("🌊 Testing natural response flow...")
            
            # Test for natural flow
            result1 = await self.send_message("I'm feeling a bit sad today")
            await asyncio.sleep(0.5)
            
            result2 = await self.send_message("Can you cheer me up?")
            
            # Check for natural, contextual responses
            response_text = result2["response_text"].lower()
            
            # Check for context-ignoring phrases
            ignoring_phrases = ["what do you mean", "i don't understand", "can you clarify", "what are you talking about"]
            context_ignoring = any(phrase in response_text for phrase in ignoring_phrases)
            
            # Check for empathetic, contextual response
            empathetic_response = any(word in response_text for word in ["sorry", "understand", "help", "cheer", "better", "feel"])
            
            natural_flow = empathetic_response and not context_ignoring
            
            return {
                "success": natural_flow,
                "natural_flow": natural_flow,
                "empathetic_response": empathetic_response,
                "context_ignoring": context_ignoring,
                "response_text": result2["response_text"][:100] + "..." if len(result2["response_text"]) > 100 else result2["response_text"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_no_context_loss(self):
        """Test for absence of context loss indicators"""
        try:
            logger.info("🚫 Testing no context loss detection...")
            
            # Establish context with specific details
            result1 = await self.send_message("I have a red bicycle that I ride to school every day")
            await asyncio.sleep(0.5)
            
            # Reference the context
            result2 = await self.send_message("Tell me more about it")
            
            response_text = result2["response_text"].lower()
            
            # Check if "it" is properly understood as the bicycle
            understands_reference = any(word in response_text for word in ["bicycle", "bike", "ride", "school", "red"])
            
            # Check for context loss indicators
            context_loss_indicators = ["what do you mean by it", "what are you referring to", "i'm not sure what you mean"]
            has_context_loss = any(indicator in response_text for indicator in context_loss_indicators)
            
            no_context_loss = understands_reference and not has_context_loss
            
            return {
                "success": no_context_loss,
                "understands_reference": understands_reference,
                "has_context_loss": has_context_loss,
                "no_context_loss": no_context_loss,
                "response_text": result2["response_text"][:100] + "..." if len(result2["response_text"]) > 100 else result2["response_text"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_summary(self):
        """Generate test summary"""
        try:
            logger.info("📊 Generating test summary...")
            
            # Count test results
            total_tests = len(self.test_results)
            passed_tests = sum(1 for result in self.test_results.values() if result["status"] == "PASS")
            failed_tests = sum(1 for result in self.test_results.values() if result["status"] == "FAIL")
            error_tests = sum(1 for result in self.test_results.values() if result["status"] == "ERROR")
            
            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            # Analyze conversation history
            conversation_count = len(self.conversation_history)
            avg_response_length = sum(entry["response_length"] for entry in self.conversation_history) / conversation_count if conversation_count > 0 else 0
            
            return {
                "success": True,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "error_tests": error_tests,
                "success_rate": f"{success_rate:.1f}%",
                "conversation_exchanges": conversation_count,
                "average_response_length": round(avg_response_length),
                "test_user_id": self.test_user_id,
                "test_session_id": self.test_session_id
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

async def main():
    """Run the conversation context continuity tests"""
    async with ConversationContextTester() as tester:
        results = await tester.run_all_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 CRITICAL CONVERSATION CONTEXT CONTINUITY TEST RESULTS")
        print("="*80)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result["status"] == "PASS")
        failed_tests = sum(1 for result in results.values() if result["status"] == "FAIL")
        error_tests = sum(1 for result in results.values() if result["status"] == "ERROR")
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   🚫 Errors: {error_tests}")
        print(f"   📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for test_name, result in results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "🚫"
            print(f"   {status_icon} {test_name}: {result['status']}")
            
            # Show key details for critical tests
            if "CRITICAL" in test_name and result["status"] != "PASS":
                details = result.get("details", {})
                if "error" in details:
                    print(f"      Error: {details['error']}")
        
        print("\n" + "="*80)
        
        return results

if __name__ == "__main__":
    asyncio.run(main())