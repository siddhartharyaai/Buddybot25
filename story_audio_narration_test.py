#!/usr/bin/env python3
"""
Story Audio Narration Testing - Critical Fixes Validation
Testing the major fixes implemented for story streaming and chunked TTS
"""

import asyncio
import aiohttp
import json
import base64
import time
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StoryAudioNarrationTester:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com/api"
        self.session = None
        self.test_results = []
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60))
        logger.info("🚀 STORY AUDIO NARRATION TESTING: Setup complete")
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
        logger.info("✅ Test cleanup complete")
        
    async def test_health_check(self) -> bool:
        """Test basic health check"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Health check passed: {data}")
                    return True
                else:
                    logger.error(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Health check error: {str(e)}")
            return False
            
    async def create_test_user(self) -> Dict[str, Any]:
        """Create a test user for story testing"""
        try:
            user_data = {
                "name": "Story Test Kid",
                "age": 8,
                "location": "Test City",
                "timezone": "UTC",
                "language": "english",
                "voice_personality": "story_narrator",
                "interests": ["stories", "adventures"],
                "learning_goals": ["creativity"],
                "gender": "prefer_not_to_say",
                "avatar": "bunny",
                "speech_speed": "normal",
                "energy_level": "balanced"
            }
            
            async with self.session.post(f"{self.base_url}/users/profile", json=user_data) as response:
                if response.status == 201:
                    user_profile = await response.json()
                    logger.info(f"✅ Test user created: {user_profile['id']}")
                    return user_profile
                else:
                    error_text = await response.text()
                    logger.error(f"❌ User creation failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"❌ User creation error: {str(e)}")
            return None
            
    async def test_story_generation_with_full_audio(self, user_id: str) -> Dict[str, Any]:
        """
        CRITICAL TEST 1: Story Generation with Full Audio
        Test story requests to verify complete audio narration (not just first few sentences)
        """
        logger.info("🎭 TESTING: Story Generation with Full Audio")
        
        try:
            # Test story request
            story_request = {
                "session_id": f"story_test_{int(time.time())}",
                "user_id": user_id,
                "message": "Tell me a complete adventure story about a brave little mouse who goes on a magical journey"
            }
            
            start_time = time.time()
            async with self.session.post(f"{self.base_url}/conversations/text", json=story_request) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Analyze the response
                    response_text = result.get('response_text', '')
                    response_audio = result.get('response_audio', '')
                    content_type = result.get('content_type', '')
                    
                    word_count = len(response_text.split())
                    audio_size = len(response_audio) if response_audio else 0
                    
                    # Check if this is a complete story with full audio
                    is_complete_story = word_count >= 300  # Should be 300+ words
                    has_full_audio = audio_size > 50000  # Should have substantial audio
                    is_story_content = content_type == "story"
                    
                    test_result = {
                        "test": "Story Generation with Full Audio",
                        "status": "PASS" if (is_complete_story and has_full_audio and is_story_content) else "FAIL",
                        "word_count": word_count,
                        "audio_size": audio_size,
                        "content_type": content_type,
                        "processing_time": f"{processing_time:.2f}s",
                        "expected_words": "300+",
                        "expected_audio": "50000+ chars",
                        "details": {
                            "complete_story": is_complete_story,
                            "full_audio": has_full_audio,
                            "correct_type": is_story_content,
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        }
                    }
                    
                    logger.info(f"📊 Story Generation Results:")
                    logger.info(f"   Words: {word_count} (target: 300+)")
                    logger.info(f"   Audio: {audio_size} chars (target: 50000+)")
                    logger.info(f"   Type: {content_type}")
                    logger.info(f"   Time: {processing_time:.2f}s")
                    
                    return test_result
                    
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Story generation failed: {response.status} - {error_text}")
                    return {
                        "test": "Story Generation with Full Audio",
                        "status": "FAIL",
                        "error": f"HTTP {response.status}: {error_text}",
                        "processing_time": f"{processing_time:.2f}s"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Story generation test error: {str(e)}")
            return {
                "test": "Story Generation with Full Audio",
                "status": "ERROR",
                "error": str(e)
            }
            
    async def test_story_streaming_pipeline(self, user_id: str) -> Dict[str, Any]:
        """
        CRITICAL TEST 2: Story Streaming Pipeline
        Verify the story streaming pipeline is working without falling back to regular processing
        """
        logger.info("🎬 TESTING: Story Streaming Pipeline")
        
        try:
            # Test story streaming request
            streaming_request = {
                "session_id": f"streaming_test_{int(time.time())}",
                "user_id": user_id,
                "text": "Tell me an exciting story about a dragon and a princess who become best friends"
            }
            
            start_time = time.time()
            async with self.session.post(f"{self.base_url}/stories/stream", json=streaming_request) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Check if streaming was successful
                    status = result.get('status', '')
                    story_mode = result.get('story_mode', False)
                    first_chunk = result.get('first_chunk', {})
                    remaining_chunks = result.get('remaining_chunks', [])
                    total_chunks = result.get('total_chunks', 0)
                    total_words = result.get('total_words', 0)
                    
                    # Verify streaming worked
                    streaming_success = status == "success" and story_mode
                    has_chunks = total_chunks > 1
                    has_audio = len(first_chunk.get('audio_base64', '')) > 0 if first_chunk else False
                    
                    test_result = {
                        "test": "Story Streaming Pipeline",
                        "status": "PASS" if (streaming_success and has_chunks and has_audio) else "FAIL",
                        "streaming_status": status,
                        "story_mode": story_mode,
                        "total_chunks": total_chunks,
                        "total_words": total_words,
                        "processing_time": f"{processing_time:.2f}s",
                        "details": {
                            "streaming_success": streaming_success,
                            "has_chunks": has_chunks,
                            "has_audio": has_audio,
                            "first_chunk_audio_size": len(first_chunk.get('audio_base64', '')) if first_chunk else 0,
                            "remaining_chunks_count": len(remaining_chunks)
                        }
                    }
                    
                    logger.info(f"📊 Story Streaming Results:")
                    logger.info(f"   Status: {status}")
                    logger.info(f"   Story Mode: {story_mode}")
                    logger.info(f"   Chunks: {total_chunks}")
                    logger.info(f"   Words: {total_words}")
                    logger.info(f"   Time: {processing_time:.2f}s")
                    
                    return test_result
                    
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Story streaming failed: {response.status} - {error_text}")
                    return {
                        "test": "Story Streaming Pipeline",
                        "status": "FAIL",
                        "error": f"HTTP {response.status}: {error_text}",
                        "processing_time": f"{processing_time:.2f}s"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Story streaming test error: {str(e)}")
            return {
                "test": "Story Streaming Pipeline",
                "status": "ERROR",
                "error": str(e)
            }
            
    async def test_chunked_tts_verification(self, user_id: str) -> Dict[str, Any]:
        """
        CRITICAL TEST 3: Chunked TTS Verification
        Test long content (>1500 chars) uses chunked TTS with complete audio
        """
        logger.info("🎵 TESTING: Chunked TTS Verification")
        
        try:
            # Create a long text that should trigger chunked TTS
            long_story_text = """Once upon a time, in a magical forest far away, there lived a brave little mouse named Whiskers. Whiskers was not like other mice - he had a heart full of courage and dreams bigger than the tallest oak tree. Every morning, he would wake up in his cozy burrow and look out at the vast forest, wondering what adventures awaited him beyond the familiar paths. One sunny day, Whiskers decided it was time to explore the mysterious Golden Valley that lay beyond the Whispering Woods. He packed his tiny backpack with cheese crumbs, a thimble of water, and his grandfather's lucky acorn. As he ventured deeper into the forest, he encountered many wonderful creatures who became his friends and helped him on his journey. The wise old owl gave him directions, the friendly squirrels shared their nuts, and the gentle deer showed him safe paths through the thorny bushes. After many exciting adventures and challenges, Whiskers finally reached the Golden Valley, where he discovered a magical crystal that granted wishes to those pure of heart. He wished for happiness and friendship for all the creatures in the forest, and his wish came true, making him the hero of the woodland realm."""
            
            # Test chunked TTS
            tts_request = {
                "text": long_story_text,
                "personality": "story_narrator"
            }
            
            start_time = time.time()
            async with self.session.post(f"{self.base_url}/voice/tts", json=tts_request) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Analyze the TTS response
                    status = result.get('status', '')
                    audio_base64 = result.get('audio_base64', '')
                    text_length = len(result.get('text', ''))
                    
                    # Check if chunked TTS was used and complete audio generated
                    is_long_content = text_length > 1500
                    has_complete_audio = len(audio_base64) > 100000  # Should be substantial for long content
                    tts_success = status == "success"
                    
                    test_result = {
                        "test": "Chunked TTS Verification",
                        "status": "PASS" if (is_long_content and has_complete_audio and tts_success) else "FAIL",
                        "tts_status": status,
                        "text_length": text_length,
                        "audio_size": len(audio_base64),
                        "processing_time": f"{processing_time:.2f}s",
                        "expected_length": "1500+ chars",
                        "expected_audio": "100000+ chars",
                        "details": {
                            "is_long_content": is_long_content,
                            "has_complete_audio": has_complete_audio,
                            "tts_success": tts_success,
                            "chunked_likely": is_long_content and has_complete_audio
                        }
                    }
                    
                    logger.info(f"📊 Chunked TTS Results:")
                    logger.info(f"   Text Length: {text_length} chars (target: 1500+)")
                    logger.info(f"   Audio Size: {len(audio_base64)} chars (target: 100000+)")
                    logger.info(f"   Status: {status}")
                    logger.info(f"   Time: {processing_time:.2f}s")
                    
                    return test_result
                    
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Chunked TTS failed: {response.status} - {error_text}")
                    return {
                        "test": "Chunked TTS Verification",
                        "status": "FAIL",
                        "error": f"HTTP {response.status}: {error_text}",
                        "processing_time": f"{processing_time:.2f}s"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Chunked TTS test error: {str(e)}")
            return {
                "test": "Chunked TTS Verification",
                "status": "ERROR",
                "error": str(e)
            }
            
    async def test_voice_processing_integration(self, user_id: str) -> Dict[str, Any]:
        """
        CRITICAL TEST 4: Voice Processing Integration
        Verify story requests through voice processing get full audio
        """
        logger.info("🎤 TESTING: Voice Processing Integration")
        
        try:
            # Create a mock audio request (we'll simulate this since we can't generate real audio)
            # In a real test, this would be actual audio data
            mock_audio_data = base64.b64encode(b"mock_audio_data_for_story_request").decode('utf-8')
            
            voice_request = {
                "session_id": f"voice_test_{int(time.time())}",
                "user_id": user_id,
                "audio_base64": mock_audio_data
            }
            
            start_time = time.time()
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_request) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Analyze voice processing response
                    status = result.get('status', '')
                    transcript = result.get('transcript', '')
                    response_text = result.get('response_text', '')
                    response_audio = result.get('response_audio', '')
                    content_type = result.get('content_type', '')
                    pipeline = result.get('pipeline', '')
                    
                    # Check if voice processing worked with audio
                    voice_success = status == "success"
                    has_response_audio = len(response_audio) > 0 if response_audio else False
                    has_response_text = len(response_text) > 0
                    
                    test_result = {
                        "test": "Voice Processing Integration",
                        "status": "PASS" if (voice_success and has_response_audio and has_response_text) else "FAIL",
                        "voice_status": status,
                        "transcript": transcript,
                        "response_length": len(response_text),
                        "audio_size": len(response_audio) if response_audio else 0,
                        "content_type": content_type,
                        "pipeline": pipeline,
                        "processing_time": f"{processing_time:.2f}s",
                        "details": {
                            "voice_success": voice_success,
                            "has_response_audio": has_response_audio,
                            "has_response_text": has_response_text,
                            "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
                        }
                    }
                    
                    logger.info(f"📊 Voice Processing Results:")
                    logger.info(f"   Status: {status}")
                    logger.info(f"   Pipeline: {pipeline}")
                    logger.info(f"   Response Length: {len(response_text)} chars")
                    logger.info(f"   Audio Size: {len(response_audio) if response_audio else 0} chars")
                    logger.info(f"   Time: {processing_time:.2f}s")
                    
                    return test_result
                    
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Voice processing failed: {response.status} - {error_text}")
                    return {
                        "test": "Voice Processing Integration",
                        "status": "FAIL",
                        "error": f"HTTP {response.status}: {error_text}",
                        "processing_time": f"{processing_time:.2f}s"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Voice processing test error: {str(e)}")
            return {
                "test": "Voice Processing Integration",
                "status": "ERROR",
                "error": str(e)
            }
            
    async def test_pipeline_performance(self, user_id: str) -> Dict[str, Any]:
        """
        CRITICAL TEST 5: Pipeline Performance
        Check if advanced pipelines (streaming, enhanced) are working optimally
        """
        logger.info("⚡ TESTING: Pipeline Performance")
        
        try:
            # Test multiple story requests to check pipeline performance
            test_requests = [
                "Tell me a short story about friendship",
                "Create an adventure story with a magical quest",
                "Tell me a bedtime story about stars"
            ]
            
            pipeline_results = []
            
            for i, story_request in enumerate(test_requests):
                request_data = {
                    "session_id": f"perf_test_{i}_{int(time.time())}",
                    "user_id": user_id,
                    "message": story_request
                }
                
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/conversations/text", json=request_data) as response:
                    processing_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        pipeline_results.append({
                            "request": story_request,
                            "processing_time": processing_time,
                            "word_count": len(result.get('response_text', '').split()),
                            "audio_size": len(result.get('response_audio', '') or ''),
                            "content_type": result.get('content_type', ''),
                            "status": "success"
                        })
                    else:
                        pipeline_results.append({
                            "request": story_request,
                            "processing_time": processing_time,
                            "status": "failed",
                            "error": f"HTTP {response.status}"
                        })
                        
                # Small delay between requests
                await asyncio.sleep(1)
                
            # Analyze pipeline performance
            successful_requests = [r for r in pipeline_results if r['status'] == 'success']
            avg_processing_time = sum(r['processing_time'] for r in successful_requests) / len(successful_requests) if successful_requests else 0
            avg_word_count = sum(r['word_count'] for r in successful_requests) / len(successful_requests) if successful_requests else 0
            avg_audio_size = sum(r['audio_size'] for r in successful_requests) / len(successful_requests) if successful_requests else 0
            
            # Performance criteria
            good_performance = avg_processing_time < 10.0  # Should be under 10 seconds
            adequate_content = avg_word_count > 100  # Should generate substantial content
            has_audio = avg_audio_size > 10000  # Should have audio
            
            test_result = {
                "test": "Pipeline Performance",
                "status": "PASS" if (good_performance and adequate_content and has_audio) else "FAIL",
                "successful_requests": len(successful_requests),
                "total_requests": len(test_requests),
                "avg_processing_time": f"{avg_processing_time:.2f}s",
                "avg_word_count": int(avg_word_count),
                "avg_audio_size": int(avg_audio_size),
                "details": {
                    "good_performance": good_performance,
                    "adequate_content": adequate_content,
                    "has_audio": has_audio,
                    "individual_results": pipeline_results
                }
            }
            
            logger.info(f"📊 Pipeline Performance Results:")
            logger.info(f"   Success Rate: {len(successful_requests)}/{len(test_requests)}")
            logger.info(f"   Avg Time: {avg_processing_time:.2f}s")
            logger.info(f"   Avg Words: {int(avg_word_count)}")
            logger.info(f"   Avg Audio: {int(avg_audio_size)} chars")
            
            return test_result
            
        except Exception as e:
            logger.error(f"❌ Pipeline performance test error: {str(e)}")
            return {
                "test": "Pipeline Performance",
                "status": "ERROR",
                "error": str(e)
            }
            
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all story audio narration tests"""
        logger.info("🎯 STARTING COMPREHENSIVE STORY AUDIO NARRATION TESTING")
        
        # Setup
        await self.setup()
        
        # Health check
        if not await self.test_health_check():
            return {"error": "Health check failed - cannot proceed with testing"}
            
        # Create test user
        test_user = await self.create_test_user()
        if not test_user:
            return {"error": "Failed to create test user - cannot proceed with testing"}
            
        user_id = test_user['id']
        
        # Run all critical tests
        tests = [
            self.test_story_generation_with_full_audio(user_id),
            self.test_story_streaming_pipeline(user_id),
            self.test_chunked_tts_verification(user_id),
            self.test_voice_processing_integration(user_id),
            self.test_pipeline_performance(user_id)
        ]
        
        # Execute tests
        test_results = []
        for test_coro in tests:
            try:
                result = await test_coro
                test_results.append(result)
            except Exception as e:
                logger.error(f"❌ Test execution error: {str(e)}")
                test_results.append({
                    "test": "Unknown Test",
                    "status": "ERROR",
                    "error": str(e)
                })
                
        # Cleanup
        await self.cleanup()
        
        # Calculate summary
        passed_tests = [t for t in test_results if t.get('status') == 'PASS']
        failed_tests = [t for t in test_results if t.get('status') == 'FAIL']
        error_tests = [t for t in test_results if t.get('status') == 'ERROR']
        
        success_rate = (len(passed_tests) / len(test_results)) * 100 if test_results else 0
        
        summary = {
            "test_suite": "Story Audio Narration Critical Fixes",
            "total_tests": len(test_results),
            "passed": len(passed_tests),
            "failed": len(failed_tests),
            "errors": len(error_tests),
            "success_rate": f"{success_rate:.1f}%",
            "overall_status": "PASS" if success_rate >= 80 else "FAIL",
            "test_results": test_results,
            "user_id": user_id
        }
        
        return summary

async def main():
    """Main test execution"""
    tester = StoryAudioNarrationTester()
    
    try:
        results = await tester.run_all_tests()
        
        # Print comprehensive results
        print("\n" + "="*80)
        print("🎭 STORY AUDIO NARRATION TESTING RESULTS")
        print("="*80)
        
        if "error" in results:
            print(f"❌ CRITICAL ERROR: {results['error']}")
            return
            
        print(f"📊 Test Suite: {results['test_suite']}")
        print(f"📈 Success Rate: {results['success_rate']}")
        print(f"✅ Passed: {results['passed']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"⚠️  Errors: {results['errors']}")
        print(f"🎯 Overall Status: {results['overall_status']}")
        
        print("\n📋 DETAILED TEST RESULTS:")
        print("-" * 80)
        
        for i, test in enumerate(results['test_results'], 1):
            status_emoji = "✅" if test['status'] == 'PASS' else "❌" if test['status'] == 'FAIL' else "⚠️"
            print(f"{i}. {status_emoji} {test['test']}: {test['status']}")
            
            if 'processing_time' in test:
                print(f"   ⏱️  Processing Time: {test['processing_time']}")
                
            if 'word_count' in test:
                print(f"   📝 Word Count: {test['word_count']}")
                
            if 'audio_size' in test:
                print(f"   🎵 Audio Size: {test['audio_size']} chars")
                
            if 'error' in test:
                print(f"   ❌ Error: {test['error']}")
                
            print()
            
        # Critical findings summary
        print("🔍 CRITICAL FINDINGS SUMMARY:")
        print("-" * 80)
        
        story_gen_test = next((t for t in results['test_results'] if 'Story Generation' in t['test']), None)
        if story_gen_test:
            if story_gen_test['status'] == 'PASS':
                print("✅ Story generation produces complete audio narration (300+ words)")
            else:
                print("❌ Story generation NOT producing complete audio narration")
                
        streaming_test = next((t for t in results['test_results'] if 'Streaming' in t['test']), None)
        if streaming_test:
            if streaming_test['status'] == 'PASS':
                print("✅ Story streaming pipeline working without fallbacks")
            else:
                print("❌ Story streaming pipeline has issues or fallbacks")
                
        chunked_test = next((t for t in results['test_results'] if 'Chunked' in t['test']), None)
        if chunked_test:
            if chunked_test['status'] == 'PASS':
                print("✅ Chunked TTS processes ALL chunks with complete audio")
            else:
                print("❌ Chunked TTS NOT processing all chunks completely")
                
        voice_test = next((t for t in results['test_results'] if 'Voice Processing' in t['test']), None)
        if voice_test:
            if voice_test['status'] == 'PASS':
                print("✅ Voice processing integration provides full audio")
            else:
                print("❌ Voice processing integration has audio issues")
                
        perf_test = next((t for t in results['test_results'] if 'Performance' in t['test']), None)
        if perf_test:
            if perf_test['status'] == 'PASS':
                print("✅ Advanced pipelines working optimally")
            else:
                print("❌ Advanced pipelines have performance issues")
                
        print("\n" + "="*80)
        
        if results['overall_status'] == 'PASS':
            print("🎉 STORY AUDIO NARRATION FIXES VALIDATION: SUCCESS!")
            print("All critical fixes are working as expected.")
        else:
            print("⚠️  STORY AUDIO NARRATION FIXES VALIDATION: ISSUES FOUND")
            print("Some critical fixes need attention.")
            
        print("="*80)
        
    except Exception as e:
        print(f"❌ CRITICAL TEST FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())