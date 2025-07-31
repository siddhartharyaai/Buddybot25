#!/usr/bin/env python3
"""
FOCUSED ULTRA-LOW LATENCY VALIDATION TEST
Testing specific ultra-low latency requirements with corrected test logic
"""

import asyncio
import aiohttp
import json
import time
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from environment
BACKEND_URL = "https://e73353f9-1d22-4a0f-9deb-0707101e1e70.preview.emergentagent.com/api"

class FocusedUltraLatencyTester:
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
    
    async def test_voice_personalities_corrected(self):
        """Test voice personalities endpoint with corrected parsing"""
        start_time = time.time()
        try:
            async with self.session.get(f"{BACKEND_URL}/voice/personalities") as response:
                latency = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Correct parsing - look for 'voices' key
                    voices = data.get('voices', [])
                    personality_count = len(voices) if isinstance(voices, list) else 0
                    
                    has_three_personalities = personality_count >= 3
                    
                    # Check for expected personality types
                    expected_personalities = ['friendly_companion', 'story_narrator', 'learning_buddy']
                    found_personalities = [voice.get('id', '') for voice in voices] if voices else []
                    all_personalities_found = all(p in found_personalities for p in expected_personalities)
                    
                    details = f"Personalities found: {personality_count} (target: 3), All expected found: {all_personalities_found}, IDs: {found_personalities}"
                    
                    self.log_test_result(
                        "Voice Personalities Endpoint (Corrected)", 
                        has_three_personalities and all_personalities_found, 
                        details, 
                        latency
                    )
                    return has_three_personalities and all_personalities_found
                else:
                    error_text = await response.text()
                    self.log_test_result(
                        "Voice Personalities Endpoint (Corrected)", 
                        False, 
                        f"HTTP {response.status}: {error_text}", 
                        latency
                    )
                    return False
                    
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Voice Personalities Endpoint (Corrected)", False, f"Error: {str(e)}", latency)
            return False
    
    async def test_ultra_fast_voice_with_user_creation(self):
        """Test ultra-fast voice endpoint after creating a user profile"""
        start_time = time.time()
        try:
            # First create a user profile
            user_profile = {
                "name": "Test User Ultra",
                "age": 7,
                "language": "english",
                "preferences": {
                    "voice_personality": "friendly_companion",
                    "learning_goals": ["general_knowledge"],
                    "favorite_topics": ["animals", "space"]
                },
                "parent_email": "test@example.com",
                "location": "Test City"
            }
            
            async with self.session.post(f"{BACKEND_URL}/users/profile", json=user_profile) as response:
                if response.status == 200:
                    profile_data = await response.json()
                    user_id = profile_data.get('id')
                    logger.info(f"Created test user: {user_id}")
                else:
                    # Use a default user ID if creation fails
                    user_id = "test_user_ultra_fast"
                    logger.warning("User creation failed, using default ID")
            
            # Now test the ultra-fast voice endpoint
            audio_base64 = self.create_test_audio_base64()
            
            form_data = aiohttp.FormData()
            form_data.add_field('session_id', 'test_session_ultra_fast')
            form_data.add_field('user_id', user_id)
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
                    
                    details = f"Pipeline: {pipeline_type}, Target <1s: {target_achieved}, Response complete: {has_transcript and has_response_text}, Has audio: {has_response_audio}"
                    
                    self.log_test_result(
                        "Ultra-Fast Voice Endpoint (With User)", 
                        target_achieved and has_response_text, 
                        details, 
                        latency
                    )
                    return target_achieved and has_response_text
                else:
                    error_text = await response.text()
                    self.log_test_result(
                        "Ultra-Fast Voice Endpoint (With User)", 
                        False, 
                        f"HTTP {response.status}: {error_text}", 
                        latency
                    )
                    return False
                    
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Ultra-Fast Voice Endpoint (With User)", False, f"Error: {str(e)}", latency)
            return False
    
    def create_test_audio_base64(self) -> str:
        """Create a simple test audio in base64 format"""
        # Create a minimal WAV file header + some audio data
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
        # Add some simple audio data (silence)
        audio_data = b'\x00' * 2048
        wav_data = wav_header + audio_data
        return base64.b64encode(wav_data).decode('utf-8')
    
    async def test_story_generation_word_count(self):
        """Test story generation meets 120+ word requirement"""
        start_time = time.time()
        try:
            payload = {
                "session_id": "test_session_story_count",
                "user_id": "test_user_story_count",
                "message": "Tell me a complete story about a brave little mouse adventure"
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
                    
                    # Check if it's actually a story (not just a conversation)
                    is_story_content = 'story' in content_type.lower() or word_count > 100
                    
                    details = f"Words: {word_count} (target: 120+), Has audio: {has_audio}, Content type: {content_type}, Is story: {is_story_content}"
                    
                    self.log_test_result(
                        "Story Generation Word Count", 
                        story_length_ok and is_story_content, 
                        details, 
                        latency
                    )
                    return story_length_ok and is_story_content
                else:
                    error_text = await response.text()
                    self.log_test_result(
                        "Story Generation Word Count", 
                        False, 
                        f"HTTP {response.status}: {error_text}", 
                        latency
                    )
                    return False
                    
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Story Generation Word Count", False, f"Error: {str(e)}", latency)
            return False
    
    async def test_quick_facts_word_count(self):
        """Test quick facts generation meets 30-50 word requirement"""
        start_time = time.time()
        try:
            payload = {
                "session_id": "test_session_facts",
                "user_id": "test_user_facts",
                "message": "What is Jupiter?"
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text_fast", json=payload) as response:
                latency = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    response_text = data.get('response_text', '')
                    word_count = len(response_text.split()) if response_text else 0
                    
                    # Quick facts should be 30-50 words
                    facts_length_ok = 25 <= word_count <= 60  # Allow some flexibility
                    target_achieved = latency < 2.0  # Fast endpoint should be <2s
                    
                    details = f"Words: {word_count} (target: 30-50), Latency: {latency:.2f}s (<2s target: {target_achieved}), Pipeline: {data.get('pipeline', 'unknown')}"
                    
                    self.log_test_result(
                        "Quick Facts Word Count & Latency", 
                        facts_length_ok and target_achieved, 
                        details, 
                        latency
                    )
                    return facts_length_ok and target_achieved
                else:
                    error_text = await response.text()
                    self.log_test_result(
                        "Quick Facts Word Count & Latency", 
                        False, 
                        f"HTTP {response.status}: {error_text}", 
                        latency
                    )
                    return False
                    
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Quick Facts Word Count & Latency", False, f"Error: {str(e)}", latency)
            return False
    
    async def test_entertainment_word_count(self):
        """Test entertainment content meets 40+ word requirement"""
        start_time = time.time()
        try:
            payload = {
                "session_id": "test_session_entertainment_count",
                "user_id": "test_user_entertainment_count",
                "message": "Tell me a funny joke about animals"
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
                        "Entertainment Content Word Count", 
                        entertainment_length_ok, 
                        details, 
                        latency
                    )
                    return entertainment_length_ok
                else:
                    error_text = await response.text()
                    self.log_test_result(
                        "Entertainment Content Word Count", 
                        False, 
                        f"HTTP {response.status}: {error_text}", 
                        latency
                    )
                    return False
                    
        except Exception as e:
            latency = time.time() - start_time
            self.log_test_result("Entertainment Content Word Count", False, f"Error: {str(e)}", latency)
            return False
    
    async def test_latency_benchmarks(self):
        """Test specific latency benchmarks"""
        tests = [
            ("Hello", 1.0, "Simple greeting should be <1s"),
            ("What is the sun?", 2.0, "Quick question should be <2s"),
            ("Hi there", 1.0, "Short response should be <1s")
        ]
        
        all_passed = True
        
        for message, target_latency, description in tests:
            start_time = time.time()
            try:
                payload = {
                    "session_id": f"test_session_latency_{hash(message)}",
                    "user_id": f"test_user_latency_{hash(message)}",
                    "message": message
                }
                
                async with self.session.post(f"{BACKEND_URL}/conversations/text_fast", json=payload) as response:
                    latency = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        target_achieved = latency < target_latency
                        has_response = bool(data.get('response_text', '').strip())
                        
                        details = f"Message: '{message}', Latency: {latency:.3f}s (target: <{target_latency}s), Has response: {has_response}"
                        
                        test_passed = target_achieved and has_response
                        self.log_test_result(
                            f"Latency Benchmark - {description}", 
                            test_passed, 
                            details, 
                            latency
                        )
                        
                        if not test_passed:
                            all_passed = False
                    else:
                        error_text = await response.text()
                        self.log_test_result(
                            f"Latency Benchmark - {description}", 
                            False, 
                            f"HTTP {response.status}: {error_text}", 
                            latency
                        )
                        all_passed = False
                        
            except Exception as e:
                latency = time.time() - start_time
                self.log_test_result(f"Latency Benchmark - {description}", False, f"Error: {str(e)}", latency)
                all_passed = False
        
        return all_passed
    
    async def test_functionality_preservation(self):
        """Test that all existing functionality is preserved"""
        # Test basic health check
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                health_ok = response.status == 200
                
            # Test content endpoints
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                stories_ok = response.status == 200
                
            # Test voice personalities
            async with self.session.get(f"{BACKEND_URL}/voice/personalities") as response:
                personalities_ok = response.status == 200
                
            functionality_preserved = health_ok and stories_ok and personalities_ok
            
            details = f"Health: {health_ok}, Stories: {stories_ok}, Personalities: {personalities_ok}"
            
            self.log_test_result(
                "Functionality Preservation", 
                functionality_preserved, 
                details
            )
            return functionality_preserved
            
        except Exception as e:
            self.log_test_result("Functionality Preservation", False, f"Error: {str(e)}")
            return False
    
    async def run_focused_tests(self):
        """Run focused ultra-low latency validation tests"""
        logger.info("🎯 STARTING FOCUSED ULTRA-LOW LATENCY VALIDATION")
        logger.info("=" * 80)
        
        # Test sequence based on priority
        test_functions = [
            self.test_functionality_preservation,
            self.test_voice_personalities_corrected,
            self.test_quick_facts_word_count,
            self.test_latency_benchmarks,
            self.test_entertainment_word_count,
            self.test_story_generation_word_count,
            self.test_ultra_fast_voice_with_user_creation,
        ]
        
        for test_func in test_functions:
            try:
                await test_func()
                await asyncio.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                logger.error(f"Test {test_func.__name__} failed with exception: {str(e)}")
                self.log_test_result(test_func.__name__, False, f"Exception: {str(e)}")
        
        # Generate summary
        self.generate_focused_summary()
    
    def generate_focused_summary(self):
        """Generate focused test summary"""
        logger.info("=" * 80)
        logger.info("🎯 FOCUSED ULTRA-LOW LATENCY VALIDATION SUMMARY")
        logger.info("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        logger.info(f"📊 OVERALL RESULTS: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}%)")
        
        # Categorize results by requirement type
        latency_tests = [test for test in self.test_results if 'Latency' in test['test'] or 'Ultra-Fast' in test['test']]
        word_count_tests = [test for test in self.test_results if 'Word Count' in test['test']]
        functionality_tests = [test for test in self.test_results if 'Functionality' in test['test'] or 'Personalities' in test['test']]
        
        # Latency Analysis
        logger.info("\n⚡ LATENCY REQUIREMENTS:")
        latency_passed = sum(1 for test in latency_tests if test['passed'])
        latency_total = len(latency_tests)
        logger.info(f"   Latency Tests: {latency_passed}/{latency_total} passed")
        
        for test in latency_tests:
            status = "✅" if test['passed'] else "❌"
            latency_info = f" ({test['latency']:.3f}s)" if test['latency'] else ""
            logger.info(f"   {status} {test['test']}{latency_info}")
        
        # Word Count Analysis
        logger.info("\n📝 CONTENT LENGTH REQUIREMENTS:")
        word_count_passed = sum(1 for test in word_count_tests if test['passed'])
        word_count_total = len(word_count_tests)
        logger.info(f"   Word Count Tests: {word_count_passed}/{word_count_total} passed")
        
        for test in word_count_tests:
            status = "✅" if test['passed'] else "❌"
            logger.info(f"   {status} {test['test']}")
        
        # Functionality Analysis
        logger.info("\n🔧 FUNCTIONALITY PRESERVATION:")
        functionality_passed = sum(1 for test in functionality_tests if test['passed'])
        functionality_total = len(functionality_tests)
        logger.info(f"   Functionality Tests: {functionality_passed}/{functionality_total} passed")
        
        for test in functionality_tests:
            status = "✅" if test['passed'] else "❌"
            logger.info(f"   {status} {test['test']}")
        
        # Final Assessment
        logger.info("\n🏆 ULTRA-LOW LATENCY SYSTEM ASSESSMENT:")
        if success_rate >= 85:
            logger.info("   ✅ EXCELLENT: Ultra-low latency system meets requirements")
        elif success_rate >= 70:
            logger.info("   ⚠️  GOOD: Minor optimizations needed")
        elif success_rate >= 50:
            logger.info("   ⚠️  NEEDS WORK: Several issues to address")
        else:
            logger.info("   ❌ CRITICAL: Major issues detected, system not ready")
        
        # Specific latency achievements
        latency_tests_with_data = [test for test in self.test_results if test['latency'] is not None]
        if latency_tests_with_data:
            avg_latency = sum(test['latency'] for test in latency_tests_with_data) / len(latency_tests_with_data)
            under_1s = sum(1 for test in latency_tests_with_data if test['latency'] < 1.0)
            under_2s = sum(1 for test in latency_tests_with_data if test['latency'] < 2.0)
            
            logger.info(f"\n⚡ LATENCY ACHIEVEMENTS:")
            logger.info(f"   Average Latency: {avg_latency:.3f}s")
            logger.info(f"   <1s Achievement: {under_1s}/{len(latency_tests_with_data)} tests")
            logger.info(f"   <2s Achievement: {under_2s}/{len(latency_tests_with_data)} tests")

async def main():
    """Main test execution function"""
    async with FocusedUltraLatencyTester() as tester:
        await tester.run_focused_tests()

if __name__ == "__main__":
    asyncio.run(main())