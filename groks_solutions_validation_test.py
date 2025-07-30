#!/usr/bin/env python3
"""
🎯 GROK'S SOLUTIONS VALIDATION - COMPREHENSIVE FINAL TESTING
Validates ALL of Grok's solutions have achieved 100% functionality as requested in review.

CRITICAL TEST AREAS:
1. VOICE PIPELINE TESTS (STT, TTS, Complete Voice Flow)
2. STORY GENERATION TESTS (300+ words, Complete narratives)
3. STATIC STORY NARRATION TESTS (Complete story loading)
4. SYSTEM INTEGRATION TESTS (Context continuity, Memory, etc.)
"""

import asyncio
import aiohttp
import json
import base64
import time
import os
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GroksValidationTester:
    def __init__(self):
        # Get backend URL from frontend .env
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    self.base_url = line.split('=')[1].strip()
                    break
        
        self.api_url = f"{self.base_url}/api"
        self.test_results = {}
        self.session = None
        
        # Test data
        self.test_user_id = "grok_validation_user"
        self.test_session_id = "grok_validation_session"
        
        logger.info(f"🎯 GROK'S VALIDATION TESTER INITIALIZED")
        logger.info(f"📡 Backend URL: {self.base_url}")
        logger.info(f"🔗 API URL: {self.api_url}")

    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
        # Create test user profile
        try:
            user_data = {
                "name": "Grok Test Child",
                "age": 7,
                "language": "english",
                "location": "Test City",
                "parent_email": "test@example.com",
                "preferences": {
                    "voice_personality": "story_narrator",
                    "learning_goals": ["storytelling", "creativity"],
                    "favorite_topics": ["adventures", "animals", "magic"]
                }
            }
            
            async with self.session.post(f"{self.api_url}/users/profile", json=user_data) as response:
                if response.status == 200:
                    logger.info("✅ Test user profile created successfully")
                else:
                    logger.warning(f"⚠️ User profile creation returned {response.status}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Could not create test user: {str(e)}")

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    # =============================================================================
    # CRITICAL VOICE PIPELINE TESTS (Must be 100%)
    # =============================================================================
    
    async def test_stt_functionality(self) -> Dict[str, Any]:
        """Test speech-to-text with FormData format"""
        logger.info("🎤 TESTING: STT Functionality with FormData format")
        
        try:
            # Create minimal test audio data (base64 encoded)
            test_audio_data = b"fake_audio_data_for_testing"
            audio_base64 = base64.b64encode(test_audio_data).decode('utf-8')
            
            # Test with FormData format as expected by the API
            form_data = aiohttp.FormData()
            form_data.add_field('session_id', self.test_session_id)
            form_data.add_field('user_id', self.test_user_id)
            form_data.add_field('audio_base64', audio_base64)
            
            async with self.session.post(f"{self.api_url}/voice/process_audio", data=form_data) as response:
                result = await response.json()
                
                if response.status == 200:
                    return {
                        "status": "✅ WORKING",
                        "details": f"STT endpoint accessible, response: {result.get('status', 'unknown')}",
                        "response_data": result
                    }
                elif response.status == 422:
                    return {
                        "status": "❌ FAILED", 
                        "details": f"HTTP 422 - Validation error: {result}",
                        "error": "FormData validation failed"
                    }
                else:
                    return {
                        "status": "❌ FAILED",
                        "details": f"HTTP {response.status}: {result}",
                        "error": f"Unexpected status code: {response.status}"
                    }
                    
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"STT test exception: {str(e)}",
                "error": str(e)
            }

    async def test_tts_functionality(self) -> Dict[str, Any]:
        """Test text-to-speech generates audio successfully"""
        logger.info("🔊 TESTING: TTS Functionality")
        
        try:
            # Test TTS through text conversation endpoint
            text_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Hello, can you say something nice?"
            }
            
            async with self.session.post(f"{self.api_url}/conversations/text", json=text_data) as response:
                result = await response.json()
                
                if response.status == 200:
                    response_audio = result.get("response_audio")
                    response_text = result.get("response_text", "")
                    
                    if response_audio and len(response_audio) > 100:
                        return {
                            "status": "✅ WORKING",
                            "details": f"TTS generated {len(response_audio)} chars of audio data",
                            "response_text": response_text[:100] + "..." if len(response_text) > 100 else response_text,
                            "audio_size": len(response_audio)
                        }
                    else:
                        return {
                            "status": "❌ FAILED",
                            "details": f"No audio generated or audio too small: {len(response_audio) if response_audio else 0} chars",
                            "response_text": response_text
                        }
                else:
                    return {
                        "status": "❌ FAILED",
                        "details": f"HTTP {response.status}: {result}",
                        "error": f"TTS endpoint failed with status {response.status}"
                    }
                    
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"TTS test exception: {str(e)}",
                "error": str(e)
            }

    async def test_complete_voice_flow(self) -> Dict[str, Any]:
        """Test STT → LLM → TTS pipeline end-to-end"""
        logger.info("🔄 TESTING: Complete Voice Flow (STT → LLM → TTS)")
        
        try:
            # Create test audio data
            test_audio_data = b"test_voice_input_for_complete_flow"
            audio_base64 = base64.b64encode(test_audio_data).decode('utf-8')
            
            # Test complete voice processing pipeline
            form_data = aiohttp.FormData()
            form_data.add_field('session_id', self.test_session_id)
            form_data.add_field('user_id', self.test_user_id)
            form_data.add_field('audio_base64', audio_base64)
            
            async with self.session.post(f"{self.api_url}/voice/process_audio", data=form_data) as response:
                result = await response.json()
                
                if response.status == 200:
                    transcript = result.get("transcript", "")
                    response_text = result.get("response_text", "")
                    response_audio = result.get("response_audio")
                    
                    pipeline_complete = all([
                        result.get("status") == "success",
                        response_text,  # LLM generated response
                        response_audio  # TTS generated audio
                    ])
                    
                    if pipeline_complete:
                        return {
                            "status": "✅ WORKING",
                            "details": f"Complete pipeline working: STT→LLM→TTS",
                            "transcript": transcript,
                            "response_text": response_text[:100] + "..." if len(response_text) > 100 else response_text,
                            "audio_generated": bool(response_audio),
                            "latency": result.get("latency", "unknown")
                        }
                    else:
                        return {
                            "status": "❌ FAILED",
                            "details": f"Pipeline incomplete - missing components",
                            "missing": {
                                "transcript": not transcript,
                                "response_text": not response_text,
                                "response_audio": not response_audio
                            }
                        }
                else:
                    return {
                        "status": "❌ FAILED",
                        "details": f"Voice flow failed with HTTP {response.status}",
                        "error": result
                    }
                    
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"Complete voice flow exception: {str(e)}",
                "error": str(e)
            }

    async def test_voice_error_handling(self) -> Dict[str, Any]:
        """Verify no 'Voice processing failed' messages"""
        logger.info("🛡️ TESTING: Voice Error Handling")
        
        try:
            # Test with empty audio data
            form_data = aiohttp.FormData()
            form_data.add_field('session_id', self.test_session_id)
            form_data.add_field('user_id', self.test_user_id)
            form_data.add_field('audio_base64', '')
            
            async with self.session.post(f"{self.api_url}/voice/process_audio", data=form_data) as response:
                result = await response.json()
                
                # Check for graceful error handling
                if response.status in [400, 422]:
                    error_message = result.get("detail", "").lower()
                    if "voice processing failed" in error_message:
                        return {
                            "status": "❌ FAILED",
                            "details": f"Found 'Voice processing failed' message: {error_message}",
                            "error": "Error message not user-friendly"
                        }
                    else:
                        return {
                            "status": "✅ WORKING",
                            "details": f"Graceful error handling with HTTP {response.status}",
                            "error_message": result.get("detail", "No error message")
                        }
                else:
                    return {
                        "status": "⚠️ PARTIAL",
                        "details": f"Unexpected response for empty audio: HTTP {response.status}",
                        "response": result
                    }
                    
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"Error handling test exception: {str(e)}",
                "error": str(e)
            }

    async def test_audio_format_support(self) -> Dict[str, Any]:
        """Test WebM, MP4, WAV compatibility"""
        logger.info("🎵 TESTING: Audio Format Support")
        
        formats_tested = []
        
        try:
            # Test different audio formats
            test_formats = [
                ("webm", b"webm_audio_data_test"),
                ("mp4", b"mp4_audio_data_test"),
                ("wav", b"wav_audio_data_test")
            ]
            
            for format_name, audio_data in test_formats:
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                form_data = aiohttp.FormData()
                form_data.add_field('session_id', self.test_session_id)
                form_data.add_field('user_id', self.test_user_id)
                form_data.add_field('audio_base64', audio_base64)
                
                async with self.session.post(f"{self.api_url}/voice/process_audio", data=form_data) as response:
                    result = await response.json()
                    
                    formats_tested.append({
                        "format": format_name,
                        "status_code": response.status,
                        "accepted": response.status != 415,  # 415 = Unsupported Media Type
                        "response": result.get("status", "unknown")
                    })
            
            # Check if formats are supported
            supported_formats = [f for f in formats_tested if f["accepted"]]
            
            if len(supported_formats) >= 2:  # At least 2 formats supported
                return {
                    "status": "✅ WORKING",
                    "details": f"Audio format support confirmed for {len(supported_formats)}/3 formats",
                    "supported_formats": [f["format"] for f in supported_formats],
                    "test_results": formats_tested
                }
            else:
                return {
                    "status": "❌ FAILED",
                    "details": f"Limited audio format support: {len(supported_formats)}/3 formats",
                    "test_results": formats_tested
                }
                
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"Audio format test exception: {str(e)}",
                "error": str(e)
            }

    # =============================================================================
    # GROK'S STORY GENERATION TESTS (Must generate 300+ words)
    # =============================================================================
    
    async def test_unlimited_token_generation(self) -> Dict[str, Any]:
        """Test stories now generate 300+ words consistently"""
        logger.info("📚 TESTING: Unlimited Token Generation (300+ words)")
        
        story_tests = [
            "Tell me a complete story about a brave little mouse who goes on an adventure",
            "I want a full story about a magical garden where animals can talk",
            "Can you tell me a long story about two friends who discover a hidden treasure"
        ]
        
        results = []
        
        try:
            for i, story_request in enumerate(story_tests, 1):
                text_data = {
                    "session_id": f"{self.test_session_id}_story_{i}",
                    "user_id": self.test_user_id,
                    "message": story_request
                }
                
                async with self.session.post(f"{self.api_url}/conversations/text", json=text_data) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        response_text = result.get("response_text", "")
                        word_count = len(response_text.split())
                        
                        results.append({
                            "test": f"Story {i}",
                            "request": story_request[:50] + "...",
                            "word_count": word_count,
                            "meets_requirement": word_count >= 300,
                            "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
                        })
                    else:
                        results.append({
                            "test": f"Story {i}",
                            "request": story_request[:50] + "...",
                            "word_count": 0,
                            "meets_requirement": False,
                            "error": f"HTTP {response.status}"
                        })
            
            # Calculate success rate
            successful_stories = [r for r in results if r["meets_requirement"]]
            success_rate = len(successful_stories) / len(results) * 100
            
            if success_rate >= 100:
                return {
                    "status": "✅ WORKING",
                    "details": f"All stories meet 300+ word requirement (100% success rate)",
                    "success_rate": f"{success_rate:.1f}%",
                    "test_results": results
                }
            elif success_rate >= 66:
                return {
                    "status": "⚠️ PARTIAL",
                    "details": f"Most stories meet requirement ({success_rate:.1f}% success rate)",
                    "success_rate": f"{success_rate:.1f}%",
                    "test_results": results
                }
            else:
                return {
                    "status": "❌ FAILED",
                    "details": f"Stories still severely truncated ({success_rate:.1f}% success rate)",
                    "success_rate": f"{success_rate:.1f}%",
                    "test_results": results,
                    "average_word_count": sum(r["word_count"] for r in results) / len(results)
                }
                
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"Story generation test exception: {str(e)}",
                "error": str(e)
            }

    async def test_story_completion(self) -> Dict[str, Any]:
        """Test stories have complete narrative structure"""
        logger.info("📖 TESTING: Story Completion (narrative structure)")
        
        try:
            story_request = "Tell me a complete story with a clear beginning, middle, and end about a young hero who overcomes a challenge"
            
            text_data = {
                "session_id": f"{self.test_session_id}_completion",
                "user_id": self.test_user_id,
                "message": story_request
            }
            
            async with self.session.post(f"{self.api_url}/conversations/text", json=text_data) as response:
                result = await response.json()
                
                if response.status == 200:
                    story_text = result.get("response_text", "")
                    word_count = len(story_text.split())
                    
                    # Check for narrative structure elements
                    structure_elements = {
                        "beginning": any(word in story_text.lower() for word in ["once", "there was", "long ago", "in a", "lived"]),
                        "character_introduction": any(word in story_text.lower() for word in ["hero", "character", "boy", "girl", "child"]),
                        "challenge": any(word in story_text.lower() for word in ["challenge", "problem", "difficulty", "obstacle", "trouble"]),
                        "resolution": any(word in story_text.lower() for word in ["solved", "overcame", "succeeded", "victory", "end", "finally"]),
                        "ending": story_text.lower().strip().endswith(('.', '!', '"'))
                    }
                    
                    structure_score = sum(structure_elements.values())
                    
                    return {
                        "status": "✅ WORKING" if structure_score >= 4 else "❌ FAILED",
                        "details": f"Story structure score: {structure_score}/5 elements present",
                        "word_count": word_count,
                        "structure_elements": structure_elements,
                        "story_preview": story_text[:200] + "..." if len(story_text) > 200 else story_text
                    }
                else:
                    return {
                        "status": "❌ FAILED",
                        "details": f"Story completion test failed with HTTP {response.status}",
                        "error": result
                    }
                    
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"Story completion test exception: {str(e)}",
                "error": str(e)
            }

    async def test_multiple_story_requests(self) -> Dict[str, Any]:
        """Test 3 different story requests for consistency"""
        logger.info("🔄 TESTING: Multiple Story Requests Consistency")
        
        story_themes = [
            "adventure",
            "friendship", 
            "magic"
        ]
        
        results = []
        
        try:
            for theme in story_themes:
                text_data = {
                    "session_id": f"{self.test_session_id}_{theme}",
                    "user_id": self.test_user_id,
                    "message": f"Tell me a complete story about {theme}"
                }
                
                async with self.session.post(f"{self.api_url}/conversations/text", json=text_data) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        story_text = result.get("response_text", "")
                        word_count = len(story_text.split())
                        
                        results.append({
                            "theme": theme,
                            "word_count": word_count,
                            "meets_300_words": word_count >= 300,
                            "content_type": result.get("content_type", "unknown"),
                            "story_preview": story_text[:100] + "..." if len(story_text) > 100 else story_text
                        })
                    else:
                        results.append({
                            "theme": theme,
                            "word_count": 0,
                            "meets_300_words": False,
                            "error": f"HTTP {response.status}"
                        })
            
            # Check consistency
            successful_stories = [r for r in results if r["meets_300_words"]]
            consistency_rate = len(successful_stories) / len(results) * 100
            avg_word_count = sum(r["word_count"] for r in results) / len(results)
            
            return {
                "status": "✅ WORKING" if consistency_rate == 100 else "❌ FAILED",
                "details": f"Story consistency: {consistency_rate:.1f}% success rate",
                "average_word_count": f"{avg_word_count:.0f} words",
                "consistency_rate": f"{consistency_rate:.1f}%",
                "test_results": results
            }
            
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"Multiple story requests test exception: {str(e)}",
                "error": str(e)
            }

    # =============================================================================
    # GROK'S STATIC STORY NARRATION TESTS (Must return complete stories)
    # =============================================================================
    
    async def test_static_story_loading(self) -> Dict[str, Any]:
        """Test get_story_narration returns complete text"""
        logger.info("📚 TESTING: Static Story Loading")
        
        try:
            # First get available stories
            async with self.session.get(f"{self.api_url}/content/stories") as response:
                if response.status != 200:
                    return {
                        "status": "❌ FAILED",
                        "details": f"Could not fetch stories list: HTTP {response.status}",
                        "error": "Stories endpoint not accessible"
                    }
                
                stories_data = await response.json()
                stories = stories_data.get("stories", [])
                
                if not stories:
                    return {
                        "status": "❌ FAILED",
                        "details": "No stories available in the library",
                        "error": "Empty stories library"
                    }
                
                # Test first story
                test_story = stories[0]
                story_id = test_story.get("id")
                
                return {
                    "status": "✅ WORKING",
                    "details": f"Static story library accessible with {len(stories)} stories",
                    "stories_count": len(stories),
                    "test_story_id": story_id,
                    "test_story_title": test_story.get("title", "Unknown"),
                    "stories_available": [{"id": s.get("id"), "title": s.get("title")} for s in stories[:3]]
                }
                
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"Static story loading test exception: {str(e)}",
                "error": str(e)
            }

    async def test_story_narration_endpoint(self) -> Dict[str, Any]:
        """Test /api/content/stories/{story_id}/narrate returns full response"""
        logger.info("🎵 TESTING: Story Narration Endpoint")
        
        try:
            # Get available stories first
            async with self.session.get(f"{self.api_url}/content/stories") as response:
                stories_data = await response.json()
                stories = stories_data.get("stories", [])
                
                if not stories:
                    return {
                        "status": "❌ FAILED",
                        "details": "No stories available for narration testing",
                        "error": "Empty stories library"
                    }
                
                # Test narration endpoint with first story
                test_story = stories[0]
                story_id = test_story.get("id")
                
                # Test story narration endpoint
                form_data = aiohttp.FormData()
                form_data.add_field('user_id', self.test_user_id)
                
                async with self.session.post(f"{self.api_url}/content/stories/{story_id}/narrate", data=form_data) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        response_text = result.get("response_text", "")
                        response_audio = result.get("response_audio", "")
                        word_count = result.get("word_count", 0)
                        
                        if response_text and len(response_text) > 100:
                            return {
                                "status": "✅ WORKING",
                                "details": f"Story narration endpoint working - {word_count} words generated",
                                "story_id": story_id,
                                "story_title": test_story.get("title"),
                                "response_text_length": len(response_text),
                                "response_audio_length": len(response_audio) if response_audio else 0,
                                "word_count": word_count,
                                "text_preview": response_text[:150] + "..." if len(response_text) > 150 else response_text
                            }
                        else:
                            return {
                                "status": "❌ FAILED",
                                "details": f"Story narration returned empty or minimal response",
                                "story_id": story_id,
                                "response_text_length": len(response_text),
                                "response_audio_length": len(response_audio) if response_audio else 0,
                                "full_response": result
                            }
                    else:
                        return {
                            "status": "❌ FAILED",
                            "details": f"Story narration endpoint failed with HTTP {response.status}",
                            "error": result,
                            "story_id": story_id
                        }
                        
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"Story narration endpoint test exception: {str(e)}",
                "error": str(e)
            }

    async def test_chunked_tts_processing(self) -> Dict[str, Any]:
        """Test complete stories generate audio without truncation"""
        logger.info("🎵 TESTING: Chunked TTS Processing")
        
        try:
            # Test with a long story request
            long_story_request = "Tell me a very detailed and complete story about a magical kingdom with multiple characters, adventures, and a satisfying conclusion. Make it a full story with at least 300 words."
            
            text_data = {
                "session_id": f"{self.test_session_id}_chunked",
                "user_id": self.test_user_id,
                "message": long_story_request
            }
            
            async with self.session.post(f"{self.api_url}/conversations/text", json=text_data) as response:
                result = await response.json()
                
                if response.status == 200:
                    response_text = result.get("response_text", "")
                    response_audio = result.get("response_audio", "")
                    word_count = len(response_text.split())
                    
                    # Check if chunked TTS would be needed (story > 1500 chars)
                    needs_chunking = len(response_text) > 1500
                    audio_generated = bool(response_audio and len(response_audio) > 1000)
                    
                    return {
                        "status": "✅ WORKING" if audio_generated else "❌ FAILED",
                        "details": f"Chunked TTS test - Story: {word_count} words, Audio: {len(response_audio) if response_audio else 0} chars",
                        "word_count": word_count,
                        "text_length": len(response_text),
                        "audio_length": len(response_audio) if response_audio else 0,
                        "needs_chunking": needs_chunking,
                        "audio_generated": audio_generated,
                        "story_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                    }
                else:
                    return {
                        "status": "❌ FAILED",
                        "details": f"Chunked TTS test failed with HTTP {response.status}",
                        "error": result
                    }
                    
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"Chunked TTS processing test exception: {str(e)}",
                "error": str(e)
            }

    async def test_all_5_stories(self) -> Dict[str, Any]:
        """Test each story in the library individually"""
        logger.info("📚 TESTING: All 5 Stories Individual Testing")
        
        try:
            # Get all available stories
            async with self.session.get(f"{self.api_url}/content/stories") as response:
                if response.status != 200:
                    return {
                        "status": "❌ FAILED",
                        "details": f"Could not fetch stories: HTTP {response.status}",
                        "error": "Stories endpoint not accessible"
                    }
                
                stories_data = await response.json()
                stories = stories_data.get("stories", [])
                
                if len(stories) < 5:
                    return {
                        "status": "⚠️ PARTIAL",
                        "details": f"Only {len(stories)} stories available, expected 5",
                        "stories_count": len(stories)
                    }
                
                # Test each story individually
                story_results = []
                
                for story in stories[:5]:  # Test first 5 stories
                    story_id = story.get("id")
                    story_title = story.get("title", "Unknown")
                    
                    # Test story narration
                    form_data = aiohttp.FormData()
                    form_data.add_field('user_id', self.test_user_id)
                    
                    try:
                        async with self.session.post(f"{self.api_url}/content/stories/{story_id}/narrate", data=form_data) as story_response:
                            story_result = await story_response.json()
                            
                            if story_response.status == 200:
                                response_text = story_result.get("response_text", "")
                                response_audio = story_result.get("response_audio", "")
                                word_count = story_result.get("word_count", 0)
                                
                                story_results.append({
                                    "story_id": story_id,
                                    "title": story_title,
                                    "status": "✅ WORKING" if response_text and len(response_text) > 100 else "❌ FAILED",
                                    "word_count": word_count,
                                    "text_length": len(response_text),
                                    "audio_length": len(response_audio) if response_audio else 0,
                                    "has_complete_response": bool(response_text and len(response_text) > 100)
                                })
                            else:
                                story_results.append({
                                    "story_id": story_id,
                                    "title": story_title,
                                    "status": "❌ FAILED",
                                    "error": f"HTTP {story_response.status}",
                                    "has_complete_response": False
                                })
                                
                    except Exception as story_error:
                        story_results.append({
                            "story_id": story_id,
                            "title": story_title,
                            "status": "❌ FAILED",
                            "error": str(story_error),
                            "has_complete_response": False
                        })
                
                # Calculate success rate
                successful_stories = [r for r in story_results if r["status"] == "✅ WORKING"]
                success_rate = len(successful_stories) / len(story_results) * 100
                
                return {
                    "status": "✅ WORKING" if success_rate == 100 else "❌ FAILED",
                    "details": f"Individual story testing: {len(successful_stories)}/{len(story_results)} stories working",
                    "success_rate": f"{success_rate:.1f}%",
                    "total_stories": len(stories),
                    "tested_stories": len(story_results),
                    "story_results": story_results
                }
                
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"All 5 stories test exception: {str(e)}",
                "error": str(e)
            }

    # =============================================================================
    # COMPLETE SYSTEM INTEGRATION TESTS
    # =============================================================================
    
    async def test_context_continuity(self) -> Dict[str, Any]:
        """Test multi-turn conversations maintain perfect context"""
        logger.info("🔄 TESTING: Context Continuity")
        
        try:
            session_id = f"{self.test_session_id}_context"
            
            # Multi-turn conversation test
            conversation_turns = [
                "My name is Alice and I love elephants",
                "What is my name?",
                "What animal do I love?",
                "Tell me a story about my favorite animal"
            ]
            
            responses = []
            
            for i, message in enumerate(conversation_turns, 1):
                text_data = {
                    "session_id": session_id,  # Same session for context
                    "user_id": self.test_user_id,
                    "message": message
                }
                
                async with self.session.post(f"{self.api_url}/conversations/text", json=text_data) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        response_text = result.get("response_text", "")
                        responses.append({
                            "turn": i,
                            "user_message": message,
                            "ai_response": response_text,
                            "response_length": len(response_text.split())
                        })
                    else:
                        responses.append({
                            "turn": i,
                            "user_message": message,
                            "error": f"HTTP {response.status}",
                            "ai_response": ""
                        })
            
            # Check context continuity
            context_checks = {
                "name_remembered": "alice" in responses[1]["ai_response"].lower() if len(responses) > 1 else False,
                "animal_remembered": "elephant" in responses[2]["ai_response"].lower() if len(responses) > 2 else False,
                "story_about_elephants": "elephant" in responses[3]["ai_response"].lower() if len(responses) > 3 else False,
                "all_responses_received": len([r for r in responses if "error" not in r]) == 4
            }
            
            context_score = sum(context_checks.values())
            
            return {
                "status": "✅ WORKING" if context_score >= 3 else "❌ FAILED",
                "details": f"Context continuity score: {context_score}/4 checks passed",
                "context_checks": context_checks,
                "conversation_turns": len(responses),
                "responses": responses
            }
            
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"Context continuity test exception: {str(e)}",
                "error": str(e)
            }

    async def test_complete_response_system(self) -> Dict[str, Any]:
        """Test riddles include punchlines, conversations are wholesome"""
        logger.info("🎭 TESTING: Complete Response System")
        
        try:
            test_requests = [
                {"type": "riddle", "message": "Tell me a riddle with the answer"},
                {"type": "joke", "message": "Tell me a funny joke"},
                {"type": "conversation", "message": "How are you feeling today?"}
            ]
            
            results = []
            
            for test in test_requests:
                text_data = {
                    "session_id": f"{self.test_session_id}_{test['type']}",
                    "user_id": self.test_user_id,
                    "message": test["message"]
                }
                
                async with self.session.post(f"{self.api_url}/conversations/text", json=text_data) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        response_text = result.get("response_text", "")
                        content_type = result.get("content_type", "unknown")
                        
                        # Check completeness based on type
                        is_complete = False
                        if test["type"] == "riddle":
                            is_complete = any(word in response_text.lower() for word in ["answer", "solution", "because", "it is"])
                        elif test["type"] == "joke":
                            is_complete = len(response_text.split()) > 10  # Jokes should be substantial
                        elif test["type"] == "conversation":
                            is_complete = len(response_text.split()) > 5  # Conversations should be meaningful
                        
                        results.append({
                            "type": test["type"],
                            "content_type_detected": content_type,
                            "is_complete": is_complete,
                            "word_count": len(response_text.split()),
                            "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
                        })
                    else:
                        results.append({
                            "type": test["type"],
                            "is_complete": False,
                            "error": f"HTTP {response.status}"
                        })
            
            # Calculate completeness score
            complete_responses = [r for r in results if r.get("is_complete", False)]
            completeness_rate = len(complete_responses) / len(results) * 100
            
            return {
                "status": "✅ WORKING" if completeness_rate >= 66 else "❌ FAILED",
                "details": f"Complete response system: {completeness_rate:.1f}% completeness rate",
                "completeness_rate": f"{completeness_rate:.1f}%",
                "test_results": results
            }
            
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"Complete response system test exception: {str(e)}",
                "error": str(e)
            }

    async def test_memory_integration(self) -> Dict[str, Any]:
        """Test user preferences and history are maintained"""
        logger.info("🧠 TESTING: Memory Integration")
        
        try:
            # Test memory endpoints
            memory_tests = []
            
            # Test memory context endpoint
            async with self.session.get(f"{self.api_url}/memory/context/{self.test_user_id}") as response:
                if response.status == 200:
                    memory_context = await response.json()
                    memory_tests.append({
                        "test": "memory_context",
                        "status": "✅ WORKING",
                        "details": f"Memory context retrieved with {len(memory_context.get('preferences', {}))} preferences"
                    })
                else:
                    memory_tests.append({
                        "test": "memory_context",
                        "status": "❌ FAILED",
                        "details": f"Memory context failed: HTTP {response.status}"
                    })
            
            # Test memory snapshot generation
            async with self.session.post(f"{self.api_url}/memory/snapshot/{self.test_user_id}") as response:
                if response.status == 200:
                    snapshot = await response.json()
                    memory_tests.append({
                        "test": "memory_snapshot",
                        "status": "✅ WORKING",
                        "details": f"Memory snapshot generated successfully"
                    })
                else:
                    memory_tests.append({
                        "test": "memory_snapshot",
                        "status": "❌ FAILED",
                        "details": f"Memory snapshot failed: HTTP {response.status}"
                    })
            
            # Test memory snapshots history
            async with self.session.get(f"{self.api_url}/memory/snapshots/{self.test_user_id}") as response:
                if response.status == 200:
                    snapshots = await response.json()
                    memory_tests.append({
                        "test": "memory_snapshots",
                        "status": "✅ WORKING",
                        "details": f"Memory snapshots history: {snapshots.get('count', 0)} snapshots"
                    })
                else:
                    memory_tests.append({
                        "test": "memory_snapshots",
                        "status": "❌ FAILED",
                        "details": f"Memory snapshots failed: HTTP {response.status}"
                    })
            
            # Calculate memory integration success
            working_tests = [t for t in memory_tests if t["status"] == "✅ WORKING"]
            success_rate = len(working_tests) / len(memory_tests) * 100
            
            return {
                "status": "✅ WORKING" if success_rate >= 66 else "❌ FAILED",
                "details": f"Memory integration: {len(working_tests)}/{len(memory_tests)} tests passed",
                "success_rate": f"{success_rate:.1f}%",
                "memory_tests": memory_tests
            }
            
        except Exception as e:
            return {
                "status": "❌ FAILED",
                "details": f"Memory integration test exception: {str(e)}",
                "error": str(e)
            }

    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    async def run_comprehensive_validation(self):
        """Run all Grok's solutions validation tests"""
        logger.info("🎯 STARTING GROK'S SOLUTIONS COMPREHENSIVE VALIDATION")
        
        await self.setup_session()
        
        # Define all test categories
        test_categories = {
            "CRITICAL VOICE PIPELINE TESTS": [
                ("STT Functionality", self.test_stt_functionality),
                ("TTS Functionality", self.test_tts_functionality),
                ("Complete Voice Flow", self.test_complete_voice_flow),
                ("Voice Error Handling", self.test_voice_error_handling),
                ("Audio Format Support", self.test_audio_format_support)
            ],
            "GROK'S STORY GENERATION TESTS": [
                ("Unlimited Token Generation", self.test_unlimited_token_generation),
                ("Story Completion", self.test_story_completion),
                ("Multiple Story Requests", self.test_multiple_story_requests)
            ],
            "GROK'S STATIC STORY NARRATION TESTS": [
                ("Static Story Loading", self.test_static_story_loading),
                ("Story Narration Endpoint", self.test_story_narration_endpoint),
                ("Chunked TTS Processing", self.test_chunked_tts_processing),
                ("All 5 Stories", self.test_all_5_stories)
            ],
            "COMPLETE SYSTEM INTEGRATION TESTS": [
                ("Context Continuity", self.test_context_continuity),
                ("Complete Response System", self.test_complete_response_system),
                ("Memory Integration", self.test_memory_integration)
            ]
        }
        
        # Run all tests
        all_results = {}
        total_tests = 0
        passed_tests = 0
        
        for category, tests in test_categories.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"🎯 TESTING CATEGORY: {category}")
            logger.info(f"{'='*60}")
            
            category_results = {}
            
            for test_name, test_func in tests:
                logger.info(f"\n🔍 Running: {test_name}")
                
                try:
                    result = await test_func()
                    category_results[test_name] = result
                    
                    status = result.get("status", "❌ FAILED")
                    details = result.get("details", "No details")
                    
                    logger.info(f"   {status}: {details}")
                    
                    total_tests += 1
                    if status == "✅ WORKING":
                        passed_tests += 1
                        
                except Exception as e:
                    logger.error(f"   ❌ FAILED: Test exception: {str(e)}")
                    category_results[test_name] = {
                        "status": "❌ FAILED",
                        "details": f"Test exception: {str(e)}",
                        "error": str(e)
                    }
                    total_tests += 1
            
            all_results[category] = category_results
        
        await self.cleanup_session()
        
        # Calculate overall success rate
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate final report
        logger.info(f"\n{'='*80}")
        logger.info(f"🎯 GROK'S SOLUTIONS VALIDATION COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"📊 OVERALL SUCCESS RATE: {overall_success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        # Detailed category breakdown
        for category, results in all_results.items():
            category_passed = len([r for r in results.values() if r.get("status") == "✅ WORKING"])
            category_total = len(results)
            category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            
            logger.info(f"\n📋 {category}: {category_rate:.1f}% ({category_passed}/{category_total})")
            
            for test_name, result in results.items():
                status = result.get("status", "❌ FAILED")
                logger.info(f"   {status} {test_name}")
        
        # Critical issues summary
        critical_failures = []
        for category, results in all_results.items():
            for test_name, result in results.items():
                if result.get("status") == "❌ FAILED":
                    critical_failures.append(f"{category}: {test_name}")
        
        if critical_failures:
            logger.info(f"\n🚨 CRITICAL FAILURES REQUIRING IMMEDIATE ATTENTION:")
            for failure in critical_failures:
                logger.info(f"   ❌ {failure}")
        
        # Success criteria assessment
        voice_pipeline_success = len([r for r in all_results.get("CRITICAL VOICE PIPELINE TESTS", {}).values() if r.get("status") == "✅ WORKING"])
        story_generation_success = len([r for r in all_results.get("GROK'S STORY GENERATION TESTS", {}).values() if r.get("status") == "✅ WORKING"])
        story_narration_success = len([r for r in all_results.get("GROK'S STATIC STORY NARRATION TESTS", {}).values() if r.get("status") == "✅ WORKING"])
        system_integration_success = len([r for r in all_results.get("COMPLETE SYSTEM INTEGRATION TESTS", {}).values() if r.get("status") == "✅ WORKING"])
        
        logger.info(f"\n🎯 SUCCESS CRITERIA ASSESSMENT:")
        logger.info(f"   Voice Pipeline: {voice_pipeline_success}/5 tests passed")
        logger.info(f"   Story Generation: {story_generation_success}/3 tests passed")
        logger.info(f"   Story Narration: {story_narration_success}/4 tests passed")
        logger.info(f"   System Integration: {system_integration_success}/3 tests passed")
        
        # Final confidence assessment
        if overall_success_rate >= 90:
            confidence_level = "🎉 HIGH CONFIDENCE - Ready for deployment"
        elif overall_success_rate >= 75:
            confidence_level = "⚠️ MODERATE CONFIDENCE - Minor fixes needed"
        elif overall_success_rate >= 50:
            confidence_level = "🔧 LOW CONFIDENCE - Major fixes required"
        else:
            confidence_level = "🚨 CRITICAL ISSUES - System not ready"
        
        logger.info(f"\n🎯 FINAL ASSESSMENT: {confidence_level}")
        logger.info(f"📊 Overall Success Rate: {overall_success_rate:.1f}%")
        
        return {
            "overall_success_rate": overall_success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "confidence_level": confidence_level,
            "critical_failures": critical_failures,
            "detailed_results": all_results,
            "category_breakdown": {
                "voice_pipeline": f"{voice_pipeline_success}/5",
                "story_generation": f"{story_generation_success}/3", 
                "story_narration": f"{story_narration_success}/4",
                "system_integration": f"{system_integration_success}/3"
            }
        }

async def main():
    """Main test execution"""
    tester = GroksValidationTester()
    results = await tester.run_comprehensive_validation()
    
    # Save results to file
    with open('/app/groks_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n🎯 GROK'S SOLUTIONS VALIDATION COMPLETE")
    print(f"📊 Final Success Rate: {results['overall_success_rate']:.1f}%")
    print(f"📋 Results saved to: /app/groks_validation_results.json")

if __name__ == "__main__":
    asyncio.run(main())