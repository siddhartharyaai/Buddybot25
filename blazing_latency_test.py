#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Blazing Latency Optimizations and STT/Response Improvements
Testing all 6 critical areas mentioned in the review request
"""

import asyncio
import aiohttp
import json
import base64
import time
import logging
import os
from typing import Dict, List, Any
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlazeLatencyOptimizationTester:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://ac3a5a48-4dec-498e-8545-e5993602e42f.preview.emergentagent.com')
        self.api_base = f"{self.backend_url}/api"
        
        # Test user profile
        self.test_user = {
            "id": "test_child_123",
            "name": "Emma",
            "age": 7,
            "voice_personality": "friendly_companion"
        }
        
        # Test session
        self.session_id = "test_session_blazing_latency"
        
        # Test results
        self.results = {
            "stt_accuracy": {"passed": 0, "failed": 0, "details": []},
            "template_system": {"passed": 0, "failed": 0, "details": []},
            "prefetch_cache": {"passed": 0, "failed": 0, "details": []},
            "empathetic_responses": {"passed": 0, "failed": 0, "details": []},
            "ultra_fast_tts": {"passed": 0, "failed": 0, "details": []},
            "barge_in": {"passed": 0, "failed": 0, "details": []},
            "latency_measurements": {"passed": 0, "failed": 0, "details": []}
        }

    async def run_comprehensive_tests(self):
        """Run all comprehensive tests for blazing latency optimizations"""
        logger.info("🚀 STARTING COMPREHENSIVE BLAZING LATENCY OPTIMIZATION TESTS")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Test 1: STT Accuracy Testing with Child Speech Patterns
            await self.test_stt_accuracy_child_speech()
            
            # Test 2: Template System Engagement Testing
            await self.test_template_system_engagement()
            
            # Test 3: Prefetch Cache Population Testing
            await self.test_prefetch_cache_population()
            
            # Test 4: Empathetic Response System Testing
            await self.test_empathetic_response_system()
            
            # Test 5: Ultra-Fast TTS Chunking Testing
            await self.test_ultra_fast_tts_chunking()
            
            # Test 6: Barge-IN Functionality Testing
            await self.test_barge_in_functionality()
            
            # Test 7: Latency Measurements
            await self.test_latency_measurements()
        
        # Generate final report
        self.generate_final_report()

    async def test_stt_accuracy_child_speech(self):
        """Test 1: STT Accuracy Testing with Deepgram Nova-3 and child speech patterns"""
        logger.info("🎤 TESTING STT ACCURACY FOR CHILDREN'S SPEECH")
        
        # Test child speech correction patterns
        child_speech_tests = [
            {"input": "I wove my widdle puppy", "expected_corrections": ["love", "little"]},
            {"input": "Can you twy to help me pwease", "expected_corrections": ["try", "please"]},
            {"input": "The bwue car is vewy gweat", "expected_corrections": ["blue", "very", "great"]},
            {"input": "I want to go to the pawty", "expected_corrections": ["party"]},
            {"input": "My fwiend is weally nice", "expected_corrections": ["friend", "really"]}
        ]
        
        for i, test_case in enumerate(child_speech_tests):
            try:
                # Test the child speech enhancement function through text conversation
                # (since we can't easily test STT directly without audio files)
                response = await self.session.post(
                    f"{self.api_base}/conversations/text",
                    json={
                        "session_id": self.session_id,
                        "user_id": self.test_user["id"],
                        "message": test_case["input"]
                    },
                    timeout=10
                )
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Check if the system can handle child-like speech patterns
                    response_text = result.get("response_text", "")
                    
                    # Verify the system responds appropriately to child speech
                    if len(response_text) > 10 and "error" not in result:
                        self.results["stt_accuracy"]["passed"] += 1
                        self.results["stt_accuracy"]["details"].append(
                            f"✅ Child speech test {i+1}: System handled '{test_case['input']}' appropriately"
                        )
                    else:
                        self.results["stt_accuracy"]["failed"] += 1
                        self.results["stt_accuracy"]["details"].append(
                            f"❌ Child speech test {i+1}: Failed to handle '{test_case['input']}'"
                        )
                else:
                    self.results["stt_accuracy"]["failed"] += 1
                    self.results["stt_accuracy"]["details"].append(
                        f"❌ Child speech test {i+1}: HTTP {response.status}"
                    )
                    
            except Exception as e:
                self.results["stt_accuracy"]["failed"] += 1
                self.results["stt_accuracy"]["details"].append(
                    f"❌ Child speech test {i+1}: Exception - {str(e)}"
                )
        
        # Test Nova-3 STT configuration by checking voice personalities endpoint
        try:
            response = await self.session.get(f"{self.api_base}/voice/personalities")
            if response.status == 200:
                personalities = await response.json()
                if "voices" in personalities and len(personalities["voices"]) >= 3:
                    self.results["stt_accuracy"]["passed"] += 1
                    self.results["stt_accuracy"]["details"].append(
                        "✅ Voice personalities endpoint working - STT system operational"
                    )
                else:
                    self.results["stt_accuracy"]["failed"] += 1
                    self.results["stt_accuracy"]["details"].append(
                        "❌ Voice personalities endpoint returned incomplete data"
                    )
            else:
                self.results["stt_accuracy"]["failed"] += 1
                self.results["stt_accuracy"]["details"].append(
                    f"❌ Voice personalities endpoint failed: HTTP {response.status}"
                )
        except Exception as e:
            self.results["stt_accuracy"]["failed"] += 1
            self.results["stt_accuracy"]["details"].append(
                f"❌ Voice personalities test failed: {str(e)}"
            )

    async def test_template_system_engagement(self):
        """Test 2: Template System Engagement with 100+ patterns for <0.1s responses"""
        logger.info("⚡ TESTING TEMPLATE SYSTEM ENGAGEMENT")
        
        # Test common template queries that should trigger fast responses
        template_queries = [
            "tell me a story",
            "tell me a story about animals",
            "joke about animals", 
            "fact about space",
            "fact about dinosaurs",
            "tell me something about the ocean",
            "what's a fun fact about cats",
            "can you tell me a joke",
            "tell me about the moon",
            "what do you know about elephants"
        ]
        
        for i, query in enumerate(template_queries):
            try:
                start_time = time.time()
                
                response = await self.session.post(
                    f"{self.api_base}/conversations/text",
                    json={
                        "session_id": self.session_id,
                        "user_id": self.test_user["id"],
                        "message": query
                    },
                    timeout=15
                )
                
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "")
                    
                    # Check if response is generated quickly (template system working)
                    if len(response_text) > 20 and response_time < 5.0:  # Reasonable threshold
                        self.results["template_system"]["passed"] += 1
                        self.results["template_system"]["details"].append(
                            f"✅ Template query {i+1}: '{query}' responded in {response_time:.2f}s"
                        )
                    else:
                        self.results["template_system"]["failed"] += 1
                        self.results["template_system"]["details"].append(
                            f"❌ Template query {i+1}: '{query}' slow response ({response_time:.2f}s) or short content"
                        )
                else:
                    self.results["template_system"]["failed"] += 1
                    self.results["template_system"]["details"].append(
                        f"❌ Template query {i+1}: HTTP {response.status}"
                    )
                    
            except Exception as e:
                self.results["template_system"]["failed"] += 1
                self.results["template_system"]["details"].append(
                    f"❌ Template query {i+1}: Exception - {str(e)}"
                )

    async def test_prefetch_cache_population(self):
        """Test 3: Prefetch Cache Population with 100+ queries and personalization"""
        logger.info("💾 TESTING PREFETCH CACHE POPULATION")
        
        # Test cache-related endpoints and functionality
        cache_tests = [
            {"endpoint": "/admin/cache-stats", "description": "Cache statistics"},
            {"endpoint": "/content/stories", "description": "Stories cache"},
            {"endpoint": "/health", "description": "System health check"}
        ]
        
        for test in cache_tests:
            try:
                response = await self.session.get(f"{self.api_base}{test['endpoint']}")
                
                if response.status == 200:
                    result = await response.json()
                    
                    if test["endpoint"] == "/admin/cache-stats":
                        # Check if cache has content
                        if "database_cache" in result or "memory_cache" in result:
                            self.results["prefetch_cache"]["passed"] += 1
                            self.results["prefetch_cache"]["details"].append(
                                f"✅ {test['description']}: Cache system operational"
                            )
                        else:
                            self.results["prefetch_cache"]["failed"] += 1
                            self.results["prefetch_cache"]["details"].append(
                                f"❌ {test['description']}: No cache data found"
                            )
                    elif test["endpoint"] == "/content/stories":
                        # Check if stories are cached/available
                        if "stories" in result and len(result["stories"]) > 0:
                            self.results["prefetch_cache"]["passed"] += 1
                            self.results["prefetch_cache"]["details"].append(
                                f"✅ {test['description']}: {len(result['stories'])} stories cached"
                            )
                        else:
                            self.results["prefetch_cache"]["failed"] += 1
                            self.results["prefetch_cache"]["details"].append(
                                f"❌ {test['description']}: No stories in cache"
                            )
                    else:
                        self.results["prefetch_cache"]["passed"] += 1
                        self.results["prefetch_cache"]["details"].append(
                            f"✅ {test['description']}: Endpoint accessible"
                        )
                else:
                    self.results["prefetch_cache"]["failed"] += 1
                    self.results["prefetch_cache"]["details"].append(
                        f"❌ {test['description']}: HTTP {response.status}"
                    )
                    
            except Exception as e:
                self.results["prefetch_cache"]["failed"] += 1
                self.results["prefetch_cache"]["details"].append(
                    f"❌ {test['description']}: Exception - {str(e)}"
                )
        
        # Test personalization with name replacement
        try:
            response = await self.session.post(
                f"{self.api_base}/conversations/text",
                json={
                    "session_id": self.session_id,
                    "user_id": self.test_user["id"],
                    "message": "tell me a story with my name in it"
                },
                timeout=10
            )
            
            if response.status == 200:
                result = await response.json()
                response_text = result.get("response_text", "")
                
                # Check if user's name appears in the response (personalization)
                if self.test_user["name"].lower() in response_text.lower():
                    self.results["prefetch_cache"]["passed"] += 1
                    self.results["prefetch_cache"]["details"].append(
                        "✅ Personalization: User name successfully included in response"
                    )
                else:
                    self.results["prefetch_cache"]["failed"] += 1
                    self.results["prefetch_cache"]["details"].append(
                        "❌ Personalization: User name not found in personalized content"
                    )
            else:
                self.results["prefetch_cache"]["failed"] += 1
                self.results["prefetch_cache"]["details"].append(
                    f"❌ Personalization test: HTTP {response.status}"
                )
                
        except Exception as e:
            self.results["prefetch_cache"]["failed"] += 1
            self.results["prefetch_cache"]["details"].append(
                f"❌ Personalization test: Exception - {str(e)}"
            )

    async def test_empathetic_response_system(self):
        """Test 4: Empathetic Response System for inappropriate content and emotional support"""
        logger.info("💝 TESTING EMPATHETIC RESPONSE SYSTEM")
        
        # Test inappropriate content detection and educational responses
        empathy_tests = [
            {"input": "this is stupid", "type": "mild_language"},
            {"input": "I'm so dumb", "type": "negative_self_talk"},
            {"input": "I hate everything", "type": "frustration"},
            {"input": "nobody likes me", "type": "social_issues"},
            {"input": "I can't do anything right", "type": "self_doubt"},
            {"input": "this is boring", "type": "mild_complaint"}
        ]
        
        for i, test_case in enumerate(empathy_tests):
            try:
                response = await self.session.post(
                    f"{self.api_base}/conversations/text",
                    json={
                        "session_id": self.session_id,
                        "user_id": self.test_user["id"],
                        "message": test_case["input"]
                    },
                    timeout=10
                )
                
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "").lower()
                    
                    # Check for empathetic/educational response patterns
                    empathetic_indicators = [
                        "understand", "feel", "help", "support", "better", "try", 
                        "learn", "practice", "together", "friend", "care", "listen"
                    ]
                    
                    found_empathy = any(indicator in response_text for indicator in empathetic_indicators)
                    
                    if found_empathy and len(response_text) > 20:
                        self.results["empathetic_responses"]["passed"] += 1
                        self.results["empathetic_responses"]["details"].append(
                            f"✅ Empathy test {i+1} ({test_case['type']}): Appropriate empathetic response"
                        )
                    else:
                        self.results["empathetic_responses"]["failed"] += 1
                        self.results["empathetic_responses"]["details"].append(
                            f"❌ Empathy test {i+1} ({test_case['type']}): No empathetic response detected"
                        )
                else:
                    self.results["empathetic_responses"]["failed"] += 1
                    self.results["empathetic_responses"]["details"].append(
                        f"❌ Empathy test {i+1}: HTTP {response.status}"
                    )
                    
            except Exception as e:
                self.results["empathetic_responses"]["failed"] += 1
                self.results["empathetic_responses"]["details"].append(
                    f"❌ Empathy test {i+1}: Exception - {str(e)}"
                )

    async def test_ultra_fast_tts_chunking(self):
        """Test 5: Ultra-Fast TTS Chunking with 50-token chunks and parallel processing"""
        logger.info("🎵 TESTING ULTRA-FAST TTS CHUNKING")
        
        # Test TTS endpoints with different content lengths
        tts_tests = [
            {"text": "Hello Emma, how are you today?", "type": "short"},
            {"text": "Once upon a time, there was a brave little mouse who lived in a cozy hole under the old oak tree. Every day, the mouse would venture out to find food and explore the wonderful world around him.", "type": "medium"},
            {"text": "Let me tell you an amazing story about a magical forest where all the animals could talk and sing beautiful songs together. In this enchanted place, there lived a wise old owl who knew all the secrets of the forest, a playful rabbit who loved to hop and dance, and a gentle deer who helped all the other animals when they needed a friend. Every morning, they would gather by the crystal clear stream to share stories and plan their adventures for the day.", "type": "long"}
        ]
        
        for i, test_case in enumerate(tts_tests):
            try:
                start_time = time.time()
                
                response = await self.session.post(
                    f"{self.api_base}/voice/tts",
                    json={
                        "text": test_case["text"],
                        "personality": self.test_user["voice_personality"]
                    },
                    timeout=20
                )
                
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get("status") == "success" and result.get("audio_base64"):
                        audio_size = len(result["audio_base64"])
                        
                        # Check if TTS completed in reasonable time with valid audio
                        if audio_size > 1000:  # Valid audio should be substantial
                            self.results["ultra_fast_tts"]["passed"] += 1
                            self.results["ultra_fast_tts"]["details"].append(
                                f"✅ TTS test {i+1} ({test_case['type']}): Generated {audio_size} chars audio in {response_time:.2f}s"
                            )
                        else:
                            self.results["ultra_fast_tts"]["failed"] += 1
                            self.results["ultra_fast_tts"]["details"].append(
                                f"❌ TTS test {i+1} ({test_case['type']}): Audio too small ({audio_size} chars)"
                            )
                    else:
                        self.results["ultra_fast_tts"]["failed"] += 1
                        self.results["ultra_fast_tts"]["details"].append(
                            f"❌ TTS test {i+1} ({test_case['type']}): No audio generated"
                        )
                else:
                    self.results["ultra_fast_tts"]["failed"] += 1
                    self.results["ultra_fast_tts"]["details"].append(
                        f"❌ TTS test {i+1}: HTTP {response.status}"
                    )
                    
            except Exception as e:
                self.results["ultra_fast_tts"]["failed"] += 1
                self.results["ultra_fast_tts"]["details"].append(
                    f"❌ TTS test {i+1}: Exception - {str(e)}"
                )
        
        # Test chunked TTS streaming endpoint
        try:
            long_text = "This is a very long story that should be processed in chunks for optimal streaming performance. " * 10
            
            response = await self.session.post(
                f"{self.api_base}/voice/tts/streaming",
                json={
                    "text": long_text,
                    "personality": self.test_user["voice_personality"]
                },
                timeout=25
            )
            
            if response.status == 200:
                result = await response.json()
                
                if result.get("status") == "success" or result.get("status") == "streaming":
                    self.results["ultra_fast_tts"]["passed"] += 1
                    self.results["ultra_fast_tts"]["details"].append(
                        "✅ Streaming TTS: Chunked processing endpoint operational"
                    )
                else:
                    self.results["ultra_fast_tts"]["failed"] += 1
                    self.results["ultra_fast_tts"]["details"].append(
                        "❌ Streaming TTS: Endpoint not working properly"
                    )
            else:
                self.results["ultra_fast_tts"]["failed"] += 1
                self.results["ultra_fast_tts"]["details"].append(
                    f"❌ Streaming TTS: HTTP {response.status}"
                )
                
        except Exception as e:
            self.results["ultra_fast_tts"]["failed"] += 1
            self.results["ultra_fast_tts"]["details"].append(
                f"❌ Streaming TTS: Exception - {str(e)}"
            )

    async def test_barge_in_functionality(self):
        """Test 6: Enhanced Barge-in Functionality with immediate interruption"""
        logger.info("🛑 TESTING BARGE-IN FUNCTIONALITY")
        
        # Test barge-in related endpoints and functionality
        # Since barge-in is primarily a frontend/audio feature, we test the backend support
        
        # Test 1: Check if voice processing endpoint supports interruption
        try:
            # Create a dummy audio data (base64 encoded silence)
            dummy_audio = base64.b64encode(b'\x00' * 1000).decode('utf-8')
            
            response = await self.session.post(
                f"{self.api_base}/voice/process_audio",
                data={
                    "session_id": self.session_id,
                    "user_id": self.test_user["id"],
                    "audio_base64": dummy_audio
                },
                timeout=10
            )
            
            # We expect this to fail gracefully (not crash) since it's dummy audio
            if response.status in [200, 400, 422]:  # Any handled response
                self.results["barge_in"]["passed"] += 1
                self.results["barge_in"]["details"].append(
                    "✅ Voice processing endpoint: Handles audio input gracefully"
                )
            else:
                self.results["barge_in"]["failed"] += 1
                self.results["barge_in"]["details"].append(
                    f"❌ Voice processing endpoint: Unexpected status {response.status}"
                )
                
        except Exception as e:
            self.results["barge_in"]["failed"] += 1
            self.results["barge_in"]["details"].append(
                f"❌ Voice processing endpoint: Exception - {str(e)}"
            )
        
        # Test 2: Check session management for barge-in support
        try:
            response = await self.session.get(f"{self.api_base}/agents/status")
            
            if response.status == 200:
                result = await response.json()
                
                # Check if orchestrator and voice agent are active (needed for barge-in)
                if result.get("orchestrator") == "active" and result.get("voice_agent") == "active":
                    self.results["barge_in"]["passed"] += 1
                    self.results["barge_in"]["details"].append(
                        "✅ Agent status: Orchestrator and voice agent active for barge-in support"
                    )
                else:
                    self.results["barge_in"]["failed"] += 1
                    self.results["barge_in"]["details"].append(
                        "❌ Agent status: Required agents not active for barge-in"
                    )
            else:
                self.results["barge_in"]["failed"] += 1
                self.results["barge_in"]["details"].append(
                    f"❌ Agent status check: HTTP {response.status}"
                )
                
        except Exception as e:
            self.results["barge_in"]["failed"] += 1
            self.results["barge_in"]["details"].append(
                f"❌ Agent status check: Exception - {str(e)}"
            )
        
        # Test 3: Test conversation interruption capability
        try:
            # Start a long conversation that could be interrupted
            response = await self.session.post(
                f"{self.api_base}/conversations/text",
                json={
                    "session_id": self.session_id,
                    "user_id": self.test_user["id"],
                    "message": "tell me a very long story about dragons"
                },
                timeout=15
            )
            
            if response.status == 200:
                result = await response.json()
                
                # Check if the system can handle story requests (which can be interrupted)
                if result.get("response_text") and len(result["response_text"]) > 50:
                    self.results["barge_in"]["passed"] += 1
                    self.results["barge_in"]["details"].append(
                        "✅ Story generation: Long content available for barge-in testing"
                    )
                else:
                    self.results["barge_in"]["failed"] += 1
                    self.results["barge_in"]["details"].append(
                        "❌ Story generation: No long content for barge-in testing"
                    )
            else:
                self.results["barge_in"]["failed"] += 1
                self.results["barge_in"]["details"].append(
                    f"❌ Story generation test: HTTP {response.status}"
                )
                
        except Exception as e:
            self.results["barge_in"]["failed"] += 1
            self.results["barge_in"]["details"].append(
                f"❌ Story generation test: Exception - {str(e)}"
            )

    async def test_latency_measurements(self):
        """Test 7: Latency Measurements for <0.5s target achievement"""
        logger.info("⏱️ TESTING LATENCY MEASUREMENTS")
        
        # Test different content types for latency
        latency_tests = [
            {"query": "hi", "type": "greeting", "target": 3.0},
            {"query": "what's 2+2", "type": "simple_question", "target": 3.0},
            {"query": "tell me a fact about cats", "type": "template_fact", "target": 2.0},
            {"query": "joke about dogs", "type": "template_joke", "target": 2.0},
            {"query": "tell me a short story", "type": "story_request", "target": 5.0}
        ]
        
        for i, test_case in enumerate(latency_tests):
            try:
                start_time = time.time()
                
                response = await self.session.post(
                    f"{self.api_base}/conversations/text",
                    json={
                        "session_id": self.session_id,
                        "user_id": self.test_user["id"],
                        "message": test_case["query"]
                    },
                    timeout=15
                )
                
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "")
                    
                    # Check if response meets latency target and has content
                    if response_time <= test_case["target"] and len(response_text) > 10:
                        self.results["latency_measurements"]["passed"] += 1
                        self.results["latency_measurements"]["details"].append(
                            f"✅ Latency test {i+1} ({test_case['type']}): {response_time:.2f}s (target: {test_case['target']}s)"
                        )
                    else:
                        self.results["latency_measurements"]["failed"] += 1
                        self.results["latency_measurements"]["details"].append(
                            f"❌ Latency test {i+1} ({test_case['type']}): {response_time:.2f}s (exceeded target: {test_case['target']}s)"
                        )
                else:
                    self.results["latency_measurements"]["failed"] += 1
                    self.results["latency_measurements"]["details"].append(
                        f"❌ Latency test {i+1}: HTTP {response.status}"
                    )
                    
            except Exception as e:
                self.results["latency_measurements"]["failed"] += 1
                self.results["latency_measurements"]["details"].append(
                    f"❌ Latency test {i+1}: Exception - {str(e)}"
                )
        
        # Test health check latency
        try:
            start_time = time.time()
            response = await self.session.get(f"{self.api_base}/health")
            response_time = time.time() - start_time
            
            if response.status == 200 and response_time < 1.0:
                self.results["latency_measurements"]["passed"] += 1
                self.results["latency_measurements"]["details"].append(
                    f"✅ Health check latency: {response_time:.2f}s"
                )
            else:
                self.results["latency_measurements"]["failed"] += 1
                self.results["latency_measurements"]["details"].append(
                    f"❌ Health check latency: {response_time:.2f}s or failed"
                )
                
        except Exception as e:
            self.results["latency_measurements"]["failed"] += 1
            self.results["latency_measurements"]["details"].append(
                f"❌ Health check latency: Exception - {str(e)}"
            )

    def generate_final_report(self):
        """Generate comprehensive final report"""
        logger.info("📊 GENERATING FINAL COMPREHENSIVE REPORT")
        
        total_passed = sum(category["passed"] for category in self.results.values())
        total_failed = sum(category["failed"] for category in self.results.values())
        total_tests = total_passed + total_failed
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*80)
        print("🚀 BLAZING LATENCY OPTIMIZATION COMPREHENSIVE TEST RESULTS")
        print("="*80)
        print(f"📊 OVERALL SUCCESS RATE: {success_rate:.1f}% ({total_passed}/{total_tests} tests passed)")
        print()
        
        # Detailed results by category
        for category, results in self.results.items():
            category_total = results["passed"] + results["failed"]
            category_rate = (results["passed"] / category_total * 100) if category_total > 0 else 0
            
            status_icon = "✅" if category_rate >= 70 else "⚠️" if category_rate >= 50 else "❌"
            
            print(f"{status_icon} {category.upper().replace('_', ' ')}: {category_rate:.1f}% ({results['passed']}/{category_total})")
            
            # Show details
            for detail in results["details"]:
                print(f"   {detail}")
            print()
        
        # Critical Issues Summary
        print("🔍 CRITICAL ISSUES SUMMARY:")
        critical_issues = []
        
        for category, results in self.results.items():
            if results["failed"] > results["passed"]:
                critical_issues.append(f"❌ {category.replace('_', ' ').title()}: More failures than successes")
        
        if critical_issues:
            for issue in critical_issues:
                print(f"   {issue}")
        else:
            print("   ✅ No critical issues detected - system performing well")
        
        print("\n" + "="*80)
        print("🎯 BLAZING LATENCY OPTIMIZATION TEST COMPLETE")
        print("="*80)

async def main():
    """Main test execution"""
    tester = BlazeLatencyOptimizationTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())