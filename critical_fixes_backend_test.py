#!/usr/bin/env python3
"""
CRITICAL BACKEND RE-TEST AFTER FIXES - VALIDATE ALL SYSTEMS
Testing the critical fixes mentioned in the review request:
1. UserProfile Error Fix - Test story narration endpoint
2. Increased Token Limits - Test 4000 tokens (300+ words)
3. Complete Story Generation - Verify not truncated at 62 words
4. Story Narration Endpoint - Test returns complete response_text
5. Ultra-Low Latency Pipeline
6. Complete Response System
7. Context Continuity
8. Memory Integration
9. All API Endpoints
10. Error Handling
"""

import asyncio
import aiohttp
import json
import base64
import time
import os
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://0e5dcf5a-4e8d-4074-9227-19f4607bd0be.preview.emergentagent.com/api"

class CriticalFixesBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.user_id = "test_user_critical_fixes"
        self.session_id = f"session_{int(time.time())}"
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print("🚀 CRITICAL BACKEND RE-TEST AFTER FIXES - STARTING")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User ID: {self.user_id}")
        print(f"Session ID: {self.session_id}")
        print("=" * 80)
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, details, critical=False):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        priority = "🔥 CRITICAL" if critical else "📋 TEST"
        
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "critical": critical,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        print(f"{priority} {status}: {test_name}")
        if isinstance(details, dict):
            for key, value in details.items():
                print(f"    {key}: {value}")
        else:
            print(f"    {details}")
        print()
        
    async def test_health_check(self):
        """Test basic health check"""
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Health Check", True, {
                        "status": data.get("status"),
                        "orchestrator": data.get("agents", {}).get("orchestrator"),
                        "gemini_configured": data.get("agents", {}).get("gemini_configured"),
                        "deepgram_configured": data.get("agents", {}).get("deepgram_configured")
                    })
                    return True
                else:
                    self.log_result("Health Check", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Health Check", False, f"Error: {str(e)}")
            return False
            
    async def test_story_generation_length(self):
        """CRITICAL: Test story generation produces 300+ words (not 62 words)"""
        try:
            # Test story request through text conversation
            payload = {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "message": "Tell me a complete story about a brave little mouse on an adventure"
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    word_count = len(response_text.split())
                    char_count = len(response_text)
                    
                    # Check if story meets 300+ word requirement
                    meets_requirement = word_count >= 300
                    
                    self.log_result("Story Generation Length", meets_requirement, {
                        "word_count": word_count,
                        "char_count": char_count,
                        "requirement": "300+ words",
                        "meets_requirement": meets_requirement,
                        "content_type": data.get("content_type"),
                        "story_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                    }, critical=True)
                    
                    return meets_requirement
                else:
                    self.log_result("Story Generation Length", False, f"HTTP {response.status}", critical=True)
                    return False
                    
        except Exception as e:
            self.log_result("Story Generation Length", False, f"Error: {str(e)}", critical=True)
            return False
            
    async def test_story_narration_endpoint(self):
        """CRITICAL: Test story narration endpoint returns complete response_text (not empty)"""
        try:
            # First get available stories
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status != 200:
                    self.log_result("Story Narration Endpoint", False, "Could not fetch stories", critical=True)
                    return False
                    
                stories_data = await response.json()
                stories = stories_data.get("stories", [])
                
                if not stories:
                    self.log_result("Story Narration Endpoint", False, "No stories available", critical=True)
                    return False
                    
                # Test narration with first story
                story_id = stories[0]["id"]
                
                # Test story narration endpoint
                form_data = aiohttp.FormData()
                form_data.add_field('user_id', self.user_id)
                
                async with self.session.post(f"{BACKEND_URL}/content/stories/{story_id}/narrate", data=form_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        response_audio = data.get("response_audio", "")
                        word_count = len(response_text.split()) if response_text else 0
                        
                        # Check for UserProfile error
                        has_userprofile_error = "UserProfile object has no attribute" in str(data)
                        has_response_text = bool(response_text and response_text.strip())
                        has_response_audio = bool(response_audio)
                        
                        success = has_response_text and not has_userprofile_error
                        
                        self.log_result("Story Narration Endpoint", success, {
                            "story_id": story_id,
                            "has_response_text": has_response_text,
                            "has_response_audio": has_response_audio,
                            "word_count": word_count,
                            "userprofile_error": has_userprofile_error,
                            "status": data.get("status"),
                            "response_preview": response_text[:100] + "..." if response_text else "EMPTY"
                        }, critical=True)
                        
                        return success
                    else:
                        response_text = await response.text()
                        self.log_result("Story Narration Endpoint", False, {
                            "http_status": response.status,
                            "response": response_text[:200]
                        }, critical=True)
                        return False
                        
        except Exception as e:
            self.log_result("Story Narration Endpoint", False, f"Error: {str(e)}", critical=True)
            return False
            
    async def test_multi_turn_conversation(self):
        """CRITICAL: Test multi-turn conversations without timeout exceptions"""
        try:
            conversations = [
                "Hi there!",
                "Tell me a riddle",
                "That's funny, tell me another one",
                "Can you tell me a joke instead?"
            ]
            
            all_success = True
            conversation_results = []
            
            for i, message in enumerate(conversations):
                payload = {
                    "session_id": self.session_id,
                    "user_id": self.user_id,
                    "message": message
                }
                
                try:
                    async with self.session.post(f"{BACKEND_URL}/conversations/text", json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            response_text = data.get("response_text", "")
                            word_count = len(response_text.split())
                            
                            conversation_results.append({
                                "turn": i + 1,
                                "message": message,
                                "response_words": word_count,
                                "content_type": data.get("content_type"),
                                "success": True
                            })
                        else:
                            conversation_results.append({
                                "turn": i + 1,
                                "message": message,
                                "error": f"HTTP {response.status}",
                                "success": False
                            })
                            all_success = False
                            
                except Exception as turn_error:
                    conversation_results.append({
                        "turn": i + 1,
                        "message": message,
                        "error": str(turn_error),
                        "success": False
                    })
                    all_success = False
                    
                # Small delay between turns
                await asyncio.sleep(0.5)
                
            self.log_result("Multi-turn Conversation", all_success, {
                "total_turns": len(conversations),
                "successful_turns": sum(1 for r in conversation_results if r["success"]),
                "conversation_flow": conversation_results
            }, critical=True)
            
            return all_success
            
        except Exception as e:
            self.log_result("Multi-turn Conversation", False, f"Error: {str(e)}", critical=True)
            return False
            
    async def test_complete_response_system(self):
        """Test riddles, jokes, and conversations for completeness"""
        try:
            test_requests = [
                {"message": "Tell me a riddle", "expected_type": "riddle"},
                {"message": "Tell me a joke", "expected_type": "joke"},
                {"message": "Let's have a conversation", "expected_type": "conversation"}
            ]
            
            all_success = True
            results = []
            
            for test_req in test_requests:
                payload = {
                    "session_id": self.session_id,
                    "user_id": self.user_id,
                    "message": test_req["message"]
                }
                
                try:
                    async with self.session.post(f"{BACKEND_URL}/conversations/text", json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            response_text = data.get("response_text", "")
                            word_count = len(response_text.split())
                            
                            # Check if response is complete (not truncated)
                            is_complete = word_count >= 10  # Minimum reasonable response
                            
                            results.append({
                                "request": test_req["message"],
                                "word_count": word_count,
                                "content_type": data.get("content_type"),
                                "is_complete": is_complete,
                                "success": is_complete
                            })
                            
                            if not is_complete:
                                all_success = False
                        else:
                            results.append({
                                "request": test_req["message"],
                                "error": f"HTTP {response.status}",
                                "success": False
                            })
                            all_success = False
                            
                except Exception as req_error:
                    results.append({
                        "request": test_req["message"],
                        "error": str(req_error),
                        "success": False
                    })
                    all_success = False
                    
            self.log_result("Complete Response System", all_success, {
                "total_requests": len(test_requests),
                "successful_requests": sum(1 for r in results if r["success"]),
                "results": results
            })
            
            return all_success
            
        except Exception as e:
            self.log_result("Complete Response System", False, f"Error: {str(e)}")
            return False
            
    async def test_ultra_low_latency_pipeline(self):
        """Test ultra-low latency pipeline (<1.5s)"""
        try:
            # Create minimal audio data for testing
            audio_data = b"test_audio_data"
            audio_base64 = base64.b64encode(audio_data).decode()
            
            start_time = time.time()
            
            form_data = aiohttp.FormData()
            form_data.add_field('session_id', self.session_id)
            form_data.add_field('user_id', self.user_id)
            form_data.add_field('audio_base64', audio_base64)
            
            async with self.session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
                end_time = time.time()
                latency = end_time - start_time
                
                if response.status == 200:
                    data = await response.json()
                    meets_latency = latency < 1.5
                    
                    self.log_result("Ultra-Low Latency Pipeline", meets_latency, {
                        "latency_seconds": f"{latency:.2f}s",
                        "requirement": "<1.5s",
                        "meets_requirement": meets_latency,
                        "status": data.get("status"),
                        "pipeline_type": data.get("pipeline", "unknown")
                    })
                    
                    return meets_latency
                else:
                    # Even if processing fails, check if latency is good
                    meets_latency = latency < 1.5
                    self.log_result("Ultra-Low Latency Pipeline", meets_latency, {
                        "latency_seconds": f"{latency:.2f}s",
                        "http_status": response.status,
                        "meets_latency_requirement": meets_latency
                    })
                    return meets_latency
                    
        except Exception as e:
            self.log_result("Ultra-Low Latency Pipeline", False, f"Error: {str(e)}")
            return False
            
    async def test_memory_integration(self):
        """Test memory integration and user context"""
        try:
            # Test memory context endpoint
            async with self.session.get(f"{BACKEND_URL}/memory/context/{self.user_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Test memory snapshot generation
                    async with self.session.post(f"{BACKEND_URL}/memory/snapshot/{self.user_id}") as snapshot_response:
                        if snapshot_response.status == 200:
                            snapshot_data = await snapshot_response.json()
                            
                            self.log_result("Memory Integration", True, {
                                "memory_context_available": True,
                                "snapshot_generation": True,
                                "context_keys": list(data.keys()) if isinstance(data, dict) else "non-dict",
                                "snapshot_keys": list(snapshot_data.keys()) if isinstance(snapshot_data, dict) else "non-dict"
                            })
                            return True
                        else:
                            self.log_result("Memory Integration", False, f"Snapshot generation failed: HTTP {snapshot_response.status}")
                            return False
                else:
                    self.log_result("Memory Integration", False, f"Memory context failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_result("Memory Integration", False, f"Error: {str(e)}")
            return False
            
    async def test_all_api_endpoints(self):
        """Test all major API endpoints"""
        try:
            endpoints_to_test = [
                {"method": "GET", "url": f"{BACKEND_URL}/health", "name": "Health Check"},
                {"method": "GET", "url": f"{BACKEND_URL}/content/stories", "name": "Stories API"},
                {"method": "GET", "url": f"{BACKEND_URL}/voice/personalities", "name": "Voice Personalities"},
                {"method": "GET", "url": f"{BACKEND_URL}/analytics/global", "name": "Analytics API"},
                {"method": "GET", "url": f"{BACKEND_URL}/agents/status", "name": "Agents Status"}
            ]
            
            results = []
            all_success = True
            
            for endpoint in endpoints_to_test:
                try:
                    if endpoint["method"] == "GET":
                        async with self.session.get(endpoint["url"]) as response:
                            success = response.status == 200
                            results.append({
                                "endpoint": endpoint["name"],
                                "status": response.status,
                                "success": success
                            })
                            if not success:
                                all_success = False
                                
                except Exception as endpoint_error:
                    results.append({
                        "endpoint": endpoint["name"],
                        "error": str(endpoint_error),
                        "success": False
                    })
                    all_success = False
                    
            self.log_result("All API Endpoints", all_success, {
                "total_endpoints": len(endpoints_to_test),
                "successful_endpoints": sum(1 for r in results if r["success"]),
                "endpoint_results": results
            })
            
            return all_success
            
        except Exception as e:
            self.log_result("All API Endpoints", False, f"Error: {str(e)}")
            return False
            
    async def test_error_handling(self):
        """Test robust error handling"""
        try:
            error_tests = [
                {
                    "name": "Invalid User ID",
                    "url": f"{BACKEND_URL}/users/profile/invalid_user_id",
                    "method": "GET",
                    "expected_status": 404
                },
                {
                    "name": "Invalid Story ID",
                    "url": f"{BACKEND_URL}/content/stories/invalid_story/narrate",
                    "method": "POST",
                    "expected_status": [404, 500],
                    "form_data": {"user_id": self.user_id}
                },
                {
                    "name": "Empty Text Input",
                    "url": f"{BACKEND_URL}/conversations/text",
                    "method": "POST",
                    "expected_status": [400, 422],
                    "json_data": {"session_id": self.session_id, "user_id": self.user_id, "message": ""}
                }
            ]
            
            results = []
            all_success = True
            
            for test in error_tests:
                try:
                    if test["method"] == "GET":
                        async with self.session.get(test["url"]) as response:
                            expected_statuses = test["expected_status"] if isinstance(test["expected_status"], list) else [test["expected_status"]]
                            success = response.status in expected_statuses
                            
                            results.append({
                                "test": test["name"],
                                "expected_status": expected_statuses,
                                "actual_status": response.status,
                                "success": success
                            })
                            
                            if not success:
                                all_success = False
                                
                    elif test["method"] == "POST":
                        if "form_data" in test:
                            form_data = aiohttp.FormData()
                            for key, value in test["form_data"].items():
                                form_data.add_field(key, value)
                            async with self.session.post(test["url"], data=form_data) as response:
                                expected_statuses = test["expected_status"] if isinstance(test["expected_status"], list) else [test["expected_status"]]
                                success = response.status in expected_statuses
                                
                                results.append({
                                    "test": test["name"],
                                    "expected_status": expected_statuses,
                                    "actual_status": response.status,
                                    "success": success
                                })
                                
                                if not success:
                                    all_success = False
                        elif "json_data" in test:
                            async with self.session.post(test["url"], json=test["json_data"]) as response:
                                expected_statuses = test["expected_status"] if isinstance(test["expected_status"], list) else [test["expected_status"]]
                                success = response.status in expected_statuses
                                
                                results.append({
                                    "test": test["name"],
                                    "expected_status": expected_statuses,
                                    "actual_status": response.status,
                                    "success": success
                                })
                                
                                if not success:
                                    all_success = False
                                    
                except Exception as test_error:
                    results.append({
                        "test": test["name"],
                        "error": str(test_error),
                        "success": False
                    })
                    all_success = False
                    
            self.log_result("Error Handling", all_success, {
                "total_tests": len(error_tests),
                "successful_tests": sum(1 for r in results if r["success"]),
                "test_results": results
            })
            
            return all_success
            
        except Exception as e:
            self.log_result("Error Handling", False, f"Error: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all critical tests"""
        await self.setup()
        
        try:
            # Run all tests
            test_functions = [
                self.test_health_check,
                self.test_story_generation_length,
                self.test_story_narration_endpoint,
                self.test_multi_turn_conversation,
                self.test_complete_response_system,
                self.test_ultra_low_latency_pipeline,
                self.test_memory_integration,
                self.test_all_api_endpoints,
                self.test_error_handling
            ]
            
            for test_func in test_functions:
                await test_func()
                await asyncio.sleep(0.5)  # Small delay between tests
                
            # Generate summary
            self.generate_summary()
            
        finally:
            await self.cleanup()
            
    def generate_summary(self):
        """Generate test summary"""
        print("=" * 80)
        print("🎯 CRITICAL BACKEND RE-TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        critical_tests = [result for result in self.test_results if result.get("critical", False)]
        critical_passed = sum(1 for result in critical_tests if result["success"])
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        critical_success_rate = (critical_passed / len(critical_tests)) * 100 if critical_tests else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        print(f"🔥 CRITICAL TESTS:")
        print(f"   Critical Tests: {len(critical_tests)}")
        print(f"   Critical Passed: {critical_passed}")
        print(f"   Critical Failed: {len(critical_tests) - critical_passed}")
        print(f"   Critical Success Rate: {critical_success_rate:.1f}%")
        print()
        
        print("📋 TEST RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            critical_marker = "🔥" if result.get("critical", False) else "📋"
            print(f"   {critical_marker} {status}: {result['test']}")
            
        print()
        
        # Specific findings for critical issues
        failed_critical = [result for result in critical_tests if not result["success"]]
        if failed_critical:
            print("🚨 CRITICAL FAILURES IDENTIFIED:")
            for failure in failed_critical:
                print(f"   ❌ {failure['test']}")
                if isinstance(failure['details'], dict):
                    for key, value in failure['details'].items():
                        print(f"      {key}: {value}")
                else:
                    print(f"      {failure['details']}")
            print()
            
        # Success criteria check
        print("✅ SUCCESS CRITERIA CHECK:")
        story_length_passed = any(r["test"] == "Story Generation Length" and r["success"] for r in self.test_results)
        story_narration_passed = any(r["test"] == "Story Narration Endpoint" and r["success"] for r in self.test_results)
        multi_turn_passed = any(r["test"] == "Multi-turn Conversation" and r["success"] for r in self.test_results)
        
        print(f"   Stories generate 300+ words: {'✅' if story_length_passed else '❌'}")
        print(f"   Story narration returns complete response: {'✅' if story_narration_passed else '❌'}")
        print(f"   Multi-turn conversations work: {'✅' if multi_turn_passed else '❌'}")
        print(f"   Overall system stability: {'✅' if success_rate >= 70 else '❌'}")
        
        print()
        print("🎯 RECOMMENDATION:")
        if critical_success_rate >= 80:
            print("   ✅ CRITICAL FIXES SUCCESSFUL - System ready for frontend testing")
        elif critical_success_rate >= 60:
            print("   ⚠️  PARTIAL SUCCESS - Some critical issues remain, investigate failures")
        else:
            print("   ❌ CRITICAL FAILURES - Major issues need immediate attention")
            
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = CriticalFixesBackendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())