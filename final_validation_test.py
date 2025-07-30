#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE VALIDATION - ALL CRITICAL FIXES
Testing the 3 critical issues that should now be resolved:
1. Story Generation Length (300+ words)
2. Voice Personalities Endpoint (HTTP 200)
3. Story Narration Endpoint UserProfile handling
"""

import requests
import json
import time
import base64
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://dfc58399-9814-411f-9cc5-6e9560883b27.preview.emergentagent.com/api"

class FinalValidationTester:
    def __init__(self):
        self.results = []
        self.test_user_id = "final_validation_user"
        
    def log_result(self, test_name, success, details, word_count=None):
        """Log test result with details"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "word_count": word_count
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        word_info = f" ({word_count} words)" if word_count else ""
        print(f"{status}: {test_name}{word_info}")
        print(f"   Details: {details}")
        print()

    def test_story_generation_length(self):
        """Test 1: Story Generation Length Validation (300+ words)"""
        print("🎯 TESTING STORY GENERATION LENGTH (300+ WORDS)")
        print("=" * 60)
        
        story_prompts = [
            "Tell me a complete story about a brave little mouse who goes on an adventure",
            "I want a full story about a magical treasure hunt in an enchanted forest",
            "Can you tell me a detailed story about a girl who can talk to animals",
            "Tell me a long story about friendship between two unlikely characters",
            "I need a complete adventure story with a beginning, middle, and end"
        ]
        
        successful_stories = 0
        total_word_count = 0
        
        for i, prompt in enumerate(story_prompts, 1):
            try:
                print(f"Testing story {i}/5: '{prompt[:50]}...'")
                
                response = requests.post(
                    f"{BACKEND_URL}/conversations/text",
                    json={
                        "session_id": f"story_test_{i}",
                        "user_id": self.test_user_id,
                        "message": prompt
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    story_text = data.get("response_text", "")
                    word_count = len(story_text.split())
                    total_word_count += word_count
                    
                    if word_count >= 300:
                        successful_stories += 1
                        self.log_result(f"Story Generation {i}", True, 
                                      f"Generated {word_count} words (meets 300+ requirement)", word_count)
                    else:
                        self.log_result(f"Story Generation {i}", False, 
                                      f"Only {word_count} words (below 300 requirement)", word_count)
                        print(f"   Story preview: {story_text[:200]}...")
                else:
                    self.log_result(f"Story Generation {i}", False, 
                                  f"HTTP {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                self.log_result(f"Story Generation {i}", False, f"Exception: {str(e)}")
        
        # Overall story generation assessment
        success_rate = (successful_stories / len(story_prompts)) * 100
        avg_word_count = total_word_count / len(story_prompts) if story_prompts else 0
        
        overall_success = successful_stories >= 3  # At least 60% success rate
        self.log_result("Story Generation Overall", overall_success, 
                       f"{successful_stories}/{len(story_prompts)} stories met 300+ words. "
                       f"Success rate: {success_rate:.1f}%. Average: {avg_word_count:.0f} words")

    def test_voice_personalities_endpoint(self):
        """Test 2: Voice Personalities Endpoint (HTTP 200 with data)"""
        print("🎯 TESTING VOICE PERSONALITIES ENDPOINT")
        print("=" * 60)
        
        try:
            response = requests.get(f"{BACKEND_URL}/voice/personalities", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has expected structure
                if isinstance(data, dict) and "personalities" in data:
                    personalities = data["personalities"]
                    if len(personalities) >= 3:
                        personality_names = [p.get("id", "unknown") for p in personalities]
                        self.log_result("Voice Personalities Endpoint", True, 
                                      f"HTTP 200 with {len(personalities)} personalities: {personality_names}")
                    else:
                        self.log_result("Voice Personalities Endpoint", False, 
                                      f"Only {len(personalities)} personalities found, expected 3+")
                elif isinstance(data, list) and len(data) >= 3:
                    personality_names = [p.get("id", "unknown") for p in data]
                    self.log_result("Voice Personalities Endpoint", True, 
                                  f"HTTP 200 with {len(data)} personalities: {personality_names}")
                else:
                    self.log_result("Voice Personalities Endpoint", False, 
                                  f"Unexpected response structure: {str(data)[:200]}")
            else:
                self.log_result("Voice Personalities Endpoint", False, 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_result("Voice Personalities Endpoint", False, f"Exception: {str(e)}")

    def test_story_narration_endpoint(self):
        """Test 3: Story Narration Endpoint UserProfile handling"""
        print("🎯 TESTING STORY NARRATION ENDPOINT")
        print("=" * 60)
        
        # First, get available stories
        try:
            stories_response = requests.get(f"{BACKEND_URL}/content/stories", timeout=10)
            if stories_response.status_code != 200:
                self.log_result("Story Narration - Get Stories", False, 
                              f"Could not fetch stories: HTTP {stories_response.status_code}")
                return
                
            stories_data = stories_response.json()
            stories = stories_data.get("stories", [])
            
            if not stories:
                self.log_result("Story Narration - Get Stories", False, "No stories available")
                return
                
            print(f"Found {len(stories)} stories available")
            
            # Test narration with different scenarios
            test_scenarios = [
                {"user_id": self.test_user_id, "description": "existing user profile"},
                {"user_id": "nonexistent_user_123", "description": "non-existing user profile"},
                {"user_id": "demo_kid", "description": "demo user profile"}
            ]
            
            successful_narrations = 0
            
            for i, scenario in enumerate(test_scenarios, 1):
                story_id = stories[0]["id"]  # Use first available story
                user_id = scenario["user_id"]
                description = scenario["description"]
                
                try:
                    print(f"Testing narration {i}/3: {description}")
                    
                    # Test story narration endpoint
                    narration_response = requests.post(
                        f"{BACKEND_URL}/content/stories/{story_id}/narrate",
                        data={"user_id": user_id},
                        timeout=30
                    )
                    
                    if narration_response.status_code == 200:
                        narration_data = narration_response.json()
                        response_text = narration_data.get("response_text", "")
                        response_audio = narration_data.get("response_audio", "")
                        
                        if response_text and response_audio:
                            successful_narrations += 1
                            word_count = len(response_text.split())
                            self.log_result(f"Story Narration {i}", True, 
                                          f"Success with {description}. Text: {word_count} words, "
                                          f"Audio: {len(response_audio)} chars", word_count)
                        elif response_text and not response_audio:
                            self.log_result(f"Story Narration {i}", False, 
                                          f"Text returned but no audio with {description}")
                        else:
                            self.log_result(f"Story Narration {i}", False, 
                                          f"Empty response_text and response_audio with {description}")
                    else:
                        error_text = narration_response.text[:300]
                        self.log_result(f"Story Narration {i}", False, 
                                      f"HTTP {narration_response.status_code} with {description}: {error_text}")
                        
                except Exception as e:
                    self.log_result(f"Story Narration {i}", False, 
                                  f"Exception with {description}: {str(e)}")
            
            # Overall narration assessment
            success_rate = (successful_narrations / len(test_scenarios)) * 100
            overall_success = successful_narrations >= 2  # At least 2/3 scenarios working
            
            self.log_result("Story Narration Overall", overall_success, 
                           f"{successful_narrations}/{len(test_scenarios)} scenarios successful. "
                           f"Success rate: {success_rate:.1f}%")
                           
        except Exception as e:
            self.log_result("Story Narration - Setup", False, f"Setup exception: {str(e)}")

    def test_integration_validation(self):
        """Test 4: End-to-end integration validation"""
        print("🎯 TESTING END-TO-END INTEGRATION")
        print("=" * 60)
        
        try:
            # Test health check
            health_response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if health_response.status_code == 200:
                health_data = health_response.json()
                agents_status = health_data.get("agents", {})
                self.log_result("Health Check", True, 
                              f"System healthy. Orchestrator: {agents_status.get('orchestrator')}, "
                              f"Gemini: {agents_status.get('gemini_configured')}, "
                              f"Deepgram: {agents_status.get('deepgram_configured')}")
            else:
                self.log_result("Health Check", False, f"HTTP {health_response.status_code}")
                
            # Test user profile creation
            profile_data = {
                "name": "Final Validation User",
                "age": 8,
                "language": "english",
                "location": "Test City",
                "parent_email": "test@example.com",
                "preferences": {
                    "voice_personality": "story_narrator",
                    "learning_goals": ["creativity"],
                    "favorite_topics": ["adventures"]
                }
            }
            
            profile_response = requests.post(
                f"{BACKEND_URL}/users/profile",
                json=profile_data,
                timeout=10
            )
            
            if profile_response.status_code == 200:
                self.log_result("User Profile Creation", True, "Profile created successfully")
            else:
                self.log_result("User Profile Creation", False, 
                              f"HTTP {profile_response.status_code}: {profile_response.text[:200]}")
                
        except Exception as e:
            self.log_result("Integration Validation", False, f"Exception: {str(e)}")

    def run_comprehensive_validation(self):
        """Run all validation tests"""
        print("🚀 FINAL COMPREHENSIVE VALIDATION - ALL CRITICAL FIXES")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User ID: {self.test_user_id}")
        print(f"Start Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Run all tests
        self.test_story_generation_length()
        self.test_voice_personalities_endpoint()
        self.test_story_narration_endpoint()
        self.test_integration_validation()
        
        # Generate final summary
        self.generate_final_summary()

    def generate_final_summary(self):
        """Generate comprehensive test summary"""
        print("🎯 FINAL COMPREHENSIVE VALIDATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical issues assessment
        story_generation_working = any(r["success"] and "Story Generation Overall" in r["test"] for r in self.results)
        voice_personalities_working = any(r["success"] and "Voice Personalities Endpoint" in r["test"] for r in self.results)
        story_narration_working = any(r["success"] and "Story Narration Overall" in r["test"] for r in self.results)
        
        print("CRITICAL ISSUES STATUS:")
        print(f"✅ Story Generation Length (300+ words): {'FIXED' if story_generation_working else 'STILL BROKEN'}")
        print(f"✅ Voice Personalities Endpoint: {'FIXED' if voice_personalities_working else 'STILL BROKEN'}")
        print(f"✅ Story Narration UserProfile handling: {'FIXED' if story_narration_working else 'STILL BROKEN'}")
        print()
        
        # Detailed results
        print("DETAILED TEST RESULTS:")
        print("-" * 40)
        for result in self.results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            word_info = f" ({result['word_count']} words)" if result.get("word_count") else ""
            print(f"{status}: {result['test']}{word_info}")
            print(f"   {result['details']}")
            print()
        
        # Final assessment
        critical_fixes_count = sum([story_generation_working, voice_personalities_working, story_narration_working])
        
        if critical_fixes_count == 3:
            print("🎉 ALL CRITICAL FIXES CONFIRMED WORKING!")
            print("The Buddy app's core functionality is operational.")
        elif critical_fixes_count >= 2:
            print("⚠️  PARTIAL SUCCESS - Most critical fixes working")
            print("Some issues remain but core functionality is largely operational.")
        else:
            print("❌ CRITICAL FAILURES REMAIN")
            print("Major backend issues still need to be resolved.")
        
        print("=" * 80)
        return success_rate >= 90

if __name__ == "__main__":
    tester = FinalValidationTester()
    tester.run_comprehensive_validation()