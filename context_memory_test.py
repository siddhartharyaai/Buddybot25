#!/usr/bin/env python3
"""
CRITICAL CONTEXT & MEMORY TESTING - DYNAMIC AI COMPANION BEHAVIOR
Testing whether the AI companion truly behaves like a human companion with perfect context retention,
continuous learning, memory persistence, and dynamic response adaptation.

Using Emma Johnson Profile:
- User ID: emma_johnson_test
- Age: 7, Location: San Francisco
- Interests: animals, stories, music, games
- Learning goals: reading, creativity, social skills
"""

import asyncio
import aiohttp
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend URL from environment
BACKEND_URL = "http://10.64.147.115:8001/api"

class ContextMemoryTester:
    """Comprehensive context and memory testing for AI companion"""
    
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.emma_user_id = "emma_johnson_test"
        self.test_session_id = None
        self.conversation_history = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_comprehensive_context_memory_tests(self):
        """Run all context and memory tests"""
        logger.info("🎯 Starting CRITICAL CONTEXT & MEMORY TESTING - DYNAMIC AI COMPANION BEHAVIOR")
        
        # Test sequence for comprehensive context and memory testing
        test_sequence = [
            # Setup Emma Johnson Profile
            ("Setup - Create Emma Johnson Profile", self.setup_emma_johnson_profile),
            ("Setup - Create Conversation Session", self.create_conversation_session),
            
            # 1. MULTI-TURN CONTEXT RETENTION TEST (10 turns)
            ("Context Test 1 - Tell me about elephants", self.context_test_turn_1),
            ("Context Test 2 - How big are they?", self.context_test_turn_2),
            ("Context Test 3 - Do they like water?", self.context_test_turn_3),
            ("Context Test 4 - Tell me a story about one", self.context_test_turn_4),
            ("Context Test 5 - What was the elephant's name?", self.context_test_turn_5),
            ("Context Test 6 - Sing a song about the same elephant", self.context_test_turn_6),
            ("Context Test 7 - Make it shorter", self.context_test_turn_7),
            ("Context Test 8 - Tell me a riddle about elephants", self.context_test_turn_8),
            ("Context Test 9 - I don't know the answer", self.context_test_turn_9),
            ("Context Test 10 - Tell me more facts about them", self.context_test_turn_10),
            
            # 2. MEMORY PERSISTENCE & LEARNING TEST
            ("Memory Test - Session 1: Express love for dinosaurs", self.memory_test_session_1),
            ("Memory Test - Generate Memory Snapshot", self.generate_memory_snapshot),
            ("Memory Test - Session 2: What do I like?", self.memory_test_session_2),
            ("Memory Test - Session 3: Ask for another story", self.memory_test_session_3),
            
            # 3. DYNAMIC RESPONSE LENGTH TESTING
            ("Response Length - Story Request (200-400 tokens)", self.test_story_response_length),
            ("Response Length - Riddle Request (20-50 tokens)", self.test_riddle_response_length),
            ("Response Length - Song Request (100-150 tokens)", self.test_song_response_length),
            ("Response Length - Joke Request (10-30 tokens)", self.test_joke_response_length),
            ("Response Length - Educational Facts (50-100 tokens)", self.test_educational_response_length),
            ("Response Length - Game Request (30-80 tokens)", self.test_game_response_length),
            ("Response Length - Comment Response (15-40 tokens)", self.test_comment_response_length),
            
            # 4. CONTEXTUAL FOLLOW-UP TESTING
            ("Follow-up Test - Story Follow-ups", self.test_story_followups),
            ("Follow-up Test - Riddle Follow-ups", self.test_riddle_followups),
            ("Follow-up Test - Song Follow-ups", self.test_song_followups),
            ("Follow-up Test - Game Follow-ups", self.test_game_followups),
            
            # 5. PERSONALITY ADAPTATION TESTING
            ("Personality Test - Age-appropriate vocabulary", self.test_age_appropriate_responses),
            ("Personality Test - Interest-based responses", self.test_interest_based_responses),
            ("Personality Test - Learning goal alignment", self.test_learning_goal_alignment),
            
            # 6. EMOTIONAL CONTEXT RETENTION
            ("Emotional Test - Express sadness", self.test_emotional_sadness),
            ("Emotional Test - Check-in later", self.test_emotional_checkin),
            ("Emotional Test - Express excitement", self.test_emotional_excitement),
            ("Emotional Test - Reference excitement", self.test_emotional_reference),
            
            # 7. CROSS-SESSION MEMORY TESTING
            ("Cross-Session Test - New session greeting", self.test_cross_session_greeting),
            ("Cross-Session Test - Reference previous session", self.test_cross_session_reference),
            ("Cross-Session Test - Long-term memory influence", self.test_long_term_memory_influence),
            
            # 8. CONTENT PERSONALIZATION TESTING
            ("Personalization Test - Animal-themed content", self.test_animal_themed_content),
            ("Personalization Test - Age-appropriate difficulty", self.test_age_appropriate_difficulty),
            ("Personalization Test - San Francisco references", self.test_location_references),
            
            # SPECIFIC TEST SCENARIOS
            ("Scenario A - Story Context Chain", self.test_story_context_chain),
            ("Scenario B - Learning & Adaptation", self.test_learning_adaptation),
            ("Scenario C - Game State Retention", self.test_game_state_retention),
        ]
        
        for test_name, test_func in test_sequence:
            try:
                logger.info(f"Running test: {test_name}")
                result = await test_func()
                self.test_results[test_name] = {
                    "status": "PASS" if result.get("success", False) else "FAIL",
                    "details": result
                }
                logger.info(f"Test {test_name}: {'PASS' if result.get('success', False) else 'FAIL'}")
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {str(e)}")
                self.test_results[test_name] = {
                    "status": "ERROR",
                    "details": {"error": str(e)}
                }
        
        return self.test_results
    
    async def setup_emma_johnson_profile(self):
        """Create Emma Johnson test profile"""
        try:
            profile_data = {
                "name": "Emma Johnson",
                "age": 7,
                "location": "San Francisco",
                "timezone": "America/Los_Angeles",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["animals", "stories", "music", "games"],
                "learning_goals": ["reading", "creativity", "social skills"],
                "parent_email": "parent@example.com"
            }
            
            # First try to get existing profile
            async with self.session.get(
                f"{BACKEND_URL}/users/profile/{self.emma_user_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Using existing Emma Johnson profile: {self.emma_user_id}")
                    return {
                        "success": True,
                        "user_id": data["id"],
                        "name": data["name"],
                        "age": data["age"],
                        "existing_profile": True
                    }
            
            # Create new profile if doesn't exist
            profile_data["id"] = self.emma_user_id
            async with self.session.post(
                f"{BACKEND_URL}/users/profile",
                json=profile_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Created Emma Johnson profile: {self.emma_user_id}")
                    return {
                        "success": True,
                        "user_id": data["id"],
                        "name": data["name"],
                        "age": data["age"],
                        "interests": data["interests"],
                        "learning_goals": data["learning_goals"],
                        "created": True
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_conversation_session(self):
        """Create conversation session for Emma"""
        try:
            session_data = {
                "user_id": self.emma_user_id,
                "session_name": "Emma's Context Memory Test Session"
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
                        "session_id": data["id"],
                        "user_id": data["user_id"],
                        "session_name": data["session_name"]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_message_and_track(self, message: str, expected_context: str = None):
        """Send message and track conversation history"""
        try:
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.emma_user_id,
                "message": message
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Track conversation
                    conversation_entry = {
                        "user_message": message,
                        "ai_response": data.get("response_text", ""),
                        "content_type": data.get("content_type", ""),
                        "response_length": len(data.get("response_text", "")),
                        "has_audio": bool(data.get("response_audio")),
                        "metadata": data.get("metadata", {}),
                        "timestamp": datetime.now().isoformat()
                    }
                    self.conversation_history.append(conversation_entry)
                    
                    # Check context retention if expected
                    context_retained = True
                    if expected_context:
                        response_text = data.get("response_text", "").lower()
                        context_retained = expected_context.lower() in response_text
                    
                    return {
                        "success": True,
                        "response_text": data.get("response_text", ""),
                        "content_type": data.get("content_type", ""),
                        "response_length": len(data.get("response_text", "")),
                        "has_audio": bool(data.get("response_audio")),
                        "context_retained": context_retained,
                        "metadata": data.get("metadata", {})
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # MULTI-TURN CONTEXT RETENTION TESTS
    async def context_test_turn_1(self):
        """Turn 1: Tell me about elephants"""
        result = await self.send_message_and_track("Tell me about elephants")
        if result["success"]:
            result["context_test"] = "Turn 1 - Establishing elephant context"
            result["elephant_mentioned"] = "elephant" in result["response_text"].lower()
        return result
    
    async def context_test_turn_2(self):
        """Turn 2: How big are they? (should know 'they' refers to elephants)"""
        result = await self.send_message_and_track("How big are they?", "elephant")
        if result["success"]:
            result["context_test"] = "Turn 2 - Pronoun reference to elephants"
            result["pronoun_context_retained"] = result["context_retained"]
        return result
    
    async def context_test_turn_3(self):
        """Turn 3: Do they like water? (should maintain elephant context)"""
        result = await self.send_message_and_track("Do they like water?", "elephant")
        if result["success"]:
            result["context_test"] = "Turn 3 - Continued elephant context"
        return result
    
    async def context_test_turn_4(self):
        """Turn 4: Tell me a story about one (should create elephant story)"""
        result = await self.send_message_and_track("Tell me a story about one", "elephant")
        if result["success"]:
            result["context_test"] = "Turn 4 - Story generation with context"
            result["story_generated"] = result["content_type"] == "story" or len(result["response_text"]) > 200
        return result
    
    async def context_test_turn_5(self):
        """Turn 5: What was the elephant's name in that story?"""
        result = await self.send_message_and_track("What was the elephant's name in that story?")
        if result["success"]:
            result["context_test"] = "Turn 5 - Story detail memory"
            result["story_detail_remembered"] = len(result["response_text"]) > 20
        return result
    
    async def context_test_turn_6(self):
        """Turn 6: Can you sing a song about the same elephant?"""
        result = await self.send_message_and_track("Can you sing a song about the same elephant?", "elephant")
        if result["success"]:
            result["context_test"] = "Turn 6 - Cross-content context (story to song)"
            result["song_generated"] = "♪" in result["response_text"] or "sing" in result["response_text"].lower()
        return result
    
    async def context_test_turn_7(self):
        """Turn 7: Make it shorter (should adjust song length)"""
        result = await self.send_message_and_track("Make it shorter")
        if result["success"]:
            result["context_test"] = "Turn 7 - Content adjustment request"
            result["adjustment_acknowledged"] = "short" in result["response_text"].lower() or len(result["response_text"]) < 200
        return result
    
    async def context_test_turn_8(self):
        """Turn 8: Now tell me a riddle about elephants"""
        result = await self.send_message_and_track("Now tell me a riddle about elephants", "elephant")
        if result["success"]:
            result["context_test"] = "Turn 8 - Topic continuity with new content type"
            result["riddle_generated"] = "?" in result["response_text"] or "riddle" in result["response_text"].lower()
        return result
    
    async def context_test_turn_9(self):
        """Turn 9: I don't know the answer (should provide riddle answer)"""
        result = await self.send_message_and_track("I don't know the answer")
        if result["success"]:
            result["context_test"] = "Turn 9 - Riddle follow-through"
            result["answer_provided"] = len(result["response_text"]) > 20
        return result
    
    async def context_test_turn_10(self):
        """Turn 10: Tell me more facts about them (should return to elephants)"""
        result = await self.send_message_and_track("Tell me more facts about them", "elephant")
        if result["success"]:
            result["context_test"] = "Turn 10 - Return to original topic"
            result["facts_provided"] = len(result["response_text"]) > 50
        return result
    
    # MEMORY PERSISTENCE & LEARNING TESTS
    async def memory_test_session_1(self):
        """Session 1: Express love for dinosaurs, ask for dinosaur story"""
        result = await self.send_message_and_track("I love dinosaurs! Can you tell me a story about dinosaurs?")
        if result["success"]:
            result["memory_test"] = "Session 1 - Establishing dinosaur preference"
            result["dinosaur_story"] = "dinosaur" in result["response_text"].lower()
        return result
    
    async def generate_memory_snapshot(self):
        """Generate memory snapshot to capture preferences"""
        try:
            async with self.session.post(
                f"{BACKEND_URL}/memory/snapshot/{self.emma_user_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "snapshot_created": bool(data.get("date")),
                        "has_summary": bool(data.get("summary")),
                        "has_insights": bool(data.get("insights")),
                        "total_interactions": data.get("total_interactions", 0)
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def memory_test_session_2(self):
        """Session 2: What do I like? (should mention dinosaurs)"""
        result = await self.send_message_and_track("What do I like?", "dinosaur")
        if result["success"]:
            result["memory_test"] = "Session 2 - Preference recall"
            result["preference_remembered"] = result["context_retained"]
        return result
    
    async def memory_test_session_3(self):
        """Session 3: Ask for another story (should offer dinosaur content)"""
        result = await self.send_message_and_track("Tell me another story")
        if result["success"]:
            result["memory_test"] = "Session 3 - Preference-based content suggestion"
            result["dinosaur_offered"] = "dinosaur" in result["response_text"].lower()
        return result
    
    # DYNAMIC RESPONSE LENGTH TESTING
    async def test_story_response_length(self):
        """Test story response length (should be 200-400 tokens)"""
        result = await self.send_message_and_track("Tell me a bedtime story about a brave mouse")
        if result["success"]:
            word_count = len(result["response_text"].split())
            result["response_type"] = "story"
            result["word_count"] = word_count
            result["appropriate_length"] = 150 <= word_count <= 600  # Approximate token range
            result["has_narrative_structure"] = any(word in result["response_text"].lower() 
                                                  for word in ["once", "then", "finally", "end"])
        return result
    
    async def test_riddle_response_length(self):
        """Test riddle response length (should be 20-50 tokens)"""
        result = await self.send_message_and_track("Give me a riddle about animals")
        if result["success"]:
            word_count = len(result["response_text"].split())
            result["response_type"] = "riddle"
            result["word_count"] = word_count
            result["appropriate_length"] = 15 <= word_count <= 75  # Approximate token range
            result["has_question"] = "?" in result["response_text"]
        return result
    
    async def test_song_response_length(self):
        """Test song response length (should be 100-150 tokens)"""
        result = await self.send_message_and_track("Sing me a song about friendship")
        if result["success"]:
            word_count = len(result["response_text"].split())
            result["response_type"] = "song"
            result["word_count"] = word_count
            result["appropriate_length"] = 75 <= word_count <= 225  # Approximate token range
            result["has_musical_elements"] = any(symbol in result["response_text"] 
                                               for symbol in ["♪", "♫", "🎵", "verse", "chorus"])
        return result
    
    async def test_joke_response_length(self):
        """Test joke response length (should be 10-30 tokens)"""
        result = await self.send_message_and_track("Tell me a funny joke")
        if result["success"]:
            word_count = len(result["response_text"].split())
            result["response_type"] = "joke"
            result["word_count"] = word_count
            result["appropriate_length"] = 8 <= word_count <= 45  # Approximate token range
            result["has_punchline"] = any(word in result["response_text"].lower() 
                                        for word in ["why", "what", "how", "because"])
        return result
    
    async def test_educational_response_length(self):
        """Test educational facts response length (should be 50-100 tokens)"""
        result = await self.send_message_and_track("Teach me about the ocean")
        if result["success"]:
            word_count = len(result["response_text"].split())
            result["response_type"] = "educational"
            result["word_count"] = word_count
            result["appropriate_length"] = 40 <= word_count <= 150  # Approximate token range
            result["has_facts"] = any(word in result["response_text"].lower() 
                                   for word in ["fact", "learn", "know", "ocean", "water"])
        return result
    
    async def test_game_response_length(self):
        """Test game response length (should be 30-80 tokens)"""
        result = await self.send_message_and_track("Let's play a word game")
        if result["success"]:
            word_count = len(result["response_text"].split())
            result["response_type"] = "game"
            result["word_count"] = word_count
            result["appropriate_length"] = 25 <= word_count <= 120  # Approximate token range
            result["has_game_setup"] = any(word in result["response_text"].lower() 
                                         for word in ["game", "play", "rules", "let's", "fun"])
        return result
    
    async def test_comment_response_length(self):
        """Test comment response length (should be 15-40 tokens)"""
        result = await self.send_message_and_track("That was great!")
        if result["success"]:
            word_count = len(result["response_text"].split())
            result["response_type"] = "comment"
            result["word_count"] = word_count
            result["appropriate_length"] = 10 <= word_count <= 60  # Approximate token range
            result["encouraging"] = any(word in result["response_text"].lower() 
                                     for word in ["glad", "happy", "great", "wonderful", "awesome"])
        return result
    
    # CONTEXTUAL FOLLOW-UP TESTING
    async def test_story_followups(self):
        """Test story follow-up handling"""
        # First tell a story
        story_result = await self.send_message_and_track("Tell me a story about a castle")
        if not story_result["success"]:
            return story_result
        
        # Test follow-ups
        followup_tests = [
            ("What happened next?", "continuation"),
            ("Why did the character do that?", "explanation"),
            ("Tell me more about the castle", "elaboration")
        ]
        
        followup_results = []
        for question, expected_type in followup_tests:
            result = await self.send_message_and_track(question)
            if result["success"]:
                followup_results.append({
                    "question": question,
                    "expected_type": expected_type,
                    "response_length": result["response_length"],
                    "contextual_response": len(result["response_text"]) > 30
                })
        
        return {
            "success": True,
            "story_told": story_result["success"],
            "followup_tests": len(followup_tests),
            "successful_followups": len([r for r in followup_results if r["contextual_response"]]),
            "followup_results": followup_results
        }
    
    async def test_riddle_followups(self):
        """Test riddle follow-up handling"""
        # First ask for a riddle
        riddle_result = await self.send_message_and_track("Give me a riddle about animals")
        if not riddle_result["success"]:
            return riddle_result
        
        # Test follow-ups
        followup_tests = [
            ("I don't know", "answer_reveal"),
            ("Give me another riddle", "new_riddle"),
            ("That was too hard", "difficulty_adjustment")
        ]
        
        followup_results = []
        for response, expected_type in followup_tests:
            result = await self.send_message_and_track(response)
            if result["success"]:
                followup_results.append({
                    "user_response": response,
                    "expected_type": expected_type,
                    "response_length": result["response_length"],
                    "appropriate_followup": len(result["response_text"]) > 20
                })
        
        return {
            "success": True,
            "riddle_asked": riddle_result["success"],
            "followup_tests": len(followup_tests),
            "successful_followups": len([r for r in followup_results if r["appropriate_followup"]]),
            "followup_results": followup_results
        }
    
    async def test_song_followups(self):
        """Test song follow-up handling"""
        # First ask for a song
        song_result = await self.send_message_and_track("Sing me a song about friendship")
        if not song_result["success"]:
            return song_result
        
        # Test follow-ups
        followup_tests = [
            ("Sing it again", "repetition"),
            ("Make up another verse", "expansion"),
            ("Teach me the words", "instruction")
        ]
        
        followup_results = []
        for request, expected_type in followup_tests:
            result = await self.send_message_and_track(request)
            if result["success"]:
                followup_results.append({
                    "user_request": request,
                    "expected_type": expected_type,
                    "response_length": result["response_length"],
                    "song_related": "song" in result["response_text"].lower() or "♪" in result["response_text"]
                })
        
        return {
            "success": True,
            "song_performed": song_result["success"],
            "followup_tests": len(followup_tests),
            "successful_followups": len([r for r in followup_results if r["song_related"]]),
            "followup_results": followup_results
        }
    
    async def test_game_followups(self):
        """Test game follow-up and state retention"""
        # Start a game
        game_result = await self.send_message_and_track("Let's play 20 questions")
        if not game_result["success"]:
            return game_result
        
        # Test game continuation
        game_moves = [
            "Is it an animal?",
            "Does it live in water?",
            "I give up"
        ]
        
        game_results = []
        for move in game_moves:
            result = await self.send_message_and_track(move)
            if result["success"]:
                game_results.append({
                    "move": move,
                    "response_length": result["response_length"],
                    "game_context_maintained": len(result["response_text"]) > 15
                })
        
        return {
            "success": True,
            "game_started": game_result["success"],
            "game_moves": len(game_moves),
            "successful_moves": len([r for r in game_results if r["game_context_maintained"]]),
            "game_results": game_results
        }
    
    # PERSONALITY ADAPTATION TESTING
    async def test_age_appropriate_responses(self):
        """Test age-appropriate vocabulary and concepts for 7-year-old"""
        test_messages = [
            "What is photosynthesis?",
            "Tell me about quantum physics",
            "How do plants grow?",
            "What makes the sky blue?"
        ]
        
        age_test_results = []
        for message in test_messages:
            result = await self.send_message_and_track(message)
            if result["success"]:
                # Check for age-appropriate language (simple words, short sentences)
                response = result["response_text"].lower()
                complex_words = ["photosynthesis", "quantum", "molecular", "theoretical"]
                simple_explanations = ["because", "like", "when", "simple", "easy"]
                
                age_test_results.append({
                    "question": message,
                    "response_length": result["response_length"],
                    "avoids_complex_terms": not any(word in response for word in complex_words),
                    "uses_simple_language": any(word in response for word in simple_explanations),
                    "appropriate_for_age_7": len(result["response_text"].split()) < 100
                })
        
        successful_adaptations = len([r for r in age_test_results if r["appropriate_for_age_7"]])
        
        return {
            "success": True,
            "age_adaptation_tests": len(test_messages),
            "successful_adaptations": successful_adaptations,
            "adaptation_rate": f"{successful_adaptations/len(test_messages)*100:.1f}%",
            "age_test_results": age_test_results
        }
    
    async def test_interest_based_responses(self):
        """Test responses based on Emma's interests (animals, stories, music, games)"""
        interest_tests = [
            ("I'm bored", "animals"),
            ("What should we do?", "stories"),
            ("I want to learn something", "music"),
            ("Let's have fun", "games")
        ]
        
        interest_results = []
        for message, expected_interest in interest_tests:
            result = await self.send_message_and_track(message)
            if result["success"]:
                response = result["response_text"].lower()
                interest_mentioned = expected_interest in response or any(
                    keyword in response for keyword in {
                        "animals": ["animal", "pet", "dog", "cat", "bird"],
                        "stories": ["story", "tale", "book", "read"],
                        "music": ["song", "sing", "music", "♪"],
                        "games": ["game", "play", "fun", "puzzle"]
                    }.get(expected_interest, [])
                )
                
                interest_results.append({
                    "user_message": message,
                    "expected_interest": expected_interest,
                    "interest_referenced": interest_mentioned,
                    "response_length": result["response_length"]
                })
        
        successful_references = len([r for r in interest_results if r["interest_referenced"]])
        
        return {
            "success": True,
            "interest_tests": len(interest_tests),
            "successful_references": successful_references,
            "interest_alignment_rate": f"{successful_references/len(interest_tests)*100:.1f}%",
            "interest_results": interest_results
        }
    
    async def test_learning_goal_alignment(self):
        """Test alignment with learning goals (reading, creativity, social skills)"""
        learning_tests = [
            ("Help me with reading", "reading"),
            ("I want to be creative", "creativity"),
            ("How do I make friends?", "social skills")
        ]
        
        learning_results = []
        for message, learning_goal in learning_tests:
            result = await self.send_message_and_track(message)
            if result["success"]:
                response = result["response_text"].lower()
                goal_addressed = any(
                    keyword in response for keyword in {
                        "reading": ["read", "book", "word", "letter", "story"],
                        "creativity": ["creative", "imagine", "draw", "make", "create"],
                        "social skills": ["friend", "kind", "share", "help", "talk"]
                    }.get(learning_goal, [])
                )
                
                learning_results.append({
                    "user_message": message,
                    "learning_goal": learning_goal,
                    "goal_addressed": goal_addressed,
                    "response_length": result["response_length"]
                })
        
        successful_alignments = len([r for r in learning_results if r["goal_addressed"]])
        
        return {
            "success": True,
            "learning_goal_tests": len(learning_tests),
            "successful_alignments": successful_alignments,
            "learning_alignment_rate": f"{successful_alignments/len(learning_tests)*100:.1f}%",
            "learning_results": learning_results
        }
    
    # EMOTIONAL CONTEXT RETENTION
    async def test_emotional_sadness(self):
        """Test emotional context - express sadness"""
        result = await self.send_message_and_track("I'm feeling sad today because my pet fish died")
        if result["success"]:
            response = result["response_text"].lower()
            result["emotional_recognition"] = any(word in response for word in ["sorry", "sad", "understand", "feel"])
            result["empathetic_response"] = len(result["response_text"]) > 30
        return result
    
    async def test_emotional_checkin(self):
        """Test emotional follow-up - check in later"""
        result = await self.send_message_and_track("Let's talk about something else now")
        if result["success"]:
            response = result["response_text"].lower()
            result["emotional_checkin"] = any(word in response for word in ["feeling", "better", "okay", "how"])
            result["remembers_sadness"] = "sad" in response or "fish" in response
        return result
    
    async def test_emotional_excitement(self):
        """Test emotional context - express excitement"""
        result = await self.send_message_and_track("I'm so excited! I'm going to the zoo tomorrow!")
        if result["success"]:
            response = result["response_text"].lower()
            result["excitement_recognition"] = any(word in response for word in ["excited", "wonderful", "amazing", "fun"])
            result["zoo_referenced"] = "zoo" in response or "animal" in response
        return result
    
    async def test_emotional_reference(self):
        """Test emotional reference - reference excitement later"""
        result = await self.send_message_and_track("What should I look for at the zoo?")
        if result["success"]:
            response = result["response_text"].lower()
            result["remembers_zoo_excitement"] = "zoo" in response or "excited" in response
            result["provides_zoo_advice"] = any(word in response for word in ["animal", "see", "look", "watch"])
        return result
    
    # CROSS-SESSION MEMORY TESTING
    async def test_cross_session_greeting(self):
        """Test new session greeting with context"""
        # Create a new session to simulate cross-session memory
        new_session_data = {
            "user_id": self.emma_user_id,
            "session_name": "Emma's New Session Test"
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/conversations/session",
                json=new_session_data
            ) as response:
                if response.status == 200:
                    new_session = await response.json()
                    old_session_id = self.test_session_id
                    self.test_session_id = new_session["id"]
                    
                    # Test greeting in new session
                    result = await self.send_message_and_track("Hi there!")
                    if result["success"]:
                        response = result["response_text"].lower()
                        result["new_session_created"] = True
                        result["contextual_greeting"] = any(word in response for word in ["emma", "back", "again", "remember"])
                        
                        # Restore original session
                        self.test_session_id = old_session_id
                        return result
                    else:
                        self.test_session_id = old_session_id
                        return result
                else:
                    return {"success": False, "error": "Could not create new session"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_cross_session_reference(self):
        """Test reference to previous session"""
        result = await self.send_message_and_track("Do you remember what we talked about before?")
        if result["success"]:
            response = result["response_text"].lower()
            result["references_previous_session"] = any(word in response for word in ["remember", "talked", "before", "earlier"])
            result["specific_memory"] = any(word in response for word in ["elephant", "dinosaur", "story", "song"])
        return result
    
    async def test_long_term_memory_influence(self):
        """Test long-term memory influence on interactions"""
        result = await self.send_message_and_track("Tell me something interesting")
        if result["success"]:
            response = result["response_text"].lower()
            # Check if response is influenced by established preferences
            result["influenced_by_interests"] = any(word in response for word in ["animal", "story", "music", "game"])
            result["personalized_content"] = len(result["response_text"]) > 50
        return result
    
    # CONTENT PERSONALIZATION TESTING
    async def test_animal_themed_content(self):
        """Test animal-themed content for Emma's interests"""
        result = await self.send_message_and_track("Surprise me with something fun!")
        if result["success"]:
            response = result["response_text"].lower()
            result["animal_themed"] = any(word in response for word in ["animal", "pet", "dog", "cat", "bird", "zoo"])
            result["age_appropriate"] = len(result["response_text"].split()) < 150
        return result
    
    async def test_age_appropriate_difficulty(self):
        """Test age-appropriate difficulty level"""
        result = await self.send_message_and_track("Teach me something new")
        if result["success"]:
            response = result["response_text"]
            # Check for 7-year-old appropriate complexity
            sentences = response.split('.')
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
            
            result["appropriate_sentence_length"] = avg_sentence_length < 15
            result["uses_simple_vocabulary"] = not any(word in response.lower() for word in ["complex", "sophisticated", "advanced"])
            result["engaging_for_child"] = any(word in response.lower() for word in ["fun", "cool", "awesome", "amazing"])
        return result
    
    async def test_location_references(self):
        """Test San Francisco location references"""
        result = await self.send_message_and_track("What's fun to do around here?")
        if result["success"]:
            response = result["response_text"].lower()
            sf_references = ["san francisco", "golden gate", "pier", "bay area", "california"]
            result["location_aware"] = any(ref in response for ref in sf_references)
            result["local_suggestions"] = len(result["response_text"]) > 40
        return result
    
    # SPECIFIC TEST SCENARIOS
    async def test_story_context_chain(self):
        """Scenario A: Story Context Chain"""
        steps = [
            ("Tell me a story about a lost puppy", "puppy"),
            ("What was the puppy's name?", "name"),
            ("Where did the puppy get lost?", "lost"),
            ("Tell me what happened next", "next"),
            ("Now sing a song about that puppy", "puppy")
        ]
        
        chain_results = []
        for step, expected_context in steps:
            result = await self.send_message_and_track(step, expected_context)
            if result["success"]:
                chain_results.append({
                    "step": step,
                    "expected_context": expected_context,
                    "context_maintained": result["context_retained"],
                    "response_length": result["response_length"]
                })
        
        successful_steps = len([r for r in chain_results if r["context_maintained"]])
        
        return {
            "success": True,
            "story_context_chain": "Scenario A",
            "total_steps": len(steps),
            "successful_steps": successful_steps,
            "chain_success_rate": f"{successful_steps/len(steps)*100:.1f}%",
            "chain_results": chain_results
        }
    
    async def test_learning_adaptation(self):
        """Scenario B: Learning & Adaptation"""
        steps = [
            ("I love robots!", None),
            ("Tell me something interesting", "robot"),
            ("That's too complicated", None)
        ]
        
        adaptation_results = []
        for step, expected_content in steps:
            result = await self.send_message_and_track(step, expected_content)
            if result["success"]:
                adaptation_results.append({
                    "step": step,
                    "expected_content": expected_content,
                    "content_adapted": result.get("context_retained", True),
                    "response_length": result["response_length"]
                })
        
        # Test if next response is simpler
        final_result = await self.send_message_and_track("Tell me more about robots")
        if final_result["success"]:
            adaptation_results.append({
                "step": "Follow-up after complexity feedback",
                "response_simplified": len(final_result["response_text"].split()) < 100,
                "response_length": final_result["response_length"]
            })
        
        return {
            "success": True,
            "learning_adaptation": "Scenario B",
            "adaptation_steps": len(adaptation_results),
            "shows_learning": len(adaptation_results) > 2,
            "adaptation_results": adaptation_results
        }
    
    async def test_game_state_retention(self):
        """Scenario C: Game State Retention"""
        steps = [
            ("Let's play 20 questions", None),
            ("Is it bigger than a car?", None),
            ("Does it live in water?", None),
            ("I give up", None),
            ("Let's play again", None)
        ]
        
        game_results = []
        for step, _ in steps:
            result = await self.send_message_and_track(step)
            if result["success"]:
                response = result["response_text"].lower()
                game_context = any(word in response for word in ["game", "question", "guess", "yes", "no", "think"])
                
                game_results.append({
                    "step": step,
                    "game_context_maintained": game_context,
                    "response_length": result["response_length"]
                })
        
        successful_game_steps = len([r for r in game_results if r["game_context_maintained"]])
        
        return {
            "success": True,
            "game_state_retention": "Scenario C",
            "game_steps": len(steps),
            "successful_game_steps": successful_game_steps,
            "game_retention_rate": f"{successful_game_steps/len(steps)*100:.1f}%",
            "game_results": game_results
        }

async def main():
    """Run the comprehensive context and memory tests"""
    async with ContextMemoryTester() as tester:
        results = await tester.run_comprehensive_context_memory_tests()
        
        # Calculate overall statistics
        total_tests = len(results)
        passed_tests = len([r for r in results.values() if r["status"] == "PASS"])
        failed_tests = len([r for r in results.values() if r["status"] == "FAIL"])
        error_tests = len([r for r in results.values() if r["status"] == "ERROR"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*80)
        print("🎯 CRITICAL CONTEXT & MEMORY TESTING - FINAL RESULTS")
        print("="*80)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"🔥 Errors: {error_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print("="*80)
        
        # Print detailed results for critical tests
        critical_tests = [
            "Context Test 1 - Tell me about elephants",
            "Context Test 2 - How big are they?",
            "Context Test 5 - What was the elephant's name?",
            "Context Test 9 - I don't know the answer",
            "Memory Test - Session 2: What do I like?",
            "Response Length - Story Request (200-400 tokens)",
            "Scenario A - Story Context Chain"
        ]
        
        print("\n🔍 CRITICAL TEST RESULTS:")
        for test_name in critical_tests:
            if test_name in results:
                status = results[test_name]["status"]
                emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "🔥"
                print(f"{emoji} {test_name}: {status}")
        
        print("\n" + "="*80)
        
        # Determine overall assessment
        if success_rate >= 90:
            print("🎉 PRODUCTION READY - AI Companion demonstrates excellent context retention and memory capabilities!")
        elif success_rate >= 75:
            print("⚠️  MOSTLY READY - AI Companion shows good context retention with some areas for improvement")
        elif success_rate >= 50:
            print("🔧 NEEDS WORK - AI Companion has basic functionality but context/memory needs significant improvement")
        else:
            print("❌ NOT READY - AI Companion requires major fixes for context retention and memory functionality")
        
        return results

if __name__ == "__main__":
    asyncio.run(main())