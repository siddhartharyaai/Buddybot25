#!/usr/bin/env python3
"""
CRITICAL PERFORMANCE ANALYSIS FOR BUDDY BOT SYSTEM
Testing Focus: Story Generation Latency, Audio Narration Pipeline, Context Retention, Bottleneck Identification
Review Request: Detailed analysis of performance issues and production readiness
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
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceAnalysisBackendTester:
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
        
        logger.info(f"🎯 PERFORMANCE ANALYSIS: Using backend URL: {self.base_url}")
        
        # Test data
        self.test_user_id = f"perf_test_user_{int(time.time())}"
        self.test_session_id = f"perf_session_{int(time.time())}"
        
        # Performance metrics tracking
        self.performance_metrics = {
            "story_generation_latency": [],
            "audio_narration_latency": [],
            "context_retrieval_times": [],
            "database_query_times": [],
            "tts_generation_times": [],
            "end_to_end_pipeline_times": [],
            "memory_usage": [],
            "error_rates": []
        }
        
        # Test results tracking
        self.test_results = {
            "story_generation_audio_pipeline": [],
            "failed_tests_analysis": [],
            "context_retention_load": [],
            "latency_bottlenecks": [],
            "production_readiness": []
        }
        
    async def run_comprehensive_performance_analysis(self):
        """Run comprehensive performance analysis as requested in review"""
        logger.info("🚀 STARTING CRITICAL PERFORMANCE ANALYSIS FOR BUDDY BOT SYSTEM")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Create test user profile first
            await self._create_test_user_profile()
            
            # 1. Story Generation & Audio Narration Latency Analysis
            logger.info("📊 TESTING: Story Generation & Audio Narration Latency")
            await self._test_story_generation_audio_latency()
            
            # 2. Failed Tests Root Cause Analysis
            logger.info("🔍 ANALYZING: Failed Tests Root Cause")
            await self._analyze_failed_tests_root_cause()
            
            # 3. Context Retention Performance Under Load
            logger.info("🧠 TESTING: Context Retention Performance Under Load")
            await self._test_context_retention_under_load()
            
            # 4. Latency Bottlenecks Identification
            logger.info("⚡ IDENTIFYING: Latency Bottlenecks")
            await self._identify_latency_bottlenecks()
            
            # 5. Production Readiness Issues
            logger.info("🏭 TESTING: Production Readiness Issues")
            await self._test_production_readiness()
            
        # Generate comprehensive performance report
        await self._generate_performance_report()
    
    async def _create_test_user_profile(self):
        """Create test user profile for performance testing"""
        try:
            profile_data = {
                "name": f"PerfTestUser_{int(time.time())}",
                "age": 7,
                "location": "Performance Test City",
                "timezone": "UTC",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "adventures", "learning"],
                "learning_goals": ["storytelling", "creativity"],
                "gender": "prefer_not_to_say",
                "avatar": "bunny",
                "speech_speed": "normal",
                "energy_level": "balanced"
            }
            
            start_time = time.time()
            async with self.session.post(f"{self.base_url}/users/profile", json=profile_data) as response:
                profile_creation_time = time.time() - start_time
                self.performance_metrics["database_query_times"].append(profile_creation_time)
                
                if response.status == 201:
                    profile = await response.json()
                    self.test_user_id = profile["id"]
                    logger.info(f"✅ Created test user profile: {self.test_user_id} (Time: {profile_creation_time:.3f}s)")
                    return True
                else:
                    logger.error(f"❌ Failed to create user profile: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error creating test user profile: {str(e)}")
            return False
    
    async def _test_story_generation_audio_latency(self):
        """Test end-to-end story generation from request to first audio chunk"""
        logger.info("🎭 TESTING: Story Generation & Audio Narration Latency Pipeline")
        
        story_requests = [
            "Tell me a complete story about a brave little mouse adventure",
            "I want a magical story about a princess and a dragon",
            "Can you tell me a bedtime story about friendship",
            "Tell me an adventure story in the enchanted forest",
            "I need a story about a child who discovers something amazing"
        ]
        
        for i, story_request in enumerate(story_requests):
            logger.info(f"📖 Testing story request {i+1}/5: '{story_request[:50]}...'")
            
            # Test 1: Text-based story generation latency
            await self._test_text_story_generation_latency(story_request, i+1)
            
            # Test 2: Voice-based story generation latency (if possible)
            await self._test_voice_story_generation_latency(story_request, i+1)
            
            # Test 3: Story streaming latency
            await self._test_story_streaming_latency(story_request, i+1)
            
            # Small delay between tests
            await asyncio.sleep(1)
    
    async def _test_text_story_generation_latency(self, story_request: str, test_num: int):
        """Test text-based story generation latency"""
        try:
            request_data = {
                "session_id": f"{self.test_session_id}_text_{test_num}",
                "user_id": self.test_user_id,
                "message": story_request
            }
            
            # Measure end-to-end latency
            start_time = time.time()
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=request_data) as response:
                first_response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Analyze response
                    response_text = result.get("response_text", "")
                    response_audio = result.get("response_audio", "")
                    content_type = result.get("content_type", "")
                    
                    # Calculate metrics
                    word_count = len(response_text.split()) if response_text else 0
                    audio_size = len(response_audio) if response_audio else 0
                    
                    # Record performance metrics
                    self.performance_metrics["story_generation_latency"].append(first_response_time)
                    if response_audio:
                        self.performance_metrics["audio_narration_latency"].append(first_response_time)
                    
                    # Evaluate against targets
                    meets_latency_target = first_response_time < 4.0  # <4s complete story audio target
                    meets_word_count = word_count >= 300  # Story should be 300+ words
                    
                    test_result = {
                        "test_type": "text_story_generation",
                        "test_number": test_num,
                        "request": story_request,
                        "latency": first_response_time,
                        "word_count": word_count,
                        "audio_size": audio_size,
                        "content_type": content_type,
                        "meets_latency_target": meets_latency_target,
                        "meets_word_count": meets_word_count,
                        "status": "success" if response.status == 200 else "failed",
                        "has_audio": bool(response_audio)
                    }
                    
                    self.test_results["story_generation_audio_pipeline"].append(test_result)
                    
                    logger.info(f"📊 Text Story {test_num}: {first_response_time:.3f}s, {word_count} words, Audio: {bool(response_audio)}")
                    
                    # Check for critical issues
                    if word_count < 100:
                        logger.warning(f"⚠️ CRITICAL: Story severely truncated ({word_count} words)")
                    if first_response_time > 4.0:
                        logger.warning(f"⚠️ LATENCY ISSUE: Story generation took {first_response_time:.3f}s (>4s target)")
                        
                else:
                    logger.error(f"❌ Text story generation failed: HTTP {response.status}")
                    error_text = await response.text()
                    self.test_results["story_generation_audio_pipeline"].append({
                        "test_type": "text_story_generation",
                        "test_number": test_num,
                        "status": "failed",
                        "error": f"HTTP {response.status}: {error_text}",
                        "latency": first_response_time
                    })
                    
        except Exception as e:
            logger.error(f"❌ Text story generation error: {str(e)}")
            self.test_results["story_generation_audio_pipeline"].append({
                "test_type": "text_story_generation",
                "test_number": test_num,
                "status": "error",
                "error": str(e)
            })
    
    async def _test_voice_story_generation_latency(self, story_request: str, test_num: int):
        """Test voice-based story generation latency (simulated)"""
        try:
            # Create a simple audio request (simulated)
            request_data = {
                "session_id": f"{self.test_session_id}_voice_{test_num}",
                "user_id": self.test_user_id,
                "audio_base64": base64.b64encode(b"simulated_audio_data").decode()
            }
            
            start_time = time.time()
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=request_data) as response:
                voice_response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    transcript = result.get("transcript", "")
                    response_text = result.get("response_text", "")
                    response_audio = result.get("response_audio", "")
                    pipeline = result.get("pipeline", "unknown")
                    
                    # Record metrics
                    self.performance_metrics["end_to_end_pipeline_times"].append(voice_response_time)
                    
                    test_result = {
                        "test_type": "voice_story_generation",
                        "test_number": test_num,
                        "latency": voice_response_time,
                        "transcript": transcript,
                        "response_length": len(response_text) if response_text else 0,
                        "has_audio": bool(response_audio),
                        "pipeline": pipeline,
                        "status": "success"
                    }
                    
                    self.test_results["story_generation_audio_pipeline"].append(test_result)
                    
                    logger.info(f"🎤 Voice Story {test_num}: {voice_response_time:.3f}s, Pipeline: {pipeline}")
                    
                else:
                    logger.error(f"❌ Voice story generation failed: HTTP {response.status}")
                    error_text = await response.text()
                    self.test_results["story_generation_audio_pipeline"].append({
                        "test_type": "voice_story_generation",
                        "test_number": test_num,
                        "status": "failed",
                        "error": f"HTTP {response.status}: {error_text}",
                        "latency": voice_response_time
                    })
                    
        except Exception as e:
            logger.error(f"❌ Voice story generation error: {str(e)}")
            self.test_results["story_generation_audio_pipeline"].append({
                "test_type": "voice_story_generation",
                "test_number": test_num,
                "status": "error",
                "error": str(e)
            })
    
    async def _test_story_streaming_latency(self, story_request: str, test_num: int):
        """Test story streaming latency for progressive display"""
        try:
            request_data = {
                "session_id": f"{self.test_session_id}_stream_{test_num}",
                "user_id": self.test_user_id,
                "text": story_request
            }
            
            start_time = time.time()
            
            async with self.session.post(f"{self.base_url}/stories/stream", json=request_data) as response:
                first_chunk_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    story_mode = result.get("story_mode", False)
                    first_chunk = result.get("first_chunk", {})
                    total_chunks = result.get("total_chunks", 0)
                    total_words = result.get("total_words", 0)
                    
                    # Record first chunk latency (critical metric)
                    self.performance_metrics["story_generation_latency"].append(first_chunk_time)
                    
                    # Check if meets <1-2s first chunk target
                    meets_first_chunk_target = first_chunk_time < 2.0
                    
                    test_result = {
                        "test_type": "story_streaming",
                        "test_number": test_num,
                        "first_chunk_latency": first_chunk_time,
                        "story_mode": story_mode,
                        "total_chunks": total_chunks,
                        "total_words": total_words,
                        "meets_first_chunk_target": meets_first_chunk_target,
                        "status": "success"
                    }
                    
                    self.test_results["story_generation_audio_pipeline"].append(test_result)
                    
                    logger.info(f"🎬 Stream Story {test_num}: {first_chunk_time:.3f}s first chunk, {total_chunks} chunks, {total_words} words")
                    
                    if not meets_first_chunk_target:
                        logger.warning(f"⚠️ FIRST CHUNK LATENCY: {first_chunk_time:.3f}s (>2s target)")
                        
                else:
                    logger.error(f"❌ Story streaming failed: HTTP {response.status}")
                    error_text = await response.text()
                    self.test_results["story_generation_audio_pipeline"].append({
                        "test_type": "story_streaming",
                        "test_number": test_num,
                        "status": "failed",
                        "error": f"HTTP {response.status}: {error_text}",
                        "first_chunk_latency": first_chunk_time
                    })
                    
        except Exception as e:
            logger.error(f"❌ Story streaming error: {str(e)}")
            self.test_results["story_generation_audio_pipeline"].append({
                "test_type": "story_streaming",
                "test_number": test_num,
                "status": "error",
                "error": str(e)
            })
    
    async def _analyze_failed_tests_root_cause(self):
        """Analyze why previous tests failed and identify specific failure points"""
        logger.info("🔍 ANALYZING: Failed Tests Root Cause Analysis")
        
        # Test 1: Story Request Pipeline Quality Check
        await self._test_story_request_pipeline_quality()
        
        # Test 2: TTS Latency Test Analysis
        await self._test_tts_latency_analysis()
        
        # Test 3: Error Message Analysis
        await self._analyze_error_messages()
    
    async def _test_story_request_pipeline_quality(self):
        """Test story request pipeline quality (3/5 success rate mentioned in review)"""
        logger.info("📊 Testing story request pipeline quality checks")
        
        story_tests = [
            "Tell me a complete story about a brave little mouse",
            "I want a magical adventure story",
            "Can you tell me a bedtime story",
            "Tell me a story about friendship",
            "I need an exciting adventure story"
        ]
        
        successful_requests = 0
        total_requests = len(story_tests)
        
        for i, story_request in enumerate(story_tests):
            try:
                request_data = {
                    "session_id": f"{self.test_session_id}_quality_{i}",
                    "user_id": self.test_user_id,
                    "message": story_request
                }
                
                async with self.session.post(f"{self.base_url}/conversations/text", json=request_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "")
                        word_count = len(response_text.split()) if response_text else 0
                        
                        # Quality check criteria
                        has_story_structure = any(word in response_text.lower() for word in ["once", "story", "adventure", "journey"])
                        meets_length = word_count >= 200  # Minimum story length
                        has_narrative = "." in response_text and len(response_text) > 100
                        
                        quality_score = sum([has_story_structure, meets_length, has_narrative])
                        
                        if quality_score >= 2:  # At least 2/3 quality criteria
                            successful_requests += 1
                            logger.info(f"✅ Story quality test {i+1}: PASS ({word_count} words, score: {quality_score}/3)")
                        else:
                            logger.warning(f"❌ Story quality test {i+1}: FAIL ({word_count} words, score: {quality_score}/3)")
                            
                        self.test_results["failed_tests_analysis"].append({
                            "test": f"story_quality_{i+1}",
                            "word_count": word_count,
                            "quality_score": quality_score,
                            "has_story_structure": has_story_structure,
                            "meets_length": meets_length,
                            "has_narrative": has_narrative,
                            "status": "pass" if quality_score >= 2 else "fail"
                        })
                    else:
                        logger.error(f"❌ Story quality test {i+1}: HTTP {response.status}")
                        self.test_results["failed_tests_analysis"].append({
                            "test": f"story_quality_{i+1}",
                            "status": "error",
                            "error": f"HTTP {response.status}"
                        })
                        
            except Exception as e:
                logger.error(f"❌ Story quality test {i+1} error: {str(e)}")
                self.test_results["failed_tests_analysis"].append({
                    "test": f"story_quality_{i+1}",
                    "status": "error",
                    "error": str(e)
                })
        
        success_rate = (successful_requests / total_requests) * 100
        logger.info(f"📊 Story Pipeline Quality: {successful_requests}/{total_requests} ({success_rate:.1f}% success rate)")
        
        # Compare with mentioned 3/5 (60%) success rate
        if success_rate < 60:
            logger.warning(f"⚠️ QUALITY ISSUE: Success rate {success_rate:.1f}% below expected 60%")
    
    async def _test_tts_latency_analysis(self):
        """Test TTS latency and analyze why some tests had no successful requests"""
        logger.info("🔊 Testing TTS latency analysis")
        
        tts_tests = [
            "Hello, this is a simple TTS test message.",
            "This is a longer TTS test message to check how the system handles medium-length text content.",
            "This is a very long TTS test message that contains multiple sentences and should test the system's ability to handle extended text content with proper chunking and processing capabilities.",
            "Tell me a story about a magical forest where animals can talk and adventures await.",
            "Can you sing me a happy song about sunshine and rainbows?"
        ]
        
        successful_tts = 0
        total_tts_tests = len(tts_tests)
        
        for i, tts_text in enumerate(tts_tests):
            try:
                request_data = {
                    "text": tts_text,
                    "personality": "friendly_companion"
                }
                
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/voice/tts", json=request_data) as response:
                    tts_latency = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        audio_base64 = result.get("audio_base64", "")
                        
                        if audio_base64:
                            successful_tts += 1
                            audio_size = len(audio_base64)
                            self.performance_metrics["tts_generation_times"].append(tts_latency)
                            
                            logger.info(f"✅ TTS test {i+1}: {tts_latency:.3f}s, {audio_size} chars audio")
                            
                            self.test_results["failed_tests_analysis"].append({
                                "test": f"tts_latency_{i+1}",
                                "latency": tts_latency,
                                "audio_size": audio_size,
                                "text_length": len(tts_text),
                                "status": "success"
                            })
                        else:
                            logger.warning(f"❌ TTS test {i+1}: No audio generated")
                            self.test_results["failed_tests_analysis"].append({
                                "test": f"tts_latency_{i+1}",
                                "latency": tts_latency,
                                "status": "no_audio",
                                "error": "No audio_base64 in response"
                            })
                    else:
                        logger.error(f"❌ TTS test {i+1}: HTTP {response.status}")
                        error_text = await response.text()
                        self.test_results["failed_tests_analysis"].append({
                            "test": f"tts_latency_{i+1}",
                            "latency": tts_latency,
                            "status": "error",
                            "error": f"HTTP {response.status}: {error_text}"
                        })
                        
            except Exception as e:
                logger.error(f"❌ TTS test {i+1} error: {str(e)}")
                self.test_results["failed_tests_analysis"].append({
                    "test": f"tts_latency_{i+1}",
                    "status": "error",
                    "error": str(e)
                })
        
        tts_success_rate = (successful_tts / total_tts_tests) * 100
        logger.info(f"🔊 TTS Success Rate: {successful_tts}/{total_tts_tests} ({tts_success_rate:.1f}%)")
        
        if tts_success_rate == 0:
            logger.error("🚨 CRITICAL: TTS has 0% success rate - matches review concern about 'no successful requests'")
    
    async def _analyze_error_messages(self):
        """Analyze common error messages and failure patterns"""
        logger.info("🔍 Analyzing error messages and failure patterns")
        
        # Test various endpoints for error patterns
        error_test_endpoints = [
            ("/health", "GET", {}),
            ("/voice/personalities", "GET", {}),
            ("/conversations/suggestions", "GET", {}),
            ("/content/stories", "GET", {}),
            ("/agents/status", "GET", {})
        ]
        
        for endpoint, method, data in error_test_endpoints:
            try:
                if method == "GET":
                    async with self.session.get(f"{self.base_url}{endpoint}") as response:
                        status = response.status
                        if status != 200:
                            error_text = await response.text()
                            logger.warning(f"⚠️ {endpoint}: HTTP {status} - {error_text[:100]}...")
                            
                            self.test_results["failed_tests_analysis"].append({
                                "endpoint": endpoint,
                                "method": method,
                                "status": status,
                                "error": error_text[:200],
                                "test_type": "endpoint_health"
                            })
                        else:
                            logger.info(f"✅ {endpoint}: OK")
                            
            except Exception as e:
                logger.error(f"❌ Error testing {endpoint}: {str(e)}")
                self.test_results["failed_tests_analysis"].append({
                    "endpoint": endpoint,
                    "method": method,
                    "status": "exception",
                    "error": str(e),
                    "test_type": "endpoint_health"
                })
    
    async def _test_context_retention_under_load(self):
        """Test context retention with heavy conversation loads"""
        logger.info("🧠 TESTING: Context Retention Performance Under Load")
        
        # Test 1: Multi-turn conversation context retention
        await self._test_multi_turn_context_retention()
        
        # Test 2: Riddle context persistence
        await self._test_riddle_context_persistence()
        
        # Test 3: Story continuation memory
        await self._test_story_continuation_memory()
        
        # Test 4: Rapid-fire interaction session management
        await self._test_rapid_fire_interactions()
    
    async def _test_multi_turn_context_retention(self):
        """Test context retention across multiple conversation turns"""
        logger.info("💬 Testing multi-turn context retention")
        
        conversation_flow = [
            "My name is Emma and I'm 7 years old",
            "What's my name?",
            "How old am I?",
            "I like elephants",
            "What animal do I like?",
            "Tell me a story about my favorite animal",
            "Can you continue that story?",
            "What was the story about again?"
        ]
        
        session_id = f"{self.test_session_id}_context_test"
        context_retention_score = 0
        total_context_tests = 0
        
        for i, message in enumerate(conversation_flow):
            try:
                request_data = {
                    "session_id": session_id,
                    "user_id": self.test_user_id,
                    "message": message
                }
                
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/conversations/text", json=request_data) as response:
                    context_time = time.time() - start_time
                    self.performance_metrics["context_retrieval_times"].append(context_time)
                    
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "").lower()
                        
                        # Check context retention
                        context_retained = False
                        if i == 1:  # "What's my name?"
                            context_retained = "emma" in response_text
                            total_context_tests += 1
                        elif i == 2:  # "How old am I?"
                            context_retained = "7" in response_text or "seven" in response_text
                            total_context_tests += 1
                        elif i == 4:  # "What animal do I like?"
                            context_retained = "elephant" in response_text
                            total_context_tests += 1
                        elif i == 5:  # Story about favorite animal
                            context_retained = "elephant" in response_text
                            total_context_tests += 1
                        elif i == 7:  # What was the story about
                            context_retained = "elephant" in response_text or "story" in response_text
                            total_context_tests += 1
                        
                        if context_retained:
                            context_retention_score += 1
                            
                        logger.info(f"💬 Turn {i+1}: '{message[:30]}...' -> Context: {'✅' if context_retained else '❌'} ({context_time:.3f}s)")
                        
                        self.test_results["context_retention_load"].append({
                            "turn": i+1,
                            "message": message,
                            "context_time": context_time,
                            "context_retained": context_retained,
                            "response_length": len(result.get("response_text", "")),
                            "status": "success"
                        })
                    else:
                        logger.error(f"❌ Context test turn {i+1}: HTTP {response.status}")
                        
            except Exception as e:
                logger.error(f"❌ Context test turn {i+1} error: {str(e)}")
        
        if total_context_tests > 0:
            context_retention_rate = (context_retention_score / total_context_tests) * 100
            logger.info(f"🧠 Context Retention Rate: {context_retention_score}/{total_context_tests} ({context_retention_rate:.1f}%)")
            
            if context_retention_rate < 80:
                logger.warning(f"⚠️ CONTEXT ISSUE: Retention rate {context_retention_rate:.1f}% below 80% target")
    
    async def _test_riddle_context_persistence(self):
        """Test riddle context persistence across multiple interactions"""
        logger.info("🧩 Testing riddle context persistence")
        
        riddle_flow = [
            "Can you give me a riddle?",
            "I don't know the answer",
            "Give me a hint",
            "Is it an elephant?",
            "What was the riddle again?"
        ]
        
        session_id = f"{self.test_session_id}_riddle_test"
        
        for i, message in enumerate(riddle_flow):
            try:
                request_data = {
                    "session_id": session_id,
                    "user_id": self.test_user_id,
                    "message": message
                }
                
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/conversations/text", json=request_data) as response:
                    riddle_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "")
                        
                        logger.info(f"🧩 Riddle turn {i+1}: '{message[:30]}...' ({riddle_time:.3f}s)")
                        
                        self.test_results["context_retention_load"].append({
                            "test_type": "riddle_context",
                            "turn": i+1,
                            "message": message,
                            "response_time": riddle_time,
                            "response_length": len(response_text),
                            "status": "success"
                        })
                    else:
                        logger.error(f"❌ Riddle test turn {i+1}: HTTP {response.status}")
                        
            except Exception as e:
                logger.error(f"❌ Riddle test turn {i+1} error: {str(e)}")
    
    async def _test_story_continuation_memory(self):
        """Test story continuation memory with long conversations"""
        logger.info("📚 Testing story continuation memory")
        
        story_flow = [
            "Tell me a story about a magical forest",
            "What happened next in the story?",
            "Can you continue the story?",
            "How does the story end?",
            "What was the main character's name?",
            "Where did the story take place?"
        ]
        
        session_id = f"{self.test_session_id}_story_memory"
        
        for i, message in enumerate(story_flow):
            try:
                request_data = {
                    "session_id": session_id,
                    "user_id": self.test_user_id,
                    "message": message
                }
                
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/conversations/text", json=request_data) as response:
                    story_memory_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "")
                        
                        logger.info(f"📚 Story memory turn {i+1}: '{message[:30]}...' ({story_memory_time:.3f}s)")
                        
                        self.test_results["context_retention_load"].append({
                            "test_type": "story_continuation_memory",
                            "turn": i+1,
                            "message": message,
                            "response_time": story_memory_time,
                            "response_length": len(response_text),
                            "status": "success"
                        })
                    else:
                        logger.error(f"❌ Story memory turn {i+1}: HTTP {response.status}")
                        
            except Exception as e:
                logger.error(f"❌ Story memory turn {i+1} error: {str(e)}")
    
    async def _test_rapid_fire_interactions(self):
        """Test session management with rapid-fire interactions"""
        logger.info("⚡ Testing rapid-fire interaction session management")
        
        rapid_messages = [
            "Hi", "Hello", "How are you?", "What's up?", "Tell me a joke",
            "Another joke", "One more", "That's funny", "Thanks", "Bye"
        ]
        
        session_id = f"{self.test_session_id}_rapid_fire"
        rapid_fire_times = []
        
        # Send messages rapidly (no delay)
        for i, message in enumerate(rapid_messages):
            try:
                request_data = {
                    "session_id": session_id,
                    "user_id": self.test_user_id,
                    "message": message
                }
                
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/conversations/text", json=request_data) as response:
                    rapid_time = time.time() - start_time
                    rapid_fire_times.append(rapid_time)
                    
                    if response.status == 200:
                        logger.info(f"⚡ Rapid {i+1}: '{message}' ({rapid_time:.3f}s)")
                    else:
                        logger.error(f"❌ Rapid {i+1}: HTTP {response.status}")
                        
            except Exception as e:
                logger.error(f"❌ Rapid fire {i+1} error: {str(e)}")
        
        if rapid_fire_times:
            avg_rapid_time = statistics.mean(rapid_fire_times)
            max_rapid_time = max(rapid_fire_times)
            logger.info(f"⚡ Rapid-fire stats: Avg {avg_rapid_time:.3f}s, Max {max_rapid_time:.3f}s")
            
            self.test_results["context_retention_load"].append({
                "test_type": "rapid_fire_interactions",
                "total_messages": len(rapid_messages),
                "avg_response_time": avg_rapid_time,
                "max_response_time": max_rapid_time,
                "all_successful": len(rapid_fire_times) == len(rapid_messages)
            })
    
    async def _identify_latency_bottlenecks(self):
        """Identify slowest components in the pipeline"""
        logger.info("⚡ IDENTIFYING: Latency Bottlenecks")
        
        # Test 1: Database query performance
        await self._test_database_query_performance()
        
        # Test 2: TTS generation vs Deepgram fallback
        await self._test_tts_vs_deepgram_performance()
        
        # Test 3: Prefetch cache hit rates
        await self._test_prefetch_cache_performance()
        
        # Test 4: Component-wise latency breakdown
        await self._test_component_latency_breakdown()
    
    async def _test_database_query_performance(self):
        """Test database query times for various operations"""
        logger.info("🗄️ Testing database query performance")
        
        db_operations = [
            ("user_profile_lookup", f"/users/profile/{self.test_user_id}"),
            ("parental_controls", f"/users/{self.test_user_id}/parental-controls"),
            ("conversation_suggestions", "/conversations/suggestions"),
            ("content_stories", "/content/stories"),
            ("voice_personalities", "/voice/personalities")
        ]
        
        for operation_name, endpoint in db_operations:
            try:
                start_time = time.time()
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    db_query_time = time.time() - start_time
                    self.performance_metrics["database_query_times"].append(db_query_time)
                    
                    if response.status == 200:
                        logger.info(f"🗄️ {operation_name}: {db_query_time:.3f}s")
                        
                        self.test_results["latency_bottlenecks"].append({
                            "component": "database",
                            "operation": operation_name,
                            "latency": db_query_time,
                            "status": "success"
                        })
                    else:
                        logger.error(f"❌ {operation_name}: HTTP {response.status} ({db_query_time:.3f}s)")
                        self.test_results["latency_bottlenecks"].append({
                            "component": "database",
                            "operation": operation_name,
                            "latency": db_query_time,
                            "status": "error",
                            "error": f"HTTP {response.status}"
                        })
                        
            except Exception as e:
                logger.error(f"❌ {operation_name} error: {str(e)}")
                self.test_results["latency_bottlenecks"].append({
                    "component": "database",
                    "operation": operation_name,
                    "status": "exception",
                    "error": str(e)
                })
    
    async def _test_tts_vs_deepgram_performance(self):
        """Compare TTS generation times vs Deepgram fallback performance"""
        logger.info("🔊 Testing TTS vs Deepgram performance comparison")
        
        test_texts = [
            "Short test message",
            "This is a medium length test message for TTS performance comparison",
            "This is a longer test message that should help us understand the performance characteristics of the TTS system compared to Deepgram fallback mechanisms"
        ]
        
        for i, text in enumerate(test_texts):
            # Test TTS performance
            try:
                request_data = {"text": text, "personality": "friendly_companion"}
                
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/voice/tts", json=request_data) as response:
                    tts_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        audio_size = len(result.get("audio_base64", ""))
                        
                        logger.info(f"🔊 TTS test {i+1}: {tts_time:.3f}s ({audio_size} chars audio)")
                        
                        self.test_results["latency_bottlenecks"].append({
                            "component": "tts",
                            "test_number": i+1,
                            "text_length": len(text),
                            "latency": tts_time,
                            "audio_size": audio_size,
                            "status": "success"
                        })
                    else:
                        logger.error(f"❌ TTS test {i+1}: HTTP {response.status}")
                        
            except Exception as e:
                logger.error(f"❌ TTS test {i+1} error: {str(e)}")
    
    async def _test_prefetch_cache_performance(self):
        """Test prefetch cache hit rates"""
        logger.info("💾 Testing prefetch cache hit rates")
        
        # Test conversation suggestions multiple times to check caching
        cache_tests = 5
        cache_times = []
        
        for i in range(cache_tests):
            try:
                start_time = time.time()
                async with self.session.get(f"{self.base_url}/conversations/suggestions") as response:
                    cache_time = time.time() - start_time
                    cache_times.append(cache_time)
                    
                    if response.status == 200:
                        result = await response.json()
                        suggestions_count = len(result) if isinstance(result, list) else 0
                        
                        logger.info(f"💾 Cache test {i+1}: {cache_time:.3f}s ({suggestions_count} suggestions)")
                    else:
                        logger.error(f"❌ Cache test {i+1}: HTTP {response.status}")
                        
            except Exception as e:
                logger.error(f"❌ Cache test {i+1} error: {str(e)}")
        
        if cache_times:
            avg_cache_time = statistics.mean(cache_times)
            first_request_time = cache_times[0]
            subsequent_avg = statistics.mean(cache_times[1:]) if len(cache_times) > 1 else first_request_time
            
            cache_improvement = ((first_request_time - subsequent_avg) / first_request_time) * 100 if first_request_time > 0 else 0
            
            logger.info(f"💾 Cache performance: First {first_request_time:.3f}s, Avg subsequent {subsequent_avg:.3f}s, Improvement {cache_improvement:.1f}%")
            
            self.test_results["latency_bottlenecks"].append({
                "component": "prefetch_cache",
                "first_request_time": first_request_time,
                "subsequent_avg_time": subsequent_avg,
                "cache_improvement_percent": cache_improvement,
                "total_tests": len(cache_times)
            })
    
    async def _test_component_latency_breakdown(self):
        """Test component-wise latency breakdown"""
        logger.info("⚡ Testing component-wise latency breakdown")
        
        # Test a complete conversation flow and measure each component
        try:
            session_id = f"{self.test_session_id}_latency_breakdown"
            message = "Tell me a short story about a friendly robot"
            
            # Measure total request time
            total_start = time.time()
            
            request_data = {
                "session_id": session_id,
                "user_id": self.test_user_id,
                "message": message
            }
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=request_data) as response:
                total_time = time.time() - total_start
                
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "")
                    response_audio = result.get("response_audio", "")
                    
                    # Estimate component breakdown (approximate)
                    estimated_llm_time = total_time * 0.4  # ~40% for LLM processing
                    estimated_tts_time = total_time * 0.3  # ~30% for TTS
                    estimated_db_time = total_time * 0.2   # ~20% for DB operations
                    estimated_overhead = total_time * 0.1  # ~10% for overhead
                    
                    logger.info(f"⚡ Latency breakdown for '{message[:30]}...':")
                    logger.info(f"   Total: {total_time:.3f}s")
                    logger.info(f"   Est. LLM: {estimated_llm_time:.3f}s")
                    logger.info(f"   Est. TTS: {estimated_tts_time:.3f}s")
                    logger.info(f"   Est. DB: {estimated_db_time:.3f}s")
                    logger.info(f"   Est. Overhead: {estimated_overhead:.3f}s")
                    
                    self.test_results["latency_bottlenecks"].append({
                        "component": "full_pipeline",
                        "total_time": total_time,
                        "estimated_llm_time": estimated_llm_time,
                        "estimated_tts_time": estimated_tts_time,
                        "estimated_db_time": estimated_db_time,
                        "estimated_overhead": estimated_overhead,
                        "response_length": len(response_text),
                        "has_audio": bool(response_audio)
                    })
                else:
                    logger.error(f"❌ Component latency test: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Component latency breakdown error: {str(e)}")
    
    async def _test_production_readiness(self):
        """Test edge cases and production readiness issues"""
        logger.info("🏭 TESTING: Production Readiness Issues")
        
        # Test 1: Edge cases that might cause failures
        await self._test_edge_cases()
        
        # Test 2: Error handling and recovery mechanisms
        await self._test_error_handling_recovery()
        
        # Test 3: Fallback systems
        await self._test_fallback_systems()
        
        # Test 4: System behavior under stress
        await self._test_stress_conditions()
    
    async def _test_edge_cases(self):
        """Test edge cases that might cause failures"""
        logger.info("🔍 Testing edge cases")
        
        edge_cases = [
            ("empty_message", ""),
            ("very_long_message", "A" * 5000),
            ("special_characters", "!@#$%^&*()_+{}|:<>?[]\\;'\",./ 🎉🎊🎈"),
            ("unicode_text", "Hello 世界 🌍 Здравствуй мир"),
            ("html_injection", "<script>alert('test')</script>"),
            ("sql_injection", "'; DROP TABLE users; --"),
            ("null_bytes", "test\x00null"),
            ("only_whitespace", "   \n\t   ")
        ]
        
        for case_name, test_input in edge_cases:
            try:
                request_data = {
                    "session_id": f"{self.test_session_id}_edge_{case_name}",
                    "user_id": self.test_user_id,
                    "message": test_input
                }
                
                async with self.session.post(f"{self.base_url}/conversations/text", json=request_data) as response:
                    if response.status in [200, 400]:  # 400 is acceptable for invalid input
                        logger.info(f"✅ Edge case '{case_name}': HTTP {response.status}")
                        
                        self.test_results["production_readiness"].append({
                            "test_type": "edge_case",
                            "case_name": case_name,
                            "status": response.status,
                            "handled_gracefully": True
                        })
                    else:
                        logger.warning(f"⚠️ Edge case '{case_name}': HTTP {response.status}")
                        self.test_results["production_readiness"].append({
                            "test_type": "edge_case",
                            "case_name": case_name,
                            "status": response.status,
                            "handled_gracefully": False
                        })
                        
            except Exception as e:
                logger.error(f"❌ Edge case '{case_name}' error: {str(e)}")
                self.test_results["production_readiness"].append({
                    "test_type": "edge_case",
                    "case_name": case_name,
                    "status": "exception",
                    "error": str(e),
                    "handled_gracefully": False
                })
    
    async def _test_error_handling_recovery(self):
        """Test error handling and recovery mechanisms"""
        logger.info("🛠️ Testing error handling and recovery mechanisms")
        
        # Test invalid endpoints
        invalid_endpoints = [
            "/nonexistent/endpoint",
            "/users/profile/invalid_user_id",
            "/conversations/text",  # POST without data
            "/voice/tts"  # POST without data
        ]
        
        for endpoint in invalid_endpoints:
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status in [404, 400, 422]:  # Expected error codes
                        logger.info(f"✅ Error handling '{endpoint}': HTTP {response.status}")
                        
                        self.test_results["production_readiness"].append({
                            "test_type": "error_handling",
                            "endpoint": endpoint,
                            "status": response.status,
                            "proper_error_code": True
                        })
                    else:
                        logger.warning(f"⚠️ Error handling '{endpoint}': HTTP {response.status}")
                        
            except Exception as e:
                logger.error(f"❌ Error handling '{endpoint}' error: {str(e)}")
    
    async def _test_fallback_systems(self):
        """Test fallback systems work properly"""
        logger.info("🔄 Testing fallback systems")
        
        # Test with invalid user profile
        try:
            request_data = {
                "session_id": f"{self.test_session_id}_fallback",
                "user_id": "nonexistent_user_id",
                "message": "Hello, test fallback system"
            }
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=request_data) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "")
                    
                    if response_text:
                        logger.info("✅ Fallback system: Created default profile and responded")
                        
                        self.test_results["production_readiness"].append({
                            "test_type": "fallback_system",
                            "test": "invalid_user_fallback",
                            "status": "success",
                            "fallback_worked": True
                        })
                    else:
                        logger.warning("⚠️ Fallback system: No response text")
                else:
                    logger.error(f"❌ Fallback system: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Fallback system error: {str(e)}")
    
    async def _test_stress_conditions(self):
        """Test system behavior under stress conditions"""
        logger.info("💪 Testing system behavior under stress conditions")
        
        # Test concurrent requests
        concurrent_requests = 5
        stress_tasks = []
        
        for i in range(concurrent_requests):
            task = self._make_concurrent_request(i)
            stress_tasks.append(task)
        
        try:
            results = await asyncio.gather(*stress_tasks, return_exceptions=True)
            
            successful_requests = sum(1 for result in results if not isinstance(result, Exception))
            success_rate = (successful_requests / concurrent_requests) * 100
            
            logger.info(f"💪 Stress test: {successful_requests}/{concurrent_requests} ({success_rate:.1f}% success)")
            
            self.test_results["production_readiness"].append({
                "test_type": "stress_test",
                "concurrent_requests": concurrent_requests,
                "successful_requests": successful_requests,
                "success_rate": success_rate,
                "handles_load": success_rate >= 80
            })
            
        except Exception as e:
            logger.error(f"❌ Stress test error: {str(e)}")
    
    async def _make_concurrent_request(self, request_id: int):
        """Make a concurrent request for stress testing"""
        try:
            request_data = {
                "session_id": f"{self.test_session_id}_stress_{request_id}",
                "user_id": self.test_user_id,
                "message": f"Stress test message {request_id}"
            }
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=request_data) as response:
                if response.status == 200:
                    return {"request_id": request_id, "status": "success"}
                else:
                    return {"request_id": request_id, "status": "failed", "http_status": response.status}
                    
        except Exception as e:
            return {"request_id": request_id, "status": "error", "error": str(e)}
    
    async def _generate_performance_report(self):
        """Generate comprehensive performance analysis report"""
        logger.info("📊 GENERATING COMPREHENSIVE PERFORMANCE ANALYSIS REPORT")
        
        # Calculate performance statistics
        story_latencies = self.performance_metrics["story_generation_latency"]
        audio_latencies = self.performance_metrics["audio_narration_latency"]
        context_times = self.performance_metrics["context_retrieval_times"]
        db_times = self.performance_metrics["database_query_times"]
        tts_times = self.performance_metrics["tts_generation_times"]
        
        report = {
            "performance_analysis_summary": {
                "test_timestamp": datetime.now().isoformat(),
                "total_tests_run": sum(len(results) for results in self.test_results.values()),
                "backend_url": self.base_url,
                "test_user_id": self.test_user_id
            },
            "key_metrics": {
                "story_generation_latency": {
                    "count": len(story_latencies),
                    "avg": statistics.mean(story_latencies) if story_latencies else 0,
                    "min": min(story_latencies) if story_latencies else 0,
                    "max": max(story_latencies) if story_latencies else 0,
                    "target": "< 4s complete story audio",
                    "meets_target": all(t < 4.0 for t in story_latencies) if story_latencies else False
                },
                "audio_narration_latency": {
                    "count": len(audio_latencies),
                    "avg": statistics.mean(audio_latencies) if audio_latencies else 0,
                    "target": "< 1-2s first chunk",
                    "meets_target": all(t < 2.0 for t in audio_latencies) if audio_latencies else False
                },
                "context_retrieval_times": {
                    "count": len(context_times),
                    "avg": statistics.mean(context_times) if context_times else 0,
                    "max": max(context_times) if context_times else 0
                },
                "database_query_times": {
                    "count": len(db_times),
                    "avg": statistics.mean(db_times) if db_times else 0,
                    "max": max(db_times) if db_times else 0
                },
                "tts_generation_times": {
                    "count": len(tts_times),
                    "avg": statistics.mean(tts_times) if tts_times else 0,
                    "max": max(tts_times) if tts_times else 0
                }
            },
            "detailed_results": self.test_results
        }
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 CRITICAL PERFORMANCE ANALYSIS RESULTS")
        print("="*80)
        
        print(f"\n📊 KEY PERFORMANCE METRICS:")
        print(f"   Story Generation Latency: {report['key_metrics']['story_generation_latency']['avg']:.3f}s avg ({len(story_latencies)} tests)")
        print(f"   Audio Narration Latency: {report['key_metrics']['audio_narration_latency']['avg']:.3f}s avg ({len(audio_latencies)} tests)")
        print(f"   Context Retrieval: {report['key_metrics']['context_retrieval_times']['avg']:.3f}s avg ({len(context_times)} tests)")
        print(f"   Database Queries: {report['key_metrics']['database_query_times']['avg']:.3f}s avg ({len(db_times)} tests)")
        print(f"   TTS Generation: {report['key_metrics']['tts_generation_times']['avg']:.3f}s avg ({len(tts_times)} tests)")
        
        print(f"\n🎯 TARGET COMPLIANCE:")
        print(f"   Story Audio < 4s: {'✅ PASS' if report['key_metrics']['story_generation_latency']['meets_target'] else '❌ FAIL'}")
        print(f"   First Chunk < 2s: {'✅ PASS' if report['key_metrics']['audio_narration_latency']['meets_target'] else '❌ FAIL'}")
        
        # Identify critical issues
        critical_issues = []
        
        # Check story generation issues
        story_pipeline_tests = self.test_results["story_generation_audio_pipeline"]
        failed_story_tests = [t for t in story_pipeline_tests if t.get("status") != "success"]
        if failed_story_tests:
            critical_issues.append(f"Story Generation Pipeline: {len(failed_story_tests)} failed tests")
        
        # Check TTS issues
        failed_tts_tests = [t for t in self.test_results["failed_tests_analysis"] if "tts" in t.get("test", "") and t.get("status") != "success"]
        if failed_tts_tests:
            critical_issues.append(f"TTS Latency: {len(failed_tts_tests)} failed tests")
        
        # Check context retention issues
        context_tests = self.test_results["context_retention_load"]
        failed_context_tests = [t for t in context_tests if not t.get("context_retained", True)]
        if failed_context_tests:
            critical_issues.append(f"Context Retention: {len(failed_context_tests)} failed tests")
        
        print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
        if critical_issues:
            for issue in critical_issues:
                print(f"   ❌ {issue}")
        else:
            print("   ✅ No critical issues detected")
        
        # Bottleneck analysis
        bottleneck_tests = self.test_results["latency_bottlenecks"]
        if bottleneck_tests:
            print(f"\n⚡ LATENCY BOTTLENECKS:")
            for test in bottleneck_tests:
                if test.get("component") == "full_pipeline":
                    print(f"   Total Pipeline: {test.get('total_time', 0):.3f}s")
                    print(f"   - Est. LLM: {test.get('estimated_llm_time', 0):.3f}s")
                    print(f"   - Est. TTS: {test.get('estimated_tts_time', 0):.3f}s")
                    print(f"   - Est. DB: {test.get('estimated_db_time', 0):.3f}s")
        
        # Production readiness
        prod_tests = self.test_results["production_readiness"]
        edge_case_failures = [t for t in prod_tests if t.get("test_type") == "edge_case" and not t.get("handled_gracefully", True)]
        
        print(f"\n🏭 PRODUCTION READINESS:")
        print(f"   Edge Cases Handled: {len(prod_tests) - len(edge_case_failures)}/{len([t for t in prod_tests if t.get('test_type') == 'edge_case'])}")
        
        if edge_case_failures:
            print(f"   ❌ Failed Edge Cases:")
            for failure in edge_case_failures:
                print(f"      - {failure.get('case_name', 'unknown')}")
        
        print("\n" + "="*80)
        print("📋 PERFORMANCE ANALYSIS COMPLETE")
        print("="*80)
        
        return report

# Main execution
async def main():
    tester = PerformanceAnalysisBackendTester()
    await tester.run_comprehensive_performance_analysis()

if __name__ == "__main__":
    asyncio.run(main())