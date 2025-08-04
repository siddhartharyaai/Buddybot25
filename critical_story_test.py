#!/usr/bin/env python3
"""
CRITICAL STORY GENERATION AND NARRATION TESTING
Focus on the three critical issues identified in test_result.md:
1. Story generation length (300+ words requirement)
2. Story narration endpoint failures 
3. Voice personalities endpoint failures
"""

import requests
import json
import time
import base64
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com/api"

class CriticalBackendTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.session.timeout = 30
        
    def log_result(self, test_name, success, details, word_count=None):
        """Log test result with details"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "word_count": word_count
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        word_info = f" ({word_count} words)" if word_count else ""
        print(f"{status}: {test_name}{word_info}")
        print(f"   Details: {details}")
        
    def test_health_check(self):
        """Test basic health check"""
        try:
            response = self.session.get(f"{self.backend_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_result("Health Check", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_story_generation_length(self):
        """CRITICAL TEST 1: Test story generation length (300+ words requirement)"""
        print("\n🎯 CRITICAL TEST 1: STORY GENERATION LENGTH")
        
        story_prompts = [
            "Tell me a story about a brave little mouse",
            "Can you tell me a complete adventure story?", 
            "I want a long story with a beginning, middle, and end",
            "Tell me a story about a magical forest adventure",
            "Can you create a story about friendship and courage?"
        ]
        
        total_tests = len(story_prompts)
        passed_tests = 0
        
        for i, prompt in enumerate(story_prompts, 1):
            try:
                print(f"\n📝 Story Test {i}/{total_tests}: '{prompt}'")
                
                payload = {
                    "session_id": f"story_test_{i}_{int(time.time())}",
                    "user_id": "test_user_story",
                    "message": prompt
                }
                
                response = self.session.post(
                    f"{self.backend_url}/conversations/text",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    story_text = data.get("response_text", "")
                    word_count = len(story_text.split())
                    
                    # Check if story meets 300+ word requirement
                    meets_requirement = word_count >= 300
                    
                    if meets_requirement:
                        passed_tests += 1
                        self.log_result(f"Story Generation Test {i}", True, 
                                      f"Story generated with {word_count} words (meets 300+ requirement)", word_count)
                    else:
                        self.log_result(f"Story Generation Test {i}", False, 
                                      f"Story only {word_count} words (below 300 requirement)", word_count)
                        print(f"   Story preview: {story_text[:200]}...")
                        
                else:
                    self.log_result(f"Story Generation Test {i}", False, 
                                  f"HTTP {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                self.log_result(f"Story Generation Test {i}", False, f"Exception: {str(e)}")
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n📊 STORY GENERATION SUMMARY: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        return passed_tests > 0
    
    def test_story_narration_endpoint(self):
        """CRITICAL TEST 2: Test story narration endpoint (HTTP 500 UserProfile error)"""
        print("\n🎯 CRITICAL TEST 2: STORY NARRATION ENDPOINT")
        
        # First get available stories
        try:
            stories_response = self.session.get(f"{self.backend_url}/content/stories")
            if stories_response.status_code != 200:
                self.log_result("Get Stories", False, f"HTTP {stories_response.status_code}")
                return False
                
            stories_data = stories_response.json()
            stories = stories_data.get("stories", [])
            
            if not stories:
                self.log_result("Get Stories", False, "No stories available")
                return False
                
            self.log_result("Get Stories", True, f"Found {len(stories)} stories")
            
        except Exception as e:
            self.log_result("Get Stories", False, f"Exception: {str(e)}")
            return False
        
        # Test narration for each story
        total_tests = min(len(stories), 5)  # Test up to 5 stories
        passed_tests = 0
        
        for i, story in enumerate(stories[:total_tests], 1):
            story_id = story.get("id", f"story_{i}")
            story_title = story.get("title", "Unknown Story")
            
            try:
                print(f"\n📖 Narration Test {i}/{total_tests}: '{story_title}' (ID: {story_id})")
                
                # Test story narration endpoint
                narration_data = {
                    "user_id": "test_user_narration"
                }
                
                response = self.session.post(
                    f"{self.backend_url}/content/stories/{story_id}/narrate",
                    data=narration_data  # Using form data as expected by endpoint
                )
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("response_text", "")
                    response_audio = data.get("response_audio", "")
                    
                    # Check if we got proper response
                    if response_text and response_audio:
                        passed_tests += 1
                        word_count = len(response_text.split())
                        self.log_result(f"Story Narration Test {i}", True, 
                                      f"Narration successful: {word_count} words, audio: {len(response_audio)} chars", word_count)
                    else:
                        self.log_result(f"Story Narration Test {i}", False, 
                                      f"Empty response - text: '{response_text}', audio: '{response_audio}'")
                        print(f"   Full response: {json.dumps(data, indent=2)}")
                        
                else:
                    error_text = response.text[:500] if response.text else "No error details"
                    self.log_result(f"Story Narration Test {i}", False, 
                                  f"HTTP {response.status_code}: {error_text}")
                    
            except Exception as e:
                self.log_result(f"Story Narration Test {i}", False, f"Exception: {str(e)}")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"\n📊 STORY NARRATION SUMMARY: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        return passed_tests > 0
    
    def test_voice_personalities_endpoint(self):
        """CRITICAL TEST 3: Test voice personalities endpoint (HTTP 500 error)"""
        print("\n🎯 CRITICAL TEST 3: VOICE PERSONALITIES ENDPOINT")
        
        try:
            response = self.session.get(f"{self.backend_url}/voice/personalities")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we got personality data
                if isinstance(data, (list, dict)) and data:
                    personality_count = len(data) if isinstance(data, list) else len(data.keys())
                    self.log_result("Voice Personalities", True, 
                                  f"Retrieved {personality_count} voice personalities")
                    print(f"   Personalities: {json.dumps(data, indent=2)}")
                    return True
                else:
                    self.log_result("Voice Personalities", False, "Empty or invalid personality data")
                    return False
                    
            else:
                error_text = response.text[:500] if response.text else "No error details"
                self.log_result("Voice Personalities", False, 
                              f"HTTP {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_result("Voice Personalities", False, f"Exception: {str(e)}")
            return False
    
    def test_iterative_story_generation(self):
        """ADDITIONAL TEST: Test iterative story generation system"""
        print("\n🔄 ADDITIONAL TEST: ITERATIVE STORY GENERATION SYSTEM")
        
        try:
            # Test with explicit request for long story
            payload = {
                "session_id": f"iterative_test_{int(time.time())}",
                "user_id": "test_user_iterative",
                "message": "Please tell me a complete, detailed story with at least 300 words about a young explorer who discovers a hidden magical kingdom. Include a beginning, middle with challenges, and a satisfying ending."
            }
            
            response = self.session.post(
                f"{self.backend_url}/conversations/text",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                story_text = data.get("response_text", "")
                word_count = len(story_text.split())
                
                # Analyze story structure
                has_beginning = any(word in story_text.lower() for word in ["once", "long ago", "there was", "in a"])
                has_middle = len(story_text.split('.')) >= 5  # At least 5 sentences
                has_ending = any(word in story_text.lower() for word in ["end", "finally", "happily", "conclusion"])
                
                structure_score = sum([has_beginning, has_middle, has_ending])
                
                if word_count >= 300 and structure_score >= 2:
                    self.log_result("Iterative Story Generation", True, 
                                  f"Complete story: {word_count} words, structure score: {structure_score}/3", word_count)
                    return True
                else:
                    self.log_result("Iterative Story Generation", False, 
                                  f"Incomplete story: {word_count} words, structure score: {structure_score}/3", word_count)
                    print(f"   Story preview: {story_text[:300]}...")
                    return False
                    
            else:
                self.log_result("Iterative Story Generation", False, 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_result("Iterative Story Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_user_profile_handling(self):
        """ADDITIONAL TEST: Test UserProfile object handling"""
        print("\n👤 ADDITIONAL TEST: USER PROFILE HANDLING")
        
        try:
            # Test creating a user profile
            profile_data = {
                "name": "Test Child",
                "age": 8,
                "language": "english",
                "preferences": {
                    "voice_personality": "friendly_companion",
                    "learning_goals": ["storytelling"],
                    "favorite_topics": ["adventure", "animals"]
                }
            }
            
            response = self.session.post(
                f"{self.backend_url}/users/profile",
                json=profile_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get("id")
                
                if user_id:
                    self.log_result("User Profile Creation", True, f"Created profile with ID: {user_id}")
                    
                    # Test retrieving the profile
                    get_response = self.session.get(f"{self.backend_url}/users/profile/{user_id}")
                    
                    if get_response.status_code == 200:
                        self.log_result("User Profile Retrieval", True, "Profile retrieved successfully")
                        return True
                    else:
                        self.log_result("User Profile Retrieval", False, f"HTTP {get_response.status_code}")
                        return False
                else:
                    self.log_result("User Profile Creation", False, "No user ID returned")
                    return False
                    
            else:
                self.log_result("User Profile Creation", False, 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_result("User Profile Handling", False, f"Exception: {str(e)}")
            return False
    
    def run_critical_tests(self):
        """Run all critical tests focusing on the three main issues"""
        print("🚨 CRITICAL STORY GENERATION AND NARRATION TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Test 1: Health check
        health_ok = self.test_health_check()
        
        if not health_ok:
            print("\n❌ CRITICAL: Backend health check failed. Cannot proceed with tests.")
            return False
        
        # Test 2: Story generation length (CRITICAL ISSUE 1)
        story_generation_ok = self.test_story_generation_length()
        
        # Test 3: Story narration endpoint (CRITICAL ISSUE 2)  
        story_narration_ok = self.test_story_narration_endpoint()
        
        # Test 4: Voice personalities endpoint (CRITICAL ISSUE 3)
        voice_personalities_ok = self.test_voice_personalities_endpoint()
        
        # Additional tests
        iterative_story_ok = self.test_iterative_story_generation()
        user_profile_ok = self.test_user_profile_handling()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 CRITICAL TESTING SUMMARY")
        print("=" * 60)
        
        critical_tests = [
            ("Story Generation Length (300+ words)", story_generation_ok),
            ("Story Narration Endpoint", story_narration_ok),
            ("Voice Personalities Endpoint", voice_personalities_ok)
        ]
        
        additional_tests = [
            ("Iterative Story Generation", iterative_story_ok),
            ("User Profile Handling", user_profile_ok)
        ]
        
        critical_passed = sum(1 for _, passed in critical_tests if passed)
        additional_passed = sum(1 for _, passed in additional_tests if passed)
        
        print(f"\n🚨 CRITICAL ISSUES ({critical_passed}/3 RESOLVED):")
        for test_name, passed in critical_tests:
            status = "✅ RESOLVED" if passed else "❌ FAILING"
            print(f"   {status}: {test_name}")
        
        print(f"\n🔍 ADDITIONAL VALIDATION ({additional_passed}/2 PASSED):")
        for test_name, passed in additional_tests:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status}: {test_name}")
        
        overall_success_rate = ((critical_passed + additional_passed) / 5) * 100
        print(f"\n📊 OVERALL SUCCESS RATE: {overall_success_rate:.1f}%")
        
        # Detailed findings
        print(f"\n📋 DETAILED FINDINGS:")
        failed_tests = [result for result in self.test_results if not result["success"]]
        
        if failed_tests:
            print(f"   ❌ {len(failed_tests)} tests failed:")
            for result in failed_tests:
                print(f"      - {result['test']}: {result['details']}")
        else:
            print("   ✅ All tests passed!")
        
        return critical_passed >= 2  # At least 2 out of 3 critical issues should be resolved

if __name__ == "__main__":
    tester = CriticalBackendTester()
    success = tester.run_critical_tests()
    
    if success:
        print("\n🎉 TESTING COMPLETED WITH ACCEPTABLE RESULTS")
    else:
        print("\n⚠️ TESTING COMPLETED WITH CRITICAL ISSUES REMAINING")
    
    exit(0 if success else 1)