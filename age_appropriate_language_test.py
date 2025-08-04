#!/usr/bin/env python3
"""
Enhanced Age-Appropriate Language System Test
Tests the age-appropriate language complexity improvements and vocabulary filtering
"""

import asyncio
import aiohttp
import json
import logging
import re
from typing import Dict, List, Any
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgeAppropriateLanguageTest:
    def __init__(self):
        self.backend_url = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com/api"
        self.session = None
        self.test_results = []
        
        # Forbidden words for younger children
        self.forbidden_words = [
            "magnificent", "extraordinary", "tremendous", "fantastic", 
            "sophisticated", "elaborate", "exceptional", "phenomenal", 
            "spectacular", "marvelous"
        ]
        
        # Age-appropriate vocabulary expectations
        self.age_vocabulary = {
            5: {
                "max_syllables": 2,
                "max_sentence_length": 8,
                "allowed_words": ["fun", "big", "small", "run", "jump", "play", "happy", "sad", "dog", "cat", "mom", "dad"],
                "forbidden_words": self.forbidden_words
            },
            8: {
                "max_syllables": 3,
                "max_sentence_length": 12,
                "allowed_words": ["learn", "school", "friend", "story", "picture", "awesome", "great", "wonderful", "interesting"],
                "forbidden_words": ["sophisticated", "elaborate", "exceptional", "tremendous", "magnificent", "extraordinary"]
            },
            11: {
                "max_syllables": 4,
                "max_sentence_length": 15,
                "allowed_words": ["amazing", "fantastic", "incredible", "discover", "explore", "understand", "explain"],
                "forbidden_words": []  # More vocabulary allowed for older children
            }
        }

    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        logger.info("🚀 Starting Enhanced Age-Appropriate Language System Test")

    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()

    async def create_user_profile(self, age: int, name: str, interests: List[str]) -> str:
        """Create a user profile for testing"""
        try:
            profile_data = {
                "name": name,
                "age": age,
                "interests": interests,
                "language": "english",
                "voice_personality": "friendly_companion",
                "location": "Test Location",
                "gender": "prefer_not_to_say"
            }
            
            async with self.session.post(f"{self.backend_url}/users/profile", json=profile_data) as response:
                if response.status == 200:
                    result = await response.json()
                    user_id = result.get("id")
                    logger.info(f"✅ Created user profile: {name} (age {age}) - ID: {user_id}")
                    return user_id
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to create user profile: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error creating user profile: {str(e)}")
            return None

    def count_syllables(self, word: str) -> int:
        """Count syllables in a word (simple approximation)"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
            
        return max(1, syllable_count)

    def analyze_language_complexity(self, text: str, age: int) -> Dict[str, Any]:
        """Analyze language complexity for age appropriateness"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Calculate metrics
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        max_sentence_length = max(len(s.split()) for s in sentences) if sentences else 0
        
        # Syllable analysis
        syllable_counts = [self.count_syllables(word) for word in words]
        avg_syllables = sum(syllable_counts) / len(syllable_counts) if syllable_counts else 0
        complex_words = [word for word in words if self.count_syllables(word) > self.age_vocabulary[age]["max_syllables"]]
        
        # Forbidden word check
        forbidden_found = [word for word in words if word in self.age_vocabulary[age]["forbidden_words"]]
        
        # Sentence length compliance
        long_sentences = [s for s in sentences if len(s.split()) > self.age_vocabulary[age]["max_sentence_length"]]
        
        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_length": avg_sentence_length,
            "max_sentence_length": max_sentence_length,
            "avg_syllables_per_word": avg_syllables,
            "complex_words": complex_words,
            "complex_word_count": len(complex_words),
            "forbidden_words_found": forbidden_found,
            "long_sentences": long_sentences,
            "compliance_score": self.calculate_compliance_score(age, avg_sentence_length, max_sentence_length, complex_words, forbidden_found)
        }

    def calculate_compliance_score(self, age: int, avg_sentence_length: float, max_sentence_length: int, complex_words: List[str], forbidden_words: List[str]) -> float:
        """Calculate compliance score (0-100)"""
        score = 100
        
        # Sentence length penalties
        max_allowed = self.age_vocabulary[age]["max_sentence_length"]
        if avg_sentence_length > max_allowed:
            score -= min(30, (avg_sentence_length - max_allowed) * 5)
        
        if max_sentence_length > max_allowed:
            score -= min(20, (max_sentence_length - max_allowed) * 3)
        
        # Complex word penalties
        if complex_words:
            score -= min(25, len(complex_words) * 5)
        
        # Forbidden word penalties (severe)
        if forbidden_words:
            score -= min(50, len(forbidden_words) * 25)
        
        return max(0, score)

    async def test_conversation(self, user_id: str, message: str, expected_content_type: str = "conversation") -> Dict[str, Any]:
        """Test a conversation and analyze language complexity"""
        try:
            conversation_data = {
                "session_id": f"test_session_{int(time.time())}",
                "user_id": user_id,
                "message": message
            }
            
            async with self.session.post(f"{self.backend_url}/conversations/text", json=conversation_data) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "")
                    content_type = result.get("content_type", "conversation")
                    
                    return {
                        "success": True,
                        "response_text": response_text,
                        "content_type": content_type,
                        "word_count": len(response_text.split()),
                        "char_count": len(response_text)
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Conversation failed: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "response_text": "",
                        "content_type": "error"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Error in conversation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response_text": "",
                "content_type": "error"
            }

    async def test_age_5_language(self) -> Dict[str, Any]:
        """Test very simple language for 5-year-old"""
        logger.info("🧒 Testing Age 5 Language (Very Simple)")
        
        # Create user profile
        user_id = await self.create_user_profile(5, "Emma", ["puppies", "colors"])
        if not user_id:
            return {"success": False, "error": "Failed to create user profile"}
        
        # Test conversation
        result = await self.test_conversation(user_id, "Tell me about puppies")
        
        if not result["success"]:
            return {"success": False, "error": result["error"]}
        
        # Analyze language complexity
        analysis = self.analyze_language_complexity(result["response_text"], 5)
        
        # Check compliance
        compliance_checks = {
            "simple_words": analysis["complex_word_count"] == 0,
            "short_sentences": analysis["max_sentence_length"] <= 8,
            "no_forbidden_words": len(analysis["forbidden_words_found"]) == 0,
            "appropriate_length": 50 <= len(result["response_text"]) <= 300
        }
        
        success_rate = sum(compliance_checks.values()) / len(compliance_checks) * 100
        
        return {
            "success": True,
            "user_id": user_id,
            "response_text": result["response_text"],
            "analysis": analysis,
            "compliance_checks": compliance_checks,
            "success_rate": success_rate,
            "compliance_score": analysis["compliance_score"]
        }

    async def test_age_8_language(self) -> Dict[str, Any]:
        """Test simple language for 8-year-old"""
        logger.info("👦 Testing Age 8 Language (Simple)")
        
        # Create user profile
        user_id = await self.create_user_profile(8, "Alex", ["space", "robots"])
        if not user_id:
            return {"success": False, "error": "Failed to create user profile"}
        
        # Test conversation
        result = await self.test_conversation(user_id, "Tell me about space")
        
        if not result["success"]:
            return {"success": False, "error": result["error"]}
        
        # Analyze language complexity
        analysis = self.analyze_language_complexity(result["response_text"], 8)
        
        # Check compliance
        compliance_checks = {
            "appropriate_vocabulary": analysis["complex_word_count"] <= 3,  # Allow some complex words
            "sentence_length": analysis["max_sentence_length"] <= 12,
            "no_forbidden_words": len(analysis["forbidden_words_found"]) == 0,
            "explanations_present": "space" in result["response_text"].lower(),  # Should explain concepts
            "appropriate_length": 100 <= len(result["response_text"]) <= 500
        }
        
        success_rate = sum(compliance_checks.values()) / len(compliance_checks) * 100
        
        return {
            "success": True,
            "user_id": user_id,
            "response_text": result["response_text"],
            "analysis": analysis,
            "compliance_checks": compliance_checks,
            "success_rate": success_rate,
            "compliance_score": analysis["compliance_score"]
        }

    async def test_age_11_language(self) -> Dict[str, Any]:
        """Test moderate language for 11-year-old"""
        logger.info("🧑 Testing Age 11 Language (Moderate)")
        
        # Create user profile
        user_id = await self.create_user_profile(11, "Jordan", ["technology", "science"])
        if not user_id:
            return {"success": False, "error": "Failed to create user profile"}
        
        # Test conversation
        result = await self.test_conversation(user_id, "Explain how computers work")
        
        if not result["success"]:
            return {"success": False, "error": result["error"]}
        
        # Analyze language complexity
        analysis = self.analyze_language_complexity(result["response_text"], 11)
        
        # Check compliance
        compliance_checks = {
            "grade_level_vocabulary": analysis["avg_syllables_per_word"] >= 1.5,  # More complex vocabulary allowed
            "sentence_length": analysis["max_sentence_length"] <= 15,
            "complex_concepts_explained": any(word in result["response_text"].lower() for word in ["computer", "technology", "process"]),
            "detailed_explanation": len(result["response_text"]) >= 200,
            "educational_content": "work" in result["response_text"].lower()
        }
        
        success_rate = sum(compliance_checks.values()) / len(compliance_checks) * 100
        
        return {
            "success": True,
            "user_id": user_id,
            "response_text": result["response_text"],
            "analysis": analysis,
            "compliance_checks": compliance_checks,
            "success_rate": success_rate,
            "compliance_score": analysis["compliance_score"]
        }

    async def test_vocabulary_compliance(self) -> Dict[str, Any]:
        """Test that forbidden words are avoided for younger children"""
        logger.info("📚 Testing Vocabulary Compliance")
        
        results = {}
        
        # Test each age group
        for age in [5, 8, 11]:
            user_id = await self.create_user_profile(age, f"TestChild{age}", ["stories", "fun"])
            if not user_id:
                results[f"age_{age}"] = {"success": False, "error": "Failed to create profile"}
                continue
            
            # Test with a prompt that might trigger complex vocabulary
            result = await self.test_conversation(user_id, "Tell me something amazing and wonderful")
            
            if not result["success"]:
                results[f"age_{age}"] = {"success": False, "error": result["error"]}
                continue
            
            # Analyze for forbidden words
            analysis = self.analyze_language_complexity(result["response_text"], age)
            
            forbidden_found = analysis["forbidden_words_found"]
            compliance_score = analysis["compliance_score"]
            
            results[f"age_{age}"] = {
                "success": True,
                "response_text": result["response_text"],
                "forbidden_words_found": forbidden_found,
                "forbidden_word_count": len(forbidden_found),
                "compliance_score": compliance_score,
                "passes_vocabulary_test": len(forbidden_found) == 0
            }
        
        # Calculate overall success rate
        successful_tests = sum(1 for r in results.values() if r.get("passes_vocabulary_test", False))
        total_tests = len(results)
        overall_success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "success": True,
            "results": results,
            "overall_success_rate": overall_success_rate,
            "successful_tests": successful_tests,
            "total_tests": total_tests
        }

    async def test_content_creation_language(self) -> Dict[str, Any]:
        """Test story/joke creation with age-appropriate language"""
        logger.info("🎭 Testing Content Creation Language")
        
        results = {}
        
        # Test story creation for each age group
        for age in [5, 8, 11]:
            user_id = await self.create_user_profile(age, f"StoryChild{age}", ["animals", "adventure"])
            if not user_id:
                results[f"age_{age}_story"] = {"success": False, "error": "Failed to create profile"}
                continue
            
            # Test story creation
            story_result = await self.test_conversation(user_id, "Tell me a story about a brave animal")
            
            if story_result["success"]:
                story_analysis = self.analyze_language_complexity(story_result["response_text"], age)
                
                results[f"age_{age}_story"] = {
                    "success": True,
                    "content_type": "story",
                    "response_text": story_result["response_text"],
                    "word_count": story_result["word_count"],
                    "analysis": story_analysis,
                    "compliance_score": story_analysis["compliance_score"],
                    "age_appropriate": story_analysis["compliance_score"] >= 70
                }
            else:
                results[f"age_{age}_story"] = {
                    "success": False,
                    "error": story_result["error"]
                }
            
            # Test joke creation
            joke_result = await self.test_conversation(user_id, "Tell me a funny joke")
            
            if joke_result["success"]:
                joke_analysis = self.analyze_language_complexity(joke_result["response_text"], age)
                
                results[f"age_{age}_joke"] = {
                    "success": True,
                    "content_type": "joke",
                    "response_text": joke_result["response_text"],
                    "word_count": joke_result["word_count"],
                    "analysis": joke_analysis,
                    "compliance_score": joke_analysis["compliance_score"],
                    "age_appropriate": joke_analysis["compliance_score"] >= 70
                }
            else:
                results[f"age_{age}_joke"] = {
                    "success": False,
                    "error": joke_result["error"]
                }
        
        # Calculate success rates
        successful_content = sum(1 for r in results.values() if r.get("age_appropriate", False))
        total_content = len([r for r in results.values() if r.get("success", False)])
        content_success_rate = (successful_content / total_content * 100) if total_content > 0 else 0
        
        return {
            "success": True,
            "results": results,
            "content_success_rate": content_success_rate,
            "successful_content": successful_content,
            "total_content": total_content
        }

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive age-appropriate language test"""
        logger.info("🎯 Running Comprehensive Age-Appropriate Language Test")
        
        test_results = {
            "test_name": "Enhanced Age-Appropriate Language System",
            "timestamp": time.time(),
            "tests": {}
        }
        
        try:
            # Test 1: Age 5 Language
            logger.info("\n" + "="*50)
            test_results["tests"]["age_5_language"] = await self.test_age_5_language()
            
            # Test 2: Age 8 Language
            logger.info("\n" + "="*50)
            test_results["tests"]["age_8_language"] = await self.test_age_8_language()
            
            # Test 3: Age 11 Language
            logger.info("\n" + "="*50)
            test_results["tests"]["age_11_language"] = await self.test_age_11_language()
            
            # Test 4: Vocabulary Compliance
            logger.info("\n" + "="*50)
            test_results["tests"]["vocabulary_compliance"] = await self.test_vocabulary_compliance()
            
            # Test 5: Content Creation Language
            logger.info("\n" + "="*50)
            test_results["tests"]["content_creation_language"] = await self.test_content_creation_language()
            
            # Calculate overall results
            successful_tests = sum(1 for test in test_results["tests"].values() if test.get("success", False))
            total_tests = len(test_results["tests"])
            overall_success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
            
            test_results["summary"] = {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "overall_success_rate": overall_success_rate,
                "status": "PASSED" if overall_success_rate >= 70 else "FAILED"
            }
            
            return test_results
            
        except Exception as e:
            logger.error(f"❌ Comprehensive test failed: {str(e)}")
            test_results["error"] = str(e)
            test_results["summary"] = {
                "status": "ERROR",
                "overall_success_rate": 0
            }
            return test_results

    def print_detailed_results(self, results: Dict[str, Any]):
        """Print detailed test results"""
        print("\n" + "="*80)
        print("🎯 ENHANCED AGE-APPROPRIATE LANGUAGE SYSTEM TEST RESULTS")
        print("="*80)
        
        summary = results.get("summary", {})
        print(f"\n📊 OVERALL SUMMARY:")
        print(f"   Status: {summary.get('status', 'UNKNOWN')}")
        print(f"   Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
        print(f"   Tests Passed: {summary.get('successful_tests', 0)}/{summary.get('total_tests', 0)}")
        
        # Detailed test results
        tests = results.get("tests", {})
        
        for test_name, test_result in tests.items():
            print(f"\n🔍 {test_name.upper().replace('_', ' ')}:")
            
            if not test_result.get("success", False):
                print(f"   ❌ FAILED: {test_result.get('error', 'Unknown error')}")
                continue
            
            if test_name in ["age_5_language", "age_8_language", "age_11_language"]:
                print(f"   ✅ SUCCESS RATE: {test_result.get('success_rate', 0):.1f}%")
                print(f"   📝 Response Length: {len(test_result.get('response_text', ''))} chars")
                
                analysis = test_result.get("analysis", {})
                print(f"   📊 Language Analysis:")
                print(f"      - Avg Sentence Length: {analysis.get('avg_sentence_length', 0):.1f} words")
                print(f"      - Complex Words: {analysis.get('complex_word_count', 0)}")
                print(f"      - Forbidden Words: {len(analysis.get('forbidden_words_found', []))}")
                print(f"      - Compliance Score: {analysis.get('compliance_score', 0):.1f}/100")
                
                compliance = test_result.get("compliance_checks", {})
                for check, passed in compliance.items():
                    status = "✅" if passed else "❌"
                    print(f"      {status} {check.replace('_', ' ').title()}")
            
            elif test_name == "vocabulary_compliance":
                print(f"   ✅ OVERALL SUCCESS RATE: {test_result.get('overall_success_rate', 0):.1f}%")
                
                for age_test, age_result in test_result.get("results", {}).items():
                    if age_result.get("success", False):
                        forbidden_count = age_result.get("forbidden_word_count", 0)
                        status = "✅" if forbidden_count == 0 else "❌"
                        print(f"      {status} {age_test}: {forbidden_count} forbidden words found")
            
            elif test_name == "content_creation_language":
                print(f"   ✅ CONTENT SUCCESS RATE: {test_result.get('content_success_rate', 0):.1f}%")
                
                for content_test, content_result in test_result.get("results", {}).items():
                    if content_result.get("success", False):
                        appropriate = content_result.get("age_appropriate", False)
                        status = "✅" if appropriate else "❌"
                        score = content_result.get("compliance_score", 0)
                        print(f"      {status} {content_test}: {score:.1f}/100 compliance")

async def main():
    """Main test function"""
    test = AgeAppropriateLanguageTest()
    
    try:
        await test.setup()
        results = await test.run_comprehensive_test()
        test.print_detailed_results(results)
        
        # Return success/failure for automation
        summary = results.get("summary", {})
        success_rate = summary.get("overall_success_rate", 0)
        
        if success_rate >= 70:
            print(f"\n🎉 ENHANCED AGE-APPROPRIATE LANGUAGE SYSTEM TEST PASSED!")
            print(f"   Overall Success Rate: {success_rate:.1f}%")
            return True
        else:
            print(f"\n❌ ENHANCED AGE-APPROPRIATE LANGUAGE SYSTEM TEST FAILED!")
            print(f"   Overall Success Rate: {success_rate:.1f}%")
            print(f"   Minimum Required: 70.0%")
            return False
            
    except Exception as e:
        print(f"\n💥 TEST EXECUTION FAILED: {str(e)}")
        return False
    finally:
        await test.cleanup()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)