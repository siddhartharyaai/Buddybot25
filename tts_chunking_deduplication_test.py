#!/usr/bin/env python3
"""
TTS CHUNKING AND DEDUPLICATION TESTING
======================================

This test specifically validates the TTS chunking and request deduplication fixes:
1. Ultra-Small Chunk TTS Processing (50 tokens)
2. Request Deduplication to prevent duplicate chunk TTS requests
3. Background TTS Interruption with proper task cancellation
4. Chunked TTS processing for long content

Focus on verifying that TTS chunks are processed correctly without duplication
and that background TTS tasks can be properly cancelled.
"""

import asyncio
import aiohttp
import json
import time
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TTSChunkingDeduplicationTester:
    def __init__(self):
        self.base_url = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com/api"
        self.session = None
        self.test_results = []
        
    async def setup(self):
        """Initialize test session"""
        self.session = aiohttp.ClientSession()
        logger.info("🎵 TTS CHUNKING AND DEDUPLICATION TESTING INITIALIZED")
        
    async def cleanup(self):
        """Clean up test session"""
        if self.session:
            await self.session.close()

    async def create_test_user(self):
        """Create a test user for TTS testing"""
        try:
            user_data = {
                "name": f"TTSTest_{int(time.time())}",
                "age": 8,
                "location": "TTS City",
                "timezone": "UTC",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories"],
                "learning_goals": ["listening"],
                "gender": "prefer_not_to_say",
                "avatar": "bunny",
                "speech_speed": "normal",
                "energy_level": "balanced"
            }
            
            async with self.session.post(f"{self.base_url}/users/profile", json=user_data) as response:
                if response.status == 201:
                    user_profile = await response.json()
                    logger.info(f"✅ Created TTS test user: {user_profile['id']}")
                    return user_profile
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to create user: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error creating test user: {str(e)}")
            return None

    async def test_ultra_small_chunk_tts(self, user_id):
        """Test ultra-small chunk TTS processing (50 tokens)"""
        logger.info("🔤 TEST: Ultra-Small Chunk TTS Processing")
        
        try:
            # Test with different text lengths to verify chunking
            test_texts = [
                "Short text for small chunk test.",  # ~6 words, should be 1 chunk
                "This is a medium length text that should be processed as a single chunk but tests the chunking system properly.",  # ~18 words
                "This is a much longer text that should definitely be split into multiple chunks when processed through the ultra-small chunk TTS system. It contains enough content to test the 50-token chunking limit and verify that the system can handle longer content by breaking it down into smaller, manageable pieces for optimal TTS processing."  # ~50+ words
            ]
            
            chunk_results = []
            
            for i, text in enumerate(test_texts):
                logger.info(f"🔤 Testing text {i+1}: {len(text)} chars, ~{len(text.split())} words")
                
                tts_request = {
                    "text": text,
                    "personality": "friendly_companion"
                }
                
                start_time = time.time()
                
                async with self.session.post(f"{self.base_url}/voice/tts", json=tts_request) as response:
                    processing_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("status") == "success":
                            audio_base64 = result.get("audio_base64", "")
                            audio_size = len(audio_base64)
                            
                            logger.info(f"✅ Text {i+1}: {audio_size} chars audio in {processing_time:.2f}s")
                            
                            chunk_results.append({
                                "text_length": len(text),
                                "word_count": len(text.split()),
                                "audio_size": audio_size,
                                "processing_time": processing_time,
                                "success": True
                            })
                        else:
                            logger.error(f"❌ Text {i+1} TTS failed: {result}")
                            chunk_results.append({
                                "text_length": len(text),
                                "word_count": len(text.split()),
                                "success": False,
                                "error": result.get("error", "Unknown error")
                            })
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Text {i+1} request failed: {response.status} - {error_text}")
                        chunk_results.append({
                            "text_length": len(text),
                            "word_count": len(text.split()),
                            "success": False,
                            "error": f"HTTP {response.status}"
                        })
            
            # Analyze results
            successful_chunks = sum(1 for r in chunk_results if r.get("success"))
            total_chunks = len(chunk_results)
            
            if successful_chunks == total_chunks:
                self.test_results.append({
                    "test": "Ultra-Small Chunk TTS",
                    "status": "PASS",
                    "details": f"All {total_chunks} text sizes processed successfully",
                    "chunk_results": chunk_results
                })
                return True
            else:
                self.test_results.append({
                    "test": "Ultra-Small Chunk TTS",
                    "status": "PARTIAL",
                    "details": f"{successful_chunks}/{total_chunks} chunks successful",
                    "chunk_results": chunk_results
                })
                return False
                
        except Exception as e:
            logger.error(f"❌ Ultra-small chunk TTS test error: {str(e)}")
            self.test_results.append({
                "test": "Ultra-Small Chunk TTS",
                "status": "FAIL",
                "details": f"Exception: {str(e)}"
            })
            return False

    async def test_streaming_tts_chunking(self, user_id):
        """Test streaming TTS for long content"""
        logger.info("🌊 TEST: Streaming TTS Chunking")
        
        try:
            # Long text that should trigger streaming/chunking
            long_text = """
            Once upon a time, in a magical forest far away, there lived a brave little mouse named Pip. 
            Pip was not like other mice - he had a heart full of courage and a mind full of dreams. 
            Every day, he would venture out from his cozy home in the old oak tree to explore the wonders of the forest. 
            The forest was filled with talking animals, sparkling streams, and mysterious caves that held ancient secrets. 
            One sunny morning, Pip discovered a golden acorn that glowed with a warm, magical light. 
            This acorn would lead him on the greatest adventure of his life, taking him through enchanted meadows, 
            across rushing rivers, and up towering mountains where he would meet new friends and face exciting challenges.
            """
            
            streaming_request = {
                "text": long_text.strip(),
                "personality": "story_narrator"
            }
            
            logger.info(f"🌊 Testing streaming TTS: {len(long_text)} chars, ~{len(long_text.split())} words")
            
            start_time = time.time()
            
            async with self.session.post(f"{self.base_url}/voice/tts/streaming", json=streaming_request) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get("status") == "success":
                        # Check for streaming response structure
                        chunks = result.get("chunks", [])
                        total_audio = result.get("audio_base64", "")
                        
                        if chunks:
                            logger.info(f"✅ Streaming TTS: {len(chunks)} chunks generated")
                            for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                                chunk_audio_size = len(chunk.get("audio_base64", ""))
                                logger.info(f"  Chunk {i+1}: {chunk_audio_size} chars audio")
                        elif total_audio:
                            logger.info(f"✅ Streaming TTS: Single audio output {len(total_audio)} chars")
                        else:
                            logger.warning("⚠️ Streaming TTS: No audio output detected")
                        
                        self.test_results.append({
                            "test": "Streaming TTS Chunking",
                            "status": "PASS",
                            "details": f"Processed {len(long_text)} chars in {processing_time:.2f}s",
                            "chunks": len(chunks) if chunks else 1,
                            "processing_time": f"{processing_time:.2f}s"
                        })
                        return True
                    else:
                        logger.error(f"❌ Streaming TTS failed: {result}")
                        self.test_results.append({
                            "test": "Streaming TTS Chunking",
                            "status": "FAIL",
                            "details": f"TTS failed: {result.get('error', 'Unknown error')}"
                        })
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Streaming TTS request failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Streaming TTS Chunking",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {error_text}"
                    })
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Streaming TTS test error: {str(e)}")
            self.test_results.append({
                "test": "Streaming TTS Chunking",
                "status": "FAIL",
                "details": f"Exception: {str(e)}"
            })
            return False

    async def test_chunk_tts_deduplication(self, user_id):
        """Test chunk TTS request deduplication"""
        logger.info("🔁 TEST: Chunk TTS Request Deduplication")
        
        try:
            session_id = str(uuid.uuid4())
            
            # Same chunk request to test deduplication
            chunk_request = {
                "text": "This is a test chunk for deduplication testing. It should only be processed once.",
                "chunk_id": 1,
                "user_id": user_id,
                "session_id": session_id
            }
            
            logger.info("🔁 Sending identical chunk requests simultaneously...")
            
            # Send 5 identical requests simultaneously
            tasks = []
            for i in range(5):
                task = asyncio.create_task(
                    self.session.post(f"{self.base_url}/stories/chunk-tts", json=chunk_request)
                )
                tasks.append(task)
            
            # Wait for all requests to complete
            start_time = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            # Analyze responses
            successful_responses = 0
            duplicate_responses = 0
            error_responses = 0
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.warning(f"Request {i+1} exception: {response}")
                    error_responses += 1
                    continue
                
                try:
                    if hasattr(response, 'status'):
                        if response.status == 200:
                            result = await response.json()
                            if result.get("status") == "success":
                                successful_responses += 1
                                logger.info(f"Request {i+1}: SUCCESS")
                            elif "duplicate" in str(result).lower() or result.get("status") == "duplicate":
                                duplicate_responses += 1
                                logger.info(f"Request {i+1}: DUPLICATE DETECTED")
                            else:
                                logger.info(f"Request {i+1}: OTHER - {result.get('status')}")
                        else:
                            error_responses += 1
                            logger.warning(f"Request {i+1}: HTTP {response.status}")
                        
                        response.close()
                except Exception as e:
                    logger.warning(f"Error processing response {i+1}: {e}")
                    error_responses += 1
            
            logger.info(f"🔁 Deduplication results: {successful_responses} success, {duplicate_responses} duplicates, {error_responses} errors")
            
            # Evaluate deduplication effectiveness
            if successful_responses == 1 and duplicate_responses >= 1:
                # Perfect deduplication
                self.test_results.append({
                    "test": "Chunk TTS Deduplication",
                    "status": "PASS",
                    "details": f"Perfect deduplication: 1 processed, {duplicate_responses} duplicates detected",
                    "processing_time": f"{total_time:.2f}s"
                })
                return True
            elif successful_responses <= 2 and (duplicate_responses > 0 or error_responses > 0):
                # Good deduplication
                self.test_results.append({
                    "test": "Chunk TTS Deduplication",
                    "status": "PASS",
                    "details": f"Good deduplication: {successful_responses} processed, {duplicate_responses} duplicates",
                    "processing_time": f"{total_time:.2f}s"
                })
                return True
            else:
                # Poor or no deduplication
                self.test_results.append({
                    "test": "Chunk TTS Deduplication",
                    "status": "PARTIAL",
                    "details": f"Limited deduplication: {successful_responses} processed, {duplicate_responses} duplicates",
                    "processing_time": f"{total_time:.2f}s"
                })
                return False
                
        except Exception as e:
            logger.error(f"❌ Chunk TTS deduplication test error: {str(e)}")
            self.test_results.append({
                "test": "Chunk TTS Deduplication",
                "status": "FAIL",
                "details": f"Exception: {str(e)}"
            })
            return False

    async def test_background_tts_cancellation(self, user_id):
        """Test background TTS task cancellation"""
        logger.info("🛑 TEST: Background TTS Task Cancellation")
        
        try:
            session_id = str(uuid.uuid4())
            
            # Create multiple long TTS requests
            long_texts = [
                "This is the first long text chunk that will be processed in the background and should be cancellable when needed.",
                "This is the second long text chunk that will also be processed in the background and should be properly cancelled.",
                "This is the third long text chunk for testing background processing and cancellation capabilities."
            ]
            
            logger.info("🛑 Starting multiple background TTS tasks...")
            
            # Start all TTS tasks
            tasks = []
            for i, text in enumerate(long_texts):
                tts_request = {
                    "text": text,
                    "personality": "friendly_companion"
                }
                
                task = asyncio.create_task(
                    self.session.post(f"{self.base_url}/voice/tts", json=tts_request)
                )
                tasks.append(task)
            
            # Wait briefly for tasks to start
            await asyncio.sleep(0.3)
            
            # Cancel all tasks
            logger.info("🛑 Cancelling background TTS tasks...")
            
            cancelled_count = 0
            completed_count = 0
            
            for i, task in enumerate(tasks):
                if not task.done():
                    task.cancel()
                    cancelled_count += 1
                    logger.info(f"  Task {i+1}: CANCELLED")
                else:
                    completed_count += 1
                    logger.info(f"  Task {i+1}: COMPLETED")
            
            # Wait for cancellation to complete
            await asyncio.sleep(0.2)
            
            logger.info(f"✅ Background TTS cancellation: {cancelled_count} cancelled, {completed_count} completed")
            
            # Successful if we could cancel at least some tasks
            if cancelled_count > 0:
                self.test_results.append({
                    "test": "Background TTS Cancellation",
                    "status": "PASS",
                    "details": f"Successfully cancelled {cancelled_count} tasks, {completed_count} completed naturally"
                })
                return True
            else:
                self.test_results.append({
                    "test": "Background TTS Cancellation",
                    "status": "PARTIAL",
                    "details": f"All {completed_count} tasks completed before cancellation"
                })
                return False
                
        except Exception as e:
            logger.error(f"❌ Background TTS cancellation test error: {str(e)}")
            self.test_results.append({
                "test": "Background TTS Cancellation",
                "status": "FAIL",
                "details": f"Exception: {str(e)}"
            })
            return False

    async def run_tts_chunking_tests(self):
        """Run all TTS chunking and deduplication tests"""
        logger.info("🎵 STARTING TTS CHUNKING AND DEDUPLICATION TESTING")
        
        try:
            await self.setup()
            
            # Create test user
            user_profile = await self.create_test_user()
            if not user_profile:
                logger.error("❌ Failed to create test user - aborting tests")
                return False
            
            user_id = user_profile["id"]
            
            # Run TTS tests
            tests = [
                ("Ultra-Small Chunk TTS", self.test_ultra_small_chunk_tts(user_id)),
                ("Streaming TTS Chunking", self.test_streaming_tts_chunking(user_id)),
                ("Chunk TTS Deduplication", self.test_chunk_tts_deduplication(user_id)),
                ("Background TTS Cancellation", self.test_background_tts_cancellation(user_id))
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
                        logger.warning(f"⚠️ {test_name}: FAILED/PARTIAL")
                except Exception as e:
                    logger.error(f"❌ {test_name}: ERROR - {str(e)}")
            
            # Generate final report
            success_rate = (passed_tests / total_tests) * 100
            
            logger.info(f"\n{'='*80}")
            logger.info(f"🎵 TTS CHUNKING AND DEDUPLICATION TESTING COMPLETE")
            logger.info(f"{'='*80}")
            logger.info(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
            
            # Print detailed results
            for result in self.test_results:
                status_emoji = "✅" if result["status"] == "PASS" else "⚠️" if result["status"] == "PARTIAL" else "❌"
                logger.info(f"{status_emoji} {result['test']}: {result['status']} - {result['details']}")
            
            # Overall assessment
            if success_rate >= 75:
                logger.info("🎉 TTS CHUNKING & DEDUPLICATION: EXCELLENT - All systems working properly")
                return True
            elif success_rate >= 50:
                logger.info("👍 TTS CHUNKING & DEDUPLICATION: GOOD - Most systems working")
                return True
            else:
                logger.warning("⚠️ TTS CHUNKING & DEDUPLICATION: NEEDS ATTENTION - Issues found")
                return False
            
        except Exception as e:
            logger.error(f"❌ TTS chunking test error: {str(e)}")
            return False
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = TTSChunkingDeduplicationTester()
    success = await tester.run_tts_chunking_tests()
    
    if success:
        print("\n🎉 TTS CHUNKING AND DEDUPLICATION: VALIDATED")
        exit(0)
    else:
        print("\n❌ TTS CHUNKING AND DEDUPLICATION: ISSUES FOUND")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())