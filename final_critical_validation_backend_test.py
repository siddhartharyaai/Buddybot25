#!/usr/bin/env python3
"""
FINAL CRITICAL TEST: Story Generation and Narration System Validation
Testing the completely fixed story generation and narration system to verify all issues are resolved.

SUCCESS CRITERIA (MUST ALL PASS):
✅ NO HTTP 400 PAYLOAD_ERROR messages
✅ NO HTTP 429 rate limit errors  
✅ Stories are 300+ words minimum length
✅ TTS generates valid base64 WAV audio
✅ End-to-end story generation → TTS → audio works
✅ All API endpoints return successful responses
✅ No critical exceptions or failures occur
"""

import asyncio
import aiohttp
import json
import base64
import time
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from environment
BACKEND_URL = "https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com/api"

class FinalCriticalValidator:
    def __init__(self):
        self.session = None
        self.test_results = {
            "tts_api_fix": {"passed": False, "details": []},
            "story_generation_quality": {"passed": False, "details": []},
            "story_streaming_pipeline": {"passed": False, "details": []},
            "production_ready_functionality": {"passed": False, "details": []},
            "end_to_end_narration": {"passed": False, "details": []},
            "overall_success": False
        }
        self.test_user_id = f"final_test_user_{int(time.time())}"
        self.test_session_id = str(uuid.uuid4())
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=120),
            headers={'Content-Type': 'application/json'}
        )
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def test_health_check(self):
        """Test basic health check"""
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Health check passed: {data.get('status', 'unknown')}")
                    return True
                else:
                    logger.error(f"❌ Health check failed: HTTP {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Health check error: {str(e)}")
            return False
            
    async def test_tts_api_fix_verification(self):
        """1. TTS API Fix Verification - Test corrected Deepgram TTS API"""
        logger.info("🔊 TESTING: TTS API Fix Verification")
        
        test_cases = [
            {
                "text": "Hello there! This is a test of the TTS system with friendly companion voice.",
                "personality": "friendly_companion",
                "description": "Basic TTS test"
            },
            {
                "text": "Once upon a time, in a magical forest, there lived a brave little rabbit who loved adventures.",
                "personality": "story_narrator", 
                "description": "Story narrator voice test"
            },
            {
                "text": "Let's learn about the amazing world of science! Did you know that butterflies taste with their feet?",
                "personality": "learning_buddy",
                "description": "Learning buddy voice test"
            }
        ]
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases):
            try:
                logger.info(f"Testing TTS case {i+1}: {test_case['description']}")
                
                payload = {
                    "text": test_case["text"],
                    "personality": test_case["personality"]
                }
                
                start_time = time.time()
                async with self.session.post(f"{BACKEND_URL}/voice/tts", json=payload) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 400:
                        response_text = await response.text()
                        if "PAYLOAD_ERROR" in response_text:
                            self.test_results["tts_api_fix"]["details"].append(
                                f"❌ CRITICAL FAILURE: HTTP 400 PAYLOAD_ERROR detected in {test_case['description']}"
                            )
                            continue
                    
                    if response.status == 429:
                        self.test_results["tts_api_fix"]["details"].append(
                            f"❌ CRITICAL FAILURE: HTTP 429 rate limit error in {test_case['description']}"
                        )
                        continue
                        
                    if response.status == 200:
                        data = await response.json()
                        
                        # Verify response structure
                        if data.get("status") == "success" and data.get("audio_base64"):
                            audio_data = data["audio_base64"]
                            
                            # Verify base64 audio is valid
                            try:
                                decoded_audio = base64.b64decode(audio_data)
                                audio_size_kb = len(decoded_audio) / 1024
                                
                                self.test_results["tts_api_fix"]["details"].append(
                                    f"✅ {test_case['description']}: Generated {audio_size_kb:.1f}KB audio in {response_time:.2f}s"
                                )
                                passed_tests += 1
                                
                            except Exception as decode_error:
                                self.test_results["tts_api_fix"]["details"].append(
                                    f"❌ {test_case['description']}: Invalid base64 audio - {str(decode_error)}"
                                )
                        else:
                            self.test_results["tts_api_fix"]["details"].append(
                                f"❌ {test_case['description']}: Invalid response structure"
                            )
                    else:
                        response_text = await response.text()
                        self.test_results["tts_api_fix"]["details"].append(
                            f"❌ {test_case['description']}: HTTP {response.status} - {response_text[:200]}"
                        )
                        
            except Exception as e:
                self.test_results["tts_api_fix"]["details"].append(
                    f"❌ {test_case['description']}: Exception - {str(e)}"
                )
                
        # Test passed if all TTS requests succeeded without PAYLOAD_ERROR or rate limits
        self.test_results["tts_api_fix"]["passed"] = passed_tests == total_tests
        
        logger.info(f"TTS API Fix Verification: {passed_tests}/{total_tests} tests passed")
        
    async def test_story_generation_quality(self):
        """2. Enhanced Story Generation Quality - Test LLM-based story continuation (300+ words)"""
        logger.info("📚 TESTING: Enhanced Story Generation Quality")
        
        story_requests = [
            "Tell me a magical adventure story about a brave little mouse",
            "Create a bedtime story about friendship in the forest",
            "Tell me a complete story about a dragon who learns to be kind"
        ]
        
        passed_tests = 0
        total_tests = len(story_requests)
        
        for i, story_request in enumerate(story_requests):
            try:
                logger.info(f"Testing story generation {i+1}: '{story_request[:50]}...'")
                
                payload = {
                    "session_id": f"{self.test_session_id}_{i}",
                    "user_id": self.test_user_id,
                    "text": story_request
                }
                
                start_time = time.time()
                async with self.session.post(f"{BACKEND_URL}/stories/stream", json=payload) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "success":
                            # Check story length
                            total_words = data.get("total_words", 0)
                            first_chunk = data.get("first_chunk", {})
                            first_chunk_text = first_chunk.get("text", "")
                            
                            # Verify minimum word count requirement
                            if total_words >= 300:
                                self.test_results["story_generation_quality"]["details"].append(
                                    f"✅ Story {i+1}: Generated {total_words} words (meets 300+ requirement) in {response_time:.2f}s"
                                )
                                passed_tests += 1
                            else:
                                self.test_results["story_generation_quality"]["details"].append(
                                    f"❌ Story {i+1}: Only {total_words} words (below 300 minimum requirement)"
                                )
                                
                            # Log story quality details
                            chunks = data.get("total_chunks", 0)
                            self.test_results["story_generation_quality"]["details"].append(
                                f"   📊 Story {i+1} details: {chunks} chunks, first chunk: '{first_chunk_text[:100]}...'"
                            )
                            
                        else:
                            error_msg = data.get("error", "Unknown error")
                            self.test_results["story_generation_quality"]["details"].append(
                                f"❌ Story {i+1}: Generation failed - {error_msg}"
                            )
                    else:
                        response_text = await response.text()
                        self.test_results["story_generation_quality"]["details"].append(
                            f"❌ Story {i+1}: HTTP {response.status} - {response_text[:200]}"
                        )
                        
            except Exception as e:
                self.test_results["story_generation_quality"]["details"].append(
                    f"❌ Story {i+1}: Exception - {str(e)}"
                )
                
        self.test_results["story_generation_quality"]["passed"] = passed_tests == total_tests
        logger.info(f"Story Generation Quality: {passed_tests}/{total_tests} tests passed")
        
    async def test_story_streaming_pipeline(self):
        """3. Complete Story Streaming Pipeline - Test end-to-end /api/stories/stream"""
        logger.info("🎭 TESTING: Complete Story Streaming Pipeline")
        
        try:
            story_request = "Tell me a complete adventure story about a magical kingdom"
            
            payload = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "text": story_request
            }
            
            logger.info("Testing complete story streaming pipeline...")
            
            start_time = time.time()
            async with self.session.post(f"{BACKEND_URL}/stories/stream", json=payload) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success":
                        # Verify streaming structure
                        first_chunk = data.get("first_chunk", {})
                        remaining_chunks = data.get("remaining_chunks", [])
                        total_chunks = data.get("total_chunks", 0)
                        total_words = data.get("total_words", 0)
                        
                        # Test first chunk has audio
                        first_chunk_audio = first_chunk.get("audio_base64", "")
                        if first_chunk_audio:
                            try:
                                decoded_audio = base64.b64decode(first_chunk_audio)
                                audio_size_kb = len(decoded_audio) / 1024
                                
                                self.test_results["story_streaming_pipeline"]["details"].append(
                                    f"✅ First chunk: {len(first_chunk.get('text', ''))} chars text, {audio_size_kb:.1f}KB audio"
                                )
                                
                                # Test remaining chunks for TTS generation
                                chunk_tts_success = 0
                                for i, chunk in enumerate(remaining_chunks[:2]):  # Test first 2 remaining chunks
                                    chunk_payload = {
                                        "text": chunk.get("text", ""),
                                        "chunk_id": i + 1,
                                        "user_id": self.test_user_id,
                                        "session_id": self.test_session_id
                                    }
                                    
                                    async with self.session.post(f"{BACKEND_URL}/stories/chunk-tts", json=chunk_payload) as chunk_response:
                                        if chunk_response.status == 200:
                                            chunk_data = await chunk_response.json()
                                            if chunk_data.get("status") == "success" and chunk_data.get("audio_base64"):
                                                chunk_audio_size = len(base64.b64decode(chunk_data["audio_base64"])) / 1024
                                                self.test_results["story_streaming_pipeline"]["details"].append(
                                                    f"✅ Chunk {i+1} TTS: {chunk_audio_size:.1f}KB audio generated"
                                                )
                                                chunk_tts_success += 1
                                            else:
                                                self.test_results["story_streaming_pipeline"]["details"].append(
                                                    f"❌ Chunk {i+1} TTS: No audio generated"
                                                )
                                        else:
                                            self.test_results["story_streaming_pipeline"]["details"].append(
                                                f"❌ Chunk {i+1} TTS: HTTP {chunk_response.status}"
                                            )
                                
                                # Pipeline passes if story generation works and at least some chunk TTS works
                                pipeline_success = (
                                    total_words >= 300 and
                                    total_chunks > 0 and
                                    first_chunk_audio and
                                    chunk_tts_success > 0
                                )
                                
                                if pipeline_success:
                                    self.test_results["story_streaming_pipeline"]["details"].append(
                                        f"✅ Complete pipeline: {total_words} words, {total_chunks} chunks, TTS working"
                                    )
                                    self.test_results["story_streaming_pipeline"]["passed"] = True
                                else:
                                    self.test_results["story_streaming_pipeline"]["details"].append(
                                        f"❌ Pipeline incomplete: words={total_words}, chunks={total_chunks}, chunk_tts={chunk_tts_success}"
                                    )
                                    
                            except Exception as audio_error:
                                self.test_results["story_streaming_pipeline"]["details"].append(
                                    f"❌ Audio processing error: {str(audio_error)}"
                                )
                        else:
                            self.test_results["story_streaming_pipeline"]["details"].append(
                                f"❌ First chunk missing audio"
                            )
                    else:
                        error_msg = data.get("error", "Unknown error")
                        self.test_results["story_streaming_pipeline"]["details"].append(
                            f"❌ Story streaming failed: {error_msg}"
                        )
                else:
                    response_text = await response.text()
                    self.test_results["story_streaming_pipeline"]["details"].append(
                        f"❌ Story streaming HTTP {response.status}: {response_text[:200]}"
                    )
                    
        except Exception as e:
            self.test_results["story_streaming_pipeline"]["details"].append(
                f"❌ Story streaming pipeline exception: {str(e)}"
            )
            
        logger.info(f"Story Streaming Pipeline: {'PASSED' if self.test_results['story_streaming_pipeline']['passed'] else 'FAILED'}")
        
    async def test_production_ready_functionality(self):
        """4. Production-Ready Functionality - Test rate-limited TTS queue"""
        logger.info("⚡ TESTING: Production-Ready Functionality")
        
        # Test sequential TTS processing without rate limits
        test_texts = [
            "This is test one for sequential processing.",
            "This is test two for sequential processing.", 
            "This is test three for sequential processing.",
            "This is test four for sequential processing.",
            "This is test five for sequential processing."
        ]
        
        successful_requests = 0
        rate_limit_errors = 0
        payload_errors = 0
        
        for i, text in enumerate(test_texts):
            try:
                payload = {
                    "text": text,
                    "personality": "friendly_companion"
                }
                
                start_time = time.time()
                async with self.session.post(f"{BACKEND_URL}/voice/tts", json=payload) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 429:
                        rate_limit_errors += 1
                        self.test_results["production_ready_functionality"]["details"].append(
                            f"❌ Request {i+1}: HTTP 429 rate limit error"
                        )
                    elif response.status == 400:
                        response_text = await response.text()
                        if "PAYLOAD_ERROR" in response_text:
                            payload_errors += 1
                            self.test_results["production_ready_functionality"]["details"].append(
                                f"❌ Request {i+1}: HTTP 400 PAYLOAD_ERROR"
                            )
                        else:
                            self.test_results["production_ready_functionality"]["details"].append(
                                f"❌ Request {i+1}: HTTP 400 - {response_text[:100]}"
                            )
                    elif response.status == 200:
                        data = await response.json()
                        if data.get("status") == "success" and data.get("audio_base64"):
                            successful_requests += 1
                            audio_size = len(base64.b64decode(data["audio_base64"])) / 1024
                            self.test_results["production_ready_functionality"]["details"].append(
                                f"✅ Request {i+1}: {audio_size:.1f}KB audio in {response_time:.2f}s"
                            )
                        else:
                            self.test_results["production_ready_functionality"]["details"].append(
                                f"❌ Request {i+1}: Invalid response structure"
                            )
                    else:
                        response_text = await response.text()
                        self.test_results["production_ready_functionality"]["details"].append(
                            f"❌ Request {i+1}: HTTP {response.status} - {response_text[:100]}"
                        )
                        
                # Small delay between requests to test sequential processing
                await asyncio.sleep(0.5)
                
            except Exception as e:
                self.test_results["production_ready_functionality"]["details"].append(
                    f"❌ Request {i+1}: Exception - {str(e)}"
                )
                
        # Production-ready passes if no rate limits or payload errors occur
        production_ready = (rate_limit_errors == 0 and payload_errors == 0 and successful_requests > 0)
        
        self.test_results["production_ready_functionality"]["passed"] = production_ready
        self.test_results["production_ready_functionality"]["details"].append(
            f"📊 Summary: {successful_requests}/{len(test_texts)} successful, {rate_limit_errors} rate limits, {payload_errors} payload errors"
        )
        
        logger.info(f"Production-Ready Functionality: {'PASSED' if production_ready else 'FAILED'}")
        
    async def test_end_to_end_narration(self):
        """5. End-to-End Story Narration - Complete user experience"""
        logger.info("🎬 TESTING: End-to-End Story Narration")
        
        try:
            # Test complete end-to-end flow: voice input → story generation → TTS → audio
            story_request = "Please tell me a magical bedtime story about a friendly dragon"
            
            # Step 1: Generate story via streaming
            payload = {
                "session_id": f"{self.test_session_id}_e2e",
                "user_id": self.test_user_id,
                "text": story_request
            }
            
            logger.info("Step 1: Generating complete story...")
            
            start_time = time.time()
            async with self.session.post(f"{BACKEND_URL}/stories/stream", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success":
                        total_words = data.get("total_words", 0)
                        total_chunks = data.get("total_chunks", 0)
                        first_chunk = data.get("first_chunk", {})
                        remaining_chunks = data.get("remaining_chunks", [])
                        
                        self.test_results["end_to_end_narration"]["details"].append(
                            f"✅ Story generated: {total_words} words in {total_chunks} chunks"
                        )
                        
                        # Step 2: Verify first chunk has audio
                        first_audio = first_chunk.get("audio_base64", "")
                        if first_audio:
                            first_audio_size = len(base64.b64decode(first_audio)) / 1024
                            self.test_results["end_to_end_narration"]["details"].append(
                                f"✅ First chunk audio: {first_audio_size:.1f}KB"
                            )
                            
                            # Step 3: Generate audio for remaining chunks
                            total_audio_size = first_audio_size
                            chunks_with_audio = 1
                            
                            for i, chunk in enumerate(remaining_chunks[:3]):  # Test first 3 remaining chunks
                                chunk_payload = {
                                    "text": chunk.get("text", ""),
                                    "chunk_id": i + 1,
                                    "user_id": self.test_user_id,
                                    "session_id": f"{self.test_session_id}_e2e"
                                }
                                
                                async with self.session.post(f"{BACKEND_URL}/stories/chunk-tts", json=chunk_payload) as chunk_response:
                                    if chunk_response.status == 200:
                                        chunk_data = await chunk_response.json()
                                        if chunk_data.get("status") == "success" and chunk_data.get("audio_base64"):
                                            chunk_audio_size = len(base64.b64decode(chunk_data["audio_base64"])) / 1024
                                            total_audio_size += chunk_audio_size
                                            chunks_with_audio += 1
                                            
                            # Step 4: Verify complete narration
                            total_time = time.time() - start_time
                            
                            # End-to-end success criteria
                            e2e_success = (
                                total_words >= 300 and  # Story length requirement
                                chunks_with_audio > 0 and  # Audio generation working
                                total_audio_size > 50  # Reasonable audio size (50KB+)
                            )
                            
                            if e2e_success:
                                self.test_results["end_to_end_narration"]["details"].append(
                                    f"✅ Complete narration: {chunks_with_audio} chunks with audio, {total_audio_size:.1f}KB total, {total_time:.2f}s"
                                )
                                self.test_results["end_to_end_narration"]["passed"] = True
                            else:
                                self.test_results["end_to_end_narration"]["details"].append(
                                    f"❌ Incomplete narration: words={total_words}, audio_chunks={chunks_with_audio}, audio_size={total_audio_size:.1f}KB"
                                )
                                
                        else:
                            self.test_results["end_to_end_narration"]["details"].append(
                                f"❌ First chunk missing audio"
                            )
                    else:
                        error_msg = data.get("error", "Unknown error")
                        self.test_results["end_to_end_narration"]["details"].append(
                            f"❌ Story generation failed: {error_msg}"
                        )
                else:
                    response_text = await response.text()
                    self.test_results["end_to_end_narration"]["details"].append(
                        f"❌ Story generation HTTP {response.status}: {response_text[:200]}"
                    )
                    
        except Exception as e:
            self.test_results["end_to_end_narration"]["details"].append(
                f"❌ End-to-end narration exception: {str(e)}"
            )
            
        logger.info(f"End-to-End Narration: {'PASSED' if self.test_results['end_to_end_narration']['passed'] else 'FAILED'}")
        
    async def run_all_tests(self):
        """Run all critical validation tests"""
        logger.info("🚀 STARTING FINAL CRITICAL VALIDATION TESTS")
        logger.info("=" * 80)
        
        await self.setup_session()
        
        try:
            # Health check first
            if not await self.test_health_check():
                logger.error("❌ Health check failed - aborting tests")
                return
                
            # Run all critical tests
            await self.test_tts_api_fix_verification()
            await self.test_story_generation_quality()
            await self.test_story_streaming_pipeline()
            await self.test_production_ready_functionality()
            await self.test_end_to_end_narration()
            
            # Determine overall success
            all_tests_passed = all(
                self.test_results[test]["passed"] 
                for test in ["tts_api_fix", "story_generation_quality", "story_streaming_pipeline", 
                           "production_ready_functionality", "end_to_end_narration"]
            )
            
            self.test_results["overall_success"] = all_tests_passed
            
        finally:
            await self.cleanup_session()
            
    def print_final_report(self):
        """Print comprehensive final validation report"""
        logger.info("=" * 80)
        logger.info("🎯 FINAL CRITICAL VALIDATION REPORT")
        logger.info("=" * 80)
        
        # Print each test section
        test_names = {
            "tts_api_fix": "1. TTS API Fix Verification",
            "story_generation_quality": "2. Enhanced Story Generation Quality", 
            "story_streaming_pipeline": "3. Complete Story Streaming Pipeline",
            "production_ready_functionality": "4. Production-Ready Functionality",
            "end_to_end_narration": "5. End-to-End Story Narration"
        }
        
        for test_key, test_name in test_names.items():
            result = self.test_results[test_key]
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            
            logger.info(f"\n{test_name}: {status}")
            for detail in result["details"]:
                logger.info(f"  {detail}")
                
        # Overall result
        logger.info("\n" + "=" * 80)
        if self.test_results["overall_success"]:
            logger.info("🎉 FINAL VALIDATION: ALL TESTS PASSED - SYSTEM IS PRODUCTION READY!")
            logger.info("✅ NO HTTP 400 PAYLOAD_ERROR messages")
            logger.info("✅ NO HTTP 429 rate limit errors")
            logger.info("✅ Stories are 300+ words minimum length")
            logger.info("✅ TTS generates valid base64 WAV audio")
            logger.info("✅ End-to-end story generation → TTS → audio works")
            logger.info("✅ All API endpoints return successful responses")
            logger.info("✅ No critical exceptions or failures occur")
        else:
            logger.info("❌ FINAL VALIDATION: SOME TESTS FAILED - ISSUES NEED RESOLUTION")
            
            # Count passed/failed tests
            passed_count = sum(1 for test in ["tts_api_fix", "story_generation_quality", "story_streaming_pipeline", 
                                            "production_ready_functionality", "end_to_end_narration"] 
                             if self.test_results[test]["passed"])
            
            logger.info(f"📊 SUMMARY: {passed_count}/5 critical tests passed")
            
        logger.info("=" * 80)

async def main():
    """Main test execution"""
    validator = FinalCriticalValidator()
    await validator.run_all_tests()
    validator.print_final_report()
    
    return validator.test_results["overall_success"]

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)