#!/usr/bin/env python3
"""
Enhanced LLM Profile Integration Backend Test
Tests comprehensive user profile information usage in conversation agent
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedProfileIntegrationTester:
    def __init__(self):
        # Get backend URL from environment
        self.base_url = "http://localhost:8001/api"
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.base_url = line.split('=')[1].strip() + '/api'
                        break
        except Exception as e:
            logger.warning(f"Could not read frontend .env file: {e}")
        
        logger.info(f"🔗 Backend URL: {self.base_url}")
        
        # Test profiles for different ages and interests
        self.test_profiles = {
            "age_5_dinosaur_lover": {
                "name": "Emma",
                "age": 5,
                "location": "New York",
                "gender": "female",
                "avatar": "dinosaur",
                "speech_speed": "slow",
                "energy_level": "high",
                "voice_personality": "friendly_companion",
                "interests": ["dinosaurs", "animals", "colors"],
                "learning_goals": ["counting", "letters", "shapes"]
            },
            "age_8_space_artist": {
                "name": "Alex",
                "age": 8,
                "location": "California",
                "gender": "male",
                "avatar": "rocket",
                "speech_speed": "normal",
                "energy_level": "balanced",
                "voice_personality": "story_narrator",
                "interests": ["space", "art", "music"],
                "learning_goals": ["science", "creativity", "reading"]
            },
            "age_11_tech_musician": {
                "name": "Jordan",
                "age": 11,
                "location": "Texas",
                "gender": "non_binary",
                "avatar": "robot",
                "speech_speed": "fast",
                "energy_level": "calm",
                "voice_personality": "learning_buddy",
                "interests": ["technology", "music", "math"],
                "learning_goals": ["programming", "advanced_math", "music_theory"]
            }
        }
        
        self.session = None
        self.test_results = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def create_test_profile(self, profile_data: Dict[str, Any]) -> str:
        """Create a test user profile"""
        try:
            async with self.session.post(f"{self.base_url}/users/profile", json=profile_data) as response:
                if response.status == 200:
                    result = await response.json()
                    user_id = result.get('id')
                    logger.info(f"✅ Created test profile for {profile_data['name']} (age {profile_data['age']}): {user_id}")
                    return user_id
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to create profile: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"❌ Error creating profile: {str(e)}")
            return None
    
    async def test_conversation_with_profile(self, user_id: str, profile_data: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Test conversation with profile integration"""
        try:
            payload = {
                "session_id": f"test_session_{user_id}",
                "user_id": user_id,
                "message": message
            }
            
            start_time = time.time()
            async with self.session.post(f"{self.base_url}/conversations/text", json=payload) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "response_text": result.get("response_text", ""),
                        "content_type": result.get("content_type", "conversation"),
                        "metadata": result.get("metadata", {}),
                        "response_time": response_time,
                        "word_count": len(result.get("response_text", "").split())
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Conversation failed: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "response_time": response_time
                    }
        except Exception as e:
            logger.error(f"❌ Error in conversation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response_time": 0
            }
    
    def analyze_profile_usage(self, response_text: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how well the response uses profile information"""
        analysis = {
            "name_usage": 0,
            "age_appropriate": 0,
            "interests_mentioned": 0,
            "learning_goals_referenced": 0,
            "new_fields_referenced": 0,
            "total_score": 0
        }
        
        response_lower = response_text.lower()
        
        # Check name usage
        name = profile_data.get('name', '').lower()
        if name and name in response_lower:
            analysis["name_usage"] = 1
            logger.info(f"✅ Name '{name}' used in response")
        
        # Check age-appropriate complexity
        age = profile_data.get('age', 7)
        words = response_text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        sentences = response_text.split('.')
        avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences) if sentences else 0
        
        if age <= 5:
            # Very simple language expected
            if avg_word_length <= 5 and avg_sentence_length <= 8:
                analysis["age_appropriate"] = 1
                logger.info(f"✅ Age-appropriate complexity for age {age}")
        elif age <= 8:
            # Simple language expected
            if avg_word_length <= 6 and avg_sentence_length <= 12:
                analysis["age_appropriate"] = 1
                logger.info(f"✅ Age-appropriate complexity for age {age}")
        else:
            # More complex language allowed
            if avg_word_length <= 7 and avg_sentence_length <= 15:
                analysis["age_appropriate"] = 1
                logger.info(f"✅ Age-appropriate complexity for age {age}")
        
        # Check interests integration
        interests = profile_data.get('interests', [])
        interests_found = 0
        for interest in interests:
            if interest.lower() in response_lower:
                interests_found += 1
                logger.info(f"✅ Interest '{interest}' mentioned in response")
        
        if interests and interests_found > 0:
            analysis["interests_mentioned"] = interests_found / len(interests)
        
        # Check learning goals integration
        learning_goals = profile_data.get('learning_goals', [])
        goals_found = 0
        for goal in learning_goals:
            if goal.lower() in response_lower:
                goals_found += 1
                logger.info(f"✅ Learning goal '{goal}' referenced in response")
        
        if learning_goals and goals_found > 0:
            analysis["learning_goals_referenced"] = goals_found / len(learning_goals)
        
        # Check new profile fields usage
        new_fields = ['gender', 'avatar', 'speech_speed', 'energy_level']
        fields_referenced = 0
        
        # Check for gender-appropriate language
        gender = profile_data.get('gender', '')
        if gender == 'female' and any(word in response_lower for word in ['she', 'her', 'girl']):
            fields_referenced += 1
        elif gender == 'male' and any(word in response_lower for word in ['he', 'him', 'boy']):
            fields_referenced += 1
        
        # Check for avatar-related content
        avatar = profile_data.get('avatar', '')
        if avatar and avatar.lower() in response_lower:
            fields_referenced += 1
            logger.info(f"✅ Avatar '{avatar}' referenced in response")
        
        # Check for energy level adaptation
        energy_level = profile_data.get('energy_level', '')
        if energy_level == 'high' and any(word in response_lower for word in ['exciting', 'fun', 'amazing', 'wow']):
            fields_referenced += 1
        elif energy_level == 'calm' and any(word in response_lower for word in ['peaceful', 'gentle', 'quiet', 'relaxing']):
            fields_referenced += 1
        
        analysis["new_fields_referenced"] = fields_referenced / len(new_fields)
        
        # Calculate total score
        analysis["total_score"] = (
            analysis["name_usage"] * 0.3 +
            analysis["age_appropriate"] * 0.25 +
            analysis["interests_mentioned"] * 0.25 +
            analysis["learning_goals_referenced"] * 0.15 +
            analysis["new_fields_referenced"] * 0.05
        )
        
        return analysis
    
    async def test_enhanced_profile_usage(self):
        """Test 1: Enhanced Profile Usage - comprehensive profile information usage"""
        logger.info("🎯 TEST 1: Enhanced Profile Usage Test")
        
        test_results = []
        
        for profile_name, profile_data in self.test_profiles.items():
            logger.info(f"\n📋 Testing profile: {profile_name}")
            
            # Create test profile
            user_id = await self.create_test_profile(profile_data)
            if not user_id:
                continue
            
            # Test general conversation
            conversation_result = await self.test_conversation_with_profile(
                user_id, profile_data, "Hi! How are you today?"
            )
            
            if conversation_result["success"]:
                analysis = self.analyze_profile_usage(conversation_result["response_text"], profile_data)
                
                result = {
                    "profile": profile_name,
                    "user_id": user_id,
                    "response": conversation_result["response_text"],
                    "analysis": analysis,
                    "word_count": conversation_result["word_count"],
                    "response_time": conversation_result["response_time"]
                }
                
                test_results.append(result)
                
                logger.info(f"📊 Profile Usage Score: {analysis['total_score']:.2f}")
                logger.info(f"📝 Response: {conversation_result['response_text'][:100]}...")
            else:
                logger.error(f"❌ Conversation failed for {profile_name}: {conversation_result.get('error')}")
        
        return test_results
    
    async def test_personalized_content_generation(self):
        """Test 2: Personalized Content Generation with profile data"""
        logger.info("\n🎯 TEST 2: Personalized Content Generation Test")
        
        test_results = []
        
        # Test with space-loving artist (Alex, age 8)
        profile_data = self.test_profiles["age_8_space_artist"]
        user_id = await self.create_test_profile(profile_data)
        
        if user_id:
            # Test personalized story
            story_result = await self.test_conversation_with_profile(
                user_id, profile_data, "Tell me a story about a brave adventure"
            )
            
            # Test personalized joke
            joke_result = await self.test_conversation_with_profile(
                user_id, profile_data, "Tell me a funny joke"
            )
            
            # Test personalized riddle
            riddle_result = await self.test_conversation_with_profile(
                user_id, profile_data, "Give me a riddle to solve"
            )
            
            for content_type, result in [("story", story_result), ("joke", joke_result), ("riddle", riddle_result)]:
                if result["success"]:
                    analysis = self.analyze_profile_usage(result["response_text"], profile_data)
                    
                    # Check for content-specific personalization
                    interests_integration = 0
                    response_lower = result["response_text"].lower()
                    
                    # Check if interests (space, art, music) are woven into content
                    for interest in profile_data["interests"]:
                        if interest.lower() in response_lower:
                            interests_integration += 1
                    
                    test_result = {
                        "content_type": content_type,
                        "user_id": user_id,
                        "response": result["response_text"],
                        "analysis": analysis,
                        "interests_integration": interests_integration,
                        "word_count": result["word_count"],
                        "response_time": result["response_time"]
                    }
                    
                    test_results.append(test_result)
                    
                    logger.info(f"📊 {content_type.title()} - Profile Score: {analysis['total_score']:.2f}, Interests: {interests_integration}/3")
                    logger.info(f"📝 {content_type.title()}: {result['response_text'][:100]}...")
                else:
                    logger.error(f"❌ {content_type.title()} generation failed: {result.get('error')}")
        
        return test_results
    
    async def test_interest_integration_verification(self):
        """Test 3: Interest Integration Verification - consistent connection to user interests"""
        logger.info("\n🎯 TEST 3: Interest Integration Verification Test")
        
        test_results = []
        
        # Test with dinosaur-loving child (Emma, age 5)
        profile_data = self.test_profiles["age_5_dinosaur_lover"]
        user_id = await self.create_test_profile(profile_data)
        
        if user_id:
            # Test various general questions to see if interests are referenced
            test_questions = [
                "What's your favorite color?",
                "What should we do today?",
                "Tell me something interesting",
                "What do you like to play?",
                "Can you help me learn something new?"
            ]
            
            for question in test_questions:
                result = await self.test_conversation_with_profile(user_id, profile_data, question)
                
                if result["success"]:
                    analysis = self.analyze_profile_usage(result["response_text"], profile_data)
                    
                    # Check specific interest integration
                    response_lower = result["response_text"].lower()
                    interests_mentioned = []
                    
                    for interest in profile_data["interests"]:  # dinosaurs, animals, colors
                        if interest.lower() in response_lower:
                            interests_mentioned.append(interest)
                    
                    test_result = {
                        "question": question,
                        "user_id": user_id,
                        "response": result["response_text"],
                        "analysis": analysis,
                        "interests_mentioned": interests_mentioned,
                        "word_count": result["word_count"],
                        "response_time": result["response_time"]
                    }
                    
                    test_results.append(test_result)
                    
                    logger.info(f"📊 Question: '{question}' - Interests mentioned: {interests_mentioned}")
                    logger.info(f"📝 Response: {result['response_text'][:100]}...")
                else:
                    logger.error(f"❌ Question failed: {question} - {result.get('error')}")
        
        return test_results
    
    async def test_age_appropriate_complexity(self):
        """Test 4: Age-Appropriate Complexity - language adaptation for different ages"""
        logger.info("\n🎯 TEST 4: Age-Appropriate Complexity Test")
        
        test_results = []
        
        # Test same question across different ages
        test_question = "How do airplanes fly?"
        
        for profile_name, profile_data in self.test_profiles.items():
            logger.info(f"\n📋 Testing age complexity for: {profile_name} (age {profile_data['age']})")
            
            user_id = await self.create_test_profile(profile_data)
            if not user_id:
                continue
            
            result = await self.test_conversation_with_profile(user_id, profile_data, test_question)
            
            if result["success"]:
                # Analyze language complexity
                response_text = result["response_text"]
                words = response_text.split()
                sentences = response_text.split('.')
                
                # Calculate complexity metrics
                avg_word_length = sum(len(word.strip('.,!?')) for word in words) / len(words) if words else 0
                avg_sentence_length = sum(len(sentence.split()) for sentence in sentences if sentence.strip()) / len([s for s in sentences if s.strip()]) if sentences else 0
                
                # Count complex words (>6 letters)
                complex_words = sum(1 for word in words if len(word.strip('.,!?')) > 6)
                complex_word_ratio = complex_words / len(words) if words else 0
                
                # Age-appropriate expectations
                age = profile_data["age"]
                complexity_appropriate = False
                
                if age <= 5:
                    # Very simple: short words, short sentences
                    complexity_appropriate = avg_word_length <= 5 and avg_sentence_length <= 8 and complex_word_ratio <= 0.1
                elif age <= 8:
                    # Simple: common words, clear sentences
                    complexity_appropriate = avg_word_length <= 6 and avg_sentence_length <= 12 and complex_word_ratio <= 0.2
                else:
                    # Moderate: grade-level vocabulary, longer sentences
                    complexity_appropriate = avg_word_length <= 7 and avg_sentence_length <= 15 and complex_word_ratio <= 0.3
                
                test_result = {
                    "profile": profile_name,
                    "age": age,
                    "user_id": user_id,
                    "response": response_text,
                    "avg_word_length": avg_word_length,
                    "avg_sentence_length": avg_sentence_length,
                    "complex_word_ratio": complex_word_ratio,
                    "complexity_appropriate": complexity_appropriate,
                    "word_count": result["word_count"],
                    "response_time": result["response_time"]
                }
                
                test_results.append(test_result)
                
                logger.info(f"📊 Age {age} - Avg word length: {avg_word_length:.1f}, Avg sentence length: {avg_sentence_length:.1f}")
                logger.info(f"📊 Complex word ratio: {complex_word_ratio:.2f}, Appropriate: {complexity_appropriate}")
                logger.info(f"📝 Response: {response_text[:100]}...")
            else:
                logger.error(f"❌ Age complexity test failed for {profile_name}: {result.get('error')}")
        
        return test_results
    
    async def run_comprehensive_test(self):
        """Run all enhanced profile integration tests"""
        logger.info("🚀 Starting Enhanced LLM Profile Integration Tests")
        
        await self.setup_session()
        
        try:
            # Test 1: Enhanced Profile Usage
            profile_usage_results = await self.test_enhanced_profile_usage()
            
            # Test 2: Personalized Content Generation
            content_generation_results = await self.test_personalized_content_generation()
            
            # Test 3: Interest Integration Verification
            interest_integration_results = await self.test_interest_integration_verification()
            
            # Test 4: Age-Appropriate Complexity
            age_complexity_results = await self.test_age_appropriate_complexity()
            
            # Compile comprehensive results
            all_results = {
                "profile_usage": profile_usage_results,
                "content_generation": content_generation_results,
                "interest_integration": interest_integration_results,
                "age_complexity": age_complexity_results
            }
            
            # Generate summary
            self.generate_test_summary(all_results)
            
            return all_results
            
        finally:
            await self.cleanup_session()
    
    def generate_test_summary(self, results: Dict[str, List[Dict[str, Any]]]):
        """Generate comprehensive test summary"""
        logger.info("\n" + "="*80)
        logger.info("🎯 ENHANCED LLM PROFILE INTEGRATION TEST SUMMARY")
        logger.info("="*80)
        
        # Test 1: Profile Usage Summary
        profile_usage = results["profile_usage"]
        if profile_usage:
            avg_score = sum(r["analysis"]["total_score"] for r in profile_usage) / len(profile_usage)
            name_usage_rate = sum(r["analysis"]["name_usage"] for r in profile_usage) / len(profile_usage)
            age_appropriate_rate = sum(r["analysis"]["age_appropriate"] for r in profile_usage) / len(profile_usage)
            interests_rate = sum(r["analysis"]["interests_mentioned"] for r in profile_usage) / len(profile_usage)
            
            logger.info(f"\n📊 TEST 1 - ENHANCED PROFILE USAGE:")
            logger.info(f"   Overall Profile Integration Score: {avg_score:.2f}/1.0")
            logger.info(f"   Name Usage Rate: {name_usage_rate:.2f} ({name_usage_rate*100:.0f}%)")
            logger.info(f"   Age-Appropriate Language: {age_appropriate_rate:.2f} ({age_appropriate_rate*100:.0f}%)")
            logger.info(f"   Interest Integration Rate: {interests_rate:.2f} ({interests_rate*100:.0f}%)")
            
            if avg_score >= 0.7:
                logger.info("   ✅ PASS - Strong profile integration")
            elif avg_score >= 0.5:
                logger.info("   ⚠️  PARTIAL - Moderate profile integration")
            else:
                logger.info("   ❌ FAIL - Weak profile integration")
        
        # Test 2: Content Generation Summary
        content_generation = results["content_generation"]
        if content_generation:
            avg_content_score = sum(r["analysis"]["total_score"] for r in content_generation) / len(content_generation)
            avg_interests_integration = sum(r["interests_integration"] for r in content_generation) / len(content_generation)
            
            logger.info(f"\n📊 TEST 2 - PERSONALIZED CONTENT GENERATION:")
            logger.info(f"   Content Personalization Score: {avg_content_score:.2f}/1.0")
            logger.info(f"   Average Interest Integration: {avg_interests_integration:.1f}/3.0")
            
            for result in content_generation:
                logger.info(f"   {result['content_type'].title()}: {result['analysis']['total_score']:.2f} score, {result['word_count']} words")
            
            if avg_content_score >= 0.6:
                logger.info("   ✅ PASS - Good content personalization")
            else:
                logger.info("   ❌ FAIL - Poor content personalization")
        
        # Test 3: Interest Integration Summary
        interest_integration = results["interest_integration"]
        if interest_integration:
            questions_with_interests = sum(1 for r in interest_integration if r["interests_mentioned"])
            interest_integration_rate = questions_with_interests / len(interest_integration)
            
            logger.info(f"\n📊 TEST 3 - INTEREST INTEGRATION VERIFICATION:")
            logger.info(f"   Questions with Interest References: {questions_with_interests}/{len(interest_integration)}")
            logger.info(f"   Interest Integration Rate: {interest_integration_rate:.2f} ({interest_integration_rate*100:.0f}%)")
            
            if interest_integration_rate >= 0.6:
                logger.info("   ✅ PASS - Consistent interest integration")
            elif interest_integration_rate >= 0.4:
                logger.info("   ⚠️  PARTIAL - Moderate interest integration")
            else:
                logger.info("   ❌ FAIL - Poor interest integration")
        
        # Test 4: Age Complexity Summary
        age_complexity = results["age_complexity"]
        if age_complexity:
            appropriate_responses = sum(1 for r in age_complexity if r["complexity_appropriate"])
            complexity_rate = appropriate_responses / len(age_complexity)
            
            logger.info(f"\n📊 TEST 4 - AGE-APPROPRIATE COMPLEXITY:")
            logger.info(f"   Age-Appropriate Responses: {appropriate_responses}/{len(age_complexity)}")
            logger.info(f"   Complexity Appropriateness Rate: {complexity_rate:.2f} ({complexity_rate*100:.0f}%)")
            
            for result in age_complexity:
                logger.info(f"   Age {result['age']}: {result['avg_word_length']:.1f} avg word length, {result['avg_sentence_length']:.1f} avg sentence length")
            
            if complexity_rate >= 0.8:
                logger.info("   ✅ PASS - Excellent age-appropriate adaptation")
            elif complexity_rate >= 0.6:
                logger.info("   ⚠️  PARTIAL - Good age-appropriate adaptation")
            else:
                logger.info("   ❌ FAIL - Poor age-appropriate adaptation")
        
        # Overall Assessment
        logger.info(f"\n🎯 OVERALL ENHANCED PROFILE INTEGRATION ASSESSMENT:")
        
        total_tests = 4
        passed_tests = 0
        
        if profile_usage and sum(r["analysis"]["total_score"] for r in profile_usage) / len(profile_usage) >= 0.7:
            passed_tests += 1
        if content_generation and sum(r["analysis"]["total_score"] for r in content_generation) / len(content_generation) >= 0.6:
            passed_tests += 1
        if interest_integration and (sum(1 for r in interest_integration if r["interests_mentioned"]) / len(interest_integration)) >= 0.6:
            passed_tests += 1
        if age_complexity and (sum(1 for r in age_complexity if r["complexity_appropriate"]) / len(age_complexity)) >= 0.8:
            passed_tests += 1
        
        success_rate = passed_tests / total_tests
        
        if success_rate >= 0.75:
            logger.info(f"   ✅ EXCELLENT - {passed_tests}/{total_tests} tests passed ({success_rate*100:.0f}%)")
            logger.info("   Enhanced LLM Profile Integration is working excellently!")
        elif success_rate >= 0.5:
            logger.info(f"   ⚠️  GOOD - {passed_tests}/{total_tests} tests passed ({success_rate*100:.0f}%)")
            logger.info("   Enhanced LLM Profile Integration is working but needs improvement")
        else:
            logger.info(f"   ❌ NEEDS WORK - {passed_tests}/{total_tests} tests passed ({success_rate*100:.0f}%)")
            logger.info("   Enhanced LLM Profile Integration needs significant improvement")
        
        logger.info("="*80)

async def main():
    """Main test execution"""
    tester = EnhancedProfileIntegrationTester()
    results = await tester.run_comprehensive_test()
    return results

if __name__ == "__main__":
    asyncio.run(main())