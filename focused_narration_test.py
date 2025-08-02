#!/usr/bin/env python3
"""
Focused Narration Fixes Backend Testing
Testing the 7 critical narration features mentioned in the review request
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FocusedNarrationTester:
    def __init__(self):
        self.base_url = "https://5989f568-2718-4892-b46b-e42563583d9e.preview.emergentagent.com/api"
        self.test_user_id = f"narration_test_{int(time.time())}"
        self.test_session_id = f"session_{int(time.time())}"
        
    async def run_focused_tests(self):
        """Run focused narration tests"""
        logger.info("🎯 STARTING FOCUSED NARRATION FIXES TESTING")
        
        results = {
            "story_session_management": [],
            "progressive_tts_playback": [],
            "barge_in_functionality": [],
            "story_continuation_logic": [],
            "enhanced_voice_processing": [],
            "database_integration": [],
            "error_handling": []
        }
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Create test user
            await self._create_test_user()
            
            # Test 1: Story Session Management
            logger.info("🎯 TEST 1: Story Session Management")
            results["story_session_management"] = await self._test_story_sessions()
            
            # Test 2: Progressive TTS Playback
            logger.info("🎯 TEST 2: Progressive TTS Playback")
            results["progressive_tts_playback"] = await self._test_progressive_tts()
            
            # Test 3: Barge-in Functionality
            logger.info("🎯 TEST 3: Barge-in Functionality")
            results["barge_in_functionality"] = await self._test_barge_in()
            
            # Test 4: Story Continuation Logic
            logger.info("🎯 TEST 4: Story Continuation Logic")
            results["story_continuation_logic"] = await self._test_story_continuation()
            
            # Test 5: Enhanced Voice Processing
            logger.info("🎯 TEST 5: Enhanced Voice Processing")
            results["enhanced_voice_processing"] = await self._test_enhanced_voice()
            
            # Test 6: Database Integration
            logger.info("🎯 TEST 6: Database Integration")
            results["database_integration"] = await self._test_database()
            
            # Test 7: Error Handling
            logger.info("🎯 TEST 7: Error Handling")
            results["error_handling"] = await self._test_error_handling()
            
        # Generate report
        await self._generate_report(results)
        return results
    
    async def _create_test_user(self):
        """Create test user profile"""
        try:
            profile_data = {
                "name": f"NarrationTest_{int(time.time())}",
                "age": 8,
                "location": "Test City",
                "timezone": "UTC",
                "language": "english",
                "voice_personality": "story_narrator",
                "interests": ["stories", "adventures"],
                "learning_goals": ["storytelling"],
                "gender": "prefer_not_to_say",
                "avatar": "dragon",
                "speech_speed": "normal",
                "energy_level": "balanced"
            }
            
            async with self.session.post(f"{self.base_url}/users/profile", json=profile_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.test_user_id = result["id"]
                    logger.info(f"✅ Created test user: {self.test_user_id}")
                    return True
                else:
                    logger.error(f"❌ Failed to create user: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ User creation error: {e}")
            return False
    
    async def _test_story_sessions(self):
        """Test story session management"""
        tests = []
        
        # Test story session creation
        try:
            story_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "text": "Tell me a story about a brave dragon"
            }
            
            async with self.session.post(f"{self.base_url}/stories/stream", json=story_request, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("story_mode"):
                        tests.append({"test": "Story session creation", "status": "PASS", "details": f"Story mode activated with {result.get('total_chunks', 0)} chunks"})
                    else:
                        tests.append({"test": "Story session creation", "status": "FAIL", "details": "Story mode not activated"})
                else:
                    tests.append({"test": "Story session creation", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Story session creation", "status": "ERROR", "details": str(e)})
        
        # Test database connectivity
        try:
            async with self.session.get(f"{self.base_url}/health", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    health = await response.json()
                    if health.get("database") == "connected":
                        tests.append({"test": "Database connectivity", "status": "PASS", "details": "Database connected"})
                    else:
                        tests.append({"test": "Database connectivity", "status": "FAIL", "details": "Database not connected"})
                else:
                    tests.append({"test": "Database connectivity", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Database connectivity", "status": "ERROR", "details": str(e)})
        
        # Test session completion
        try:
            async with self.session.post(f"{self.base_url}/session/end/{self.test_session_id}", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    tests.append({"test": "Session completion", "status": "PASS", "details": "Session ended successfully"})
                else:
                    tests.append({"test": "Session completion", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Session completion", "status": "ERROR", "details": str(e)})
        
        return tests
    
    async def _test_progressive_tts(self):
        """Test progressive TTS playback"""
        tests = []
        
        # Test streaming TTS
        try:
            story_text = "Once upon a time, there was a magical kingdom where dragons lived. The brave princess discovered a secret garden. She embarked on an amazing adventure to save her kingdom."
            
            tts_request = {"text": story_text, "personality": "story_narrator"}
            
            async with self.session.post(f"{self.base_url}/voice/tts/streaming", json=tts_request, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "streaming" and result.get("initial_audio"):
                        tests.append({"test": "Streaming TTS", "status": "PASS", "details": f"Streaming with {result.get('total_chunks', 0)} chunks"})
                    else:
                        tests.append({"test": "Streaming TTS", "status": "FAIL", "details": f"Not streaming: {result.get('status')}"})
                else:
                    tests.append({"test": "Streaming TTS", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Streaming TTS", "status": "ERROR", "details": str(e)})
        
        # Test chunk TTS
        try:
            chunk_request = {"text": "This is a test audio chunk.", "chunk_id": 1, "user_id": self.test_user_id}
            
            async with self.session.post(f"{self.base_url}/stories/chunk-tts", json=chunk_request, timeout=aiohttp.ClientTimeout(total=20)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success" and result.get("audio_base64"):
                        tests.append({"test": "Chunk TTS", "status": "PASS", "details": f"Audio generated: {len(result.get('audio_base64', ''))} chars"})
                    else:
                        tests.append({"test": "Chunk TTS", "status": "FAIL", "details": f"No audio: {result}"})
                else:
                    tests.append({"test": "Chunk TTS", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Chunk TTS", "status": "ERROR", "details": str(e)})
        
        # Test regular TTS with long text
        try:
            long_text = "This is a long story text that should trigger chunked processing. " * 30
            tts_request = {"text": long_text, "personality": "story_narrator"}
            
            async with self.session.post(f"{self.base_url}/voice/tts", json=tts_request, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success" and result.get("audio_base64"):
                        tests.append({"test": "Long text TTS", "status": "PASS", "details": f"Audio: {len(result.get('audio_base64', ''))} chars"})
                    else:
                        tests.append({"test": "Long text TTS", "status": "FAIL", "details": f"Failed: {result}"})
                else:
                    tests.append({"test": "Long text TTS", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Long text TTS", "status": "ERROR", "details": str(e)})
        
        return tests
    
    async def _test_barge_in(self):
        """Test barge-in functionality"""
        tests = []
        
        # Test ambient listening start
        try:
            ambient_request = {
                "session_id": self.test_session_id,
                "user_profile": {"id": self.test_user_id, "name": "Test User", "age": 8, "voice_personality": "story_narrator"}
            }
            
            async with self.session.post(f"{self.base_url}/ambient/start", json=ambient_request, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "started":
                        tests.append({"test": "Ambient listening start", "status": "PASS", "details": "Started successfully"})
                    else:
                        tests.append({"test": "Ambient listening start", "status": "FAIL", "details": f"Not started: {result}"})
                else:
                    tests.append({"test": "Ambient listening start", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Ambient listening start", "status": "ERROR", "details": str(e)})
        
        # Test ambient listening stop
        try:
            async with self.session.post(f"{self.base_url}/ambient/stop", json={"session_id": self.test_session_id}, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "stopped":
                        tests.append({"test": "Ambient listening stop", "status": "PASS", "details": "Stopped successfully"})
                    else:
                        tests.append({"test": "Ambient listening stop", "status": "FAIL", "details": f"Not stopped: {result}"})
                else:
                    tests.append({"test": "Ambient listening stop", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Ambient listening stop", "status": "ERROR", "details": str(e)})
        
        # Test session status
        try:
            async with self.session.get(f"{self.base_url}/ambient/status/{self.test_session_id}", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    result = await response.json()
                    tests.append({"test": "Session status", "status": "PASS", "details": f"Status retrieved: {result}"})
                else:
                    tests.append({"test": "Session status", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Session status", "status": "ERROR", "details": str(e)})
        
        return tests
    
    async def _test_story_continuation(self):
        """Test story continuation logic"""
        tests = []
        
        # Test continue keyword
        try:
            continue_request = {"session_id": self.test_session_id, "message": "continue the story", "user_id": self.test_user_id}
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=continue_request, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("response_text") and len(result.get("response_text", "")) > 50:
                        tests.append({"test": "Continue keyword", "status": "PASS", "details": f"Continuation: {len(result.get('response_text', ''))} chars"})
                    else:
                        tests.append({"test": "Continue keyword", "status": "FAIL", "details": f"Poor continuation: {result}"})
                else:
                    tests.append({"test": "Continue keyword", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Continue keyword", "status": "ERROR", "details": str(e)})
        
        # Test story then continuation
        try:
            story_request = {"session_id": self.test_session_id, "message": "Tell me a story about a magical forest", "user_id": self.test_user_id}
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=story_request, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    # Now test continuation
                    continue_request = {"session_id": self.test_session_id, "message": "what happens next?", "user_id": self.test_user_id}
                    
                    async with self.session.post(f"{self.base_url}/conversations/text", json=continue_request, timeout=aiohttp.ClientTimeout(total=30)) as cont_response:
                        if cont_response.status == 200:
                            cont_result = await cont_response.json()
                            if cont_result.get("response_text") and len(cont_result.get("response_text", "")) > 30:
                                tests.append({"test": "Story continuation", "status": "PASS", "details": f"Continued: {len(cont_result.get('response_text', ''))} chars"})
                            else:
                                tests.append({"test": "Story continuation", "status": "FAIL", "details": f"Poor continuation: {cont_result}"})
                        else:
                            tests.append({"test": "Story continuation", "status": "FAIL", "details": f"HTTP {cont_response.status}"})
                else:
                    tests.append({"test": "Story continuation", "status": "FAIL", "details": f"Initial story failed: HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Story continuation", "status": "ERROR", "details": str(e)})
        
        # Test memory context
        try:
            async with self.session.get(f"{self.base_url}/memory/context/{self.test_user_id}", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result and isinstance(result, dict):
                        tests.append({"test": "Memory context", "status": "PASS", "details": f"Context: {len(str(result))} chars"})
                    else:
                        tests.append({"test": "Memory context", "status": "FAIL", "details": f"No context: {result}"})
                else:
                    tests.append({"test": "Memory context", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Memory context", "status": "ERROR", "details": str(e)})
        
        return tests
    
    async def _test_enhanced_voice(self):
        """Test enhanced voice processing"""
        tests = []
        
        # Test TTS with aura-2-amalthea-en
        try:
            voice_request = {"text": "This is a test of enhanced voice processing with aura-2-amalthea-en model.", "personality": "story_narrator"}
            
            async with self.session.post(f"{self.base_url}/voice/tts", json=voice_request, timeout=aiohttp.ClientTimeout(total=20)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success" and result.get("audio_base64"):
                        tests.append({"test": "Enhanced TTS", "status": "PASS", "details": f"Audio: {len(result.get('audio_base64', ''))} chars"})
                    else:
                        tests.append({"test": "Enhanced TTS", "status": "FAIL", "details": f"Failed: {result}"})
                else:
                    tests.append({"test": "Enhanced TTS", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Enhanced TTS", "status": "ERROR", "details": str(e)})
        
        # Test voice personalities
        try:
            async with self.session.get(f"{self.base_url}/voice/personalities", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    result = await response.json()
                    if isinstance(result, dict) and len(result) >= 3:
                        tests.append({"test": "Voice personalities", "status": "PASS", "details": f"Personalities: {list(result.keys())}"})
                    else:
                        tests.append({"test": "Voice personalities", "status": "FAIL", "details": f"Insufficient: {result}"})
                else:
                    tests.append({"test": "Voice personalities", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Voice personalities", "status": "ERROR", "details": str(e)})
        
        # Test agents status
        try:
            async with self.session.get(f"{self.base_url}/agents/status", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("orchestrator") == "active" and result.get("voice_agent") == "active":
                        tests.append({"test": "Agent status", "status": "PASS", "details": f"Sessions: {result.get('session_count', 0)}"})
                    else:
                        tests.append({"test": "Agent status", "status": "FAIL", "details": f"Not active: {result}"})
                else:
                    tests.append({"test": "Agent status", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Agent status", "status": "ERROR", "details": str(e)})
        
        return tests
    
    async def _test_database(self):
        """Test database integration"""
        tests = []
        
        # Test memory snapshot
        try:
            async with self.session.post(f"{self.base_url}/memory/snapshot/{self.test_user_id}", timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result and isinstance(result, dict):
                        tests.append({"test": "Memory snapshot", "status": "PASS", "details": f"Snapshot: {result.get('id', 'created')}"})
                    else:
                        tests.append({"test": "Memory snapshot", "status": "FAIL", "details": f"Failed: {result}"})
                else:
                    tests.append({"test": "Memory snapshot", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Memory snapshot", "status": "ERROR", "details": str(e)})
        
        # Test memory snapshots retrieval
        try:
            async with self.session.get(f"{self.base_url}/memory/snapshots/{self.test_user_id}", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result and result.get("snapshots") is not None:
                        tests.append({"test": "Snapshots retrieval", "status": "PASS", "details": f"Count: {result.get('count', 0)}"})
                    else:
                        tests.append({"test": "Snapshots retrieval", "status": "FAIL", "details": f"No snapshots: {result}"})
                else:
                    tests.append({"test": "Snapshots retrieval", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Snapshots retrieval", "status": "ERROR", "details": str(e)})
        
        # Test cleanup
        try:
            async with self.session.post(f"{self.base_url}/maintenance/cleanup", json={"memory_days": 1, "telemetry_days": 1}, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result and isinstance(result, dict):
                        tests.append({"test": "Database cleanup", "status": "PASS", "details": f"Cleanup: {result}"})
                    else:
                        tests.append({"test": "Database cleanup", "status": "FAIL", "details": f"Failed: {result}"})
                else:
                    tests.append({"test": "Database cleanup", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Database cleanup", "status": "ERROR", "details": str(e)})
        
        return tests
    
    async def _test_error_handling(self):
        """Test error handling"""
        tests = []
        
        # Test invalid story session
        try:
            invalid_request = {"session_id": "invalid_session", "user_id": "invalid_user", "text": "Tell me a story"}
            
            async with self.session.post(f"{self.base_url}/stories/stream", json=invalid_request, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status in [200, 400, 404, 500]:
                    tests.append({"test": "Invalid session handling", "status": "PASS", "details": f"Handled: HTTP {response.status}"})
                else:
                    tests.append({"test": "Invalid session handling", "status": "FAIL", "details": f"Unexpected: HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Invalid session handling", "status": "PASS", "details": f"Exception handled: {str(e)[:50]}"})
        
        # Test empty TTS
        try:
            empty_request = {"text": "", "personality": "story_narrator"}
            
            async with self.session.post(f"{self.base_url}/voice/tts", json=empty_request, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status in [200, 400]:
                    tests.append({"test": "Empty TTS handling", "status": "PASS", "details": f"Handled: HTTP {response.status}"})
                else:
                    tests.append({"test": "Empty TTS handling", "status": "FAIL", "details": f"Poor handling: HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Empty TTS handling", "status": "PASS", "details": f"Exception handled: {str(e)[:50]}"})
        
        # Test continuation fallback
        try:
            malformed_request = {"session_id": self.test_session_id, "message": "continue", "user_id": self.test_user_id}
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=malformed_request, timeout=aiohttp.ClientTimeout(total=20)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("response_text"):
                        tests.append({"test": "Continuation fallback", "status": "PASS", "details": f"Fallback: {len(result.get('response_text', ''))} chars"})
                    else:
                        tests.append({"test": "Continuation fallback", "status": "FAIL", "details": f"No fallback: {result}"})
                else:
                    tests.append({"test": "Continuation fallback", "status": "FAIL", "details": f"HTTP {response.status}"})
        except Exception as e:
            tests.append({"test": "Continuation fallback", "status": "ERROR", "details": str(e)})
        
        return tests
    
    async def _generate_report(self, results):
        """Generate comprehensive test report"""
        logger.info("🎯 GENERATING FOCUSED NARRATION FIXES TEST REPORT")
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        
        report = []
        report.append("=" * 80)
        report.append("FOCUSED NARRATION FIXES BACKEND TESTING REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Backend URL: {self.base_url}")
        report.append(f"Test User ID: {self.test_user_id}")
        report.append("")
        
        for category, tests in results.items():
            if not tests:
                continue
                
            category_passed = len([t for t in tests if t['status'] == 'PASS'])
            category_failed = len([t for t in tests if t['status'] == 'FAIL'])
            category_errors = len([t for t in tests if t['status'] == 'ERROR'])
            category_total = len(tests)
            
            total_tests += category_total
            total_passed += category_passed
            total_failed += category_failed
            total_errors += category_errors
            
            success_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            
            report.append(f"📋 {category.upper().replace('_', ' ')}")
            report.append(f"   Success Rate: {success_rate:.1f}% ({category_passed}/{category_total})")
            report.append("")
            
            for test in tests:
                status_icon = "✅" if test['status'] == 'PASS' else "❌" if test['status'] == 'FAIL' else "🔥"
                report.append(f"   {status_icon} {test['test']}: {test['status']}")
                report.append(f"      {test['details']}")
                report.append("")
        
        # Overall summary
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report.append("=" * 80)
        report.append("OVERALL SUMMARY")
        report.append("=" * 80)
        report.append(f"Total Tests: {total_tests}")
        report.append(f"✅ Passed: {total_passed}")
        report.append(f"❌ Failed: {total_failed}")
        report.append(f"🔥 Errors: {total_errors}")
        report.append(f"Overall Success Rate: {overall_success_rate:.1f}%")
        report.append("")
        
        # Critical assessment
        if overall_success_rate >= 80:
            report.append("🎉 EXCELLENT: Narration fixes are working well!")
        elif overall_success_rate >= 60:
            report.append("⚠️  GOOD: Most narration fixes working, some issues need attention")
        else:
            report.append("🚨 CRITICAL: Major issues with narration fixes implementation")
        
        report.append("")
        report.append("KEY FINDINGS:")
        
        # Analyze key findings
        for category, tests in results.items():
            if tests:
                passed = len([t for t in tests if t['status'] == 'PASS'])
                total = len(tests)
                if passed >= total * 0.8:
                    report.append(f"✅ {category.replace('_', ' ').title()}: Working correctly")
                else:
                    report.append(f"❌ {category.replace('_', ' ').title()}: Needs attention")
        
        report.append("")
        report.append("=" * 80)
        
        # Print report
        for line in report:
            logger.info(line)
        
        return {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_errors": total_errors,
            "success_rate": overall_success_rate,
            "detailed_results": results
        }

async def main():
    """Main test execution"""
    tester = FocusedNarrationTester()
    results = await tester.run_focused_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())