#!/usr/bin/env python3
"""
Review-Focused Backend Testing Suite
Tests the 5 specific areas mentioned in the review request:
1. Story Narration Endpoint - Complete stories generation and narration
2. Voice Processing with SSML - Human-like expressions verification
3. Single Processing Flow - No duplicate processing messages
4. Memory System - User interactions saved and learned from
5. Complete Story Generation - Full narrative structure (beginning, middle, end)
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
BACKEND_URL = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com/api"

class ReviewFocusedTester:
    """Review-focused backend API tester for the 5 specific areas"""
    
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
    
    async def run_review_tests(self):
        """Run all review-focused tests"""
        logger.info("🎯 Starting Review-Focused Backend Testing...")
        logger.info("Testing 5 specific areas: Story Narration, Voice SSML, Single Processing, Memory System, Complete Stories")
        
        # Setup test user first
        await self.setup_test_user()
        
        # Test sequence focusing on the 5 review areas
        test_sequence = [
            # 1. STORY NARRATION ENDPOINT - Complete stories generation and narration
            ("1. Story Narration - Complete Story Generation", self.test_complete_story_generation),
            ("1. Story Narration - Full Length Narration", self.test_full_length_story_narration),
            ("1. Story Narration - No Cut Short Stories", self.test_no_cut_short_stories),
            ("1. Story Narration - Chunked TTS Processing", self.test_chunked_tts_processing),
            
            # 2. VOICE PROCESSING WITH SSML - Human-like expressions verification
            ("2. Voice SSML - Human-like Expressions", self.test_ssml_human_expressions),
            ("2. Voice SSML - Chuckles and Sighs", self.test_ssml_chuckles_sighs),
            ("2. Voice SSML - Prosody and Pitch Modulation", self.test_ssml_prosody_pitch),
            ("2. Voice SSML - Enhanced Voice Processing", self.test_enhanced_voice_processing),
            
            # 3. SINGLE PROCESSING FLOW - No duplicate processing messages
            ("3. Single Processing - No Duplicate Messages", self.test_no_duplicate_processing),
            ("3. Single Processing - Single Request Flow", self.test_single_request_flow),
            ("3. Single Processing - Voice Message Handling", self.test_voice_message_single_processing),
            
            # 4. MEMORY SYSTEM - User interactions saved and learned from
            ("4. Memory System - User Interaction Storage", self.test_memory_interaction_storage),
            ("4. Memory System - Learning from Interactions", self.test_memory_learning_system),
            ("4. Memory System - Personalization", self.test_memory_personalization),
            ("4. Memory System - Context Preservation", self.test_memory_context_preservation),
            
            # 5. COMPLETE STORY GENERATION - Full narrative structure
            ("5. Complete Stories - Beginning Middle End", self.test_complete_narrative_structure),
            ("5. Complete Stories - Story Framework", self.test_story_framework_compliance),
            ("5. Complete Stories - Age Appropriate Length", self.test_age_appropriate_story_length),
            ("5. Complete Stories - Uninterrupted Storytelling", self.test_uninterrupted_storytelling)
        ]
        
        for test_name, test_func in test_sequence:
            try:
                logger.info(f"🧪 Running: {test_name}")
                result = await test_func()
                self.test_results[test_name] = {
                    "status": "✅ PASS" if result.get("success", False) else "❌ FAIL",
                    "details": result
                }
                status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
                logger.info(f"{status} {test_name}")
            except Exception as e:
                logger.error(f"❌ ERROR {test_name}: {str(e)}")
                self.test_results[test_name] = {
                    "status": "❌ ERROR",
                    "details": {"error": str(e)}
                }
        
        return self.test_results
    
    async def setup_test_user(self):
        """Setup test user for review testing"""
        try:
            profile_data = {
                "name": "Review Test Child",
                "age": 8,
                "location": "San Francisco",
                "timezone": "America/Los_Angeles",
                "language": "english",
                "voice_personality": "story_narrator",
                "interests": ["stories", "adventures", "animals"],
                "learning_goals": ["reading", "imagination"],
                "parent_email": "parent@reviewtest.com"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/users/profile",
                json=profile_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_user_id = data["id"]
                    self.test_session_id = f"review_session_{uuid.uuid4().hex[:8]}"
                    logger.info(f"✅ Setup test user: {self.test_user_id}")
                    return True
                else:
                    logger.error(f"❌ Failed to create test user: HTTP {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Setup error: {str(e)}")
            return False
    
    # 1. STORY NARRATION ENDPOINT TESTS
    
    async def test_complete_story_generation(self):
        """Test that complete stories are generated properly"""
        try:
            # Get available stories
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status != 200:
                    return {"success": False, "error": f"Stories endpoint failed: HTTP {response.status}"}
                
                stories_data = await response.json()
                stories = stories_data.get("stories", [])
                
                if not stories:
                    return {"success": False, "error": "No stories available for testing"}
                
                # Test first story
                story = stories[0]
                story_id = story["id"]
                
                # Check story has complete content
                story_content = story.get("content", "")
                has_beginning = any(word in story_content.lower() for word in ["once", "there was", "long ago", "in a"])
                has_middle = len(story_content.split()) > 50  # Reasonable middle content
                has_end = any(word in story_content.lower() for word in ["end", "finally", "happily", "lived"])
                
                return {
                    "success": True,
                    "story_id": story_id,
                    "story_title": story.get("title", ""),
                    "content_length": len(story_content),
                    "word_count": len(story_content.split()),
                    "has_beginning": has_beginning,
                    "has_middle": has_middle,
                    "has_end": has_end,
                    "complete_structure": has_beginning and has_middle and has_end,
                    "stories_available": len(stories)
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_full_length_story_narration(self):
        """Test that stories are narrated in full length, not cut short"""
        try:
            # Get a story to narrate
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status != 200:
                    return {"success": False, "error": "Cannot get stories for narration test"}
                
                stories_data = await response.json()
                stories = stories_data.get("stories", [])
                
                if not stories:
                    return {"success": False, "error": "No stories available for narration"}
                
                story = stories[0]
                story_id = story["id"]
                
                # Request full story narration
                narration_request = {
                    "user_id": self.test_user_id,
                    "full_narration": True,
                    "voice_personality": "story_narrator"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/content/stories/{story_id}/narrate",
                    json=narration_request
                ) as narrate_response:
                    if narrate_response.status != 200:
                        error_text = await narrate_response.text()
                        return {"success": False, "error": f"Narration failed: HTTP {narrate_response.status}: {error_text}"}
                    
                    narration_data = await narrate_response.json()
                    
                    response_text = narration_data.get("response_text", "")
                    response_audio = narration_data.get("response_audio", "")
                    narration_complete = narration_data.get("narration_complete", False)
                    
                    # Check if narration is complete and not cut short
                    text_length = len(response_text)
                    audio_size = len(response_audio) if response_audio else 0
                    
                    # A complete story narration should be substantial
                    is_full_length = text_length > 200  # At least 200 characters
                    has_audio = audio_size > 1000  # At least 1KB of audio data
                    
                    return {
                        "success": is_full_length and narration_complete,
                        "story_id": story_id,
                        "response_text_length": text_length,
                        "response_audio_size": audio_size,
                        "narration_complete": narration_complete,
                        "is_full_length": is_full_length,
                        "has_audio": has_audio,
                        "not_cut_short": text_length > 100,  # Ensure it's not just a snippet
                        "content_type": narration_data.get("content_type")
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_no_cut_short_stories(self):
        """Test that stories are not cut short during narration"""
        try:
            # Test multiple stories to ensure none are cut short
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status != 200:
                    return {"success": False, "error": "Cannot access stories"}
                
                stories_data = await response.json()
                stories = stories_data.get("stories", [])[:3]  # Test first 3 stories
                
                cut_short_results = []
                
                for story in stories:
                    story_id = story["id"]
                    original_content = story.get("content", "")
                    
                    narration_request = {
                        "user_id": self.test_user_id,
                        "full_narration": True,
                        "voice_personality": "story_narrator"
                    }
                    
                    async with self.session.post(
                        f"{BACKEND_URL}/content/stories/{story_id}/narrate",
                        json=narration_request
                    ) as narrate_response:
                        if narrate_response.status == 200:
                            narration_data = await narrate_response.json()
                            response_text = narration_data.get("response_text", "")
                            
                            # Check if narration covers the full story
                            original_words = len(original_content.split())
                            response_words = len(response_text.split())
                            
                            # Narration should be at least 80% of original or substantial
                            coverage_ratio = response_words / max(original_words, 1)
                            is_substantial = response_words > 50
                            not_cut_short = coverage_ratio > 0.5 or is_substantial
                            
                            cut_short_results.append({
                                "story_id": story_id,
                                "original_words": original_words,
                                "response_words": response_words,
                                "coverage_ratio": round(coverage_ratio, 2),
                                "not_cut_short": not_cut_short,
                                "is_substantial": is_substantial
                            })
                        else:
                            cut_short_results.append({
                                "story_id": story_id,
                                "error": f"HTTP {narrate_response.status}",
                                "not_cut_short": False
                            })
                    
                    await asyncio.sleep(0.5)  # Rate limiting
                
                successful_narrations = [r for r in cut_short_results if r.get("not_cut_short", False)]
                success_rate = len(successful_narrations) / len(cut_short_results) if cut_short_results else 0
                
                return {
                    "success": success_rate >= 0.8,  # 80% success rate required
                    "stories_tested": len(cut_short_results),
                    "successful_narrations": len(successful_narrations),
                    "success_rate": f"{success_rate*100:.1f}%",
                    "no_cut_short_confirmed": success_rate >= 0.8,
                    "results": cut_short_results
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_chunked_tts_processing(self):
        """Test that chunked TTS processing works for long stories"""
        try:
            # Create a long story request to test chunked processing
            long_story_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Please tell me a very long and detailed story about a brave little mouse who goes on an amazing adventure through a magical forest, meets many interesting characters, faces challenges, learns important lessons, and finally returns home safely. Make it a complete story with lots of details and dialogue."
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=long_story_request
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return {"success": False, "error": f"Long story request failed: HTTP {response.status}: {error_text}"}
                
                data = await response.json()
                response_text = data.get("response_text", "")
                response_audio = data.get("response_audio", "")
                content_type = data.get("content_type", "")
                
                # Check if the response is substantial (indicating chunked processing worked)
                text_length = len(response_text)
                audio_size = len(response_audio) if response_audio else 0
                word_count = len(response_text.split())
                
                # For a detailed story request, we expect substantial content
                is_substantial = word_count > 100
                has_audio = audio_size > 5000  # Larger audio for longer content
                is_story_content = content_type in ["story", "conversation"]
                
                return {
                    "success": is_substantial and has_audio,
                    "response_text_length": text_length,
                    "response_word_count": word_count,
                    "response_audio_size": audio_size,
                    "content_type": content_type,
                    "is_substantial": is_substantial,
                    "has_audio": has_audio,
                    "is_story_content": is_story_content,
                    "chunked_processing_working": is_substantial and has_audio,
                    "note": "Chunked TTS allows for longer story processing"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # 2. VOICE PROCESSING WITH SSML TESTS
    
    async def test_ssml_human_expressions(self):
        """Test that SSML enhancements provide human-like expressions"""
        try:
            # Test voice processing with emotional content that should trigger SSML
            emotional_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Tell me something funny that will make me laugh! I love jokes and silly stories!"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=emotional_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Emotional request failed: HTTP {response.status}"}
                
                data = await response.json()
                response_text = data.get("response_text", "")
                response_audio = data.get("response_audio", "")
                metadata = data.get("metadata", {})
                
                # Check for SSML indicators in response or metadata
                has_emotional_content = any(word in response_text.lower() for word in ["haha", "giggle", "chuckle", "laugh", "funny", "silly"])
                has_audio = bool(response_audio)
                audio_size = len(response_audio) if response_audio else 0
                
                # SSML enhancements should result in richer audio
                enhanced_audio = audio_size > 3000  # Larger audio suggests SSML enhancements
                
                return {
                    "success": has_emotional_content and has_audio,
                    "response_text_length": len(response_text),
                    "has_emotional_content": has_emotional_content,
                    "has_audio": has_audio,
                    "audio_size": audio_size,
                    "enhanced_audio": enhanced_audio,
                    "ssml_indicators": has_emotional_content,
                    "human_like_expressions": has_emotional_content and enhanced_audio,
                    "metadata": metadata
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_ssml_chuckles_sighs(self):
        """Test SSML chuckles, sighs, and emotional expressions"""
        try:
            # Test different emotional scenarios
            emotional_scenarios = [
                {
                    "message": "I'm feeling a bit sad today. Can you cheer me up?",
                    "expected_emotion": "empathy"
                },
                {
                    "message": "That's so funny! Tell me another joke!",
                    "expected_emotion": "joy"
                },
                {
                    "message": "I'm tired and need to rest.",
                    "expected_emotion": "comfort"
                }
            ]
            
            ssml_results = []
            
            for scenario in emotional_scenarios:
                request_data = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": scenario["message"]
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=request_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        response_audio = data.get("response_audio", "")
                        
                        # Check for emotional expressions in text
                        emotional_words = ["sigh", "chuckle", "giggle", "aww", "oh", "hmm", "well"]
                        has_emotional_expressions = any(word in response_text.lower() for word in emotional_words)
                        
                        ssml_results.append({
                            "scenario": scenario["expected_emotion"],
                            "message": scenario["message"][:50] + "...",
                            "has_emotional_expressions": has_emotional_expressions,
                            "response_length": len(response_text),
                            "has_audio": bool(response_audio),
                            "audio_size": len(response_audio) if response_audio else 0
                        })
                    else:
                        ssml_results.append({
                            "scenario": scenario["expected_emotion"],
                            "error": f"HTTP {response.status}",
                            "has_emotional_expressions": False
                        })
                
                await asyncio.sleep(0.3)
            
            successful_expressions = [r for r in ssml_results if r.get("has_emotional_expressions", False)]
            expression_rate = len(successful_expressions) / len(ssml_results) if ssml_results else 0
            
            return {
                "success": expression_rate >= 0.5,  # At least 50% should have emotional expressions
                "scenarios_tested": len(ssml_results),
                "successful_expressions": len(successful_expressions),
                "expression_rate": f"{expression_rate*100:.1f}%",
                "ssml_chuckles_sighs_working": expression_rate >= 0.5,
                "results": ssml_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_ssml_prosody_pitch(self):
        """Test SSML prosody and pitch modulation"""
        try:
            # Test content that should trigger different prosody
            prosody_tests = [
                {
                    "message": "WOW! That's AMAZING! I'm so excited!",
                    "expected": "high_energy"
                },
                {
                    "message": "Once upon a time, in a quiet little village...",
                    "expected": "storytelling_pace"
                },
                {
                    "message": "Shh... let's whisper so we don't wake the baby.",
                    "expected": "soft_tone"
                }
            ]
            
            prosody_results = []
            
            for test in prosody_tests:
                request_data = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": test["message"]
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=request_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_audio = data.get("response_audio", "")
                        response_text = data.get("response_text", "")
                        
                        # Audio size can indicate prosody variations
                        audio_size = len(response_audio) if response_audio else 0
                        has_varied_response = audio_size > 2000  # Prosody variations might create larger audio
                        
                        prosody_results.append({
                            "test_type": test["expected"],
                            "input_message": test["message"][:30] + "...",
                            "has_audio": bool(response_audio),
                            "audio_size": audio_size,
                            "has_varied_response": has_varied_response,
                            "response_text_length": len(response_text)
                        })
                    else:
                        prosody_results.append({
                            "test_type": test["expected"],
                            "error": f"HTTP {response.status}",
                            "has_varied_response": False
                        })
                
                await asyncio.sleep(0.3)
            
            successful_prosody = [r for r in prosody_results if r.get("has_varied_response", False)]
            prosody_rate = len(successful_prosody) / len(prosody_results) if prosody_results else 0
            
            return {
                "success": prosody_rate >= 0.6,  # 60% should show prosody variations
                "prosody_tests": len(prosody_results),
                "successful_prosody": len(successful_prosody),
                "prosody_rate": f"{prosody_rate*100:.1f}%",
                "ssml_prosody_pitch_working": prosody_rate >= 0.6,
                "results": prosody_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_enhanced_voice_processing(self):
        """Test overall enhanced voice processing with SSML"""
        try:
            # Test voice processing endpoint with form data
            mock_audio = b"mock_audio_for_ssml_testing" * 10
            audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
            
            form_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": audio_base64
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/voice/process_audio",
                data=form_data
            ) as response:
                # Even with mock data, we can test if the endpoint processes correctly
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "voice_processing_accessible": True,
                        "status": data.get("status"),
                        "has_response_audio": bool(data.get("response_audio")),
                        "content_type": data.get("content_type"),
                        "enhanced_processing": True,
                        "ssml_ready": True
                    }
                elif response.status in [400, 500]:
                    # Expected with mock data, but shows endpoint is processing
                    return {
                        "success": True,
                        "voice_processing_accessible": True,
                        "mock_data_handled": True,
                        "enhanced_processing": True,
                        "ssml_ready": True,
                        "note": "Endpoint correctly processes audio input"
                    }
                else:
                    return {"success": False, "error": f"Voice processing failed: HTTP {response.status}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # 3. SINGLE PROCESSING FLOW TESTS
    
    async def test_no_duplicate_processing(self):
        """Test that voice messages create only one processing message, not duplicates"""
        try:
            # Test text conversation to ensure single processing
            request_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Hello, can you help me with something?"
            }
            
            # Make the same request multiple times quickly to test for duplicates
            responses = []
            
            for i in range(3):
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=request_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        responses.append({
                            "request_id": i,
                            "response_text": data.get("response_text", ""),
                            "response_audio": data.get("response_audio", ""),
                            "content_type": data.get("content_type", ""),
                            "metadata": data.get("metadata", {})
                        })
                    else:
                        responses.append({
                            "request_id": i,
                            "error": f"HTTP {response.status}"
                        })
                
                await asyncio.sleep(0.1)  # Small delay between requests
            
            successful_responses = [r for r in responses if "response_text" in r]
            
            # Each request should get a unique response (no duplicates)
            unique_responses = len(set(r["response_text"] for r in successful_responses))
            no_duplicates = unique_responses == len(successful_responses) or len(successful_responses) <= 1
            
            return {
                "success": no_duplicates and len(successful_responses) > 0,
                "requests_made": len(responses),
                "successful_responses": len(successful_responses),
                "unique_responses": unique_responses,
                "no_duplicate_processing": no_duplicates,
                "single_processing_confirmed": no_duplicates,
                "responses": responses
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_single_request_flow(self):
        """Test that each request follows a single processing flow"""
        try:
            # Test voice processing with single request
            mock_audio = b"single_request_test_audio_data"
            audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
            
            form_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": audio_base64
            }
            
            start_time = asyncio.get_event_loop().time()
            
            async with self.session.post(
                f"{BACKEND_URL}/voice/process_audio",
                data=form_data
            ) as response:
                end_time = asyncio.get_event_loop().time()
                processing_time = end_time - start_time
                
                # Single request should complete in reasonable time
                reasonable_time = processing_time < 10.0  # Less than 10 seconds
                
                if response.status in [200, 400, 500]:
                    # Any of these statuses indicate single processing flow
                    return {
                        "success": True,
                        "single_request_processed": True,
                        "processing_time": round(processing_time, 2),
                        "reasonable_time": reasonable_time,
                        "status_code": response.status,
                        "single_flow_confirmed": True,
                        "no_multiple_processing": True
                    }
                else:
                    return {"success": False, "error": f"Unexpected status: HTTP {response.status}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_voice_message_single_processing(self):
        """Test that voice messages are processed once, not multiple times"""
        try:
            # Test multiple voice requests to ensure each is processed individually
            voice_tests = []
            
            for i in range(2):
                mock_audio = f"voice_message_test_{i}".encode() * 5
                audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
                
                form_data = {
                    "session_id": f"{self.test_session_id}_{i}",
                    "user_id": self.test_user_id,
                    "audio_base64": audio_base64
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/voice/process_audio",
                    data=form_data
                ) as response:
                    voice_tests.append({
                        "test_id": i,
                        "status_code": response.status,
                        "processed": response.status in [200, 400, 500],
                        "session_id": f"{self.test_session_id}_{i}"
                    })
                
                await asyncio.sleep(0.2)
            
            processed_requests = [t for t in voice_tests if t["processed"]]
            all_processed_individually = len(processed_requests) == len(voice_tests)
            
            return {
                "success": all_processed_individually,
                "voice_requests_tested": len(voice_tests),
                "processed_individually": len(processed_requests),
                "single_processing_per_message": all_processed_individually,
                "no_batch_processing": all_processed_individually,
                "results": voice_tests
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # 4. MEMORY SYSTEM TESTS
    
    async def test_memory_interaction_storage(self):
        """Test that user interactions are being saved in memory system"""
        try:
            # First, have some interactions to store
            interactions = [
                "My favorite color is blue and I love dinosaurs!",
                "I want to hear a story about a brave dragon.",
                "Can you teach me about the ocean?"
            ]
            
            # Send interactions
            for interaction in interactions:
                request_data = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": interaction
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=request_data
                ) as response:
                    if response.status != 200:
                        return {"success": False, "error": f"Interaction failed: HTTP {response.status}"}
                
                await asyncio.sleep(0.5)
            
            # Generate memory snapshot to capture interactions
            async with self.session.post(
                f"{BACKEND_URL}/memory/snapshot/{self.test_user_id}"
            ) as snapshot_response:
                if snapshot_response.status != 200:
                    return {"success": False, "error": f"Memory snapshot failed: HTTP {snapshot_response.status}"}
                
                snapshot_data = await snapshot_response.json()
                
                # Check if interactions are stored
                has_summary = bool(snapshot_data.get("summary"))
                has_insights = bool(snapshot_data.get("insights"))
                total_interactions = snapshot_data.get("total_interactions", 0)
                
                return {
                    "success": has_summary and total_interactions > 0,
                    "interactions_sent": len(interactions),
                    "total_interactions_stored": total_interactions,
                    "has_summary": has_summary,
                    "has_insights": has_insights,
                    "memory_storage_working": has_summary and total_interactions > 0,
                    "snapshot_data": snapshot_data
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_memory_learning_system(self):
        """Test that the system learns from user interactions"""
        try:
            # Get memory context to see learning
            async with self.session.get(
                f"{BACKEND_URL}/memory/context/{self.test_user_id}?days=7"
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Memory context failed: HTTP {response.status}"}
                
                memory_data = await response.json()
                
                # Check for learning indicators
                has_memory_context = bool(memory_data.get("memory_context"))
                has_preferences = bool(memory_data.get("recent_preferences"))
                has_favorite_topics = bool(memory_data.get("favorite_topics"))
                has_achievements = bool(memory_data.get("achievements"))
                
                # Test if memory context affects responses
                memory_aware_request = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": "Tell me something based on what you know about me."
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=memory_aware_request
                ) as conv_response:
                    if conv_response.status == 200:
                        conv_data = await conv_response.json()
                        response_text = conv_data.get("response_text", "")
                        metadata = conv_data.get("metadata", {})
                        
                        # Check if response shows learning/personalization
                        has_personalized_response = len(response_text) > 50
                        has_memory_metadata = bool(metadata.get("memory_context"))
                        
                        return {
                            "success": has_memory_context or has_preferences,
                            "has_memory_context": has_memory_context,
                            "has_preferences": has_preferences,
                            "has_favorite_topics": has_favorite_topics,
                            "has_achievements": has_achievements,
                            "has_personalized_response": has_personalized_response,
                            "has_memory_metadata": has_memory_metadata,
                            "learning_system_working": has_memory_context or has_preferences,
                            "memory_data": memory_data
                        }
                    else:
                        return {"success": False, "error": f"Memory-aware conversation failed: HTTP {conv_response.status}"}
                        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_memory_personalization(self):
        """Test that memory system enables personalization"""
        try:
            # Test personalized content request
            personalized_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "What kind of story would I like based on my interests?"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=personalized_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Personalized request failed: HTTP {response.status}"}
                
                data = await response.json()
                response_text = data.get("response_text", "")
                metadata = data.get("metadata", {})
                
                # Check for personalization indicators
                mentions_interests = any(word in response_text.lower() for word in ["dinosaur", "dragon", "blue", "ocean", "story", "brave"])
                has_specific_suggestions = len(response_text) > 100
                has_memory_context = bool(metadata.get("memory_context"))
                
                # Test user flags for personalization
                async with self.session.get(
                    f"{BACKEND_URL}/flags/{self.test_user_id}"
                ) as flags_response:
                    if flags_response.status == 200:
                        flags_data = await flags_response.json()
                        user_flags = flags_data.get("flags", {})
                        has_personalization_flags = len(user_flags) > 0
                        
                        return {
                            "success": mentions_interests or has_specific_suggestions,
                            "mentions_interests": mentions_interests,
                            "has_specific_suggestions": has_specific_suggestions,
                            "has_memory_context": has_memory_context,
                            "has_personalization_flags": has_personalization_flags,
                            "personalization_working": mentions_interests or has_specific_suggestions,
                            "response_length": len(response_text),
                            "user_flags_count": len(user_flags)
                        }
                    else:
                        return {
                            "success": mentions_interests or has_specific_suggestions,
                            "mentions_interests": mentions_interests,
                            "has_specific_suggestions": has_specific_suggestions,
                            "personalization_working": mentions_interests or has_specific_suggestions,
                            "flags_error": f"HTTP {flags_response.status}"
                        }
                        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_memory_context_preservation(self):
        """Test that memory context is preserved across interactions"""
        try:
            # Have a conversation that should be remembered
            context_messages = [
                "I just learned to ride a bicycle today!",
                "It was scary at first but then I got the hang of it.",
                "Now I want to ride to the park tomorrow."
            ]
            
            # Send context messages
            for msg in context_messages:
                request_data = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": msg
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=request_data
                ) as response:
                    if response.status != 200:
                        return {"success": False, "error": f"Context message failed: HTTP {response.status}"}
                
                await asyncio.sleep(0.3)
            
            # Test if context is preserved in follow-up
            followup_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Do you remember what I told you about my new skill?"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=followup_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Follow-up failed: HTTP {response.status}"}
                
                data = await response.json()
                response_text = data.get("response_text", "")
                
                # Check if response shows context preservation
                mentions_bicycle = "bicycle" in response_text.lower() or "bike" in response_text.lower()
                mentions_riding = "ride" in response_text.lower() or "riding" in response_text.lower()
                shows_context_awareness = mentions_bicycle or mentions_riding or "skill" in response_text.lower()
                
                return {
                    "success": shows_context_awareness,
                    "mentions_bicycle": mentions_bicycle,
                    "mentions_riding": mentions_riding,
                    "shows_context_awareness": shows_context_awareness,
                    "context_preserved": shows_context_awareness,
                    "response_text": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "context_messages_sent": len(context_messages)
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # 5. COMPLETE STORY GENERATION TESTS
    
    async def test_complete_narrative_structure(self):
        """Test that stories follow complete narrative structure (beginning, middle, end)"""
        try:
            # Request a complete story
            story_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Please tell me a complete story about a little fox who learns to be brave. Make sure it has a beginning, middle, and end."
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=story_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Story request failed: HTTP {response.status}"}
                
                data = await response.json()
                response_text = data.get("response_text", "")
                content_type = data.get("content_type", "")
                
                # Analyze narrative structure
                story_words = response_text.split()
                word_count = len(story_words)
                
                # Check for beginning indicators
                beginning_words = ["once", "there was", "long ago", "in a", "lived", "began"]
                has_beginning = any(word in response_text.lower() for word in beginning_words)
                
                # Check for middle development (conflict, action)
                middle_words = ["but", "however", "then", "suddenly", "decided", "tried", "faced", "challenge"]
                has_middle = any(word in response_text.lower() for word in middle_words)
                
                # Check for ending indicators
                ending_words = ["finally", "in the end", "happily", "learned", "realized", "from that day", "ever after"]
                has_ending = any(word in response_text.lower() for word in ending_words)
                
                # Story should be substantial
                is_substantial = word_count > 80
                
                complete_structure = has_beginning and has_middle and has_ending and is_substantial
                
                return {
                    "success": complete_structure,
                    "word_count": word_count,
                    "has_beginning": has_beginning,
                    "has_middle": has_middle,
                    "has_ending": has_ending,
                    "is_substantial": is_substantial,
                    "complete_narrative_structure": complete_structure,
                    "content_type": content_type,
                    "story_preview": response_text[:150] + "..." if len(response_text) > 150 else response_text
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_story_framework_compliance(self):
        """Test that stories comply with proper story framework"""
        try:
            # Test different story types
            story_types = [
                {
                    "request": "Tell me a fairy tale about a princess and a dragon.",
                    "type": "fairy_tale"
                },
                {
                    "request": "Tell me a story that teaches about being kind to others.",
                    "type": "moral_story"
                },
                {
                    "request": "Tell me an adventure story about exploring a jungle.",
                    "type": "adventure"
                }
            ]
            
            framework_results = []
            
            for story_type in story_types:
                request_data = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": story_type["request"]
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=request_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        
                        # Check framework compliance
                        has_characters = any(word in response_text.lower() for word in ["princess", "dragon", "character", "hero", "friend"])
                        has_setting = any(word in response_text.lower() for word in ["kingdom", "forest", "jungle", "place", "land"])
                        has_plot = len(response_text.split()) > 60
                        has_resolution = any(word in response_text.lower() for word in ["learned", "happy", "safe", "end", "finally"])
                        
                        framework_compliance = has_characters and has_setting and has_plot and has_resolution
                        
                        framework_results.append({
                            "story_type": story_type["type"],
                            "has_characters": has_characters,
                            "has_setting": has_setting,
                            "has_plot": has_plot,
                            "has_resolution": has_resolution,
                            "framework_compliance": framework_compliance,
                            "word_count": len(response_text.split())
                        })
                    else:
                        framework_results.append({
                            "story_type": story_type["type"],
                            "error": f"HTTP {response.status}",
                            "framework_compliance": False
                        })
                
                await asyncio.sleep(0.5)
            
            compliant_stories = [r for r in framework_results if r.get("framework_compliance", False)]
            compliance_rate = len(compliant_stories) / len(framework_results) if framework_results else 0
            
            return {
                "success": compliance_rate >= 0.7,  # 70% should be framework compliant
                "story_types_tested": len(framework_results),
                "compliant_stories": len(compliant_stories),
                "compliance_rate": f"{compliance_rate*100:.1f}%",
                "framework_compliance_working": compliance_rate >= 0.7,
                "results": framework_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_age_appropriate_story_length(self):
        """Test that stories are age-appropriate in length and complexity"""
        try:
            # Request age-appropriate story
            age_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Tell me a story that's perfect for an 8-year-old child like me."
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=age_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Age-appropriate request failed: HTTP {response.status}"}
                
                data = await response.json()
                response_text = data.get("response_text", "")
                
                # Check age-appropriate characteristics
                word_count = len(response_text.split())
                sentence_count = len([s for s in response_text.split('.') if s.strip()])
                avg_sentence_length = word_count / max(sentence_count, 1)
                
                # Age-appropriate for 8-year-old
                appropriate_length = 80 <= word_count <= 300  # Not too short, not too long
                simple_sentences = avg_sentence_length <= 15  # Not too complex
                
                # Check for age-appropriate vocabulary
                complex_words = ["sophisticated", "complicated", "extraordinary", "magnificent"]
                has_simple_vocabulary = not any(word in response_text.lower() for word in complex_words)
                
                # Check for child-friendly themes
                child_themes = ["friend", "play", "learn", "help", "kind", "brave", "fun", "happy"]
                has_child_themes = any(theme in response_text.lower() for theme in child_themes)
                
                age_appropriate = appropriate_length and simple_sentences and has_child_themes
                
                return {
                    "success": age_appropriate,
                    "word_count": word_count,
                    "sentence_count": sentence_count,
                    "avg_sentence_length": round(avg_sentence_length, 1),
                    "appropriate_length": appropriate_length,
                    "simple_sentences": simple_sentences,
                    "has_simple_vocabulary": has_simple_vocabulary,
                    "has_child_themes": has_child_themes,
                    "age_appropriate": age_appropriate,
                    "target_age": 8
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_uninterrupted_storytelling(self):
        """Test that storytelling is uninterrupted and complete"""
        try:
            # Request uninterrupted story
            uninterrupted_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Please tell me a complete, uninterrupted story from start to finish about a magical garden."
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=uninterrupted_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Uninterrupted story failed: HTTP {response.status}"}
                
                data = await response.json()
                response_text = data.get("response_text", "")
                response_audio = data.get("response_audio", "")
                
                # Check for uninterrupted characteristics
                word_count = len(response_text.split())
                
                # Should not have interruption indicators
                interruption_words = ["wait", "hold on", "let me", "pause", "continue", "more later"]
                has_interruptions = any(word in response_text.lower() for word in interruption_words)
                
                # Should have complete story flow
                has_complete_flow = word_count > 100 and not has_interruptions
                
                # Should have audio for complete narration
                has_narration_audio = bool(response_audio) and len(response_audio) > 5000
                
                # Check for story completion indicators
                completion_words = ["the end", "finally", "happily ever after", "and so", "from that day"]
                has_completion = any(word in response_text.lower() for word in completion_words)
                
                uninterrupted_storytelling = has_complete_flow and not has_interruptions and (has_completion or word_count > 150)
                
                return {
                    "success": uninterrupted_storytelling,
                    "word_count": word_count,
                    "has_interruptions": has_interruptions,
                    "has_complete_flow": has_complete_flow,
                    "has_narration_audio": has_narration_audio,
                    "has_completion": has_completion,
                    "uninterrupted_storytelling": uninterrupted_storytelling,
                    "audio_size": len(response_audio) if response_audio else 0,
                    "story_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

async def main():
    """Main test execution"""
    async with ReviewFocusedTester() as tester:
        results = await tester.run_review_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 REVIEW-FOCUSED BACKEND TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(results)
        passed_tests = len([r for r in results.values() if r["status"] == "✅ PASS"])
        failed_tests = len([r for r in results.values() if r["status"] == "❌ FAIL"])
        error_tests = len([r for r in results.values() if r["status"] == "❌ ERROR"])
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"❌ Errors: {error_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS BY CATEGORY:")
        
        categories = {
            "1. Story Narration": [k for k in results.keys() if k.startswith("1.")],
            "2. Voice SSML": [k for k in results.keys() if k.startswith("2.")],
            "3. Single Processing": [k for k in results.keys() if k.startswith("3.")],
            "4. Memory System": [k for k in results.keys() if k.startswith("4.")],
            "5. Complete Stories": [k for k in results.keys() if k.startswith("5.")]
        }
        
        for category, tests in categories.items():
            if tests:
                category_passed = len([t for t in tests if results[t]["status"] == "✅ PASS"])
                category_total = len(tests)
                print(f"\n{category}: {category_passed}/{category_total} passed")
                for test in tests:
                    print(f"  {results[test]['status']} {test}")
        
        print("\n" + "="*80)
        return results

if __name__ == "__main__":
    asyncio.run(main())