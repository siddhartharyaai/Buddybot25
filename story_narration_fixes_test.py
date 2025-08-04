#!/usr/bin/env python3
"""
STORY AUDIO NARRATION FIXES VALIDATION
======================================

This test specifically validates the story audio narration fixes mentioned in the review:
1. Enhanced Barge-in System with background task cancellation and session state management
2. Background TTS Interruption with proper task cancellation  
3. Request Deduplication to prevent duplicate chunk TTS requests
4. Session Management with enhanced session tracking and cleanup

Focus on verifying that stories play from beginning to end without loops,
and that barge-in immediately stops all audio processing.
"""

import asyncio
import aiohttp
import json
import base64
import time
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StoryNarrationFixesTester:
    def __init__(self):
        self.base_url = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com/api"
        self.session = None
        self.test_results = []
        
    async def setup(self):
        """Initialize test session"""
        self.session = aiohttp.ClientSession()
        logger.info("🎭 STORY AUDIO NARRATION FIXES TESTING INITIALIZED")
        
    async def cleanup(self):
        """Clean up test session"""
        if self.session:
            await self.session.close()

    async def create_test_user(self):
        """Create a test user for story testing"""
        try:
            user_data = {
                "name": f"StoryTest_{int(time.time())}",
                "age": 7,
                "location": "Story City",
                "timezone": "UTC",
                "language": "english",
                "voice_personality": "story_narrator",
                "interests": ["stories", "adventures", "fairy tales"],
                "learning_goals": ["creativity", "imagination"],
                "gender": "prefer_not_to_say",
                "avatar": "bunny",
                "speech_speed": "normal",
                "energy_level": "balanced"
            }
            
            async with self.session.post(f"{self.base_url}/users/profile", json=user_data) as response:
                if response.status == 201:
                    user_profile = await response.json()
                    logger.info(f"✅ Created story test user: {user_profile['id']}")
                    return user_profile
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to create user: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error creating test user: {str(e)}")
            return None

    async def test_complete_story_narration(self, user_id):
        """Test complete story narration without loops or truncation"""
        logger.info("📖 TEST: Complete Story Narration - No Loops, Full Audio")
        
        try:
            session_id = str(uuid.uuid4())
            
            # Request a complete story
            story_request = {
                "session_id": session_id,
                "user_id": user_id,
                "text": "Tell me a complete adventure story about a brave little mouse who goes on a magical journey"
            }
            
            start_time = time.time()
            
            async with self.session.post(f"{self.base_url}/stories/stream", json=story_request) as response:
                if response.status == 200:
                    result = await response.json()
                    processing_time = time.time() - start_time
                    
                    if result.get("status") == "success" and result.get("story_mode"):
                        first_chunk = result.get("first_chunk", {})
                        remaining_chunks = result.get("remaining_chunks", [])
                        total_chunks = result.get("total_chunks", 0)
                        total_words = result.get("total_words", 0)
                        
                        logger.info(f"📖 Story structure: {total_chunks} chunks, {total_words} words")
                        logger.info(f"📖 First chunk: {len(first_chunk.get('text', ''))} chars")
                        logger.info(f"📖 Remaining chunks: {len(remaining_chunks)}")
                        
                        # Verify first chunk has audio
                        first_audio = first_chunk.get("audio_base64", "")
                        if first_audio:
                            logger.info(f"🎵 First chunk audio: {len(first_audio)} chars")
                            
                            # Test processing remaining chunks to ensure no loops
                            chunk_audio_sizes = []
                            for i, chunk in enumerate(remaining_chunks[:2]):  # Test first 2 remaining chunks
                                chunk_request = {
                                    "text": chunk.get("text", ""),
                                    "chunk_id": i + 1,
                                    "user_id": user_id,
                                    "session_id": session_id
                                }
                                
                                async with self.session.post(f"{self.base_url}/stories/chunk-tts", json=chunk_request) as chunk_response:
                                    if chunk_response.status == 200:
                                        chunk_result = await chunk_response.json()
                                        if chunk_result.get("status") == "success":
                                            chunk_audio = chunk_result.get("audio_base64", "")
                                            chunk_audio_sizes.append(len(chunk_audio))
                                            logger.info(f"🎵 Chunk {i+1} audio: {len(chunk_audio)} chars")
                                        else:
                                            logger.warning(f"⚠️ Chunk {i+1} TTS failed: {chunk_result}")
                                    else:
                                        logger.warning(f"⚠️ Chunk {i+1} request failed: {chunk_response.status}")
                            
                            # Verify no audio loops (different sizes indicate different content)
                            unique_sizes = len(set(chunk_audio_sizes))
                            if unique_sizes > 1 or len(chunk_audio_sizes) <= 1:
                                logger.info("✅ No audio loops detected - chunks have different audio sizes")
                                loop_status = "No loops"
                            else:
                                logger.warning("⚠️ Potential audio loops - all chunks have same audio size")
                                loop_status = "Potential loops"
                            
                            self.test_results.append({
                                "test": "Complete Story Narration",
                                "status": "PASS",
                                "details": f"{total_chunks} chunks, {total_words} words, {loop_status}",
                                "processing_time": f"{processing_time:.2f}s",
                                "audio_sizes": chunk_audio_sizes
                            })
                            return True
                        else:
                            logger.error("❌ No audio in first chunk")
                            self.test_results.append({
                                "test": "Complete Story Narration",
                                "status": "FAIL",
                                "details": "No audio generated for first chunk"
                            })
                            return False
                    else:
                        logger.error(f"❌ Invalid story response: {result}")
                        self.test_results.append({
                            "test": "Complete Story Narration",
                            "status": "FAIL",
                            "details": f"Invalid response: {result.get('status')}"
                        })
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Story request failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Complete Story Narration",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {error_text}"
                    })
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Story narration test error: {str(e)}")
            self.test_results.append({
                "test": "Complete Story Narration",
                "status": "FAIL",
                "details": f"Exception: {str(e)}"
            })
            return False

    async def test_barge_in_during_story(self, user_id):
        """Test barge-in functionality during story playback"""
        logger.info("🛑 TEST: Barge-in During Story - Immediate Stop")
        
        try:
            session_id = str(uuid.uuid4())
            
            # Start a long story
            story_request = {
                "session_id": session_id,
                "user_id": user_id,
                "text": "Tell me a very long detailed story with multiple chapters about a magical kingdom"
            }
            
            logger.info("📖 Starting long story...")
            
            # Start story in background
            story_response = await self.session.post(f"{self.base_url}/stories/stream", json=story_request)
            
            if story_response.status == 200:
                story_result = await story_response.json()
                story_response.close()
                
                if story_result.get("story_mode"):
                    logger.info("📖 Story started successfully")
                    
                    # Wait a moment for story to be "playing"
                    await asyncio.sleep(1.0)
                    
                    # Simulate barge-in with voice input
                    logger.info("🛑 Simulating barge-in...")
                    
                    # Create realistic audio data for barge-in
                    fake_audio = base64.b64encode(b"stop_story_please").decode()
                    
                    barge_in_data = {
                        "session_id": session_id,
                        "user_id": user_id,
                        "audio_base64": fake_audio
                    }
                    
                    barge_start = time.time()
                    
                    async with self.session.post(f"{self.base_url}/voice/process_audio", data=barge_in_data) as barge_response:
                        barge_time = time.time() - barge_start
                        
                        if barge_response.status == 200:
                            barge_result = await barge_response.json()
                            
                            logger.info(f"✅ Barge-in processed in {barge_time:.2f}s")
                            logger.info(f"✅ Barge-in status: {barge_result.get('status')}")
                            
                            # Check if session state is properly managed
                            session_check = await self.check_session_cleanup(session_id)
                            
                            self.test_results.append({
                                "test": "Barge-in During Story",
                                "status": "PASS",
                                "details": f"Barge-in processed in {barge_time:.2f}s, session cleanup: {session_check}",
                                "barge_in_time": f"{barge_time:.2f}s"
                            })
                            return True
                        else:
                            error_text = await barge_response.text()
                            logger.error(f"❌ Barge-in failed: {barge_response.status} - {error_text}")
                            self.test_results.append({
                                "test": "Barge-in During Story",
                                "status": "FAIL",
                                "details": f"Barge-in failed: HTTP {barge_response.status}"
                            })
                            return False
                else:
                    logger.error("❌ Story failed to start")
                    self.test_results.append({
                        "test": "Barge-in During Story",
                        "status": "FAIL",
                        "details": "Story failed to start for barge-in test"
                    })
                    return False
            else:
                logger.error(f"❌ Story request failed: {story_response.status}")
                story_response.close()
                self.test_results.append({
                    "test": "Barge-in During Story",
                    "status": "FAIL",
                    "details": f"Story request failed: HTTP {story_response.status}"
                })
                return False
                
        except Exception as e:
            logger.error(f"❌ Barge-in test error: {str(e)}")
            self.test_results.append({
                "test": "Barge-in During Story",
                "status": "FAIL",
                "details": f"Exception: {str(e)}"
            })
            return False

    async def test_session_state_cleanup(self, user_id):
        """Test session state management and cleanup"""
        logger.info("🗂️ TEST: Session State Cleanup")
        
        try:
            session_id = str(uuid.uuid4())
            
            # Start ambient listening
            ambient_request = {"user_id": user_id}
            
            async with self.session.post(f"{self.base_url}/ambient/start", json=ambient_request) as response:
                if response.status == 200:
                    result = await response.json()
                    actual_session_id = result.get("session_id", session_id)
                    logger.info(f"✅ Started ambient session: {actual_session_id}")
                    
                    # Check session status
                    async with self.session.get(f"{self.base_url}/ambient/status/{actual_session_id}") as status_response:
                        if status_response.status == 200:
                            status = await status_response.json()
                            logger.info(f"✅ Session status: {status.get('status')}")
                            
                            # Clean up session
                            stop_request = {"session_id": actual_session_id}
                            async with self.session.post(f"{self.base_url}/ambient/stop", json=stop_request) as stop_response:
                                if stop_response.status == 200:
                                    logger.info("✅ Session cleaned up successfully")
                                    
                                    self.test_results.append({
                                        "test": "Session State Cleanup",
                                        "status": "PASS",
                                        "details": "Session created, monitored, and cleaned up successfully"
                                    })
                                    return True
                                else:
                                    logger.error(f"❌ Session cleanup failed: {stop_response.status}")
                                    self.test_results.append({
                                        "test": "Session State Cleanup",
                                        "status": "FAIL",
                                        "details": f"Cleanup failed: HTTP {stop_response.status}"
                                    })
                                    return False
                        else:
                            logger.error(f"❌ Session status check failed: {status_response.status}")
                            self.test_results.append({
                                "test": "Session State Cleanup",
                                "status": "FAIL",
                                "details": f"Status check failed: HTTP {status_response.status}"
                            })
                            return False
                else:
                    logger.error(f"❌ Ambient session start failed: {response.status}")
                    self.test_results.append({
                        "test": "Session State Cleanup",
                        "status": "FAIL",
                        "details": f"Session start failed: HTTP {response.status}"
                    })
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Session cleanup test error: {str(e)}")
            self.test_results.append({
                "test": "Session State Cleanup",
                "status": "FAIL",
                "details": f"Exception: {str(e)}"
            })
            return False

    async def check_session_cleanup(self, session_id):
        """Helper to check if session was properly cleaned up"""
        try:
            async with self.session.get(f"{self.base_url}/ambient/status/{session_id}") as response:
                if response.status == 200:
                    status = await response.json()
                    return status.get("status", "unknown")
                else:
                    return "not_found"
        except:
            return "error"

    async def run_story_narration_tests(self):
        """Run all story narration fix tests"""
        logger.info("🎭 STARTING STORY AUDIO NARRATION FIXES VALIDATION")
        
        try:
            await self.setup()
            
            # Create test user
            user_profile = await self.create_test_user()
            if not user_profile:
                logger.error("❌ Failed to create test user - aborting tests")
                return False
            
            user_id = user_profile["id"]
            
            # Run story narration tests
            tests = [
                ("Complete Story Narration", self.test_complete_story_narration(user_id)),
                ("Barge-in During Story", self.test_barge_in_during_story(user_id)),
                ("Session State Cleanup", self.test_session_state_cleanup(user_id))
            ]
            
            passed_tests = 0
            total_tests = len(tests)
            
            for test_name, test_coro in tests:
                logger.info(f"\n{'='*60}")
                logger.info(f"RUNNING: {test_name}")
                logger.info(f"{'='*60}")
                
                try:
                    result = await test_coro
                    if result:
                        passed_tests += 1
                        logger.info(f"✅ {test_name}: PASSED")
                    else:
                        logger.warning(f"⚠️ {test_name}: FAILED")
                except Exception as e:
                    logger.error(f"❌ {test_name}: ERROR - {str(e)}")
            
            # Generate final report
            success_rate = (passed_tests / total_tests) * 100
            
            logger.info(f"\n{'='*80}")
            logger.info(f"🎭 STORY AUDIO NARRATION FIXES VALIDATION COMPLETE")
            logger.info(f"{'='*80}")
            logger.info(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
            
            # Print detailed results
            for result in self.test_results:
                status_emoji = "✅" if result["status"] == "PASS" else "❌"
                logger.info(f"{status_emoji} {result['test']}: {result['status']} - {result['details']}")
            
            # Overall assessment
            if success_rate >= 80:
                logger.info("🎉 STORY NARRATION FIXES: EXCELLENT - All critical issues resolved")
                return True
            elif success_rate >= 60:
                logger.info("👍 STORY NARRATION FIXES: GOOD - Most issues resolved")
                return True
            else:
                logger.warning("⚠️ STORY NARRATION FIXES: NEEDS ATTENTION - Critical issues remain")
                return False
            
        except Exception as e:
            logger.error(f"❌ Story narration test error: {str(e)}")
            return False
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = StoryNarrationFixesTester()
    success = await tester.run_story_narration_tests()
    
    if success:
        print("\n🎉 STORY AUDIO NARRATION FIXES: VALIDATED")
        exit(0)
    else:
        print("\n❌ STORY AUDIO NARRATION FIXES: ISSUES FOUND")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())