#!/usr/bin/env python3
"""
Review-Focused Age-Appropriate Language Post-Processing Test
Testing the specific requirements from the review request
"""

import asyncio
import aiohttp
import json
import logging
import sys
import time
import re
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from environment
BACKEND_URL = "https://e5199e07-d73b-431f-bd43-a7eca782e60c.preview.emergentagent.com/api"

class ReviewFocusedLanguageTest:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def create_user_profile(self, user_id: str, name: str, age: int, interests: List[str]) -> Dict[str, Any]:
        """Create a user profile for testing"""
        try:
            profile_data = {
                "name": name,
                "age": age,
                "location": "Test City",
                "interests": interests,
                "language": "english",
                "voice_personality": "friendly_companion",
                "learning_goals": ["language_development", "creativity"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/users/profile", json=profile_data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Created user profile: {name} (age {age})")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to create profile: {response.status} - {error_text}")
                    return {"error": f"HTTP {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Error creating user profile: {str(e)}")
            return {"error": str(e)}
    
    async def test_conversation(self, user_id: str, message: str) -> Dict[str, Any]:
        """Test conversation and return response"""
        try:
            conversation_data = {
                "session_id": f"test_session_{user_id}_{int(time.time())}",
                "user_id": user_id,
                "message": message
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text", json=conversation_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "response_text": result.get("response_text", ""),
                        "content_type": result.get("content_type", "conversation")
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Conversation failed: {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Error in conversation: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def analyze_word_replacements(self, text: str, age: int) -> Dict[str, Any]:
        """Analyze if complex words were properly replaced"""
        text_lower = text.lower()
        
        # Define expected replacements based on age
        if age <= 5:
            # Age 5 replacements
            expected_replacements = {
                'magnificent': 'big and fun',
                'extraordinary': 'super cool',
                'tremendous': 'really big'
            }
            forbidden_words = ['magnificent', 'extraordinary', 'tremendous', 'fantastic', 'incredible', 'amazing', 'wonderful', 'spectacular', 'marvelous', 'phenomenal', 'sophisticated', 'elaborate', 'exceptional']
        elif age <= 8:
            # Age 8 replacements
            expected_replacements = {
                'magnificent': 'awesome',
                'extraordinary': 'amazing',
                'tremendous': 'really big'
            }
            forbidden_words = ['magnificent', 'extraordinary', 'tremendous', 'sophisticated', 'elaborate', 'exceptional', 'phenomenal', 'spectacular']
        else:
            expected_replacements = {}
            forbidden_words = []
        
        # Check for forbidden words
        forbidden_found = []
        for word in forbidden_words:
            if re.search(r'\b' + word + r'\b', text_lower):
                forbidden_found.append(word)
        
        # Check for expected replacements
        replacements_found = []
        for original, replacement in expected_replacements.items():
            if replacement.lower() in text_lower:
                replacements_found.append(f"{original} → {replacement}")
        
        return {
            "forbidden_words_found": forbidden_found,
            "replacements_found": replacements_found,
            "vocabulary_compliant": len(forbidden_found) == 0
        }
    
    def analyze_sentence_length(self, text: str, age: int) -> Dict[str, Any]:
        """Analyze sentence length compliance"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Define max sentence length by age
        if age <= 5:
            max_length = 8
        elif age <= 8:
            max_length = 12
        else:
            max_length = 15
        
        sentence_lengths = [len(sentence.split()) for sentence in sentences]
        long_sentences = [i for i, length in enumerate(sentence_lengths) if length > max_length]
        avg_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        return {
            "total_sentences": len(sentences),
            "sentence_lengths": sentence_lengths,
            "avg_sentence_length": round(avg_length, 1),
            "max_allowed_length": max_length,
            "long_sentences_count": len(long_sentences),
            "sentence_length_compliant": len(long_sentences) == 0
        }
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            logger.info(f"✅ {test_name}: PASSED {details}")
        else:
            logger.error(f"❌ {test_name}: FAILED {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    async def test_age_5_post_processing(self):
        """Test Age 5 Language Post-Processing as specified in review"""
        logger.info("🧒 Testing Age 5 Language Post-Processing (Review Requirements)")
        
        # Create user profile: age 5, name "Emma", interests ["puppies", "colors"]
        user_id = "emma_age5_review"
        profile_result = await self.create_user_profile(
            user_id=user_id,
            name="Emma",
            age=5,
            interests=["puppies", "colors"]
        )
        
        if "error" in profile_result:
            self.log_test_result("Age 5 Profile Creation", False, f"Failed: {profile_result['error']}")
            return
        
        self.log_test_result("Age 5 Profile Creation", True, "Emma (age 5) with interests [puppies, colors]")
        
        # Test simple questions as specified
        test_questions = [
            "Tell me about puppies",
            "What colors do you like?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            logger.info(f"Testing Age 5 Question {i}: {question}")
            
            result = await self.test_conversation(user_id, question)
            
            if not result.get("success"):
                self.log_test_result(f"Age 5 Question {i} Response", False, f"Conversation failed: {result.get('error')}")
                continue
            
            response_text = result["response_text"]
            
            # Analyze word replacements
            word_analysis = self.analyze_word_replacements(response_text, 5)
            
            # Analyze sentence length
            sentence_analysis = self.analyze_sentence_length(response_text, 5)
            
            # Log analysis
            logger.info(f"Response: {response_text[:100]}...")
            logger.info(f"Word Analysis: Forbidden words: {word_analysis['forbidden_words_found']}, Replacements: {word_analysis['replacements_found']}")
            logger.info(f"Sentence Analysis: Avg length: {sentence_analysis['avg_sentence_length']}, Long sentences: {sentence_analysis['long_sentences_count']}")
            
            # Verify requirements
            vocab_success = word_analysis["vocabulary_compliant"]
            sentence_success = sentence_analysis["sentence_length_compliant"]
            overall_success = vocab_success and sentence_success
            
            details = f"Vocab: {'✅' if vocab_success else '❌'}, Sentences: {'✅' if sentence_success else '❌'}"
            self.log_test_result(f"Age 5 Question {i} Post-Processing", overall_success, details)
    
    async def test_age_8_post_processing(self):
        """Test Age 8 Language Post-Processing as specified in review"""
        logger.info("👦 Testing Age 8 Language Post-Processing (Review Requirements)")
        
        # Create user profile: age 8, name "Alex", interests ["space", "robots"]
        user_id = "alex_age8_review"
        profile_result = await self.create_user_profile(
            user_id=user_id,
            name="Alex",
            age=8,
            interests=["space", "robots"]
        )
        
        if "error" in profile_result:
            self.log_test_result("Age 8 Profile Creation", False, f"Failed: {profile_result['error']}")
            return
        
        self.log_test_result("Age 8 Profile Creation", True, "Alex (age 8) with interests [space, robots]")
        
        # Test questions as specified
        test_questions = [
            "Tell me about space",
            "What are robots?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            logger.info(f"Testing Age 8 Question {i}: {question}")
            
            result = await self.test_conversation(user_id, question)
            
            if not result.get("success"):
                self.log_test_result(f"Age 8 Question {i} Response", False, f"Conversation failed: {result.get('error')}")
                continue
            
            response_text = result["response_text"]
            
            # Analyze word replacements
            word_analysis = self.analyze_word_replacements(response_text, 8)
            
            # Analyze sentence length
            sentence_analysis = self.analyze_sentence_length(response_text, 8)
            
            # Log analysis
            logger.info(f"Response: {response_text[:100]}...")
            logger.info(f"Word Analysis: Forbidden words: {word_analysis['forbidden_words_found']}, Replacements: {word_analysis['replacements_found']}")
            logger.info(f"Sentence Analysis: Avg length: {sentence_analysis['avg_sentence_length']}, Long sentences: {sentence_analysis['long_sentences_count']}")
            
            # Verify requirements
            vocab_success = word_analysis["vocabulary_compliant"]
            sentence_success = sentence_analysis["sentence_length_compliant"]
            overall_success = vocab_success and sentence_success
            
            details = f"Vocab: {'✅' if vocab_success else '❌'}, Sentences: {'✅' if sentence_success else '❌'}"
            self.log_test_result(f"Age 8 Question {i} Post-Processing", overall_success, details)
    
    async def test_complex_word_replacement_verification(self):
        """Test Complex Word Replacement Verification as specified in review"""
        logger.info("🔄 Testing Complex Word Replacement Verification (Review Requirements)")
        
        # Create test user
        user_id = "word_test_review"
        profile_result = await self.create_user_profile(
            user_id=user_id,
            name="TestChild",
            age=5,
            interests=["animals"]
        )
        
        if "error" in profile_result:
            self.log_test_result("Word Replacement Profile", False, f"Failed: {profile_result['error']}")
            return
        
        # Test specific word replacements as mentioned in review
        test_cases = [
            ("Tell me about a magnificent animal", "magnificent", "big and fun"),
            ("Show me something extraordinary", "extraordinary", "super cool"),
            ("That's tremendous!", "tremendous", "really big")
        ]
        
        for i, (prompt, original_word, expected_replacement) in enumerate(test_cases, 1):
            logger.info(f"Testing Word Replacement {i}: {prompt}")
            
            result = await self.test_conversation(user_id, prompt)
            
            if not result.get("success"):
                self.log_test_result(f"Word Replacement Test {i}", False, f"Conversation failed: {result.get('error')}")
                continue
            
            response_text = result["response_text"]
            text_lower = response_text.lower()
            
            # Check if original word was removed
            original_found = re.search(r'\b' + original_word + r'\b', text_lower)
            
            # Check if replacement was used
            replacement_found = expected_replacement.lower() in text_lower
            
            success = not original_found  # Original word should NOT be present
            details = f"Original '{original_word}': {'❌ Found' if original_found else '✅ Removed'}, " \
                     f"Replacement '{expected_replacement}': {'✅ Found' if replacement_found else '❌ Not Found'}"
            
            logger.info(f"Response: {response_text[:100]}...")
            logger.info(f"Analysis: {details}")
            
            self.log_test_result(f"Word Replacement Test {i} ({original_word})", success, details)
    
    async def test_sentence_length_enforcement(self):
        """Test Sentence Length Enforcement as specified in review"""
        logger.info("📏 Testing Sentence Length Enforcement (Review Requirements)")
        
        # Test both age groups
        test_users = [
            ("sentence_age5_review", "TestChild5", 5, 8),  # Max 8 words
            ("sentence_age8_review", "TestChild8", 8, 12)  # Max 12 words
        ]
        
        for user_id, name, age, max_words in test_users:
            profile_result = await self.create_user_profile(
                user_id=user_id,
                name=name,
                age=age,
                interests=["stories"]
            )
            
            if "error" in profile_result:
                self.log_test_result(f"Sentence Length Profile Age {age}", False, f"Failed: {profile_result['error']}")
                continue
            
            # Test with prompts that might generate long sentences
            test_prompts = [
                "Tell me a detailed story about your favorite animal and explain why you like it so much and what makes it special",
                "Explain step by step how to make a peanut butter and jelly sandwich with all the details"
            ]
            
            for i, prompt in enumerate(test_prompts, 1):
                logger.info(f"Testing Sentence Length Age {age} Prompt {i}: {prompt[:50]}...")
                
                result = await self.test_conversation(user_id, prompt)
                
                if not result.get("success"):
                    self.log_test_result(f"Sentence Length Age {age} Test {i}", False, f"Conversation failed: {result.get('error')}")
                    continue
                
                response_text = result["response_text"]
                sentence_analysis = self.analyze_sentence_length(response_text, age)
                
                success = sentence_analysis["sentence_length_compliant"]
                details = f"Avg: {sentence_analysis['avg_sentence_length']} words (max {max_words}), " \
                         f"Long sentences: {sentence_analysis['long_sentences_count']}"
                
                logger.info(f"Response: {response_text[:100]}...")
                logger.info(f"Sentence Analysis: {details}")
                
                self.log_test_result(f"Sentence Length Age {age} Test {i}", success, details)
    
    async def run_review_tests(self):
        """Run all review-focused tests"""
        logger.info("🚀 Starting Review-Focused Age-Appropriate Language Post-Processing Tests")
        
        await self.setup_session()
        
        try:
            # Test health check first
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status != 200:
                    logger.error("❌ Backend health check failed")
                    return
                logger.info("✅ Backend health check passed")
            
            # Run all test suites as specified in review
            await self.test_age_5_post_processing()
            await self.test_age_8_post_processing()
            await self.test_complex_word_replacement_verification()
            await self.test_sentence_length_enforcement()
            
        finally:
            await self.cleanup_session()
        
        # Print final results
        self.print_final_results()
    
    def print_final_results(self):
        """Print final test results"""
        logger.info("=" * 80)
        logger.info("🎯 REVIEW-FOCUSED AGE-APPROPRIATE LANGUAGE POST-PROCESSING TEST RESULTS")
        logger.info("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        logger.info(f"Total Tests: {self.total_tests}")
        logger.info(f"Passed: {self.passed_tests}")
        logger.info(f"Failed: {self.total_tests - self.passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        logger.info("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            logger.info(f"{status}: {result['test']} - {result['details']}")
        
        # Summary for main agent
        logger.info("\n🎯 REVIEW REQUIREMENTS ASSESSMENT:")
        
        # Count specific test categories
        age_5_tests = [r for r in self.test_results if "Age 5" in r["test"]]
        age_8_tests = [r for r in self.test_results if "Age 8" in r["test"]]
        word_replacement_tests = [r for r in self.test_results if "Word Replacement" in r["test"]]
        sentence_length_tests = [r for r in self.test_results if "Sentence Length" in r["test"]]
        
        age_5_success = sum(1 for r in age_5_tests if r["success"]) / len(age_5_tests) * 100 if age_5_tests else 0
        age_8_success = sum(1 for r in age_8_tests if r["success"]) / len(age_8_tests) * 100 if age_8_tests else 0
        word_success = sum(1 for r in word_replacement_tests if r["success"]) / len(word_replacement_tests) * 100 if word_replacement_tests else 0
        sentence_success = sum(1 for r in sentence_length_tests if r["success"]) / len(sentence_length_tests) * 100 if sentence_length_tests else 0
        
        logger.info(f"1. Age 5 Language Post-Processing: {age_5_success:.1f}% success")
        logger.info(f"2. Age 8 Language Post-Processing: {age_8_success:.1f}% success")
        logger.info(f"3. Complex Word Replacement: {word_success:.1f}% success")
        logger.info(f"4. Sentence Length Enforcement: {sentence_success:.1f}% success")
        
        if success_rate >= 80:
            logger.info("🎉 OVERALL ASSESSMENT: Enhanced Age-Appropriate Language Post-Processing System is WORKING")
        elif success_rate >= 60:
            logger.info("⚠️ OVERALL ASSESSMENT: Enhanced Age-Appropriate Language Post-Processing System has MINOR ISSUES")
        else:
            logger.info("❌ OVERALL ASSESSMENT: Enhanced Age-Appropriate Language Post-Processing System has MAJOR ISSUES")

async def main():
    """Main test function"""
    test_runner = ReviewFocusedLanguageTest()
    await test_runner.run_review_tests()

if __name__ == "__main__":
    asyncio.run(main())