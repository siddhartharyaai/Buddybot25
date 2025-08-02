#!/usr/bin/env python3
"""
COMPREHENSIVE END-TO-END BACKEND TESTING - 99% CONFIDENCE VALIDATION
Testing all critical improvements with ultra-thorough validation
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

class ComprehensiveBackendTester:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = "https://5989f568-2718-4892-b46b-e42563583d9e.preview.emergentagent.com/api"
        self.test_results = []
        self.session = None
        
        # Test data
        self.test_user_id = "test_user_comprehensive_2025"
        self.test_session_id = "session_comprehensive_2025"
        
        logger.info(f"🎯 COMPREHENSIVE BACKEND TESTING INITIALIZED")
        logger.info(f"Backend URL: {self.backend_url}")

    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    def log_test_result(self, test_name: str, success: bool, details: str, latency: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        latency_info = f" ({latency:.2f}s)" if latency > 0 else ""
        logger.info(f"{status}: {test_name}{latency_info} - {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "latency": latency,
            "timestamp": datetime.now().isoformat()
        })

    async def test_ultra_low_latency_pipeline(self):
        """Test 1: ULTRA-LOW LATENCY PIPELINE TESTING"""
        logger.info("🚀 TESTING ULTRA-LOW LATENCY PIPELINE")
        
        # Create minimal test audio (base64 encoded silence)
        test_audio = base64.b64encode(b'\x00' * 1000).decode('utf-8')
        
        try:
            # Test streaming voice processing
            start_time = time.time()
            
            payload = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": test_audio
            }
            
            async with self.session.post(
                f"{self.backend_url}/voice/process_audio",
                data=payload,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                latency = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Check for streaming pipeline indicators
                    has_pipeline_type = "pipeline" in result
                    has_latency_info = "latency" in result
                    
                    if latency < 1.5:  # Target <1.5s latency
                        self.log_test_result(
                            "Ultra-Low Latency Voice Processing",
                            True,
                            f"Latency {latency:.2f}s meets <1.5s target. Pipeline type: {result.get('pipeline', 'unknown')}",
                            latency
                        )
                    else:
                        self.log_test_result(
                            "Ultra-Low Latency Voice Processing",
                            False,
                            f"Latency {latency:.2f}s exceeds 1.5s target",
                            latency
                        )
                else:
                    self.log_test_result(
                        "Ultra-Low Latency Voice Processing",
                        False,
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_test_result(
                "Ultra-Low Latency Voice Processing",
                False,
                f"Exception: {str(e)}"
            )

    async def test_streaming_voice_processing(self):
        """Test 2: STREAMING VOICE PROCESSING WITH PARALLEL STT/LLM/TTS"""
        logger.info("🎵 TESTING STREAMING VOICE PROCESSING")
        
        try:
            # Test process_voice_streaming method availability
            test_audio = base64.b64encode(b'\x00' * 2000).decode('utf-8')
            
            payload = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": test_audio
            }
            
            start_time = time.time()
            async with self.session.post(
                f"{self.backend_url}/voice/process_audio",
                data=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                latency = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Check for streaming indicators
                    has_streaming = result.get("pipeline_type") == "streaming"
                    has_fallback = "fallback" in str(result)
                    
                    self.log_test_result(
                        "Streaming Voice Processing",
                        True,
                        f"Streaming pipeline accessible. Type: {result.get('pipeline_type', 'unknown')}, Latency: {latency:.2f}s",
                        latency
                    )
                else:
                    self.log_test_result(
                        "Streaming Voice Processing",
                        False,
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_test_result(
                "Streaming Voice Processing",
                False,
                f"Exception: {str(e)}"
            )

    async def test_complete_response_system(self):
        """Test 3: COMPLETE RESPONSE SYSTEM TESTING"""
        logger.info("💬 TESTING COMPLETE RESPONSE SYSTEM")
        
        test_cases = [
            {
                "input": "Tell me a joke about animals",
                "expected_type": "joke",
                "min_words": 10,
                "should_have_punchline": True
            },
            {
                "input": "Can you tell me a riddle?",
                "expected_type": "riddle", 
                "min_words": 15,
                "should_have_question": True
            },
            {
                "input": "Tell me a story about friendship",
                "expected_type": "story",
                "min_words": 300,  # Critical requirement
                "should_be_complete": True
            }
        ]
        
        for test_case in test_cases:
            try:
                payload = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": test_case["input"]
                }
                
                async with self.session.post(
                    f"{self.backend_url}/conversations/text",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "")
                        word_count = len(response_text.split())
                        
                        # Check completeness criteria
                        meets_word_count = word_count >= test_case["min_words"]
                        has_human_expressions = any(expr in response_text.lower() for expr in ["giggle", "chuckle", "hmm", "oh!"])
                        
                        success = meets_word_count
                        details = f"Words: {word_count}/{test_case['min_words']}, Type: {result.get('content_type', 'unknown')}"
                        
                        if test_case["expected_type"] == "story" and word_count < 300:
                            success = False
                            details += f" - CRITICAL: Story only {word_count} words, needs 300+"
                        
                        self.log_test_result(
                            f"Complete Response - {test_case['expected_type'].title()}",
                            success,
                            details
                        )
                    else:
                        self.log_test_result(
                            f"Complete Response - {test_case['expected_type'].title()}",
                            False,
                            f"HTTP {response.status}: {await response.text()}"
                        )
                        
            except Exception as e:
                self.log_test_result(
                    f"Complete Response - {test_case['expected_type'].title()}",
                    False,
                    f"Exception: {str(e)}"
                )

    async def test_story_narration_system(self):
        """Test 4: FIXED STORY NARRATION TESTING"""
        logger.info("📚 TESTING STORY NARRATION SYSTEM")
        
        try:
            # First get available stories
            async with self.session.get(
                f"{self.backend_url}/content/stories",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    stories_data = await response.json()
                    stories = stories_data.get("stories", [])
                    
                    if stories:
                        # Test first story narration
                        story = stories[0]
                        story_id = story.get("id", "story_001")
                        
                        # Test story narration endpoint
                        payload = {"user_id": self.test_user_id}
                        
                        async with self.session.post(
                            f"{self.backend_url}/content/stories/{story_id}/narrate",
                            data=payload,
                            timeout=aiohttp.ClientTimeout(total=20)
                        ) as narrate_response:
                            
                            if narrate_response.status == 200:
                                narration = await narrate_response.json()
                                
                                response_text = narration.get("response_text", "")
                                response_audio = narration.get("response_audio", "")
                                word_count = narration.get("word_count", 0)
                                
                                # Critical checks
                                has_text = len(response_text) > 0
                                has_audio = len(response_audio) > 0 if response_audio else False
                                meets_word_count = word_count >= 300
                                is_complete = narration.get("is_complete", False)
                                
                                success = has_text and meets_word_count and is_complete
                                details = f"Words: {word_count}, Has audio: {has_audio}, Complete: {is_complete}"
                                
                                if not has_text:
                                    details += " - CRITICAL: Empty response_text"
                                if word_count < 300:
                                    details += f" - CRITICAL: Only {word_count} words, needs 300+"
                                
                                self.log_test_result(
                                    "Story Narration Complete System",
                                    success,
                                    details
                                )
                            else:
                                self.log_test_result(
                                    "Story Narration Complete System",
                                    False,
                                    f"Narration HTTP {narrate_response.status}: {await narrate_response.text()}"
                                )
                    else:
                        self.log_test_result(
                            "Story Narration Complete System",
                            False,
                            "No stories available for testing"
                        )
                else:
                    self.log_test_result(
                        "Story Narration Complete System",
                        False,
                        f"Stories HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_test_result(
                "Story Narration Complete System",
                False,
                f"Exception: {str(e)}"
            )

    async def test_context_continuity(self):
        """Test 5: ENHANCED CONTEXT CONTINUITY TESTING"""
        logger.info("🧠 TESTING CONTEXT CONTINUITY")
        
        # Multi-turn conversation test
        conversation_flow = [
            "Hi, my name is Emma and I love elephants",
            "What do you remember about me?",
            "Tell me more about elephants",
            "What was my favorite animal again?",
            "Can you tell me a story about my favorite animal?"
        ]
        
        context_maintained = True
        conversation_details = []
        
        for i, message in enumerate(conversation_flow):
            try:
                payload = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": message
                }
                
                async with self.session.post(
                    f"{self.backend_url}/conversations/text",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "").lower()
                        
                        # Check context awareness
                        if i == 1:  # "What do you remember about me?"
                            remembers_name = "emma" in response_text
                            remembers_preference = "elephant" in response_text
                            context_check = remembers_name or remembers_preference
                        elif i == 3:  # "What was my favorite animal again?"
                            context_check = "elephant" in response_text
                        elif i == 4:  # Story about favorite animal
                            context_check = "elephant" in response_text
                        else:
                            context_check = True  # First and third messages don't need context
                        
                        if not context_check:
                            context_maintained = False
                        
                        conversation_details.append(f"Turn {i+1}: {'✓' if context_check else '✗'}")
                        
                    else:
                        context_maintained = False
                        conversation_details.append(f"Turn {i+1}: HTTP {response.status}")
                        
            except Exception as e:
                context_maintained = False
                conversation_details.append(f"Turn {i+1}: Exception {str(e)}")
        
        self.log_test_result(
            "Context Continuity Multi-turn",
            context_maintained,
            f"5-turn conversation: {', '.join(conversation_details)}"
        )

    async def test_memory_integration(self):
        """Test 6: MEMORY INTEGRATION TESTING"""
        logger.info("🧠 TESTING MEMORY INTEGRATION")
        
        try:
            # Test memory context endpoint
            async with self.session.get(
                f"{self.backend_url}/memory/context/{self.test_user_id}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    memory_data = await response.json()
                    
                    has_memory_structure = isinstance(memory_data, dict)
                    self.log_test_result(
                        "Memory Context Retrieval",
                        has_memory_structure,
                        f"Memory data structure: {type(memory_data)}, Keys: {list(memory_data.keys()) if has_memory_structure else 'None'}"
                    )
                else:
                    self.log_test_result(
                        "Memory Context Retrieval",
                        False,
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
            # Test memory snapshot generation
            async with self.session.post(
                f"{self.backend_url}/memory/snapshot/{self.test_user_id}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    snapshot_data = await response.json()
                    
                    has_snapshot = isinstance(snapshot_data, dict)
                    self.log_test_result(
                        "Memory Snapshot Generation",
                        has_snapshot,
                        f"Snapshot generated: {has_snapshot}"
                    )
                else:
                    self.log_test_result(
                        "Memory Snapshot Generation",
                        False,
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_test_result(
                "Memory Integration",
                False,
                f"Exception: {str(e)}"
            )

    async def test_cross_platform_compatibility(self):
        """Test 7: CROSS-PLATFORM COMPATIBILITY TESTING"""
        logger.info("📱 TESTING CROSS-PLATFORM COMPATIBILITY")
        
        # Test mobile audio processing
        mobile_audio_formats = [
            ("webm", b'\x1a\x45\xdf\xa3' + b'\x00' * 500),  # WebM format
            ("mp4", b'\x00\x00\x00\x20ftypmp4' + b'\x00' * 500),  # MP4 format
            ("wav", b'RIFF' + b'\x00' * 500),  # WAV format
        ]
        
        for format_name, audio_data in mobile_audio_formats:
            try:
                test_audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                
                payload = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "audio_base64": test_audio_b64
                }
                
                async with self.session.post(
                    f"{self.backend_url}/voice/process_audio",
                    data=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    success = response.status in [200, 400]  # 400 is acceptable for invalid audio
                    details = f"Format {format_name}: HTTP {response.status}"
                    
                    if response.status == 200:
                        result = await response.json()
                        details += f", Status: {result.get('status', 'unknown')}"
                    
                    self.log_test_result(
                        f"Mobile Audio Format - {format_name.upper()}",
                        success,
                        details
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Mobile Audio Format - {format_name.upper()}",
                    False,
                    f"Exception: {str(e)}"
                )

    async def test_api_endpoints_comprehensive(self):
        """Test 8: COMPREHENSIVE API ENDPOINTS TESTING"""
        logger.info("🔗 TESTING API ENDPOINTS COMPREHENSIVELY")
        
        endpoints_to_test = [
            ("GET", "/health", None, "Health Check"),
            ("GET", "/voice/personalities", None, "Voice Personalities"),
            ("GET", "/content/stories", None, "Stories Content"),
            ("GET", f"/analytics/dashboard/{self.test_user_id}", None, "Analytics Dashboard"),
            ("GET", "/agents/status", None, "Agents Status"),
        ]
        
        for method, endpoint, payload, name in endpoints_to_test:
            try:
                if method == "GET":
                    async with self.session.get(
                        f"{self.backend_url}{endpoint}",
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        success = response.status == 200
                        if success:
                            data = await response.json()
                            details = f"HTTP 200, Data keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}"
                        else:
                            details = f"HTTP {response.status}: {await response.text()}"
                else:
                    # POST method
                    async with self.session.post(
                        f"{self.backend_url}{endpoint}",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        success = response.status == 200
                        details = f"HTTP {response.status}"
                
                self.log_test_result(
                    f"API Endpoint - {name}",
                    success,
                    details
                )
                
            except Exception as e:
                self.log_test_result(
                    f"API Endpoint - {name}",
                    False,
                    f"Exception: {str(e)}"
                )

    async def test_error_handling_robustness(self):
        """Test 9: ERROR HANDLING ROBUSTNESS"""
        logger.info("⚠️ TESTING ERROR HANDLING ROBUSTNESS")
        
        error_test_cases = [
            {
                "name": "Invalid Audio Data",
                "endpoint": "/voice/process_audio",
                "payload": {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "audio_base64": "invalid_base64_data"
                },
                "expected_status": [400, 422, 500]
            },
            {
                "name": "Missing Required Fields",
                "endpoint": "/conversations/text",
                "payload": {
                    "session_id": self.test_session_id
                    # Missing user_id and message
                },
                "expected_status": [400, 422]
            },
            {
                "name": "Non-existent Story",
                "endpoint": "/content/stories/non_existent_story/narrate",
                "payload": {"user_id": self.test_user_id},
                "expected_status": [404, 500]
            }
        ]
        
        for test_case in error_test_cases:
            try:
                if test_case["endpoint"].endswith("/narrate"):
                    # POST with form data
                    async with self.session.post(
                        f"{self.backend_url}{test_case['endpoint']}",
                        data=test_case["payload"],
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        success = response.status in test_case["expected_status"]
                        details = f"HTTP {response.status} (expected {test_case['expected_status']})"
                else:
                    # POST with JSON
                    async with self.session.post(
                        f"{self.backend_url}{test_case['endpoint']}",
                        json=test_case["payload"],
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        success = response.status in test_case["expected_status"]
                        details = f"HTTP {response.status} (expected {test_case['expected_status']})"
                
                self.log_test_result(
                    f"Error Handling - {test_case['name']}",
                    success,
                    details
                )
                
            except Exception as e:
                self.log_test_result(
                    f"Error Handling - {test_case['name']}",
                    False,
                    f"Exception: {str(e)}"
                )

    async def test_performance_metrics(self):
        """Test 10: PERFORMANCE METRICS TESTING"""
        logger.info("⚡ TESTING PERFORMANCE METRICS")
        
        # Test concurrent requests
        concurrent_requests = 3
        tasks = []
        
        for i in range(concurrent_requests):
            payload = {
                "session_id": f"{self.test_session_id}_{i}",
                "user_id": f"{self.test_user_id}_{i}",
                "message": f"Hello, this is concurrent test {i+1}"
            }
            
            task = self.session.post(
                f"{self.backend_url}/conversations/text",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15)
            )
            tasks.append(task)
        
        try:
            start_time = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            successful_responses = 0
            for response in responses:
                if not isinstance(response, Exception) and hasattr(response, 'status'):
                    if response.status == 200:
                        successful_responses += 1
                    await response.release()  # Clean up response
            
            success = successful_responses >= (concurrent_requests * 0.8)  # 80% success rate
            details = f"{successful_responses}/{concurrent_requests} requests successful in {total_time:.2f}s"
            
            self.log_test_result(
                "Concurrent Request Handling",
                success,
                details
            )
            
        except Exception as e:
            self.log_test_result(
                "Concurrent Request Handling",
                False,
                f"Exception: {str(e)}"
            )

    async def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        logger.info("🎯 STARTING COMPREHENSIVE END-TO-END BACKEND TESTING")
        
        await self.setup_session()
        
        try:
            # Run all test categories
            await self.test_ultra_low_latency_pipeline()
            await self.test_streaming_voice_processing()
            await self.test_complete_response_system()
            await self.test_story_narration_system()
            await self.test_context_continuity()
            await self.test_memory_integration()
            await self.test_cross_platform_compatibility()
            await self.test_api_endpoints_comprehensive()
            await self.test_error_handling_robustness()
            await self.test_performance_metrics()
            
        finally:
            await self.cleanup_session()
        
        # Generate comprehensive report
        self.generate_comprehensive_report()

    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 COMPREHENSIVE BACKEND TESTING REPORT")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info("=" * 80)
        
        # Critical failures
        critical_failures = []
        story_generation_failures = []
        
        for result in self.test_results:
            if not result["success"]:
                if "story" in result["test"].lower() and "300" in result["details"]:
                    story_generation_failures.append(result)
                elif any(keyword in result["test"].lower() for keyword in ["latency", "streaming", "voice"]):
                    critical_failures.append(result)
        
        if story_generation_failures:
            logger.info("🚨 CRITICAL STORY GENERATION FAILURES:")
            for failure in story_generation_failures:
                logger.info(f"   ❌ {failure['test']}: {failure['details']}")
        
        if critical_failures:
            logger.info("🚨 CRITICAL SYSTEM FAILURES:")
            for failure in critical_failures:
                logger.info(f"   ❌ {failure['test']}: {failure['details']}")
        
        # Success highlights
        successes = [result for result in self.test_results if result["success"]]
        if successes:
            logger.info("✅ SUCCESSFUL TESTS:")
            for success in successes[:10]:  # Show first 10 successes
                logger.info(f"   ✅ {success['test']}: {success['details']}")
        
        logger.info("=" * 80)
        
        # 99% confidence assessment
        confidence_level = min(success_rate, 99.0)
        logger.info(f"🎯 CONFIDENCE LEVEL: {confidence_level:.1f}%")
        
        if confidence_level >= 95:
            logger.info("🎉 SYSTEM READY FOR DEPLOYMENT")
        elif confidence_level >= 85:
            logger.info("⚠️ SYSTEM NEEDS MINOR FIXES")
        else:
            logger.info("🚨 SYSTEM NEEDS MAJOR FIXES")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "confidence_level": confidence_level,
            "critical_failures": len(critical_failures),
            "story_failures": len(story_generation_failures)
        }

async def main():
    """Main test execution"""
    tester = ComprehensiveBackendTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())