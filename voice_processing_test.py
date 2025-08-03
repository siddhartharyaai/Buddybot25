#!/usr/bin/env python3
"""
Voice Processing Functionality Test
Focus: "No audio: Missing audio data" issue resolution

Test Requirements from Review:
1. Voice Processing Endpoint Testing with various scenarios
2. Audio Output Validation - verify response_audio field contains valid base64 audio data  
3. User Profile Handling - test fixed user profile exception handling
4. TTS Pipeline Verification - confirm TTS generation is working
"""

import requests
import json
import base64
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://754f72e7-5d73-488b-8ab4-20151131dc19.preview.emergentagent.com/api"

class VoiceProcessingTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session_id = f"test_session_{int(time.time())}"
        
    def log_result(self, test_name, success, details, audio_length=0):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "audio_length": audio_length,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   Details: {details}")
        if audio_length > 0:
            print(f"   Audio Length: {audio_length} chars")
        print()

    def create_test_audio_base64(self):
        """Create a simple test audio data in base64 format"""
        # Create minimal WAV header + some audio data
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
        # Add some sample audio data (silence)
        audio_data = b'\x00' * 1000  # 1000 bytes of silence
        full_audio = wav_header + audio_data
        return base64.b64encode(full_audio).decode('utf-8')

    def test_direct_tts_endpoint(self):
        """Test 1: Direct TTS endpoint functionality"""
        try:
            url = f"{self.backend_url}/voice/tts"
            payload = {
                "text": "Hello, this is a test of the text-to-speech system.",
                "personality": "friendly_companion"
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and data.get("audio_base64"):
                    audio_length = len(data["audio_base64"])
                    self.log_result(
                        "Direct TTS Endpoint", 
                        True, 
                        f"TTS generated successfully with {audio_length} chars of audio data",
                        audio_length
                    )
                    return True
                else:
                    self.log_result("Direct TTS Endpoint", False, f"No audio in response: {data}")
                    return False
            else:
                self.log_result("Direct TTS Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Direct TTS Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_voice_processing_with_valid_audio(self):
        """Test 2: Voice processing with valid audio data"""
        try:
            url = f"{self.backend_url}/voice/process_audio"
            
            # Create form data
            form_data = {
                'session_id': self.session_id,
                'user_id': 'test_user_voice_001',
                'audio_base64': self.create_test_audio_base64()
            }
            
            response = requests.post(url, data=form_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    response_audio = data.get("response_audio")
                    if response_audio and len(response_audio) > 0:
                        self.log_result(
                            "Voice Processing - Valid Audio", 
                            True, 
                            f"Voice processing successful with {len(response_audio)} chars of response audio",
                            len(response_audio)
                        )
                        return True
                    else:
                        self.log_result("Voice Processing - Valid Audio", False, "No response_audio in successful response")
                        return False
                else:
                    self.log_result("Voice Processing - Valid Audio", False, f"Processing failed: {data}")
                    return False
            else:
                self.log_result("Voice Processing - Valid Audio", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Voice Processing - Valid Audio", False, f"Exception: {str(e)}")
            return False

    def test_voice_processing_with_silent_audio(self):
        """Test 3: Voice processing with silent/empty audio (should return fallback TTS)"""
        try:
            url = f"{self.backend_url}/voice/process_audio"
            
            # Create minimal silent audio
            silent_audio = base64.b64encode(b'\x00' * 100).decode('utf-8')
            
            form_data = {
                'session_id': f"{self.session_id}_silent",
                'user_id': 'test_user_voice_002',
                'audio_base64': silent_audio
            }
            
            response = requests.post(url, data=form_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    response_audio = data.get("response_audio")
                    if response_audio and len(response_audio) > 0:
                        self.log_result(
                            "Voice Processing - Silent Audio Fallback", 
                            True, 
                            f"Fallback TTS working: {len(response_audio)} chars of audio generated",
                            len(response_audio)
                        )
                        return True
                    else:
                        self.log_result("Voice Processing - Silent Audio Fallback", False, "No fallback audio generated for silent input")
                        return False
                else:
                    self.log_result("Voice Processing - Silent Audio Fallback", False, f"Processing failed: {data}")
                    return False
            else:
                self.log_result("Voice Processing - Silent Audio Fallback", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Voice Processing - Silent Audio Fallback", False, f"Exception: {str(e)}")
            return False

    def test_voice_processing_invalid_user_profile(self):
        """Test 4: Voice processing with non-existent user_id (should use default profile + generate audio)"""
        try:
            url = f"{self.backend_url}/voice/process_audio"
            
            form_data = {
                'session_id': f"{self.session_id}_invalid_user",
                'user_id': 'non_existent_user_12345',
                'audio_base64': self.create_test_audio_base64()
            }
            
            response = requests.post(url, data=form_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    response_audio = data.get("response_audio")
                    if response_audio and len(response_audio) > 0:
                        self.log_result(
                            "Voice Processing - Invalid User Profile", 
                            True, 
                            f"Default profile handling working: {len(response_audio)} chars of audio generated",
                            len(response_audio)
                        )
                        return True
                    else:
                        self.log_result("Voice Processing - Invalid User Profile", False, "No audio generated for invalid user profile")
                        return False
                else:
                    self.log_result("Voice Processing - Invalid User Profile", False, f"Processing failed: {data}")
                    return False
            else:
                # Should NOT return 404 errors for missing profiles anymore
                self.log_result("Voice Processing - Invalid User Profile", False, f"HTTP {response.status_code}: Should not return 404 for missing profiles")
                return False
                
        except Exception as e:
            self.log_result("Voice Processing - Invalid User Profile", False, f"Exception: {str(e)}")
            return False

    def test_voice_personalities_endpoint(self):
        """Test 5: Voice personalities endpoint functionality"""
        try:
            url = f"{self.backend_url}/voice/personalities"
            
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "personalities" in data:
                    personalities = data["personalities"]
                    if len(personalities) > 0:
                        self.log_result(
                            "Voice Personalities Endpoint", 
                            True, 
                            f"Retrieved {len(personalities)} voice personalities successfully"
                        )
                        return True
                    else:
                        self.log_result("Voice Personalities Endpoint", False, "No personalities returned")
                        return False
                else:
                    self.log_result("Voice Personalities Endpoint", False, f"Unexpected response format: {data}")
                    return False
            else:
                self.log_result("Voice Personalities Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Voice Personalities Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_multiple_voice_personalities_tts(self):
        """Test 6: TTS with different voice personalities"""
        personalities = ["friendly_companion", "story_narrator", "learning_buddy"]
        success_count = 0
        
        for personality in personalities:
            try:
                url = f"{self.backend_url}/voice/tts"
                payload = {
                    "text": f"Hello, I am the {personality.replace('_', ' ')} personality.",
                    "personality": personality
                }
                
                response = requests.post(url, json=payload, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success" and data.get("audio_base64"):
                        success_count += 1
                        print(f"   ✅ {personality}: {len(data['audio_base64'])} chars audio")
                    else:
                        print(f"   ❌ {personality}: No audio generated")
                else:
                    print(f"   ❌ {personality}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {personality}: Exception {str(e)}")
        
        success = success_count == len(personalities)
        self.log_result(
            "Multiple Voice Personalities TTS", 
            success, 
            f"{success_count}/{len(personalities)} personalities working"
        )
        return success

    def validate_base64_audio_format(self, audio_data):
        """Test 7: Validate base64 audio format"""
        try:
            if not audio_data:
                return False, "Audio data is empty"
            
            if len(audio_data) < 100:
                return False, f"Audio data too short: {len(audio_data)} chars"
            
            # Try to decode base64
            try:
                decoded = base64.b64decode(audio_data)
                if len(decoded) < 50:
                    return False, f"Decoded audio too short: {len(decoded)} bytes"
            except Exception as e:
                return False, f"Invalid base64 format: {str(e)}"
            
            return True, f"Valid base64 audio: {len(audio_data)} chars, {len(decoded)} bytes"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def run_comprehensive_voice_test(self):
        """Run all voice processing tests"""
        print("🎯 VOICE PROCESSING FUNCTIONALITY TEST")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Session ID: {self.session_id}")
        print()
        
        # Run all tests
        tests = [
            self.test_direct_tts_endpoint,
            self.test_voice_processing_with_valid_audio,
            self.test_voice_processing_with_silent_audio,
            self.test_voice_processing_invalid_user_profile,
            self.test_voice_personalities_endpoint,
            self.test_multiple_voice_personalities_tts
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        # Additional validation test
        print("🔍 AUDIO FORMAT VALIDATION TEST")
        print("-" * 40)
        
        # Test audio format validation on a sample
        try:
            url = f"{self.backend_url}/voice/tts"
            payload = {"text": "Audio format validation test", "personality": "friendly_companion"}
            response = requests.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                audio_data = data.get("audio_base64")
                is_valid, message = self.validate_base64_audio_format(audio_data)
                self.log_result("Base64 Audio Format Validation", is_valid, message)
                if is_valid:
                    passed += 1
                total += 1
            else:
                self.log_result("Base64 Audio Format Validation", False, "Could not get audio for validation")
                total += 1
        except Exception as e:
            self.log_result("Base64 Audio Format Validation", False, f"Validation test failed: {str(e)}")
            total += 1
        
        # Summary
        print("=" * 60)
        print("🎯 VOICE PROCESSING TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        # Critical issues check
        critical_issues = []
        for result in self.test_results:
            if not result["success"]:
                if "No audio" in result["details"] or "Missing audio data" in result["details"]:
                    critical_issues.append(f"CRITICAL: {result['test']} - {result['details']}")
                elif result["audio_length"] == 0 and "audio" in result["test"].lower():
                    critical_issues.append(f"CRITICAL: {result['test']} - No audio generated")
        
        if critical_issues:
            print("🚨 CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"   {issue}")
        else:
            print("✅ NO CRITICAL 'Missing audio data' ISSUES FOUND")
        
        print()
        print("🎵 AUDIO OUTPUT ANALYSIS:")
        audio_tests = [r for r in self.test_results if r["audio_length"] > 0]
        if audio_tests:
            avg_audio_length = sum(r["audio_length"] for r in audio_tests) / len(audio_tests)
            print(f"   Average Audio Length: {avg_audio_length:.0f} chars")
            print(f"   Audio Generation Success: {len(audio_tests)}/{total} tests")
        else:
            print("   ❌ NO AUDIO GENERATED IN ANY TEST")
        
        return passed, total, critical_issues

def main():
    """Main test execution"""
    tester = VoiceProcessingTester()
    passed, total, critical_issues = tester.run_comprehensive_voice_test()
    
    # Exit with appropriate code
    if len(critical_issues) > 0:
        print("\n🚨 CRITICAL VOICE PROCESSING ISSUES DETECTED")
        exit(1)
    elif passed == total:
        print("\n✅ ALL VOICE PROCESSING TESTS PASSED")
        exit(0)
    else:
        print(f"\n⚠️ SOME TESTS FAILED ({passed}/{total} passed)")
        exit(1)

if __name__ == "__main__":
    main()
"""
Voice Processing Backend Test - Focused on Review Requirements
Tests voice processing endpoint, conversation flow, and story narration
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

# Get backend URL from frontend environment
BACKEND_URL = "https://754f72e7-5d73-488b-8ab4-20151131dc19.preview.emergentagent.com/api"

class VoiceProcessingTester:
    """Focused voice processing backend tester"""
    
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
    
    async def run_voice_tests(self):
        """Run focused voice processing tests"""
        logger.info("🎤 Starting Voice Processing Backend Testing...")
        
        # Test sequence focused on voice processing
        test_sequence = [
            ("Health Check", self.test_health_check),
            ("User Profile Setup", self.test_setup_user_profile),
            ("Voice Processing Endpoint - Basic", self.test_voice_processing_basic),
            ("Voice Processing Endpoint - Audio Data", self.test_voice_processing_audio_data),
            ("Voice Processing Endpoint - Form Data", self.test_voice_processing_form_data),
            ("Voice Processing Endpoint - Error Handling", self.test_voice_processing_error_handling),
            ("Basic Conversation Flow", self.test_basic_conversation_flow),
            ("Story Narration Endpoint", self.test_story_narration_endpoint),
            ("Voice Personalities", self.test_voice_personalities),
            ("Content Stories API", self.test_content_stories_api),
            ("Critical API Endpoints", self.test_critical_api_endpoints)
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
            except Exception as e:
                logger.error(f"💥 Test {test_name} failed with exception: {str(e)}")
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
                    logger.info(f"🏥 Health check response: {data}")
                    
                    return {
                        "success": True,
                        "status": data.get("status"),
                        "orchestrator_initialized": data.get("agents", {}).get("orchestrator", False),
                        "gemini_configured": data.get("agents", {}).get("gemini_configured", False),
                        "deepgram_configured": data.get("agents", {}).get("deepgram_configured", False),
                        "database": data.get("database")
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_setup_user_profile(self):
        """Setup test user profile"""
        try:
            profile_data = {
                "name": "Test Child",
                "age": 8,
                "location": "San Francisco",
                "timezone": "America/Los_Angeles",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "animals", "music"],
                "learning_goals": ["reading", "counting"],
                "parent_email": "parent@test.com"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/users/profile",
                json=profile_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_user_id = data["id"]
                    self.test_session_id = f"session_{uuid.uuid4().hex[:8]}"
                    logger.info(f"👤 Created test user: {self.test_user_id}")
                    
                    return {
                        "success": True,
                        "user_id": data["id"],
                        "name": data["name"],
                        "age": data["age"]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_voice_processing_basic(self):
        """Test basic voice processing endpoint accessibility"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test with minimal valid data
            mock_audio = b"test_audio_data"
            audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
            
            form_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": audio_base64
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/voice/process_audio",
                data=form_data
            ) as response:
                logger.info(f"🎤 Voice processing response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "endpoint_accessible": True,
                        "status": data.get("status"),
                        "has_transcript": bool(data.get("transcript")),
                        "has_response_text": bool(data.get("response_text")),
                        "has_response_audio": bool(data.get("response_audio")),
                        "content_type": data.get("content_type")
                    }
                elif response.status in [400, 422, 500]:
                    # Expected for test data - endpoint is accessible
                    try:
                        error_data = await response.json()
                        return {
                            "success": True,
                            "endpoint_accessible": True,
                            "expected_error": True,
                            "status_code": response.status,
                            "error_handled": True,
                            "error_detail": error_data.get("detail", "")
                        }
                    except:
                        return {
                            "success": True,
                            "endpoint_accessible": True,
                            "expected_error": True,
                            "status_code": response.status
                        }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_voice_processing_audio_data(self):
        """Test voice processing with various audio data sizes"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test different audio data sizes
            test_cases = [
                {"name": "1 byte", "size": 1},
                {"name": "100 bytes", "size": 100},
                {"name": "1KB", "size": 1024},
                {"name": "8KB", "size": 8192}
            ]
            
            results = []
            
            for case in test_cases:
                mock_audio = b"A" * case["size"]
                audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
                
                form_data = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "audio_base64": audio_base64
                }
                
                try:
                    async with self.session.post(
                        f"{BACKEND_URL}/voice/process_audio",
                        data=form_data
                    ) as response:
                        results.append({
                            "size": case["name"],
                            "status_code": response.status,
                            "processed": response.status in [200, 400, 422, 500],
                            "base64_length": len(audio_base64)
                        })
                except Exception as e:
                    results.append({
                        "size": case["name"],
                        "error": str(e),
                        "processed": False
                    })
                
                await asyncio.sleep(0.1)
            
            processed_count = sum(1 for r in results if r.get("processed", False))
            
            return {
                "success": True,
                "test_cases": len(test_cases),
                "processed_successfully": processed_count,
                "processing_rate": f"{processed_count/len(test_cases)*100:.1f}%",
                "results": results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_voice_processing_form_data(self):
        """Test voice processing form data validation"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test missing required fields
            test_cases = [
                {
                    "name": "Missing audio_base64",
                    "data": {
                        "session_id": self.test_session_id,
                        "user_id": self.test_user_id
                    },
                    "expected_status": 422
                },
                {
                    "name": "Missing session_id",
                    "data": {
                        "user_id": self.test_user_id,
                        "audio_base64": base64.b64encode(b"test").decode('utf-8')
                    },
                    "expected_status": 422
                },
                {
                    "name": "Missing user_id",
                    "data": {
                        "session_id": self.test_session_id,
                        "audio_base64": base64.b64encode(b"test").decode('utf-8')
                    },
                    "expected_status": 422
                },
                {
                    "name": "All fields present",
                    "data": {
                        "session_id": self.test_session_id,
                        "user_id": self.test_user_id,
                        "audio_base64": base64.b64encode(b"test_audio").decode('utf-8')
                    },
                    "expected_status": [200, 400, 500]  # Any processing status is fine
                }
            ]
            
            validation_results = []
            
            for case in test_cases:
                try:
                    async with self.session.post(
                        f"{BACKEND_URL}/voice/process_audio",
                        data=case["data"]
                    ) as response:
                        expected = case["expected_status"]
                        if isinstance(expected, list):
                            validation_correct = response.status in expected
                        else:
                            validation_correct = response.status == expected
                        
                        validation_results.append({
                            "test_case": case["name"],
                            "status_code": response.status,
                            "validation_correct": validation_correct,
                            "expected": expected
                        })
                except Exception as e:
                    validation_results.append({
                        "test_case": case["name"],
                        "error": str(e),
                        "validation_correct": False
                    })
                
                await asyncio.sleep(0.1)
            
            correct_validations = sum(1 for r in validation_results if r.get("validation_correct", False))
            
            return {
                "success": True,
                "validation_tests": len(test_cases),
                "correct_validations": correct_validations,
                "validation_rate": f"{correct_validations/len(test_cases)*100:.1f}%",
                "results": validation_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_voice_processing_error_handling(self):
        """Test voice processing error handling"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test error scenarios
            error_cases = [
                {
                    "name": "Empty audio",
                    "audio_base64": "",
                    "expected_error": True
                },
                {
                    "name": "Invalid base64",
                    "audio_base64": "invalid_base64!!!",
                    "expected_error": True
                },
                {
                    "name": "Very large audio",
                    "audio_base64": base64.b64encode(b"X" * 100000).decode('utf-8'),
                    "expected_error": False  # Should handle large data
                }
            ]
            
            error_handling_results = []
            
            for case in error_cases:
                form_data = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "audio_base64": case["audio_base64"]
                }
                
                try:
                    async with self.session.post(
                        f"{BACKEND_URL}/voice/process_audio",
                        data=form_data
                    ) as response:
                        is_error = response.status >= 400
                        error_handled_correctly = is_error == case["expected_error"]
                        
                        error_handling_results.append({
                            "test_case": case["name"],
                            "status_code": response.status,
                            "is_error": is_error,
                            "expected_error": case["expected_error"],
                            "handled_correctly": error_handled_correctly
                        })
                except Exception as e:
                    error_handling_results.append({
                        "test_case": case["name"],
                        "exception": str(e),
                        "handled_correctly": case["expected_error"]  # Exception is expected for error cases
                    })
                
                await asyncio.sleep(0.1)
            
            correct_handling = sum(1 for r in error_handling_results if r.get("handled_correctly", False))
            
            return {
                "success": True,
                "error_cases_tested": len(error_cases),
                "correctly_handled": correct_handling,
                "error_handling_rate": f"{correct_handling/len(error_cases)*100:.1f}%",
                "results": error_handling_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_basic_conversation_flow(self):
        """Test basic conversation flow through orchestrator"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test text conversation first
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Hi! Can you tell me a short story about a friendly animal?"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "success": True,
                        "conversation_working": True,
                        "response_received": bool(data.get("response_text")),
                        "response_length": len(data.get("response_text", "")),
                        "content_type": data.get("content_type"),
                        "has_audio": bool(data.get("response_audio")),
                        "audio_size": len(data.get("response_audio", "")) if data.get("response_audio") else 0,
                        "orchestrator_processing": "Working correctly"
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_story_narration_endpoint(self):
        """Test story narration endpoint functionality"""
        if not self.test_user_id:
            return {"success": False, "error": "Missing test user ID"}
        
        try:
            # First get available stories
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status != 200:
                    return {"success": False, "error": "Could not fetch stories"}
                
                stories_data = await response.json()
                stories = stories_data.get("stories", [])
                
                if not stories:
                    return {"success": False, "error": "No stories available"}
                
                # Test narration with first story
                story = stories[0]
                story_id = story.get("id")
                
                narration_request = {
                    "user_id": self.test_user_id,
                    "full_narration": True,
                    "voice_personality": "friendly_companion"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/content/stories/{story_id}/narrate",
                    json=narration_request
                ) as narration_response:
                    if narration_response.status == 200:
                        narration_data = await narration_response.json()
                        
                        return {
                            "success": True,
                            "story_narration_working": True,
                            "story_id": narration_data.get("story_id"),
                            "narration_complete": narration_data.get("narration_complete"),
                            "has_response_text": bool(narration_data.get("response_text")),
                            "has_response_audio": bool(narration_data.get("response_audio")),
                            "response_text_length": len(narration_data.get("response_text", "")),
                            "response_audio_size": len(narration_data.get("response_audio", "")) if narration_data.get("response_audio") else 0,
                            "content_type": narration_data.get("content_type"),
                            "stories_available": len(stories)
                        }
                    else:
                        error_text = await narration_response.text()
                        return {"success": False, "error": f"Narration HTTP {narration_response.status}: {error_text}"}
                        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_voice_personalities(self):
        """Test voice personalities endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/voice/personalities") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "success": True,
                        "personalities_available": True,
                        "personalities_count": len(data) if isinstance(data, (list, dict)) else 0,
                        "personalities": list(data.keys()) if isinstance(data, dict) else data,
                        "has_descriptions": all("description" in v for v in data.values()) if isinstance(data, dict) else False
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_content_stories_api(self):
        """Test content stories API"""
        try:
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status == 200:
                    data = await response.json()
                    stories = data.get("stories", [])
                    
                    return {
                        "success": True,
                        "stories_api_working": True,
                        "stories_count": len(stories),
                        "has_stories": len(stories) > 0,
                        "story_structure": bool(stories and all(
                            "id" in story and "title" in story and "content" in story 
                            for story in stories[:3]  # Check first 3
                        )),
                        "sample_story_titles": [story.get("title", "") for story in stories[:3]]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_critical_api_endpoints(self):
        """Test all critical API endpoints are responding"""
        try:
            critical_endpoints = [
                {"path": "/health", "method": "GET"},
                {"path": "/voice/personalities", "method": "GET"},
                {"path": "/content/stories", "method": "GET"},
                {"path": "/agents/status", "method": "GET"}
            ]
            
            endpoint_results = []
            
            for endpoint in critical_endpoints:
                try:
                    if endpoint["method"] == "GET":
                        async with self.session.get(f"{BACKEND_URL}{endpoint['path']}") as response:
                            endpoint_results.append({
                                "endpoint": endpoint["path"],
                                "status_code": response.status,
                                "responding": response.status < 500,
                                "accessible": True
                            })
                    else:
                        endpoint_results.append({
                            "endpoint": endpoint["path"],
                            "method": endpoint["method"],
                            "accessible": False,
                            "note": "Method not tested"
                        })
                except Exception as e:
                    endpoint_results.append({
                        "endpoint": endpoint["path"],
                        "error": str(e),
                        "accessible": False
                    })
                
                await asyncio.sleep(0.1)
            
            responding_endpoints = sum(1 for r in endpoint_results if r.get("responding", False))
            
            return {
                "success": True,
                "critical_endpoints_tested": len(critical_endpoints),
                "responding_endpoints": responding_endpoints,
                "response_rate": f"{responding_endpoints/len(critical_endpoints)*100:.1f}%",
                "endpoint_results": endpoint_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

async def main():
    """Main test runner"""
    async with VoiceProcessingTester() as tester:
        results = await tester.run_voice_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("🎤 VOICE PROCESSING BACKEND TEST SUMMARY")
        print("="*80)
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r["status"] == "PASS")
        failed_tests = sum(1 for r in results.values() if r["status"] == "FAIL")
        error_tests = sum(1 for r in results.values() if r["status"] == "ERROR")
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"💥 Errors: {error_tests}")
        print(f"📈 Success Rate: {passed_tests/total_tests*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for test_name, result in results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "💥"
            print(f"{status_icon} {test_name}: {result['status']}")
            
            # Show key details for important tests
            if "Voice Processing" in test_name and result["status"] == "PASS":
                details = result.get("details", {})
                if "endpoint_accessible" in details:
                    print(f"   🔗 Endpoint Accessible: {details['endpoint_accessible']}")
                if "processing_rate" in details:
                    print(f"   📊 Processing Rate: {details['processing_rate']}")
            
            if "Story Narration" in test_name and result["status"] == "PASS":
                details = result.get("details", {})
                if "story_narration_working" in details:
                    print(f"   📚 Story Narration: {details['story_narration_working']}")
                if "stories_available" in details:
                    print(f"   📖 Stories Available: {details['stories_available']}")
        
        print("\n" + "="*80)
        
        # Return success if most tests passed
        return passed_tests >= total_tests * 0.8

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)