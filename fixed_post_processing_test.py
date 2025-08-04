#!/usr/bin/env python3
"""
FIXED Age-Appropriate Language Post-Processing System Test
Tests the critical bug fix to ensure post-processing runs for ALL content types
"""

import asyncio
import requests
import json
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from environment
BACKEND_URL = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com/api"

class FixedPostProcessingTest:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def log_test_result(self, test_name: str, success: bool, details: str):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: {test_name} - {details}")

    async def create_test_user_profile(self, user_id: str, name: str, age: int, interests: list):
        """Create a test user profile"""
        try:
            profile_data = {
                "id": user_id,
                "name": name,
                "age": age,
                "interests": interests,
                "language": "english",
                "voice_personality": "friendly_companion",
                "learning_goals": ["language_development", "creativity"],
                "location": "Test Location"
            }
            
            response = requests.post(
                f"{self.backend_url}/users/profile",
                json=profile_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Created test user profile: {name} (age {age})")
                return True
            else:
                logger.error(f"❌ Failed to create user profile: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating user profile: {str(e)}")
            return False

    async def test_text_conversation(self, user_id: str, message: str):
        """Test text conversation and analyze response"""
        try:
            payload = {
                "session_id": self.session_id,
                "user_id": user_id,
                "message": message
            }
            
            response = requests.post(
                f"{self.backend_url}/conversations/text",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response_text", "")
                content_type = data.get("content_type", "conversation")
                
                logger.info(f"📝 Response ({content_type}): {response_text[:100]}...")
                
                return {
                    "success": True,
                    "response_text": response_text,
                    "content_type": content_type,
                    "word_count": len(response_text.split())
                }
            else:
                logger.error(f"❌ Text conversation failed: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error in text conversation: {str(e)}")
            return {"success": False, "error": str(e)}

    def analyze_word_replacements(self, text: str, age: int):
        """Analyze if forbidden words were replaced appropriately"""
        text_lower = text.lower()
        
        if age <= 5:
            # Age 5 forbidden words and their expected replacements
            forbidden_words = {
                'magnificent': 'big and fun',
                'extraordinary': 'super cool',
                'tremendous': 'really big',
                'fantastic': 'super fun',
                'incredible': 'really cool',
                'amazing': 'really fun',
                'wonderful': 'really nice',
                'spectacular': 'really cool',
                'marvelous': 'really good',
                'phenomenal': 'super good'
            }
        elif age <= 8:
            # Age 8 forbidden words and their expected replacements
            forbidden_words = {
                'magnificent': 'awesome',
                'extraordinary': 'amazing',
                'tremendous': 'really big',
                'sophisticated': 'fancy',
                'elaborate': 'detailed',
                'exceptional': 'really great',
                'phenomenal': 'awesome',
                'spectacular': 'amazing'
            }
        else:
            # Age 11+ has lighter filtering
            forbidden_words = {}
        
        violations = []
        replacements = []
        
        for forbidden, expected in forbidden_words.items():
            if forbidden in text_lower:
                violations.append(f"Found forbidden word: '{forbidden}'")
            elif expected in text_lower:
                replacements.append(f"Correctly replaced with: '{expected}'")
        
        return {
            "violations": violations,
            "replacements": replacements,
            "has_violations": len(violations) > 0,
            "has_replacements": len(replacements) > 0
        }

    def analyze_sentence_length(self, text: str, age: int):
        """Analyze sentence length compliance"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if age <= 5:
            max_words = 8
        elif age <= 8:
            max_words = 12
        else:
            max_words = 15
        
        long_sentences = []
        for sentence in sentences:
            word_count = len(sentence.split())
            if word_count > max_words:
                long_sentences.append(f"'{sentence}' ({word_count} words)")
        
        return {
            "max_allowed": max_words,
            "long_sentences": long_sentences,
            "compliant": len(long_sentences) == 0,
            "total_sentences": len(sentences)
        }

    async def test_critical_bug_fix(self):
        """Test 1: Critical Bug Fix - Post-processing runs for ALL content types"""
        logger.info("🎯 TEST 1: Critical Bug Fix Verification")
        
        # Create Emma, age 5, interests ["puppies", "colors"]
        user_id = "emma_age5_critical_test"
        profile_created = await self.create_test_user_profile(
            user_id, "Emma", 5, ["puppies", "colors"]
        )
        
        if not profile_created:
            self.log_test_result("Critical Bug Fix - Profile Creation", False, "Failed to create test profile")
            return False
        
        # Test the specific prompt from review request
        test_message = "Tell me about a magnificent animal that is extraordinary"
        result = await self.test_text_conversation(user_id, test_message)
        
        if not result["success"]:
            self.log_test_result("Critical Bug Fix - API Call", False, f"API failed: {result.get('error')}")
            return False
        
        response_text = result["response_text"]
        content_type = result["content_type"]
        
        # Analyze word replacements
        word_analysis = self.analyze_word_replacements(response_text, 5)
        
        # Check if post-processing ran (no forbidden words should remain)
        post_processing_ran = not word_analysis["has_violations"]
        
        # Check if correct replacements were made
        correct_replacements = word_analysis["has_replacements"]
        
        details = f"Content type: {content_type}, Post-processing ran: {post_processing_ran}, Correct replacements: {correct_replacements}"
        if word_analysis["violations"]:
            details += f", Violations: {word_analysis['violations']}"
        if word_analysis["replacements"]:
            details += f", Replacements: {word_analysis['replacements']}"
        
        success = post_processing_ran and (correct_replacements or not any(word in response_text.lower() for word in ['magnificent', 'extraordinary']))
        
        self.log_test_result("Critical Bug Fix - Universal Post-Processing", success, details)
        return success

    async def test_age5_strict_filtering(self):
        """Test 2: Age 5 Strict Filtering"""
        logger.info("🎯 TEST 2: Age 5 Strict Filtering Test")
        
        user_id = "emma_age5_critical_test"  # Use existing profile
        
        test_cases = [
            "Tell me about something magnificent and extraordinary",
            "What is a tremendous and fantastic animal?",
            "Can you tell me an incredible and amazing story?"
        ]
        
        all_passed = True
        
        for i, test_message in enumerate(test_cases, 1):
            result = await self.test_text_conversation(user_id, test_message)
            
            if result["success"]:
                response_text = result["response_text"]
                content_type = result["content_type"]
                
                # Analyze word replacements
                word_analysis = self.analyze_word_replacements(response_text, 5)
                
                # Analyze sentence length (only for non-story content)
                sentence_analysis = self.analyze_sentence_length(response_text, 5)
                
                # For stories, sentence length rules are relaxed (gentle mode)
                if content_type == "story":
                    sentence_compliant = True  # Gentle mode for stories
                    sentence_note = "Gentle mode for story content"
                else:
                    sentence_compliant = sentence_analysis["compliant"]
                    sentence_note = f"Max {sentence_analysis['max_allowed']} words per sentence"
                
                word_compliant = not word_analysis["has_violations"]
                test_passed = word_compliant and sentence_compliant
                all_passed = all_passed and test_passed
                
                details = f"Test {i} ({content_type}): Words OK: {word_compliant}, Sentences OK: {sentence_compliant} ({sentence_note})"
                
                self.log_test_result(f"Age 5 Filtering - Test {i}", test_passed, details)
            else:
                all_passed = False
                self.log_test_result(f"Age 5 Filtering - Test {i}", False, f"API failed: {result.get('error')}")
        
        return all_passed

    async def test_age8_moderate_filtering(self):
        """Test 3: Age 8 Moderate Filtering"""
        logger.info("🎯 TEST 3: Age 8 Moderate Filtering Test")
        
        # Create age 8 user
        user_id = "alex_age8_critical_test"
        profile_created = await self.create_test_user_profile(
            user_id, "Alex", 8, ["science", "space"]
        )
        
        if not profile_created:
            self.log_test_result("Age 8 Filtering - Profile Creation", False, "Failed to create test profile")
            return False
        
        test_cases = [
            "Tell me about magnificent space exploration and extraordinary discoveries",
            "What makes robots so sophisticated and elaborate?"
        ]
        
        all_passed = True
        
        for i, test_message in enumerate(test_cases, 1):
            result = await self.test_text_conversation(user_id, test_message)
            
            if result["success"]:
                response_text = result["response_text"]
                content_type = result["content_type"]
                
                # Analyze word replacements for age 8
                word_analysis = self.analyze_word_replacements(response_text, 8)
                
                # Analyze sentence length for age 8
                sentence_analysis = self.analyze_sentence_length(response_text, 8)
                
                # For stories, sentence length rules are relaxed (gentle mode)
                if content_type == "story":
                    sentence_compliant = True  # Gentle mode for stories
                    sentence_note = "Gentle mode for story content"
                else:
                    sentence_compliant = sentence_analysis["compliant"]
                    sentence_note = f"Max {sentence_analysis['max_allowed']} words per sentence"
                
                word_compliant = not word_analysis["has_violations"]
                test_passed = word_compliant and sentence_compliant
                all_passed = all_passed and test_passed
                
                details = f"Test {i} ({content_type}): Words OK: {word_compliant}, Sentences OK: {sentence_compliant} ({sentence_note})"
                
                self.log_test_result(f"Age 8 Filtering - Test {i}", test_passed, details)
            else:
                all_passed = False
                self.log_test_result(f"Age 8 Filtering - Test {i}", False, f"API failed: {result.get('error')}")
        
        return all_passed

    async def test_universal_application(self):
        """Test 4: Universal Application across content types"""
        logger.info("🎯 TEST 4: Universal Application Test")
        
        user_id = "emma_age5_critical_test"  # Use existing age 5 profile
        
        # Test same input that should trigger different content types
        test_inputs = [
            "Tell me about a magnificent animal that is extraordinary",  # Story
            "Can you sing about a magnificent animal that is extraordinary",  # Song
            "Tell me a joke about a magnificent animal that is extraordinary"  # Joke
        ]
        
        all_passed = True
        content_types_found = []
        
        for i, test_input in enumerate(test_inputs, 1):
            result = await self.test_text_conversation(user_id, test_input)
            
            if result["success"]:
                response_text = result["response_text"]
                content_type = result["content_type"]
                word_count = result["word_count"]
                
                content_types_found.append(content_type)
                
                # Analyze word replacements
                word_analysis = self.analyze_word_replacements(response_text, 5)
                
                # Check if post-processing applied universally
                post_processing_applied = not word_analysis["has_violations"]
                
                # For story content with 200+ words, gentle mode should be active
                gentle_mode_active = content_type == "story" and word_count >= 200
                
                details = f"Content: {content_type}, Words: {word_count}, Post-processing: {post_processing_applied}"
                if gentle_mode_active:
                    details += ", Gentle mode: Active"
                
                test_passed = post_processing_applied
                all_passed = all_passed and test_passed
                
                self.log_test_result(f"Universal Application - Test {i}", test_passed, details)
            else:
                all_passed = False
                self.log_test_result(f"Universal Application - Test {i}", False, f"API failed: {result.get('error')}")
        
        # Check content type diversity
        unique_types = len(set(content_types_found))
        if unique_types >= 2:
            self.log_test_result("Universal Application - Content Diversity", True, f"Tested {unique_types} content types: {content_types_found}")
        else:
            self.log_test_result("Universal Application - Content Diversity", False, f"Only {unique_types} content type tested: {content_types_found}")
            all_passed = False
        
        return all_passed

    async def run_comprehensive_test(self):
        """Run all tests for the FIXED Age-Appropriate Language Post-Processing System"""
        logger.info("🚀 TESTING FIXED Age-Appropriate Language Post-Processing System")
        logger.info("=" * 80)
        
        # Run all tests
        test1_result = await self.test_critical_bug_fix()
        test2_result = await self.test_age5_strict_filtering()
        test3_result = await self.test_age8_moderate_filtering()
        test4_result = await self.test_universal_application()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 COMPREHENSIVE TEST RESULTS")
        logger.info("=" * 80)
        
        # Main test results
        main_tests = [
            ("Critical Bug Fix Verification", test1_result),
            ("Age 5 Strict Filtering", test2_result),
            ("Age 8 Moderate Filtering", test3_result),
            ("Universal Application", test4_result)
        ]
        
        for test_name, result in main_tests:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status}: {test_name}")
        
        logger.info(f"\n📊 STATISTICS:")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        # Critical assessment
        critical_bug_fixed = test1_result
        age_filtering_working = test2_result and test3_result
        
        if critical_bug_fixed and age_filtering_working:
            logger.info(f"\n✅ ASSESSMENT: CRITICAL BUG FIXED - Post-processing now runs for ALL content types")
            return True
        else:
            logger.info(f"\n❌ ASSESSMENT: CRITICAL BUG NOT FIXED - Post-processing still has issues")
            if not critical_bug_fixed:
                logger.info("   - Post-processing not running universally")
            if not age_filtering_working:
                logger.info("   - Age-appropriate filtering not working properly")
            return False

async def main():
    """Main test execution"""
    test_suite = FixedPostProcessingTest()
    
    try:
        success = await test_suite.run_comprehensive_test()
        
        if success:
            logger.info("✅ FIXED Age-Appropriate Language Post-Processing System is working correctly")
            sys.exit(0)
        else:
            logger.info("❌ CRITICAL BUG NOT FIXED - Post-processing system still has issues")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Test suite failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())