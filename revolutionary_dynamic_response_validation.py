#!/usr/bin/env python3
"""
CRITICAL FIX VALIDATION: Revolutionary Dynamic Response System Testing
Testing the system after fixing missing method to validate if it works as originally claimed.
"""

import asyncio
import aiohttp
import json
import time
import re
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RevolutionaryDynamicResponseValidator:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://e73353f9-1d22-4a0f-9deb-0707101e1e70.preview.emergentagent.com/api"
        self.session = None
        self.test_results = []
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def calculate_language_complexity(self, text: str) -> float:
        """Calculate language complexity score (average words per sentence)"""
        if not text:
            return 0.0
            
        # Split into sentences
        sentences = re.split(r'[.!?]+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
            
        total_words = 0
        for sentence in sentences:
            words = len(sentence.split())
            total_words += words
            
        return total_words / len(sentences)
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        if not text:
            return 0
        return len(text.split())
    
    async def test_story_generation_validation(self) -> Dict[str, Any]:
        """
        CRITICAL TEST 1: Story Generation Validation
        Test: "Tell me a story about a brave mouse" 
        Required: 120-300 words for age 8
        """
        logger.info("🎯 TESTING: Story Generation Validation")
        
        test_data = {
            "session_id": "story_validation_test",
            "user_id": "test_child_age_8",
            "message": "Tell me a story about a brave mouse"
        }
        
        try:
            start_time = time.time()
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=test_data) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "")
                    word_count = self.count_words(response_text)
                    
                    # Check if meets 120-300 word requirement
                    meets_requirement = 120 <= word_count <= 300
                    
                    return {
                        "test": "Story Generation Validation",
                        "status": "success" if meets_requirement else "failed",
                        "word_count": word_count,
                        "required_range": "120-300 words",
                        "meets_requirement": meets_requirement,
                        "response_time": f"{response_time:.2f}s",
                        "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text,
                        "details": f"Generated {word_count} words ({'✅ PASS' if meets_requirement else '❌ FAIL - Below minimum'})"
                    }
                else:
                    return {
                        "test": "Story Generation Validation", 
                        "status": "error",
                        "error": f"HTTP {response.status}",
                        "details": "API request failed"
                    }
                    
        except Exception as e:
            return {
                "test": "Story Generation Validation",
                "status": "error", 
                "error": str(e),
                "details": "Exception during story generation test"
            }
    
    async def test_age_appropriate_language_validation(self) -> List[Dict[str, Any]]:
        """
        CRITICAL TEST 2: Age-Appropriate Language Validation
        Test with ages 5, 8, 11
        Required: Language complexity appropriate for age (simple words for younger kids)
        """
        logger.info("🎯 TESTING: Age-Appropriate Language Validation")
        
        age_tests = [
            {"age": 5, "max_complexity": 8.0, "user_id": "test_child_age_5"},
            {"age": 8, "max_complexity": 12.0, "user_id": "test_child_age_8"}, 
            {"age": 11, "max_complexity": 16.0, "user_id": "test_child_age_11"}
        ]
        
        results = []
        
        for age_test in age_tests:
            test_data = {
                "session_id": f"age_test_{age_test['age']}",
                "user_id": age_test["user_id"],
                "message": "Tell me about animals in the forest"
            }
            
            try:
                async with self.session.post(f"{self.base_url}/conversations/text", json=test_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "")
                        complexity = self.calculate_language_complexity(response_text)
                        
                        meets_requirement = complexity <= age_test["max_complexity"]
                        
                        results.append({
                            "test": f"Age-Appropriate Language (Age {age_test['age']})",
                            "status": "success" if meets_requirement else "failed",
                            "age": age_test["age"],
                            "complexity_score": round(complexity, 1),
                            "max_allowed": age_test["max_complexity"],
                            "meets_requirement": meets_requirement,
                            "response_preview": response_text[:80] + "..." if len(response_text) > 80 else response_text,
                            "details": f"Complexity {complexity:.1f} ({'✅ PASS' if meets_requirement else '❌ FAIL - Too complex'})"
                        })
                    else:
                        results.append({
                            "test": f"Age-Appropriate Language (Age {age_test['age']})",
                            "status": "error",
                            "error": f"HTTP {response.status}",
                            "details": "API request failed"
                        })
                        
            except Exception as e:
                results.append({
                    "test": f"Age-Appropriate Language (Age {age_test['age']})",
                    "status": "error",
                    "error": str(e),
                    "details": "Exception during age-appropriate test"
                })
                
        return results
    
    async def test_quick_fact_testing(self) -> Dict[str, Any]:
        """
        CRITICAL TEST 3: Quick Fact Testing
        Test: "What is Jupiter?"
        Required: 30-50 words, 3-5 seconds
        """
        logger.info("🎯 TESTING: Quick Fact Testing")
        
        test_data = {
            "session_id": "quick_fact_test",
            "user_id": "test_child_age_8", 
            "message": "What is Jupiter?"
        }
        
        try:
            start_time = time.time()
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=test_data) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "")
                    word_count = self.count_words(response_text)
                    
                    # Check requirements: 30-50 words, 3-5 seconds
                    word_requirement = 30 <= word_count <= 50
                    time_requirement = 3.0 <= response_time <= 5.0
                    
                    return {
                        "test": "Quick Fact Testing",
                        "status": "success" if (word_requirement and time_requirement) else "failed",
                        "word_count": word_count,
                        "required_words": "30-50 words",
                        "response_time": f"{response_time:.2f}s",
                        "required_time": "3-5 seconds",
                        "word_requirement_met": word_requirement,
                        "time_requirement_met": time_requirement,
                        "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text,
                        "details": f"Words: {word_count} ({'✅' if word_requirement else '❌'}), Time: {response_time:.2f}s ({'✅' if time_requirement else '❌'})"
                    }
                else:
                    return {
                        "test": "Quick Fact Testing",
                        "status": "error",
                        "error": f"HTTP {response.status}",
                        "details": "API request failed"
                    }
                    
        except Exception as e:
            return {
                "test": "Quick Fact Testing",
                "status": "error",
                "error": str(e),
                "details": "Exception during quick fact test"
            }
    
    async def test_voice_pipeline_validation(self) -> List[Dict[str, Any]]:
        """
        CRITICAL TEST 4: Voice Pipeline Validation
        Test voice processing endpoints
        Previous: HTTP 422 errors
        """
        logger.info("🎯 TESTING: Voice Pipeline Validation")
        
        results = []
        
        # Test 1: Voice personalities endpoint
        try:
            async with self.session.get(f"{self.base_url}/voice/personalities") as response:
                if response.status == 200:
                    result = await response.json()
                    personalities = result.get("personalities", [])
                    
                    results.append({
                        "test": "Voice Personalities Endpoint",
                        "status": "success",
                        "personality_count": len(personalities),
                        "personalities": [p.get("name", "Unknown") for p in personalities] if personalities else [],
                        "details": f"✅ WORKING - {len(personalities)} personalities available"
                    })
                else:
                    results.append({
                        "test": "Voice Personalities Endpoint",
                        "status": "failed",
                        "error": f"HTTP {response.status}",
                        "details": "❌ FAILED - Endpoint returned error"
                    })
        except Exception as e:
            results.append({
                "test": "Voice Personalities Endpoint",
                "status": "error",
                "error": str(e),
                "details": "❌ ERROR - Exception during test"
            })
        
        # Test 2: TTS endpoint
        try:
            tts_data = {
                "text": "Hello, this is a test message",
                "personality": "friendly_companion"
            }
            
            async with self.session.post(f"{self.base_url}/voice/tts", json=tts_data) as response:
                if response.status == 200:
                    result = await response.json()
                    audio_data = result.get("audio_base64", "")
                    
                    results.append({
                        "test": "TTS Endpoint",
                        "status": "success",
                        "audio_generated": len(audio_data) > 0,
                        "audio_size": f"{len(audio_data)} chars" if audio_data else "0 chars",
                        "details": f"✅ WORKING - Generated {len(audio_data)} chars of audio data"
                    })
                else:
                    results.append({
                        "test": "TTS Endpoint", 
                        "status": "failed",
                        "error": f"HTTP {response.status}",
                        "details": "❌ FAILED - TTS endpoint returned error"
                    })
        except Exception as e:
            results.append({
                "test": "TTS Endpoint",
                "status": "error",
                "error": str(e),
                "details": "❌ ERROR - Exception during TTS test"
            })
            
        return results
    
    async def test_entertainment_content(self) -> Dict[str, Any]:
        """
        CRITICAL TEST 5: Entertainment Content
        Test: "Tell me a joke"
        Required: 40-80 words, complete joke
        """
        logger.info("🎯 TESTING: Entertainment Content")
        
        test_data = {
            "session_id": "entertainment_test",
            "user_id": "test_child_age_8",
            "message": "Tell me a joke"
        }
        
        try:
            start_time = time.time()
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=test_data) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "")
                    word_count = self.count_words(response_text)
                    
                    # Check if meets 40-80 word requirement
                    meets_requirement = 40 <= word_count <= 80
                    
                    # Check if it's a complete joke (has setup and punchline)
                    is_complete_joke = "?" in response_text or "!" in response_text
                    
                    return {
                        "test": "Entertainment Content (Joke)",
                        "status": "success" if (meets_requirement and is_complete_joke) else "failed",
                        "word_count": word_count,
                        "required_range": "40-80 words",
                        "meets_word_requirement": meets_requirement,
                        "is_complete_joke": is_complete_joke,
                        "response_time": f"{response_time:.2f}s",
                        "response_preview": response_text[:150] + "..." if len(response_text) > 150 else response_text,
                        "details": f"Words: {word_count} ({'✅' if meets_requirement else '❌'}), Complete: {'✅' if is_complete_joke else '❌'}"
                    }
                else:
                    return {
                        "test": "Entertainment Content (Joke)",
                        "status": "error",
                        "error": f"HTTP {response.status}",
                        "details": "API request failed"
                    }
                    
        except Exception as e:
            return {
                "test": "Entertainment Content (Joke)",
                "status": "error",
                "error": str(e),
                "details": "Exception during entertainment content test"
            }
    
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all critical validation tests"""
        logger.info("🚀 STARTING: Revolutionary Dynamic Response System Validation")
        
        await self.setup()
        
        try:
            # Run all critical tests
            story_result = await self.test_story_generation_validation()
            age_results = await self.test_age_appropriate_language_validation()
            fact_result = await self.test_quick_fact_testing()
            voice_results = await self.test_voice_pipeline_validation()
            entertainment_result = await self.test_entertainment_content()
            
            # Compile results
            all_results = [story_result] + age_results + [fact_result] + voice_results + [entertainment_result]
            
            # Calculate success rates
            total_tests = len(all_results)
            successful_tests = len([r for r in all_results if r.get("status") == "success"])
            failed_tests = len([r for r in all_results if r.get("status") == "failed"])
            error_tests = len([r for r in all_results if r.get("status") == "error"])
            
            success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
            
            # Critical success criteria analysis
            story_success = story_result.get("status") == "success"
            age_success = all(r.get("status") == "success" for r in age_results)
            fact_success = fact_result.get("status") == "success"
            voice_success = all(r.get("status") == "success" for r in voice_results)
            entertainment_success = entertainment_result.get("status") == "success"
            
            critical_success_rate = sum([story_success, age_success, fact_success, voice_success, entertainment_success]) / 5 * 100
            
            return {
                "validation_summary": {
                    "total_tests": total_tests,
                    "successful": successful_tests,
                    "failed": failed_tests,
                    "errors": error_tests,
                    "overall_success_rate": f"{success_rate:.1f}%",
                    "critical_success_rate": f"{critical_success_rate:.1f}%"
                },
                "critical_criteria_status": {
                    "story_generation_120_words": story_success,
                    "age_appropriate_language": age_success,
                    "quick_facts_30_50_words": fact_success,
                    "voice_pipeline_working": voice_success,
                    "entertainment_40_80_words": entertainment_success
                },
                "detailed_results": all_results,
                "final_assessment": "PASS" if critical_success_rate >= 80 else "FAIL",
                "revolutionary_system_status": "OPERATIONAL" if critical_success_rate >= 80 else "NEEDS_FIXES"
            }
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    validator = RevolutionaryDynamicResponseValidator()
    
    print("=" * 80)
    print("🎯 CRITICAL FIX VALIDATION: Revolutionary Dynamic Response System")
    print("Testing system after fixing missing method to validate original claims")
    print("=" * 80)
    
    results = await validator.run_comprehensive_validation()
    
    # Print summary
    print(f"\n📊 VALIDATION SUMMARY:")
    print(f"Total Tests: {results['validation_summary']['total_tests']}")
    print(f"Successful: {results['validation_summary']['successful']}")
    print(f"Failed: {results['validation_summary']['failed']}")
    print(f"Errors: {results['validation_summary']['errors']}")
    print(f"Overall Success Rate: {results['validation_summary']['overall_success_rate']}")
    print(f"Critical Success Rate: {results['validation_summary']['critical_success_rate']}")
    
    print(f"\n🎯 CRITICAL SUCCESS CRITERIA:")
    criteria = results['critical_criteria_status']
    print(f"✅ Story Generation (120+ words): {'PASS' if criteria['story_generation_120_words'] else 'FAIL'}")
    print(f"✅ Age-Appropriate Language: {'PASS' if criteria['age_appropriate_language'] else 'FAIL'}")
    print(f"✅ Quick Facts (30-50 words): {'PASS' if criteria['quick_facts_30_50_words'] else 'FAIL'}")
    print(f"✅ Voice Pipeline Working: {'PASS' if criteria['voice_pipeline_working'] else 'FAIL'}")
    print(f"✅ Entertainment (40-80 words): {'PASS' if criteria['entertainment_40_80_words'] else 'FAIL'}")
    
    print(f"\n🏆 FINAL ASSESSMENT: {results['final_assessment']}")
    print(f"🚀 Revolutionary System Status: {results['revolutionary_system_status']}")
    
    # Print detailed results
    print(f"\n📋 DETAILED TEST RESULTS:")
    for i, result in enumerate(results['detailed_results'], 1):
        status_icon = "✅" if result['status'] == 'success' else "❌" if result['status'] == 'failed' else "⚠️"
        print(f"{i}. {status_icon} {result['test']}: {result.get('details', result['status'])}")
    
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())