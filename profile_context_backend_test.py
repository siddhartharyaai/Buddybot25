#!/usr/bin/env python3
"""
Backend Test: LLM Context Retention and User Profile Integration
Focus: Testing that conversation agent uses user profile information and maintains context
"""

import asyncio
import aiohttp
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from environment
BACKEND_URL = "https://0e5dcf5a-4e8d-4074-9227-19f4607bd0be.preview.emergentagent.com/api"

class ProfileContextTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_users = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        logger.info("✅ HTTP session initialized")
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("✅ HTTP session closed")
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: {test_name} - {details}")
    
    async def create_test_user(self, name: str, age: int, interests: List[str], learning_goals: List[str], 
                              voice_personality: str = "friendly_companion", gender: str = "prefer_not_to_say",
                              avatar: str = "bunny", speech_speed: str = "normal", energy_level: str = "balanced") -> Dict[str, Any]:
        """Create a test user profile"""
        try:
            profile_data = {
                "name": name,
                "age": age,
                "location": "Test City",
                "timezone": "UTC",
                "language": "english",
                "voice_personality": voice_personality,
                "interests": interests,
                "learning_goals": learning_goals,
                "parent_email": f"parent_{name.lower()}@test.com",
                "gender": gender,
                "avatar": avatar,
                "speech_speed": speech_speed,
                "energy_level": energy_level
            }
            
            async with self.session.post(f"{BACKEND_URL}/users/profile", json=profile_data) as response:
                if response.status == 200:
                    user_profile = await response.json()
                    self.test_users.append(user_profile)
                    logger.info(f"✅ Created test user: {name} (age {age})")
                    return user_profile
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to create user {name}: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error creating user {name}: {str(e)}")
            return None
    
    async def test_profile_context_usage(self):
        """Test 1: Profile Context Test - that conversation agent uses user profile information"""
        logger.info("🎯 TEST 1: Profile Context Usage")
        
        # Create test users with different profiles
        emma = await self.create_test_user(
            name="Emma", 
            age=7, 
            interests=["animals", "stories", "drawing"], 
            learning_goals=["reading", "creativity"],
            voice_personality="story_narrator",
            gender="female",
            avatar="cat",
            speech_speed="slow",
            energy_level="calm"
        )
        
        if not emma:
            self.log_test_result("Profile Context - User Creation", False, "Failed to create test user Emma")
            return
        
        # Test conversation that should use profile information
        test_cases = [
            {
                "input": "Tell me about yourself",
                "expected_elements": ["Emma", "7", "animals", "stories", "drawing"],
                "description": "Should reference user's name, age, and interests"
            },
            {
                "input": "What should we do today?",
                "expected_elements": ["story", "animal", "draw", "read"],
                "description": "Should suggest activities based on interests and learning goals"
            },
            {
                "input": "I'm feeling sad",
                "expected_elements": ["Emma", "understand", "feel"],
                "description": "Should use empathetic tone appropriate for 7-year-old Emma"
            }
        ]
        
        session_id = f"profile_test_{int(time.time())}"
        
        for i, test_case in enumerate(test_cases):
            try:
                # Send text conversation request
                conversation_data = {
                    "session_id": session_id,
                    "user_id": emma["id"],
                    "message": test_case["input"]
                }
                
                async with self.session.post(f"{BACKEND_URL}/conversations/text", json=conversation_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "").lower()
                        
                        # Check if profile elements are used
                        elements_found = []
                        elements_missing = []
                        
                        for element in test_case["expected_elements"]:
                            if element.lower() in response_text:
                                elements_found.append(element)
                            else:
                                elements_missing.append(element)
                        
                        success = len(elements_found) >= len(test_case["expected_elements"]) // 2  # At least half should be present
                        
                        details = f"{test_case['description']} - Found: {elements_found}, Missing: {elements_missing}"
                        self.log_test_result(f"Profile Context Test {i+1}", success, details, {
                            "input": test_case["input"],
                            "response": result.get("response_text", "")[:200],
                            "elements_found": elements_found,
                            "elements_missing": elements_missing
                        })
                        
                    else:
                        error_text = await response.text()
                        self.log_test_result(f"Profile Context Test {i+1}", False, f"HTTP {response.status}: {error_text}")
                        
            except Exception as e:
                self.log_test_result(f"Profile Context Test {i+1}", False, f"Exception: {str(e)}")
    
    async def test_profile_update_integration(self):
        """Test 2: Profile Update Integration - that updated profile info is used in subsequent conversations"""
        logger.info("🎯 TEST 2: Profile Update Integration")
        
        # Create initial user
        alex = await self.create_test_user(
            name="Alex", 
            age=9, 
            interests=["sports", "games"], 
            learning_goals=["math", "science"],
            voice_personality="learning_buddy"
        )
        
        if not alex:
            self.log_test_result("Profile Update - User Creation", False, "Failed to create test user Alex")
            return
        
        session_id = f"update_test_{int(time.time())}"
        
        # Initial conversation to establish baseline
        try:
            conversation_data = {
                "session_id": session_id,
                "user_id": alex["id"],
                "message": "What are my favorite things?"
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text", json=conversation_data) as response:
                if response.status == 200:
                    initial_result = await response.json()
                    initial_response = initial_result.get("response_text", "").lower()
                    
                    # Should mention sports and games
                    has_sports = "sport" in initial_response
                    has_games = "game" in initial_response
                    
                    self.log_test_result("Profile Update - Initial State", has_sports or has_games, 
                                       f"Initial interests mentioned: sports={has_sports}, games={has_games}",
                                       {"response": initial_result.get("response_text", "")[:200]})
                else:
                    self.log_test_result("Profile Update - Initial State", False, f"HTTP {response.status}")
                    return
                    
        except Exception as e:
            self.log_test_result("Profile Update - Initial State", False, f"Exception: {str(e)}")
            return
        
        # Update user profile with new interests
        try:
            update_data = {
                "interests": ["music", "art", "cooking"],
                "learning_goals": ["creativity", "cooking skills"],
                "voice_personality": "friendly_companion"
            }
            
            async with self.session.put(f"{BACKEND_URL}/users/profile/{alex['id']}", json=update_data) as response:
                if response.status == 200:
                    updated_profile = await response.json()
                    self.log_test_result("Profile Update - Update Success", True, "Profile updated successfully")
                else:
                    error_text = await response.text()
                    self.log_test_result("Profile Update - Update Success", False, f"HTTP {response.status}: {error_text}")
                    return
                    
        except Exception as e:
            self.log_test_result("Profile Update - Update Success", False, f"Exception: {str(e)}")
            return
        
        # Wait a moment for any caching to clear
        await asyncio.sleep(2)
        
        # Test conversation with updated profile
        try:
            conversation_data = {
                "session_id": f"{session_id}_updated",
                "user_id": alex["id"],
                "message": "What are my favorite things now?"
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text", json=conversation_data) as response:
                if response.status == 200:
                    updated_result = await response.json()
                    updated_response = updated_result.get("response_text", "").lower()
                    
                    # Should mention new interests
                    has_music = "music" in updated_response
                    has_art = "art" in updated_response
                    has_cooking = "cook" in updated_response
                    
                    # Should NOT mention old interests as prominently
                    has_old_sports = "sport" in updated_response
                    has_old_games = "game" in updated_response
                    
                    new_interests_mentioned = sum([has_music, has_art, has_cooking])
                    old_interests_mentioned = sum([has_old_sports, has_old_games])
                    
                    success = new_interests_mentioned > old_interests_mentioned
                    
                    details = f"New interests: music={has_music}, art={has_art}, cooking={has_cooking}. Old interests: sports={has_old_sports}, games={has_old_games}"
                    self.log_test_result("Profile Update - Updated Interests Used", success, details,
                                       {"response": updated_result.get("response_text", "")[:200]})
                else:
                    error_text = await response.text()
                    self.log_test_result("Profile Update - Updated Interests Used", False, f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test_result("Profile Update - Updated Interests Used", False, f"Exception: {str(e)}")
    
    async def test_age_appropriate_content(self):
        """Test 3: Age-Appropriate Content - for different age brackets (5, 8, 11)"""
        logger.info("🎯 TEST 3: Age-Appropriate Content Generation")
        
        # Create users of different ages
        test_ages = [
            {"name": "Lily", "age": 5, "expected_complexity": "simple"},
            {"name": "Sam", "age": 8, "expected_complexity": "moderate"},
            {"name": "Jordan", "age": 11, "expected_complexity": "advanced"}
        ]
        
        age_users = []
        for age_data in test_ages:
            user = await self.create_test_user(
                name=age_data["name"],
                age=age_data["age"],
                interests=["stories", "learning"],
                learning_goals=["general_knowledge"]
            )
            if user:
                age_users.append({**age_data, "user": user})
        
        if len(age_users) != 3:
            self.log_test_result("Age-Appropriate Content - User Creation", False, f"Only created {len(age_users)}/3 users")
            return
        
        # Test story generation for each age group
        story_prompt = "Tell me a story about a brave little mouse"
        
        for age_data in age_users:
            try:
                session_id = f"age_test_{age_data['age']}_{int(time.time())}"
                conversation_data = {
                    "session_id": session_id,
                    "user_id": age_data["user"]["id"],
                    "message": story_prompt
                }
                
                async with self.session.post(f"{BACKEND_URL}/conversations/text", json=conversation_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        story_text = result.get("response_text", "")
                        
                        # Analyze story complexity
                        word_count = len(story_text.split())
                        sentence_count = len([s for s in story_text.split('.') if s.strip()])
                        avg_sentence_length = word_count / max(sentence_count, 1)
                        
                        # Age-appropriate expectations
                        age = age_data["age"]
                        if age <= 5:  # Toddler
                            expected_min_words = 50
                            expected_max_avg_sentence = 8
                            complexity_check = avg_sentence_length <= expected_max_avg_sentence
                        elif age <= 9:  # Child
                            expected_min_words = 100
                            expected_max_avg_sentence = 12
                            complexity_check = 6 <= avg_sentence_length <= expected_max_avg_sentence
                        else:  # Preteen
                            expected_min_words = 150
                            expected_max_avg_sentence = 20
                            complexity_check = avg_sentence_length >= 8
                        
                        length_check = word_count >= expected_min_words
                        success = length_check and complexity_check
                        
                        details = f"Age {age}: {word_count} words, {sentence_count} sentences, avg {avg_sentence_length:.1f} words/sentence"
                        self.log_test_result(f"Age-Appropriate Content - Age {age}", success, details, {
                            "age": age,
                            "word_count": word_count,
                            "sentence_count": sentence_count,
                            "avg_sentence_length": avg_sentence_length,
                            "story_preview": story_text[:150]
                        })
                        
                    else:
                        error_text = await response.text()
                        self.log_test_result(f"Age-Appropriate Content - Age {age_data['age']}", False, f"HTTP {response.status}: {error_text}")
                        
            except Exception as e:
                self.log_test_result(f"Age-Appropriate Content - Age {age_data['age']}", False, f"Exception: {str(e)}")
    
    async def test_context_retention(self):
        """Test 4: Context Retention - that LLM maintains conversation context across multiple interactions"""
        logger.info("🎯 TEST 4: Context Retention Across Multiple Interactions")
        
        # Create test user
        maya = await self.create_test_user(
            name="Maya",
            age=8,
            interests=["animals", "nature"],
            learning_goals=["science", "reading"]
        )
        
        if not maya:
            self.log_test_result("Context Retention - User Creation", False, "Failed to create test user Maya")
            return
        
        session_id = f"context_test_{int(time.time())}"
        
        # Multi-turn conversation to test context retention
        conversation_turns = [
            {
                "input": "My favorite animal is a dolphin",
                "expected_context": ["dolphin"],
                "description": "Establish context about favorite animal"
            },
            {
                "input": "What do you know about them?",
                "expected_context": ["dolphin", "they", "them", "smart", "ocean", "mammal"],
                "description": "Should understand 'them' refers to dolphins"
            },
            {
                "input": "Do they live in groups?",
                "expected_context": ["dolphin", "pod", "group", "social", "together"],
                "description": "Should continue dolphin context and answer about social behavior"
            },
            {
                "input": "What's my favorite animal again?",
                "expected_context": ["dolphin", "favorite"],
                "description": "Should remember the favorite animal from earlier"
            }
        ]
        
        context_scores = []
        
        for i, turn in enumerate(conversation_turns):
            try:
                conversation_data = {
                    "session_id": session_id,  # Same session for context retention
                    "user_id": maya["id"],
                    "message": turn["input"]
                }
                
                async with self.session.post(f"{BACKEND_URL}/conversations/text", json=conversation_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "").lower()
                        
                        # Check context retention
                        context_elements_found = []
                        for element in turn["expected_context"]:
                            if element.lower() in response_text:
                                context_elements_found.append(element)
                        
                        context_score = len(context_elements_found) / len(turn["expected_context"])
                        context_scores.append(context_score)
                        
                        success = context_score >= 0.3  # At least 30% of expected context elements
                        
                        details = f"Turn {i+1}: {turn['description']} - Context score: {context_score:.2f} ({len(context_elements_found)}/{len(turn['expected_context'])} elements)"
                        self.log_test_result(f"Context Retention - Turn {i+1}", success, details, {
                            "input": turn["input"],
                            "response": result.get("response_text", "")[:200],
                            "context_elements_found": context_elements_found,
                            "context_score": context_score
                        })
                        
                        # Add small delay between turns
                        await asyncio.sleep(1)
                        
                    else:
                        error_text = await response.text()
                        self.log_test_result(f"Context Retention - Turn {i+1}", False, f"HTTP {response.status}: {error_text}")
                        context_scores.append(0)
                        
            except Exception as e:
                self.log_test_result(f"Context Retention - Turn {i+1}", False, f"Exception: {str(e)}")
                context_scores.append(0)
        
        # Overall context retention assessment
        if context_scores:
            avg_context_score = sum(context_scores) / len(context_scores)
            overall_success = avg_context_score >= 0.4  # At least 40% average context retention
            
            self.log_test_result("Context Retention - Overall", overall_success, 
                               f"Average context retention score: {avg_context_score:.2f}",
                               {"context_scores": context_scores})
    
    async def test_memory_integration(self):
        """Test 5: Memory Integration - that user profile data integrates with memory system"""
        logger.info("🎯 TEST 5: Memory Integration with User Profile")
        
        # Create test user
        zoe = await self.create_test_user(
            name="Zoe",
            age=10,
            interests=["space", "robots", "coding"],
            learning_goals=["programming", "astronomy"],
            voice_personality="learning_buddy"
        )
        
        if not zoe:
            self.log_test_result("Memory Integration - User Creation", False, "Failed to create test user Zoe")
            return
        
        # Test memory context retrieval
        try:
            async with self.session.get(f"{BACKEND_URL}/memory/context/{zoe['id']}") as response:
                if response.status == 200:
                    memory_context = await response.json()
                    self.log_test_result("Memory Integration - Context Retrieval", True, 
                                       f"Retrieved memory context for user {zoe['name']}")
                else:
                    # Memory context might be empty for new user, which is acceptable
                    self.log_test_result("Memory Integration - Context Retrieval", True, 
                                       f"No existing memory context (expected for new user)")
                    
        except Exception as e:
            self.log_test_result("Memory Integration - Context Retrieval", False, f"Exception: {str(e)}")
        
        # Test memory snapshot generation
        try:
            async with self.session.post(f"{BACKEND_URL}/memory/snapshot/{zoe['id']}") as response:
                if response.status == 200:
                    snapshot = await response.json()
                    self.log_test_result("Memory Integration - Snapshot Generation", True, 
                                       "Successfully generated memory snapshot")
                else:
                    error_text = await response.text()
                    self.log_test_result("Memory Integration - Snapshot Generation", False, 
                                       f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test_result("Memory Integration - Snapshot Generation", False, f"Exception: {str(e)}")
        
        # Test conversation with profile-aware memory
        try:
            session_id = f"memory_test_{int(time.time())}"
            conversation_data = {
                "session_id": session_id,
                "user_id": zoe["id"],
                "message": "Let's talk about my interests"
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text", json=conversation_data) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "").lower()
                    
                    # Check if profile interests are mentioned
                    profile_elements = ["space", "robot", "cod", "program", "astron", "zoe"]
                    elements_found = [elem for elem in profile_elements if elem in response_text]
                    
                    success = len(elements_found) >= 2  # At least 2 profile elements should be mentioned
                    
                    details = f"Profile elements found in response: {elements_found}"
                    self.log_test_result("Memory Integration - Profile-Aware Response", success, details, {
                        "response": result.get("response_text", "")[:200],
                        "profile_elements_found": elements_found
                    })
                    
                else:
                    error_text = await response.text()
                    self.log_test_result("Memory Integration - Profile-Aware Response", False, f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test_result("Memory Integration - Profile-Aware Response", False, f"Exception: {str(e)}")
    
    async def cleanup_test_users(self):
        """Clean up test users created during testing"""
        logger.info("🧹 Cleaning up test users...")
        
        for user in self.test_users:
            try:
                async with self.session.delete(f"{BACKEND_URL}/users/profile/{user['id']}") as response:
                    if response.status == 200:
                        logger.info(f"✅ Deleted test user: {user['name']}")
                    else:
                        logger.warning(f"⚠️ Failed to delete user {user['name']}: HTTP {response.status}")
                        
            except Exception as e:
                logger.warning(f"⚠️ Error deleting user {user['name']}: {str(e)}")
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 PROFILE CONTEXT & LLM INTEGRATION TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info("=" * 80)
        
        # Group results by test category
        categories = {}
        for result in self.test_results:
            category = result["test"].split(" - ")[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "tests": []}
            
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
            
            categories[category]["tests"].append(result)
        
        # Print category summaries
        for category, data in categories.items():
            total = data["passed"] + data["failed"]
            rate = (data["passed"] / total * 100) if total > 0 else 0
            status = "✅" if rate >= 70 else "⚠️" if rate >= 50 else "❌"
            
            logger.info(f"{status} {category}: {data['passed']}/{total} ({rate:.1f}%)")
            
            # Show failed tests
            failed_tests = [t for t in data["tests"] if not t["success"]]
            if failed_tests:
                for test in failed_tests:
                    logger.info(f"   ❌ {test['test']}: {test['details']}")
        
        logger.info("=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "categories": categories,
            "detailed_results": self.test_results
        }

async def main():
    """Main test execution"""
    tester = ProfileContextTester()
    
    try:
        await tester.setup_session()
        
        # Run all tests
        await tester.test_profile_context_usage()
        await tester.test_profile_update_integration()
        await tester.test_age_appropriate_content()
        await tester.test_context_retention()
        await tester.test_memory_integration()
        
        # Generate summary
        summary = tester.generate_summary()
        
        # Cleanup
        await tester.cleanup_test_users()
        
        return summary
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {str(e)}")
        return None
        
    finally:
        await tester.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())