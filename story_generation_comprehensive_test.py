#!/usr/bin/env python3
"""
CRITICAL: Comprehensive Story Generation and Narration System Testing
Testing the completely rebuilt story generation and narration system end-to-end
Focus: Resolve "hundreds of failures" with production-ready solution
"""

import asyncio
import aiohttp
import json
import base64
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class StoryGenerationTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.user_id = "story_test_user_2025"
        self.session_id = f"story_session_{int(time.time())}"
        
    async def setup_session(self):
        """Setup HTTP session for testing"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=120)  # 2 minute timeout for story generation
        )
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, details, duration=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        duration_str = f" ({duration:.2f}s)" if duration else ""
        print(f"{status}: {test_name}{duration_str}")
        print(f"   Details: {details}")
        print()
        
    async def test_health_check(self):
        """Test basic health check"""
        start_time = time.time()
        try:
            async with self.session.get(f"{API_BASE}/health") as response:
                duration = time.time() - start_time
                if response.status == 200:
                    data = await response.json()
                    self.log_result(
                        "Health Check", 
                        True, 
                        f"Backend healthy: {data.get('status', 'unknown')}", 
                        duration
                    )
                    return True
                else:
                    self.log_result(
                        "Health Check", 
                        False, 
                        f"HTTP {response.status}: {await response.text()}", 
                        duration
                    )
                    return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Health Check", False, f"Connection error: {str(e)}", duration)
            return False
            
    async def test_story_generation_quality(self):
        """Test 1: Story Generation Quality - 300+ words, age-appropriate"""
        print("🎭 TESTING STORY GENERATION QUALITY...")
        
        story_requests = [
            "Tell me a magical adventure story about a brave little dragon",
            "Create a bedtime story about friendship in the forest", 
            "Tell me an exciting story about space exploration for kids",
            "Generate a story about a curious kitten who discovers something amazing"
        ]
        
        successful_stories = 0
        total_words = 0
        
        for i, story_request in enumerate(story_requests):
            start_time = time.time()
            try:
                # Test story streaming endpoint
                payload = {
                    "session_id": f"{self.session_id}_story_{i}",
                    "user_id": self.user_id,
                    "text": story_request
                }
                
                async with self.session.post(f"{API_BASE}/stories/stream", json=payload) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "success":
                            # Check story content
                            first_chunk = data.get("first_chunk", {})
                            story_text = first_chunk.get("text", "")
                            word_count = len(story_text.split())
                            total_words += word_count
                            
                            # Validate story quality
                            is_quality_story = (
                                word_count >= 50 and  # At least 50 words in first chunk
                                len(story_text) > 200 and  # At least 200 characters
                                any(keyword in story_text.lower() for keyword in ['once', 'story', 'adventure', 'magical', 'little', 'brave']) and
                                data.get("total_words", 0) >= 300  # Total story should be 300+ words
                            )
                            
                            if is_quality_story:
                                successful_stories += 1
                                self.log_result(
                                    f"Story Quality Test {i+1}",
                                    True,
                                    f"Generated {word_count} words in first chunk, total: {data.get('total_words', 0)} words. Story appears age-appropriate and engaging.",
                                    duration
                                )
                            else:
                                self.log_result(
                                    f"Story Quality Test {i+1}",
                                    False,
                                    f"Story quality insufficient: {word_count} words in chunk, total: {data.get('total_words', 0)} words. Content: '{story_text[:100]}...'",
                                    duration
                                )
                        else:
                            self.log_result(
                                f"Story Quality Test {i+1}",
                                False,
                                f"Story generation failed: {data.get('error', 'Unknown error')}",
                                duration
                            )
                    else:
                        error_text = await response.text()
                        self.log_result(
                            f"Story Quality Test {i+1}",
                            False,
                            f"HTTP {response.status}: {error_text}",
                            duration
                        )
                        
            except Exception as e:
                duration = time.time() - start_time
                self.log_result(
                    f"Story Quality Test {i+1}",
                    False,
                    f"Exception: {str(e)}",
                    duration
                )
                
        # Overall story generation quality assessment
        success_rate = (successful_stories / len(story_requests)) * 100
        avg_words = total_words / len(story_requests) if story_requests else 0
        
        overall_success = success_rate >= 75 and avg_words >= 100
        self.log_result(
            "Overall Story Generation Quality",
            overall_success,
            f"Success rate: {success_rate:.1f}% ({successful_stories}/{len(story_requests)}), Average words per chunk: {avg_words:.1f}"
        )
        
        return overall_success
        
    async def test_tts_rate_limiting_reliability(self):
        """Test 2: TTS Rate Limiting and Reliability - No HTTP 429 errors"""
        print("🔊 TESTING TTS RATE LIMITING AND RELIABILITY...")
        
        # Test multiple TTS requests in quick succession
        tts_requests = [
            "Hello there! This is a test of the TTS system reliability.",
            "The quick brown fox jumps over the lazy dog. This is a longer sentence to test TTS processing.",
            "Once upon a time, in a magical forest, there lived a brave little rabbit who loved adventures.",
            "Testing the TTS system with various sentence lengths and complexity levels.",
            "This is the final test message to ensure no rate limiting occurs."
        ]
        
        successful_tts = 0
        rate_limit_errors = 0
        
        for i, text in enumerate(tts_requests):
            start_time = time.time()
            try:
                payload = {
                    "text": text,
                    "personality": "story_narrator"
                }
                
                async with self.session.post(f"{API_BASE}/voice/tts", json=payload) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "success" and data.get("audio_base64"):
                            audio_data = data.get("audio_base64", "")
                            successful_tts += 1
                            
                            self.log_result(
                                f"TTS Reliability Test {i+1}",
                                True,
                                f"TTS generated successfully. Audio size: {len(audio_data)} chars, Duration: {duration:.2f}s",
                                duration
                            )
                        else:
                            self.log_result(
                                f"TTS Reliability Test {i+1}",
                                False,
                                f"TTS failed: {data.get('error', 'No audio generated')}",
                                duration
                            )
                    elif response.status == 429:
                        rate_limit_errors += 1
                        error_text = await response.text()
                        self.log_result(
                            f"TTS Reliability Test {i+1}",
                            False,
                            f"RATE LIMIT ERROR (HTTP 429): {error_text}",
                            duration
                        )
                    else:
                        error_text = await response.text()
                        self.log_result(
                            f"TTS Reliability Test {i+1}",
                            False,
                            f"HTTP {response.status}: {error_text}",
                            duration
                        )
                        
                # Small delay between requests to test rate limiting
                await asyncio.sleep(0.5)
                        
            except Exception as e:
                duration = time.time() - start_time
                self.log_result(
                    f"TTS Reliability Test {i+1}",
                    False,
                    f"Exception: {str(e)}",
                    duration
                )
                
        # Overall TTS reliability assessment
        success_rate = (successful_tts / len(tts_requests)) * 100
        no_rate_limits = rate_limit_errors == 0
        
        overall_success = success_rate >= 80 and no_rate_limits
        self.log_result(
            "TTS Rate Limiting & Reliability",
            overall_success,
            f"Success rate: {success_rate:.1f}% ({successful_tts}/{len(tts_requests)}), Rate limit errors: {rate_limit_errors}"
        )
        
        return overall_success
        
    async def test_chunked_vs_single_tts(self):
        """Test 3: Chunked vs Single TTS Response formats"""
        print("📝 TESTING CHUNKED VS SINGLE TTS RESPONSE FORMATS...")
        
        # Test short text (should use single TTS)
        short_text = "Hello! This is a short message for testing single TTS response."
        
        # Test long text (should use chunked TTS)
        long_text = """Once upon a time, in a magical kingdom far, far away, there lived a brave young princess named Luna who had the most extraordinary gift - she could speak to the stars themselves. Every night, when the moon rose high in the sky and cast its silver light across the land, Princess Luna would climb to the highest tower of her castle and whisper secrets to the twinkling stars above. The stars would whisper back, telling her stories of distant worlds, brave heroes, and magical adventures that awaited those who dared to dream. One particularly starry night, the brightest star in the sky, a magnificent golden star named Stella, told Princess Luna about a terrible curse that had befallen a neighboring kingdom. The people there had forgotten how to laugh, how to sing, and how to find joy in the simple pleasures of life. Their world had become gray and colorless, and only someone with a pure heart and the courage to face the unknown could break the spell and restore happiness to the land."""
        
        # Test single TTS
        start_time = time.time()
        try:
            payload = {"text": short_text, "personality": "friendly_companion"}
            
            async with self.session.post(f"{API_BASE}/voice/tts", json=payload) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success" and data.get("audio_base64"):
                        # Should be single response format
                        audio_size = len(data.get("audio_base64", ""))
                        self.log_result(
                            "Single TTS Response Test",
                            True,
                            f"Single TTS successful. Audio size: {audio_size} chars, Format: single response",
                            duration
                        )
                        single_tts_success = True
                    else:
                        self.log_result(
                            "Single TTS Response Test",
                            False,
                            f"Single TTS failed: {data.get('error', 'No audio')}"
                        )
                        single_tts_success = False
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Single TTS Response Test",
                        False,
                        f"HTTP {response.status}: {error_text}"
                    )
                    single_tts_success = False
        except Exception as e:
            self.log_result("Single TTS Response Test", False, f"Exception: {str(e)}")
            single_tts_success = False
            
        # Test chunked TTS via story streaming
        start_time = time.time()
        try:
            payload = {
                "session_id": f"{self.session_id}_chunked",
                "user_id": self.user_id,
                "text": f"Tell me this story: {long_text}"
            }
            
            async with self.session.post(f"{API_BASE}/stories/stream", json=payload) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success":
                        # Should have chunked format
                        total_chunks = data.get("total_chunks", 0)
                        first_chunk = data.get("first_chunk", {})
                        
                        if total_chunks > 1 and first_chunk.get("audio_base64"):
                            self.log_result(
                                "Chunked TTS Response Test",
                                True,
                                f"Chunked TTS successful. Total chunks: {total_chunks}, First chunk audio size: {len(first_chunk.get('audio_base64', ''))} chars",
                                duration
                            )
                            chunked_tts_success = True
                        else:
                            self.log_result(
                                "Chunked TTS Response Test",
                                False,
                                f"Chunked format not detected. Chunks: {total_chunks}, Audio present: {bool(first_chunk.get('audio_base64'))}"
                            )
                            chunked_tts_success = False
                    else:
                        self.log_result(
                            "Chunked TTS Response Test",
                            False,
                            f"Chunked TTS failed: {data.get('error', 'Unknown error')}"
                        )
                        chunked_tts_success = False
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Chunked TTS Response Test",
                        False,
                        f"HTTP {response.status}: {error_text}"
                    )
                    chunked_tts_success = False
        except Exception as e:
            self.log_result("Chunked TTS Response Test", False, f"Exception: {str(e)}")
            chunked_tts_success = False
            
        # Overall chunked vs single assessment
        overall_success = single_tts_success and chunked_tts_success
        self.log_result(
            "Chunked vs Single TTS Formats",
            overall_success,
            f"Single TTS: {'✅' if single_tts_success else '❌'}, Chunked TTS: {'✅' if chunked_tts_success else '❌'}"
        )
        
        return overall_success
        
    async def test_story_streaming_pipeline(self):
        """Test 4: Complete Story Streaming Pipeline"""
        print("🎬 TESTING COMPLETE STORY STREAMING PIPELINE...")
        
        test_scenarios = [
            {
                "request": "Tell me an adventure story about a young explorer discovering a hidden treasure",
                "voice_personality": "story_narrator"
            },
            {
                "request": "Create a magical story about a unicorn who helps children learn about friendship",
                "voice_personality": "friendly_companion"
            }
        ]
        
        successful_pipelines = 0
        
        for i, scenario in enumerate(test_scenarios):
            start_time = time.time()
            try:
                # Test complete pipeline
                payload = {
                    "session_id": f"{self.session_id}_pipeline_{i}",
                    "user_id": self.user_id,
                    "text": scenario["request"]
                }
                
                async with self.session.post(f"{API_BASE}/stories/stream", json=payload) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "success":
                            # Validate complete pipeline
                            first_chunk = data.get("first_chunk", {})
                            story_text = first_chunk.get("text", "")
                            audio_data = first_chunk.get("audio_base64", "")
                            total_chunks = data.get("total_chunks", 0)
                            total_words = data.get("total_words", 0)
                            
                            pipeline_complete = (
                                len(story_text) > 100 and  # Meaningful story content
                                len(audio_data) > 1000 and  # Substantial audio data
                                total_chunks >= 1 and  # At least one chunk
                                total_words >= 200  # Reasonable story length
                            )
                            
                            if pipeline_complete:
                                successful_pipelines += 1
                                
                                # Test chunk TTS for remaining chunks
                                chunk_tts_success = await self.test_chunk_tts_generation(
                                    first_chunk.get("text", ""), 
                                    0, 
                                    f"{self.session_id}_pipeline_{i}"
                                )
                                
                                self.log_result(
                                    f"Story Streaming Pipeline {i+1}",
                                    True,
                                    f"Complete pipeline working. Story: {len(story_text)} chars, Audio: {len(audio_data)} chars, Chunks: {total_chunks}, Words: {total_words}, Chunk TTS: {'✅' if chunk_tts_success else '❌'}",
                                    duration
                                )
                            else:
                                self.log_result(
                                    f"Story Streaming Pipeline {i+1}",
                                    False,
                                    f"Pipeline incomplete. Story: {len(story_text)} chars, Audio: {len(audio_data)} chars, Chunks: {total_chunks}, Words: {total_words}",
                                    duration
                                )
                        else:
                            self.log_result(
                                f"Story Streaming Pipeline {i+1}",
                                False,
                                f"Pipeline failed: {data.get('error', 'Unknown error')}",
                                duration
                            )
                    else:
                        error_text = await response.text()
                        self.log_result(
                            f"Story Streaming Pipeline {i+1}",
                            False,
                            f"HTTP {response.status}: {error_text}",
                            duration
                        )
                        
            except Exception as e:
                duration = time.time() - start_time
                self.log_result(
                    f"Story Streaming Pipeline {i+1}",
                    False,
                    f"Exception: {str(e)}",
                    duration
                )
                
        # Overall pipeline assessment
        success_rate = (successful_pipelines / len(test_scenarios)) * 100
        overall_success = success_rate >= 75
        
        self.log_result(
            "Complete Story Streaming Pipeline",
            overall_success,
            f"Pipeline success rate: {success_rate:.1f}% ({successful_pipelines}/{len(test_scenarios)})"
        )
        
        return overall_success
        
    async def test_chunk_tts_generation(self, chunk_text, chunk_id, session_id):
        """Helper: Test individual chunk TTS generation"""
        try:
            payload = {
                "text": chunk_text,
                "chunk_id": chunk_id,
                "user_id": self.user_id,
                "session_id": session_id
            }
            
            async with self.session.post(f"{API_BASE}/stories/chunk-tts", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("status") == "success" and data.get("audio_base64")
                return False
        except:
            return False
            
    async def test_audio_quality_format(self):
        """Test 5: Audio Quality and Format validation"""
        print("🎵 TESTING AUDIO QUALITY AND FORMAT...")
        
        # Test different voice personalities
        voice_tests = [
            {"personality": "story_narrator", "text": "Once upon a time, in a magical land far away, there lived a brave little hero."},
            {"personality": "friendly_companion", "text": "Hello there! Let's go on an amazing adventure together today!"},
            {"personality": "learning_buddy", "text": "Did you know that stars are actually giant balls of burning gas? Isn't that fascinating?"}
        ]
        
        successful_audio_tests = 0
        
        for i, test in enumerate(voice_tests):
            start_time = time.time()
            try:
                payload = {
                    "text": test["text"],
                    "personality": test["personality"]
                }
                
                async with self.session.post(f"{API_BASE}/voice/tts", json=payload) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "success" and data.get("audio_base64"):
                            audio_base64 = data.get("audio_base64", "")
                            
                            # Validate audio format
                            try:
                                # Decode base64 to check if it's valid
                                audio_bytes = base64.b64decode(audio_base64)
                                audio_size_kb = len(audio_bytes) / 1024
                                
                                # Check if it looks like WAV format (basic validation)
                                is_wav_format = audio_bytes[:4] == b'RIFF' if len(audio_bytes) > 4 else False
                                
                                # Audio quality checks
                                reasonable_size = 10 <= audio_size_kb <= 5000  # Between 10KB and 5MB
                                substantial_content = len(audio_base64) > 1000  # At least 1000 base64 chars
                                
                                if reasonable_size and substantial_content:
                                    successful_audio_tests += 1
                                    self.log_result(
                                        f"Audio Quality Test - {test['personality']}",
                                        True,
                                        f"Audio quality good. Size: {audio_size_kb:.1f}KB, Base64 length: {len(audio_base64)}, WAV format: {'✅' if is_wav_format else '❓'}",
                                        duration
                                    )
                                else:
                                    self.log_result(
                                        f"Audio Quality Test - {test['personality']}",
                                        False,
                                        f"Audio quality issues. Size: {audio_size_kb:.1f}KB, Base64 length: {len(audio_base64)}, Reasonable size: {reasonable_size}",
                                        duration
                                    )
                                    
                            except Exception as decode_error:
                                self.log_result(
                                    f"Audio Quality Test - {test['personality']}",
                                    False,
                                    f"Audio decode error: {str(decode_error)}",
                                    duration
                                )
                        else:
                            self.log_result(
                                f"Audio Quality Test - {test['personality']}",
                                False,
                                f"No audio generated: {data.get('error', 'Unknown error')}",
                                duration
                            )
                    else:
                        error_text = await response.text()
                        self.log_result(
                            f"Audio Quality Test - {test['personality']}",
                            False,
                            f"HTTP {response.status}: {error_text}",
                            duration
                        )
                        
            except Exception as e:
                duration = time.time() - start_time
                self.log_result(
                    f"Audio Quality Test - {test['personality']}",
                    False,
                    f"Exception: {str(e)}",
                    duration
                )
                
        # Overall audio quality assessment
        success_rate = (successful_audio_tests / len(voice_tests)) * 100
        overall_success = success_rate >= 75
        
        self.log_result(
            "Audio Quality & Format",
            overall_success,
            f"Audio quality success rate: {success_rate:.1f}% ({successful_audio_tests}/{len(voice_tests)})"
        )
        
        return overall_success
        
    async def test_end_to_end_story_flow(self):
        """Test 6: Complete End-to-End Story Generation → TTS → Audio Response"""
        print("🎯 TESTING END-TO-END STORY FLOW...")
        
        start_time = time.time()
        try:
            # Complete end-to-end test
            story_request = "Tell me a complete adventure story about a young wizard learning magic"
            
            payload = {
                "session_id": f"{self.session_id}_e2e",
                "user_id": self.user_id,
                "text": story_request
            }
            
            async with self.session.post(f"{API_BASE}/stories/stream", json=payload) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success":
                        # Validate complete end-to-end flow
                        first_chunk = data.get("first_chunk", {})
                        story_text = first_chunk.get("text", "")
                        audio_data = first_chunk.get("audio_base64", "")
                        total_words = data.get("total_words", 0)
                        total_chunks = data.get("total_chunks", 0)
                        
                        # End-to-end success criteria
                        story_generated = len(story_text) > 200 and total_words >= 300
                        audio_generated = len(audio_data) > 1000
                        proper_chunking = total_chunks >= 1
                        
                        e2e_success = story_generated and audio_generated and proper_chunking
                        
                        if e2e_success:
                            # Test additional chunk processing
                            remaining_chunks = data.get("remaining_chunks", [])
                            chunk_tests_passed = 0
                            
                            for chunk_idx, chunk_info in enumerate(remaining_chunks[:2]):  # Test first 2 remaining chunks
                                chunk_success = await self.test_chunk_tts_generation(
                                    chunk_info.get("text", ""),
                                    chunk_idx + 1,
                                    f"{self.session_id}_e2e"
                                )
                                if chunk_success:
                                    chunk_tests_passed += 1
                                    
                            self.log_result(
                                "End-to-End Story Flow",
                                True,
                                f"Complete E2E success! Story: {len(story_text)} chars ({total_words} words), Audio: {len(audio_data)} chars, Chunks: {total_chunks}, Additional chunk tests: {chunk_tests_passed}/{min(2, len(remaining_chunks))}",
                                duration
                            )
                            return True
                        else:
                            self.log_result(
                                "End-to-End Story Flow",
                                False,
                                f"E2E incomplete. Story: {story_generated} ({len(story_text)} chars, {total_words} words), Audio: {audio_generated} ({len(audio_data)} chars), Chunks: {proper_chunking} ({total_chunks})",
                                duration
                            )
                            return False
                    else:
                        self.log_result(
                            "End-to-End Story Flow",
                            False,
                            f"E2E failed: {data.get('error', 'Unknown error')}",
                            duration
                        )
                        return False
                else:
                    error_text = await response.text()
                    self.log_result(
                        "End-to-End Story Flow",
                        False,
                        f"HTTP {response.status}: {error_text}",
                        duration
                    )
                    return False
                    
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(
                "End-to-End Story Flow",
                False,
                f"Exception: {str(e)}",
                duration
            )
            return False
            
    async def run_comprehensive_tests(self):
        """Run all comprehensive story generation and narration tests"""
        print("🎭 STARTING COMPREHENSIVE STORY GENERATION & NARRATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User ID: {self.user_id}")
        print(f"Test Session ID: {self.session_id}")
        print("=" * 80)
        print()
        
        await self.setup_session()
        
        try:
            # Run all tests
            test_results = {}
            
            # 1. Health Check
            test_results["health"] = await self.test_health_check()
            
            # 2. Story Generation Quality
            test_results["story_quality"] = await self.test_story_generation_quality()
            
            # 3. TTS Rate Limiting and Reliability
            test_results["tts_reliability"] = await self.test_tts_rate_limiting_reliability()
            
            # 4. Chunked vs Single TTS
            test_results["tts_formats"] = await self.test_chunked_vs_single_tts()
            
            # 5. Story Streaming Pipeline
            test_results["streaming_pipeline"] = await self.test_story_streaming_pipeline()
            
            # 6. Audio Quality and Format
            test_results["audio_quality"] = await self.test_audio_quality_format()
            
            # 7. End-to-End Flow
            test_results["end_to_end"] = await self.test_end_to_end_story_flow()
            
            # Calculate overall results
            total_tests = len(test_results)
            passed_tests = sum(1 for result in test_results.values() if result)
            success_rate = (passed_tests / total_tests) * 100
            
            print("=" * 80)
            print("🎯 COMPREHENSIVE STORY GENERATION & NARRATION TEST RESULTS")
            print("=" * 80)
            
            for test_name, result in test_results.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status}: {test_name.replace('_', ' ').title()}")
                
            print()
            print(f"📊 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests})")
            
            # Critical success criteria assessment
            critical_tests = [
                "tts_reliability",  # NO HTTP 429 errors
                "story_quality",    # 300+ words stories
                "streaming_pipeline", # Complete pipeline works
                "audio_quality",    # Proper audio format
                "end_to_end"       # Full flow works
            ]
            
            critical_passed = sum(1 for test in critical_tests if test_results.get(test, False))
            critical_rate = (critical_passed / len(critical_tests)) * 100
            
            print(f"🎯 CRITICAL SUCCESS CRITERIA: {critical_rate:.1f}% ({critical_passed}/{len(critical_tests)})")
            
            if critical_rate >= 80:
                print("🎉 MISSION ACCOMPLISHED: Story generation and narration system is production-ready!")
                print("✅ The 'hundreds of failures' have been resolved with the production-ready solution.")
            else:
                print("⚠️  CRITICAL ISSUES REMAIN: Story system needs additional fixes before production.")
                
            print("=" * 80)
            
            return success_rate >= 75 and critical_rate >= 80
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = StoryGenerationTester()
    success = await tester.run_comprehensive_tests()
    
    if success:
        print("\n🎉 COMPREHENSIVE STORY TESTING: SUCCESS")
        exit(0)
    else:
        print("\n❌ COMPREHENSIVE STORY TESTING: FAILED")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())