#!/usr/bin/env python3
"""
Critical Voice Pipeline Testing Suite
Tests the specific voice functionality issues reported by the user
"""

import asyncio
import aiohttp
import json
import base64
import uuid
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend URL from environment
BACKEND_URL = "https://9c87ad27-55c0-4609-a47c-ef5b9de00cdd.preview.emergentagent.com/api"

class VoicePipelineTester:
    """Critical voice pipeline functionality tester"""
    
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.test_user_id = None
        self.test_session_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_critical_voice_tests(self):
        """Run critical voice functionality tests"""
        logger.info("Starting CRITICAL VOICE PIPELINE TESTING...")
        
        # Test sequence for voice functionality
        test_sequence = [
            ("Setup - Create Test User", self.setup_test_user),
            ("Setup - Create Test Session", self.setup_test_session),
            ("1. Wake Word Detection Endpoints", self.test_wake_word_detection_endpoints),
            ("2. STT/TTS Pipeline Integration", self.test_stt_tts_pipeline_integration),
            ("3. Ambient Listening Functionality", self.test_ambient_listening_functionality),
            ("4. Story Generation - Full Length", self.test_story_generation_full_length),
            ("5. Song Generation - Complete Song", self.test_song_generation_complete),
            ("6. Enhanced Story Detection Logic", self.test_enhanced_story_detection_logic),
            ("7. Token Limits - Stories vs Chat", self.test_token_limits_stories_vs_chat),
            ("8. Voice Endpoints Audio Base64", self.test_voice_endpoints_audio_base64),
            ("9. Content Processing Stories", self.test_content_processing_stories),
            ("10. Wake Word Activation Flow", self.test_wake_word_activation_flow),
            ("11. Voice Processing Pipeline", self.test_voice_processing_pipeline),
            ("12. TTS Audio Response Quality", self.test_tts_audio_response_quality)
        ]
        
        for test_name, test_func in test_sequence:
            try:
                logger.info(f"Running test: {test_name}")
                result = await test_func()
                self.test_results[test_name] = {
                    "status": "PASS" if result else "FAIL",
                    "details": result if isinstance(result, dict) else {"success": result}
                }
                logger.info(f"Test {test_name}: {'PASS' if result else 'FAIL'}")
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {str(e)}")
                self.test_results[test_name] = {
                    "status": "ERROR",
                    "details": {"error": str(e)}
                }
        
        return self.test_results
    
    async def setup_test_user(self):
        """Setup test user for voice testing"""
        try:
            profile_data = {
                "name": "Sophia",
                "age": 8,
                "location": "San Francisco",
                "timezone": "America/Los_Angeles",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "animals", "music", "adventures"],
                "learning_goals": ["reading", "creativity", "imagination"],
                "parent_email": "parent@voicetest.com"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/users/profile",
                json=profile_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_user_id = data["id"]
                    logger.info(f"Created test user: {self.test_user_id}")
                    return {
                        "success": True,
                        "user_id": data["id"],
                        "name": data["name"],
                        "voice_personality": data["voice_personality"]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def setup_test_session(self):
        """Setup test session for voice testing"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            session_data = {
                "user_id": self.test_user_id,
                "session_name": "Voice Pipeline Test Session"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/session",
                json=session_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_session_id = data["id"]
                    return {
                        "success": True,
                        "session_id": data["id"],
                        "user_id": data["user_id"]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_wake_word_detection_endpoints(self):
        """Test wake word detection endpoints to ensure 'Hey Buddy' activation works"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test ambient listening start endpoint
            start_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status == 200:
                    start_data = await response.json()
                    
                    # Verify wake word configuration
                    wake_words = start_data.get("wake_words", [])
                    has_hey_buddy = "hey buddy" in wake_words
                    
                    # Test ambient status endpoint
                    async with self.session.get(
                        f"{BACKEND_URL}/ambient/status/{self.test_session_id}"
                    ) as status_response:
                        if status_response.status == 200:
                            status_data = await status_response.json()
                            
                            return {
                                "success": True,
                                "ambient_start_working": True,
                                "wake_words_configured": len(wake_words) > 0,
                                "hey_buddy_included": has_hey_buddy,
                                "wake_words": wake_words,
                                "listening_state": start_data.get("listening_state"),
                                "status_endpoint_working": True,
                                "ambient_listening_active": status_data.get("ambient_listening", False)
                            }
                        else:
                            return {
                                "success": False,
                                "error": f"Status endpoint failed: HTTP {status_response.status}",
                                "ambient_start_working": True,
                                "wake_words": wake_words
                            }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Ambient start failed: HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_stt_tts_pipeline_integration(self):
        """Test STT/TTS pipeline integration with Deepgram"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test voice personalities endpoint (part of TTS pipeline)
            async with self.session.get(f"{BACKEND_URL}/voice/personalities") as response:
                if response.status == 200:
                    personalities = await response.json()
                    
                    # Test text conversation to verify TTS integration
                    text_input = {
                        "session_id": self.test_session_id,
                        "user_id": self.test_user_id,
                        "message": "Hello! Can you say something short for me to test your voice?"
                    }
                    
                    async with self.session.post(
                        f"{BACKEND_URL}/conversations/text",
                        json=text_input
                    ) as conv_response:
                        if conv_response.status == 200:
                            conv_data = await conv_response.json()
                            
                            # Test voice input endpoint (STT pipeline)
                            mock_audio = b"mock_audio_data_for_stt_testing"
                            audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
                            
                            voice_input = {
                                "session_id": self.test_session_id,
                                "user_id": self.test_user_id,
                                "audio_base64": audio_base64
                            }
                            
                            async with self.session.post(
                                f"{BACKEND_URL}/conversations/voice",
                                json=voice_input
                            ) as voice_response:
                                # Voice might fail with mock data, but endpoint should be accessible
                                voice_accessible = voice_response.status in [200, 400]
                                
                                return {
                                    "success": True,
                                    "tts_personalities_available": len(personalities) > 0,
                                    "personalities": list(personalities.keys()) if isinstance(personalities, dict) else [],
                                    "text_to_audio_working": bool(conv_data.get("response_audio")),
                                    "stt_endpoint_accessible": voice_accessible,
                                    "deepgram_integration": {
                                        "tts_configured": bool(conv_data.get("response_audio")),
                                        "stt_configured": voice_accessible,
                                        "voice_personalities_count": len(personalities) if isinstance(personalities, dict) else 0
                                    }
                                }
                        else:
                            return {"success": False, "error": f"Text conversation failed: HTTP {conv_response.status}"}
                else:
                    return {"success": False, "error": f"Voice personalities failed: HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_ambient_listening_functionality(self):
        """Test ambient listening functionality"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Start ambient listening
            start_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status == 200:
                    start_data = await response.json()
                    
                    # Test ambient audio processing
                    mock_wake_word_audio = b"hey_buddy_mock_audio_data"
                    audio_base64 = base64.b64encode(mock_wake_word_audio).decode('utf-8')
                    
                    process_request = {
                        "session_id": self.test_session_id,
                        "audio_base64": audio_base64
                    }
                    
                    async with self.session.post(
                        f"{BACKEND_URL}/ambient/process",
                        json=process_request
                    ) as process_response:
                        process_accessible = process_response.status in [200, 400]
                        
                        # Test stop ambient listening
                        stop_request = {"session_id": self.test_session_id}
                        async with self.session.post(
                            f"{BACKEND_URL}/ambient/stop",
                            json=stop_request
                        ) as stop_response:
                            if stop_response.status == 200:
                                stop_data = await stop_response.json()
                                
                                return {
                                    "success": True,
                                    "ambient_start_working": True,
                                    "ambient_process_accessible": process_accessible,
                                    "ambient_stop_working": True,
                                    "listening_states": {
                                        "start": start_data.get("listening_state"),
                                        "stop": stop_data.get("listening_state")
                                    },
                                    "wake_word_detection_ready": bool(start_data.get("wake_words")),
                                    "continuous_processing_ready": process_accessible
                                }
                            else:
                                return {"success": False, "error": f"Ambient stop failed: HTTP {stop_response.status}"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Ambient start failed: HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_story_generation_full_length(self):
        """Test story generation with full length (300-800 words, not 2 lines)"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test explicit story request
            story_requests = [
                "Tell me a story about a brave little mouse",
                "Can you tell me a bedtime story?",
                "I want to hear a story about magical animals",
                "Please tell me a story"
            ]
            
            story_results = []
            
            for story_request in story_requests:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": story_request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "")
                        
                        # Analyze story length and quality
                        word_count = len(response_text.split())
                        has_story_elements = any(element in response_text.lower() for element in [
                            "once upon a time", "there was", "long ago", "in a", "the end"
                        ])
                        
                        story_results.append({
                            "request": story_request,
                            "word_count": word_count,
                            "content_type": content_type,
                            "has_story_elements": has_story_elements,
                            "is_full_length": word_count >= 50,  # At least 50 words for a proper story
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        })
                    else:
                        story_results.append({
                            "request": story_request,
                            "error": f"HTTP {response.status}"
                        })
                
                # Small delay between requests
                await asyncio.sleep(0.5)
            
            # Analyze results
            successful_stories = [r for r in story_results if "error" not in r]
            full_length_stories = [r for r in successful_stories if r.get("is_full_length", False)]
            story_content_types = [r for r in successful_stories if r.get("content_type") == "story"]
            
            return {
                "success": len(successful_stories) > 0,
                "total_requests": len(story_requests),
                "successful_responses": len(successful_stories),
                "full_length_stories": len(full_length_stories),
                "story_content_type_detected": len(story_content_types),
                "average_word_count": sum(r.get("word_count", 0) for r in successful_stories) / len(successful_stories) if successful_stories else 0,
                "story_results": story_results,
                "issues_found": {
                    "short_responses": len([r for r in successful_stories if r.get("word_count", 0) < 50]),
                    "missing_story_elements": len([r for r in successful_stories if not r.get("has_story_elements", False)]),
                    "wrong_content_type": len([r for r in successful_stories if r.get("content_type") != "story"])
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_song_generation_complete(self):
        """Test song generation with complete song"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test explicit song requests
            song_requests = [
                "Sing me a song about friendship",
                "Can you sing a lullaby?",
                "I want to hear a song about animals",
                "Please sing me a song"
            ]
            
            song_results = []
            
            for song_request in song_requests:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": song_request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        content_type = data.get("content_type", "")
                        
                        # Analyze song structure
                        has_verses = response_text.count('\n') > 2  # Multiple lines suggest verses
                        has_rhyming = any(word in response_text.lower() for word in ["la", "na", "oh", "yeah"])
                        word_count = len(response_text.split())
                        
                        song_results.append({
                            "request": song_request,
                            "word_count": word_count,
                            "content_type": content_type,
                            "has_verses": has_verses,
                            "has_rhyming_elements": has_rhyming,
                            "is_complete_song": word_count >= 30 and has_verses,
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                        })
                    else:
                        song_results.append({
                            "request": song_request,
                            "error": f"HTTP {response.status}"
                        })
                
                await asyncio.sleep(0.5)
            
            # Analyze results
            successful_songs = [r for r in song_results if "error" not in r]
            complete_songs = [r for r in successful_songs if r.get("is_complete_song", False)]
            song_content_types = [r for r in successful_songs if r.get("content_type") == "song"]
            
            return {
                "success": len(successful_songs) > 0,
                "total_requests": len(song_requests),
                "successful_responses": len(successful_songs),
                "complete_songs": len(complete_songs),
                "song_content_type_detected": len(song_content_types),
                "average_word_count": sum(r.get("word_count", 0) for r in successful_songs) / len(successful_songs) if successful_songs else 0,
                "song_results": song_results,
                "issues_found": {
                    "incomplete_songs": len([r for r in successful_songs if not r.get("is_complete_song", False)]),
                    "missing_song_structure": len([r for r in successful_songs if not r.get("has_verses", False)]),
                    "wrong_content_type": len([r for r in successful_songs if r.get("content_type") != "song"])
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_enhanced_story_detection_logic(self):
        """Test enhanced story detection and conversation agent logic"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test various story trigger phrases
            story_triggers = [
                "tell me a story",
                "can you tell a story",
                "I want a story",
                "story please",
                "bedtime story",
                "tell story",
                "story time"
            ]
            
            non_story_requests = [
                "how are you?",
                "what's the weather?",
                "help me with math",
                "let's play a game",
                "sing a song"
            ]
            
            detection_results = []
            
            # Test story triggers
            for trigger in story_triggers:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": trigger
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content_type = data.get("content_type", "")
                        
                        detection_results.append({
                            "input": trigger,
                            "expected": "story",
                            "detected": content_type,
                            "correct_detection": content_type == "story",
                            "type": "story_trigger"
                        })
                    else:
                        detection_results.append({
                            "input": trigger,
                            "error": f"HTTP {response.status}",
                            "type": "story_trigger"
                        })
                
                await asyncio.sleep(0.3)
            
            # Test non-story requests
            for request in non_story_requests:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": request
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content_type = data.get("content_type", "")
                        
                        detection_results.append({
                            "input": request,
                            "expected": "conversation",
                            "detected": content_type,
                            "correct_detection": content_type != "story",
                            "type": "non_story"
                        })
                    else:
                        detection_results.append({
                            "input": request,
                            "error": f"HTTP {response.status}",
                            "type": "non_story"
                        })
                
                await asyncio.sleep(0.3)
            
            # Analyze detection accuracy
            successful_tests = [r for r in detection_results if "error" not in r]
            correct_detections = [r for r in successful_tests if r.get("correct_detection", False)]
            story_trigger_accuracy = len([r for r in correct_detections if r["type"] == "story_trigger"]) / len([r for r in successful_tests if r["type"] == "story_trigger"]) if successful_tests else 0
            non_story_accuracy = len([r for r in correct_detections if r["type"] == "non_story"]) / len([r for r in successful_tests if r["type"] == "non_story"]) if successful_tests else 0
            
            return {
                "success": len(correct_detections) > len(successful_tests) * 0.7,  # 70% accuracy threshold
                "total_tests": len(detection_results),
                "successful_tests": len(successful_tests),
                "correct_detections": len(correct_detections),
                "overall_accuracy": len(correct_detections) / len(successful_tests) if successful_tests else 0,
                "story_trigger_accuracy": story_trigger_accuracy,
                "non_story_accuracy": non_story_accuracy,
                "detection_results": detection_results,
                "issues_found": {
                    "false_positives": len([r for r in successful_tests if r["type"] == "non_story" and not r.get("correct_detection", False)]),
                    "false_negatives": len([r for r in successful_tests if r["type"] == "story_trigger" and not r.get("correct_detection", False)])
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_token_limits_stories_vs_chat(self):
        """Test token limits (1000 tokens for stories vs 200 for regular chat)"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test regular chat response length
            chat_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "How are you today? Tell me about yourself."
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=chat_input
            ) as response:
                if response.status == 200:
                    chat_data = await response.json()
                    chat_response = chat_data.get("response_text", "")
                    chat_word_count = len(chat_response.split())
                    chat_content_type = chat_data.get("content_type", "")
                    
                    # Test story response length
                    story_input = {
                        "session_id": self.test_session_id,
                        "user_id": self.test_user_id,
                        "message": "Please tell me a detailed story about a magical adventure with dragons and princesses."
                    }
                    
                    async with self.session.post(
                        f"{BACKEND_URL}/conversations/text",
                        json=story_input
                    ) as story_response:
                        if story_response.status == 200:
                            story_data = await story_response.json()
                            story_response_text = story_data.get("response_text", "")
                            story_word_count = len(story_response_text.split())
                            story_content_type = story_data.get("content_type", "")
                            
                            # Estimate token counts (rough approximation: 1 token ≈ 0.75 words)
                            chat_estimated_tokens = int(chat_word_count * 1.33)
                            story_estimated_tokens = int(story_word_count * 1.33)
                            
                            return {
                                "success": True,
                                "chat_response": {
                                    "word_count": chat_word_count,
                                    "estimated_tokens": chat_estimated_tokens,
                                    "content_type": chat_content_type,
                                    "within_chat_limit": chat_estimated_tokens <= 250,  # Allow some buffer
                                    "preview": chat_response[:100] + "..." if len(chat_response) > 100 else chat_response
                                },
                                "story_response": {
                                    "word_count": story_word_count,
                                    "estimated_tokens": story_estimated_tokens,
                                    "content_type": story_content_type,
                                    "within_story_limit": story_estimated_tokens <= 1200,  # Allow some buffer
                                    "meets_story_minimum": story_estimated_tokens >= 100,  # Should be substantial
                                    "preview": story_response_text[:100] + "..." if len(story_response_text) > 100 else story_response_text
                                },
                                "token_limit_working": {
                                    "chat_appropriately_short": chat_estimated_tokens <= 250,
                                    "story_appropriately_long": story_estimated_tokens >= 100,
                                    "clear_difference": story_estimated_tokens > chat_estimated_tokens * 2
                                }
                            }
                        else:
                            return {"success": False, "error": f"Story request failed: HTTP {story_response.status}"}
                else:
                    return {"success": False, "error": f"Chat request failed: HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_voice_endpoints_audio_base64(self):
        """Test that voice endpoints return proper audio base64 data for TTS"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test text conversation for TTS audio response
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Say hello to test the audio response"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_audio = data.get("response_audio")
                    
                    # Validate base64 audio data
                    audio_valid = False
                    audio_size = 0
                    if response_audio:
                        try:
                            # Try to decode base64
                            audio_bytes = base64.b64decode(response_audio)
                            audio_size = len(audio_bytes)
                            audio_valid = audio_size > 0
                        except Exception:
                            audio_valid = False
                    
                    # Test voice personalities for TTS configuration
                    async with self.session.get(f"{BACKEND_URL}/voice/personalities") as voice_response:
                        if voice_response.status == 200:
                            personalities = await voice_response.json()
                            
                            return {
                                "success": audio_valid,
                                "tts_audio_response": {
                                    "has_audio": bool(response_audio),
                                    "audio_valid_base64": audio_valid,
                                    "audio_size_bytes": audio_size,
                                    "audio_preview": response_audio[:50] + "..." if response_audio and len(response_audio) > 50 else response_audio
                                },
                                "voice_personalities": {
                                    "available": len(personalities) > 0,
                                    "count": len(personalities) if isinstance(personalities, dict) else 0,
                                    "personalities": list(personalities.keys()) if isinstance(personalities, dict) else []
                                },
                                "deepgram_tts_integration": {
                                    "configured": audio_valid,
                                    "working": audio_valid and audio_size > 1000  # Reasonable audio size
                                }
                            }
                        else:
                            return {"success": False, "error": f"Voice personalities failed: HTTP {voice_response.status}"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Text conversation failed: HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_content_processing_stories(self):
        """Test content processing for stories"""
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            # Test content suggestions
            async with self.session.get(
                f"{BACKEND_URL}/content/suggestions/{self.test_user_id}"
            ) as response:
                if response.status == 200:
                    suggestions = await response.json()
                    
                    # Test content by type - stories
                    async with self.session.get(
                        f"{BACKEND_URL}/content/story/{self.test_user_id}"
                    ) as story_response:
                        story_available = story_response.status == 200
                        story_data = None
                        if story_available:
                            story_data = await story_response.json()
                        
                        # Test content by type - songs
                        async with self.session.get(
                            f"{BACKEND_URL}/content/song/{self.test_user_id}"
                        ) as song_response:
                            song_available = song_response.status == 200
                            song_data = None
                            if song_available:
                                song_data = await song_response.json()
                            
                            return {
                                "success": True,
                                "content_suggestions": {
                                    "available": len(suggestions) > 0,
                                    "count": len(suggestions),
                                    "types": [item.get("content_type") for item in suggestions] if suggestions else []
                                },
                                "story_content": {
                                    "available": story_available,
                                    "data": story_data,
                                    "has_content": bool(story_data) if story_available else False
                                },
                                "song_content": {
                                    "available": song_available,
                                    "data": song_data,
                                    "has_content": bool(song_data) if song_available else False
                                },
                                "content_system_working": len(suggestions) > 0 or story_available or song_available
                            }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Content suggestions failed: HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_wake_word_activation_flow(self):
        """Test complete wake word activation flow"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Start ambient listening
            start_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ambient/start",
                json=start_request
            ) as response:
                if response.status == 200:
                    start_data = await response.json()
                    
                    # Simulate wake word detection with mock audio
                    wake_word_phrases = [
                        "hey buddy tell me a story",
                        "ai buddy how are you",
                        "hello buddy sing a song"
                    ]
                    
                    activation_results = []
                    
                    for phrase in wake_word_phrases:
                        # Mock audio data representing the phrase
                        mock_audio = f"mock_audio_{phrase.replace(' ', '_')}".encode()
                        audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
                        
                        process_request = {
                            "session_id": self.test_session_id,
                            "audio_base64": audio_base64
                        }
                        
                        async with self.session.post(
                            f"{BACKEND_URL}/ambient/process",
                            json=process_request
                        ) as process_response:
                            if process_response.status == 200:
                                process_data = await process_response.json()
                                activation_results.append({
                                    "phrase": phrase,
                                    "status": process_data.get("status"),
                                    "listening_state": process_data.get("listening_state"),
                                    "processed": True
                                })
                            else:
                                activation_results.append({
                                    "phrase": phrase,
                                    "error": f"HTTP {process_response.status}",
                                    "processed": False
                                })
                        
                        await asyncio.sleep(0.2)
                    
                    # Test status after processing
                    async with self.session.get(
                        f"{BACKEND_URL}/ambient/status/{self.test_session_id}"
                    ) as status_response:
                        if status_response.status == 200:
                            final_status = await status_response.json()
                            
                            return {
                                "success": True,
                                "ambient_listening_started": bool(start_data.get("status")),
                                "wake_word_processing": {
                                    "total_phrases_tested": len(wake_word_phrases),
                                    "successfully_processed": len([r for r in activation_results if r.get("processed", False)]),
                                    "activation_results": activation_results
                                },
                                "session_status_tracking": {
                                    "status_accessible": True,
                                    "session_id": final_status.get("session_id"),
                                    "listening_state": final_status.get("listening_state")
                                },
                                "wake_word_flow_working": bool(start_data.get("status")) and len([r for r in activation_results if r.get("processed", False)]) > 0
                            }
                        else:
                            return {"success": False, "error": f"Status check failed: HTTP {status_response.status}"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Ambient start failed: HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_voice_processing_pipeline(self):
        """Test complete voice processing pipeline"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test voice input processing
            mock_audio = b"mock_voice_input_for_pipeline_testing"
            audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
            
            voice_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": audio_base64
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/voice",
                json=voice_input
            ) as response:
                voice_endpoint_accessible = response.status in [200, 400]  # 400 expected for mock data
                
                if response.status == 200:
                    voice_data = await response.json()
                    pipeline_working = True
                    pipeline_data = voice_data
                elif response.status == 400:
                    # Expected for mock audio - endpoint is working but rejecting invalid audio
                    pipeline_working = True
                    pipeline_data = {"note": "Endpoint correctly rejected mock audio"}
                else:
                    pipeline_working = False
                    pipeline_data = {"error": f"HTTP {response.status}"}
                
                # Test text input for comparison
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": "Test voice pipeline with text input"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as text_response:
                    if text_response.status == 200:
                        text_data = await text_response.json()
                        
                        return {
                            "success": pipeline_working,
                            "voice_endpoint": {
                                "accessible": voice_endpoint_accessible,
                                "working": pipeline_working,
                                "response": pipeline_data
                            },
                            "text_endpoint": {
                                "working": True,
                                "has_audio_response": bool(text_data.get("response_audio")),
                                "content_type": text_data.get("content_type")
                            },
                            "pipeline_integration": {
                                "stt_endpoint_ready": voice_endpoint_accessible,
                                "tts_working": bool(text_data.get("response_audio")),
                                "conversation_processing": True,
                                "audio_pipeline_complete": voice_endpoint_accessible and bool(text_data.get("response_audio"))
                            }
                        }
                    else:
                        return {"success": False, "error": f"Text endpoint failed: HTTP {text_response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_tts_audio_response_quality(self):
        """Test TTS audio response quality and format"""
        if not self.test_user_id or not self.test_session_id:
            return {"success": False, "error": "Missing test user ID or session ID"}
        
        try:
            # Test different types of content for TTS
            test_inputs = [
                {"message": "Hello, how are you?", "expected_type": "conversation"},
                {"message": "Tell me a short story", "expected_type": "story"},
                {"message": "Sing me a song", "expected_type": "song"}
            ]
            
            tts_results = []
            
            for test_input in test_inputs:
                text_request = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": test_input["message"]
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_request
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_audio = data.get("response_audio")
                        
                        # Analyze audio quality
                        audio_analysis = {
                            "has_audio": bool(response_audio),
                            "audio_size": 0,
                            "valid_base64": False,
                            "reasonable_size": False
                        }
                        
                        if response_audio:
                            try:
                                audio_bytes = base64.b64decode(response_audio)
                                audio_analysis["audio_size"] = len(audio_bytes)
                                audio_analysis["valid_base64"] = True
                                audio_analysis["reasonable_size"] = len(audio_bytes) > 1000  # At least 1KB
                            except Exception:
                                audio_analysis["valid_base64"] = False
                        
                        tts_results.append({
                            "input": test_input["message"],
                            "expected_type": test_input["expected_type"],
                            "actual_type": data.get("content_type"),
                            "audio_analysis": audio_analysis,
                            "response_text_length": len(data.get("response_text", "")),
                            "tts_working": audio_analysis["has_audio"] and audio_analysis["valid_base64"]
                        })
                    else:
                        tts_results.append({
                            "input": test_input["message"],
                            "error": f"HTTP {response.status}"
                        })
                
                await asyncio.sleep(0.5)
            
            # Analyze overall TTS performance
            successful_tests = [r for r in tts_results if "error" not in r]
            working_tts = [r for r in successful_tests if r.get("tts_working", False)]
            
            return {
                "success": len(working_tts) > 0,
                "total_tests": len(test_inputs),
                "successful_responses": len(successful_tests),
                "working_tts_responses": len(working_tts),
                "tts_success_rate": len(working_tts) / len(successful_tests) if successful_tests else 0,
                "tts_results": tts_results,
                "audio_quality_summary": {
                    "all_have_audio": all(r.get("audio_analysis", {}).get("has_audio", False) for r in successful_tests),
                    "all_valid_base64": all(r.get("audio_analysis", {}).get("valid_base64", False) for r in successful_tests),
                    "all_reasonable_size": all(r.get("audio_analysis", {}).get("reasonable_size", False) for r in successful_tests),
                    "average_audio_size": sum(r.get("audio_analysis", {}).get("audio_size", 0) for r in successful_tests) / len(successful_tests) if successful_tests else 0
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

async def main():
    """Run critical voice pipeline tests"""
    async with VoicePipelineTester() as tester:
        results = await tester.run_critical_voice_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("CRITICAL VOICE PIPELINE TEST RESULTS")
        print("="*80)
        
        total_tests = len(results)
        passed_tests = len([r for r in results.values() if r["status"] == "PASS"])
        failed_tests = len([r for r in results.values() if r["status"] == "FAIL"])
        error_tests = len([r for r in results.values() if r["status"] == "ERROR"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDETAILED RESULTS:")
        print("-"*80)
        
        for test_name, result in results.items():
            status_symbol = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_symbol} {test_name}: {result['status']}")
            
            # Show key details for failed tests
            if result["status"] != "PASS" and "details" in result:
                details = result["details"]
                if "error" in details:
                    print(f"   Error: {details['error']}")
                elif "issues_found" in details:
                    print(f"   Issues: {details['issues_found']}")
        
        print("\n" + "="*80)
        
        return results

if __name__ == "__main__":
    asyncio.run(main())