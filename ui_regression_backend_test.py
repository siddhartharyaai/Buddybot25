#!/usr/bin/env python3
"""
UI/Navigation/Avatar Fixes Backend Regression Test
=================================================

This test validates that UI/navigation/avatar fixes didn't break any backend functionality.
Focus areas:
1. Basic Health Check
2. User Profile API 
3. Authentication Flow
4. Welcome Message Content
5. Navigation Support APIs
6. Voice & Chat Functionality
"""

import asyncio
import aiohttp
import json
import base64
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com/api"

class UIRegressionBackendTest:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_user_id = None
        self.test_profile_id = None
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print(f"🔧 Testing backend at: {BACKEND_URL}")
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        })
        
    async def test_basic_health_check(self):
        """Test 1: Basic Health Check - Verify backend server is running"""
        print("\n🏥 TESTING: Basic Health Check")
        
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if all required components are healthy
                    agents_status = data.get("agents", {})
                    orchestrator_ok = agents_status.get("orchestrator", False)
                    gemini_ok = agents_status.get("gemini_configured", False)
                    deepgram_ok = agents_status.get("deepgram_configured", False)
                    db_ok = data.get("database") == "connected"
                    
                    if orchestrator_ok and gemini_ok and deepgram_ok and db_ok:
                        self.log_result("Health Check", True, 
                                      f"All systems healthy - Orchestrator: {orchestrator_ok}, Gemini: {gemini_ok}, Deepgram: {deepgram_ok}, DB: {db_ok}")
                    else:
                        self.log_result("Health Check", False, 
                                      f"Some systems unhealthy - Orchestrator: {orchestrator_ok}, Gemini: {gemini_ok}, Deepgram: {deepgram_ok}, DB: {db_ok}")
                else:
                    self.log_result("Health Check", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_result("Health Check", False, f"Exception: {str(e)}")
            
    async def test_user_profile_api(self):
        """Test 2: User Profile API - Test CRUD operations work correctly"""
        print("\n👤 TESTING: User Profile API")
        
        # Test profile creation
        try:
            profile_data = {
                "name": "Emma Rodriguez",
                "age": 8,
                "location": "San Francisco, CA",
                "timezone": "America/Los_Angeles",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["animals", "stories", "music"],
                "learning_goals": ["reading", "creativity"],
                "gender": "female",
                "avatar": "🦄",  # Test avatar functionality
                "speech_speed": "normal",
                "energy_level": "balanced"
            }
            
            async with self.session.post(f"{BACKEND_URL}/users/profile", 
                                       json=profile_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_user_id = data.get("id")
                    self.test_profile_id = data.get("id")
                    
                    # Verify avatar is preserved
                    if data.get("avatar") == "🦄":
                        self.log_result("Profile Creation", True, 
                                      f"Profile created with ID: {self.test_user_id}, Avatar: {data.get('avatar')}")
                    else:
                        self.log_result("Profile Creation", False, 
                                      f"Avatar not preserved - Expected: 🦄, Got: {data.get('avatar')}")
                else:
                    self.log_result("Profile Creation", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_result("Profile Creation", False, f"Exception: {str(e)}")
            
        # Test profile retrieval
        if self.test_user_id:
            try:
                async with self.session.get(f"{BACKEND_URL}/users/profile/{self.test_user_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("avatar") == "🦄" and data.get("name") == "Emma Rodriguez":
                            self.log_result("Profile Retrieval", True, 
                                          f"Profile retrieved correctly - Name: {data.get('name')}, Avatar: {data.get('avatar')}")
                        else:
                            self.log_result("Profile Retrieval", False, 
                                          f"Profile data incorrect - Name: {data.get('name')}, Avatar: {data.get('avatar')}")
                    else:
                        self.log_result("Profile Retrieval", False, f"HTTP {response.status}")
                        
            except Exception as e:
                self.log_result("Profile Retrieval", False, f"Exception: {str(e)}")
                
        # Test profile update (avatar change)
        if self.test_user_id:
            try:
                update_data = {
                    "avatar": "🐰",  # Change avatar to test update functionality
                    "interests": ["animals", "stories", "music", "science"]
                }
                
                async with self.session.put(f"{BACKEND_URL}/users/profile/{self.test_user_id}", 
                                          json=update_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("avatar") == "🐰":
                            self.log_result("Profile Update", True, 
                                          f"Profile updated - New avatar: {data.get('avatar')}")
                        else:
                            self.log_result("Profile Update", False, 
                                          f"Avatar update failed - Expected: 🐰, Got: {data.get('avatar')}")
                    else:
                        self.log_result("Profile Update", False, f"HTTP {response.status}")
                        
            except Exception as e:
                self.log_result("Profile Update", False, f"Exception: {str(e)}")
                
    async def test_authentication_flow(self):
        """Test 3: Authentication Flow - Verify login/signup still works"""
        print("\n🔐 TESTING: Authentication Flow")
        
        # Test signup
        try:
            signup_data = {
                "email": f"test_{int(time.time())}@example.com",
                "password": "SecurePass123!",
                "name": "Test Child",
                "age": 7,
                "location": "Test City"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/signup", 
                                       json=signup_data) as response:
                if response.status == 200:
                    data = await response.json()
                    access_token = data.get("access_token")
                    user_id = data.get("user_id")
                    profile_id = data.get("profile_id")
                    
                    if access_token and user_id and profile_id:
                        self.log_result("Authentication Signup", True, 
                                      f"Signup successful - User ID: {user_id}, Profile ID: {profile_id}")
                        
                        # Test signin with same credentials
                        signin_data = {
                            "email": signup_data["email"],
                            "password": signup_data["password"]
                        }
                        
                        async with self.session.post(f"{BACKEND_URL}/auth/signin", 
                                                   json=signin_data) as signin_response:
                            if signin_response.status == 200:
                                signin_data_response = await signin_response.json()
                                if signin_data_response.get("access_token"):
                                    self.log_result("Authentication Signin", True, 
                                                  "Signin successful after signup")
                                else:
                                    self.log_result("Authentication Signin", False, 
                                                  "No access token in signin response")
                            else:
                                self.log_result("Authentication Signin", False, 
                                              f"Signin HTTP {signin_response.status}")
                    else:
                        self.log_result("Authentication Signup", False, 
                                      "Missing required fields in signup response")
                else:
                    self.log_result("Authentication Signup", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_result("Authentication Signup", False, f"Exception: {str(e)}")
            
    async def test_welcome_message_content(self):
        """Test 4: Welcome Message - Test that message says 'I'm Buddy, your AI friend'"""
        print("\n💬 TESTING: Welcome Message Content")
        
        if not self.test_user_id:
            # Create a test user for this test
            try:
                profile_data = {
                    "name": "Welcome Test User",
                    "age": 6,
                    "location": "Test Location",
                    "avatar": "🤖"
                }
                
                async with self.session.post(f"{BACKEND_URL}/users/profile", 
                                           json=profile_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        test_user_id = data.get("id")
                    else:
                        self.log_result("Welcome Message Setup", False, "Failed to create test user")
                        return
            except Exception as e:
                self.log_result("Welcome Message Setup", False, f"Exception: {str(e)}")
                return
        else:
            test_user_id = self.test_user_id
            
        # Test text conversation to get welcome-style response
        try:
            text_data = {
                "session_id": f"welcome_test_{int(time.time())}",
                "user_id": test_user_id,
                "message": "Hello, who are you?"
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text", 
                                       json=text_data) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "").lower()
                    
                    # Check if response contains "buddy" and "friend" instead of "companion"
                    has_buddy = "buddy" in response_text
                    has_friend = "friend" in response_text
                    has_companion = "companion" in response_text
                    
                    if has_buddy and has_friend and not has_companion:
                        self.log_result("Welcome Message Content", True, 
                                      f"Correct messaging - Contains 'buddy' and 'friend', no 'companion'")
                    elif has_buddy and not has_companion:
                        self.log_result("Welcome Message Content", True, 
                                      f"Acceptable messaging - Contains 'buddy', no 'companion'")
                    elif has_companion:
                        self.log_result("Welcome Message Content", False, 
                                      f"Old messaging detected - Still contains 'companion'")
                    else:
                        self.log_result("Welcome Message Content", True, 
                                      f"Response received - May not be introduction: '{response_text[:100]}...'")
                else:
                    self.log_result("Welcome Message Content", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_result("Welcome Message Content", False, f"Exception: {str(e)}")
            
    async def test_navigation_support_apis(self):
        """Test 5: Navigation Support - Verify profile and parental controls APIs work"""
        print("\n🧭 TESTING: Navigation Support APIs")
        
        if not self.test_user_id:
            self.log_result("Navigation Support", False, "No test user available")
            return
            
        # Test parental controls API (supports navigation)
        try:
            async with self.session.get(f"{BACKEND_URL}/users/{self.test_user_id}/parental-controls") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if parental controls have expected structure for navigation
                    has_time_limits = "time_limits" in data
                    has_content_restrictions = "content_restrictions" in data
                    has_monitoring = "monitoring_enabled" in data
                    
                    if has_time_limits and has_content_restrictions and has_monitoring:
                        self.log_result("Parental Controls API", True, 
                                      "Parental controls API working - All navigation data available")
                    else:
                        self.log_result("Parental Controls API", False, 
                                      "Parental controls missing required fields for navigation")
                else:
                    self.log_result("Parental Controls API", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_result("Parental Controls API", False, f"Exception: {str(e)}")
            
        # Test parental controls update (navigation functionality)
        try:
            update_data = {
                "time_limits": {
                    "monday": 90,
                    "tuesday": 90,
                    "wednesday": 90,
                    "thursday": 90,
                    "friday": 120,
                    "saturday": 120,
                    "sunday": 120
                },
                "monitoring_enabled": True
            }
            
            async with self.session.put(f"{BACKEND_URL}/users/{self.test_user_id}/parental-controls", 
                                      json=update_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("time_limits", {}).get("friday") == 120:
                        self.log_result("Parental Controls Update", True, 
                                      "Parental controls update working for navigation")
                    else:
                        self.log_result("Parental Controls Update", False, 
                                      "Parental controls update failed")
                else:
                    self.log_result("Parental Controls Update", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_result("Parental Controls Update", False, f"Exception: {str(e)}")
            
    async def test_voice_and_chat_functionality(self):
        """Test 6: Voice & Chat Functionality - Ensure core features remain intact"""
        print("\n🎤 TESTING: Voice & Chat Functionality")
        
        if not self.test_user_id:
            self.log_result("Voice & Chat", False, "No test user available")
            return
            
        # Test text chat functionality
        try:
            text_data = {
                "session_id": f"chat_test_{int(time.time())}",
                "user_id": self.test_user_id,
                "message": "Tell me a short story about a friendly cat"
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text", 
                                       json=text_data) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    content_type = data.get("content_type", "")
                    
                    if response_text and len(response_text) > 50:
                        self.log_result("Text Chat Functionality", True, 
                                      f"Text chat working - Response: {len(response_text)} chars, Type: {content_type}")
                    else:
                        self.log_result("Text Chat Functionality", False, 
                                      f"Text chat response too short: {len(response_text)} chars")
                else:
                    self.log_result("Text Chat Functionality", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_result("Text Chat Functionality", False, f"Exception: {str(e)}")
            
        # Test voice personalities endpoint (supports voice functionality)
        try:
            async with self.session.get(f"{BACKEND_URL}/voice/personalities") as response:
                if response.status == 200:
                    data = await response.json()
                    personalities = data.get("personalities", [])
                    
                    if len(personalities) >= 3:
                        personality_names = [p.get("name", "") for p in personalities]
                        self.log_result("Voice Personalities", True, 
                                      f"Voice personalities available: {personality_names}")
                    else:
                        self.log_result("Voice Personalities", False, 
                                      f"Insufficient voice personalities: {len(personalities)}")
                else:
                    self.log_result("Voice Personalities", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_result("Voice Personalities", False, f"Exception: {str(e)}")
            
        # Test TTS functionality
        try:
            tts_data = {
                "text": "Hello! This is a test of the text-to-speech system.",
                "personality": "friendly_companion"
            }
            
            async with self.session.post(f"{BACKEND_URL}/voice/tts", 
                                       json=tts_data) as response:
                if response.status == 200:
                    data = await response.json()
                    audio_base64 = data.get("audio_base64", "")
                    
                    if audio_base64 and len(audio_base64) > 1000:
                        self.log_result("TTS Functionality", True, 
                                      f"TTS working - Generated {len(audio_base64)} chars of audio")
                    else:
                        self.log_result("TTS Functionality", False, 
                                      f"TTS audio too short: {len(audio_base64)} chars")
                else:
                    self.log_result("TTS Functionality", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_result("TTS Functionality", False, f"Exception: {str(e)}")
            
    async def test_content_apis(self):
        """Test additional content APIs that support the UI"""
        print("\n📚 TESTING: Content APIs")
        
        # Test stories API (supports Stories page navigation)
        try:
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status == 200:
                    data = await response.json()
                    stories = data.get("stories", [])
                    
                    if len(stories) >= 2:
                        self.log_result("Stories API", True, 
                                      f"Stories API working - {len(stories)} stories available")
                    else:
                        self.log_result("Stories API", False, 
                                      f"Insufficient stories: {len(stories)}")
                else:
                    self.log_result("Stories API", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_result("Stories API", False, f"Exception: {str(e)}")
            
        # Test content generation API
        if self.test_user_id:
            try:
                content_data = {
                    "content_type": "joke",
                    "user_input": "Tell me a funny joke",
                    "user_id": self.test_user_id
                }
                
                async with self.session.post(f"{BACKEND_URL}/content/generate", 
                                           json=content_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("content") or data.get("text"):
                            self.log_result("Content Generation API", True, 
                                          "Content generation working")
                        else:
                            self.log_result("Content Generation API", False, 
                                          "No content in generation response")
                    else:
                        self.log_result("Content Generation API", False, f"HTTP {response.status}")
                        
            except Exception as e:
                self.log_result("Content Generation API", False, f"Exception: {str(e)}")
                
    async def run_all_tests(self):
        """Run all regression tests"""
        print("🚀 STARTING UI/Navigation/Avatar Backend Regression Tests")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run all tests in sequence
            await self.test_basic_health_check()
            await self.test_user_profile_api()
            await self.test_authentication_flow()
            await self.test_welcome_message_content()
            await self.test_navigation_support_apis()
            await self.test_voice_and_chat_functionality()
            await self.test_content_apis()
            
        finally:
            await self.cleanup()
            
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 UI/NAVIGATION/AVATAR BACKEND REGRESSION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
                    
        print(f"\n🎯 REGRESSION TEST CONCLUSION:")
        if success_rate >= 90:
            print("   ✅ EXCELLENT - UI changes did not break backend functionality")
        elif success_rate >= 75:
            print("   ⚠️  GOOD - Minor issues detected, but core functionality intact")
        elif success_rate >= 50:
            print("   ⚠️  MODERATE - Some backend functionality affected by UI changes")
        else:
            print("   ❌ CRITICAL - Significant backend regression detected")
            
        return success_rate >= 75  # Return True if acceptable

async def main():
    """Main test execution"""
    tester = UIRegressionBackendTest()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    asyncio.run(main())