#!/usr/bin/env python3
"""
CRITICAL STORY GENERATION VALIDATION AFTER FIXES
Testing the specific fixes mentioned in the review request:
1. Fixed _post_process_ambient_response method that was truncating stories
2. Resolved duplicate method definitions issue 
3. Added missing get_available_voices() method to VoiceAgent class
"""

import asyncio
import aiohttp
import json
import time
import sys
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://6ddee563-7037-4e87-80ca-83a8a9a9bcae.preview.emergentagent.com/api"

class StoryGenerationValidator:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.user_id = "story_test_user_001"
        self.session_id = f"story_session_{int(time.time())}"
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name: str, success: bool, details: str, data: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.time(),
            "data": data or {}
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        
    async def test_story_generation_length(self):
        """Test 1: STORY GENERATION LENGTH VALIDATION"""
        print("\n🎯 TESTING STORY GENERATION LENGTH VALIDATION")
        print("=" * 60)
        
        story_prompts = [
            "Tell me a complete story about a brave little mouse",
            "Can you tell me a long adventure story with beginning, middle and end",
            "I want a detailed story about a magical forest with characters and plot",
            "Please create a full story about friendship that's at least 300 words"
        ]
        
        total_tests = len(story_prompts)
        passed_tests = 0
        word_counts = []
        
        for i, prompt in enumerate(story_prompts, 1):
            print(f"\n📝 Test {i}/{total_tests}: '{prompt[:50]}...'")
            
            try:
                payload = {
                    "session_id": f"{self.session_id}_story_{i}",
                    "user_id": self.user_id,
                    "message": prompt
                }
                
                async with self.session.post(f"{BACKEND_URL}/conversations/text", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        word_count = len(response_text.split())
                        word_counts.append(word_count)
                        
                        # Check if meets 300+ word requirement
                        meets_requirement = word_count >= 300
                        if meets_requirement:
                            passed_tests += 1
                            
                        self.log_result(
                            f"Story Length Test {i}",
                            meets_requirement,
                            f"Generated {word_count} words ({'PASS' if meets_requirement else 'FAIL - needs 300+'})",
                            {
                                "prompt": prompt,
                                "word_count": word_count,
                                "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                                "content_type": data.get("content_type", "unknown")
                            }
                        )
                        
                        print(f"   📊 Word count: {word_count} ({'✅ PASS' if meets_requirement else '❌ FAIL'})")
                        print(f"   📄 Preview: {response_text[:100]}...")
                        
                    else:
                        error_text = await response.text()
                        self.log_result(
                            f"Story Length Test {i}",
                            False,
                            f"HTTP {response.status}: {error_text[:100]}",
                            {"prompt": prompt, "http_status": response.status}
                        )
                        print(f"   ❌ HTTP {response.status}: {error_text[:100]}")
                        
            except Exception as e:
                self.log_result(
                    f"Story Length Test {i}",
                    False,
                    f"Exception: {str(e)}",
                    {"prompt": prompt, "error": str(e)}
                )
                print(f"   ❌ Exception: {str(e)}")
                
        # Summary
        success_rate = (passed_tests / total_tests) * 100
        avg_word_count = sum(word_counts) / len(word_counts) if word_counts else 0
        
        print(f"\n📊 STORY LENGTH VALIDATION SUMMARY:")
        print(f"   Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"   Average Word Count: {avg_word_count:.0f} words")
        print(f"   Word Count Range: {min(word_counts) if word_counts else 0}-{max(word_counts) if word_counts else 0}")
        
        return success_rate >= 75  # At least 75% should pass
        
    async def test_voice_personalities_endpoint(self):
        """Test 2: VOICE PERSONALITIES ENDPOINT"""
        print("\n🎤 TESTING VOICE PERSONALITIES ENDPOINT")
        print("=" * 60)
        
        try:
            async with self.session.get(f"{BACKEND_URL}/voice/personalities") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    is_valid = isinstance(data, (dict, list)) and len(data) > 0
                    
                    if is_valid:
                        personality_count = len(data) if isinstance(data, list) else len(data.get('personalities', []))
                        self.log_result(
                            "Voice Personalities Endpoint",
                            True,
                            f"Successfully returned {personality_count} voice personalities",
                            {"response_data": data, "personality_count": personality_count}
                        )
                        print(f"   ✅ Found {personality_count} voice personalities")
                        print(f"   📄 Response: {json.dumps(data, indent=2)[:300]}...")
                        return True
                    else:
                        self.log_result(
                            "Voice Personalities Endpoint",
                            False,
                            "Invalid response format - empty or malformed data",
                            {"response_data": data}
                        )
                        print(f"   ❌ Invalid response format")
                        return False
                        
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Voice Personalities Endpoint",
                        False,
                        f"HTTP {response.status}: {error_text}",
                        {"http_status": response.status, "error": error_text}
                    )
                    print(f"   ❌ HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_result(
                "Voice Personalities Endpoint",
                False,
                f"Exception: {str(e)}",
                {"error": str(e)}
            )
            print(f"   ❌ Exception: {str(e)}")
            return False
            
    async def test_post_processing_validation(self):
        """Test 3: POST-PROCESSING VALIDATION"""
        print("\n🔄 TESTING POST-PROCESSING VALIDATION")
        print("=" * 60)
        
        # Test with different content types to ensure no truncation
        test_cases = [
            {
                "prompt": "Tell me a very detailed story about a dragon and a princess with lots of description",
                "expected_type": "story",
                "min_words": 200
            },
            {
                "prompt": "Can you create a long educational explanation about how plants grow",
                "expected_type": "educational",
                "min_words": 150
            },
            {
                "prompt": "Please tell me an extended conversation between two friends planning an adventure",
                "expected_type": "conversation",
                "min_words": 100
            }
        ]
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Post-processing Test {i}/{total_tests}: {test_case['expected_type']}")
            
            try:
                payload = {
                    "session_id": f"{self.session_id}_postproc_{i}",
                    "user_id": self.user_id,
                    "message": test_case["prompt"]
                }
                
                async with self.session.post(f"{BACKEND_URL}/conversations/text", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        word_count = len(response_text.split())
                        content_type = data.get("content_type", "unknown")
                        
                        # Check if content wasn't truncated
                        not_truncated = word_count >= test_case["min_words"]
                        type_detected = content_type == test_case["expected_type"] or content_type != "unknown"
                        
                        test_passed = not_truncated and type_detected
                        if test_passed:
                            passed_tests += 1
                            
                        self.log_result(
                            f"Post-processing Test {i}",
                            test_passed,
                            f"Words: {word_count}, Type: {content_type}, Not truncated: {not_truncated}",
                            {
                                "prompt": test_case["prompt"],
                                "word_count": word_count,
                                "content_type": content_type,
                                "expected_type": test_case["expected_type"],
                                "min_words": test_case["min_words"],
                                "not_truncated": not_truncated
                            }
                        )
                        
                        print(f"   📊 Words: {word_count} (min: {test_case['min_words']})")
                        print(f"   🏷️ Content Type: {content_type}")
                        print(f"   ✂️ Not Truncated: {'✅' if not_truncated else '❌'}")
                        
                    else:
                        error_text = await response.text()
                        self.log_result(
                            f"Post-processing Test {i}",
                            False,
                            f"HTTP {response.status}: {error_text[:100]}",
                            {"http_status": response.status, "error": error_text}
                        )
                        print(f"   ❌ HTTP {response.status}")
                        
            except Exception as e:
                self.log_result(
                    f"Post-processing Test {i}",
                    False,
                    f"Exception: {str(e)}",
                    {"error": str(e)}
                )
                print(f"   ❌ Exception: {str(e)}")
                
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n📊 POST-PROCESSING VALIDATION SUMMARY:")
        print(f"   Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        return success_rate >= 66  # At least 2/3 should pass
        
    async def test_method_routing_validation(self):
        """Test 4: METHOD ROUTING VALIDATION"""
        print("\n🔀 TESTING METHOD ROUTING VALIDATION")
        print("=" * 60)
        
        # Test iterative generation logic by requesting short stories that should trigger continuation
        test_prompts = [
            "Tell me a short story",  # Should trigger iterative generation if too short
            "Create a brief tale",    # Should trigger iterative generation if too short
            "Quick story please"      # Should trigger iterative generation if too short
        ]
        
        passed_tests = 0
        total_tests = len(test_prompts)
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📝 Routing Test {i}/{total_tests}: '{prompt}'")
            
            try:
                payload = {
                    "session_id": f"{self.session_id}_routing_{i}",
                    "user_id": self.user_id,
                    "message": prompt
                }
                
                async with self.session.post(f"{BACKEND_URL}/conversations/text", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        word_count = len(response_text.split())
                        content_type = data.get("content_type", "unknown")
                        
                        # Check if iterative generation worked (should produce longer content)
                        iterative_worked = word_count >= 150  # Should be expanded by iterative logic
                        story_detected = content_type == "story" or "story" in response_text.lower()
                        
                        test_passed = iterative_worked and story_detected
                        if test_passed:
                            passed_tests += 1
                            
                        self.log_result(
                            f"Method Routing Test {i}",
                            test_passed,
                            f"Iterative generation: {iterative_worked}, Story detected: {story_detected}, Words: {word_count}",
                            {
                                "prompt": prompt,
                                "word_count": word_count,
                                "content_type": content_type,
                                "iterative_worked": iterative_worked,
                                "story_detected": story_detected
                            }
                        )
                        
                        print(f"   📊 Word count: {word_count}")
                        print(f"   🔄 Iterative generation: {'✅' if iterative_worked else '❌'}")
                        print(f"   📖 Story detected: {'✅' if story_detected else '❌'}")
                        
                    else:
                        error_text = await response.text()
                        self.log_result(
                            f"Method Routing Test {i}",
                            False,
                            f"HTTP {response.status}: {error_text[:100]}",
                            {"http_status": response.status}
                        )
                        print(f"   ❌ HTTP {response.status}")
                        
            except Exception as e:
                self.log_result(
                    f"Method Routing Test {i}",
                    False,
                    f"Exception: {str(e)}",
                    {"error": str(e)}
                )
                print(f"   ❌ Exception: {str(e)}")
                
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n📊 METHOD ROUTING VALIDATION SUMMARY:")
        print(f"   Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        return success_rate >= 50  # At least 50% should show iterative generation
        
    async def run_all_tests(self):
        """Run all validation tests"""
        print("🚀 CRITICAL STORY GENERATION VALIDATION AFTER FIXES")
        print("=" * 80)
        print("Testing fixes:")
        print("1. Fixed _post_process_ambient_response method truncation")
        print("2. Resolved duplicate method definitions issue")
        print("3. Added missing get_available_voices() method")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Run all tests
            test1_passed = await self.test_story_generation_length()
            test2_passed = await self.test_voice_personalities_endpoint()
            test3_passed = await self.test_post_processing_validation()
            test4_passed = await self.test_method_routing_validation()
            
            # Calculate overall results
            tests_passed = sum([test1_passed, test2_passed, test3_passed, test4_passed])
            total_tests = 4
            overall_success_rate = (tests_passed / total_tests) * 100
            
            print("\n" + "=" * 80)
            print("🎯 FINAL VALIDATION RESULTS")
            print("=" * 80)
            print(f"✅ Story Generation Length: {'PASS' if test1_passed else 'FAIL'}")
            print(f"✅ Voice Personalities Endpoint: {'PASS' if test2_passed else 'FAIL'}")
            print(f"✅ Post-Processing Validation: {'PASS' if test3_passed else 'FAIL'}")
            print(f"✅ Method Routing Validation: {'PASS' if test4_passed else 'FAIL'}")
            print(f"\n🏆 OVERALL SUCCESS RATE: {tests_passed}/{total_tests} ({overall_success_rate:.1f}%)")
            
            # Detailed findings
            print("\n📋 DETAILED FINDINGS:")
            
            # Count word-related failures
            story_failures = [r for r in self.test_results if "Story Length Test" in r["test"] and not r["success"]]
            if story_failures:
                avg_failed_words = sum([r["data"].get("word_count", 0) for r in story_failures]) / len(story_failures)
                print(f"   📉 Story length failures: {len(story_failures)} stories averaged {avg_failed_words:.0f} words")
            
            # Voice endpoint status
            voice_test = next((r for r in self.test_results if "Voice Personalities" in r["test"]), None)
            if voice_test:
                if voice_test["success"]:
                    print(f"   🎤 Voice personalities endpoint: WORKING ({voice_test['data'].get('personality_count', 0)} personalities)")
                else:
                    print(f"   🎤 Voice personalities endpoint: FAILED - {voice_test['details']}")
            
            # Post-processing status
            truncation_tests = [r for r in self.test_results if "Post-processing Test" in r["test"]]
            truncation_failures = [r for r in truncation_tests if not r["success"]]
            if truncation_failures:
                print(f"   ✂️ Post-processing truncation detected in {len(truncation_failures)}/{len(truncation_tests)} tests")
            else:
                print(f"   ✂️ No post-processing truncation detected")
            
            # Method routing status
            routing_tests = [r for r in self.test_results if "Method Routing Test" in r["test"]]
            routing_successes = [r for r in routing_tests if r["success"]]
            if routing_successes:
                print(f"   🔀 Iterative generation working in {len(routing_successes)}/{len(routing_tests)} tests")
            else:
                print(f"   🔀 Iterative generation not working properly")
            
            print("\n" + "=" * 80)
            
            if overall_success_rate >= 75:
                print("🎉 VALIDATION PASSED - Fixes are working correctly!")
                return True
            else:
                print("⚠️ VALIDATION FAILED - Critical issues remain")
                return False
                
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    validator = StoryGenerationValidator()
    success = await validator.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())