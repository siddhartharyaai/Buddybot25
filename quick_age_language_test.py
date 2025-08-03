#!/usr/bin/env python3
"""
Quick Age-Appropriate Language Test
Focused test for the Enhanced Age-Appropriate Language System
"""

import asyncio
import aiohttp
import json
import logging
import re
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuickAgeLanguageTest:
    def __init__(self):
        self.backend_url = "https://a720410a-cd33-47aa-8dde-f4048df3b4e9.preview.emergentagent.com/api"
        self.session = None
        
        # Forbidden words for younger children
        self.forbidden_words = ["magnificent", "extraordinary", "tremendous", "sophisticated", "elaborate", "exceptional"]

    async def setup(self):
        self.session = aiohttp.ClientSession()

    async def cleanup(self):
        if self.session:
            await self.session.close()

    async def create_user_profile(self, age: int, name: str, interests: list) -> str:
        """Create a user profile for testing"""
        try:
            profile_data = {
                "name": name,
                "age": age,
                "interests": interests,
                "language": "english",
                "voice_personality": "friendly_companion"
            }
            
            async with self.session.post(f"{self.backend_url}/users/profile", json=profile_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("id")
                else:
                    logger.error(f"Failed to create profile: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error creating profile: {e}")
            return None

    async def test_conversation(self, user_id: str, message: str) -> dict:
        """Test a conversation"""
        try:
            conversation_data = {
                "session_id": f"test_{int(time.time())}",
                "user_id": user_id,
                "message": message
            }
            
            async with self.session.post(f"{self.backend_url}/conversations/text", json=conversation_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "response_text": result.get("response_text", ""),
                        "content_type": result.get("content_type", "conversation")
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_language_for_age(self, text: str, age: int) -> dict:
        """Analyze language complexity for age appropriateness"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Calculate sentence lengths
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        max_sentence_length = max(sentence_lengths) if sentence_lengths else 0
        
        # Check for forbidden words
        forbidden_found = [word for word in words if word in self.forbidden_words]
        
        # Age-specific checks
        if age <= 5:
            max_allowed_sentence = 8
            complexity_threshold = 2.0
        elif age <= 8:
            max_allowed_sentence = 12
            complexity_threshold = 2.5
        else:
            max_allowed_sentence = 15
            complexity_threshold = 3.0
        
        # Calculate compliance
        sentence_compliance = max_sentence_length <= max_allowed_sentence
        vocabulary_compliance = len(forbidden_found) == 0
        
        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_length": avg_sentence_length,
            "max_sentence_length": max_sentence_length,
            "forbidden_words_found": forbidden_found,
            "sentence_compliance": sentence_compliance,
            "vocabulary_compliance": vocabulary_compliance,
            "overall_compliance": sentence_compliance and vocabulary_compliance
        }

    async def run_quick_test(self) -> dict:
        """Run quick age-appropriate language test"""
        logger.info("🎯 Running Quick Age-Appropriate Language Test")
        
        results = {
            "test_name": "Quick Age-Appropriate Language Test",
            "timestamp": time.time(),
            "tests": {}
        }
        
        try:
            # Test Age 5 - Very Simple Language
            logger.info("🧒 Testing Age 5 Language")
            user_id_5 = await self.create_user_profile(5, "Emma", ["puppies", "colors"])
            if user_id_5:
                result_5 = await self.test_conversation(user_id_5, "Tell me about puppies")
                if result_5["success"]:
                    analysis_5 = self.analyze_language_for_age(result_5["response_text"], 5)
                    results["tests"]["age_5"] = {
                        "success": True,
                        "response_text": result_5["response_text"],
                        "analysis": analysis_5,
                        "compliance": analysis_5["overall_compliance"]
                    }
                    logger.info(f"Age 5 Response: {result_5['response_text'][:100]}...")
                    logger.info(f"Age 5 Compliance: {analysis_5['overall_compliance']}")
                else:
                    results["tests"]["age_5"] = {"success": False, "error": result_5["error"]}
            
            # Test Age 8 - Simple Language
            logger.info("👦 Testing Age 8 Language")
            user_id_8 = await self.create_user_profile(8, "Alex", ["space", "robots"])
            if user_id_8:
                result_8 = await self.test_conversation(user_id_8, "Tell me about space")
                if result_8["success"]:
                    analysis_8 = self.analyze_language_for_age(result_8["response_text"], 8)
                    results["tests"]["age_8"] = {
                        "success": True,
                        "response_text": result_8["response_text"],
                        "analysis": analysis_8,
                        "compliance": analysis_8["overall_compliance"]
                    }
                    logger.info(f"Age 8 Response: {result_8['response_text'][:100]}...")
                    logger.info(f"Age 8 Compliance: {analysis_8['overall_compliance']}")
                else:
                    results["tests"]["age_8"] = {"success": False, "error": result_8["error"]}
            
            # Test Age 11 - Moderate Language
            logger.info("🧑 Testing Age 11 Language")
            user_id_11 = await self.create_user_profile(11, "Jordan", ["technology", "science"])
            if user_id_11:
                result_11 = await self.test_conversation(user_id_11, "Explain how computers work")
                if result_11["success"]:
                    analysis_11 = self.analyze_language_for_age(result_11["response_text"], 11)
                    results["tests"]["age_11"] = {
                        "success": True,
                        "response_text": result_11["response_text"],
                        "analysis": analysis_11,
                        "compliance": analysis_11["overall_compliance"]
                    }
                    logger.info(f"Age 11 Response: {result_11['response_text'][:100]}...")
                    logger.info(f"Age 11 Compliance: {analysis_11['overall_compliance']}")
                else:
                    results["tests"]["age_11"] = {"success": False, "error": result_11["error"]}
            
            # Calculate overall results
            successful_tests = sum(1 for test in results["tests"].values() 
                                 if test.get("success", False) and test.get("compliance", False))
            total_tests = len([test for test in results["tests"].values() if test.get("success", False)])
            
            success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
            
            results["summary"] = {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": success_rate,
                "status": "PASSED" if success_rate >= 66 else "FAILED"
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            results["error"] = str(e)
            results["summary"] = {"status": "ERROR", "success_rate": 0}
            return results

    def print_results(self, results: dict):
        """Print test results"""
        print("\n" + "="*60)
        print("🎯 QUICK AGE-APPROPRIATE LANGUAGE TEST RESULTS")
        print("="*60)
        
        summary = results.get("summary", {})
        print(f"\n📊 SUMMARY:")
        print(f"   Status: {summary.get('status', 'UNKNOWN')}")
        print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
        print(f"   Tests Passed: {summary.get('successful_tests', 0)}/{summary.get('total_tests', 0)}")
        
        for test_name, test_result in results.get("tests", {}).items():
            print(f"\n🔍 {test_name.upper()}:")
            
            if not test_result.get("success", False):
                print(f"   ❌ FAILED: {test_result.get('error', 'Unknown error')}")
                continue
            
            analysis = test_result.get("analysis", {})
            compliance = test_result.get("compliance", False)
            
            status = "✅ PASSED" if compliance else "❌ FAILED"
            print(f"   {status}")
            print(f"   📝 Response Length: {len(test_result.get('response_text', ''))} chars")
            print(f"   📊 Max Sentence Length: {analysis.get('max_sentence_length', 0)} words")
            print(f"   🚫 Forbidden Words: {len(analysis.get('forbidden_words_found', []))}")
            print(f"   ✅ Sentence Compliance: {analysis.get('sentence_compliance', False)}")
            print(f"   ✅ Vocabulary Compliance: {analysis.get('vocabulary_compliance', False)}")
            
            # Show sample of response
            response_text = test_result.get("response_text", "")
            if response_text:
                print(f"   📄 Sample: {response_text[:150]}...")

async def main():
    test = QuickAgeLanguageTest()
    
    try:
        await test.setup()
        results = await test.run_quick_test()
        test.print_results(results)
        
        success_rate = results.get("summary", {}).get("success_rate", 0)
        
        if success_rate >= 66:
            print(f"\n🎉 QUICK AGE-APPROPRIATE LANGUAGE TEST PASSED!")
            return True
        else:
            print(f"\n❌ QUICK AGE-APPROPRIATE LANGUAGE TEST FAILED!")
            return False
            
    except Exception as e:
        print(f"\n💥 TEST EXECUTION FAILED: {str(e)}")
        return False
    finally:
        await test.cleanup()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)