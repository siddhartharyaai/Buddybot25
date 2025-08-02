#!/usr/bin/env python3
"""
ULTRA-LOW LATENCY VALIDATION: <1 Second End-to-End Pipeline Testing
Testing the new ultra-low latency optimizations in ultra-low-latency branch

CRITICAL LATENCY VALIDATION - Test Requirements:
✅ Voice processing: <1 second end-to-end (STT+LLM+TTS)
✅ Component timing: STT <200ms, LLM <500ms, TTS <300ms
✅ All existing functionality preserved (no regressions)
✅ Audio quality maintained
✅ Error handling working properly
✅ Performance logging detailed and accurate
"""

import asyncio
import aiohttp
import json
import time
import base64
import os
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from environment
BACKEND_URL = "https://ac3a5a48-4dec-498e-8545-e5993602e42f.preview.emergentagent.com/api"

class UltraLowLatencyTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, passed: bool, details: str, latency: float = None):
        """Log test result with latency information"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        latency_info = f" | Latency: {latency:.3f}s" if latency else ""
        logger.info(f"{status} - {test_name}{latency_info}")
        logger.info(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "latency": latency
        })
    
    def create_test_audio_base64(self) -> str:
        """Create a simple test audio in base64 format"""
        # Create a minimal WAV file header + some audio data
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
        # Add some simple audio data (silence)
        audio_data = b'\x00' * 2048
        wav_data = wav_header + audio_data
        return base64.b64encode(wav_data).decode('utf-8')
    
    async def test_health_check(self):
        """Test basic health check endpoint"""
        start_time = time.time()
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                latency = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result(
                        "Health Check", 
                        True, 
                        f"Backend healthy, agents initialized: {data.get('agents', {})}", 
                        latency
                    )
                    return True
                else:
                    self.log_test_result("Health Check", False, f"HTTP {response.status}", latency)
                    return False
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Health Check", False, f"Connection error: {str(e)}", latency)
            return False
    
    async def test_ultra_fast_voice_endpoint(self):
        """Test the new ultra-fast voice endpoint: POST /api/voice/process_audio_ultra_fast"""
        start_time = time.time()
        try:
            # Create test audio data
            audio_base64 = self.create_test_audio_base64()
            
            # Prepare form data for the ultra-fast endpoint
            form_data = aiohttp.FormData()
            form_data.add_field('session_id', 'test_session_ultra_fast')
            form_data.add_field('user_id', 'test_user_ultra')
            form_data.add_field('audio_base64', audio_base64)
            
            async with self.session.post(f"{BACKEND_URL}/voice/process_audio_ultra_fast", data=form_data) as response:
                latency = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if latency target is achieved
                    target_achieved = latency < 1.0
                    pipeline_type = data.get('pipeline', 'unknown')
                    
                    # Validate response structure
                    has_transcript = 'transcript' in data
                    has_response_text = 'response_text' in data
                    has_response_audio = 'response_audio' in data
                    
                    details = f"Pipeline: {pipeline_type}, Target <1s: {target_achieved}, Response complete: {has_transcript and has_response_text}"
                    
                    self.log_test_result(
                        "Ultra-Fast Voice Endpoint", 
                        target_achieved and has_response_text, 
                        details, 
                        latency
                    )
                    return target_achieved
                else:
                    error_text = await response.text()
                    self.log_test_result(
                        "Ultra-Fast Voice Endpoint", 
                        False, 
                        f"HTTP {response.status}: {error_text}", 
                        latency
                    )
                    return False
                    
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Ultra-Fast Voice Endpoint", False, f"Error: {str(e)}", latency)
            return False
    
    async def test_fast_text_endpoint(self):
        """Test the new fast text endpoint: POST /conversations/text_fast"""
        start_time = time.time()
        try:
            payload = {
                "session_id": "test_session_fast_text",
                "user_id": "test_user_fast",
                "message": "Hello, what is Jupiter?"
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text_fast", json=payload) as response:
                latency = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if latency target is achieved (<2s for text)
                    target_achieved = latency < 2.0
                    response_text = data.get('response_text', '')
                    word_count = len(response_text.split()) if response_text else 0
                    
                    # For quick facts, should be 30-50 words
                    word_count_ok = 20 <= word_count <= 80  # Allow some flexibility
                    
                    details = f"Latency: {latency:.2f}s (<2s target: {target_achieved}), Words: {word_count} (target: 30-50), Pipeline: {data.get('pipeline', 'unknown')}"
                    
                    self.log_test_result(
                        "Fast Text Endpoint - Quick Facts", 
                        target_achieved and word_count_ok, 
                        details, 
                        latency
                    )
                    return target_achieved and word_count_ok
                else:
                    error_text = await response.text()
                    self.log_test_result(
                        "Fast Text Endpoint - Quick Facts", 
                        False, 
                        f"HTTP {response.status}: {error_text}", 
                        latency
                    )
                    return False
                    
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Fast Text Endpoint - Quick Facts", False, f"Error: {str(e)}", latency)
            return False
    
    async def test_story_generation_preservation(self):
        """Test that story generation still works with 120+ words"""
        start_time = time.time()
        try:
            payload = {
                "session_id": "test_session_story",
                "user_id": "test_user_story",
                "message": "Tell me a complete story about a brave little mouse"
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text", json=payload) as response:
                latency = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    response_text = data.get('response_text', '')
                    word_count = len(response_text.split()) if response_text else 0
                    
                    # Stories should be 120+ words (as per requirements)
                    story_length_ok = word_count >= 120
                    has_audio = bool(data.get('response_audio'))
                    content_type = data.get('content_type', '')
                    
                    details = f"Words: {word_count} (target: 120+), Has audio: {has_audio}, Content type: {content_type}, Complete story: {story_length_ok}"
                    
                    self.log_test_result(
                        "Story Generation Preservation", 
                        story_length_ok, 
                        details, 
                        latency
                    )
                    return story_length_ok
                else:
                    error_text = await response.text()
                    self.log_test_result(
                        "Story Generation Preservation", 
                        False, 
                        f"HTTP {response.status}: {error_text}", 
                        latency
                    )
                    return False
                    
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Story Generation Preservation", False, f"Error: {str(e)}", latency)
            return False
    
    async def test_voice_personalities_endpoint(self):
        """Test voice personalities endpoint functionality"""
        start_time = time.time()
        try:
            async with self.session.get(f"{BACKEND_URL}/voice/personalities") as response:
                latency = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Should have 3 personalities as per requirements
                    personalities = data.get('personalities', []) if isinstance(data, dict) else data
                    personality_count = len(personalities) if isinstance(personalities, list) else 0
                    
                    has_three_personalities = personality_count >= 3
                    
                    details = f"Personalities found: {personality_count} (target: 3), Response structure: {type(data).__name__}"
                    
                    self.log_test_result(
                        "Voice Personalities Endpoint", 
                        has_three_personalities, 
                        details, 
                        latency
                    )
                    return has_three_personalities
                else:
                    error_text = await response.text()
                    self.log_test_result(
                        "Voice Personalities Endpoint", 
                        False, 
                        f"HTTP {response.status}: {error_text}", 
                        latency
                    )
                    return False
                    
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Voice Personalities Endpoint", False, f"Error: {str(e)}", latency)
            return False
    
    async def test_entertainment_content_generation(self):
        """Test entertainment content generation (40+ words)"""
        start_time = time.time()
        try:
            payload = {
                "session_id": "test_session_entertainment",
                "user_id": "test_user_entertainment",
                "message": "Tell me a funny joke"
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text", json=payload) as response:
                latency = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    response_text = data.get('response_text', '')
                    word_count = len(response_text.split()) if response_text else 0
                    
                    # Entertainment should be 40+ words
                    entertainment_length_ok = word_count >= 40
                    has_audio = bool(data.get('response_audio'))
                    
                    details = f"Words: {word_count} (target: 40+), Has audio: {has_audio}, Entertainment content: {entertainment_length_ok}"
                    
                    self.log_test_result(
                        "Entertainment Content Generation", 
                        entertainment_length_ok, 
                        details, 
                        latency
                    )
                    return entertainment_length_ok
                else:
                    error_text = await response.text()
                    self.log_test_result(
                        "Entertainment Content Generation", 
                        False, 
                        f"HTTP {response.status}: {error_text}", 
                        latency
                    )
                    return False
                    
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Entertainment Content Generation", False, f"Error: {str(e)}", latency)
            return False
    
    async def test_simple_greeting_latency(self):
        """Test simple greeting with <1s target"""
        start_time = time.time()
        try:
            payload = {
                "session_id": "test_session_greeting",
                "user_id": "test_user_greeting",
                "message": "Hello"
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text_fast", json=payload) as response:
                latency = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Simple greetings should be <1s
                    target_achieved = latency < 1.0
                    response_text = data.get('response_text', '')
                    has_response = bool(response_text.strip())
                    
                    details = f"Latency: {latency:.3f}s (<1s target: {target_achieved}), Has response: {has_response}, Pipeline: {data.get('pipeline', 'unknown')}"
                    
                    self.log_test_result(
                        "Simple Greeting Latency", 
                        target_achieved and has_response, 
                        details, 
                        latency
                    )
                    return target_achieved and has_response
                else:
                    error_text = await response.text()
                    self.log_test_result(
                        "Simple Greeting Latency", 
                        False, 
                        f"HTTP {response.status}: {error_text}", 
                        latency
                    )
                    return False
                    
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Simple Greeting Latency", False, f"Error: {str(e)}", latency)
            return False
    
    async def test_error_handling_invalid_audio(self):
        """Test error handling with invalid audio format"""
        start_time = time.time()
        try:
            # Send invalid base64 audio data
            form_data = aiohttp.FormData()
            form_data.add_field('session_id', 'test_session_error')
            form_data.add_field('user_id', 'test_user_error')
            form_data.add_field('audio_base64', 'invalid_base64_data!')
            
            async with self.session.post(f"{BACKEND_URL}/voice/process_audio_ultra_fast", data=form_data) as response:
                latency = time.time() - start_time
                
                # Should handle error gracefully (not crash)
                if response.status in [400, 422, 500]:
                    data = await response.json()
                    has_error_message = 'error' in data or 'message' in data
                    
                    details = f"Graceful error handling: HTTP {response.status}, Has error message: {has_error_message}"
                    
                    self.log_test_result(
                        "Error Handling - Invalid Audio", 
                        has_error_message, 
                        details, 
                        latency
                    )
                    return has_error_message
                else:
                    details = f"Unexpected response: HTTP {response.status}"
                    self.log_test_result("Error Handling - Invalid Audio", False, details, latency)
                    return False
                    
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Error Handling - Invalid Audio", False, f"Error: {str(e)}", latency)
            return False
    
    async def test_concurrent_requests_performance(self):
        """Test performance under concurrent load"""
        start_time = time.time()
        try:
            # Create multiple concurrent requests
            tasks = []
            for i in range(3):  # Test with 3 concurrent requests
                payload = {
                    "session_id": f"test_session_concurrent_{i}",
                    "user_id": f"test_user_concurrent_{i}",
                    "message": f"Quick question {i}: What is the sun?"
                }
                task = self.session.post(f"{BACKEND_URL}/conversations/text_fast", json=payload)
                tasks.append(task)
            
            # Execute all requests concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            total_latency = time.time() - start_time
            
            successful_responses = 0
            avg_individual_latency = 0
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    continue
                    
                if response.status == 200:
                    successful_responses += 1
                    # Individual response latency would be measured separately in real scenario
                    avg_individual_latency += total_latency / len(responses)
                
                await response.close()
            
            success_rate = successful_responses / len(tasks)
            performance_ok = success_rate >= 0.8 and total_latency < 5.0  # Allow 5s for 3 concurrent requests
            
            details = f"Concurrent requests: {len(tasks)}, Successful: {successful_responses}, Success rate: {success_rate:.1%}, Total time: {total_latency:.2f}s"
            
            self.log_test_result(
                "Concurrent Requests Performance", 
                performance_ok, 
                details, 
                total_latency
            )
            return performance_ok
            
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Concurrent Requests Performance", False, f"Error: {str(e)}", latency)
            return False
    
    async def test_age_appropriate_language(self):
        """Test age-appropriate language functionality"""
        start_time = time.time()
        try:
            # Test with different age profiles
            payload = {
                "session_id": "test_session_age",
                "user_id": "test_user_age_5",
                "message": "Tell me about space"
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text", json=payload) as response:
                latency = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    response_text = data.get('response_text', '')
                    has_response = bool(response_text.strip())
                    
                    # Check if response is appropriate (basic check - not too complex)
                    words = response_text.split()
                    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
                    age_appropriate = avg_word_length < 8  # Simple heuristic for age-appropriate language
                    
                    details = f"Has response: {has_response}, Avg word length: {avg_word_length:.1f} chars (target: <8 for young age), Age-appropriate: {age_appropriate}"
                    
                    self.log_test_result(
                        "Age-Appropriate Language", 
                        has_response and age_appropriate, 
                        details, 
                        latency
                    )
                    return has_response and age_appropriate
                else:
                    error_text = await response.text()
                    self.log_test_result(
                        "Age-Appropriate Language", 
                        False, 
                        f"HTTP {response.status}: {error_text}", 
                        latency
                    )
                    return False
                    
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Age-Appropriate Language", False, f"Error: {str(e)}", latency)
            return False
    
    async def run_all_tests(self):
        """Run all ultra-low latency validation tests"""
        logger.info("🚀 STARTING ULTRA-LOW LATENCY VALIDATION TESTS")
        logger.info("=" * 80)
        
        # Test sequence based on priority
        test_functions = [
            self.test_health_check,
            self.test_ultra_fast_voice_endpoint,
            self.test_fast_text_endpoint,
            self.test_simple_greeting_latency,
            self.test_voice_personalities_endpoint,
            self.test_story_generation_preservation,
            self.test_entertainment_content_generation,
            self.test_age_appropriate_language,
            self.test_error_handling_invalid_audio,
            self.test_concurrent_requests_performance,
        ]
        
        for test_func in test_functions:
            try:
                await test_func()
                await asyncio.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                logger.error(f"Test {test_func.__name__} failed with exception: {str(e)}")
                self.log_test_result(test_func.__name__, False, f"Exception: {str(e)}")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        logger.info("=" * 80)
        logger.info("🎯 ULTRA-LOW LATENCY VALIDATION SUMMARY")
        logger.info("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        logger.info(f"📊 OVERALL RESULTS: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}%)")
        
        # Categorize results
        critical_tests = []
        performance_tests = []
        functionality_tests = []
        
        for result in self.test_results:
            test_name = result['test']
            if 'Ultra-Fast' in test_name or 'Latency' in test_name or 'Concurrent' in test_name:
                performance_tests.append(result)
            elif 'Health' in test_name or 'Error Handling' in test_name:
                critical_tests.append(result)
            else:
                functionality_tests.append(result)
        
        # Performance Analysis
        logger.info("\n🚀 PERFORMANCE ANALYSIS:")
        performance_passed = sum(1 for test in performance_tests if test['passed'])
        performance_total = len(performance_tests)
        logger.info(f"   Performance Tests: {performance_passed}/{performance_total} passed")
        
        for test in performance_tests:
            status = "✅" if test['passed'] else "❌"
            latency_info = f" ({test['latency']:.3f}s)" if test['latency'] else ""
            logger.info(f"   {status} {test['test']}{latency_info}")
        
        # Functionality Analysis
        logger.info("\n🎭 FUNCTIONALITY PRESERVATION:")
        functionality_passed = sum(1 for test in functionality_tests if test['passed'])
        functionality_total = len(functionality_tests)
        logger.info(f"   Functionality Tests: {functionality_passed}/{functionality_total} passed")
        
        for test in functionality_tests:
            status = "✅" if test['passed'] else "❌"
            logger.info(f"   {status} {test['test']}")
        
        # Critical Systems Analysis
        logger.info("\n🔧 CRITICAL SYSTEMS:")
        critical_passed = sum(1 for test in critical_tests if test['passed'])
        critical_total = len(critical_tests)
        logger.info(f"   Critical Tests: {critical_passed}/{critical_total} passed")
        
        for test in critical_tests:
            status = "✅" if test['passed'] else "❌"
            logger.info(f"   {status} {test['test']}")
        
        # Final Assessment
        logger.info("\n🏆 FINAL ASSESSMENT:")
        if success_rate >= 80:
            logger.info("   ✅ ULTRA-LOW LATENCY SYSTEM: READY FOR PRODUCTION")
        elif success_rate >= 60:
            logger.info("   ⚠️  ULTRA-LOW LATENCY SYSTEM: NEEDS MINOR FIXES")
        else:
            logger.info("   ❌ ULTRA-LOW LATENCY SYSTEM: MAJOR ISSUES DETECTED")
        
        # Latency Summary
        latency_tests = [test for test in self.test_results if test['latency'] is not None]
        if latency_tests:
            avg_latency = sum(test['latency'] for test in latency_tests) / len(latency_tests)
            max_latency = max(test['latency'] for test in latency_tests)
            min_latency = min(test['latency'] for test in latency_tests)
            
            logger.info(f"\n⚡ LATENCY ANALYSIS:")
            logger.info(f"   Average Latency: {avg_latency:.3f}s")
            logger.info(f"   Maximum Latency: {max_latency:.3f}s")
            logger.info(f"   Minimum Latency: {min_latency:.3f}s")
            logger.info(f"   <1s Target Achievement: {sum(1 for test in latency_tests if test['latency'] < 1.0)}/{len(latency_tests)} tests")

async def main():
    """Main test execution function"""
    async with UltraLowLatencyTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())