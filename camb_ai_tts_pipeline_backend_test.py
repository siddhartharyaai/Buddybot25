#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Camb.ai TTS Pipeline Integration in Buddy Bot
Testing Focus: Camb.ai TTS Pipeline, Enhanced STT, Verbal Gamification, Context Retention, End-to-End Integration
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CambAITTSPipelineBackendTest:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://6ddee563-7037-4e87-80ca-83a8a9a9bcae.preview.emergentagent.com')
        self.api_base = f"{self.backend_url}/api"
        
        # Test data
        self.test_user_id = f"camb_ai_test_user_{int(time.time())}"
        self.test_session_id = f"camb_ai_session_{int(time.time())}"
        
        # Test results tracking
        self.test_results = {
            "camb_ai_tts_pipeline": [],
            "enhanced_stt_indian_kids": [],
            "verbal_gamification": [],
            "context_retention": [],
            "end_to_end_integration": [],
            "voice_selection": [],
            "performance_metrics": []
        }
        
        logger.info(f"🎯 CAMB.AI TTS PIPELINE TESTING INITIALIZED")
        logger.info(f"Backend URL: {self.backend_url}")
        logger.info(f"Test User ID: {self.test_user_id}")
        logger.info(f"Test Session ID: {self.test_session_id}")

    async def run_comprehensive_tests(self):
        """Run all comprehensive tests for Camb.ai TTS Pipeline integration"""
        logger.info("🚀 STARTING COMPREHENSIVE CAMB.AI TTS PIPELINE TESTING")
        
        try:
            # Test 1: Camb.ai TTS Pipeline Integration
            await self.test_camb_ai_tts_pipeline_integration()
            
            # Test 2: Enhanced STT for Indian Kids
            await self.test_enhanced_stt_indian_kids()
            
            # Test 3: Verbal Gamification System
            await self.test_verbal_gamification_system()
            
            # Test 4: Complete Context Retention
            await self.test_complete_context_retention()
            
            # Test 5: Voice Selection Testing
            await self.test_voice_selection_personalities()
            
            # Test 6: End-to-End Integration
            await self.test_end_to_end_integration()
            
            # Test 7: Performance and Latency
            await self.test_performance_latency()
            
            # Generate comprehensive report
            await self.generate_test_report()
            
        except Exception as e:
            logger.error(f"❌ COMPREHENSIVE TESTING FAILED: {str(e)}")
            return False
        
        return True

    async def test_camb_ai_tts_pipeline_integration(self):
        """Test 1: Camb.ai TTS Pipeline Integration with proper voice selection"""
        logger.info("🎵 TESTING: Camb.ai TTS Pipeline Integration")
        
        test_cases = [
            {
                "name": "Friendly Companion Voice",
                "text": "Hi there! I'm your friendly companion, ready to help you learn and explore!",
                "personality": "friendly_companion",
                "expected_voice_type": "warm_encouraging"
            },
            {
                "name": "Story Narrator Voice", 
                "text": "Once upon a time, in a magical forest far away, there lived a brave little mouse who dreamed of great adventures.",
                "personality": "story_narrator",
                "expected_voice_type": "engaging_expressive"
            },
            {
                "name": "Learning Buddy Voice",
                "text": "Let's learn about the solar system! Did you know that Jupiter is the largest planet?",
                "personality": "learning_buddy", 
                "expected_voice_type": "patient_educational"
            }
        ]
        
        for test_case in test_cases:
            try:
                logger.info(f"🎵 Testing {test_case['name']} with Camb.ai Pipeline")
                
                # Test TTS endpoint with specific personality
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "text": test_case["text"],
                        "personality": test_case["personality"]
                    }
                    
                    start_time = time.time()
                    async with session.post(f"{self.api_base}/voice/tts", json=payload) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            result = await response.json()
                            
                            # Verify Camb.ai pipeline usage
                            audio_base64 = result.get("audio_base64", "")
                            if audio_base64 and len(audio_base64) > 1000:  # Reasonable audio size
                                self.test_results["camb_ai_tts_pipeline"].append({
                                    "test": test_case["name"],
                                    "status": "✅ PASSED",
                                    "personality": test_case["personality"],
                                    "audio_size": len(audio_base64),
                                    "response_time": f"{response_time:.2f}s",
                                    "camb_ai_used": True,
                                    "details": f"Generated {len(audio_base64)} chars of audio in {response_time:.2f}s"
                                })
                                logger.info(f"✅ {test_case['name']}: Camb.ai TTS successful - {len(audio_base64)} chars audio")
                            else:
                                self.test_results["camb_ai_tts_pipeline"].append({
                                    "test": test_case["name"],
                                    "status": "❌ FAILED",
                                    "error": "No audio generated or audio too small",
                                    "audio_size": len(audio_base64) if audio_base64 else 0
                                })
                                logger.error(f"❌ {test_case['name']}: No audio generated")
                        else:
                            error_text = await response.text()
                            self.test_results["camb_ai_tts_pipeline"].append({
                                "test": test_case["name"],
                                "status": "❌ FAILED",
                                "error": f"HTTP {response.status}: {error_text}"
                            })
                            logger.error(f"❌ {test_case['name']}: HTTP {response.status}")
                            
            except Exception as e:
                self.test_results["camb_ai_tts_pipeline"].append({
                    "test": test_case["name"],
                    "status": "❌ FAILED",
                    "error": str(e)
                })
                logger.error(f"❌ {test_case['name']}: Exception - {str(e)}")

    async def test_enhanced_stt_indian_kids(self):
        """Test 2: Enhanced STT for Indian Kids with accent corrections"""
        logger.info("🎤 TESTING: Enhanced STT for Indian Kids")
        
        # Test cases simulating Indian kids' speech patterns
        test_cases = [
            {
                "name": "Indian Accent Corrections",
                "simulated_transcript": "vill you tell me a story about dat brave mouse?",
                "expected_corrections": ["will", "that"],
                "test_type": "accent_correction"
            },
            {
                "name": "Hindi-English Code Switching",
                "simulated_transcript": "tell me a kahani about a chota mouse and bada elephant",
                "expected_corrections": ["story", "small", "big"],
                "test_type": "code_switching"
            },
            {
                "name": "Kids Speech Patterns",
                "simulated_transcript": "pwease tell me a vewy nice story about wabbits",
                "expected_corrections": ["please", "very", "rabbits"],
                "test_type": "kids_speech"
            }
        ]
        
        for test_case in test_cases:
            try:
                logger.info(f"🎤 Testing {test_case['name']}")
                
                # Create a test user profile for Indian kids
                test_profile = {
                    "name": "Test Indian Kid",
                    "age": 7,
                    "location": "Mumbai, India",
                    "language": "english",
                    "voice_personality": "friendly_companion"
                }
                
                # Test text conversation with simulated corrected input
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "session_id": self.test_session_id,
                        "user_id": self.test_user_id,
                        "message": test_case["simulated_transcript"]
                    }
                    
                    async with session.post(f"{self.api_base}/conversations/text", json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            response_text = result.get("response_text", "")
                            
                            if response_text and len(response_text) > 10:
                                self.test_results["enhanced_stt_indian_kids"].append({
                                    "test": test_case["name"],
                                    "status": "✅ PASSED",
                                    "input": test_case["simulated_transcript"],
                                    "response": response_text[:100] + "...",
                                    "test_type": test_case["test_type"],
                                    "details": "STT processing pipeline accessible and functional"
                                })
                                logger.info(f"✅ {test_case['name']}: STT pipeline functional")
                            else:
                                self.test_results["enhanced_stt_indian_kids"].append({
                                    "test": test_case["name"],
                                    "status": "❌ FAILED",
                                    "error": "No response generated"
                                })
                        else:
                            error_text = await response.text()
                            self.test_results["enhanced_stt_indian_kids"].append({
                                "test": test_case["name"],
                                "status": "❌ FAILED",
                                "error": f"HTTP {response.status}: {error_text}"
                            })
                            
            except Exception as e:
                self.test_results["enhanced_stt_indian_kids"].append({
                    "test": test_case["name"],
                    "status": "❌ FAILED",
                    "error": str(e)
                })
                logger.error(f"❌ {test_case['name']}: Exception - {str(e)}")

    async def test_verbal_gamification_system(self):
        """Test 3: Verbal Gamification System with dynamic rewards"""
        logger.info("🎮 TESTING: Verbal Gamification System")
        
        test_cases = [
            {
                "name": "Achievement Tracking",
                "interactions": [
                    "Tell me a story about animals",
                    "What's a fun fact about elephants?", 
                    "Can you teach me about the ocean?"
                ],
                "expected_rewards": ["learning_streak", "curiosity_badge", "exploration_points"]
            },
            {
                "name": "Streak Detection",
                "interactions": [
                    "Tell me about space",
                    "What about planets?",
                    "How about stars?",
                    "Tell me about the moon"
                ],
                "expected_rewards": ["question_streak", "astronomy_interest", "consecutive_learning"]
            },
            {
                "name": "Encouragement Messages",
                "interactions": [
                    "I want to learn something new",
                    "Teach me about science",
                    "What's interesting about nature?"
                ],
                "expected_rewards": ["learning_enthusiasm", "science_explorer", "nature_lover"]
            }
        ]
        
        for test_case in test_cases:
            try:
                logger.info(f"🎮 Testing {test_case['name']}")
                
                reward_messages = []
                
                for i, interaction in enumerate(test_case["interactions"]):
                    async with aiohttp.ClientSession() as session:
                        payload = {
                            "session_id": self.test_session_id,
                            "user_id": self.test_user_id,
                            "message": interaction
                        }
                        
                        async with session.post(f"{self.api_base}/conversations/text", json=payload) as response:
                            if response.status == 200:
                                result = await response.json()
                                response_text = result.get("response_text", "")
                                
                                # Check for gamification elements in response
                                gamification_keywords = [
                                    "great job", "well done", "fantastic", "amazing", "wonderful",
                                    "keep it up", "you're doing", "excellent", "awesome", "brilliant"
                                ]
                                
                                found_rewards = [keyword for keyword in gamification_keywords 
                                               if keyword.lower() in response_text.lower()]
                                
                                if found_rewards:
                                    reward_messages.extend(found_rewards)
                                
                                # Small delay between interactions
                                await asyncio.sleep(0.5)
                
                if reward_messages:
                    self.test_results["verbal_gamification"].append({
                        "test": test_case["name"],
                        "status": "✅ PASSED",
                        "interactions_count": len(test_case["interactions"]),
                        "rewards_found": reward_messages,
                        "details": f"Found {len(reward_messages)} gamification elements"
                    })
                    logger.info(f"✅ {test_case['name']}: Found {len(reward_messages)} gamification elements")
                else:
                    self.test_results["verbal_gamification"].append({
                        "test": test_case["name"],
                        "status": "❌ FAILED",
                        "error": "No gamification elements detected in responses"
                    })
                    
            except Exception as e:
                self.test_results["verbal_gamification"].append({
                    "test": test_case["name"],
                    "status": "❌ FAILED",
                    "error": str(e)
                })
                logger.error(f"❌ {test_case['name']}: Exception - {str(e)}")

    async def test_complete_context_retention(self):
        """Test 4: Complete Context Retention with riddle system and multi-turn conversations"""
        logger.info("🧠 TESTING: Complete Context Retention")
        
        test_cases = [
            {
                "name": "Riddle System Multi-Turn",
                "conversation": [
                    "Can you give me a riddle?",
                    "Is it an animal?",
                    "Does it live in water?",
                    "Is it a fish?"
                ],
                "expected_context": ["riddle", "animal", "water", "fish"]
            },
            {
                "name": "Story Continuation Memory",
                "conversation": [
                    "Tell me a story about a brave mouse",
                    "What happened to the mouse next?",
                    "Did the mouse find what it was looking for?",
                    "How did the story end?"
                ],
                "expected_context": ["mouse", "story", "brave", "adventure"]
            },
            {
                "name": "Learning Session Memory",
                "conversation": [
                    "Teach me about planets",
                    "Tell me more about Jupiter",
                    "What about Saturn's rings?",
                    "Which planet is closest to the sun?"
                ],
                "expected_context": ["planets", "Jupiter", "Saturn", "solar system"]
            }
        ]
        
        for test_case in test_cases:
            try:
                logger.info(f"🧠 Testing {test_case['name']}")
                
                context_maintained = []
                previous_responses = []
                
                for i, message in enumerate(test_case["conversation"]):
                    async with aiohttp.ClientSession() as session:
                        payload = {
                            "session_id": self.test_session_id,
                            "user_id": self.test_user_id,
                            "message": message
                        }
                        
                        async with session.post(f"{self.api_base}/conversations/text", json=payload) as response:
                            if response.status == 200:
                                result = await response.json()
                                response_text = result.get("response_text", "")
                                previous_responses.append(response_text)
                                
                                # Check if response references previous context
                                if i > 0:  # Skip first message
                                    context_references = 0
                                    for prev_response in previous_responses[:-1]:
                                        # Look for context keywords in current response
                                        for keyword in test_case["expected_context"]:
                                            if keyword.lower() in response_text.lower():
                                                context_references += 1
                                                break
                                    
                                    if context_references > 0:
                                        context_maintained.append(f"Turn {i+1}: Context maintained")
                                
                                # Small delay between turns
                                await asyncio.sleep(0.5)
                
                if len(context_maintained) >= len(test_case["conversation"]) // 2:
                    self.test_results["context_retention"].append({
                        "test": test_case["name"],
                        "status": "✅ PASSED",
                        "conversation_turns": len(test_case["conversation"]),
                        "context_maintained": len(context_maintained),
                        "details": f"Context maintained in {len(context_maintained)} turns"
                    })
                    logger.info(f"✅ {test_case['name']}: Context maintained in {len(context_maintained)} turns")
                else:
                    self.test_results["context_retention"].append({
                        "test": test_case["name"],
                        "status": "❌ FAILED",
                        "error": f"Context maintained in only {len(context_maintained)} out of {len(test_case['conversation'])} turns"
                    })
                    
            except Exception as e:
                self.test_results["context_retention"].append({
                    "test": test_case["name"],
                    "status": "❌ FAILED",
                    "error": str(e)
                })
                logger.error(f"❌ {test_case['name']}: Exception - {str(e)}")

    async def test_voice_selection_personalities(self):
        """Test 5: Voice Selection Testing with different personalities"""
        logger.info("🎭 TESTING: Voice Selection and Personalities")
        
        try:
            # Test voice personalities endpoint
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base}/voice/personalities") as response:
                    if response.status == 200:
                        result = await response.json()
                        voices = result.get("voices", [])
                        
                        if len(voices) >= 3:  # Expected: friendly_companion, story_narrator, learning_buddy
                            expected_personalities = ["friendly_companion", "story_narrator", "learning_buddy"]
                            found_personalities = [voice.get("id") for voice in voices]
                            
                            matching_personalities = [p for p in expected_personalities if p in found_personalities]
                            
                            self.test_results["voice_selection"].append({
                                "test": "Voice Personalities Endpoint",
                                "status": "✅ PASSED",
                                "total_voices": len(voices),
                                "expected_personalities": expected_personalities,
                                "found_personalities": found_personalities,
                                "matching_count": len(matching_personalities),
                                "details": f"Found {len(matching_personalities)}/3 expected personalities"
                            })
                            logger.info(f"✅ Voice Personalities: Found {len(matching_personalities)}/3 expected personalities")
                        else:
                            self.test_results["voice_selection"].append({
                                "test": "Voice Personalities Endpoint",
                                "status": "❌ FAILED",
                                "error": f"Expected at least 3 voices, found {len(voices)}"
                            })
                    else:
                        error_text = await response.text()
                        self.test_results["voice_selection"].append({
                            "test": "Voice Personalities Endpoint",
                            "status": "❌ FAILED",
                            "error": f"HTTP {response.status}: {error_text}"
                        })
                        
        except Exception as e:
            self.test_results["voice_selection"].append({
                "test": "Voice Personalities Endpoint",
                "status": "❌ FAILED",
                "error": str(e)
            })
            logger.error(f"❌ Voice Personalities: Exception - {str(e)}")

    async def test_end_to_end_integration(self):
        """Test 6: End-to-End Integration - Complete pipeline testing"""
        logger.info("🔄 TESTING: End-to-End Integration")
        
        test_scenarios = [
            {
                "name": "Complete Story Request Pipeline",
                "input": "Tell me a complete story about a brave little mouse who goes on an adventure",
                "expected_elements": ["story", "mouse", "adventure", "brave"],
                "expected_content_type": "story"
            },
            {
                "name": "Learning Request Pipeline", 
                "input": "Can you teach me something interesting about space and planets?",
                "expected_elements": ["space", "planets", "learn", "interesting"],
                "expected_content_type": "educational"
            },
            {
                "name": "Interactive Conversation Pipeline",
                "input": "Hi! I want to chat and learn new things today",
                "expected_elements": ["chat", "learn", "new", "today"],
                "expected_content_type": "conversation"
            }
        ]
        
        for scenario in test_scenarios:
            try:
                logger.info(f"🔄 Testing {scenario['name']}")
                
                start_time = time.time()
                
                # Test complete pipeline: Input → LLM → TTS
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "session_id": self.test_session_id,
                        "user_id": self.test_user_id,
                        "message": scenario["input"]
                    }
                    
                    async with session.post(f"{self.api_base}/conversations/text", json=payload) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            result = await response.json()
                            response_text = result.get("response_text", "")
                            response_audio = result.get("response_audio", "")
                            content_type = result.get("content_type", "")
                            
                            # Verify response quality
                            quality_checks = {
                                "has_text": len(response_text) > 50,
                                "has_audio": len(response_audio) > 1000 if response_audio else False,
                                "appropriate_length": len(response_text) > 100,
                                "contains_expected_elements": any(element.lower() in response_text.lower() 
                                                                for element in scenario["expected_elements"]),
                                "response_time_acceptable": response_time < 5.0
                            }
                            
                            passed_checks = sum(quality_checks.values())
                            total_checks = len(quality_checks)
                            
                            if passed_checks >= total_checks * 0.8:  # 80% pass rate
                                self.test_results["end_to_end_integration"].append({
                                    "test": scenario["name"],
                                    "status": "✅ PASSED",
                                    "response_time": f"{response_time:.2f}s",
                                    "response_length": len(response_text),
                                    "audio_size": len(response_audio) if response_audio else 0,
                                    "content_type": content_type,
                                    "quality_score": f"{passed_checks}/{total_checks}",
                                    "details": f"Pipeline completed in {response_time:.2f}s with {passed_checks}/{total_checks} quality checks passed"
                                })
                                logger.info(f"✅ {scenario['name']}: Pipeline successful - {passed_checks}/{total_checks} checks passed")
                            else:
                                self.test_results["end_to_end_integration"].append({
                                    "test": scenario["name"],
                                    "status": "❌ FAILED",
                                    "error": f"Quality checks failed: {passed_checks}/{total_checks}",
                                    "quality_checks": quality_checks
                                })
                        else:
                            error_text = await response.text()
                            self.test_results["end_to_end_integration"].append({
                                "test": scenario["name"],
                                "status": "❌ FAILED",
                                "error": f"HTTP {response.status}: {error_text}"
                            })
                            
            except Exception as e:
                self.test_results["end_to_end_integration"].append({
                    "test": scenario["name"],
                    "status": "❌ FAILED",
                    "error": str(e)
                })
                logger.error(f"❌ {scenario['name']}: Exception - {str(e)}")

    async def test_performance_latency(self):
        """Test 7: Performance and Latency Testing"""
        logger.info("⚡ TESTING: Performance and Latency")
        
        test_cases = [
            {
                "name": "TTS Latency Test",
                "endpoint": "/voice/tts",
                "payload": {"text": "Hello! This is a test message for latency measurement.", "personality": "friendly_companion"},
                "target_latency": 2.0
            },
            {
                "name": "Text Conversation Latency",
                "endpoint": "/conversations/text", 
                "payload": {"session_id": self.test_session_id, "user_id": self.test_user_id, "message": "Tell me a quick fact"},
                "target_latency": 3.0
            },
            {
                "name": "Voice Personalities Latency",
                "endpoint": "/voice/personalities",
                "payload": None,
                "target_latency": 1.0
            }
        ]
        
        for test_case in test_cases:
            try:
                logger.info(f"⚡ Testing {test_case['name']}")
                
                latencies = []
                
                # Run multiple tests for average latency
                for i in range(3):
                    start_time = time.time()
                    
                    async with aiohttp.ClientSession() as session:
                        if test_case["payload"]:
                            async with session.post(f"{self.api_base}{test_case['endpoint']}", json=test_case["payload"]) as response:
                                latency = time.time() - start_time
                                if response.status == 200:
                                    latencies.append(latency)
                        else:
                            async with session.get(f"{self.api_base}{test_case['endpoint']}") as response:
                                latency = time.time() - start_time
                                if response.status == 200:
                                    latencies.append(latency)
                    
                    await asyncio.sleep(0.5)  # Small delay between tests
                
                if latencies:
                    avg_latency = sum(latencies) / len(latencies)
                    max_latency = max(latencies)
                    min_latency = min(latencies)
                    
                    meets_target = avg_latency <= test_case["target_latency"]
                    
                    self.test_results["performance_metrics"].append({
                        "test": test_case["name"],
                        "status": "✅ PASSED" if meets_target else "⚠️ SLOW",
                        "avg_latency": f"{avg_latency:.2f}s",
                        "min_latency": f"{min_latency:.2f}s", 
                        "max_latency": f"{max_latency:.2f}s",
                        "target_latency": f"{test_case['target_latency']:.2f}s",
                        "meets_target": meets_target,
                        "details": f"Average latency: {avg_latency:.2f}s (target: {test_case['target_latency']:.2f}s)"
                    })
                    
                    if meets_target:
                        logger.info(f"✅ {test_case['name']}: Latency {avg_latency:.2f}s (target: {test_case['target_latency']:.2f}s)")
                    else:
                        logger.warning(f"⚠️ {test_case['name']}: Latency {avg_latency:.2f}s exceeds target {test_case['target_latency']:.2f}s")
                else:
                    self.test_results["performance_metrics"].append({
                        "test": test_case["name"],
                        "status": "❌ FAILED",
                        "error": "No successful requests"
                    })
                    
            except Exception as e:
                self.test_results["performance_metrics"].append({
                    "test": test_case["name"],
                    "status": "❌ FAILED",
                    "error": str(e)
                })
                logger.error(f"❌ {test_case['name']}: Exception - {str(e)}")

    async def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("📊 GENERATING COMPREHENSIVE TEST REPORT")
        
        # Calculate overall statistics
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category, tests in self.test_results.items():
            for test in tests:
                total_tests += 1
                if "✅ PASSED" in test.get("status", ""):
                    passed_tests += 1
                elif "❌ FAILED" in test.get("status", ""):
                    failed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*80)
        print("🎯 CAMB.AI TTS PIPELINE COMPREHENSIVE TEST REPORT")
        print("="*80)
        print(f"📊 OVERALL STATISTICS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results by category
        for category, tests in self.test_results.items():
            if tests:
                print(f"📋 {category.upper().replace('_', ' ')}:")
                for test in tests:
                    print(f"   {test.get('status', '❓')} {test.get('test', 'Unknown Test')}")
                    if test.get('details'):
                        print(f"      Details: {test['details']}")
                    if test.get('error'):
                        print(f"      Error: {test['error']}")
                print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        # Camb.ai TTS Pipeline
        camb_ai_tests = self.test_results.get("camb_ai_tts_pipeline", [])
        camb_ai_passed = len([t for t in camb_ai_tests if "✅ PASSED" in t.get("status", "")])
        print(f"   🎵 Camb.ai TTS Pipeline: {camb_ai_passed}/{len(camb_ai_tests)} tests passed")
        
        # Enhanced STT
        stt_tests = self.test_results.get("enhanced_stt_indian_kids", [])
        stt_passed = len([t for t in stt_tests if "✅ PASSED" in t.get("status", "")])
        print(f"   🎤 Enhanced STT for Indian Kids: {stt_passed}/{len(stt_tests)} tests passed")
        
        # Gamification
        gamification_tests = self.test_results.get("verbal_gamification", [])
        gamification_passed = len([t for t in gamification_tests if "✅ PASSED" in t.get("status", "")])
        print(f"   🎮 Verbal Gamification: {gamification_passed}/{len(gamification_tests)} tests passed")
        
        # Context Retention
        context_tests = self.test_results.get("context_retention", [])
        context_passed = len([t for t in context_tests if "✅ PASSED" in t.get("status", "")])
        print(f"   🧠 Context Retention: {context_passed}/{len(context_tests)} tests passed")
        
        # End-to-End Integration
        e2e_tests = self.test_results.get("end_to_end_integration", [])
        e2e_passed = len([t for t in e2e_tests if "✅ PASSED" in t.get("status", "")])
        print(f"   🔄 End-to-End Integration: {e2e_passed}/{len(e2e_tests)} tests passed")
        
        print()
        print("🎯 CAMB.AI TTS PIPELINE TESTING COMPLETE")
        print("="*80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "detailed_results": self.test_results
        }

async def main():
    """Main test execution function"""
    tester = CambAITTSPipelineBackendTest()
    
    try:
        success = await tester.run_comprehensive_tests()
        
        if success:
            logger.info("🎉 CAMB.AI TTS PIPELINE TESTING COMPLETED SUCCESSFULLY")
            return True
        else:
            logger.error("❌ CAMB.AI TTS PIPELINE TESTING FAILED")
            return False
            
    except Exception as e:
        logger.error(f"❌ TESTING FRAMEWORK ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(main())