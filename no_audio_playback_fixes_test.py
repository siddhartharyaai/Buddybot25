#!/usr/bin/env python3
"""
Comprehensive No-Audio Playback Fixes Testing
Focus: Backend Audio Return Validation, TTS Audio Generation, Audio Pipeline End-to-End, Fallback Mechanisms, No Silent Failures
"""

import asyncio
import requests
import json
import base64
import logging
import time
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NoAudioPlaybackFixesTest:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://a720410a-cd33-47aa-8dde-f4048df3b4e9.preview.emergentagent.com/api"
        self.test_user_id = "audio_test_user_001"
        self.test_session_id = "audio_test_session_001"
        self.results = []
        
    def log_test_result(self, test_name: str, success: bool, details: str, audio_size: int = 0):
        """Log test result with audio size validation"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "audio_size": audio_size,
            "timestamp": time.time()
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        audio_info = f" (Audio: {audio_size} chars)" if audio_size > 0 else " (No Audio)" if not success else ""
        logger.info(f"{status} {test_name}: {details}{audio_info}")
    
    def validate_audio_response(self, response_data: Dict[str, Any], test_name: str) -> bool:
        """Validate that response contains non-empty audio_base64"""
        try:
            # Check for audio_base64 field
            audio_base64 = response_data.get("audio_base64") or response_data.get("response_audio")
            
            if not audio_base64:
                self.log_test_result(test_name, False, "No audio_base64 field in response", 0)
                return False
            
            if len(audio_base64) == 0:
                self.log_test_result(test_name, False, "Empty audio_base64 field (size=0)", 0)
                return False
            
            # Validate it's proper base64
            try:
                base64.b64decode(audio_base64)
            except Exception as e:
                self.log_test_result(test_name, False, f"Invalid base64 audio data: {str(e)}", len(audio_base64))
                return False
            
            self.log_test_result(test_name, True, "Valid non-empty audio_base64 returned", len(audio_base64))
            return True
            
        except Exception as e:
            self.log_test_result(test_name, False, f"Audio validation error: {str(e)}", 0)
            return False
    
    def test_backend_audio_return_validation(self):
        """Test 1: Backend Audio Return Validation - voice_agent.py methods confirm audio_base64 is non-empty"""
        logger.info("🎵 TESTING: Backend Audio Return Validation")
        
        test_cases = [
            {"text": "tell me a story", "expected_content": "story"},
            {"text": "quick fact about Jupiter", "expected_content": "fact"},
            {"text": "tell me a joke", "expected_content": "joke"}
        ]
        
        passed = 0
        total = len(test_cases)
        
        for i, case in enumerate(test_cases):
            try:
                # Test TTS endpoint directly
                response = requests.post(
                    f"{self.base_url}/voice/tts",
                    json={
                        "text": case["text"],
                        "personality": "friendly_companion"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if self.validate_audio_response(data, f"TTS Direct - {case['expected_content']}"):
                        passed += 1
                        
                        # Check for fallback logging indicators
                        if "Test audio response" in data.get("text", ""):
                            logger.warning(f"🎵 Empty TTS fallback detected for: {case['text']}")
                else:
                    self.log_test_result(f"TTS Direct - {case['expected_content']}", False, 
                                       f"HTTP {response.status_code}: {response.text}", 0)
                    
            except Exception as e:
                self.log_test_result(f"TTS Direct - {case['expected_content']}", False, 
                                   f"Request error: {str(e)}", 0)
        
        logger.info(f"🎵 Backend Audio Return Validation: {passed}/{total} tests passed")
        return passed == total
    
    def test_tts_audio_generation_validation(self):
        """Test 2: TTS Audio Generation Validation - various content types ensure audio generation"""
        logger.info("🎵 TESTING: TTS Audio Generation Validation")
        
        test_cases = [
            {"text": "tell me a story about a brave little mouse", "type": "story"},
            {"text": "quick fact about Jupiter", "type": "fact"},
            {"text": "tell me a joke", "type": "joke"},
            {"text": "Hello there!", "type": "greeting"},
            {"text": "What is 2 plus 2?", "type": "question"}
        ]
        
        passed = 0
        total = len(test_cases)
        
        for case in test_cases:
            try:
                # Test text conversation endpoint (should include audio)
                response = requests.post(
                    f"{self.base_url}/conversations/text",
                    json={
                        "session_id": self.test_session_id,
                        "user_id": self.test_user_id,
                        "message": case["text"]
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if self.validate_audio_response(data, f"Text Conversation - {case['type']}"):
                        passed += 1
                        
                        # Verify blob size is >0
                        audio_size = len(data.get("response_audio", ""))
                        if audio_size == 0:
                            logger.warning(f"🎵 Zero-size audio blob for {case['type']}")
                else:
                    self.log_test_result(f"Text Conversation - {case['type']}", False, 
                                       f"HTTP {response.status_code}: {response.text}", 0)
                    
            except Exception as e:
                self.log_test_result(f"Text Conversation - {case['type']}", False, 
                                   f"Request error: {str(e)}", 0)
        
        logger.info(f"🎵 TTS Audio Generation Validation: {passed}/{total} tests passed")
        return passed == total
    
    def test_audio_pipeline_end_to_end(self):
        """Test 3: Audio Pipeline End-to-End - all audio endpoints return non-empty response_audio"""
        logger.info("🎵 TESTING: Audio Pipeline End-to-End")
        
        endpoints_to_test = [
            {
                "name": "Voice TTS Endpoint",
                "url": f"{self.base_url}/voice/tts",
                "method": "POST",
                "data": {"text": "Hello world", "personality": "friendly_companion"},
                "audio_field": "audio_base64"
            },
            {
                "name": "Text Conversation Endpoint", 
                "url": f"{self.base_url}/conversations/text",
                "method": "POST",
                "data": {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": "Hello there"
                },
                "audio_field": "response_audio"
            }
        ]
        
        passed = 0
        total = len(endpoints_to_test)
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.request(
                    endpoint["method"],
                    endpoint["url"],
                    json=endpoint["data"],
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    audio_data = data.get(endpoint["audio_field"])
                    
                    if audio_data and len(audio_data) > 0:
                        self.log_test_result(endpoint["name"], True, 
                                           "Non-empty audio returned", len(audio_data))
                        passed += 1
                    else:
                        self.log_test_result(endpoint["name"], False, 
                                           f"Empty or missing {endpoint['audio_field']} field", 0)
                else:
                    self.log_test_result(endpoint["name"], False, 
                                       f"HTTP {response.status_code}: {response.text}", 0)
                    
            except Exception as e:
                self.log_test_result(endpoint["name"], False, 
                                   f"Request error: {str(e)}", 0)
        
        logger.info(f"🎵 Audio Pipeline End-to-End: {passed}/{total} tests passed")
        return passed == total
    
    def test_fallback_mechanism_testing(self):
        """Test 4: Fallback Mechanism Testing - empty inputs and invalid parameters trigger fallbacks"""
        logger.info("🎵 TESTING: Fallback Mechanism Testing")
        
        test_cases = [
            {
                "name": "Empty Text Input",
                "url": f"{self.base_url}/voice/tts",
                "data": {"text": "", "personality": "friendly_companion"},
                "should_have_fallback": True
            },
            {
                "name": "Invalid Personality",
                "url": f"{self.base_url}/voice/tts", 
                "data": {"text": "Hello", "personality": "invalid_personality"},
                "should_have_fallback": True
            },
            {
                "name": "Missing Text Field",
                "url": f"{self.base_url}/voice/tts",
                "data": {"personality": "friendly_companion"},
                "should_have_fallback": True
            }
        ]
        
        passed = 0
        total = len(test_cases)
        
        for case in test_cases:
            try:
                response = requests.post(
                    case["url"],
                    json=case["data"],
                    timeout=30
                )
                
                # For fallback tests, we expect either:
                # 1. HTTP 400 with proper error handling, OR
                # 2. HTTP 200 with fallback audio (like "Test audio response")
                
                if response.status_code == 400:
                    # Proper error handling
                    self.log_test_result(case["name"], True, 
                                       "Proper error handling for invalid input", 0)
                    passed += 1
                elif response.status_code == 200:
                    data = response.json()
                    audio_data = data.get("audio_base64")
                    
                    if audio_data and len(audio_data) > 0:
                        # Check if it's a fallback response
                        text_content = data.get("text", "")
                        if "Test audio" in text_content or "fallback" in text_content.lower():
                            self.log_test_result(case["name"], True, 
                                               "Fallback audio generated", len(audio_data))
                            logger.info(f"🎵 SIMPLE TEST AUDIO detected for: {case['name']}")
                        else:
                            self.log_test_result(case["name"], True, 
                                               "Audio generated for edge case", len(audio_data))
                        passed += 1
                    else:
                        self.log_test_result(case["name"], False, 
                                           "No fallback audio generated", 0)
                else:
                    self.log_test_result(case["name"], False, 
                                       f"Unexpected HTTP {response.status_code}", 0)
                    
            except Exception as e:
                self.log_test_result(case["name"], False, 
                                   f"Request error: {str(e)}", 0)
        
        logger.info(f"🎵 Fallback Mechanism Testing: {passed}/{total} tests passed")
        return passed == total
    
    def test_no_silent_failures(self):
        """Test 5: No Silent Failures - ensure no API calls return success with empty audio"""
        logger.info("🎵 TESTING: No Silent Failures")
        
        test_cases = [
            {
                "name": "Story Request",
                "endpoint": f"{self.base_url}/conversations/text",
                "data": {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": "tell me a story about friendship"
                }
            },
            {
                "name": "Fact Request", 
                "endpoint": f"{self.base_url}/conversations/text",
                "data": {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": "tell me a fact about space"
                }
            },
            {
                "name": "Direct TTS",
                "endpoint": f"{self.base_url}/voice/tts",
                "data": {
                    "text": "This is a test message",
                    "personality": "friendly_companion"
                }
            }
        ]
        
        passed = 0
        total = len(test_cases)
        
        for case in test_cases:
            try:
                response = requests.post(
                    case["endpoint"],
                    json=case["data"],
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for silent failure (HTTP 200 but empty audio)
                    audio_field = "response_audio" if "conversations" in case["endpoint"] else "audio_base64"
                    audio_data = data.get(audio_field)
                    
                    if not audio_data or len(audio_data) == 0:
                        self.log_test_result(case["name"], False, 
                                           f"SILENT FAILURE: HTTP 200 but empty {audio_field}", 0)
                    else:
                        self.log_test_result(case["name"], True, 
                                           f"No silent failure - valid audio returned", len(audio_data))
                        passed += 1
                else:
                    # Non-200 responses are acceptable (proper error handling)
                    self.log_test_result(case["name"], True, 
                                       f"Proper error response: HTTP {response.status_code}", 0)
                    passed += 1
                    
            except Exception as e:
                self.log_test_result(case["name"], False, 
                                   f"Request error: {str(e)}", 0)
        
        logger.info(f"🎵 No Silent Failures: {passed}/{total} tests passed")
        return passed == total
    
    def test_voice_personalities_endpoint(self):
        """Test Voice Personalities Endpoint - should return available personalities"""
        logger.info("🎵 TESTING: Voice Personalities Endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/voice/personalities", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if personalities are returned
                voices = data.get("voices", [])
                if len(voices) >= 3:  # Should have at least 3 personalities
                    personality_names = [voice.get("id") for voice in voices]
                    expected = ["friendly_companion", "story_narrator", "learning_buddy"]
                    
                    if all(name in personality_names for name in expected):
                        self.log_test_result("Voice Personalities", True, 
                                           f"All {len(voices)} personalities available", 0)
                        return True
                    else:
                        self.log_test_result("Voice Personalities", False, 
                                           f"Missing expected personalities: {expected}", 0)
                else:
                    self.log_test_result("Voice Personalities", False, 
                                       f"Only {len(voices)} personalities found", 0)
            else:
                self.log_test_result("Voice Personalities", False, 
                                   f"HTTP {response.status_code}: {response.text}", 0)
                
        except Exception as e:
            self.log_test_result("Voice Personalities", False, 
                               f"Request error: {str(e)}", 0)
        
        return False
    
    def run_comprehensive_test(self):
        """Run all comprehensive no-audio playback fixes tests"""
        logger.info("🎵 STARTING: Comprehensive No-Audio Playback Fixes Testing")
        logger.info("=" * 80)
        
        test_results = []
        
        # Run all test categories
        test_results.append(("Backend Audio Return Validation", self.test_backend_audio_return_validation()))
        test_results.append(("TTS Audio Generation Validation", self.test_tts_audio_generation_validation()))
        test_results.append(("Audio Pipeline End-to-End", self.test_audio_pipeline_end_to_end()))
        test_results.append(("Fallback Mechanism Testing", self.test_fallback_mechanism_testing()))
        test_results.append(("No Silent Failures", self.test_no_silent_failures()))
        test_results.append(("Voice Personalities Endpoint", self.test_voice_personalities_endpoint()))
        
        # Calculate overall results
        passed_categories = sum(1 for _, result in test_results if result)
        total_categories = len(test_results)
        
        # Calculate individual test results
        total_individual_tests = len(self.results)
        passed_individual_tests = sum(1 for result in self.results if result["success"])
        
        logger.info("=" * 80)
        logger.info("🎵 COMPREHENSIVE NO-AUDIO PLAYBACK FIXES TEST RESULTS")
        logger.info("=" * 80)
        
        for category, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} {category}")
        
        logger.info("-" * 80)
        logger.info(f"📊 CATEGORY SUMMARY: {passed_categories}/{total_categories} categories passed ({passed_categories/total_categories*100:.1f}%)")
        logger.info(f"📊 INDIVIDUAL TESTS: {passed_individual_tests}/{total_individual_tests} tests passed ({passed_individual_tests/total_individual_tests*100:.1f}%)")
        
        # Audio size statistics
        audio_sizes = [r["audio_size"] for r in self.results if r["audio_size"] > 0]
        if audio_sizes:
            avg_audio_size = sum(audio_sizes) / len(audio_sizes)
            logger.info(f"📊 AUDIO STATISTICS: {len(audio_sizes)} responses with audio, avg size: {avg_audio_size:.0f} chars")
        
        # Check for critical issues
        critical_failures = [r for r in self.results if not r["success"] and "SILENT FAILURE" in r["details"]]
        if critical_failures:
            logger.error(f"🚨 CRITICAL: {len(critical_failures)} silent failures detected!")
            for failure in critical_failures:
                logger.error(f"   - {failure['test']}: {failure['details']}")
        
        # Final assessment
        if passed_categories == total_categories:
            logger.info("🎉 ALL CATEGORIES PASSED - No-audio playback fixes are working correctly!")
            return True
        else:
            logger.error(f"❌ {total_categories - passed_categories} categories failed - Audio fixes need attention")
            return False

def main():
    """Main test execution"""
    tester = NoAudioPlaybackFixesTest()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎵 COMPREHENSIVE NO-AUDIO PLAYBACK FIXES: ALL TESTS PASSED")
        exit(0)
    else:
        print("\n🎵 COMPREHENSIVE NO-AUDIO PLAYBACK FIXES: SOME TESTS FAILED")
        exit(1)

if __name__ == "__main__":
    main()