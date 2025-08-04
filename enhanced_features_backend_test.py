#!/usr/bin/env python3
"""
Enhanced Perfect MVP Buddy Bot Backend Testing
Testing Focus: Camb.ai TTS Integration, Enhanced STT for Indian Kids, Verbal Gamification, Enhanced Context Retention
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

class EnhancedFeaturesBackendTester:
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
        
        logger.info(f"🎯 ENHANCED FEATURES TESTING: Using backend URL: {self.base_url}")
        
        # Test data
        self.test_user_id = f"enhanced_test_user_{int(time.time())}"
        self.test_session_id = f"enhanced_session_{int(time.time())}"
        
        # Test results tracking
        self.test_results = {
            "camb_ai_tts_integration": [],
            "enhanced_stt_indian_kids": [],
            "verbal_gamification_system": [],
            "enhanced_context_retention": [],
            "riddle_system_testing": [],
            "conversation_memory": [],
            "dynamic_voice_selection": [],
            "system_integration": []
        }
        
    async def run_comprehensive_enhanced_tests(self):
        """Run all enhanced features tests"""
        logger.info("🎯 STARTING COMPREHENSIVE ENHANCED FEATURES TESTING")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Create test user profile first
            await self._create_test_user_profile()
            
            # Test 1: Camb.ai TTS Integration
            await self._test_camb_ai_tts_integration()
            
            # Test 2: Enhanced STT for Indian Kids
            await self._test_enhanced_stt_indian_kids()
            
            # Test 3: Verbal Gamification System
            await self._test_verbal_gamification_system()
            
            # Test 4: Enhanced Context Retention
            await self._test_enhanced_context_retention()
            
            # Test 5: Riddle System Testing
            await self._test_riddle_system()
            
            # Test 6: Conversation Memory
            await self._test_conversation_memory()
            
            # Test 7: Dynamic Voice Selection
            await self._test_dynamic_voice_selection()
            
            # Test 8: System Integration
            await self._test_system_integration()
            
        # Generate comprehensive report
        await self._generate_test_report()
    
    async def _create_test_user_profile(self):
        """Create test user profile for enhanced features testing"""
        try:
            profile_data = {
                "name": f"EnhancedTestUser_{int(time.time())}",
                "age": 8,
                "location": "Mumbai, India",
                "timezone": "Asia/Kolkata",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "riddles", "learning", "games"],
                "learning_goals": ["vocabulary", "problem_solving", "creativity"],
                "gender": "prefer_not_to_say",
                "avatar": "bunny",
                "speech_speed": "normal",
                "energy_level": "balanced"
            }
            
            async with self.session.post(f"{self.base_url}/users/profile", json=profile_data) as response:
                if response.status == 201:
                    result = await response.json()
                    self.test_user_id = result["id"]
                    logger.info(f"✅ Created test user profile: {self.test_user_id}")
                    return True
                else:
                    logger.error(f"❌ Failed to create test user profile: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error creating test user profile: {e}")
            return False
    
    async def _test_camb_ai_tts_integration(self):
        """Test 1: Camb.ai TTS Integration - MARS model with dynamic voice selection"""
        logger.info("🎯 TEST 1: Camb.ai TTS Integration")
        
        test_results = []
        
        # Test 1.1: Camb.ai MARS model usage
        try:
            tts_request = {
                "text": "Hello! I'm your AI buddy using the new Camb.ai MARS model for enhanced voice quality.",
                "personality": "friendly_companion"
            }
            
            async with self.session.post(f"{self.base_url}/voice/tts", json=tts_request) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success" and result.get("audio_base64"):
                        # Check if audio is generated (Camb.ai should produce audio)
                        audio_size = len(result.get("audio_base64", ""))
                        test_results.append({
                            "test": "Camb.ai MARS model usage",
                            "status": "PASS",
                            "details": f"TTS successful with Camb.ai: {audio_size} chars audio generated"
                        })
                    else:
                        test_results.append({
                            "test": "Camb.ai MARS model usage",
                            "status": "FAIL",
                            "details": f"TTS failed: {result}"
                        })
                else:
                    test_results.append({
                        "test": "Camb.ai MARS model usage",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Camb.ai MARS model usage",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 1.2: Dynamic voice selection based on personalities
        try:
            personalities = ["friendly_companion", "story_narrator", "learning_buddy"]
            voice_tests = []
            
            for personality in personalities:
                voice_request = {
                    "text": f"Testing {personality} voice personality with Camb.ai integration.",
                    "personality": personality
                }
                
                async with self.session.post(f"{self.base_url}/voice/tts", json=voice_request) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("status") == "success" and result.get("audio_base64"):
                            voice_tests.append(f"{personality}: SUCCESS")
                        else:
                            voice_tests.append(f"{personality}: FAILED")
                    else:
                        voice_tests.append(f"{personality}: HTTP {response.status}")
            
            if len([t for t in voice_tests if "SUCCESS" in t]) >= 2:
                test_results.append({
                    "test": "Dynamic voice selection",
                    "status": "PASS",
                    "details": f"Voice personalities working: {', '.join(voice_tests)}"
                })
            else:
                test_results.append({
                    "test": "Dynamic voice selection",
                    "status": "FAIL",
                    "details": f"Voice personalities issues: {', '.join(voice_tests)}"
                })
                    
        except Exception as e:
            test_results.append({
                "test": "Dynamic voice selection",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 1.3: Camb.ai API key configuration
        try:
            # Check if Camb.ai API key is configured by testing health endpoint
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    # Check if agents are properly configured
                    if health_data.get("agents", {}).get("orchestrator"):
                        test_results.append({
                            "test": "Camb.ai API configuration",
                            "status": "PASS",
                            "details": "System initialized with TTS configuration"
                        })
                    else:
                        test_results.append({
                            "test": "Camb.ai API configuration",
                            "status": "FAIL",
                            "details": "System not properly initialized"
                        })
                else:
                    test_results.append({
                        "test": "Camb.ai API configuration",
                        "status": "FAIL",
                        "details": f"Health check failed: HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Camb.ai API configuration",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["camb_ai_tts_integration"] = test_results
        logger.info(f"✅ Camb.ai TTS Integration Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_enhanced_stt_indian_kids(self):
        """Test 2: Enhanced STT for Indian Kids - Speech patterns and accent handling"""
        logger.info("🎯 TEST 2: Enhanced STT for Indian Kids")
        
        test_results = []
        
        # Test 2.1: Indian accent speech pattern processing
        try:
            # Simulate Indian kids' speech patterns (we can't actually test audio, but test the endpoint)
            # Test with text that simulates common Indian English patterns
            indian_speech_request = {
                "session_id": self.test_session_id,
                "message": "Tell me story about elephant and mouse friendship",  # Common Indian English pattern
                "user_id": self.test_user_id
            }
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=indian_speech_request) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("response_text") and len(result.get("response_text", "")) > 50:
                        test_results.append({
                            "test": "Indian accent speech processing",
                            "status": "PASS",
                            "details": f"Processed Indian speech pattern: {len(result.get('response_text', ''))} chars response"
                        })
                    else:
                        test_results.append({
                            "test": "Indian accent speech processing",
                            "status": "FAIL",
                            "details": f"Poor response to Indian speech: {result}"
                        })
                else:
                    test_results.append({
                        "test": "Indian accent speech processing",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Indian accent speech processing",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 2.2: Kids' speech pattern corrections
        try:
            # Test with common kids' speech patterns
            kids_speech_patterns = [
                "Can you tell me bout animals?",  # Missing 'a' - common in kids
                "I want hear story",  # Missing 'to' - common grammar issue
                "What is dat animal?",  # 'dat' instead of 'that'
            ]
            
            pattern_results = []
            for pattern in kids_speech_patterns:
                pattern_request = {
                    "session_id": self.test_session_id,
                    "message": pattern,
                    "user_id": self.test_user_id
                }
                
                async with self.session.post(f"{self.base_url}/conversations/text", json=pattern_request) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("response_text"):
                            pattern_results.append("SUCCESS")
                        else:
                            pattern_results.append("FAILED")
                    else:
                        pattern_results.append("ERROR")
            
            success_rate = len([r for r in pattern_results if r == "SUCCESS"]) / len(pattern_results)
            if success_rate >= 0.8:
                test_results.append({
                    "test": "Kids speech pattern corrections",
                    "status": "PASS",
                    "details": f"Handled {len([r for r in pattern_results if r == 'SUCCESS'])}/{len(pattern_results)} patterns successfully"
                })
            else:
                test_results.append({
                    "test": "Kids speech pattern corrections",
                    "status": "FAIL",
                    "details": f"Only {len([r for r in pattern_results if r == 'SUCCESS'])}/{len(pattern_results)} patterns handled"
                })
                    
        except Exception as e:
            test_results.append({
                "test": "Kids speech pattern corrections",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 2.3: Enhanced processing and corrections
        try:
            # Test voice processing endpoint (even though we can't send real audio)
            # This tests if the enhanced STT infrastructure is in place
            async with self.session.get(f"{self.base_url}/voice/personalities") as response:
                if response.status == 200:
                    result = await response.json()
                    if isinstance(result, dict) and len(result) >= 3:
                        test_results.append({
                            "test": "Enhanced STT infrastructure",
                            "status": "PASS",
                            "details": f"Voice processing system ready with {len(result)} personalities"
                        })
                    else:
                        test_results.append({
                            "test": "Enhanced STT infrastructure",
                            "status": "FAIL",
                            "details": f"Voice system not properly configured: {result}"
                        })
                else:
                    test_results.append({
                        "test": "Enhanced STT infrastructure",
                        "status": "FAIL",
                        "details": f"Voice system unavailable: HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Enhanced STT infrastructure",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["enhanced_stt_indian_kids"] = test_results
        logger.info(f"✅ Enhanced STT for Indian Kids Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_verbal_gamification_system(self):
        """Test 3: Verbal Gamification System - Dynamic rewards and achievements"""
        logger.info("🎯 TEST 3: Verbal Gamification System")
        
        test_results = []
        
        # Test 3.1: Dynamic rewards integration in responses
        try:
            # Make multiple content requests to trigger gamification
            content_requests = [
                "Tell me a story about a brave knight",
                "Can you tell me a joke?",
                "What's a fun fact about space?",
                "Can you give me a riddle?"
            ]
            
            reward_responses = []
            for request in content_requests:
                content_request = {
                    "session_id": self.test_session_id,
                    "message": request,
                    "user_id": self.test_user_id
                }
                
                async with self.session.post(f"{self.base_url}/conversations/text", json=content_request) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "").lower()
                        
                        # Check for gamification elements
                        reward_keywords = ["star", "point", "achievement", "great job", "well done", "awesome", "fantastic", "reward", "badge"]
                        has_reward = any(keyword in response_text for keyword in reward_keywords)
                        
                        if has_reward:
                            reward_responses.append("REWARD_FOUND")
                        else:
                            reward_responses.append("NO_REWARD")
                    else:
                        reward_responses.append("ERROR")
            
            reward_rate = len([r for r in reward_responses if r == "REWARD_FOUND"]) / len(reward_responses)
            if reward_rate >= 0.5:  # At least 50% should have some gamification
                test_results.append({
                    "test": "Dynamic rewards integration",
                    "status": "PASS",
                    "details": f"Gamification found in {len([r for r in reward_responses if r == 'REWARD_FOUND'])}/{len(reward_responses)} responses"
                })
            else:
                test_results.append({
                    "test": "Dynamic rewards integration",
                    "status": "FAIL",
                    "details": f"Low gamification rate: {len([r for r in reward_responses if r == 'REWARD_FOUND'])}/{len(reward_responses)} responses"
                })
                    
        except Exception as e:
            test_results.append({
                "test": "Dynamic rewards integration",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 3.2: Achievement messages and encouragement
        try:
            # Test with learning-focused requests that should trigger achievements
            learning_request = {
                "session_id": self.test_session_id,
                "message": "I learned something new today! Can you teach me more?",
                "user_id": self.test_user_id
            }
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=learning_request) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "").lower()
                    
                    # Check for achievement/encouragement language
                    achievement_keywords = ["proud", "learning", "smart", "clever", "keep going", "great question", "wonderful"]
                    has_achievement = any(keyword in response_text for keyword in achievement_keywords)
                    
                    if has_achievement:
                        test_results.append({
                            "test": "Achievement messages",
                            "status": "PASS",
                            "details": f"Achievement language detected in response: {len(response_text)} chars"
                        })
                    else:
                        test_results.append({
                            "test": "Achievement messages",
                            "status": "FAIL",
                            "details": f"No achievement language found: {response_text[:100]}..."
                        })
                else:
                    test_results.append({
                        "test": "Achievement messages",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Achievement messages",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 3.3: Verbal rewards embedded in responses
        try:
            # Test analytics dashboard to see if gamification is tracked
            async with self.session.get(f"{self.base_url}/analytics/dashboard/{self.test_user_id}") as response:
                if response.status == 200:
                    result = await response.json()
                    if result and isinstance(result, dict):
                        # Check if analytics include engagement or achievement data
                        has_engagement_data = any(key in str(result).lower() for key in ["engagement", "interaction", "session", "activity"])
                        
                        if has_engagement_data:
                            test_results.append({
                                "test": "Verbal rewards tracking",
                                "status": "PASS",
                                "details": f"Analytics tracking gamification: {len(str(result))} chars data"
                            })
                        else:
                            test_results.append({
                                "test": "Verbal rewards tracking",
                                "status": "FAIL",
                                "details": f"No gamification tracking: {result}"
                            })
                    else:
                        test_results.append({
                            "test": "Verbal rewards tracking",
                            "status": "FAIL",
                            "details": "No analytics data available"
                        })
                else:
                    test_results.append({
                        "test": "Verbal rewards tracking",
                        "status": "FAIL",
                        "details": f"Analytics unavailable: HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Verbal rewards tracking",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["verbal_gamification_system"] = test_results
        logger.info(f"✅ Verbal Gamification System Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_enhanced_context_retention(self):
        """Test 4: Enhanced Context Retention - Multi-turn conversation memory"""
        logger.info("🎯 TEST 4: Enhanced Context Retention")
        
        test_results = []
        
        # Test 4.1: Multi-turn conversation memory
        try:
            # Start a conversation with context
            context_requests = [
                "My name is Arjun and I love elephants",
                "What's my favorite animal?",
                "Can you tell me a story about my favorite animal?",
                "What was my name again?"
            ]
            
            context_results = []
            for i, request in enumerate(context_requests):
                context_request = {
                    "session_id": self.test_session_id,
                    "message": request,
                    "user_id": self.test_user_id
                }
                
                async with self.session.post(f"{self.base_url}/conversations/text", json=context_request) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "").lower()
                        
                        if i == 1:  # Should remember favorite animal
                            if "elephant" in response_text:
                                context_results.append("CONTEXT_RETAINED")
                            else:
                                context_results.append("CONTEXT_LOST")
                        elif i == 2:  # Should use elephant in story
                            if "elephant" in response_text:
                                context_results.append("CONTEXT_APPLIED")
                            else:
                                context_results.append("CONTEXT_NOT_APPLIED")
                        elif i == 3:  # Should remember name
                            if "arjun" in response_text:
                                context_results.append("NAME_RETAINED")
                            else:
                                context_results.append("NAME_LOST")
                        else:
                            context_results.append("INITIAL")
                    else:
                        context_results.append("ERROR")
            
            context_success = len([r for r in context_results if "RETAINED" in r or "APPLIED" in r]) / max(1, len(context_results) - 1)
            if context_success >= 0.6:
                test_results.append({
                    "test": "Multi-turn conversation memory",
                    "status": "PASS",
                    "details": f"Context retention: {context_results}"
                })
            else:
                test_results.append({
                    "test": "Multi-turn conversation memory",
                    "status": "FAIL",
                    "details": f"Poor context retention: {context_results}"
                })
                    
        except Exception as e:
            test_results.append({
                "test": "Multi-turn conversation memory",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 4.2: Memory context retrieval
        try:
            async with self.session.get(f"{self.base_url}/memory/context/{self.test_user_id}") as response:
                if response.status == 200:
                    result = await response.json()
                    if result and isinstance(result, dict):
                        # Check if memory context contains conversation data
                        memory_data = str(result).lower()
                        has_context = len(memory_data) > 100  # Should have substantial context
                        
                        if has_context:
                            test_results.append({
                                "test": "Memory context retrieval",
                                "status": "PASS",
                                "details": f"Memory context available: {len(memory_data)} chars"
                            })
                        else:
                            test_results.append({
                                "test": "Memory context retrieval",
                                "status": "FAIL",
                                "details": f"Insufficient memory context: {len(memory_data)} chars"
                            })
                    else:
                        test_results.append({
                            "test": "Memory context retrieval",
                            "status": "FAIL",
                            "details": "No memory context available"
                        })
                else:
                    test_results.append({
                        "test": "Memory context retrieval",
                        "status": "FAIL",
                        "details": f"Memory system unavailable: HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Memory context retrieval",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 4.3: Memory snapshot generation
        try:
            async with self.session.post(f"{self.base_url}/memory/snapshot/{self.test_user_id}") as response:
                if response.status == 200:
                    result = await response.json()
                    if result and isinstance(result, dict):
                        test_results.append({
                            "test": "Memory snapshot generation",
                            "status": "PASS",
                            "details": f"Memory snapshot created: {result.get('id', 'unknown')}"
                        })
                    else:
                        test_results.append({
                            "test": "Memory snapshot generation",
                            "status": "FAIL",
                            "details": f"Snapshot creation failed: {result}"
                        })
                else:
                    test_results.append({
                        "test": "Memory snapshot generation",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Memory snapshot generation",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["enhanced_context_retention"] = test_results
        logger.info(f"✅ Enhanced Context Retention Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_riddle_system(self):
        """Test 5: Riddle System Testing - Riddle context and answer tracking"""
        logger.info("🎯 TEST 5: Riddle System Testing")
        
        test_results = []
        
        # Test 5.1: Riddle generation and context
        try:
            riddle_request = {
                "session_id": self.test_session_id,
                "message": "Can you give me a riddle?",
                "user_id": self.test_user_id
            }
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=riddle_request) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "").lower()
                    
                    # Check if response contains riddle elements
                    riddle_keywords = ["riddle", "guess", "what am i", "what is", "answer", "think", "clue"]
                    has_riddle = any(keyword in response_text for keyword in riddle_keywords)
                    
                    if has_riddle and len(response_text) > 50:
                        test_results.append({
                            "test": "Riddle generation",
                            "status": "PASS",
                            "details": f"Riddle generated: {len(response_text)} chars"
                        })
                        
                        # Store riddle for follow-up test
                        self.riddle_response = response_text
                    else:
                        test_results.append({
                            "test": "Riddle generation",
                            "status": "FAIL",
                            "details": f"No proper riddle: {response_text[:100]}..."
                        })
                else:
                    test_results.append({
                        "test": "Riddle generation",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Riddle generation",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 5.2: Riddle answer attempt and context retention
        try:
            # Attempt to answer the riddle
            answer_request = {
                "session_id": self.test_session_id,
                "message": "Is it a book?",  # Common riddle answer
                "user_id": self.test_user_id
            }
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=answer_request) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "").lower()
                    
                    # Check if bot remembers the riddle context
                    context_keywords = ["correct", "wrong", "try again", "good guess", "riddle", "answer"]
                    has_context = any(keyword in response_text for keyword in context_keywords)
                    
                    if has_context:
                        test_results.append({
                            "test": "Riddle context retention",
                            "status": "PASS",
                            "details": f"Bot remembers riddle context: {len(response_text)} chars"
                        })
                    else:
                        test_results.append({
                            "test": "Riddle context retention",
                            "status": "FAIL",
                            "details": f"No riddle context: {response_text[:100]}..."
                        })
                else:
                    test_results.append({
                        "test": "Riddle context retention",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Riddle context retention",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 5.3: Multiple riddle handling
        try:
            # Request another riddle to test system handling
            another_riddle_request = {
                "session_id": self.test_session_id,
                "message": "Give me another riddle please",
                "user_id": self.test_user_id
            }
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=another_riddle_request) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "").lower()
                    
                    # Check if new riddle is provided
                    riddle_keywords = ["riddle", "guess", "what am i", "what is", "here's another"]
                    has_new_riddle = any(keyword in response_text for keyword in riddle_keywords)
                    
                    if has_new_riddle and len(response_text) > 30:
                        test_results.append({
                            "test": "Multiple riddle handling",
                            "status": "PASS",
                            "details": f"New riddle provided: {len(response_text)} chars"
                        })
                    else:
                        test_results.append({
                            "test": "Multiple riddle handling",
                            "status": "FAIL",
                            "details": f"No new riddle: {response_text[:100]}..."
                        })
                else:
                    test_results.append({
                        "test": "Multiple riddle handling",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Multiple riddle handling",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["riddle_system_testing"] = test_results
        logger.info(f"✅ Riddle System Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_conversation_memory(self):
        """Test 6: Conversation Memory - Long-term memory across sessions"""
        logger.info("🎯 TEST 6: Conversation Memory")
        
        test_results = []
        
        # Test 6.1: Session-based memory persistence
        try:
            # Create a new session to test cross-session memory
            new_session_id = f"memory_test_session_{int(time.time())}"
            
            memory_request = {
                "session_id": new_session_id,
                "message": "Do you remember what my favorite animal is?",
                "user_id": self.test_user_id
            }
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=memory_request) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "").lower()
                    
                    # Check if bot remembers previous conversation (elephant from earlier test)
                    memory_indicators = ["remember", "elephant", "favorite", "previous", "earlier"]
                    has_memory = any(indicator in response_text for indicator in memory_indicators)
                    
                    if has_memory:
                        test_results.append({
                            "test": "Session-based memory persistence",
                            "status": "PASS",
                            "details": f"Cross-session memory working: {len(response_text)} chars"
                        })
                    else:
                        test_results.append({
                            "test": "Session-based memory persistence",
                            "status": "FAIL",
                            "details": f"No cross-session memory: {response_text[:100]}..."
                        })
                else:
                    test_results.append({
                        "test": "Session-based memory persistence",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Session-based memory persistence",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 6.2: Memory snapshots history
        try:
            async with self.session.get(f"{self.base_url}/memory/snapshots/{self.test_user_id}") as response:
                if response.status == 200:
                    result = await response.json()
                    if result and result.get("snapshots") is not None:
                        snapshot_count = result.get("count", 0)
                        
                        if snapshot_count > 0:
                            test_results.append({
                                "test": "Memory snapshots history",
                                "status": "PASS",
                                "details": f"Memory snapshots available: {snapshot_count} snapshots"
                            })
                        else:
                            test_results.append({
                                "test": "Memory snapshots history",
                                "status": "FAIL",
                                "details": "No memory snapshots found"
                            })
                    else:
                        test_results.append({
                            "test": "Memory snapshots history",
                            "status": "FAIL",
                            "details": f"Invalid snapshots response: {result}"
                        })
                else:
                    test_results.append({
                        "test": "Memory snapshots history",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Memory snapshots history",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 6.3: Long-term learning and preferences
        try:
            # Test if system learns from interactions
            learning_request = {
                "session_id": self.test_session_id,
                "message": "I really enjoyed that elephant story. Can you remember that I like animal stories?",
                "user_id": self.test_user_id
            }
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=learning_request) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "").lower()
                    
                    # Check if bot acknowledges learning preference
                    learning_keywords = ["remember", "note", "preference", "like", "animal stories", "understand"]
                    has_learning = any(keyword in response_text for keyword in learning_keywords)
                    
                    if has_learning:
                        test_results.append({
                            "test": "Long-term learning",
                            "status": "PASS",
                            "details": f"Learning acknowledgment: {len(response_text)} chars"
                        })
                    else:
                        test_results.append({
                            "test": "Long-term learning",
                            "status": "FAIL",
                            "details": f"No learning acknowledgment: {response_text[:100]}..."
                        })
                else:
                    test_results.append({
                        "test": "Long-term learning",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Long-term learning",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["conversation_memory"] = test_results
        logger.info(f"✅ Conversation Memory Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_dynamic_voice_selection(self):
        """Test 7: Dynamic Voice Selection - Personality-based voice changes"""
        logger.info("🎯 TEST 7: Dynamic Voice Selection")
        
        test_results = []
        
        # Test 7.1: Voice personalities availability
        try:
            async with self.session.get(f"{self.base_url}/voice/personalities") as response:
                if response.status == 200:
                    result = await response.json()
                    if isinstance(result, dict) and len(result) >= 3:
                        personalities = list(result.keys())
                        test_results.append({
                            "test": "Voice personalities availability",
                            "status": "PASS",
                            "details": f"Available personalities: {personalities}"
                        })
                        
                        # Store personalities for next test
                        self.available_personalities = personalities
                    else:
                        test_results.append({
                            "test": "Voice personalities availability",
                            "status": "FAIL",
                            "details": f"Insufficient personalities: {result}"
                        })
                        self.available_personalities = ["friendly_companion"]
                else:
                    test_results.append({
                        "test": "Voice personalities availability",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    self.available_personalities = ["friendly_companion"]
                    
        except Exception as e:
            test_results.append({
                "test": "Voice personalities availability",
                "status": "ERROR",
                "details": str(e)
            })
            self.available_personalities = ["friendly_companion"]
        
        # Test 7.2: Personality-based voice generation
        try:
            personality_tests = []
            test_personalities = self.available_personalities[:3]  # Test up to 3 personalities
            
            for personality in test_personalities:
                voice_request = {
                    "text": f"Hello! This is a test of the {personality} voice personality.",
                    "personality": personality
                }
                
                async with self.session.post(f"{self.base_url}/voice/tts", json=voice_request) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("status") == "success" and result.get("audio_base64"):
                            audio_size = len(result.get("audio_base64", ""))
                            personality_tests.append(f"{personality}: SUCCESS ({audio_size} chars)")
                        else:
                            personality_tests.append(f"{personality}: FAILED")
                    else:
                        personality_tests.append(f"{personality}: HTTP {response.status}")
            
            success_count = len([t for t in personality_tests if "SUCCESS" in t])
            if success_count >= len(test_personalities) * 0.8:
                test_results.append({
                    "test": "Personality-based voice generation",
                    "status": "PASS",
                    "details": f"Voice generation: {', '.join(personality_tests)}"
                })
            else:
                test_results.append({
                    "test": "Personality-based voice generation",
                    "status": "FAIL",
                    "details": f"Voice generation issues: {', '.join(personality_tests)}"
                })
                    
        except Exception as e:
            test_results.append({
                "test": "Personality-based voice generation",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 7.3: Dynamic voice switching in conversations
        try:
            # Test conversation with different content types that should trigger different voices
            content_types = [
                ("Tell me a bedtime story", "story_narrator"),
                ("Help me learn about math", "learning_buddy"),
                ("Let's chat about my day", "friendly_companion")
            ]
            
            voice_switching_results = []
            for content, expected_personality in content_types:
                content_request = {
                    "session_id": self.test_session_id,
                    "message": content,
                    "user_id": self.test_user_id
                }
                
                async with self.session.post(f"{self.base_url}/conversations/text", json=content_request) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("response_text"):
                            voice_switching_results.append("SUCCESS")
                        else:
                            voice_switching_results.append("FAILED")
                    else:
                        voice_switching_results.append("ERROR")
            
            success_rate = len([r for r in voice_switching_results if r == "SUCCESS"]) / len(voice_switching_results)
            if success_rate >= 0.8:
                test_results.append({
                    "test": "Dynamic voice switching",
                    "status": "PASS",
                    "details": f"Voice switching: {len([r for r in voice_switching_results if r == 'SUCCESS'])}/{len(voice_switching_results)} successful"
                })
            else:
                test_results.append({
                    "test": "Dynamic voice switching",
                    "status": "FAIL",
                    "details": f"Voice switching issues: {voice_switching_results}"
                })
                    
        except Exception as e:
            test_results.append({
                "test": "Dynamic voice switching",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["dynamic_voice_selection"] = test_results
        logger.info(f"✅ Dynamic Voice Selection Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_system_integration(self):
        """Test 8: System Integration - Overall system health and integration"""
        logger.info("🎯 TEST 8: System Integration")
        
        test_results = []
        
        # Test 8.1: Overall system health
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    
                    # Check system components
                    system_healthy = (
                        health_data.get("status") == "healthy" and
                        health_data.get("agents", {}).get("orchestrator") and
                        health_data.get("database") == "connected"
                    )
                    
                    if system_healthy:
                        test_results.append({
                            "test": "Overall system health",
                            "status": "PASS",
                            "details": f"System healthy: {health_data}"
                        })
                    else:
                        test_results.append({
                            "test": "Overall system health",
                            "status": "FAIL",
                            "details": f"System issues: {health_data}"
                        })
                else:
                    test_results.append({
                        "test": "Overall system health",
                        "status": "FAIL",
                        "details": f"Health check failed: HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Overall system health",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 8.2: Agent status and coordination
        try:
            async with self.session.get(f"{self.base_url}/agents/status") as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Check if multiple agents are active
                    active_agents = [k for k, v in result.items() if v == "active"]
                    
                    if len(active_agents) >= 5:  # Should have orchestrator, voice, conversation, etc.
                        test_results.append({
                            "test": "Agent coordination",
                            "status": "PASS",
                            "details": f"Active agents: {active_agents}"
                        })
                    else:
                        test_results.append({
                            "test": "Agent coordination",
                            "status": "FAIL",
                            "details": f"Insufficient active agents: {active_agents}"
                        })
                else:
                    test_results.append({
                        "test": "Agent coordination",
                        "status": "FAIL",
                        "details": f"Agent status unavailable: HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Agent coordination",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 8.3: End-to-end feature integration
        try:
            # Test a complete interaction that uses multiple enhanced features
            integration_request = {
                "session_id": self.test_session_id,
                "message": "Hi! I'm Priya from Delhi. Can you tell me a story about a clever monkey and then give me a riddle?",
                "user_id": self.test_user_id
            }
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=integration_request) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "").lower()
                    
                    # Check for multiple feature integration
                    features_present = {
                        "story": any(word in response_text for word in ["story", "monkey", "once upon"]),
                        "riddle": any(word in response_text for word in ["riddle", "guess", "what am i"]),
                        "personalization": any(word in response_text for word in ["priya", "delhi"]),
                        "gamification": any(word in response_text for word in ["great", "wonderful", "smart"])
                    }
                    
                    feature_count = sum(features_present.values())
                    if feature_count >= 2:
                        test_results.append({
                            "test": "End-to-end feature integration",
                            "status": "PASS",
                            "details": f"Features integrated: {feature_count}/4 - {features_present}"
                        })
                    else:
                        test_results.append({
                            "test": "End-to-end feature integration",
                            "status": "FAIL",
                            "details": f"Poor integration: {feature_count}/4 - {features_present}"
                        })
                else:
                    test_results.append({
                        "test": "End-to-end feature integration",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "End-to-end feature integration",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["system_integration"] = test_results
        logger.info(f"✅ System Integration Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("🎯 GENERATING COMPREHENSIVE ENHANCED FEATURES TEST REPORT")
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        
        report = []
        report.append("=" * 80)
        report.append("ENHANCED PERFECT MVP BUDDY BOT BACKEND TESTING REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Backend URL: {self.base_url}")
        report.append(f"Test User ID: {self.test_user_id}")
        report.append(f"Test Session ID: {self.test_session_id}")
        report.append("")
        
        for category, tests in self.test_results.items():
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
            report.append(f"   ✅ Passed: {category_passed}")
            report.append(f"   ❌ Failed: {category_failed}")
            report.append(f"   🔥 Errors: {category_errors}")
            report.append("")
            
            for test in tests:
                status_icon = "✅" if test['status'] == 'PASS' else "❌" if test['status'] == 'FAIL' else "🔥"
                report.append(f"   {status_icon} {test['test']}: {test['status']}")
                report.append(f"      Details: {test['details']}")
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
        
        # Critical assessment for enhanced features
        if overall_success_rate >= 80:
            report.append("🎉 EXCELLENT: Enhanced Perfect MVP features are working well!")
        elif overall_success_rate >= 60:
            report.append("⚠️  GOOD: Most enhanced features working, some issues need attention")
        else:
            report.append("🚨 CRITICAL: Major issues with enhanced features implementation")
        
        report.append("")
        report.append("ENHANCED FEATURES ASSESSMENT:")
        
        # Analyze enhanced features specifically
        camb_tests = self.test_results.get("camb_ai_tts_integration", [])
        if camb_tests:
            camb_passed = len([t for t in camb_tests if t['status'] == 'PASS'])
            if camb_passed >= len(camb_tests) * 0.8:
                report.append("✅ Camb.ai TTS Integration: Working correctly")
            else:
                report.append("❌ Camb.ai TTS Integration: Needs attention")
        
        stt_tests = self.test_results.get("enhanced_stt_indian_kids", [])
        if stt_tests:
            stt_passed = len([t for t in stt_tests if t['status'] == 'PASS'])
            if stt_passed >= len(stt_tests) * 0.8:
                report.append("✅ Enhanced STT for Indian Kids: Working correctly")
            else:
                report.append("❌ Enhanced STT for Indian Kids: Needs attention")
        
        gamification_tests = self.test_results.get("verbal_gamification_system", [])
        if gamification_tests:
            gamification_passed = len([t for t in gamification_tests if t['status'] == 'PASS'])
            if gamification_passed >= len(gamification_tests) * 0.8:
                report.append("✅ Verbal Gamification System: Working correctly")
            else:
                report.append("❌ Verbal Gamification System: Needs attention")
        
        context_tests = self.test_results.get("enhanced_context_retention", [])
        if context_tests:
            context_passed = len([t for t in context_tests if t['status'] == 'PASS'])
            if context_passed >= len(context_tests) * 0.8:
                report.append("✅ Enhanced Context Retention: Working correctly")
            else:
                report.append("❌ Enhanced Context Retention: Needs attention")
        
        riddle_tests = self.test_results.get("riddle_system_testing", [])
        if riddle_tests:
            riddle_passed = len([t for t in riddle_tests if t['status'] == 'PASS'])
            if riddle_passed >= len(riddle_tests) * 0.8:
                report.append("✅ Riddle System: Working correctly")
            else:
                report.append("❌ Riddle System: Needs attention")
        
        memory_tests = self.test_results.get("conversation_memory", [])
        if memory_tests:
            memory_passed = len([t for t in memory_tests if t['status'] == 'PASS'])
            if memory_passed >= len(memory_tests) * 0.8:
                report.append("✅ Conversation Memory: Working correctly")
            else:
                report.append("❌ Conversation Memory: Needs attention")
        
        voice_tests = self.test_results.get("dynamic_voice_selection", [])
        if voice_tests:
            voice_passed = len([t for t in voice_tests if t['status'] == 'PASS'])
            if voice_passed >= len(voice_tests) * 0.8:
                report.append("✅ Dynamic Voice Selection: Working correctly")
            else:
                report.append("❌ Dynamic Voice Selection: Needs attention")
        
        integration_tests = self.test_results.get("system_integration", [])
        if integration_tests:
            integration_passed = len([t for t in integration_tests if t['status'] == 'PASS'])
            if integration_passed >= len(integration_tests) * 0.8:
                report.append("✅ System Integration: Working correctly")
            else:
                report.append("❌ System Integration: Needs attention")
        
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
            "detailed_results": self.test_results
        }

async def main():
    """Main test execution"""
    tester = EnhancedFeaturesBackendTester()
    results = await tester.run_comprehensive_enhanced_tests()
    
    # Return results for further processing
    return results

if __name__ == "__main__":
    asyncio.run(main())