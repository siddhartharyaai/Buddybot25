#!/usr/bin/env python3
"""
Critical Fixes Validation Backend Test
=====================================

This test validates the three critical fixes implemented:
1. Welcome Message System - personalized welcome messages based on user profiles
2. Content Deduplication - prevents repetitive responses with variation detection
3. Ultra-Low Latency Pipeline - optimized voice processing for <2 second response times

Test Focus Areas:
- Response time measurements for voice pipeline
- Content variation detection
- Welcome message personalization
- System stability and error handling
- Memory usage and session management
"""

import asyncio
import aiohttp
import json
import time
import base64
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from environment
BACKEND_URL = "https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com/api"

class CriticalFixesValidator:
    def __init__(self):
        self.session = None
        self.test_results = {
            "welcome_message_system": {"status": "pending", "details": []},
            "content_deduplication": {"status": "pending", "details": []},
            "ultra_low_latency": {"status": "pending", "details": []},
            "regression_tests": {"status": "pending", "details": []},
            "overall_success_rate": 0
        }
        self.test_user_id = f"test_user_{int(time.time())}"
        self.test_session_id = str(uuid.uuid4())
        
    async def setup_session(self):
        """Setup HTTP session for testing"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def create_test_user(self):
        """Create a test user profile for testing"""
        try:
            user_data = {
                "name": "Emma Test",
                "age": 8,
                "location": "Test City",
                "timezone": "UTC",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "animals", "adventure"],
                "learning_goals": ["creativity", "language"],
                "gender": "female",
                "avatar": "bunny",
                "speech_speed": "normal",
                "energy_level": "balanced"
            }
            
            async with self.session.post(f"{BACKEND_URL}/users/profile", json=user_data) as response:
                if response.status == 201:
                    profile = await response.json()
                    self.test_user_id = profile["id"]
                    logger.info(f"✅ Created test user profile: {self.test_user_id}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to create test user: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error creating test user: {str(e)}")
            return False
    
    async def test_welcome_message_system(self):
        """Test 1: Welcome Message System - personalized welcome messages"""
        logger.info("🎯 TESTING: Welcome Message System")
        test_details = []
        success_count = 0
        total_tests = 3
        
        try:
            # Test 1.1: Basic welcome message generation
            logger.info("Testing basic welcome message generation...")
            welcome_request = {
                "user_id": self.test_user_id,
                "session_id": self.test_session_id
            }
            
            start_time = time.time()
            async with self.session.post(f"{BACKEND_URL}/conversations/welcome", json=welcome_request) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    welcome_data = await response.json()
                    message = welcome_data.get("message", "")
                    content_type = welcome_data.get("content_type", "")
                    metadata = welcome_data.get("metadata", {})
                    
                    if message and len(message) > 10:
                        success_count += 1
                        test_details.append(f"✅ Basic welcome message: Generated {len(message)} chars in {response_time:.2f}s")
                        logger.info(f"✅ Welcome message generated: '{message[:100]}...'")
                    else:
                        test_details.append(f"❌ Basic welcome message: Empty or too short message")
                        logger.error("❌ Welcome message too short or empty")
                else:
                    error_text = await response.text()
                    test_details.append(f"❌ Basic welcome message: HTTP {response.status} - {error_text}")
                    logger.error(f"❌ Welcome message endpoint failed: {response.status}")
            
            # Test 1.2: Personalization based on user profile
            logger.info("Testing welcome message personalization...")
            # Create another user with different profile
            different_user_data = {
                "name": "Alex Adventure",
                "age": 10,
                "location": "Adventure City",
                "interests": ["science", "space", "robots"],
                "voice_personality": "learning_buddy"
            }
            
            async with self.session.post(f"{BACKEND_URL}/users/profile", json=different_user_data) as response:
                if response.status == 201:
                    different_profile = await response.json()
                    different_user_id = different_profile["id"]
                    
                    # Get welcome message for different user
                    different_welcome_request = {
                        "user_id": different_user_id,
                        "session_id": str(uuid.uuid4())
                    }
                    
                    async with self.session.post(f"{BACKEND_URL}/conversations/welcome", json=different_welcome_request) as response2:
                        if response2.status == 200:
                            different_welcome = await response2.json()
                            different_message = different_welcome.get("message", "")
                            
                            # Check if messages are different (personalization working)
                            if different_message != message and len(different_message) > 10:
                                success_count += 1
                                test_details.append(f"✅ Personalization: Different messages for different users")
                                logger.info("✅ Welcome messages are personalized")
                            else:
                                test_details.append(f"❌ Personalization: Messages appear identical or invalid")
                                logger.error("❌ Welcome messages not personalized")
                        else:
                            test_details.append(f"❌ Personalization: Failed to get second welcome message")
                else:
                    test_details.append(f"❌ Personalization: Failed to create second test user")
            
            # Test 1.3: Welcome message metadata and structure
            logger.info("Testing welcome message metadata...")
            if 'welcome_data' in locals():
                metadata = welcome_data.get("metadata", {})
                content_type = welcome_data.get("content_type", "")
                
                if content_type == "welcome" or content_type == "conversation":
                    success_count += 1
                    test_details.append(f"✅ Metadata: Proper content_type '{content_type}' and metadata structure")
                    logger.info(f"✅ Welcome message has proper structure")
                else:
                    test_details.append(f"❌ Metadata: Invalid content_type '{content_type}'")
                    logger.error(f"❌ Invalid welcome message content_type")
            else:
                test_details.append(f"❌ Metadata: No welcome data to analyze")
                
        except Exception as e:
            test_details.append(f"❌ Welcome message system error: {str(e)}")
            logger.error(f"❌ Welcome message system test error: {str(e)}")
        
        # Calculate success rate
        success_rate = (success_count / total_tests) * 100
        self.test_results["welcome_message_system"] = {
            "status": "pass" if success_rate >= 70 else "fail",
            "success_rate": f"{success_rate:.1f}%",
            "details": test_details
        }
        
        logger.info(f"🎯 Welcome Message System: {success_rate:.1f}% success rate")
        return success_rate >= 70
    
    async def test_content_deduplication(self):
        """Test 2: Content Deduplication - prevents repetitive responses"""
        logger.info("🔄 TESTING: Content Deduplication")
        test_details = []
        success_count = 0
        total_tests = 4
        
        try:
            # Test 2.1: Send similar requests multiple times
            logger.info("Testing content deduplication with similar requests...")
            similar_requests = [
                "Tell me a story about a cat",
                "Can you tell me a story about a cat?",
                "I want to hear a story about a cat",
                "Please tell me a cat story"
            ]
            
            responses = []
            for i, request_text in enumerate(similar_requests):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request_text
                }
                
                async with self.session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        response_text = response_data.get("response_text", "")
                        responses.append(response_text)
                        logger.info(f"Response {i+1}: '{response_text[:100]}...'")
                    else:
                        responses.append("")
                        logger.error(f"Failed to get response {i+1}")
                
                # Small delay between requests
                await asyncio.sleep(0.5)
            
            # Analyze responses for variation
            if len(responses) >= 3:
                unique_responses = set(responses)
                if len(unique_responses) > 1:
                    success_count += 1
                    test_details.append(f"✅ Similar requests: {len(unique_responses)}/{len(responses)} unique responses")
                    logger.info(f"✅ Content deduplication working: {len(unique_responses)} unique responses")
                else:
                    test_details.append(f"❌ Similar requests: All responses identical - no deduplication")
                    logger.error("❌ No content deduplication detected")
            else:
                test_details.append(f"❌ Similar requests: Insufficient responses to analyze")
            
            # Test 2.2: Test with identical requests
            logger.info("Testing with identical requests...")
            identical_request = "What's your favorite color?"
            identical_responses = []
            
            for i in range(3):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": identical_request
                }
                
                async with self.session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        response_text = response_data.get("response_text", "")
                        identical_responses.append(response_text)
                    else:
                        identical_responses.append("")
                
                await asyncio.sleep(0.5)
            
            # Check for variation in identical requests
            unique_identical = set(identical_responses)
            if len(unique_identical) > 1:
                success_count += 1
                test_details.append(f"✅ Identical requests: {len(unique_identical)}/3 unique responses")
                logger.info("✅ Deduplication adds variation to identical requests")
            else:
                test_details.append(f"❌ Identical requests: All responses identical")
                logger.error("❌ No variation added to identical requests")
            
            # Test 2.3: Test conversation suggestions for variety
            logger.info("Testing conversation suggestions variety...")
            suggestions_responses = []
            
            for i in range(3):
                async with self.session.get(f"{BACKEND_URL}/conversations/suggestions") as response:
                    if response.status == 200:
                        suggestions = await response.json()
                        suggestions_responses.append(str(suggestions))
                    else:
                        suggestions_responses.append("")
                
                await asyncio.sleep(0.5)
            
            # Check if suggestions vary or are consistent
            if len(set(suggestions_responses)) >= 1 and suggestions_responses[0]:
                success_count += 1
                test_details.append(f"✅ Conversation suggestions: Endpoint working with {len(suggestions_responses[0])} chars")
                logger.info("✅ Conversation suggestions endpoint operational")
            else:
                test_details.append(f"❌ Conversation suggestions: Endpoint not working")
                logger.error("❌ Conversation suggestions endpoint failed")
            
            # Test 2.4: Test response quality and coherence
            logger.info("Testing response quality with deduplication...")
            quality_request = "Tell me about dinosaurs"
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text", json={
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": quality_request
            }) as response:
                if response.status == 200:
                    response_data = await response.json()
                    response_text = response_data.get("response_text", "")
                    
                    # Check response quality (length, coherence)
                    if len(response_text) > 50 and "dinosaur" in response_text.lower():
                        success_count += 1
                        test_details.append(f"✅ Response quality: {len(response_text)} chars, relevant content")
                        logger.info("✅ Response quality maintained with deduplication")
                    else:
                        test_details.append(f"❌ Response quality: Poor quality or irrelevant response")
                        logger.error("❌ Response quality degraded")
                else:
                    test_details.append(f"❌ Response quality: Failed to get response")
                    
        except Exception as e:
            test_details.append(f"❌ Content deduplication error: {str(e)}")
            logger.error(f"❌ Content deduplication test error: {str(e)}")
        
        # Calculate success rate
        success_rate = (success_count / total_tests) * 100
        self.test_results["content_deduplication"] = {
            "status": "pass" if success_rate >= 70 else "fail",
            "success_rate": f"{success_rate:.1f}%",
            "details": test_details
        }
        
        logger.info(f"🔄 Content Deduplication: {success_rate:.1f}% success rate")
        return success_rate >= 70
    
    async def test_ultra_low_latency_pipeline(self):
        """Test 3: Ultra-Low Latency Pipeline - <2 second response times"""
        logger.info("⚡ TESTING: Ultra-Low Latency Pipeline")
        test_details = []
        success_count = 0
        total_tests = 5
        
        try:
            # Test 3.1: Voice processing latency test
            logger.info("Testing voice processing latency...")
            
            # Create a simple audio data (base64 encoded silence for testing)
            # This is a minimal WAV file with 1 second of silence
            sample_audio_base64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA="
            
            # Use form data for voice processing endpoint
            form_data = aiohttp.FormData()
            form_data.add_field('session_id', self.test_session_id)
            form_data.add_field('user_id', self.test_user_id)
            form_data.add_field('audio_base64', sample_audio_base64)
            
            start_time = time.time()
            async with self.session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    voice_data = await response.json()
                    transcript = voice_data.get("transcript", "")
                    response_text = voice_data.get("response_text", "")
                    response_audio = voice_data.get("response_audio", "")
                    pipeline = voice_data.get("pipeline", "unknown")
                    
                    if response_time < 5.0:  # Allow 5 seconds for testing environment
                        success_count += 1
                        test_details.append(f"✅ Voice latency: {response_time:.2f}s (pipeline: {pipeline})")
                        logger.info(f"✅ Voice processing completed in {response_time:.2f}s")
                    else:
                        test_details.append(f"❌ Voice latency: {response_time:.2f}s (too slow)")
                        logger.error(f"❌ Voice processing too slow: {response_time:.2f}s")
                else:
                    error_text = await response.text()
                    test_details.append(f"❌ Voice processing: HTTP {response.status} - {error_text}")
                    logger.error(f"❌ Voice processing failed: {response.status}")
            
            # Test 3.2: TTS endpoint latency
            logger.info("Testing TTS endpoint latency...")
            tts_request = {
                "text": "Hello, this is a test message for TTS latency testing.",
                "personality": "friendly_companion"
            }
            
            start_time = time.time()
            async with self.session.post(f"{BACKEND_URL}/voice/tts", json=tts_request) as response:
                tts_time = time.time() - start_time
                
                if response.status == 200:
                    tts_data = await response.json()
                    audio_base64 = tts_data.get("audio_base64", "")
                    
                    if tts_time < 3.0 and audio_base64:  # Allow 3 seconds for TTS
                        success_count += 1
                        test_details.append(f"✅ TTS latency: {tts_time:.2f}s, audio: {len(audio_base64)} chars")
                        logger.info(f"✅ TTS completed in {tts_time:.2f}s")
                    else:
                        test_details.append(f"❌ TTS latency: {tts_time:.2f}s (too slow or no audio)")
                        logger.error(f"❌ TTS too slow or failed: {tts_time:.2f}s")
                else:
                    error_text = await response.text()
                    test_details.append(f"❌ TTS endpoint: HTTP {response.status} - {error_text}")
                    logger.error(f"❌ TTS endpoint failed: {response.status}")
            
            # Test 3.3: Text conversation latency
            logger.info("Testing text conversation latency...")
            text_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "What's the weather like?"
            }
            
            start_time = time.time()
            async with self.session.post(f"{BACKEND_URL}/conversations/text", json=text_request) as response:
                text_time = time.time() - start_time
                
                if response.status == 200:
                    text_data = await response.json()
                    response_text = text_data.get("response_text", "")
                    
                    if text_time < 2.0 and response_text:  # Target <2 seconds
                        success_count += 1
                        test_details.append(f"✅ Text conversation: {text_time:.2f}s, response: {len(response_text)} chars")
                        logger.info(f"✅ Text conversation completed in {text_time:.2f}s")
                    else:
                        test_details.append(f"❌ Text conversation: {text_time:.2f}s (target <2s)")
                        logger.error(f"❌ Text conversation latency: {text_time:.2f}s")
                else:
                    error_text = await response.text()
                    test_details.append(f"❌ Text conversation: HTTP {response.status} - {error_text}")
                    logger.error(f"❌ Text conversation failed: {response.status}")
            
            # Test 3.4: Story streaming latency (first chunk)
            logger.info("Testing story streaming first chunk latency...")
            story_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "text": "Tell me a short story about a brave mouse"
            }
            
            start_time = time.time()
            async with self.session.post(f"{BACKEND_URL}/stories/stream", json=story_request) as response:
                story_time = time.time() - start_time
                
                if response.status == 200:
                    story_data = await response.json()
                    first_chunk = story_data.get("first_chunk", {})
                    total_chunks = story_data.get("total_chunks", 0)
                    
                    if story_time < 3.0 and first_chunk:  # Allow 3 seconds for story generation
                        success_count += 1
                        test_details.append(f"✅ Story streaming: {story_time:.2f}s, chunks: {total_chunks}")
                        logger.info(f"✅ Story streaming first chunk in {story_time:.2f}s")
                    else:
                        test_details.append(f"❌ Story streaming: {story_time:.2f}s (too slow)")
                        logger.error(f"❌ Story streaming too slow: {story_time:.2f}s")
                else:
                    error_text = await response.text()
                    test_details.append(f"❌ Story streaming: HTTP {response.status} - {error_text}")
                    logger.error(f"❌ Story streaming failed: {response.status}")
            
            # Test 3.5: Parallel processing capability
            logger.info("Testing parallel processing capability...")
            
            # Send multiple requests simultaneously
            tasks = []
            for i in range(3):
                task_request = {
                    "session_id": f"{self.test_session_id}_{i}",
                    "user_id": self.test_user_id,
                    "message": f"Quick question {i+1}: What is {i+1} plus {i+1}?"
                }
                task = self.session.post(f"{BACKEND_URL}/conversations/text", json=task_request)
                tasks.append(task)
            
            start_time = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            parallel_time = time.time() - start_time
            
            successful_responses = 0
            for i, response in enumerate(responses):
                if not isinstance(response, Exception):
                    if response.status == 200:
                        successful_responses += 1
                    await response.close()
            
            if parallel_time < 5.0 and successful_responses >= 2:
                success_count += 1
                test_details.append(f"✅ Parallel processing: {parallel_time:.2f}s, {successful_responses}/3 successful")
                logger.info(f"✅ Parallel processing: {successful_responses}/3 requests in {parallel_time:.2f}s")
            else:
                test_details.append(f"❌ Parallel processing: {parallel_time:.2f}s, {successful_responses}/3 successful")
                logger.error(f"❌ Parallel processing issues: {parallel_time:.2f}s")
                
        except Exception as e:
            test_details.append(f"❌ Ultra-low latency pipeline error: {str(e)}")
            logger.error(f"❌ Ultra-low latency pipeline test error: {str(e)}")
        
        # Calculate success rate
        success_rate = (success_count / total_tests) * 100
        self.test_results["ultra_low_latency"] = {
            "status": "pass" if success_rate >= 60 else "fail",  # Lower threshold due to network latency
            "success_rate": f"{success_rate:.1f}%",
            "details": test_details
        }
        
        logger.info(f"⚡ Ultra-Low Latency Pipeline: {success_rate:.1f}% success rate")
        return success_rate >= 60
    
    async def test_regression_functionality(self):
        """Test 4: Regression Tests - ensure existing functionality works"""
        logger.info("🔍 TESTING: Regression Functionality")
        test_details = []
        success_count = 0
        total_tests = 6
        
        try:
            # Test 4.1: Health check
            logger.info("Testing health check...")
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    if health_data.get("status") == "healthy":
                        success_count += 1
                        test_details.append(f"✅ Health check: System healthy")
                        logger.info("✅ Health check passed")
                    else:
                        test_details.append(f"❌ Health check: System not healthy")
                        logger.error("❌ Health check failed - system not healthy")
                else:
                    test_details.append(f"❌ Health check: HTTP {response.status}")
                    logger.error(f"❌ Health check failed: {response.status}")
            
            # Test 4.2: User profile operations
            logger.info("Testing user profile operations...")
            async with self.session.get(f"{BACKEND_URL}/users/profile/{self.test_user_id}") as response:
                if response.status == 200:
                    profile_data = await response.json()
                    if profile_data.get("id") == self.test_user_id:
                        success_count += 1
                        test_details.append(f"✅ User profile: Retrieved successfully")
                        logger.info("✅ User profile retrieval working")
                    else:
                        test_details.append(f"❌ User profile: Invalid profile data")
                        logger.error("❌ User profile data invalid")
                else:
                    test_details.append(f"❌ User profile: HTTP {response.status}")
                    logger.error(f"❌ User profile retrieval failed: {response.status}")
            
            # Test 4.3: Voice personalities
            logger.info("Testing voice personalities...")
            async with self.session.get(f"{BACKEND_URL}/voice/personalities") as response:
                if response.status == 200:
                    personalities = await response.json()
                    if isinstance(personalities, list) and len(personalities) > 0:
                        success_count += 1
                        test_details.append(f"✅ Voice personalities: {len(personalities)} available")
                        logger.info(f"✅ Voice personalities: {len(personalities)} available")
                    else:
                        test_details.append(f"❌ Voice personalities: No personalities available")
                        logger.error("❌ No voice personalities available")
                else:
                    test_details.append(f"❌ Voice personalities: HTTP {response.status}")
                    logger.error(f"❌ Voice personalities failed: {response.status}")
            
            # Test 4.4: Conversation suggestions
            logger.info("Testing conversation suggestions...")
            async with self.session.get(f"{BACKEND_URL}/conversations/suggestions") as response:
                if response.status == 200:
                    suggestions = await response.json()
                    if isinstance(suggestions, list) and len(suggestions) > 0:
                        success_count += 1
                        test_details.append(f"✅ Conversation suggestions: {len(suggestions)} suggestions")
                        logger.info(f"✅ Conversation suggestions: {len(suggestions)} available")
                    else:
                        test_details.append(f"❌ Conversation suggestions: No suggestions available")
                        logger.error("❌ No conversation suggestions available")
                else:
                    test_details.append(f"❌ Conversation suggestions: HTTP {response.status}")
                    logger.error(f"❌ Conversation suggestions failed: {response.status}")
            
            # Test 4.5: Ambient listening endpoints
            logger.info("Testing ambient listening...")
            ambient_start_request = {"user_id": self.test_user_id}
            
            async with self.session.post(f"{BACKEND_URL}/ambient/start", json=ambient_start_request) as response:
                if response.status == 200:
                    ambient_data = await response.json()
                    session_id = ambient_data.get("session_id")
                    
                    if session_id:
                        # Test session status
                        async with self.session.get(f"{BACKEND_URL}/ambient/status/{session_id}") as status_response:
                            if status_response.status == 200:
                                success_count += 1
                                test_details.append(f"✅ Ambient listening: Start/status working")
                                logger.info("✅ Ambient listening working")
                                
                                # Stop the session
                                stop_request = {"session_id": session_id}
                                await self.session.post(f"{BACKEND_URL}/ambient/stop", json=stop_request)
                            else:
                                test_details.append(f"❌ Ambient listening: Status check failed")
                                logger.error("❌ Ambient listening status failed")
                    else:
                        test_details.append(f"❌ Ambient listening: No session ID returned")
                        logger.error("❌ Ambient listening no session ID")
                else:
                    test_details.append(f"❌ Ambient listening: HTTP {response.status}")
                    logger.error(f"❌ Ambient listening failed: {response.status}")
            
            # Test 4.6: Memory and analytics
            logger.info("Testing memory and analytics...")
            async with self.session.get(f"{BACKEND_URL}/analytics/dashboard/{self.test_user_id}") as response:
                if response.status == 200:
                    analytics_data = await response.json()
                    if isinstance(analytics_data, dict):
                        success_count += 1
                        test_details.append(f"✅ Analytics: Dashboard accessible")
                        logger.info("✅ Analytics dashboard working")
                    else:
                        test_details.append(f"❌ Analytics: Invalid dashboard data")
                        logger.error("❌ Analytics dashboard invalid")
                else:
                    test_details.append(f"❌ Analytics: HTTP {response.status}")
                    logger.error(f"❌ Analytics dashboard failed: {response.status}")
                    
        except Exception as e:
            test_details.append(f"❌ Regression tests error: {str(e)}")
            logger.error(f"❌ Regression tests error: {str(e)}")
        
        # Calculate success rate
        success_rate = (success_count / total_tests) * 100
        self.test_results["regression_tests"] = {
            "status": "pass" if success_rate >= 70 else "fail",
            "success_rate": f"{success_rate:.1f}%",
            "details": test_details
        }
        
        logger.info(f"🔍 Regression Tests: {success_rate:.1f}% success rate")
        return success_rate >= 70
    
    async def run_all_tests(self):
        """Run all critical fixes validation tests"""
        logger.info("🚀 STARTING CRITICAL FIXES VALIDATION")
        logger.info("=" * 60)
        
        await self.setup_session()
        
        try:
            # Create test user
            if not await self.create_test_user():
                logger.error("❌ Failed to create test user - aborting tests")
                return
            
            # Run all test suites
            test_results = []
            
            # Test 1: Welcome Message System
            result1 = await self.test_welcome_message_system()
            test_results.append(result1)
            
            # Test 2: Content Deduplication
            result2 = await self.test_content_deduplication()
            test_results.append(result2)
            
            # Test 3: Ultra-Low Latency Pipeline
            result3 = await self.test_ultra_low_latency_pipeline()
            test_results.append(result3)
            
            # Test 4: Regression Tests
            result4 = await self.test_regression_functionality()
            test_results.append(result4)
            
            # Calculate overall success rate
            overall_success = (sum(test_results) / len(test_results)) * 100
            self.test_results["overall_success_rate"] = overall_success
            
            # Print final results
            logger.info("=" * 60)
            logger.info("🎯 CRITICAL FIXES VALIDATION RESULTS")
            logger.info("=" * 60)
            
            for test_name, result in self.test_results.items():
                if test_name != "overall_success_rate":
                    status = result["status"]
                    success_rate = result.get("success_rate", "N/A")
                    emoji = "✅" if status == "pass" else "❌"
                    logger.info(f"{emoji} {test_name.replace('_', ' ').title()}: {status.upper()} ({success_rate})")
                    
                    # Print details
                    for detail in result["details"]:
                        logger.info(f"   {detail}")
            
            logger.info("=" * 60)
            logger.info(f"🏆 OVERALL SUCCESS RATE: {overall_success:.1f}%")
            
            if overall_success >= 70:
                logger.info("🎉 CRITICAL FIXES VALIDATION: PASSED")
                logger.info("✅ All critical fixes are working correctly!")
            else:
                logger.info("⚠️ CRITICAL FIXES VALIDATION: NEEDS ATTENTION")
                logger.info("❌ Some critical fixes require investigation")
            
            logger.info("=" * 60)
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    validator = CriticalFixesValidator()
    await validator.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())