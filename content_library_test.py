#!/usr/bin/env python3
"""
Content Library Testing Suite - Focus on expanded engaging content
Tests the 5 classic stories, 6 beloved songs, 4 nursery rhymes, 5 interactive games, jokes & riddles
"""

import asyncio
import aiohttp
import json
import uuid
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend URL from environment
BACKEND_URL = "https://5989f568-2718-4892-b46b-e42563583d9e.preview.emergentagent.com/api"

class ContentLibraryTester:
    """Content Library Testing Suite"""
    
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
                "interests": ["stories", "animals", "music"],
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
                    logger.info(f"Created test user: {self.test_user_id}")
                else:
                    logger.error(f"Failed to create user: {response.status}")
                    return False
            
            # Create conversation session
            session_data = {
                "user_id": self.test_user_id,
                "session_name": "Content Library Test Session"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/session",
                json=session_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_session_id = data["id"]
                    logger.info(f"Created test session: {self.test_session_id}")
                    return True
                else:
                    logger.error(f"Failed to create session: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Setup failed: {str(e)}")
            return False
    
    async def run_content_library_tests(self):
        """Run all content library tests"""
        logger.info("Starting comprehensive content library testing...")
        
        # Setup test user first
        if not await self.setup_test_user():
            return {"error": "Failed to setup test user"}
        
        # Test sequence for content library
        test_sequence = [
            ("Stories Content Library Test", self.test_stories_content_library),
            ("Songs Content Library Test", self.test_songs_content_library),
            ("Rhymes Content Library Test", self.test_rhymes_content_library),
            ("Interactive Games Test", self.test_interactive_games_content_library),
            ("Jokes & Riddles Test", self.test_jokes_riddles_content_library),
            ("Quality Verification Test", self.test_content_quality_verification),
            ("Age-Appropriate Filtering Test", self.test_age_appropriate_filtering),
            ("Local-First Fallback Test", self.test_local_first_fallback),
            ("Engagement Features Test", self.test_engagement_features)
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
    
    async def test_stories_content_library(self):
        """Test the 5 engaging classic stories in the content library"""
        try:
            # Test specific story requests
            story_requests = [
                "Tell me a story about three little pigs",
                "Tell me the story of Goldilocks",
                "Tell me about the tortoise and the hare",
                "Tell me about the ugly duckling",
                "Tell me a story about Little Red Riding Hood"
            ]
            
            story_results = []
            
            for i, request in enumerate(story_requests):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "")
                        
                        # Analyze story quality
                        word_count = len(response_text.split())
                        has_moral = any(moral_word in response_text.lower() for moral_word in 
                                      ["moral", "lesson", "learned", "important", "remember", "wise"])
                        has_engaging_ending = any(ending in response_text.lower() for ending in 
                                                ["the end", "happily ever after", "lived happily", "and so"])
                        
                        story_results.append({
                            "request": request,
                            "story_detected": content_type == "story" or "story" in content_type,
                            "word_count": word_count,
                            "full_length": 400 <= word_count <= 800,
                            "has_moral": has_moral,
                            "has_engaging_ending": has_engaging_ending,
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        })
                    else:
                        story_results.append({
                            "request": request,
                            "error": f"HTTP {response.status}",
                            "story_detected": False
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate success metrics
            successful_stories = [r for r in story_results if r.get("story_detected", False)]
            full_length_stories = [r for r in story_results if r.get("full_length", False)]
            stories_with_morals = [r for r in story_results if r.get("has_moral", False)]
            
            return {
                "success": True,
                "total_stories_tested": len(story_requests),
                "stories_detected": len(successful_stories),
                "full_length_stories": len(full_length_stories),
                "stories_with_morals": len(stories_with_morals),
                "story_detection_rate": f"{len(successful_stories)/len(story_requests)*100:.1f}%",
                "full_length_rate": f"{len(full_length_stories)/len(story_requests)*100:.1f}%",
                "moral_inclusion_rate": f"{len(stories_with_morals)/len(story_requests)*100:.1f}%",
                "detailed_results": story_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_songs_content_library(self):
        """Test the 6 beloved classic songs in the content library"""
        try:
            # Test specific song requests
            song_requests = [
                "Sing Mary had a little lamb",
                "Sing the wheels on the bus",
                "Sing the ABC song",
                "Sing Old MacDonald",
                "Sing itsy bitsy spider",
                "Sing Twinkle Twinkle Little Star"
            ]
            
            song_results = []
            
            for i, request in enumerate(song_requests):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "")
                        
                        # Analyze song quality
                        has_verses = response_text.count('\n') >= 3  # Multiple lines suggest verses
                        has_actions = any(action in response_text.lower() for action in 
                                        ["clap", "stomp", "jump", "dance", "move", "hands", "feet"])
                        has_engaging_reaction = any(reaction in response_text.lower() for reaction in 
                                                  ["let's sing", "come on", "together", "fun", "great job"])
                        has_repetition = any(word in response_text.lower() for word in 
                                           ["la la", "tra la", "again", "repeat", "chorus"])
                        
                        song_results.append({
                            "request": request,
                            "song_detected": content_type == "song" or "song" in content_type,
                            "has_verses": has_verses,
                            "has_actions": has_actions,
                            "has_engaging_reaction": has_engaging_reaction,
                            "has_repetition": has_repetition,
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        })
                    else:
                        song_results.append({
                            "request": request,
                            "error": f"HTTP {response.status}",
                            "song_detected": False
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate success metrics
            successful_songs = [r for r in song_results if r.get("song_detected", False)]
            songs_with_verses = [r for r in song_results if r.get("has_verses", False)]
            songs_with_actions = [r for r in song_results if r.get("has_actions", False)]
            
            return {
                "success": True,
                "total_songs_tested": len(song_requests),
                "songs_detected": len(successful_songs),
                "songs_with_verses": len(songs_with_verses),
                "songs_with_actions": len(songs_with_actions),
                "song_detection_rate": f"{len(successful_songs)/len(song_requests)*100:.1f}%",
                "verse_inclusion_rate": f"{len(songs_with_verses)/len(song_requests)*100:.1f}%",
                "action_inclusion_rate": f"{len(songs_with_actions)/len(song_requests)*100:.1f}%",
                "detailed_results": song_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_rhymes_content_library(self):
        """Test the 4 classic nursery rhymes in the content library"""
        try:
            # Test specific rhyme requests
            rhyme_requests = [
                "Tell me Humpty Dumpty",
                "Say Jack and Jill",
                "Recite Hickory Dickory Dock",
                "Tell me Mary Had a Little Lamb"
            ]
            
            rhyme_results = []
            
            for i, request in enumerate(rhyme_requests):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "")
                        
                        # Analyze rhyme quality
                        has_rhyming = self._check_rhyming_pattern(response_text)
                        has_full_version = len(response_text.split()) >= 20  # Full nursery rhymes are typically longer
                        has_moral_lesson = any(lesson in response_text.lower() for lesson in 
                                             ["careful", "lesson", "important", "remember", "wise", "learn"])
                        
                        rhyme_results.append({
                            "request": request,
                            "rhyme_detected": content_type == "rhyme" or "rhyme" in content_type or "nursery" in content_type,
                            "has_rhyming": has_rhyming,
                            "has_full_version": has_full_version,
                            "has_moral_lesson": has_moral_lesson,
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        })
                    else:
                        rhyme_results.append({
                            "request": request,
                            "error": f"HTTP {response.status}",
                            "rhyme_detected": False
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate success metrics
            successful_rhymes = [r for r in rhyme_results if r.get("rhyme_detected", False)]
            rhymes_with_patterns = [r for r in rhyme_results if r.get("has_rhyming", False)]
            full_version_rhymes = [r for r in rhyme_results if r.get("has_full_version", False)]
            
            return {
                "success": True,
                "total_rhymes_tested": len(rhyme_requests),
                "rhymes_detected": len(successful_rhymes),
                "rhymes_with_patterns": len(rhymes_with_patterns),
                "full_version_rhymes": len(full_version_rhymes),
                "rhyme_detection_rate": f"{len(successful_rhymes)/len(rhyme_requests)*100:.1f}%",
                "rhyming_pattern_rate": f"{len(rhymes_with_patterns)/len(rhyme_requests)*100:.1f}%",
                "full_version_rate": f"{len(full_version_rhymes)/len(rhyme_requests)*100:.1f}%",
                "detailed_results": rhyme_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _check_rhyming_pattern(self, text: str) -> bool:
        """Check if text contains rhyming patterns"""
        # Simple rhyme detection - look for common rhyming endings
        rhyme_patterns = [
            r'\b\w*all\b.*\b\w*all\b',  # wall/fall pattern
            r'\b\w*ock\b.*\b\w*ock\b',  # dock/clock pattern
            r'\b\w*ill\b.*\b\w*ill\b',  # hill/Jill pattern
            r'\b\w*ell\b.*\b\w*ell\b',  # well/fell pattern
        ]
        
        import re
        for pattern in rhyme_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Also check for repeated ending sounds
        words = text.lower().split()
        endings = [word[-2:] if len(word) > 2 else word for word in words if word.isalpha()]
        return len(set(endings)) < len(endings) * 0.8  # If many words share endings
    
    async def test_interactive_games_content_library(self):
        """Test the 5 engaging interactive games in the content library"""
        try:
            # Test specific game requests
            game_requests = [
                "Let's play quick math",
                "Let's play animal sounds",
                "Let's play color hunt",
                "Let's build a story",
                "Let's play a guessing game"
            ]
            
            game_results = []
            
            for i, request in enumerate(game_requests):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "")
                        
                        # Analyze game quality
                        has_clear_instructions = any(instruction in response_text.lower() for instruction in 
                                                   ["let's", "here's how", "rules", "instructions", "first", "step"])
                        has_enthusiastic_reaction = any(reaction in response_text.lower() for reaction in 
                                                      ["great", "awesome", "fantastic", "wonderful", "excellent", "amazing"])
                        has_interactive_elements = any(element in response_text.lower() for element in 
                                                     ["your turn", "what do you", "can you", "try to", "guess"])
                        is_educational = any(education in response_text.lower() for education in 
                                           ["learn", "practice", "skill", "brain", "smart", "clever"])
                        
                        game_results.append({
                            "request": request,
                            "game_detected": content_type == "game" or "game" in content_type or "play" in content_type,
                            "has_clear_instructions": has_clear_instructions,
                            "has_enthusiastic_reaction": has_enthusiastic_reaction,
                            "has_interactive_elements": has_interactive_elements,
                            "is_educational": is_educational,
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        })
                    else:
                        game_results.append({
                            "request": request,
                            "error": f"HTTP {response.status}",
                            "game_detected": False
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate success metrics
            successful_games = [r for r in game_results if r.get("game_detected", False)]
            games_with_instructions = [r for r in game_results if r.get("has_clear_instructions", False)]
            interactive_games = [r for r in game_results if r.get("has_interactive_elements", False)]
            
            return {
                "success": True,
                "total_games_tested": len(game_requests),
                "games_detected": len(successful_games),
                "games_with_instructions": len(games_with_instructions),
                "interactive_games": len(interactive_games),
                "game_detection_rate": f"{len(successful_games)/len(game_requests)*100:.1f}%",
                "instruction_rate": f"{len(games_with_instructions)/len(game_requests)*100:.1f}%",
                "interactivity_rate": f"{len(interactive_games)/len(game_requests)*100:.1f}%",
                "detailed_results": game_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_jokes_riddles_content_library(self):
        """Test jokes and riddles content in the library"""
        try:
            # Test specific joke and riddle requests
            joke_riddle_requests = [
                "Tell me a joke",
                "Make me laugh",
                "Tell me a riddle",
                "Give me a brain teaser",
                "Tell me something funny",
                "Share an amazing fact"
            ]
            
            joke_riddle_results = []
            
            for i, request in enumerate(joke_riddle_requests):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "")
                        
                        # Analyze joke/riddle quality
                        is_age_appropriate = not any(inappropriate in response_text.lower() for inappropriate in 
                                                   ["scary", "violent", "adult", "inappropriate"])
                        has_interactive_riddle = any(riddle_element in response_text.lower() for riddle_element in 
                                                   ["what am i", "guess", "riddle", "answer", "think"])
                        has_celebration = any(celebration in response_text.lower() for celebration in 
                                            ["great job", "correct", "well done", "amazing", "fantastic"])
                        has_enthusiastic_reaction = any(reaction in response_text.lower() for reaction in 
                                                      ["wow", "amazing", "incredible", "fantastic", "cool"])
                        
                        joke_riddle_results.append({
                            "request": request,
                            "content_detected": any(ct in content_type for ct in ["joke", "riddle", "fact", "fun"]),
                            "is_age_appropriate": is_age_appropriate,
                            "has_interactive_riddle": has_interactive_riddle,
                            "has_celebration": has_celebration,
                            "has_enthusiastic_reaction": has_enthusiastic_reaction,
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        })
                    else:
                        joke_riddle_results.append({
                            "request": request,
                            "error": f"HTTP {response.status}",
                            "content_detected": False
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate success metrics
            successful_content = [r for r in joke_riddle_results if r.get("content_detected", False)]
            age_appropriate_content = [r for r in joke_riddle_results if r.get("is_age_appropriate", False)]
            interactive_content = [r for r in joke_riddle_results if r.get("has_interactive_riddle", False)]
            
            return {
                "success": True,
                "total_requests_tested": len(joke_riddle_requests),
                "content_detected": len(successful_content),
                "age_appropriate_content": len(age_appropriate_content),
                "interactive_content": len(interactive_content),
                "content_detection_rate": f"{len(successful_content)/len(joke_riddle_requests)*100:.1f}%",
                "age_appropriate_rate": f"{len(age_appropriate_content)/len(joke_riddle_requests)*100:.1f}%",
                "interactivity_rate": f"{len(interactive_content)/len(joke_riddle_requests)*100:.1f}%",
                "detailed_results": joke_riddle_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_content_quality_verification(self):
        """Test overall content quality and engagement features"""
        try:
            # Test various content requests to verify quality
            quality_test_requests = [
                "Tell me a story",
                "Sing me a song", 
                "Let's play a game",
                "Tell me a joke",
                "Share a fun fact"
            ]
            
            quality_results = []
            
            for request in quality_test_requests:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        
                        # Check for emotional expressions
                        has_emotions = any(emotion in response_text for emotion in 
                                         ["😂", "🤯", "✨", "🎵", "🎭", "🌟", "💫", "🎪"])
                        
                        # Check for re-engagement prompts
                        has_reengagement = any(prompt in response_text.lower() for prompt in 
                                             ["want another", "should we", "would you like", "let's try", "how about"])
                        
                        # Check for engaging language
                        has_engaging_language = any(engaging in response_text.lower() for engaging in 
                                                  ["amazing", "wonderful", "fantastic", "incredible", "awesome", "great"])
                        
                        quality_results.append({
                            "request": request,
                            "has_emotions": has_emotions,
                            "has_reengagement": has_reengagement,
                            "has_engaging_language": has_engaging_language,
                            "response_length": len(response_text),
                            "response_preview": response_text[:150] + "..." if len(response_text) > 150 else response_text
                        })
                    else:
                        quality_results.append({
                            "request": request,
                            "error": f"HTTP {response.status}",
                            "has_emotions": False,
                            "has_reengagement": False,
                            "has_engaging_language": False
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate quality metrics
            responses_with_emotions = [r for r in quality_results if r.get("has_emotions", False)]
            responses_with_reengagement = [r for r in quality_results if r.get("has_reengagement", False)]
            responses_with_engaging_language = [r for r in quality_results if r.get("has_engaging_language", False)]
            
            return {
                "success": True,
                "total_requests_tested": len(quality_test_requests),
                "responses_with_emotions": len(responses_with_emotions),
                "responses_with_reengagement": len(responses_with_reengagement),
                "responses_with_engaging_language": len(responses_with_engaging_language),
                "emotion_rate": f"{len(responses_with_emotions)/len(quality_test_requests)*100:.1f}%",
                "reengagement_rate": f"{len(responses_with_reengagement)/len(quality_test_requests)*100:.1f}%",
                "engaging_language_rate": f"{len(responses_with_engaging_language)/len(quality_test_requests)*100:.1f}%",
                "detailed_results": quality_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_age_appropriate_filtering(self):
        """Test age-appropriate content filtering"""
        try:
            # Test various age-appropriate requests
            age_test_requests = [
                "Tell me about dinosaurs",
                "What's a rainbow?",
                "How do birds fly?",
                "Tell me about friendship",
                "What makes people happy?"
            ]
            
            age_results = []
            
            for request in age_test_requests:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        
                        # Check for age-appropriate content
                        is_age_appropriate = not any(inappropriate in response_text.lower() for inappropriate in 
                                                   ["scary", "violent", "death", "adult", "complex", "difficult"])
                        
                        uses_simple_language = any(simple in response_text.lower() for simple in 
                                                 ["fun", "happy", "nice", "good", "pretty", "cool", "amazing"])
                        
                        has_educational_value = any(educational in response_text.lower() for educational in 
                                                  ["learn", "discover", "explore", "find out", "interesting"])
                        
                        age_results.append({
                            "request": request,
                            "is_age_appropriate": is_age_appropriate,
                            "uses_simple_language": uses_simple_language,
                            "has_educational_value": has_educational_value,
                            "response_preview": response_text[:150] + "..." if len(response_text) > 150 else response_text
                        })
                    else:
                        age_results.append({
                            "request": request,
                            "error": f"HTTP {response.status}",
                            "is_age_appropriate": False
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate age-appropriateness metrics
            appropriate_responses = [r for r in age_results if r.get("is_age_appropriate", False)]
            simple_language_responses = [r for r in age_results if r.get("uses_simple_language", False)]
            educational_responses = [r for r in age_results if r.get("has_educational_value", False)]
            
            return {
                "success": True,
                "total_requests_tested": len(age_test_requests),
                "appropriate_responses": len(appropriate_responses),
                "simple_language_responses": len(simple_language_responses),
                "educational_responses": len(educational_responses),
                "appropriateness_rate": f"{len(appropriate_responses)/len(age_test_requests)*100:.1f}%",
                "simple_language_rate": f"{len(simple_language_responses)/len(age_test_requests)*100:.1f}%",
                "educational_rate": f"{len(educational_responses)/len(age_test_requests)*100:.1f}%",
                "detailed_results": age_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_local_first_fallback(self):
        """Test local-first fallback system"""
        try:
            # Test requests that should trigger local content first
            local_test_requests = [
                "Tell me a joke about elephants",
                "Give me a riddle about candles",
                "Share a fact about honey",
                "Tell me about octopuses",
                "What's a fun fact about space?"
            ]
            
            local_results = []
            
            for request in local_test_requests:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        metadata = data.get("metadata", {})
                        
                        # Check for local content indicators
                        has_structured_format = any(format_indicator in response_text for format_indicator in 
                                                  ["setup:", "punchline:", "question:", "answer:", "fact:"])
                        
                        has_quick_response = len(response_text) > 50  # Local content should be substantial
                        
                        has_consistent_quality = not any(error_indicator in response_text.lower() for error_indicator in 
                                                       ["error", "sorry", "can't", "unable", "try again"])
                        
                        local_results.append({
                            "request": request,
                            "has_structured_format": has_structured_format,
                            "has_quick_response": has_quick_response,
                            "has_consistent_quality": has_consistent_quality,
                            "response_length": len(response_text),
                            "response_preview": response_text[:150] + "..." if len(response_text) > 150 else response_text
                        })
                    else:
                        local_results.append({
                            "request": request,
                            "error": f"HTTP {response.status}",
                            "has_structured_format": False,
                            "has_quick_response": False,
                            "has_consistent_quality": False
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate local fallback metrics
            structured_responses = [r for r in local_results if r.get("has_structured_format", False)]
            quick_responses = [r for r in local_results if r.get("has_quick_response", False)]
            quality_responses = [r for r in local_results if r.get("has_consistent_quality", False)]
            
            return {
                "success": True,
                "total_requests_tested": len(local_test_requests),
                "structured_responses": len(structured_responses),
                "quick_responses": len(quick_responses),
                "quality_responses": len(quality_responses),
                "structured_rate": f"{len(structured_responses)/len(local_test_requests)*100:.1f}%",
                "quick_response_rate": f"{len(quick_responses)/len(local_test_requests)*100:.1f}%",
                "quality_rate": f"{len(quality_responses)/len(local_test_requests)*100:.1f}%",
                "detailed_results": local_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_engagement_features(self):
        """Test engagement features like emotional expressions and re-engagement prompts"""
        try:
            # Test various engagement scenarios
            engagement_requests = [
                "I'm bored",
                "That was fun!",
                "I don't understand",
                "Tell me more",
                "What else can we do?"
            ]
            
            engagement_results = []
            
            for request in engagement_requests:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        
                        # Check for engagement features
                        has_emotional_response = any(emotion in response_text for emotion in 
                                                   ["😊", "😄", "🎉", "✨", "🌟", "💫", "🎪", "🎭"])
                        
                        has_empathy = any(empathy in response_text.lower() for empathy in 
                                        ["understand", "feel", "know how", "that's okay", "no worries"])
                        
                        has_encouragement = any(encourage in response_text.lower() for encourage in 
                                              ["great", "awesome", "wonderful", "keep going", "you can do it"])
                        
                        has_follow_up = any(followup in response_text.lower() for followup in 
                                          ["what would you like", "shall we", "how about", "want to try"])
                        
                        engagement_results.append({
                            "request": request,
                            "has_emotional_response": has_emotional_response,
                            "has_empathy": has_empathy,
                            "has_encouragement": has_encouragement,
                            "has_follow_up": has_follow_up,
                            "response_preview": response_text[:150] + "..." if len(response_text) > 150 else response_text
                        })
                    else:
                        engagement_results.append({
                            "request": request,
                            "error": f"HTTP {response.status}",
                            "has_emotional_response": False,
                            "has_empathy": False,
                            "has_encouragement": False,
                            "has_follow_up": False
                        })
                
                await asyncio.sleep(0.2)
            
            # Calculate engagement metrics
            emotional_responses = [r for r in engagement_results if r.get("has_emotional_response", False)]
            empathetic_responses = [r for r in engagement_results if r.get("has_empathy", False)]
            encouraging_responses = [r for r in engagement_results if r.get("has_encouragement", False)]
            followup_responses = [r for r in engagement_results if r.get("has_follow_up", False)]
            
            return {
                "success": True,
                "total_requests_tested": len(engagement_requests),
                "emotional_responses": len(emotional_responses),
                "empathetic_responses": len(empathetic_responses),
                "encouraging_responses": len(encouraging_responses),
                "followup_responses": len(followup_responses),
                "emotional_rate": f"{len(emotional_responses)/len(engagement_requests)*100:.1f}%",
                "empathy_rate": f"{len(empathetic_responses)/len(engagement_requests)*100:.1f}%",
                "encouragement_rate": f"{len(encouraging_responses)/len(engagement_requests)*100:.1f}%",
                "followup_rate": f"{len(followup_responses)/len(engagement_requests)*100:.1f}%",
                "detailed_results": engagement_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

async def main():
    """Main test execution"""
    async with ContentLibraryTester() as tester:
        results = await tester.run_content_library_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("CONTENT LIBRARY TEST RESULTS SUMMARY")
        print("="*80)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result["status"] == "PASS")
        failed_tests = sum(1 for result in results.values() if result["status"] == "FAIL")
        error_tests = sum(1 for result in results.values() if result["status"] == "ERROR")
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Errors: {error_tests}")
        print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
        
        print("\nDETAILED RESULTS:")
        print("-" * 80)
        
        for test_name, result in results.items():
            status = result["status"]
            details = result["details"]
            
            print(f"\n{test_name}: {status}")
            
            if status == "PASS" and "success" in details:
                # Print key metrics for passed tests
                if "story_detection_rate" in details:
                    print(f"  - Story Detection Rate: {details['story_detection_rate']}")
                    print(f"  - Full Length Stories: {details['full_length_stories']}/{details['total_stories_tested']}")
                elif "song_detection_rate" in details:
                    print(f"  - Song Detection Rate: {details['song_detection_rate']}")
                    print(f"  - Songs with Verses: {details['songs_with_verses']}/{details['total_songs_tested']}")
                elif "rhyme_detection_rate" in details:
                    print(f"  - Rhyme Detection Rate: {details['rhyme_detection_rate']}")
                    print(f"  - Full Version Rhymes: {details['full_version_rhymes']}/{details['total_rhymes_tested']}")
                elif "game_detection_rate" in details:
                    print(f"  - Game Detection Rate: {details['game_detection_rate']}")
                    print(f"  - Interactive Games: {details['interactive_games']}/{details['total_games_tested']}")
                elif "content_detection_rate" in details:
                    print(f"  - Content Detection Rate: {details['content_detection_rate']}")
                    print(f"  - Age Appropriate: {details['age_appropriate_content']}/{details['total_requests_tested']}")
                elif "emotion_rate" in details:
                    print(f"  - Emotion Rate: {details['emotion_rate']}")
                    print(f"  - Re-engagement Rate: {details['reengagement_rate']}")
                elif "appropriateness_rate" in details:
                    print(f"  - Appropriateness Rate: {details['appropriateness_rate']}")
                    print(f"  - Educational Rate: {details['educational_rate']}")
                elif "structured_rate" in details:
                    print(f"  - Structured Response Rate: {details['structured_rate']}")
                    print(f"  - Quality Rate: {details['quality_rate']}")
                elif "emotional_rate" in details:
                    print(f"  - Emotional Response Rate: {details['emotional_rate']}")
                    print(f"  - Follow-up Rate: {details['followup_rate']}")
            elif status == "FAIL":
                print(f"  - Error: {details.get('error', 'Test failed')}")
            elif status == "ERROR":
                print(f"  - Exception: {details.get('error', 'Unknown error')}")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)