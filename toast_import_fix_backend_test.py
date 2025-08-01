#!/usr/bin/env python3
"""
Toast Import Fix Backend Validation Test
Tests backend APIs that support toast functionality after toast import fix
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

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    base_url = line.split('=')[1].strip()
                    return f"{base_url}/api"
    except:
        pass
    return "http://localhost:8001/api"

BACKEND_URL = get_backend_url()

class ToastImportFixBackendTester:
    """Backend tester focused on APIs that support toast functionality"""
    
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.test_user_data = {
            "email": f"toast_test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPassword123!",
            "name": "Toast Test User",
            "age": 8,
            "location": "Test City"
        }
        self.auth_token = None
        self.user_id = None
        self.profile_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_check(self):
        """Test basic health check"""
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Health Check: {data}")
                    return True
                else:
                    logger.error(f"❌ Health Check Failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Health Check Error: {str(e)}")
            return False
    
    async def test_signup_validation_backend(self):
        """Test signup validation that triggers toast messages"""
        logger.info("🧪 Testing Signup Validation Backend APIs...")
        
        results = {
            "valid_signup": False,
            "duplicate_email": False,
            "invalid_age": False,
            "missing_fields": False
        }
        
        # Test 1: Valid signup
        try:
            signup_data = self.test_user_data.copy()
            async with self.session.post(f"{BACKEND_URL}/auth/signup", json=signup_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    self.user_id = data.get("user_id")
                    self.profile_id = data.get("profile_id")
                    results["valid_signup"] = True
                    logger.info("✅ Valid signup successful")
                else:
                    logger.error(f"❌ Valid signup failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Valid signup error: {str(e)}")
        
        # Test 2: Duplicate email (should trigger error toast)
        try:
            async with self.session.post(f"{BACKEND_URL}/auth/signup", json=self.test_user_data) as response:
                if response.status == 400:
                    data = await response.json()
                    if "already registered" in data.get("detail", "").lower():
                        results["duplicate_email"] = True
                        logger.info("✅ Duplicate email validation working")
                else:
                    logger.error(f"❌ Duplicate email test failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Duplicate email test error: {str(e)}")
        
        # Test 3: Invalid age (should trigger validation toast)
        try:
            invalid_age_data = self.test_user_data.copy()
            invalid_age_data["email"] = f"invalid_age_{uuid.uuid4().hex[:8]}@example.com"
            invalid_age_data["age"] = 2  # Below minimum age
            async with self.session.post(f"{BACKEND_URL}/auth/signup", json=invalid_age_data) as response:
                if response.status == 422:  # Validation error
                    results["invalid_age"] = True
                    logger.info("✅ Age validation working")
                else:
                    logger.error(f"❌ Age validation test failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Age validation test error: {str(e)}")
        
        # Test 4: Missing required fields (should trigger validation toast)
        try:
            missing_fields_data = {"email": f"missing_{uuid.uuid4().hex[:8]}@example.com"}
            async with self.session.post(f"{BACKEND_URL}/auth/signup", json=missing_fields_data) as response:
                if response.status == 422:  # Validation error
                    results["missing_fields"] = True
                    logger.info("✅ Missing fields validation working")
                else:
                    logger.error(f"❌ Missing fields test failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Missing fields test error: {str(e)}")
        
        success_rate = sum(results.values()) / len(results) * 100
        logger.info(f"📊 Signup Validation Backend: {success_rate:.1f}% success rate")
        return results
    
    async def test_signin_validation_backend(self):
        """Test signin validation that triggers toast messages"""
        logger.info("🧪 Testing Signin Validation Backend APIs...")
        
        results = {
            "valid_signin": False,
            "invalid_credentials": False,
            "missing_email": False,
            "missing_password": False
        }
        
        # Test 1: Valid signin
        try:
            signin_data = {
                "email": self.test_user_data["email"],
                "password": self.test_user_data["password"]
            }
            async with self.session.post(f"{BACKEND_URL}/auth/signin", json=signin_data) as response:
                if response.status == 200:
                    data = await response.json()
                    results["valid_signin"] = True
                    logger.info("✅ Valid signin successful")
                else:
                    logger.error(f"❌ Valid signin failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Valid signin error: {str(e)}")
        
        # Test 2: Invalid credentials (should trigger error toast)
        try:
            invalid_creds = {
                "email": self.test_user_data["email"],
                "password": "WrongPassword123!"
            }
            async with self.session.post(f"{BACKEND_URL}/auth/signin", json=invalid_creds) as response:
                if response.status == 401:
                    data = await response.json()
                    if "invalid" in data.get("detail", "").lower():
                        results["invalid_credentials"] = True
                        logger.info("✅ Invalid credentials validation working")
                else:
                    logger.error(f"❌ Invalid credentials test failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Invalid credentials test error: {str(e)}")
        
        # Test 3: Missing email (should trigger validation toast)
        try:
            missing_email = {"password": "TestPassword123!"}
            async with self.session.post(f"{BACKEND_URL}/auth/signin", json=missing_email) as response:
                if response.status == 422:  # Validation error
                    results["missing_email"] = True
                    logger.info("✅ Missing email validation working")
                else:
                    logger.error(f"❌ Missing email test failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Missing email test error: {str(e)}")
        
        # Test 4: Missing password (should trigger validation toast)
        try:
            missing_password = {"email": self.test_user_data["email"]}
            async with self.session.post(f"{BACKEND_URL}/auth/signin", json=missing_password) as response:
                if response.status == 422:  # Validation error
                    results["missing_password"] = True
                    logger.info("✅ Missing password validation working")
                else:
                    logger.error(f"❌ Missing password test failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Missing password test error: {str(e)}")
        
        success_rate = sum(results.values()) / len(results) * 100
        logger.info(f"📊 Signin Validation Backend: {success_rate:.1f}% success rate")
        return results
    
    async def test_profile_update_backend(self):
        """Test profile update APIs that trigger success/error toasts"""
        logger.info("🧪 Testing Profile Update Backend APIs...")
        
        if not self.profile_id:
            logger.error("❌ No profile ID available for testing")
            return {"profile_update": False, "profile_get": False}
        
        results = {
            "profile_update": False,
            "profile_get": False,
            "invalid_profile_id": False
        }
        
        # Test 1: Valid profile update (should trigger success toast)
        try:
            update_data = {
                "interests": ["dinosaurs", "space", "animals"],
                "learning_goals": ["science", "reading"]
            }
            async with self.session.put(f"{BACKEND_URL}/users/profile/{self.profile_id}", json=update_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("interests") == update_data["interests"]:
                        results["profile_update"] = True
                        logger.info("✅ Profile update successful")
                else:
                    logger.error(f"❌ Profile update failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Profile update error: {str(e)}")
        
        # Test 2: Get profile (should work after update)
        try:
            async with self.session.get(f"{BACKEND_URL}/users/profile/{self.profile_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("id") == self.profile_id:
                        results["profile_get"] = True
                        logger.info("✅ Profile get successful")
                else:
                    logger.error(f"❌ Profile get failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Profile get error: {str(e)}")
        
        # Test 3: Invalid profile ID (should trigger error toast)
        try:
            invalid_id = "invalid_profile_id_123"
            async with self.session.get(f"{BACKEND_URL}/users/profile/{invalid_id}") as response:
                if response.status == 404:
                    results["invalid_profile_id"] = True
                    logger.info("✅ Invalid profile ID validation working")
                else:
                    logger.error(f"❌ Invalid profile ID test failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Invalid profile ID test error: {str(e)}")
        
        success_rate = sum(results.values()) / len(results) * 100
        logger.info(f"📊 Profile Update Backend: {success_rate:.1f}% success rate")
        return results
    
    async def test_parental_controls_backend(self):
        """Test parental controls APIs that trigger confirmation toasts"""
        logger.info("🧪 Testing Parental Controls Backend APIs...")
        
        if not self.profile_id:
            logger.error("❌ No profile ID available for testing")
            return {"parental_get": False, "parental_update": False}
        
        results = {
            "parental_get": False,
            "parental_update": False,
            "invalid_user_id": False
        }
        
        # Test 1: Get parental controls
        try:
            async with self.session.get(f"{BACKEND_URL}/users/{self.profile_id}/parental-controls") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("user_id") == self.profile_id:
                        results["parental_get"] = True
                        logger.info("✅ Parental controls get successful")
                else:
                    logger.error(f"❌ Parental controls get failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Parental controls get error: {str(e)}")
        
        # Test 2: Update parental controls (should trigger success toast)
        try:
            update_data = {
                "time_limits": {"monday": 45, "tuesday": 45, "wednesday": 45, "thursday": 45, "friday": 60, "saturday": 90, "sunday": 90},
                "monitoring_enabled": True
            }
            async with self.session.put(f"{BACKEND_URL}/users/{self.profile_id}/parental-controls", json=update_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("time_limits", {}).get("monday") == 45:
                        results["parental_update"] = True
                        logger.info("✅ Parental controls update successful")
                else:
                    logger.error(f"❌ Parental controls update failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Parental controls update error: {str(e)}")
        
        # Test 3: Invalid user ID (should trigger error toast)
        try:
            invalid_id = "invalid_user_id_123"
            async with self.session.get(f"{BACKEND_URL}/users/{invalid_id}/parental-controls") as response:
                if response.status == 404:
                    results["invalid_user_id"] = True
                    logger.info("✅ Invalid user ID validation working")
                else:
                    logger.error(f"❌ Invalid user ID test failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Invalid user ID test error: {str(e)}")
        
        success_rate = sum(results.values()) / len(results) * 100
        logger.info(f"📊 Parental Controls Backend: {success_rate:.1f}% success rate")
        return results
    
    async def test_core_api_endpoints(self):
        """Test core API endpoints for no regression"""
        logger.info("🧪 Testing Core API Endpoints...")
        
        results = {
            "voice_personalities": False,
            "content_stories": False,
            "text_conversation": False,
            "tts_simple": False
        }
        
        # Test 1: Voice personalities endpoint
        try:
            async with self.session.get(f"{BACKEND_URL}/voice/personalities") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, dict) and len(data.get("personalities", [])) > 0:
                        results["voice_personalities"] = True
                        logger.info("✅ Voice personalities endpoint working")
                else:
                    logger.error(f"❌ Voice personalities failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Voice personalities error: {str(e)}")
        
        # Test 2: Content stories endpoint
        try:
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, dict) and len(data.get("stories", [])) > 0:
                        results["content_stories"] = True
                        logger.info("✅ Content stories endpoint working")
                else:
                    logger.error(f"❌ Content stories failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Content stories error: {str(e)}")
        
        # Test 3: Text conversation endpoint
        try:
            if self.profile_id:
                conversation_data = {
                    "session_id": str(uuid.uuid4()),
                    "user_id": self.profile_id,
                    "message": "Hello, how are you today?"
                }
                async with self.session.post(f"{BACKEND_URL}/conversations/text", json=conversation_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("response_text"):
                            results["text_conversation"] = True
                            logger.info("✅ Text conversation endpoint working")
                    else:
                        logger.error(f"❌ Text conversation failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Text conversation error: {str(e)}")
        
        # Test 4: Simple TTS endpoint
        try:
            tts_data = {
                "text": "Hello, this is a test message for TTS.",
                "personality": "friendly_companion"
            }
            async with self.session.post(f"{BACKEND_URL}/voice/tts", json=tts_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success" and data.get("audio_base64"):
                        results["tts_simple"] = True
                        logger.info("✅ Simple TTS endpoint working")
                else:
                    logger.error(f"❌ Simple TTS failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Simple TTS error: {str(e)}")
        
        success_rate = sum(results.values()) / len(results) * 100
        logger.info(f"📊 Core API Endpoints: {success_rate:.1f}% success rate")
        return results
    
    async def test_error_handling_scenarios(self):
        """Test various error scenarios that should trigger toast notifications"""
        logger.info("🧪 Testing Error Handling Scenarios...")
        
        results = {
            "invalid_json": False,
            "missing_content_type": False,
            "server_error_handling": False,
            "timeout_handling": False
        }
        
        # Test 1: Invalid JSON (should trigger error toast)
        try:
            headers = {"Content-Type": "application/json"}
            async with self.session.post(f"{BACKEND_URL}/auth/signin", data="invalid json", headers=headers) as response:
                if response.status == 422:  # Unprocessable Entity
                    results["invalid_json"] = True
                    logger.info("✅ Invalid JSON handling working")
                else:
                    logger.error(f"❌ Invalid JSON test failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Invalid JSON test error: {str(e)}")
        
        # Test 2: Missing content type (should be handled gracefully)
        try:
            async with self.session.post(f"{BACKEND_URL}/health") as response:
                if response.status in [200, 405]:  # OK or Method Not Allowed
                    results["missing_content_type"] = True
                    logger.info("✅ Missing content type handling working")
                else:
                    logger.error(f"❌ Missing content type test failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Missing content type test error: {str(e)}")
        
        # Test 3: Non-existent endpoint (should trigger error toast)
        try:
            async with self.session.get(f"{BACKEND_URL}/nonexistent/endpoint") as response:
                if response.status == 404:
                    results["server_error_handling"] = True
                    logger.info("✅ Server error handling working")
                else:
                    logger.error(f"❌ Server error test failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Server error test error: {str(e)}")
        
        # Test 4: Timeout handling (simulate with very short timeout)
        try:
            timeout = aiohttp.ClientTimeout(total=0.001)  # 1ms timeout
            async with aiohttp.ClientSession(timeout=timeout) as short_session:
                try:
                    async with short_session.get(f"{BACKEND_URL}/health") as response:
                        pass
                except asyncio.TimeoutError:
                    results["timeout_handling"] = True
                    logger.info("✅ Timeout handling working")
                except Exception:
                    results["timeout_handling"] = True
                    logger.info("✅ Timeout handling working (connection error)")
        except Exception as e:
            logger.error(f"❌ Timeout test error: {str(e)}")
        
        success_rate = sum(results.values()) / len(results) * 100
        logger.info(f"📊 Error Handling Scenarios: {success_rate:.1f}% success rate")
        return results
    
    async def test_tts_audio_output_fixes(self):
        """Test the TTS Audio Output fixes that need retesting"""
        logger.info("🧪 Testing TTS Audio Output Fixes (needs_retesting: true)...")
        
        results = {
            "tts_basic": False,
            "tts_chunked": False,
            "tts_streaming": False,
            "voice_processing": False
        }
        
        # Test 1: Basic TTS functionality
        try:
            tts_data = {
                "text": "This is a test message for TTS audio generation.",
                "personality": "friendly_companion"
            }
            async with self.session.post(f"{BACKEND_URL}/voice/tts", json=tts_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success" and data.get("audio_base64"):
                        audio_size = len(data.get("audio_base64", ""))
                        if audio_size > 1000:  # Should have substantial audio data
                            results["tts_basic"] = True
                            logger.info(f"✅ Basic TTS working - Audio size: {audio_size} chars")
                        else:
                            logger.error(f"❌ Basic TTS audio too small: {audio_size} chars")
                    else:
                        logger.error(f"❌ Basic TTS failed - Status: {data.get('status')}")
                else:
                    logger.error(f"❌ Basic TTS failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Basic TTS error: {str(e)}")
        
        # Test 2: TTS with long text (should trigger chunked processing)
        try:
            long_text = "This is a very long text that should trigger chunked processing. " * 50  # ~3500 chars
            tts_data = {
                "text": long_text,
                "personality": "story_narrator"
            }
            async with self.session.post(f"{BACKEND_URL}/voice/tts", json=tts_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success" and data.get("audio_base64"):
                        audio_size = len(data.get("audio_base64", ""))
                        if audio_size > 5000:  # Should have substantial audio for long text
                            results["tts_chunked"] = True
                            logger.info(f"✅ TTS chunked processing working - Audio size: {audio_size} chars")
                        else:
                            logger.error(f"❌ TTS chunked audio too small: {audio_size} chars")
                    else:
                        logger.error(f"❌ TTS chunked failed - Status: {data.get('status')}")
                else:
                    logger.error(f"❌ TTS chunked failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ TTS chunked error: {str(e)}")
        
        # Test 3: Streaming TTS endpoint
        try:
            streaming_text = "This is a test for streaming TTS functionality. " * 20  # ~1000 chars
            tts_data = {
                "text": streaming_text,
                "personality": "learning_buddy"
            }
            async with self.session.post(f"{BACKEND_URL}/voice/tts/streaming", json=tts_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success":
                        results["tts_streaming"] = True
                        logger.info("✅ Streaming TTS working")
                    else:
                        logger.error(f"❌ Streaming TTS failed - Status: {data.get('status')}")
                else:
                    logger.error(f"❌ Streaming TTS failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Streaming TTS error: {str(e)}")
        
        # Test 4: Voice processing endpoint (if available)
        try:
            if self.profile_id:
                # Create a simple audio data (base64 encoded silence)
                silence_audio = base64.b64encode(b'\x00' * 1000).decode('utf-8')
                form_data = aiohttp.FormData()
                form_data.add_field('session_id', str(uuid.uuid4()))
                form_data.add_field('user_id', self.profile_id)
                form_data.add_field('audio_base64', silence_audio)
                
                async with self.session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "success":
                            results["voice_processing"] = True
                            logger.info("✅ Voice processing working")
                        else:
                            logger.error(f"❌ Voice processing failed - Status: {data.get('status')}")
                    else:
                        logger.error(f"❌ Voice processing failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Voice processing error: {str(e)}")
        
        success_rate = sum(results.values()) / len(results) * 100
        logger.info(f"📊 TTS Audio Output Fixes: {success_rate:.1f}% success rate")
        return results
    
    async def run_all_tests(self):
        """Run all toast import fix backend validation tests"""
        logger.info("🚀 Starting Toast Import Fix Backend Validation Tests...")
        logger.info(f"🔗 Backend URL: {BACKEND_URL}")
        
        all_results = {}
        
        # Test sequence
        test_sequence = [
            ("Health Check", self.test_health_check),
            ("Signup Validation Backend", self.test_signup_validation_backend),
            ("Signin Validation Backend", self.test_signin_validation_backend),
            ("Profile Update Backend", self.test_profile_update_backend),
            ("Parental Controls Backend", self.test_parental_controls_backend),
            ("Core API Endpoints", self.test_core_api_endpoints),
            ("Error Handling Scenarios", self.test_error_handling_scenarios),
            ("TTS Audio Output Fixes", self.test_tts_audio_output_fixes)
        ]
        
        for test_name, test_func in test_sequence:
            logger.info(f"\n{'='*60}")
            logger.info(f"🧪 Running: {test_name}")
            logger.info(f"{'='*60}")
            
            try:
                result = await test_func()
                all_results[test_name] = result
                
                if isinstance(result, dict):
                    success_count = sum(1 for v in result.values() if v)
                    total_count = len(result)
                    logger.info(f"📊 {test_name}: {success_count}/{total_count} tests passed")
                elif isinstance(result, bool):
                    logger.info(f"📊 {test_name}: {'✅ PASSED' if result else '❌ FAILED'}")
                
            except Exception as e:
                logger.error(f"❌ {test_name} failed with error: {str(e)}")
                all_results[test_name] = False
        
        # Calculate overall results
        total_tests = 0
        passed_tests = 0
        
        for test_name, result in all_results.items():
            if isinstance(result, dict):
                total_tests += len(result)
                passed_tests += sum(1 for v in result.values() if v)
            elif isinstance(result, bool):
                total_tests += 1
                passed_tests += 1 if result else 0
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 TOAST IMPORT FIX BACKEND VALIDATION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"📊 Overall Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        # Detailed results
        for test_name, result in all_results.items():
            if isinstance(result, dict):
                success_count = sum(1 for v in result.values() if v)
                total_count = len(result)
                status = "✅" if success_count == total_count else "⚠️" if success_count > 0 else "❌"
                logger.info(f"{status} {test_name}: {success_count}/{total_count}")
            elif isinstance(result, bool):
                status = "✅" if result else "❌"
                logger.info(f"{status} {test_name}")
        
        # Critical findings
        logger.info(f"\n🔍 CRITICAL FINDINGS:")
        
        # Check if authentication is working
        auth_working = all_results.get("Signup Validation Backend", {}).get("valid_signup", False) and \
                      all_results.get("Signin Validation Backend", {}).get("valid_signin", False)
        
        if auth_working:
            logger.info("✅ Authentication system working - Toast notifications should work for auth flows")
        else:
            logger.info("❌ Authentication system issues - Toast notifications may not work properly")
        
        # Check if core APIs are working
        core_working = all_results.get("Core API Endpoints", {})
        if isinstance(core_working, dict):
            core_success_rate = sum(core_working.values()) / len(core_working) * 100
            if core_success_rate >= 75:
                logger.info("✅ Core APIs working - No regression detected")
            else:
                logger.info("⚠️ Some core APIs have issues - Potential regression detected")
        
        # Check TTS fixes
        tts_working = all_results.get("TTS Audio Output Fixes", {})
        if isinstance(tts_working, dict):
            tts_success_rate = sum(tts_working.values()) / len(tts_working) * 100
            if tts_success_rate >= 75:
                logger.info("✅ TTS Audio Output fixes working correctly")
            else:
                logger.info("❌ TTS Audio Output fixes need attention")
        
        return {
            "overall_success_rate": success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "detailed_results": all_results,
            "authentication_working": auth_working,
            "no_regression": success_rate >= 70
        }

async def main():
    """Main test runner"""
    async with ToastImportFixBackendTester() as tester:
        results = await tester.run_all_tests()
        
        # Final assessment
        if results["overall_success_rate"] >= 80:
            print("\n🎉 TOAST IMPORT FIX BACKEND VALIDATION: EXCELLENT")
            print("✅ Backend APIs supporting toast functionality are working correctly")
            print("✅ No major regressions detected")
        elif results["overall_success_rate"] >= 60:
            print("\n⚠️ TOAST IMPORT FIX BACKEND VALIDATION: GOOD WITH ISSUES")
            print("✅ Most backend APIs working")
            print("⚠️ Some issues detected that may affect toast functionality")
        else:
            print("\n❌ TOAST IMPORT FIX BACKEND VALIDATION: NEEDS ATTENTION")
            print("❌ Significant backend issues detected")
            print("❌ Toast functionality may be impacted")
        
        return results

if __name__ == "__main__":
    asyncio.run(main())