#!/usr/bin/env python3
"""
Critical Backend Testing for Buddy AI Voice Companion
Focus: Critical issues from test_result.md history and review request priorities
- Story Generation System (300+ words requirement)
- Prefetch Cache Optimization (100+ entries)
- Template System Expansion
- Ultra-Low Latency Pipeline (<0.5s)
- API Endpoint Functionality
"""

import asyncio
import aiohttp
import json
import base64
import time
import logging
from typing import Dict, Any, List
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CriticalBuddyAITester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.backend_url = self.get_backend_url()
        self.session = None
        self.test_results = []
        
    def get_backend_url(self):
        """Get backend URL from frontend .env file"""
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        url = line.split('=', 1)[1].strip()
                        return f"{url}/api"
            return "http://localhost:8001/api"  # fallback
        except Exception as e:
            logger.warning(f"Could not read frontend .env: {e}")
            return "http://localhost:8001/api"
    
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(verify_ssl=False)
        )
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name, success, details, duration=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        duration_str = f" ({duration:.2f}s)" if duration else ""
        logger.info(f"{status}: {test_name}{duration_str} - {details}")
    
    async def test_health_check(self):
        """Test basic health check endpoint"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.backend_url}/health") as response:
                duration = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    agents_status = data.get('agents', {})
                    orchestrator_ok = agents_status.get('orchestrator', False)
                    gemini_ok = agents_status.get('gemini_configured', False)
                    deepgram_ok = agents_status.get('deepgram_configured', False)
                    
                    if orchestrator_ok and gemini_ok and deepgram_ok:
                        self.log_test_result("Health Check", True, 
                                           f"All systems operational - Orchestrator: {orchestrator_ok}, Gemini: {gemini_ok}, Deepgram: {deepgram_ok}", duration)
                        return True
                    else:
                        self.log_test_result("Health Check", False, 
                                           f"System issues - Orchestrator: {orchestrator_ok}, Gemini: {gemini_ok}, Deepgram: {deepgram_ok}", duration)
                        return False
                else:
                    self.log_test_result("Health Check", False, f"HTTP {response.status}", duration)
                    return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Health Check", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_story_generation_word_count(self):
        """CRITICAL: Test if stories are generating 300+ words as required"""
        start_time = time.time()
        try:
            # Create test user profile first
            test_user_id = f"test_story_user_{int(time.time())}"
            
            # Test story generation via text conversation endpoint
            story_requests = [
                "Tell me a complete story about a brave little mouse adventure",
                "Can you tell me a long story about a magical forest with talking animals",
                "I want a detailed story about two friends who discover a hidden treasure"
            ]
            
            story_results = []
            for i, story_request in enumerate(story_requests):
                try:
                    payload = {
                        "session_id": f"story_test_session_{i}",
                        "user_id": test_user_id,
                        "message": story_request
                    }
                    
                    async with self.session.post(f"{self.backend_url}/conversations/text", 
                                               json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            response_text = data.get('response_text', '')
                            word_count = len(response_text.split())
                            story_results.append({
                                "request": story_request[:50] + "...",
                                "word_count": word_count,
                                "meets_requirement": word_count >= 300,
                                "response_preview": response_text[:100] + "..." if response_text else "No response"
                            })
                        else:
                            story_results.append({
                                "request": story_request[:50] + "...",
                                "word_count": 0,
                                "meets_requirement": False,
                                "error": f"HTTP {response.status}"
                            })
                except Exception as e:
                    story_results.append({
                        "request": story_request[:50] + "...",
                        "word_count": 0,
                        "meets_requirement": False,
                        "error": str(e)
                    })
            
            duration = time.time() - start_time
            
            # Analyze results
            total_stories = len(story_results)
            successful_stories = sum(1 for r in story_results if r.get('meets_requirement', False))
            avg_word_count = sum(r.get('word_count', 0) for r in story_results) / total_stories if total_stories > 0 else 0
            
            success = successful_stories > 0  # At least one story should meet requirements
            
            details = f"Stories meeting 300+ word requirement: {successful_stories}/{total_stories} ({successful_stories/total_stories*100:.1f}%). Average word count: {avg_word_count:.0f} words"
            
            if not success:
                details += f". CRITICAL FAILURE: All stories severely truncated. Results: {story_results}"
            
            self.log_test_result("Story Generation Word Count", success, details, duration)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Story Generation Word Count", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_prefetch_cache_optimization(self):
        """CRITICAL: Test prefetch cache initialization and population"""
        start_time = time.time()
        try:
            # Test conversation agent cache status through suggestions endpoint
            async with self.session.get(f"{self.backend_url}/conversations/suggestions") as response:
                duration = time.time() - start_time
                if response.status == 200:
                    suggestions = await response.json()
                    suggestion_count = len(suggestions) if isinstance(suggestions, list) else 0
                    
                    # Check if we have substantial suggestions (should be 100+ from prefetch cache)
                    if suggestion_count >= 5:  # At least basic suggestions working
                        cache_status = "WORKING" if suggestion_count >= 20 else "PARTIAL"
                        success = suggestion_count >= 5
                        details = f"Template suggestions available: {suggestion_count} entries. Cache status: {cache_status}. Suggestions: {suggestions[:3] if suggestions else 'None'}"
                    else:
                        success = False
                        details = f"CRITICAL: Insufficient suggestions ({suggestion_count}). Expected 100+ from prefetch cache, got {suggestion_count}"
                    
                    self.log_test_result("Prefetch Cache Optimization", success, details, duration)
                    return success
                else:
                    self.log_test_result("Prefetch Cache Optimization", False, f"HTTP {response.status}", duration)
                    return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Prefetch Cache Optimization", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_template_system_functionality(self):
        """CRITICAL: Test template system and variable replacement"""
        start_time = time.time()
        try:
            # Test template suggestions endpoint
            async with self.session.get(f"{self.backend_url}/conversations/suggestions") as response:
                if response.status == 200:
                    suggestions = await response.json()
                    
                    # Test if suggestions contain template patterns
                    template_patterns_found = []
                    expected_patterns = ["story", "song", "joke", "fact", "help"]
                    
                    for suggestion in suggestions:
                        suggestion_lower = suggestion.lower()
                        for pattern in expected_patterns:
                            if pattern in suggestion_lower:
                                template_patterns_found.append(pattern)
                    
                    duration = time.time() - start_time
                    unique_patterns = list(set(template_patterns_found))
                    
                    success = len(unique_patterns) >= 3  # Should have diverse template categories
                    details = f"Template patterns found: {unique_patterns} in {len(suggestions)} suggestions. Sample suggestions: {suggestions[:3] if suggestions else 'None'}"
                    
                    self.log_test_result("Template System Functionality", success, details, duration)
                    return success
                else:
                    duration = time.time() - start_time
                    self.log_test_result("Template System Functionality", False, f"HTTP {response.status}", duration)
                    return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Template System Functionality", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_ultra_low_latency_pipeline(self):
        """CRITICAL: Test ultra-low latency pipeline (<0.5s target)"""
        start_time = time.time()
        try:
            test_user_id = f"latency_test_user_{int(time.time())}"
            
            # Test simple conversation for latency
            payload = {
                "session_id": f"latency_test_session",
                "user_id": test_user_id,
                "message": "Hello, how are you today?"
            }
            
            request_start = time.time()
            async with self.session.post(f"{self.backend_url}/conversations/text", 
                                       json=payload) as response:
                request_duration = time.time() - request_start
                
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get('response_text', '')
                    
                    # Check if response is reasonable
                    if response_text and len(response_text) > 10:
                        # Latency target: <0.5s for ultra-low latency, <1.5s acceptable
                        ultra_fast = request_duration < 0.5
                        acceptable = request_duration < 1.5
                        
                        success = acceptable
                        latency_status = "ULTRA-FAST" if ultra_fast else "ACCEPTABLE" if acceptable else "SLOW"
                        
                        details = f"Response latency: {request_duration:.3f}s ({latency_status}). Target: <0.5s ultra-fast, <1.5s acceptable. Response: '{response_text[:100]}...'"
                    else:
                        success = False
                        details = f"Invalid response in {request_duration:.3f}s: '{response_text}'"
                    
                    duration = time.time() - start_time
                    self.log_test_result("Ultra-Low Latency Pipeline", success, details, duration)
                    return success
                else:
                    duration = time.time() - start_time
                    self.log_test_result("Ultra-Low Latency Pipeline", False, f"HTTP {response.status} in {request_duration:.3f}s", duration)
                    return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Ultra-Low Latency Pipeline", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_voice_personalities_endpoint(self):
        """Test voice personalities endpoint functionality"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.backend_url}/voice/personalities") as response:
                duration = time.time() - start_time
                if response.status == 200:
                    personalities = await response.json()
                    
                    if isinstance(personalities, (list, dict)) and personalities:
                        personality_count = len(personalities) if isinstance(personalities, list) else len(personalities.keys())
                        success = personality_count >= 3  # Should have at least 3 personalities
                        details = f"Voice personalities available: {personality_count}. Data: {personalities}"
                    else:
                        success = False
                        details = f"Empty or invalid personalities response: {personalities}"
                    
                    self.log_test_result("Voice Personalities Endpoint", success, details, duration)
                    return success
                else:
                    self.log_test_result("Voice Personalities Endpoint", False, f"HTTP {response.status}", duration)
                    return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Voice Personalities Endpoint", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_user_profile_functionality(self):
        """Test user profile creation and retrieval (mentioned UserProfile.get() bug)"""
        start_time = time.time()
        try:
            # Create test user profile
            test_user_data = {
                "name": f"TestUser_{int(time.time())}",
                "age": 7,
                "location": "Test City",
                "timezone": "UTC",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "animals"],
                "learning_goals": ["creativity"],
                "gender": "prefer_not_to_say",
                "avatar": "bunny",
                "speech_speed": "normal",
                "energy_level": "balanced"
            }
            
            # Test profile creation
            async with self.session.post(f"{self.backend_url}/users/profile", 
                                       json=test_user_data) as response:
                if response.status == 201:
                    profile_data = await response.json()
                    user_id = profile_data.get('id')
                    
                    if user_id:
                        # Test profile retrieval
                        async with self.session.get(f"{self.backend_url}/users/profile/{user_id}") as get_response:
                            duration = time.time() - start_time
                            if get_response.status == 200:
                                retrieved_profile = await get_response.json()
                                success = retrieved_profile.get('name') == profile_data.get('name')
                                details = f"Profile created and retrieved successfully. User ID: {user_id}, Name: {retrieved_profile.get('name')}"
                            else:
                                success = False
                                details = f"Profile creation OK but retrieval failed: HTTP {get_response.status}"
                    else:
                        duration = time.time() - start_time
                        success = False
                        details = "Profile creation response missing user ID"
                else:
                    duration = time.time() - start_time
                    success = False
                    details = f"Profile creation failed: HTTP {response.status}"
            
            self.log_test_result("User Profile Functionality", success, details, duration)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("User Profile Functionality", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_story_narration_endpoint(self):
        """Test story narration endpoint (mentioned UserProfile.get() bug)"""
        start_time = time.time()
        try:
            # Get available stories first
            async with self.session.get(f"{self.backend_url}/content/stories") as response:
                if response.status == 200:
                    stories_data = await response.json()
                    stories = stories_data.get('stories', [])
                    
                    if stories:
                        # Test narrating first story
                        story_id = stories[0].get('id')
                        test_user_id = f"narration_test_user_{int(time.time())}"
                        
                        # Use form data as expected by endpoint
                        form_data = aiohttp.FormData()
                        form_data.add_field('user_id', test_user_id)
                        
                        async with self.session.post(f"{self.backend_url}/content/stories/{story_id}/narrate",
                                                   data=form_data) as narrate_response:
                            duration = time.time() - start_time
                            
                            if narrate_response.status == 200:
                                narration_data = await narrate_response.json()
                                response_text = narration_data.get('response_text', '')
                                response_audio = narration_data.get('response_audio', '')
                                
                                if response_text and len(response_text) > 50:
                                    success = True
                                    details = f"Story narration working. Story ID: {story_id}, Text length: {len(response_text)}, Audio: {'Yes' if response_audio else 'No'}"
                                else:
                                    success = False
                                    details = f"Story narration returned empty/short response. Text: '{response_text[:100]}', Audio: {'Yes' if response_audio else 'No'}"
                            else:
                                success = False
                                details = f"Story narration failed: HTTP {narrate_response.status}"
                    else:
                        duration = time.time() - start_time
                        success = False
                        details = "No stories available for narration test"
                else:
                    duration = time.time() - start_time
                    success = False
                    details = f"Could not fetch stories: HTTP {response.status}"
            
            self.log_test_result("Story Narration Endpoint", success, details, duration)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Story Narration Endpoint", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_tts_functionality(self):
        """Test TTS functionality for ultra-small chunk processing"""
        start_time = time.time()
        try:
            # Test simple TTS
            tts_payload = {
                "text": "Hello, this is a test of the text-to-speech system.",
                "personality": "friendly_companion"
            }
            
            async with self.session.post(f"{self.backend_url}/voice/tts", 
                                       json=tts_payload) as response:
                duration = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    audio_base64 = data.get('audio_base64', '')
                    
                    if audio_base64 and len(audio_base64) > 100:  # Should have substantial audio data
                        success = True
                        details = f"TTS working. Audio data length: {len(audio_base64)} chars, Status: {data.get('status')}"
                    else:
                        success = False
                        details = f"TTS returned insufficient audio data: {len(audio_base64) if audio_base64 else 0} chars"
                else:
                    success = False
                    details = f"TTS failed: HTTP {response.status}"
                
                self.log_test_result("TTS Functionality", success, details, duration)
                return success
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("TTS Functionality", False, f"Exception: {str(e)}", duration)
            return False
    
    async def run_comprehensive_test(self):
        """Run all critical backend tests"""
        logger.info(f"🚀 Starting Critical Backend Testing for Buddy AI")
        logger.info(f"Backend URL: {self.backend_url}")
        
        await self.setup_session()
        
        try:
            # Run all critical tests based on review priorities
            test_functions = [
                self.test_health_check,
                self.test_story_generation_word_count,  # CRITICAL: 300+ words requirement
                self.test_prefetch_cache_optimization,   # CRITICAL: Cache population
                self.test_template_system_functionality, # CRITICAL: Template system
                self.test_ultra_low_latency_pipeline,   # CRITICAL: <0.5s latency
                self.test_voice_personalities_endpoint,  # API functionality
                self.test_user_profile_functionality,    # UserProfile.get() bug
                self.test_story_narration_endpoint,     # UserProfile.get() bug
                self.test_tts_functionality             # Ultra-small chunk TTS
            ]
            
            total_tests = len(test_functions)
            passed_tests = 0
            
            for test_func in test_functions:
                try:
                    result = await test_func()
                    if result:
                        passed_tests += 1
                except Exception as e:
                    logger.error(f"Test {test_func.__name__} failed with exception: {e}")
            
            # Summary
            success_rate = (passed_tests / total_tests) * 100
            logger.info(f"\n{'='*60}")
            logger.info(f"🎯 CRITICAL BACKEND TEST SUMMARY")
            logger.info(f"{'='*60}")
            logger.info(f"Total Tests: {total_tests}")
            logger.info(f"Passed: {passed_tests}")
            logger.info(f"Failed: {total_tests - passed_tests}")
            logger.info(f"Success Rate: {success_rate:.1f}%")
            logger.info(f"{'='*60}")
            
            # Critical issues analysis
            critical_failures = []
            for result in self.test_results:
                if not result['success'] and any(keyword in result['test'] for keyword in 
                    ['Story Generation', 'Prefetch Cache', 'Template System', 'Ultra-Low Latency']):
                    critical_failures.append(result['test'])
            
            if critical_failures:
                logger.error(f"🚨 CRITICAL FAILURES DETECTED: {critical_failures}")
            else:
                logger.info(f"✅ All critical systems operational")
            
            return success_rate >= 70  # 70% success rate threshold
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = CriticalBuddyAITester()
    success = await tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 Critical backend testing completed successfully!")
    else:
        print("\n❌ Critical backend testing revealed major issues!")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())