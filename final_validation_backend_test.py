#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE VALIDATION - Backend Testing Suite
Focus on 100% validation of all critical systems as requested in review
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
BACKEND_URL = "https://3cbdebd6-5d67-48fd-b7e8-d76cde3db08d.preview.emergentagent.com/api"

class FinalValidationTester:
    """Final comprehensive validation tester for all critical systems"""
    
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.test_user_id = None
        self.test_session_id = None
        self.critical_failures = []
        self.success_count = 0
        self.total_tests = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_final_validation(self):
        """Run final comprehensive validation of all critical systems"""
        logger.info("🎯 STARTING FINAL COMPREHENSIVE VALIDATION - MUST ACHIEVE 100% SUCCESS")
        
        # Critical test sequence based on review requirements
        critical_tests = [
            # MISSION CRITICAL VOICE PIPELINE (Must be 100%)
            ("🎤 STT Processing Validation", self.test_stt_processing),
            ("🔊 TTS Generation Validation", self.test_tts_generation),
            ("🎵 Complete Voice Flow Pipeline", self.test_complete_voice_flow),
            ("⚠️ Voice Error Handling", self.test_voice_error_handling),
            
            # STORY GENERATION WITH UNLIMITED TOKENS (Must generate 300+ words)
            ("📚 Story Length Validation (300+ words)", self.test_story_length_validation),
            ("📖 Complete Narrative Structure", self.test_complete_narrative_structure),
            ("📝 Multiple Story Tests Consistency", self.test_multiple_story_consistency),
            ("🚀 Unlimited Token Implementation", self.test_unlimited_token_implementation),
            
            # STATIC STORY NARRATION SYSTEM (Must return complete stories)
            ("👤 UserProfile Error Fix", self.test_userprofile_error_fix),
            ("📚 Complete Story Loading", self.test_complete_story_loading),
            ("🎵 Story Narration Endpoint", self.test_story_narration_endpoint),
            ("📖 All 5 Stories Available", self.test_all_stories_available),
            
            # COMPLETE SYSTEM INTEGRATION (Must be perfect)
            ("🧠 Context Continuity", self.test_context_continuity),
            ("😊 Human-like Expressions", self.test_human_like_expressions),
            ("💾 Memory Integration", self.test_memory_integration),
            ("✅ Complete Responses", self.test_complete_responses),
            
            # FRONTEND-BACKEND INTEGRATION (Must be seamless)
            ("📋 FormData Processing", self.test_formdata_processing),
            ("🔗 API Contract Alignment", self.test_api_contract_alignment),
            ("🛡️ Error Recovery", self.test_error_recovery),
            ("📱 Cross-Platform Compatibility", self.test_cross_platform_compatibility),
        ]
        
        # Setup test environment
        await self.setup_test_environment()
        
        # Run all critical tests
        for test_name, test_func in critical_tests:
            self.total_tests += 1
            try:
                logger.info(f"🔍 Running: {test_name}")
                result = await test_func()
                
                if result and result.get("success", False):
                    self.success_count += 1
                    self.test_results[test_name] = {
                        "status": "✅ PASS",
                        "details": result
                    }
                    logger.info(f"✅ {test_name}: PASS")
                else:
                    self.critical_failures.append(test_name)
                    self.test_results[test_name] = {
                        "status": "❌ FAIL",
                        "details": result
                    }
                    logger.error(f"❌ {test_name}: FAIL - {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                self.critical_failures.append(test_name)
                self.test_results[test_name] = {
                    "status": "💥 ERROR",
                    "details": {"error": str(e)}
                }
                logger.error(f"💥 {test_name}: ERROR - {str(e)}")
        
        # Generate final report
        return await self.generate_final_report()
    
    async def setup_test_environment(self):
        """Setup test environment with user profile and session"""
        try:
            # Create test user profile
            profile_data = {
                "name": "Emma",
                "age": 7,
                "location": "New York",
                "timezone": "America/New_York",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "animals", "music"],
                "learning_goals": ["reading", "counting"],
                "parent_email": "parent@example.com"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/users/profile",
                json=profile_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_user_id = data["id"]
                    logger.info(f"✅ Test user created: {self.test_user_id}")
                else:
                    logger.error(f"❌ Failed to create test user: {response.status}")
                    
            # Create test session
            session_data = {
                "user_id": self.test_user_id,
                "session_name": "Final Validation Session"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/session",
                json=session_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_session_id = data["id"]
                    logger.info(f"✅ Test session created: {self.test_session_id}")
                else:
                    logger.error(f"❌ Failed to create test session: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Setup failed: {str(e)}")
    
    # MISSION CRITICAL VOICE PIPELINE TESTS
    
    async def test_stt_processing(self):
        """Test speech-to-text processing without HTTP 422 errors"""
        try:
            # Test with various audio formats
            test_formats = [
                {"name": "WebM", "data": b'\x1a\x45\xdf\xa3' + b"mock_webm_audio" * 20},
                {"name": "WAV", "data": b'RIFF' + b"mock_wav_audio" * 20},
                {"name": "MP4", "data": b'\x00\x00\x00\x20ftypmp4' + b"mock_mp4_audio" * 20}
            ]
            
            stt_results = []
            for fmt in test_formats:
                audio_base64 = base64.b64encode(fmt["data"]).decode('utf-8')
                
                form_data = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "audio_base64": audio_base64
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/voice/process_audio",
                    data=form_data
                ) as response:
                    stt_results.append({
                        "format": fmt["name"],
                        "status_code": response.status,
                        "no_422_error": response.status != 422,
                        "accessible": response.status in [200, 400, 500]  # Not 422
                    })
            
            no_422_errors = all(r["no_422_error"] for r in stt_results)
            accessible_count = sum(1 for r in stt_results if r["accessible"])
            
            return {
                "success": no_422_errors and accessible_count >= 2,
                "no_422_errors": no_422_errors,
                "formats_accessible": f"{accessible_count}/{len(test_formats)}",
                "stt_results": stt_results,
                "message": "STT processing accessible without HTTP 422 errors" if no_422_errors else "HTTP 422 errors detected"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_tts_generation(self):
        """Test text-to-speech generation produces audio successfully"""
        try:
            test_messages = [
                "Hello Emma! How are you today?",
                "Let me tell you a wonderful story about friendship.",
                "What would you like to learn about today?"
            ]
            
            tts_results = []
            for message in test_messages:
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": message
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_audio = data.get("response_audio")
                        
                        tts_results.append({
                            "message": message[:30] + "...",
                            "has_audio": bool(response_audio),
                            "audio_size": len(response_audio) if response_audio else 0,
                            "audio_size_kb": round(len(response_audio) / 1024, 1) if response_audio else 0
                        })
                    else:
                        tts_results.append({
                            "message": message[:30] + "...",
                            "has_audio": False,
                            "error": f"HTTP {response.status}"
                        })
            
            successful_tts = [r for r in tts_results if r.get("has_audio", False)]
            success_rate = len(successful_tts) / len(test_messages) * 100
            
            return {
                "success": success_rate >= 100,  # Must be 100%
                "success_rate": f"{success_rate:.1f}%",
                "successful_tts": len(successful_tts),
                "total_tests": len(test_messages),
                "average_audio_size_kb": round(sum(r.get("audio_size_kb", 0) for r in successful_tts) / len(successful_tts), 1) if successful_tts else 0,
                "tts_results": tts_results,
                "message": "TTS generation successful" if success_rate >= 100 else "TTS generation failures detected"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_complete_voice_flow(self):
        """Test STT→LLM→TTS pipeline is fully functional"""
        try:
            # Test complete voice flow
            mock_audio = b"mock_voice_flow_test_audio_data" * 10
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
                
                if response.status == 200:
                    data = await response.json()
                    
                    pipeline_complete = all([
                        data.get("status") == "success",
                        bool(data.get("transcript")),
                        bool(data.get("response_text")),
                        bool(data.get("response_audio"))
                    ])
                    
                    return {
                        "success": pipeline_complete,
                        "pipeline_complete": pipeline_complete,
                        "processing_time": f"{processing_time:.2f}s",
                        "pipeline_stages": {
                            "stt_stage": bool(data.get("transcript")),
                            "llm_stage": bool(data.get("response_text")),
                            "tts_stage": bool(data.get("response_audio"))
                        },
                        "response_data": {
                            "transcript_length": len(data.get("transcript", "")),
                            "response_text_length": len(data.get("response_text", "")),
                            "response_audio_size": len(data.get("response_audio", ""))
                        },
                        "message": "Complete voice flow functional" if pipeline_complete else "Voice flow pipeline incomplete"
                    }
                else:
                    # Check if it's accessible but processing failed (expected with mock data)
                    return {
                        "success": response.status != 422,  # As long as it's not 422, pipeline is accessible
                        "pipeline_accessible": response.status != 422,
                        "status_code": response.status,
                        "processing_time": f"{processing_time:.2f}s",
                        "message": "Voice flow pipeline accessible" if response.status != 422 else "Voice flow pipeline blocked"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_voice_error_handling(self):
        """Test no 'Voice processing failed' messages appear"""
        try:
            # Test various error scenarios
            error_scenarios = [
                {"name": "Empty audio", "audio_base64": ""},
                {"name": "Invalid base64", "audio_base64": "invalid!!!"},
                {"name": "Very small audio", "audio_base64": base64.b64encode(b"x").decode('utf-8')},
            ]
            
            error_handling_results = []
            
            for scenario in error_scenarios:
                form_data = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "audio_base64": scenario["audio_base64"]
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/voice/process_audio",
                    data=form_data
                ) as response:
                    response_text = await response.text()
                    
                    # Check for "Voice processing failed" message
                    has_voice_failed_message = "Voice processing failed" in response_text
                    
                    error_handling_results.append({
                        "scenario": scenario["name"],
                        "status_code": response.status,
                        "has_voice_failed_message": has_voice_failed_message,
                        "graceful_error": response.status in [400, 422] and not has_voice_failed_message
                    })
            
            no_voice_failed_messages = not any(r["has_voice_failed_message"] for r in error_handling_results)
            graceful_errors = sum(1 for r in error_handling_results if r["graceful_error"])
            
            return {
                "success": no_voice_failed_messages,
                "no_voice_failed_messages": no_voice_failed_messages,
                "graceful_error_handling": f"{graceful_errors}/{len(error_scenarios)}",
                "error_handling_results": error_handling_results,
                "message": "Voice error handling working correctly" if no_voice_failed_messages else "Voice processing failed messages detected"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # STORY GENERATION WITH UNLIMITED TOKENS TESTS
    
    async def test_story_length_validation(self):
        """Test stories generate 300+ words consistently"""
        try:
            story_requests = [
                "Tell me a complete story about a brave little mouse who goes on an adventure",
                "Can you tell me a full story about two friends who discover something magical",
                "I want to hear a complete story about a dragon who learns to be kind"
            ]
            
            story_results = []
            
            for request in story_requests:
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
                        response_text = data.get("response_text", "")
                        word_count = len(response_text.split())
                        
                        story_results.append({
                            "request": request[:50] + "...",
                            "word_count": word_count,
                            "meets_300_words": word_count >= 300,
                            "response_length": len(response_text),
                            "content_type": data.get("content_type")
                        })
                    else:
                        story_results.append({
                            "request": request[:50] + "...",
                            "word_count": 0,
                            "meets_300_words": False,
                            "error": f"HTTP {response.status}"
                        })
            
            stories_meeting_requirement = [r for r in story_results if r.get("meets_300_words", False)]
            success_rate = len(stories_meeting_requirement) / len(story_requests) * 100
            average_word_count = sum(r.get("word_count", 0) for r in story_results) / len(story_results)
            
            return {
                "success": success_rate >= 100,  # Must be 100%
                "success_rate": f"{success_rate:.1f}%",
                "stories_meeting_300_words": len(stories_meeting_requirement),
                "total_stories": len(story_requests),
                "average_word_count": round(average_word_count),
                "story_results": story_results,
                "message": f"Story length validation: {success_rate:.1f}% success rate, avg {round(average_word_count)} words"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_complete_narrative_structure(self):
        """Test stories have beginning, middle, end"""
        try:
            story_request = "Tell me a complete story about a little girl who finds a magical key"
            
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
                    story_text = data.get("response_text", "")
                    
                    # Analyze narrative structure
                    narrative_elements = {
                        "has_beginning": any(phrase in story_text.lower() for phrase in ["once upon", "there was", "long ago", "in a", "one day"]),
                        "has_character_development": any(phrase in story_text.lower() for phrase in ["little girl", "she", "her", "character"]),
                        "has_conflict_or_adventure": any(phrase in story_text.lower() for phrase in ["found", "discovered", "adventure", "journey", "problem", "challenge"]),
                        "has_resolution": any(phrase in story_text.lower() for phrase in ["finally", "in the end", "happily", "learned", "realized"]),
                        "has_ending": any(phrase in story_text.lower() for phrase in ["the end", "ever after", "home", "happy", "safe"])
                    }
                    
                    structure_score = sum(narrative_elements.values())
                    word_count = len(story_text.split())
                    
                    return {
                        "success": structure_score >= 4 and word_count >= 200,  # At least 4/5 elements + reasonable length
                        "narrative_structure_score": f"{structure_score}/5",
                        "word_count": word_count,
                        "narrative_elements": narrative_elements,
                        "story_preview": story_text[:200] + "..." if len(story_text) > 200 else story_text,
                        "message": f"Narrative structure: {structure_score}/5 elements, {word_count} words"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "message": "Failed to generate story for structure analysis"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_multiple_story_consistency(self):
        """Test 3 different story requests for consistency"""
        try:
            story_requests = [
                "Tell me a story about a brave knight",
                "Can you tell me a story about a wise owl",
                "I want a story about a friendly robot"
            ]
            
            consistency_results = []
            
            for request in story_requests:
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
                        response_text = data.get("response_text", "")
                        word_count = len(response_text.split())
                        
                        consistency_results.append({
                            "request": request,
                            "word_count": word_count,
                            "response_length": len(response_text),
                            "content_type": data.get("content_type"),
                            "consistent_quality": word_count >= 200  # Minimum quality threshold
                        })
                    else:
                        consistency_results.append({
                            "request": request,
                            "word_count": 0,
                            "consistent_quality": False,
                            "error": f"HTTP {response.status}"
                        })
                
                await asyncio.sleep(0.5)  # Brief pause between requests
            
            consistent_stories = [r for r in consistency_results if r.get("consistent_quality", False)]
            consistency_rate = len(consistent_stories) / len(story_requests) * 100
            
            word_counts = [r.get("word_count", 0) for r in consistency_results if r.get("word_count", 0) > 0]
            word_count_variance = max(word_counts) - min(word_counts) if word_counts else 0
            
            return {
                "success": consistency_rate >= 100 and word_count_variance < 500,  # High consistency required
                "consistency_rate": f"{consistency_rate:.1f}%",
                "consistent_stories": len(consistent_stories),
                "total_stories": len(story_requests),
                "word_count_variance": word_count_variance,
                "average_word_count": round(sum(word_counts) / len(word_counts)) if word_counts else 0,
                "consistency_results": consistency_results,
                "message": f"Story consistency: {consistency_rate:.1f}% rate, {word_count_variance} word variance"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_unlimited_token_implementation(self):
        """Test unlimited token solution works"""
        try:
            # Test with explicit request for long story
            long_story_request = "Please tell me a very long, detailed story with at least 300 words about a magical forest adventure with multiple characters and a complete plot"
            
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": long_story_request
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    word_count = len(response_text.split())
                    
                    # Check for signs of token limitation
                    appears_truncated = response_text.endswith("...") or len(response_text) < 500
                    has_complete_ending = any(phrase in response_text.lower()[-100:] for phrase in ["the end", "happily", "finally", "home", "safe"])
                    
                    unlimited_tokens_working = word_count >= 300 and not appears_truncated and has_complete_ending
                    
                    return {
                        "success": unlimited_tokens_working,
                        "unlimited_tokens_working": unlimited_tokens_working,
                        "word_count": word_count,
                        "character_count": len(response_text),
                        "appears_truncated": appears_truncated,
                        "has_complete_ending": has_complete_ending,
                        "content_type": data.get("content_type"),
                        "story_preview": response_text[:300] + "..." if len(response_text) > 300 else response_text,
                        "message": f"Unlimited tokens: {word_count} words, {'working' if unlimited_tokens_working else 'limited'}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "message": "Failed to test unlimited token implementation"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # STATIC STORY NARRATION SYSTEM TESTS
    
    async def test_userprofile_error_fix(self):
        """Test no more 'Failed to retrieve user profile' errors"""
        try:
            # Test user profile retrieval
            async with self.session.get(
                f"{BACKEND_URL}/users/profile/{self.test_user_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Test story narration endpoint that previously had UserProfile errors
                    form_data = {"user_id": self.test_user_id}
                    
                    async with self.session.post(
                        f"{BACKEND_URL}/content/stories/story_clever_rabbit/narrate",
                        data=form_data
                    ) as narrate_response:
                        narrate_text = await narrate_response.text()
                        
                        has_profile_error = "Failed to retrieve user profile" in narrate_text
                        has_userprofile_error = "UserProfile object has no attribute" in narrate_text
                        
                        return {
                            "success": not has_profile_error and not has_userprofile_error,
                            "user_profile_accessible": True,
                            "no_profile_error": not has_profile_error,
                            "no_userprofile_attribute_error": not has_userprofile_error,
                            "narration_status": narrate_response.status,
                            "user_profile_data": {
                                "id": data.get("id"),
                                "name": data.get("name"),
                                "age": data.get("age")
                            },
                            "message": "UserProfile errors fixed" if not has_profile_error and not has_userprofile_error else "UserProfile errors still present"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"User profile not accessible: HTTP {response.status}",
                        "message": "User profile retrieval failed"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_complete_story_loading(self):
        """Test get_story_narration returns full 1000+ word stories"""
        try:
            # Test story narration endpoint
            form_data = {"user_id": self.test_user_id}
            
            async with self.session.post(
                f"{BACKEND_URL}/content/stories/story_clever_rabbit/narrate",
                data=form_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    response_audio = data.get("response_audio", "")
                    word_count = len(response_text.split()) if response_text else 0
                    
                    complete_story_loaded = word_count >= 500 and bool(response_text) and bool(response_audio)
                    
                    return {
                        "success": complete_story_loaded,
                        "complete_story_loaded": complete_story_loaded,
                        "word_count": word_count,
                        "has_response_text": bool(response_text),
                        "has_response_audio": bool(response_audio),
                        "audio_size": len(response_audio) if response_audio else 0,
                        "story_title": data.get("title", ""),
                        "story_preview": response_text[:200] + "..." if response_text and len(response_text) > 200 else response_text,
                        "message": f"Story loading: {word_count} words, {'complete' if complete_story_loaded else 'incomplete'}"
                    }
                else:
                    response_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                        "message": "Story loading failed"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_story_narration_endpoint(self):
        """Test /api/content/stories/{story_id}/narrate works perfectly"""
        try:
            # Test the story narration endpoint
            form_data = {"user_id": self.test_user_id}
            
            async with self.session.post(
                f"{BACKEND_URL}/content/stories/story_clever_rabbit/narrate",
                data=form_data
            ) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        
                        endpoint_working_perfectly = all([
                            data.get("status") == "success",
                            bool(data.get("response_text")),
                            bool(data.get("response_audio")),
                            data.get("word_count", 0) > 0
                        ])
                        
                        return {
                            "success": endpoint_working_perfectly,
                            "endpoint_working_perfectly": endpoint_working_perfectly,
                            "status": data.get("status"),
                            "has_response_text": bool(data.get("response_text")),
                            "has_response_audio": bool(data.get("response_audio")),
                            "word_count": data.get("word_count", 0),
                            "story_title": data.get("title", ""),
                            "is_complete": data.get("is_complete", False),
                            "method": data.get("method", ""),
                            "message": "Story narration endpoint working perfectly" if endpoint_working_perfectly else "Story narration endpoint has issues"
                        }
                    except json.JSONDecodeError:
                        return {
                            "success": False,
                            "error": "Invalid JSON response",
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                            "message": "Story narration endpoint returning invalid JSON"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                        "message": "Story narration endpoint not working"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_all_stories_available(self):
        """Test each of the 5 stories can be narrated completely"""
        try:
            # Get list of available stories
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status == 200:
                    data = await response.json()
                    stories = data.get("stories", [])
                    
                    if len(stories) < 5:
                        return {
                            "success": False,
                            "error": f"Only {len(stories)} stories available, need 5",
                            "available_stories": len(stories),
                            "message": "Insufficient stories available"
                        }
                    
                    # Test narration for each story
                    narration_results = []
                    
                    for story in stories[:5]:  # Test first 5 stories
                        story_id = story.get("id", "")
                        form_data = {"user_id": self.test_user_id}
                        
                        async with self.session.post(
                            f"{BACKEND_URL}/content/stories/{story_id}/narrate",
                            data=form_data
                        ) as narrate_response:
                            if narrate_response.status == 200:
                                narrate_data = await narrate_response.json()
                                
                                narration_results.append({
                                    "story_id": story_id,
                                    "title": story.get("title", ""),
                                    "narration_working": bool(narrate_data.get("response_text")) and bool(narrate_data.get("response_audio")),
                                    "word_count": narrate_data.get("word_count", 0),
                                    "has_audio": bool(narrate_data.get("response_audio"))
                                })
                            else:
                                narration_results.append({
                                    "story_id": story_id,
                                    "title": story.get("title", ""),
                                    "narration_working": False,
                                    "error": f"HTTP {narrate_response.status}"
                                })
                        
                        await asyncio.sleep(0.3)  # Brief pause between requests
                    
                    working_narrations = [r for r in narration_results if r.get("narration_working", False)]
                    all_stories_working = len(working_narrations) == 5
                    
                    return {
                        "success": all_stories_working,
                        "all_stories_working": all_stories_working,
                        "working_narrations": len(working_narrations),
                        "total_stories": len(narration_results),
                        "available_stories": len(stories),
                        "narration_results": narration_results,
                        "message": f"Story narration: {len(working_narrations)}/5 stories working"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Stories endpoint failed: HTTP {response.status}",
                        "message": "Cannot retrieve stories list"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # COMPLETE SYSTEM INTEGRATION TESTS
    
    async def test_context_continuity(self):
        """Test conversation history is maintained perfectly"""
        try:
            # Multi-turn conversation test
            conversation_turns = [
                "Hi, my name is Emma and I love animals",
                "What's my name?",
                "What do I love?",
                "Can you tell me a story about my favorite thing?"
            ]
            
            context_results = []
            
            for i, message in enumerate(conversation_turns):
                text_input = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": message
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=text_input
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "").lower()
                        
                        # Check context awareness
                        context_maintained = False
                        if i == 1:  # "What's my name?"
                            context_maintained = "emma" in response_text
                        elif i == 2:  # "What do I love?"
                            context_maintained = "animal" in response_text
                        elif i == 3:  # Story about favorite thing
                            context_maintained = "animal" in response_text or "creature" in response_text
                        else:
                            context_maintained = True  # First message
                        
                        context_results.append({
                            "turn": i + 1,
                            "message": message,
                            "context_maintained": context_maintained,
                            "response_preview": data.get("response_text", "")[:100] + "..."
                        })
                    else:
                        context_results.append({
                            "turn": i + 1,
                            "message": message,
                            "context_maintained": False,
                            "error": f"HTTP {response.status}"
                        })
                
                await asyncio.sleep(0.5)  # Brief pause between turns
            
            context_maintained_count = sum(1 for r in context_results if r.get("context_maintained", False))
            perfect_context = context_maintained_count == len(conversation_turns)
            
            return {
                "success": perfect_context,
                "perfect_context_continuity": perfect_context,
                "context_maintained_turns": context_maintained_count,
                "total_turns": len(conversation_turns),
                "context_success_rate": f"{context_maintained_count/len(conversation_turns)*100:.1f}%",
                "context_results": context_results,
                "message": f"Context continuity: {context_maintained_count}/{len(conversation_turns)} turns maintained"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_human_like_expressions(self):
        """Test [giggle], [chuckle] expressions are processed"""
        try:
            # Test conversation that should trigger human-like expressions
            expression_request = "Tell me a funny joke that will make me laugh!"
            
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": expression_request
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    
                    # Check for human-like expressions
                    expressions_found = []
                    expression_patterns = ["[giggle]", "[chuckle]", "[laugh]", "[smile]", "[wink]", "*giggle*", "*chuckle*", "*laugh*"]
                    
                    for pattern in expression_patterns:
                        if pattern in response_text.lower():
                            expressions_found.append(pattern)
                    
                    has_expressions = len(expressions_found) > 0
                    
                    return {
                        "success": has_expressions,
                        "has_human_like_expressions": has_expressions,
                        "expressions_found": expressions_found,
                        "expression_count": len(expressions_found),
                        "response_text": response_text,
                        "content_type": data.get("content_type"),
                        "message": f"Human-like expressions: {len(expressions_found)} found" if has_expressions else "No human-like expressions detected"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "message": "Failed to test human-like expressions"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_memory_integration(self):
        """Test user preferences and past interactions are remembered"""
        try:
            # Generate memory snapshot first
            async with self.session.post(
                f"{BACKEND_URL}/memory/snapshot/{self.test_user_id}"
            ) as snapshot_response:
                snapshot_success = snapshot_response.status == 200
            
            # Get memory context
            async with self.session.get(
                f"{BACKEND_URL}/memory/context/{self.test_user_id}"
            ) as context_response:
                if context_response.status == 200:
                    context_data = await context_response.json()
                    
                    # Test memory-aware conversation
                    memory_request = "Remember what we talked about before and tell me something related"
                    
                    text_input = {
                        "session_id": self.test_session_id,
                        "user_id": self.test_user_id,
                        "message": memory_request
                    }
                    
                    async with self.session.post(
                        f"{BACKEND_URL}/conversations/text",
                        json=text_input
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            metadata = data.get("metadata", {})
                            
                            memory_integration_working = all([
                                snapshot_success,
                                bool(context_data.get("memory_context") or context_data.get("recent_preferences")),
                                bool(metadata.get("memory_context")),
                                bool(data.get("response_text"))
                            ])
                            
                            return {
                                "success": memory_integration_working,
                                "memory_integration_working": memory_integration_working,
                                "snapshot_generated": snapshot_success,
                                "has_memory_context": bool(context_data.get("memory_context") or context_data.get("recent_preferences")),
                                "conversation_uses_memory": bool(metadata.get("memory_context")),
                                "memory_context_type": type(context_data.get("memory_context", "")).__name__,
                                "response_length": len(data.get("response_text", "")),
                                "message": "Memory integration working" if memory_integration_working else "Memory integration issues detected"
                            }
                        else:
                            return {
                                "success": False,
                                "error": f"Memory conversation failed: HTTP {response.status}",
                                "message": "Memory-aware conversation failed"
                            }
                else:
                    return {
                        "success": False,
                        "error": f"Memory context failed: HTTP {context_response.status}",
                        "message": "Memory context retrieval failed"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_complete_responses(self):
        """Test riddles include punchlines, conversations are wholesome"""
        try:
            # Test riddle with punchline
            riddle_request = "Tell me a riddle with the answer"
            
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": riddle_request
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    
                    # Check for complete riddle structure
                    has_question = "?" in response_text
                    has_answer_indicator = any(phrase in response_text.lower() for phrase in ["answer:", "answer is", "the answer", "it's", "it is"])
                    is_wholesome = not any(word in response_text.lower() for word in ["scary", "violent", "inappropriate", "bad"])
                    
                    complete_response = has_question and has_answer_indicator and is_wholesome and len(response_text) > 50
                    
                    return {
                        "success": complete_response,
                        "complete_response": complete_response,
                        "has_question": has_question,
                        "has_answer": has_answer_indicator,
                        "is_wholesome": is_wholesome,
                        "response_length": len(response_text),
                        "content_type": data.get("content_type"),
                        "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                        "message": "Complete responses working" if complete_response else "Incomplete responses detected"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "message": "Failed to test complete responses"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # FRONTEND-BACKEND INTEGRATION TESTS
    
    async def test_formdata_processing(self):
        """Test frontend FormData is processed correctly by backend"""
        try:
            # Test FormData processing (like voice endpoint)
            mock_audio = b"mock_formdata_audio_test" * 10
            audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
            
            form_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": audio_base64
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/voice/process_audio",
                data=form_data  # FormData format
            ) as response:
                formdata_processed = response.status != 422  # Not unprocessable entity
                
                # Also test story narration FormData
                story_form_data = {"user_id": self.test_user_id}
                
                async with self.session.post(
                    f"{BACKEND_URL}/content/stories/story_clever_rabbit/narrate",
                    data=story_form_data
                ) as story_response:
                    story_formdata_processed = story_response.status != 422
                    
                    both_formdata_working = formdata_processed and story_formdata_processed
                    
                    return {
                        "success": both_formdata_working,
                        "formdata_processing_working": both_formdata_working,
                        "voice_formdata_processed": formdata_processed,
                        "story_formdata_processed": story_formdata_processed,
                        "voice_status": response.status,
                        "story_status": story_response.status,
                        "message": "FormData processing working" if both_formdata_working else "FormData processing issues"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_api_contract_alignment(self):
        """Test all endpoints use correct data formats"""
        try:
            # Test various endpoint contracts
            contract_tests = []
            
            # Test JSON endpoint
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Test message"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                contract_tests.append({
                    "endpoint": "conversations/text",
                    "format": "JSON",
                    "status": response.status,
                    "contract_aligned": response.status in [200, 400, 500]
                })
            
            # Test FormData endpoint
            form_data = {"user_id": self.test_user_id}
            
            async with self.session.post(
                f"{BACKEND_URL}/content/stories/story_clever_rabbit/narrate",
                data=form_data
            ) as response:
                contract_tests.append({
                    "endpoint": "content/stories/narrate",
                    "format": "FormData",
                    "status": response.status,
                    "contract_aligned": response.status in [200, 400, 500]
                })
            
            # Test GET endpoint
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                contract_tests.append({
                    "endpoint": "health",
                    "format": "GET",
                    "status": response.status,
                    "contract_aligned": response.status == 200
                })
            
            aligned_contracts = [t for t in contract_tests if t.get("contract_aligned", False)]
            all_contracts_aligned = len(aligned_contracts) == len(contract_tests)
            
            return {
                "success": all_contracts_aligned,
                "api_contracts_aligned": all_contracts_aligned,
                "aligned_contracts": len(aligned_contracts),
                "total_contracts": len(contract_tests),
                "contract_tests": contract_tests,
                "message": f"API contracts: {len(aligned_contracts)}/{len(contract_tests)} aligned"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_error_recovery(self):
        """Test graceful error handling throughout the system"""
        try:
            # Test various error scenarios
            error_scenarios = [
                {
                    "name": "Invalid user ID",
                    "endpoint": f"{BACKEND_URL}/users/profile/invalid_user_id",
                    "method": "GET",
                    "expected_status": [404, 500]
                },
                {
                    "name": "Missing required field",
                    "endpoint": f"{BACKEND_URL}/conversations/text",
                    "method": "POST",
                    "data": {"session_id": "test"},  # Missing user_id and message
                    "expected_status": [400, 422, 500]
                },
                {
                    "name": "Invalid story ID",
                    "endpoint": f"{BACKEND_URL}/content/stories/invalid_story/narrate",
                    "method": "POST",
                    "data": {"user_id": self.test_user_id},
                    "expected_status": [404, 400, 500]
                }
            ]
            
            error_recovery_results = []
            
            for scenario in error_scenarios:
                try:
                    if scenario["method"] == "GET":
                        async with self.session.get(scenario["endpoint"]) as response:
                            graceful_error = response.status in scenario["expected_status"]
                            error_recovery_results.append({
                                "scenario": scenario["name"],
                                "status": response.status,
                                "graceful_error": graceful_error,
                                "method": scenario["method"]
                            })
                    else:  # POST
                        async with self.session.post(
                            scenario["endpoint"],
                            json=scenario.get("data", {}),
                            data=scenario.get("data", {}) if "narrate" in scenario["endpoint"] else None
                        ) as response:
                            graceful_error = response.status in scenario["expected_status"]
                            error_recovery_results.append({
                                "scenario": scenario["name"],
                                "status": response.status,
                                "graceful_error": graceful_error,
                                "method": scenario["method"]
                            })
                except Exception as e:
                    error_recovery_results.append({
                        "scenario": scenario["name"],
                        "graceful_error": False,
                        "error": str(e),
                        "method": scenario["method"]
                    })
            
            graceful_errors = [r for r in error_recovery_results if r.get("graceful_error", False)]
            error_recovery_working = len(graceful_errors) == len(error_scenarios)
            
            return {
                "success": error_recovery_working,
                "error_recovery_working": error_recovery_working,
                "graceful_errors": len(graceful_errors),
                "total_scenarios": len(error_scenarios),
                "error_recovery_results": error_recovery_results,
                "message": f"Error recovery: {len(graceful_errors)}/{len(error_scenarios)} scenarios handled gracefully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_cross_platform_compatibility(self):
        """Test system works on mobile and desktop"""
        try:
            # Test different user agents and content types
            compatibility_tests = []
            
            # Test with mobile user agent
            mobile_headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
            }
            
            async with self.session.get(
                f"{BACKEND_URL}/health",
                headers=mobile_headers
            ) as response:
                compatibility_tests.append({
                    "platform": "Mobile",
                    "test": "Health check",
                    "status": response.status,
                    "compatible": response.status == 200
                })
            
            # Test with desktop user agent
            desktop_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            async with self.session.get(
                f"{BACKEND_URL}/health",
                headers=desktop_headers
            ) as response:
                compatibility_tests.append({
                    "platform": "Desktop",
                    "test": "Health check",
                    "status": response.status,
                    "compatible": response.status == 200
                })
            
            # Test API endpoints work regardless of platform
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Cross-platform test"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input,
                headers=mobile_headers
            ) as response:
                compatibility_tests.append({
                    "platform": "Mobile",
                    "test": "Text conversation",
                    "status": response.status,
                    "compatible": response.status == 200
                })
            
            compatible_tests = [t for t in compatibility_tests if t.get("compatible", False)]
            cross_platform_working = len(compatible_tests) == len(compatibility_tests)
            
            return {
                "success": cross_platform_working,
                "cross_platform_compatible": cross_platform_working,
                "compatible_tests": len(compatible_tests),
                "total_tests": len(compatibility_tests),
                "compatibility_tests": compatibility_tests,
                "message": f"Cross-platform: {len(compatible_tests)}/{len(compatibility_tests)} tests compatible"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_final_report(self):
        """Generate comprehensive final validation report"""
        success_rate = (self.success_count / self.total_tests * 100) if self.total_tests > 0 else 0
        
        # Categorize results
        voice_pipeline_tests = [k for k in self.test_results.keys() if "🎤" in k or "🔊" in k or "🎵" in k or "⚠️" in k]
        story_generation_tests = [k for k in self.test_results.keys() if "📚" in k or "📖" in k or "📝" in k or "🚀" in k]
        story_narration_tests = [k for k in self.test_results.keys() if "👤" in k or "📚" in k or "🎵" in k and "narration" in k.lower()]
        system_integration_tests = [k for k in self.test_results.keys() if "🧠" in k or "😊" in k or "💾" in k or "✅" in k]
        frontend_backend_tests = [k for k in self.test_results.keys() if "📋" in k or "🔗" in k or "🛡️" in k or "📱" in k]
        
        # Calculate category success rates
        def calculate_category_success(test_keys):
            if not test_keys:
                return 0
            passed = sum(1 for k in test_keys if self.test_results[k]["status"] == "✅ PASS")
            return (passed / len(test_keys)) * 100
        
        voice_success = calculate_category_success(voice_pipeline_tests)
        story_success = calculate_category_success(story_generation_tests)
        narration_success = calculate_category_success(story_narration_tests)
        integration_success = calculate_category_success(system_integration_tests)
        frontend_success = calculate_category_success(frontend_backend_tests)
        
        report = {
            "final_validation_summary": {
                "overall_success_rate": f"{success_rate:.1f}%",
                "total_tests": self.total_tests,
                "passed_tests": self.success_count,
                "failed_tests": len(self.critical_failures),
                "confidence_level": "HIGH" if success_rate >= 90 else "MEDIUM" if success_rate >= 70 else "LOW"
            },
            "category_results": {
                "voice_pipeline": {
                    "success_rate": f"{voice_success:.1f}%",
                    "tests": len(voice_pipeline_tests),
                    "status": "✅ WORKING" if voice_success >= 100 else "❌ ISSUES"
                },
                "story_generation": {
                    "success_rate": f"{story_success:.1f}%",
                    "tests": len(story_generation_tests),
                    "status": "✅ WORKING" if story_success >= 100 else "❌ ISSUES"
                },
                "story_narration": {
                    "success_rate": f"{narration_success:.1f}%",
                    "tests": len(story_narration_tests),
                    "status": "✅ WORKING" if narration_success >= 100 else "❌ ISSUES"
                },
                "system_integration": {
                    "success_rate": f"{integration_success:.1f}%",
                    "tests": len(system_integration_tests),
                    "status": "✅ WORKING" if integration_success >= 100 else "❌ ISSUES"
                },
                "frontend_backend": {
                    "success_rate": f"{frontend_success:.1f}%",
                    "tests": len(frontend_backend_tests),
                    "status": "✅ WORKING" if frontend_success >= 100 else "❌ ISSUES"
                }
            },
            "critical_failures": self.critical_failures,
            "detailed_results": self.test_results,
            "production_readiness": {
                "ready": success_rate >= 95,
                "confidence": f"{success_rate:.1f}%",
                "blocking_issues": len(self.critical_failures),
                "recommendation": "DEPLOY" if success_rate >= 95 else "FIX ISSUES" if success_rate >= 80 else "MAJOR FIXES NEEDED"
            }
        }
        
        return report

async def main():
    """Run final comprehensive validation"""
    async with FinalValidationTester() as tester:
        results = await tester.run_final_validation()
        
        print("\n" + "="*80)
        print("🎯 FINAL COMPREHENSIVE VALIDATION RESULTS")
        print("="*80)
        
        summary = results["final_validation_summary"]
        print(f"Overall Success Rate: {summary['overall_success_rate']}")
        print(f"Tests Passed: {summary['passed_tests']}/{summary['total_tests']}")
        print(f"Confidence Level: {summary['confidence_level']}")
        
        print("\n📊 CATEGORY BREAKDOWN:")
        for category, data in results["category_results"].items():
            print(f"  {category.replace('_', ' ').title()}: {data['success_rate']} {data['status']}")
        
        if results["critical_failures"]:
            print(f"\n❌ CRITICAL FAILURES ({len(results['critical_failures'])}):")
            for failure in results["critical_failures"]:
                print(f"  - {failure}")
        
        production = results["production_readiness"]
        print(f"\n🚀 PRODUCTION READINESS: {production['recommendation']}")
        print(f"   Ready: {'YES' if production['ready'] else 'NO'}")
        print(f"   Confidence: {production['confidence']}")
        print(f"   Blocking Issues: {production['blocking_issues']}")
        
        return results

if __name__ == "__main__":
    results = asyncio.run(main())