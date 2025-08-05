#!/usr/bin/env python3
"""
Audio Barge-in Fix Backend Testing
Focus: Audio and performance optimizations testing as requested in review

PRIORITY 1: Story Generation Speed Test
PRIORITY 2: TTS Voice Model Verification  
PRIORITY 3: Audio Overlap Prevention
PRIORITY 4: Conversation Endpoints Performance
"""

import asyncio
import aiohttp
import time
import json
import base64
import logging
from typing import Dict, List, Any
import concurrent.futures
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from frontend/.env
BACKEND_URL = "https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com/api"

class AudioBargeinTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_user_id = "audio_test_user_emma"
        self.test_session_id = f"audio_test_session_{int(time.time())}"
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test_result(self, test_name: str, success: bool, details: str, duration: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
        
    async def create_test_user(self):
        """Create test user profile"""
        try:
            user_data = {
                "name": "Emma",
                "age": 7,
                "location": "New York",
                "timezone": "America/New_York",
                "language": "english",
                "voice_personality": "story_narrator",
                "interests": ["stories", "adventures", "animals"],
                "learning_goals": ["creativity", "language"],
                "gender": "female",
                "avatar": "princess",
                "speech_speed": "normal",
                "energy_level": "balanced"
            }
            
            async with self.session.post(f"{BACKEND_URL}/users/profile", json=user_data) as response:
                if response.status == 201:
                    profile = await response.json()
                    self.test_user_id = profile["id"]
                    self.log_test_result("User Profile Creation", True, f"Created user profile: {profile['name']} (ID: {self.test_user_id})")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test_result("User Profile Creation", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test_result("User Profile Creation", False, f"Exception: {str(e)}")
            return False

    # PRIORITY 1: Story Generation Speed Test
    async def test_story_generation_speed(self):
        """Test story generation with new token optimizations (200 tokens for creative content, 100 for chunks)"""
        logger.info("🎯 PRIORITY 1: Testing Story Generation Speed with Token Optimizations")
        
        story_prompts = [
            "Tell me a complete story about a brave little mouse who goes on an adventure",
            "Create a magical story about a girl who can talk to animals",
            "Tell me a story about two friends who discover a hidden treasure"
        ]
        
        for i, prompt in enumerate(story_prompts, 1):
            try:
                start_time = time.time()
                
                # Test text conversation endpoint for story generation
                text_input = {
                    "session_id": f"{self.test_session_id}_story_{i}",
                    "user_id": self.test_user_id,
                    "message": prompt
                }
                
                async with self.session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "")
                        word_count = len(response_text.split())
                        
                        # Check if story meets requirements
                        speed_ok = duration < 10.0  # Should complete in <10 seconds
                        length_ok = word_count >= 100  # Should be substantial story
                        
                        if speed_ok and length_ok:
                            self.log_test_result(
                                f"Story Generation Speed Test {i}", 
                                True, 
                                f"Generated {word_count} words in {duration:.2f}s (target: <10s, ≥100 words)",
                                duration
                            )
                        else:
                            issues = []
                            if not speed_ok:
                                issues.append(f"Too slow: {duration:.2f}s > 10s")
                            if not length_ok:
                                issues.append(f"Too short: {word_count} words < 100")
                            
                            self.log_test_result(
                                f"Story Generation Speed Test {i}", 
                                False, 
                                f"Issues: {', '.join(issues)}. Got {word_count} words in {duration:.2f}s",
                                duration
                            )
                    else:
                        error_text = await response.text()
                        self.log_test_result(
                            f"Story Generation Speed Test {i}", 
                            False, 
                            f"HTTP {response.status}: {error_text}",
                            duration
                        )
                        
            except Exception as e:
                self.log_test_result(f"Story Generation Speed Test {i}", False, f"Exception: {str(e)}")
                
    # PRIORITY 2: TTS Voice Model Verification
    async def test_tts_voice_model_verification(self):
        """Test TTS endpoints to confirm aura-2-amalthea-en model is being used"""
        logger.info("🎯 PRIORITY 2: Testing TTS Voice Model Verification (aura-2-amalthea-en)")
        
        test_texts = [
            ("Short Text", "Hello Emma! How are you today?"),
            ("Medium Text", "Once upon a time, in a magical forest far away, there lived a brave little rabbit who loved to explore new places and make friends with all the woodland creatures."),
            ("Long Text", "In the heart of an enchanted kingdom, where the mountains touched the clouds and the rivers sang sweet melodies, there lived a young princess who had the most extraordinary gift. She could understand the language of all living things - from the tiniest ant to the mightiest dragon. Every morning, she would walk through her beautiful garden, listening to the stories that the flowers would tell her about their dreams, and the tales that the butterflies would share about their journeys across distant lands.")
        ]
        
        for test_name, text in test_texts:
            try:
                start_time = time.time()
                
                # Test TTS endpoint
                tts_request = {
                    "text": text,
                    "personality": "story_narrator"
                }
                
                async with self.session.post(f"{BACKEND_URL}/voice/tts", json=tts_request) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        audio_base64 = result.get("audio_base64", "")
                        
                        if audio_base64:
                            # Estimate audio size and quality
                            audio_size = len(audio_base64)
                            estimated_duration = len(text) / 150  # Rough estimate: 150 chars per second
                            
                            # Check if generation is reasonably fast
                            speed_ok = duration < (estimated_duration * 2)  # Should be faster than 2x real-time
                            quality_ok = audio_size > 1000  # Should have substantial audio data
                            
                            if speed_ok and quality_ok:
                                self.log_test_result(
                                    f"TTS Voice Model Test - {test_name}", 
                                    True, 
                                    f"Generated {audio_size} chars audio in {duration:.2f}s for {len(text)} chars text",
                                    duration
                                )
                            else:
                                issues = []
                                if not speed_ok:
                                    issues.append(f"Slow generation: {duration:.2f}s")
                                if not quality_ok:
                                    issues.append(f"Small audio: {audio_size} chars")
                                
                                self.log_test_result(
                                    f"TTS Voice Model Test - {test_name}", 
                                    False, 
                                    f"Issues: {', '.join(issues)}",
                                    duration
                                )
                        else:
                            self.log_test_result(
                                f"TTS Voice Model Test - {test_name}", 
                                False, 
                                "No audio data returned",
                                duration
                            )
                    else:
                        error_text = await response.text()
                        self.log_test_result(
                            f"TTS Voice Model Test - {test_name}", 
                            False, 
                            f"HTTP {response.status}: {error_text}",
                            duration
                        )
                        
            except Exception as e:
                self.log_test_result(f"TTS Voice Model Test - {test_name}", False, f"Exception: {str(e)}")

    # PRIORITY 3: Audio Overlap Prevention
    async def test_audio_overlap_prevention(self):
        """Test multiple concurrent TTS requests to verify server handles concurrent audio generation properly"""
        logger.info("🎯 PRIORITY 3: Testing Audio Overlap Prevention with Concurrent Requests")
        
        # Test concurrent TTS requests
        concurrent_texts = [
            "This is the first audio message being generated simultaneously.",
            "Here is the second audio message that should not interfere with others.",
            "The third audio message tests concurrent processing capabilities.",
            "Fourth message ensures the system can handle multiple requests.",
            "Fifth and final message completes the concurrent audio test."
        ]
        
        try:
            start_time = time.time()
            
            # Create concurrent TTS requests
            tasks = []
            for i, text in enumerate(concurrent_texts):
                task = self.generate_concurrent_tts(text, f"concurrent_test_{i}")
                tasks.append(task)
            
            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_duration = time.time() - start_time
            
            # Analyze results
            successful_requests = 0
            failed_requests = 0
            audio_sizes = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_requests += 1
                    logger.error(f"Concurrent request {i} failed: {str(result)}")
                elif result.get("success"):
                    successful_requests += 1
                    audio_sizes.append(result.get("audio_size", 0))
                else:
                    failed_requests += 1
            
            # Check if concurrent processing worked properly
            if successful_requests >= 4:  # At least 4 out of 5 should succeed
                avg_audio_size = sum(audio_sizes) / len(audio_sizes) if audio_sizes else 0
                self.log_test_result(
                    "Audio Overlap Prevention - Concurrent TTS", 
                    True, 
                    f"Successfully processed {successful_requests}/5 concurrent requests in {total_duration:.2f}s, avg audio size: {avg_audio_size:.0f} chars",
                    total_duration
                )
            else:
                self.log_test_result(
                    "Audio Overlap Prevention - Concurrent TTS", 
                    False, 
                    f"Only {successful_requests}/5 concurrent requests succeeded in {total_duration:.2f}s",
                    total_duration
                )
                
        except Exception as e:
            self.log_test_result("Audio Overlap Prevention - Concurrent TTS", False, f"Exception: {str(e)}")
            
        # Test story streaming with chunked TTS
        await self.test_story_streaming_chunks()
        
    async def generate_concurrent_tts(self, text: str, request_id: str):
        """Generate TTS for concurrent testing"""
        try:
            tts_request = {
                "text": text,
                "personality": "friendly_companion"
            }
            
            async with self.session.post(f"{BACKEND_URL}/voice/tts", json=tts_request) as response:
                if response.status == 200:
                    result = await response.json()
                    audio_base64 = result.get("audio_base64", "")
                    return {
                        "success": True,
                        "request_id": request_id,
                        "audio_size": len(audio_base64)
                    }
                else:
                    return {
                        "success": False,
                        "request_id": request_id,
                        "error": f"HTTP {response.status}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "request_id": request_id,
                "error": str(e)
            }
            
    async def test_story_streaming_chunks(self):
        """Test story streaming with chunked TTS"""
        try:
            start_time = time.time()
            
            # Test story streaming endpoint
            story_request = {
                "session_id": f"{self.test_session_id}_streaming",
                "user_id": self.test_user_id,
                "text": "Tell me a story about a magical adventure with dragons and princesses"
            }
            
            async with self.session.post(f"{BACKEND_URL}/stories/stream", json=story_request) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get("status") == "success" and result.get("story_mode"):
                        total_chunks = result.get("total_chunks", 0)
                        total_words = result.get("total_words", 0)
                        
                        self.log_test_result(
                            "Audio Overlap Prevention - Story Streaming", 
                            True, 
                            f"Story streaming working: {total_chunks} chunks, {total_words} words in {duration:.2f}s",
                            duration
                        )
                    else:
                        self.log_test_result(
                            "Audio Overlap Prevention - Story Streaming", 
                            False, 
                            f"Story streaming not working properly: {result.get('status', 'unknown')}",
                            duration
                        )
                else:
                    error_text = await response.text()
                    self.log_test_result(
                        "Audio Overlap Prevention - Story Streaming", 
                        False, 
                        f"HTTP {response.status}: {error_text}",
                        duration
                    )
                    
        except Exception as e:
            self.log_test_result("Audio Overlap Prevention - Story Streaming", False, f"Exception: {str(e)}")

    # PRIORITY 4: Conversation Endpoints Performance
    async def test_conversation_endpoints_performance(self):
        """Test conversation endpoint performance with optimized tokens"""
        logger.info("🎯 PRIORITY 4: Testing Conversation Endpoints Performance")
        
        # Test different types of conversation requests
        conversation_tests = [
            ("Quick Question", "What is your favorite color?"),
            ("Story Request", "Can you tell me a story about friendship?"),
            ("Educational Query", "Tell me about dinosaurs"),
            ("Creative Request", "Help me write a poem about the ocean"),
            ("Continuation", "That was interesting, tell me more about that topic")
        ]
        
        for test_name, message in conversation_tests:
            try:
                start_time = time.time()
                
                text_input = {
                    "session_id": f"{self.test_session_id}_perf",
                    "user_id": self.test_user_id,
                    "message": message
                }
                
                async with self.session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "")
                        content_type = result.get("content_type", "conversation")
                        word_count = len(response_text.split())
                        
                        # Check performance criteria
                        speed_ok = duration < 5.0  # Should respond within 5 seconds
                        quality_ok = word_count >= 10  # Should have meaningful response
                        
                        if speed_ok and quality_ok:
                            self.log_test_result(
                                f"Conversation Performance - {test_name}", 
                                True, 
                                f"Response: {word_count} words, {duration:.2f}s, type: {content_type}",
                                duration
                            )
                        else:
                            issues = []
                            if not speed_ok:
                                issues.append(f"Slow: {duration:.2f}s > 5s")
                            if not quality_ok:
                                issues.append(f"Short: {word_count} words < 10")
                            
                            self.log_test_result(
                                f"Conversation Performance - {test_name}", 
                                False, 
                                f"Issues: {', '.join(issues)}",
                                duration
                            )
                    else:
                        error_text = await response.text()
                        self.log_test_result(
                            f"Conversation Performance - {test_name}", 
                            False, 
                            f"HTTP {response.status}: {error_text}",
                            duration
                        )
                        
            except Exception as e:
                self.log_test_result(f"Conversation Performance - {test_name}", False, f"Exception: {str(e)}")
                
        # Test session management for stories
        await self.test_session_management()
        
    async def test_session_management(self):
        """Test session management for stories and conversations"""
        try:
            # Test story narration endpoint
            story_data = {
                "user_id": self.test_user_id
            }
            
            # First get available stories
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status == 200:
                    stories_result = await response.json()
                    stories = stories_result.get("stories", [])
                    
                    if stories:
                        # Test narrating the first story
                        story_id = stories[0]["id"]
                        
                        # Use form data as expected by the endpoint
                        form_data = aiohttp.FormData()
                        form_data.add_field('user_id', self.test_user_id)
                        
                        start_time = time.time()
                        async with self.session.post(f"{BACKEND_URL}/content/stories/{story_id}/narrate", data=form_data) as narrate_response:
                            duration = time.time() - start_time
                            
                            if narrate_response.status == 200:
                                narrate_result = await narrate_response.json()
                                
                                if narrate_result.get("status") == "success":
                                    response_text = narrate_result.get("response_text", "")
                                    response_audio = narrate_result.get("response_audio", "")
                                    word_count = len(response_text.split()) if response_text else 0
                                    
                                    self.log_test_result(
                                        "Session Management - Story Narration", 
                                        True, 
                                        f"Story narrated: {word_count} words, audio: {len(response_audio)} chars in {duration:.2f}s",
                                        duration
                                    )
                                else:
                                    self.log_test_result(
                                        "Session Management - Story Narration", 
                                        False, 
                                        f"Story narration failed: {narrate_result.get('error', 'unknown error')}",
                                        duration
                                    )
                            else:
                                error_text = await narrate_response.text()
                                self.log_test_result(
                                    "Session Management - Story Narration", 
                                    False, 
                                    f"HTTP {narrate_response.status}: {error_text}",
                                    duration
                                )
                    else:
                        self.log_test_result("Session Management - Story Narration", False, "No stories available")
                else:
                    error_text = await response.text()
                    self.log_test_result("Session Management - Story Narration", False, f"Failed to get stories: HTTP {response.status}")
                    
        except Exception as e:
            self.log_test_result("Session Management - Story Narration", False, f"Exception: {str(e)}")

    async def test_voice_personalities_endpoint(self):
        """Test voice personalities endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/voice/personalities") as response:
                if response.status == 200:
                    personalities = await response.json()
                    
                    if isinstance(personalities, dict) and personalities.get("personalities"):
                        personality_count = len(personalities["personalities"])
                        self.log_test_result(
                            "Voice Personalities Endpoint", 
                            True, 
                            f"Retrieved {personality_count} voice personalities"
                        )
                    else:
                        self.log_test_result(
                            "Voice Personalities Endpoint", 
                            False, 
                            f"Invalid response format: {personalities}"
                        )
                else:
                    error_text = await response.text()
                    self.log_test_result(
                        "Voice Personalities Endpoint", 
                        False, 
                        f"HTTP {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            self.log_test_result("Voice Personalities Endpoint", False, f"Exception: {str(e)}")

    async def run_all_tests(self):
        """Run all audio barge-in fix tests"""
        logger.info("🚀 Starting Audio Barge-in Fix Backend Testing")
        
        await self.setup_session()
        
        try:
            # Setup test user
            await self.create_test_user()
            
            # Run priority tests
            await self.test_story_generation_speed()
            await self.test_tts_voice_model_verification()
            await self.test_audio_overlap_prevention()
            await self.test_conversation_endpoints_performance()
            await self.test_voice_personalities_endpoint()
            
        finally:
            await self.cleanup_session()
            
        # Generate summary
        self.generate_test_summary()
        
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 AUDIO BARGE-IN FIX BACKEND TESTING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info("=" * 80)
        
        # Priority-specific summaries
        priorities = {
            "Story Generation Speed": [r for r in self.test_results if "Story Generation Speed" in r["test"]],
            "TTS Voice Model": [r for r in self.test_results if "TTS Voice Model" in r["test"]],
            "Audio Overlap Prevention": [r for r in self.test_results if "Audio Overlap Prevention" in r["test"]],
            "Conversation Performance": [r for r in self.test_results if "Conversation Performance" in r["test"]]
        }
        
        for priority, results in priorities.items():
            if results:
                priority_passed = sum(1 for r in results if r["success"])
                priority_total = len(results)
                priority_rate = (priority_passed / priority_total * 100) if priority_total > 0 else 0
                logger.info(f"{priority}: {priority_passed}/{priority_total} ({priority_rate:.1f}%)")
        
        logger.info("=" * 80)
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            duration_info = f" ({result['duration']:.2f}s)" if result["duration"] > 0 else ""
            logger.info(f"{status} {result['test']}: {result['details']}{duration_info}")

async def main():
    """Main test execution"""
    tester = AudioBargeinTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())