#!/usr/bin/env python3
"""
FINAL PRODUCTION VALIDATION TEST
Complete story generation and narration system validation with all fixes applied
Focus: Story length verification, TTS system, end-to-end pipeline, production reliability
"""

import asyncio
import aiohttp
import json
import base64
import time
import logging
from typing import Dict, Any, List
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalProductionValidationTester:
    def __init__(self):
        # Get backend URL from environment
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.base_url = line.split('=')[1].strip() + '/api'
                        break
                else:
                    self.base_url = "http://localhost:8001/api"
        except FileNotFoundError:
            self.base_url = "http://localhost:8001/api"
        
        logger.info(f"🎯 FINAL PRODUCTION VALIDATION: Using backend URL: {self.base_url}")
        
        # Test data
        self.test_user_id = f"final_validation_user_{int(time.time())}"
        self.test_session_id = f"final_validation_session_{int(time.time())}"
        
        # Test results tracking
        self.test_results = {
            "story_length_verification": [],
            "tts_system_verification": [],
            "end_to_end_pipeline": [],
            "production_reliability": [],
            "user_experience_validation": []
        }
        
        # Success criteria tracking
        self.success_criteria = {
            "stories_350_plus_words": False,
            "tts_valid_base64_audio": False,
            "no_http_400_payload_errors": False,
            "no_http_429_rate_limits": False,
            "end_to_end_story_pipeline": False,
            "all_api_endpoints_successful": False,
            "concurrent_requests_handled": False,
            "error_handling_works": False
        }

    async def make_request(self, method: str, endpoint: str, data: Dict = None, timeout: int = 30) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                if method.upper() == 'GET':
                    async with session.get(url) as response:
                        response_data = await response.json()
                        return {
                            "status_code": response.status,
                            "data": response_data,
                            "success": response.status < 400
                        }
                elif method.upper() == 'POST':
                    async with session.post(url, json=data) as response:
                        response_data = await response.json()
                        return {
                            "status_code": response.status,
                            "data": response_data,
                            "success": response.status < 400
                        }
        except asyncio.TimeoutError:
            return {"status_code": 408, "data": {"error": "Request timeout"}, "success": False}
        except Exception as e:
            return {"status_code": 500, "data": {"error": str(e)}, "success": False}

    async def test_story_length_verification(self):
        """Test 1: Story Length Verification - Stories must be 350+ words minimum"""
        logger.info("🎭 TESTING: Story Length Verification (350+ words minimum)")
        
        story_requests = [
            "Tell me a complete adventure story about a brave little mouse exploring a magical forest",
            "Create a long bedtime story about a princess who discovers a hidden kingdom underwater", 
            "Write a detailed story about a young wizard learning magic at a special school"
        ]
        
        for i, story_request in enumerate(story_requests):
            logger.info(f"📖 Testing story request {i+1}: '{story_request[:50]}...'")
            
            # Test story streaming endpoint
            result = await self.make_request('POST', '/stories/stream', {
                "session_id": f"{self.test_session_id}_{i}",
                "user_id": self.test_user_id,
                "text": story_request
            })
            
            if result["success"]:
                story_data = result["data"]
                total_words = story_data.get("total_words", 0)
                first_chunk = story_data.get("first_chunk", {})
                remaining_chunks = story_data.get("remaining_chunks", [])
                
                # Calculate total story length
                total_text = first_chunk.get("text", "")
                for chunk in remaining_chunks:
                    total_text += " " + chunk.get("text", "")
                
                actual_word_count = len(total_text.split())
                
                test_result = {
                    "story_request": story_request[:50] + "...",
                    "reported_words": total_words,
                    "actual_words": actual_word_count,
                    "meets_350_requirement": actual_word_count >= 350,
                    "chunks_count": 1 + len(remaining_chunks),
                    "status": "PASS" if actual_word_count >= 350 else "FAIL"
                }
                
                logger.info(f"📊 Story {i+1}: {actual_word_count} words, {test_result['chunks_count']} chunks - {test_result['status']}")
                
                if actual_word_count >= 350:
                    self.success_criteria["stories_350_plus_words"] = True
                    
            else:
                test_result = {
                    "story_request": story_request[:50] + "...",
                    "error": result["data"].get("error", "Unknown error"),
                    "status": "FAIL"
                }
                logger.error(f"❌ Story {i+1} failed: {test_result['error']}")
            
            self.test_results["story_length_verification"].append(test_result)
            await asyncio.sleep(1)  # Rate limiting

    async def test_tts_system_verification(self):
        """Test 2: TTS System Verification - No HTTP 400 PAYLOAD_ERROR or HTTP 429 rate limits"""
        logger.info("🔊 TESTING: TTS System Verification (No HTTP 400/429 errors)")
        
        # Test all voice personalities
        personalities_result = await self.make_request('GET', '/voice/personalities')
        
        if personalities_result["success"]:
            personalities = personalities_result["data"]
            logger.info(f"🎭 Found {len(personalities)} voice personalities")
            
            # Test TTS with each personality
            test_texts = [
                "Hello there! This is a test of the TTS system with enhanced audio generation.",
                "Once upon a time, in a magical kingdom far away, there lived a brave little dragon who loved to help others.",
                "Let me tell you an exciting story about adventure, friendship, and discovering the magic within yourself."
            ]
            
            for personality in personalities:
                if isinstance(personality, dict):
                    personality_name = personality.get("name", "unknown")
                else:
                    personality_name = str(personality)
                logger.info(f"🎵 Testing TTS with personality: {personality_name}")
                
                for i, text in enumerate(test_texts):
                    result = await self.make_request('POST', '/voice/tts', {
                        "text": text,
                        "personality": personality_name
                    })
                    
                    test_result = {
                        "personality": personality_name,
                        "text_length": len(text),
                        "status_code": result["status_code"],
                        "success": result["success"],
                        "has_audio": False,
                        "audio_size": 0,
                        "is_valid_base64": False,
                        "no_payload_error": True,
                        "no_rate_limit": True
                    }
                    
                    if result["success"]:
                        audio_base64 = result["data"].get("audio_base64", "")
                        if audio_base64:
                            test_result["has_audio"] = True
                            test_result["audio_size"] = len(audio_base64)
                            
                            # Validate base64 audio
                            try:
                                audio_bytes = base64.b64decode(audio_base64)
                                test_result["is_valid_base64"] = True
                                test_result["decoded_size"] = len(audio_bytes)
                                logger.info(f"✅ TTS Success: {personality_name} - {len(audio_bytes)} bytes audio")
                                self.success_criteria["tts_valid_base64_audio"] = True
                            except Exception as e:
                                test_result["base64_error"] = str(e)
                                logger.error(f"❌ Invalid base64 audio: {str(e)}")
                    else:
                        error_msg = result["data"].get("error", "")
                        if "PAYLOAD_ERROR" in str(error_msg):
                            test_result["no_payload_error"] = False
                            logger.error(f"❌ HTTP 400 PAYLOAD_ERROR detected: {error_msg}")
                        elif result["status_code"] == 429:
                            test_result["no_rate_limit"] = False
                            logger.error(f"❌ HTTP 429 Rate limit error detected")
                        else:
                            logger.error(f"❌ TTS Error: {error_msg}")
                    
                    self.test_results["tts_system_verification"].append(test_result)
                    await asyncio.sleep(0.5)  # Rate limiting between requests
        
        # Check success criteria
        if all(result.get("no_payload_error", False) for result in self.test_results["tts_system_verification"]):
            self.success_criteria["no_http_400_payload_errors"] = True
        
        if all(result.get("no_rate_limit", False) for result in self.test_results["tts_system_verification"]):
            self.success_criteria["no_http_429_rate_limits"] = True

    async def test_end_to_end_story_pipeline(self):
        """Test 3: End-to-End Story Pipeline - Complete story generation → TTS → audio response"""
        logger.info("🎬 TESTING: End-to-End Story Pipeline")
        
        # Test complete pipeline
        story_request = "Tell me a magical story about a young girl who discovers she can talk to animals"
        
        logger.info(f"🎭 Testing complete pipeline with: '{story_request[:50]}...'")
        
        # Step 1: Generate story with streaming
        story_result = await self.make_request('POST', '/stories/stream', {
            "session_id": self.test_session_id,
            "user_id": self.test_user_id,
            "text": story_request
        })
        
        pipeline_test = {
            "story_generation": False,
            "story_chunks": 0,
            "total_words": 0,
            "chunk_tts_success": 0,
            "chunk_tts_total": 0,
            "audio_chunks_generated": 0,
            "total_audio_size": 0,
            "pipeline_complete": False
        }
        
        if story_result["success"]:
            story_data = story_result["data"]
            pipeline_test["story_generation"] = True
            pipeline_test["total_words"] = story_data.get("total_words", 0)
            
            first_chunk = story_data.get("first_chunk", {})
            remaining_chunks = story_data.get("remaining_chunks", [])
            all_chunks = [first_chunk] + remaining_chunks
            pipeline_test["story_chunks"] = len(all_chunks)
            
            logger.info(f"📖 Story generated: {pipeline_test['total_words']} words, {pipeline_test['story_chunks']} chunks")
            
            # Step 2: Test TTS for each chunk
            for i, chunk in enumerate(all_chunks):
                chunk_text = chunk.get("text", "")
                if chunk_text:
                    pipeline_test["chunk_tts_total"] += 1
                    
                    # Test chunk TTS
                    tts_result = await self.make_request('POST', '/stories/chunk-tts', {
                        "text": chunk_text,
                        "chunk_id": i,
                        "user_id": self.test_user_id,
                        "session_id": self.test_session_id
                    })
                    
                    if tts_result["success"]:
                        audio_base64 = tts_result["data"].get("audio_base64", "")
                        if audio_base64:
                            pipeline_test["chunk_tts_success"] += 1
                            pipeline_test["audio_chunks_generated"] += 1
                            pipeline_test["total_audio_size"] += len(audio_base64)
                            logger.info(f"🎵 Chunk {i} TTS: {len(audio_base64)} chars audio")
                    else:
                        logger.error(f"❌ Chunk {i} TTS failed: {tts_result['data'].get('error', 'Unknown')}")
                    
                    await asyncio.sleep(0.5)  # Rate limiting
            
            # Check if pipeline is complete
            if (pipeline_test["story_generation"] and 
                pipeline_test["chunk_tts_success"] > 0 and
                pipeline_test["audio_chunks_generated"] > 0):
                pipeline_test["pipeline_complete"] = True
                self.success_criteria["end_to_end_story_pipeline"] = True
                logger.info("✅ End-to-end pipeline COMPLETE")
            else:
                logger.error("❌ End-to-end pipeline INCOMPLETE")
        else:
            logger.error(f"❌ Story generation failed: {story_result['data'].get('error', 'Unknown')}")
        
        self.test_results["end_to_end_pipeline"].append(pipeline_test)

    async def test_production_reliability(self):
        """Test 4: Production Reliability - Error handling and fallback mechanisms"""
        logger.info("🛡️ TESTING: Production Reliability")
        
        reliability_tests = []
        
        # Test 1: Health check
        health_result = await self.make_request('GET', '/health')
        reliability_tests.append({
            "test": "health_check",
            "success": health_result["success"],
            "status_code": health_result["status_code"]
        })
        
        # Test 2: Invalid requests handling
        invalid_story_result = await self.make_request('POST', '/stories/stream', {
            "session_id": "",  # Invalid session
            "user_id": "",     # Invalid user
            "text": ""         # Empty text
        })
        reliability_tests.append({
            "test": "invalid_request_handling",
            "success": not invalid_story_result["success"],  # Should fail gracefully
            "status_code": invalid_story_result["status_code"],
            "proper_error": invalid_story_result["status_code"] == 400
        })
        
        # Test 3: Large text handling
        large_text = "Tell me a story. " * 100  # Very long request
        large_text_result = await self.make_request('POST', '/voice/tts', {
            "text": large_text,
            "personality": "friendly_companion"
        })
        reliability_tests.append({
            "test": "large_text_handling",
            "success": large_text_result["success"],
            "status_code": large_text_result["status_code"],
            "text_length": len(large_text)
        })
        
        # Test 4: Concurrent requests
        logger.info("🔄 Testing concurrent requests...")
        concurrent_tasks = []
        for i in range(3):
            task = self.make_request('POST', '/conversations/welcome', {
                "user_id": f"{self.test_user_id}_{i}",
                "session_id": f"{self.test_session_id}_{i}"
            })
            concurrent_tasks.append(task)
        
        concurrent_results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        successful_concurrent = sum(1 for result in concurrent_results 
                                  if isinstance(result, dict) and result.get("success", False))
        
        reliability_tests.append({
            "test": "concurrent_requests",
            "total_requests": len(concurrent_tasks),
            "successful_requests": successful_concurrent,
            "success": successful_concurrent >= 2  # At least 2/3 should succeed
        })
        
        if successful_concurrent >= 2:
            self.success_criteria["concurrent_requests_handled"] = True
        
        # Check if all API endpoints are working
        endpoint_tests = [
            ("GET", "/health"),
            ("GET", "/voice/personalities"),
            ("GET", "/conversations/suggestions")
        ]
        
        successful_endpoints = 0
        for method, endpoint in endpoint_tests:
            result = await self.make_request(method, endpoint)
            if result["success"]:
                successful_endpoints += 1
        
        if successful_endpoints == len(endpoint_tests):
            self.success_criteria["all_api_endpoints_successful"] = True
        
        # Check error handling
        error_handling_works = any(test.get("proper_error", False) for test in reliability_tests)
        if error_handling_works:
            self.success_criteria["error_handling_works"] = True
        
        self.test_results["production_reliability"] = reliability_tests

    async def test_user_experience_validation(self):
        """Test 5: User Experience Validation - Complete stories with audio narration"""
        logger.info("👥 TESTING: User Experience Validation")
        
        user_scenarios = [
            {
                "scenario": "Child requests bedtime story",
                "request": "Can you tell me a bedtime story about a sleepy bunny?",
                "expected_content": "story"
            },
            {
                "scenario": "Child asks for adventure story", 
                "request": "I want an exciting adventure story with dragons!",
                "expected_content": "story"
            },
            {
                "scenario": "Child requests educational content",
                "request": "Tell me about how butterflies grow and change",
                "expected_content": "educational"
            }
        ]
        
        for scenario in user_scenarios:
            logger.info(f"👶 Testing scenario: {scenario['scenario']}")
            
            # Test story generation
            result = await self.make_request('POST', '/stories/stream', {
                "session_id": f"{self.test_session_id}_{scenario['scenario'].replace(' ', '_')}",
                "user_id": self.test_user_id,
                "text": scenario["request"]
            })
            
            scenario_result = {
                "scenario": scenario["scenario"],
                "request": scenario["request"],
                "story_generated": False,
                "appropriate_length": False,
                "audio_available": False,
                "child_appropriate": True,  # Assume true unless detected otherwise
                "complete_experience": False
            }
            
            if result["success"]:
                story_data = result["data"]
                scenario_result["story_generated"] = True
                
                total_words = story_data.get("total_words", 0)
                if total_words >= 200:  # Minimum for good user experience
                    scenario_result["appropriate_length"] = True
                
                # Check if first chunk has audio
                first_chunk = story_data.get("first_chunk", {})
                if first_chunk.get("audio_base64"):
                    scenario_result["audio_available"] = True
                
                # Complete experience check
                if (scenario_result["story_generated"] and 
                    scenario_result["appropriate_length"] and
                    scenario_result["audio_available"]):
                    scenario_result["complete_experience"] = True
                
                logger.info(f"✅ Scenario complete: {total_words} words, audio: {scenario_result['audio_available']}")
            else:
                logger.error(f"❌ Scenario failed: {result['data'].get('error', 'Unknown')}")
            
            self.test_results["user_experience_validation"].append(scenario_result)
            await asyncio.sleep(1)

    async def run_all_tests(self):
        """Run all production validation tests"""
        logger.info("🚀 STARTING FINAL PRODUCTION VALIDATION TESTS")
        start_time = time.time()
        
        try:
            # Run all test categories
            await self.test_story_length_verification()
            await self.test_tts_system_verification()
            await self.test_end_to_end_story_pipeline()
            await self.test_production_reliability()
            await self.test_user_experience_validation()
            
            # Generate final report
            await self.generate_final_report()
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {str(e)}")
        
        total_time = time.time() - start_time
        logger.info(f"⏱️ Total test execution time: {total_time:.2f} seconds")

    async def generate_final_report(self):
        """Generate comprehensive final validation report"""
        logger.info("📊 GENERATING FINAL VALIDATION REPORT")
        
        # Calculate overall success rate
        total_criteria = len(self.success_criteria)
        passed_criteria = sum(1 for passed in self.success_criteria.values() if passed)
        success_rate = (passed_criteria / total_criteria) * 100
        
        print("\n" + "="*80)
        print("🎯 FINAL PRODUCTION VALIDATION REPORT")
        print("="*80)
        
        print(f"\n📈 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_criteria}/{total_criteria} criteria passed)")
        
        print("\n🎯 SUCCESS CRITERIA STATUS:")
        for criterion, passed in self.success_criteria.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {criterion}: {status}")
        
        print("\n📊 DETAILED TEST RESULTS:")
        
        # Story Length Verification
        story_tests = self.test_results["story_length_verification"]
        if story_tests:
            passed_stories = sum(1 for test in story_tests if test.get("meets_350_requirement", False))
            print(f"\n📖 Story Length Verification: {passed_stories}/{len(story_tests)} stories meet 350+ word requirement")
            for test in story_tests:
                status = "✅" if test.get("meets_350_requirement", False) else "❌"
                words = test.get("actual_words", 0)
                print(f"  {status} {words} words - {test.get('story_request', 'Unknown')}")
        
        # TTS System Verification
        tts_tests = self.test_results["tts_system_verification"]
        if tts_tests:
            successful_tts = sum(1 for test in tts_tests if test.get("success", False))
            print(f"\n🔊 TTS System Verification: {successful_tts}/{len(tts_tests)} TTS requests successful")
            
            payload_errors = sum(1 for test in tts_tests if not test.get("no_payload_error", True))
            rate_limits = sum(1 for test in tts_tests if not test.get("no_rate_limit", True))
            print(f"  HTTP 400 PAYLOAD_ERROR count: {payload_errors}")
            print(f"  HTTP 429 Rate limit count: {rate_limits}")
        
        # End-to-End Pipeline
        pipeline_tests = self.test_results["end_to_end_pipeline"]
        if pipeline_tests:
            for test in pipeline_tests:
                status = "✅ COMPLETE" if test.get("pipeline_complete", False) else "❌ INCOMPLETE"
                print(f"\n🎬 End-to-End Pipeline: {status}")
                print(f"  Story generation: {'✅' if test.get('story_generation', False) else '❌'}")
                print(f"  Chunks generated: {test.get('story_chunks', 0)}")
                print(f"  Audio chunks: {test.get('audio_chunks_generated', 0)}/{test.get('chunk_tts_total', 0)}")
                print(f"  Total audio size: {test.get('total_audio_size', 0)} chars")
        
        # Production Reliability
        reliability_tests = self.test_results["production_reliability"]
        if reliability_tests:
            print(f"\n🛡️ Production Reliability:")
            for test in reliability_tests:
                status = "✅" if test.get("success", False) else "❌"
                print(f"  {status} {test.get('test', 'Unknown test')}")
        
        # User Experience
        ux_tests = self.test_results["user_experience_validation"]
        if ux_tests:
            complete_experiences = sum(1 for test in ux_tests if test.get("complete_experience", False))
            print(f"\n👥 User Experience: {complete_experiences}/{len(ux_tests)} scenarios provide complete experience")
            for test in ux_tests:
                status = "✅" if test.get("complete_experience", False) else "❌"
                print(f"  {status} {test.get('scenario', 'Unknown scenario')}")
        
        print("\n" + "="*80)
        
        if success_rate >= 80:
            print("🎉 FINAL ASSESSMENT: PRODUCTION READY - System meets validation criteria")
        elif success_rate >= 60:
            print("⚠️ FINAL ASSESSMENT: NEEDS MINOR FIXES - Most functionality working")
        else:
            print("❌ FINAL ASSESSMENT: NEEDS MAJOR FIXES - Critical issues detected")
        
        print("="*80)

async def main():
    """Main test execution"""
    tester = FinalProductionValidationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())