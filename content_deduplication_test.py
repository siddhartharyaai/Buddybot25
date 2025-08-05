#!/usr/bin/env python3
"""
Optimized Content Deduplication System Testing
Tests the performance improvements for content deduplication in Buddy AI companion app backend
"""

import asyncio
import aiohttp
import json
import time
import logging
import sys
from typing import Dict, List, Any
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentDeduplicationTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = None
        self.test_results = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_check(self) -> bool:
        """Test if backend is accessible"""
        try:
            async with self.session.get(f"{self.base_url}/api/health") as response:
                if response.status == 200:
                    logger.info("✅ Backend health check passed")
                    return True
                else:
                    logger.error(f"❌ Backend health check failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Backend health check error: {str(e)}")
            return False
    
    async def create_test_user(self) -> Dict[str, Any]:
        """Create a test user for deduplication testing"""
        try:
            user_data = {
                "name": "Dedup Test User",
                "age": 8,
                "location": "Test City",
                "timezone": "UTC",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "animals", "science"],
                "learning_goals": ["creativity", "knowledge"],
                "gender": "prefer_not_to_say",
                "avatar": "bunny",
                "speech_speed": "normal",
                "energy_level": "balanced"
            }
            
            async with self.session.post(f"{self.base_url}/api/users/profile", json=user_data) as response:
                if response.status == 201:
                    user_profile = await response.json()
                    logger.info(f"✅ Created test user: {user_profile['id']}")
                    return user_profile
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to create test user: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"❌ Error creating test user: {str(e)}")
            return None
    
    async def test_content_deduplication_performance(self, user_id: str) -> Dict[str, Any]:
        """Test 1: Content Deduplication Performance - Multiple similar requests rapidly"""
        logger.info("🧪 Testing Content Deduplication Performance...")
        
        # Similar text requests that should trigger deduplication
        similar_requests = [
            "Tell me about cats",
            "Can you tell me about cats?", 
            "I want to know about cats",
            "Tell me something about cats",
            "What can you tell me about cats?"
        ]
        
        session_id = f"dedup_test_{int(time.time())}"
        response_times = []
        responses = []
        deduplication_detected = 0
        timeout_issues = 0
        
        start_time = time.time()
        
        # Send requests rapidly to test timeout prevention
        for i, request_text in enumerate(similar_requests):
            request_start = time.time()
            
            try:
                request_data = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "message": request_text
                }
                
                # Set timeout to detect hanging issues
                timeout = aiohttp.ClientTimeout(total=10.0)  # 10 second timeout
                
                async with self.session.post(
                    f"{self.base_url}/api/conversations/text", 
                    json=request_data,
                    timeout=timeout
                ) as response:
                    request_time = time.time() - request_start
                    response_times.append(request_time)
                    
                    if response.status == 200:
                        response_data = await response.json()
                        response_text = response_data.get('response_text', '')
                        responses.append(response_text)
                        
                        # Check if response shows variation (indicating deduplication worked)
                        if i > 0:  # Skip first response
                            for prev_response in responses[:-1]:
                                if self._check_response_similarity(response_text, prev_response):
                                    # Similar content but should have variation
                                    if self._has_variation_markers(response_text):
                                        deduplication_detected += 1
                                        logger.info(f"🔄 Deduplication variation detected in response {i+1}")
                                    break
                        
                        logger.info(f"✅ Request {i+1} completed in {request_time:.3f}s")
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Request {i+1} failed: {response.status} - {error_text}")
                        
            except asyncio.TimeoutError:
                timeout_issues += 1
                logger.error(f"⏰ Request {i+1} timed out - potential performance issue")
            except Exception as e:
                logger.error(f"❌ Request {i+1} error: {str(e)}")
        
        total_time = time.time() - start_time
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        result = {
            "test_name": "Content Deduplication Performance",
            "total_requests": len(similar_requests),
            "successful_requests": len(responses),
            "timeout_issues": timeout_issues,
            "deduplication_detected": deduplication_detected,
            "total_time": total_time,
            "average_response_time": avg_response_time,
            "max_response_time": max(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "responses": responses[:3],  # Store first 3 responses for analysis
            "passed": timeout_issues == 0 and len(responses) >= 4  # At least 4/5 should succeed
        }
        
        logger.info(f"📊 Deduplication Performance Results:")
        logger.info(f"   - Successful requests: {result['successful_requests']}/{result['total_requests']}")
        logger.info(f"   - Timeout issues: {result['timeout_issues']}")
        logger.info(f"   - Deduplication detected: {result['deduplication_detected']} times")
        logger.info(f"   - Average response time: {result['average_response_time']:.3f}s")
        logger.info(f"   - Test passed: {result['passed']}")
        
        return result
    
    async def test_response_variation_system(self, user_id: str) -> Dict[str, Any]:
        """Test 2: Response Variation Testing - Verify 25% variation rate"""
        logger.info("🧪 Testing Response Variation System...")
        
        # Use the same request multiple times to trigger variation
        test_request = "Tell me a fun fact about elephants"
        session_id = f"variation_test_{int(time.time())}"
        
        responses = []
        variation_count = 0
        total_requests = 20  # Test with 20 requests to get statistical significance
        
        for i in range(total_requests):
            try:
                request_data = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "message": test_request
                }
                
                async with self.session.post(f"{self.base_url}/api/conversations/text", json=request_data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        response_text = response_data.get('response_text', '')
                        responses.append(response_text)
                        
                        # Check for variation markers
                        if self._has_variation_markers(response_text):
                            variation_count += 1
                            logger.info(f"🔄 Variation detected in response {i+1}")
                    else:
                        logger.error(f"❌ Request {i+1} failed: {response.status}")
                        
            except Exception as e:
                logger.error(f"❌ Request {i+1} error: {str(e)}")
        
        variation_rate = (variation_count / len(responses)) * 100 if responses else 0
        expected_rate = 25  # 25% variation rate expected
        rate_tolerance = 10  # Allow ±10% tolerance
        
        result = {
            "test_name": "Response Variation System",
            "total_requests": total_requests,
            "successful_responses": len(responses),
            "variation_count": variation_count,
            "variation_rate": variation_rate,
            "expected_rate": expected_rate,
            "rate_tolerance": rate_tolerance,
            "passed": abs(variation_rate - expected_rate) <= rate_tolerance and len(responses) >= 15
        }
        
        logger.info(f"📊 Response Variation Results:")
        logger.info(f"   - Successful responses: {result['successful_responses']}/{result['total_requests']}")
        logger.info(f"   - Variation rate: {result['variation_rate']:.1f}% (expected: {expected_rate}%)")
        logger.info(f"   - Test passed: {result['passed']}")
        
        return result
    
    async def test_memory_management(self, user_id: str) -> Dict[str, Any]:
        """Test 3: Memory Management - Verify only 3 recent responses stored"""
        logger.info("🧪 Testing Memory Management...")
        
        session_id = f"memory_test_{int(time.time())}"
        
        # Send 10 different requests to fill up memory
        test_requests = [
            "Tell me about dogs",
            "What's a fun fact about space?",
            "Tell me a joke about animals",
            "Sing me a song about friendship",
            "What can you teach me about science?",
            "Tell me a story about adventure",
            "What's your favorite color?",
            "How do birds fly?",
            "Tell me about the ocean",
            "What makes you happy?"
        ]
        
        responses = []
        memory_efficiency_indicators = []
        
        for i, request_text in enumerate(test_requests):
            try:
                request_data = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "message": request_text
                }
                
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/api/conversations/text", json=request_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        response_data = await response.json()
                        response_text = response_data.get('response_text', '')
                        responses.append({
                            'request': request_text,
                            'response': response_text,
                            'response_time': response_time
                        })
                        
                        # Memory efficiency indicator: response time should not increase significantly
                        memory_efficiency_indicators.append(response_time)
                        
                        logger.info(f"✅ Request {i+1} completed in {response_time:.3f}s")
                    else:
                        logger.error(f"❌ Request {i+1} failed: {response.status}")
                        
            except Exception as e:
                logger.error(f"❌ Request {i+1} error: {str(e)}")
        
        # Analyze memory efficiency
        if len(memory_efficiency_indicators) >= 5:
            early_avg = statistics.mean(memory_efficiency_indicators[:3])
            late_avg = statistics.mean(memory_efficiency_indicators[-3:])
            memory_growth = late_avg - early_avg
        else:
            memory_growth = 0
        
        # Test that recent similar requests still get deduplication (proving memory works)
        # Send similar request to one of the last 3
        if len(responses) >= 3:
            similar_request = "Tell me about the ocean again"  # Similar to request 9
            try:
                request_data = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "message": similar_request
                }
                
                async with self.session.post(f"{self.base_url}/api/conversations/text", json=request_data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        similar_response = response_data.get('response_text', '')
                        
                        # Check if it shows variation (proving deduplication memory works)
                        deduplication_working = self._has_variation_markers(similar_response)
                    else:
                        deduplication_working = False
            except:
                deduplication_working = False
        else:
            deduplication_working = False
        
        result = {
            "test_name": "Memory Management",
            "total_requests": len(test_requests),
            "successful_responses": len(responses),
            "memory_growth": memory_growth,
            "deduplication_memory_working": deduplication_working,
            "average_response_time": statistics.mean(memory_efficiency_indicators) if memory_efficiency_indicators else 0,
            "passed": len(responses) >= 8 and memory_growth < 0.5 and deduplication_working  # Memory growth should be minimal
        }
        
        logger.info(f"📊 Memory Management Results:")
        logger.info(f"   - Successful responses: {result['successful_responses']}/{result['total_requests']}")
        logger.info(f"   - Memory growth: {result['memory_growth']:.3f}s")
        logger.info(f"   - Deduplication memory working: {result['deduplication_memory_working']}")
        logger.info(f"   - Test passed: {result['passed']}")
        
        return result
    
    async def test_error_handling(self, user_id: str) -> Dict[str, Any]:
        """Test 4: Error Handling - Deduplication failures don't break conversation flow"""
        logger.info("🧪 Testing Error Handling...")
        
        session_id = f"error_test_{int(time.time())}"
        
        # Test various edge cases that might cause deduplication issues
        edge_case_requests = [
            "",  # Empty request
            "a",  # Very short request
            "Tell me " * 100,  # Very long repetitive request
            "🎉🎊🎈" * 20,  # Emoji-heavy request
            "Tell me about cats" * 10,  # Highly repetitive request
            "Normal request after edge cases"  # Normal request to test recovery
        ]
        
        successful_responses = 0
        error_recovery_count = 0
        conversation_flow_maintained = True
        
        for i, request_text in enumerate(edge_case_requests):
            try:
                request_data = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "message": request_text
                }
                
                async with self.session.post(f"{self.base_url}/api/conversations/text", json=request_data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        response_text = response_data.get('response_text', '')
                        
                        if response_text:  # Got a valid response
                            successful_responses += 1
                            if i > 0:  # Recovery from previous potential error
                                error_recovery_count += 1
                            logger.info(f"✅ Edge case {i+1} handled successfully")
                        else:
                            logger.warning(f"⚠️ Edge case {i+1} returned empty response")
                    elif response.status == 400 and not request_text.strip():
                        # Empty request should return 400 - this is expected
                        logger.info(f"✅ Edge case {i+1} (empty request) properly rejected")
                        successful_responses += 1
                    else:
                        logger.error(f"❌ Edge case {i+1} failed: {response.status}")
                        conversation_flow_maintained = False
                        
            except Exception as e:
                logger.error(f"❌ Edge case {i+1} error: {str(e)}")
                conversation_flow_maintained = False
        
        # Test that normal conversation continues after edge cases
        normal_request = "Tell me a simple story"
        try:
            request_data = {
                "session_id": session_id,
                "user_id": user_id,
                "message": normal_request
            }
            
            async with self.session.post(f"{self.base_url}/api/conversations/text", json=request_data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get('response_text'):
                        conversation_continues = True
                        logger.info("✅ Normal conversation continues after edge cases")
                    else:
                        conversation_continues = False
                else:
                    conversation_continues = False
        except:
            conversation_continues = False
        
        result = {
            "test_name": "Error Handling",
            "total_edge_cases": len(edge_case_requests),
            "successful_responses": successful_responses,
            "error_recovery_count": error_recovery_count,
            "conversation_flow_maintained": conversation_flow_maintained,
            "conversation_continues": conversation_continues,
            "passed": conversation_flow_maintained and conversation_continues and successful_responses >= 4
        }
        
        logger.info(f"📊 Error Handling Results:")
        logger.info(f"   - Successful responses: {result['successful_responses']}/{result['total_edge_cases']}")
        logger.info(f"   - Conversation flow maintained: {result['conversation_flow_maintained']}")
        logger.info(f"   - Conversation continues: {result['conversation_continues']}")
        logger.info(f"   - Test passed: {result['passed']}")
        
        return result
    
    async def test_overall_performance(self, user_id: str) -> Dict[str, Any]:
        """Test 5: Overall Performance - Measure response times and validate no regressions"""
        logger.info("🧪 Testing Overall Performance...")
        
        session_id = f"performance_test_{int(time.time())}"
        
        # Mix of different request types to test overall system performance
        performance_requests = [
            "Tell me a story about a brave mouse",
            "What's a fun fact about elephants?",
            "Tell me a joke about cats",
            "Help me learn about space",
            "Sing me a song about friendship",
            "Tell me about dogs",  # Similar to earlier request
            "What can you teach me about science?",
            "Tell me another story about animals",
            "What's your favorite color?",
            "How do birds fly?"
        ]
        
        response_times = []
        successful_requests = 0
        deduplication_optimizations = 0
        
        overall_start = time.time()
        
        for i, request_text in enumerate(performance_requests):
            try:
                request_data = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "message": request_text
                }
                
                request_start = time.time()
                async with self.session.post(f"{self.base_url}/api/conversations/text", json=request_data) as response:
                    request_time = time.time() - request_start
                    response_times.append(request_time)
                    
                    if response.status == 200:
                        response_data = await response.json()
                        response_text = response_data.get('response_text', '')
                        
                        if response_text:
                            successful_requests += 1
                            
                            # Check if deduplication optimization was applied
                            if self._has_variation_markers(response_text):
                                deduplication_optimizations += 1
                            
                            logger.info(f"✅ Performance request {i+1} completed in {request_time:.3f}s")
                        else:
                            logger.warning(f"⚠️ Performance request {i+1} returned empty response")
                    else:
                        logger.error(f"❌ Performance request {i+1} failed: {response.status}")
                        
            except Exception as e:
                logger.error(f"❌ Performance request {i+1} error: {str(e)}")
        
        total_time = time.time() - overall_start
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 1 else max_response_time
        else:
            avg_response_time = max_response_time = min_response_time = p95_response_time = 0
        
        # Performance criteria
        performance_target = 5.0  # 5 seconds average response time
        p95_target = 10.0  # 95th percentile under 10 seconds
        
        result = {
            "test_name": "Overall Performance",
            "total_requests": len(performance_requests),
            "successful_requests": successful_requests,
            "deduplication_optimizations": deduplication_optimizations,
            "total_time": total_time,
            "average_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "p95_response_time": p95_response_time,
            "performance_target": performance_target,
            "p95_target": p95_target,
            "passed": (avg_response_time <= performance_target and 
                      p95_response_time <= p95_target and 
                      successful_requests >= 8)
        }
        
        logger.info(f"📊 Overall Performance Results:")
        logger.info(f"   - Successful requests: {result['successful_requests']}/{result['total_requests']}")
        logger.info(f"   - Average response time: {result['average_response_time']:.3f}s (target: {performance_target}s)")
        logger.info(f"   - 95th percentile: {result['p95_response_time']:.3f}s (target: {p95_target}s)")
        logger.info(f"   - Deduplication optimizations: {result['deduplication_optimizations']}")
        logger.info(f"   - Test passed: {result['passed']}")
        
        return result
    
    def _check_response_similarity(self, response1: str, response2: str) -> bool:
        """Check if two responses are similar (simplified version of backend logic)"""
        if not response1 or not response2:
            return False
            
        # Simple word overlap check
        words1 = set(response1.lower().split())
        words2 = set(response2.lower().split())
        
        if len(words1) < 5 or len(words2) < 5:
            return False
            
        intersection = len(words1.intersection(words2))
        overlap = intersection / min(len(words1), len(words2))
        
        return overlap > 0.6
    
    def _has_variation_markers(self, response: str) -> bool:
        """Check if response has variation markers indicating deduplication was applied"""
        variation_markers = [
            "Here's another way to think about it",
            "What do you think about that",
            "Let me share this with you",
            "Does that sound interesting",
            "Here's something cool",
            "Want to explore this more"
        ]
        
        return any(marker in response for marker in variation_markers)
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all content deduplication tests"""
        logger.info("🚀 Starting Optimized Content Deduplication System Testing...")
        
        # Check backend health
        if not await self.test_health_check():
            return {"error": "Backend health check failed"}
        
        # Create test user
        user_profile = await self.create_test_user()
        if not user_profile:
            return {"error": "Failed to create test user"}
        
        user_id = user_profile['id']
        
        # Run all tests
        test_results = {}
        
        try:
            test_results['deduplication_performance'] = await self.test_content_deduplication_performance(user_id)
            await asyncio.sleep(1)  # Brief pause between tests
            
            test_results['response_variation'] = await self.test_response_variation_system(user_id)
            await asyncio.sleep(1)
            
            test_results['memory_management'] = await self.test_memory_management(user_id)
            await asyncio.sleep(1)
            
            test_results['error_handling'] = await self.test_error_handling(user_id)
            await asyncio.sleep(1)
            
            test_results['overall_performance'] = await self.test_overall_performance(user_id)
            
        except Exception as e:
            logger.error(f"❌ Test execution error: {str(e)}")
            test_results['execution_error'] = str(e)
        
        # Calculate overall results
        passed_tests = sum(1 for result in test_results.values() 
                          if isinstance(result, dict) and result.get('passed', False))
        total_tests = len([r for r in test_results.values() if isinstance(r, dict) and 'passed' in r])
        
        overall_result = {
            "test_suite": "Optimized Content Deduplication System",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "overall_passed": passed_tests >= 4,  # At least 4/5 tests should pass
            "test_results": test_results,
            "user_id": user_id
        }
        
        logger.info(f"🏁 Testing Complete!")
        logger.info(f"📊 Overall Results: {passed_tests}/{total_tests} tests passed ({overall_result['success_rate']:.1f}%)")
        logger.info(f"🎯 Overall Status: {'✅ PASSED' if overall_result['overall_passed'] else '❌ FAILED'}")
        
        return overall_result

async def main():
    """Main test execution"""
    # Get backend URL from environment or use default
    import os
    backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com')
    
    logger.info(f"🎯 Testing backend at: {backend_url}")
    
    async with ContentDeduplicationTester(backend_url) as tester:
        results = await tester.run_all_tests()
        
        # Print detailed results
        print("\n" + "="*80)
        print("OPTIMIZED CONTENT DEDUPLICATION SYSTEM TEST RESULTS")
        print("="*80)
        
        if "error" in results:
            print(f"❌ CRITICAL ERROR: {results['error']}")
            return 1
        
        print(f"📊 Test Suite: {results['test_suite']}")
        print(f"🎯 Overall Status: {'✅ PASSED' if results['overall_passed'] else '❌ FAILED'}")
        print(f"📈 Success Rate: {results['success_rate']:.1f}% ({results['passed_tests']}/{results['total_tests']})")
        print()
        
        # Detailed test results
        for test_name, test_result in results['test_results'].items():
            if isinstance(test_result, dict) and 'passed' in test_result:
                status = "✅ PASSED" if test_result['passed'] else "❌ FAILED"
                print(f"{status} - {test_result['test_name']}")
                
                # Show key metrics for each test
                if test_name == 'deduplication_performance':
                    print(f"   • Timeout issues: {test_result['timeout_issues']}")
                    print(f"   • Avg response time: {test_result['average_response_time']:.3f}s")
                    print(f"   • Deduplication detected: {test_result['deduplication_detected']} times")
                elif test_name == 'response_variation':
                    print(f"   • Variation rate: {test_result['variation_rate']:.1f}% (expected: 25%)")
                elif test_name == 'memory_management':
                    print(f"   • Memory growth: {test_result['memory_growth']:.3f}s")
                    print(f"   • Deduplication memory: {'✅' if test_result['deduplication_memory_working'] else '❌'}")
                elif test_name == 'error_handling':
                    print(f"   • Conversation flow: {'✅' if test_result['conversation_flow_maintained'] else '❌'}")
                elif test_name == 'overall_performance':
                    print(f"   • Avg response time: {test_result['average_response_time']:.3f}s")
                    print(f"   • 95th percentile: {test_result['p95_response_time']:.3f}s")
                print()
        
        print("="*80)
        
        return 0 if results['overall_passed'] else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)