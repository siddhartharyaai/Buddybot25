#!/usr/bin/env python3
"""
Review Priority Backend Testing - Focus on Story Generation & Streaming
Testing Focus: Story Generation Length, Story Session Management, Barge-in Integration, Story Streaming Pipeline, Voice Processing Integration
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

class ReviewPriorityBackendTester:
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
        
        logger.info(f"🎯 REVIEW PRIORITY TESTING: Using backend URL: {self.base_url}")
        
        # Test data
        self.test_user_id = f"review_test_user_{int(time.time())}"
        self.test_session_id = f"review_session_{int(time.time())}"
        
        # Test results tracking
        self.test_results = {
            "story_generation_length": [],
            "story_session_management": [],
            "barge_in_integration": [],
            "story_streaming_pipeline": [],
            "voice_processing_integration": [],
            "overall_summary": {}
        }
        
        # Story test prompts for length testing
        self.story_prompts = [
            "Tell me a complete story about a brave little mouse who goes on an adventure",
            "I want a full story about a magical forest where animals can talk",
            "Can you tell me a long story about two friends who discover a hidden treasure",
            "Please tell me a detailed story about a young girl who can speak to dragons",
            "I'd like to hear a complete adventure story about a boy who finds a magic key"
        ]

    async def make_request(self, method: str, endpoint: str, data: Dict = None, timeout: int = 30) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                if method.upper() == 'GET':
                    async with session.get(url) as response:
                        result = await response.json()
                        return {"status_code": response.status, "data": result}
                elif method.upper() == 'POST':
                    headers = {'Content-Type': 'application/json'}
                    async with session.post(url, json=data, headers=headers) as response:
                        result = await response.json()
                        return {"status_code": response.status, "data": result}
                elif method.upper() == 'PUT':
                    headers = {'Content-Type': 'application/json'}
                    async with session.put(url, json=data, headers=headers) as response:
                        result = await response.json()
                        return {"status_code": response.status, "data": result}
        except asyncio.TimeoutError:
            return {"status_code": 408, "data": {"error": "Request timeout"}}
        except Exception as e:
            return {"status_code": 500, "data": {"error": str(e)}}

    async def test_story_generation_length(self) -> Dict[str, Any]:
        """PRIORITY 1: Test story generation endpoints to verify 300+ word stories"""
        logger.info("🎭 PRIORITY 1: Testing Story Generation Length...")
        
        results = []
        
        for i, prompt in enumerate(self.story_prompts):
            logger.info(f"📖 Testing story prompt {i+1}: '{prompt[:50]}...'")
            
            # Test text conversation endpoint for story generation
            text_data = {
                "session_id": f"{self.test_session_id}_story_{i}",
                "user_id": self.test_user_id,
                "message": prompt
            }
            
            start_time = time.time()
            response = await self.make_request('POST', '/conversations/text', text_data, timeout=45)
            processing_time = time.time() - start_time
            
            if response["status_code"] == 200:
                response_text = response["data"].get("response_text", "")
                word_count = len(response_text.split())
                
                # Check if story meets 300+ word requirement
                meets_requirement = word_count >= 300
                
                result = {
                    "prompt": prompt[:50] + "...",
                    "word_count": word_count,
                    "meets_300_word_requirement": meets_requirement,
                    "response_length_chars": len(response_text),
                    "processing_time": f"{processing_time:.2f}s",
                    "content_type": response["data"].get("content_type", "unknown"),
                    "status": "success" if meets_requirement else "failed",
                    "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                }
                
                logger.info(f"✅ Story {i+1}: {word_count} words ({'✅ PASS' if meets_requirement else '❌ FAIL - Too Short'})")
                
            else:
                result = {
                    "prompt": prompt[:50] + "...",
                    "word_count": 0,
                    "meets_300_word_requirement": False,
                    "processing_time": f"{processing_time:.2f}s",
                    "status": "error",
                    "error": response["data"].get("error", "Unknown error")
                }
                
                logger.error(f"❌ Story {i+1} failed: {response['data'].get('error', 'Unknown error')}")
            
            results.append(result)
            
            # Small delay between requests
            await asyncio.sleep(1)
        
        # Calculate summary statistics
        successful_stories = [r for r in results if r["status"] == "success"]
        stories_meeting_requirement = [r for r in successful_stories if r["meets_300_word_requirement"]]
        
        summary = {
            "total_stories_tested": len(results),
            "successful_generations": len(successful_stories),
            "stories_meeting_300_words": len(stories_meeting_requirement),
            "success_rate": f"{(len(stories_meeting_requirement) / len(results)) * 100:.1f}%",
            "average_word_count": sum(r["word_count"] for r in successful_stories) / len(successful_stories) if successful_stories else 0,
            "detailed_results": results
        }
        
        self.test_results["story_generation_length"] = summary
        return summary

    async def test_story_session_management(self) -> Dict[str, Any]:
        """PRIORITY 2: Test story session creation, tracking, and continuation"""
        logger.info("📚 PRIORITY 2: Testing Story Session Management...")
        
        results = []
        
        # Test 1: Create story session
        logger.info("🔄 Testing story session creation...")
        session_data = {
            "user_id": self.test_user_id,
            "session_type": "story",
            "context": {"story_theme": "adventure"}
        }
        
        response = await self.make_request('POST', '/conversations/session', session_data)
        
        if response["status_code"] == 200:
            session_id = response["data"].get("id")
            results.append({
                "test": "story_session_creation",
                "status": "success",
                "session_id": session_id,
                "details": "Story session created successfully"
            })
            logger.info(f"✅ Story session created: {session_id}")
        else:
            results.append({
                "test": "story_session_creation",
                "status": "failed",
                "error": response["data"].get("error", "Unknown error")
            })
            logger.error(f"❌ Story session creation failed: {response['data'].get('error')}")
            session_id = self.test_session_id  # Fallback
        
        # Test 2: Story continuation logic
        logger.info("🔄 Testing story continuation logic...")
        
        # Start a story
        initial_story_data = {
            "session_id": session_id,
            "user_id": self.test_user_id,
            "message": "Tell me a story about a brave knight"
        }
        
        response = await self.make_request('POST', '/conversations/text', initial_story_data)
        
        if response["status_code"] == 200:
            initial_story = response["data"].get("response_text", "")
            
            # Continue the story
            continuation_data = {
                "session_id": session_id,
                "user_id": self.test_user_id,
                "message": "What happens next in the story?"
            }
            
            await asyncio.sleep(2)  # Brief pause
            continuation_response = await self.make_request('POST', '/conversations/text', continuation_data)
            
            if continuation_response["status_code"] == 200:
                continued_story = continuation_response["data"].get("response_text", "")
                
                # Check if continuation maintains context
                context_maintained = len(continued_story) > 50 and "knight" in continued_story.lower()
                
                results.append({
                    "test": "story_continuation",
                    "status": "success" if context_maintained else "partial",
                    "initial_story_length": len(initial_story.split()),
                    "continuation_length": len(continued_story.split()),
                    "context_maintained": context_maintained,
                    "details": "Story continuation working" if context_maintained else "Context may not be maintained"
                })
                
                logger.info(f"✅ Story continuation: {'Context maintained' if context_maintained else 'Context unclear'}")
            else:
                results.append({
                    "test": "story_continuation",
                    "status": "failed",
                    "error": continuation_response["data"].get("error", "Unknown error")
                })
                logger.error(f"❌ Story continuation failed: {continuation_response['data'].get('error')}")
        else:
            results.append({
                "test": "story_continuation",
                "status": "failed",
                "error": "Initial story generation failed"
            })
            logger.error("❌ Initial story generation failed for continuation test")
        
        # Test 3: Story session retrieval from MongoDB
        logger.info("🔄 Testing story session persistence...")
        
        # This would typically involve checking if sessions are stored in MongoDB
        # For now, we'll test if we can retrieve session context
        context_test_data = {
            "session_id": session_id,
            "user_id": self.test_user_id,
            "message": "Can you remind me what we were talking about?"
        }
        
        response = await self.make_request('POST', '/conversations/text', context_test_data)
        
        if response["status_code"] == 200:
            context_response = response["data"].get("response_text", "")
            context_aware = len(context_response) > 20
            
            results.append({
                "test": "session_persistence",
                "status": "success" if context_aware else "partial",
                "context_aware": context_aware,
                "details": "Session context retrievable" if context_aware else "Limited context awareness"
            })
            
            logger.info(f"✅ Session persistence: {'Working' if context_aware else 'Limited'}")
        else:
            results.append({
                "test": "session_persistence",
                "status": "failed",
                "error": response["data"].get("error", "Unknown error")
            })
            logger.error(f"❌ Session persistence test failed: {response['data'].get('error')}")
        
        summary = {
            "total_tests": len(results),
            "successful_tests": len([r for r in results if r["status"] == "success"]),
            "detailed_results": results
        }
        
        self.test_results["story_session_management"] = summary
        return summary

    async def test_barge_in_integration(self) -> Dict[str, Any]:
        """PRIORITY 3: Test backend barge-in functionality in orchestrator.py"""
        logger.info("🛑 PRIORITY 3: Testing Barge-in Integration...")
        
        results = []
        
        # Test 1: Check if orchestrator has barge-in functionality
        logger.info("🔄 Testing barge-in backend functionality...")
        
        # Test agents status to see if orchestrator is available
        response = await self.make_request('GET', '/agents/status')
        
        if response["status_code"] == 200:
            agents_data = response["data"]
            orchestrator_available = "orchestrator" in str(agents_data).lower()
            
            results.append({
                "test": "orchestrator_availability",
                "status": "success" if orchestrator_available else "failed",
                "orchestrator_detected": orchestrator_available,
                "agents_count": len(agents_data.get("agents", {})) if isinstance(agents_data.get("agents"), dict) else 0
            })
            
            logger.info(f"✅ Orchestrator availability: {'Available' if orchestrator_available else 'Not detected'}")
        else:
            results.append({
                "test": "orchestrator_availability",
                "status": "failed",
                "error": response["data"].get("error", "Unknown error")
            })
            logger.error(f"❌ Orchestrator availability test failed: {response['data'].get('error')}")
        
        # Test 2: Test voice processing with potential barge-in scenarios
        logger.info("🔄 Testing voice processing pipeline for barge-in support...")
        
        # Create a simple audio data for testing (base64 encoded silence)
        # This is a minimal WAV file header + some silence
        test_audio_data = base64.b64encode(b'\x00' * 1024).decode('utf-8')
        
        voice_data = {
            "session_id": self.test_session_id,
            "user_id": self.test_user_id,
            "audio_base64": test_audio_data
        }
        
        # Test voice processing endpoint
        response = await self.make_request('POST', '/voice/process_audio', voice_data, timeout=30)
        
        if response["status_code"] == 200:
            voice_result = response["data"]
            has_interrupt_support = "barge" in str(voice_result).lower() or "interrupt" in str(voice_result).lower()
            
            results.append({
                "test": "voice_processing_barge_in",
                "status": "success",
                "interrupt_support_detected": has_interrupt_support,
                "pipeline_type": voice_result.get("pipeline", "unknown"),
                "processing_successful": True
            })
            
            logger.info(f"✅ Voice processing: Pipeline working, interrupt support: {'Detected' if has_interrupt_support else 'Not explicitly detected'}")
        else:
            # Voice processing might fail due to invalid audio, but we can check the error type
            error_msg = response["data"].get("error", "").lower()
            expected_audio_error = "audio" in error_msg or "format" in error_msg or "decode" in error_msg
            
            results.append({
                "test": "voice_processing_barge_in",
                "status": "partial" if expected_audio_error else "failed",
                "error": response["data"].get("error", "Unknown error"),
                "expected_audio_error": expected_audio_error,
                "details": "Endpoint accessible but audio format issue" if expected_audio_error else "Endpoint failed"
            })
            
            logger.info(f"⚠️ Voice processing: {'Expected audio format error' if expected_audio_error else 'Unexpected error'}")
        
        # Test 3: Check for audio interrupt flags and speaking state management
        logger.info("🔄 Testing speaking state management...")
        
        # Test if we can get session status that might include speaking state
        session_status_response = await self.make_request('GET', f'/ambient/status/{self.test_session_id}')
        
        if session_status_response["status_code"] == 200:
            status_data = session_status_response["data"]
            has_speaking_state = "speaking" in str(status_data).lower() or "state" in str(status_data).lower()
            
            results.append({
                "test": "speaking_state_management",
                "status": "success",
                "speaking_state_detected": has_speaking_state,
                "session_status_available": True
            })
            
            logger.info(f"✅ Speaking state management: {'Detected' if has_speaking_state else 'Basic session tracking'}")
        else:
            results.append({
                "test": "speaking_state_management",
                "status": "partial",
                "error": session_status_response["data"].get("error", "Unknown error"),
                "details": "Session status endpoint not available or session not found"
            })
            
            logger.info("⚠️ Speaking state management: Session status endpoint not accessible")
        
        summary = {
            "total_tests": len(results),
            "successful_tests": len([r for r in results if r["status"] == "success"]),
            "partial_tests": len([r for r in results if r["status"] == "partial"]),
            "detailed_results": results
        }
        
        self.test_results["barge_in_integration"] = summary
        return summary

    async def test_story_streaming_pipeline(self) -> Dict[str, Any]:
        """PRIORITY 4: Test story streaming endpoints and chunked TTS generation"""
        logger.info("🎵 PRIORITY 4: Testing Story Streaming Pipeline...")
        
        results = []
        
        # Test 1: Story streaming endpoint
        logger.info("🔄 Testing POST /api/stories/stream...")
        
        stream_data = {
            "session_id": self.test_session_id,
            "user_id": self.test_user_id,
            "text": "Tell me a complete adventure story about a young explorer"
        }
        
        response = await self.make_request('POST', '/stories/stream', stream_data, timeout=45)
        
        if response["status_code"] == 200:
            stream_result = response["data"]
            
            # Check if streaming response has expected structure
            has_chunks = "chunk" in str(stream_result).lower()
            has_story_mode = stream_result.get("story_mode", False)
            total_words = stream_result.get("total_words", 0)
            
            results.append({
                "test": "story_streaming_endpoint",
                "status": "success",
                "story_mode": has_story_mode,
                "has_chunks": has_chunks,
                "total_words": total_words,
                "meets_word_requirement": total_words >= 300,
                "response_structure": "Complete" if has_chunks and has_story_mode else "Basic"
            })
            
            logger.info(f"✅ Story streaming: {total_words} words, chunks: {'Yes' if has_chunks else 'No'}")
        else:
            results.append({
                "test": "story_streaming_endpoint",
                "status": "failed",
                "error": response["data"].get("error", "Unknown error")
            })
            logger.error(f"❌ Story streaming failed: {response['data'].get('error')}")
        
        # Test 2: Chunked TTS processing
        logger.info("🔄 Testing POST /api/stories/chunk-tts...")
        
        chunk_data = {
            "text": "Once upon a time, in a magical forest far away, there lived a brave little rabbit who dreamed of great adventures.",
            "chunk_id": 0,
            "user_id": self.test_user_id
        }
        
        response = await self.make_request('POST', '/stories/chunk-tts', chunk_data, timeout=30)
        
        if response["status_code"] == 200:
            tts_result = response["data"]
            has_audio = "audio" in str(tts_result).lower()
            audio_generated = len(tts_result.get("audio_base64", "")) > 100 if tts_result.get("audio_base64") else False
            
            results.append({
                "test": "chunked_tts_processing",
                "status": "success",
                "audio_generated": audio_generated,
                "audio_length": len(tts_result.get("audio_base64", "")),
                "chunk_processing": "Working"
            })
            
            logger.info(f"✅ Chunked TTS: Audio generated: {'Yes' if audio_generated else 'No'}")
        else:
            results.append({
                "test": "chunked_tts_processing",
                "status": "failed",
                "error": response["data"].get("error", "Unknown error")
            })
            logger.error(f"❌ Chunked TTS failed: {response['data'].get('error')}")
        
        # Test 3: Story narration endpoint
        logger.info("🔄 Testing POST /api/content/stories/{story_id}/narrate...")
        
        # First get available stories
        stories_response = await self.make_request('GET', '/content/stories')
        
        if stories_response["status_code"] == 200:
            stories_data = stories_response["data"]
            stories = stories_data.get("stories", [])
            
            if stories:
                # Test narration with first story
                story_id = stories[0].get("id", "story_001")
                
                narration_data = {
                    "user_id": self.test_user_id
                }
                
                response = await self.make_request('POST', f'/content/stories/{story_id}/narrate', narration_data, timeout=30)
                
                if response["status_code"] == 200:
                    narration_result = response["data"]
                    has_text = len(narration_result.get("response_text", "")) > 0
                    has_audio = len(narration_result.get("response_audio", "")) > 0
                    
                    results.append({
                        "test": "story_narration_endpoint",
                        "status": "success",
                        "story_id": story_id,
                        "has_response_text": has_text,
                        "has_response_audio": has_audio,
                        "text_length": len(narration_result.get("response_text", "")),
                        "audio_length": len(narration_result.get("response_audio", ""))
                    })
                    
                    logger.info(f"✅ Story narration: Text: {'Yes' if has_text else 'No'}, Audio: {'Yes' if has_audio else 'No'}")
                else:
                    results.append({
                        "test": "story_narration_endpoint",
                        "status": "failed",
                        "story_id": story_id,
                        "error": response["data"].get("error", "Unknown error")
                    })
                    logger.error(f"❌ Story narration failed: {response['data'].get('error')}")
            else:
                results.append({
                    "test": "story_narration_endpoint",
                    "status": "failed",
                    "error": "No stories available for testing"
                })
                logger.error("❌ No stories available for narration testing")
        else:
            results.append({
                "test": "story_narration_endpoint",
                "status": "failed",
                "error": "Could not retrieve stories list"
            })
            logger.error("❌ Could not retrieve stories for narration testing")
        
        summary = {
            "total_tests": len(results),
            "successful_tests": len([r for r in results if r["status"] == "success"]),
            "detailed_results": results
        }
        
        self.test_results["story_streaming_pipeline"] = summary
        return summary

    async def test_voice_processing_integration(self) -> Dict[str, Any]:
        """PRIORITY 5: Test voice processing pipeline with story requests"""
        logger.info("🎤 PRIORITY 5: Testing Voice Processing Integration...")
        
        results = []
        
        # Test 1: Voice personalities endpoint
        logger.info("🔄 Testing voice personalities endpoint...")
        
        response = await self.make_request('GET', '/voice/personalities')
        
        if response["status_code"] == 200:
            personalities = response["data"]
            personality_count = len(personalities) if isinstance(personalities, list) else len(personalities.get("personalities", [])) if isinstance(personalities, dict) else 0
            
            results.append({
                "test": "voice_personalities",
                "status": "success",
                "personality_count": personality_count,
                "personalities_available": personality_count > 0
            })
            
            logger.info(f"✅ Voice personalities: {personality_count} available")
        else:
            results.append({
                "test": "voice_personalities",
                "status": "failed",
                "error": response["data"].get("error", "Unknown error")
            })
            logger.error(f"❌ Voice personalities failed: {response['data'].get('error')}")
        
        # Test 2: TTS generation for story responses
        logger.info("🔄 Testing TTS generation...")
        
        tts_data = {
            "text": "Once upon a time, there was a magical kingdom where all the animals could speak and sing beautiful songs together.",
            "personality": "story_narrator"
        }
        
        response = await self.make_request('POST', '/voice/tts', tts_data, timeout=30)
        
        if response["status_code"] == 200:
            tts_result = response["data"]
            audio_generated = len(tts_result.get("audio_base64", "")) > 100
            
            results.append({
                "test": "tts_generation",
                "status": "success",
                "audio_generated": audio_generated,
                "audio_length": len(tts_result.get("audio_base64", "")),
                "personality_used": tts_result.get("personality", "unknown")
            })
            
            logger.info(f"✅ TTS generation: Audio generated: {'Yes' if audio_generated else 'No'}")
        else:
            results.append({
                "test": "tts_generation",
                "status": "failed",
                "error": response["data"].get("error", "Unknown error")
            })
            logger.error(f"❌ TTS generation failed: {response['data'].get('error')}")
        
        # Test 3: Smart routing for story vs regular requests
        logger.info("🔄 Testing smart routing with voice processing...")
        
        # Create minimal test audio data
        test_audio_data = base64.b64encode(b'\x00' * 1024).decode('utf-8')
        
        voice_data = {
            "session_id": self.test_session_id,
            "user_id": self.test_user_id,
            "audio_base64": test_audio_data
        }
        
        response = await self.make_request('POST', '/voice/process_audio', voice_data, timeout=30)
        
        # Even if it fails due to audio format, we can check if the endpoint is accessible
        if response["status_code"] == 200:
            voice_result = response["data"]
            has_smart_routing = "pipeline" in str(voice_result).lower() or "routing" in str(voice_result).lower()
            
            results.append({
                "test": "smart_routing",
                "status": "success",
                "smart_routing_detected": has_smart_routing,
                "pipeline_info": voice_result.get("pipeline", "unknown"),
                "endpoint_accessible": True
            })
            
            logger.info(f"✅ Smart routing: {'Detected' if has_smart_routing else 'Basic processing'}")
        else:
            # Check if it's an expected audio format error
            error_msg = response["data"].get("error", "").lower()
            audio_format_error = "audio" in error_msg or "format" in error_msg or "decode" in error_msg
            
            results.append({
                "test": "smart_routing",
                "status": "partial" if audio_format_error else "failed",
                "error": response["data"].get("error", "Unknown error"),
                "endpoint_accessible": audio_format_error,
                "details": "Endpoint accessible but requires valid audio" if audio_format_error else "Endpoint failed"
            })
            
            logger.info(f"⚠️ Smart routing: {'Endpoint accessible' if audio_format_error else 'Endpoint failed'}")
        
        summary = {
            "total_tests": len(results),
            "successful_tests": len([r for r in results if r["status"] == "success"]),
            "partial_tests": len([r for r in results if r["status"] == "partial"]),
            "detailed_results": results
        }
        
        self.test_results["voice_processing_integration"] = summary
        return summary

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all priority tests and generate comprehensive report"""
        logger.info("🚀 STARTING COMPREHENSIVE REVIEW PRIORITY TESTING...")
        
        start_time = time.time()
        
        # Create test user profile first
        await self.create_test_user()
        
        # Run all priority tests
        try:
            priority_1 = await self.test_story_generation_length()
            await asyncio.sleep(2)
            
            priority_2 = await self.test_story_session_management()
            await asyncio.sleep(2)
            
            priority_3 = await self.test_barge_in_integration()
            await asyncio.sleep(2)
            
            priority_4 = await self.test_story_streaming_pipeline()
            await asyncio.sleep(2)
            
            priority_5 = await self.test_voice_processing_integration()
            
        except Exception as e:
            logger.error(f"❌ Error during testing: {str(e)}")
        
        total_time = time.time() - start_time
        
        # Generate overall summary
        overall_summary = self.generate_overall_summary(total_time)
        self.test_results["overall_summary"] = overall_summary
        
        logger.info(f"🎯 COMPREHENSIVE TESTING COMPLETED in {total_time:.2f}s")
        
        return self.test_results

    async def create_test_user(self):
        """Create a test user profile for testing"""
        user_data = {
            "name": f"Review Test User {int(time.time())}",
            "age": 8,
            "location": "Test City",
            "parent_email": "test@example.com",
            "timezone": "UTC",
            "language": "english",
            "voice_personality": "friendly_companion",
            "interests": ["stories", "adventures", "animals"],
            "learning_goals": ["creativity", "language"],
            "gender": "prefer_not_to_say",
            "avatar": "rabbit",
            "speech_speed": "normal",
            "energy_level": "balanced"
        }
        
        response = await self.make_request('POST', '/users/profile', user_data)
        
        if response["status_code"] == 200:
            logger.info(f"✅ Test user created: {self.test_user_id}")
        else:
            logger.warning(f"⚠️ Could not create test user: {response['data'].get('error', 'Unknown error')}")

    def generate_overall_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        
        # Calculate success rates for each priority
        priority_results = {}
        
        for priority, data in self.test_results.items():
            if priority != "overall_summary" and isinstance(data, dict):
                total_tests = data.get("total_tests", 0)
                successful_tests = data.get("successful_tests", 0)
                partial_tests = data.get("partial_tests", 0)
                
                if total_tests > 0:
                    success_rate = (successful_tests / total_tests) * 100
                    priority_results[priority] = {
                        "success_rate": f"{success_rate:.1f}%",
                        "successful_tests": successful_tests,
                        "total_tests": total_tests,
                        "partial_tests": partial_tests,
                        "status": "PASS" if success_rate >= 70 else "PARTIAL" if success_rate >= 40 else "FAIL"
                    }
        
        # Overall assessment
        all_success_rates = [float(r["success_rate"].replace('%', '')) for r in priority_results.values()]
        overall_success_rate = sum(all_success_rates) / len(all_success_rates) if all_success_rates else 0
        
        # Critical issues identification
        critical_issues = []
        
        # Check story generation length (Priority 1)
        story_gen_data = self.test_results.get("story_generation_length", {})
        if story_gen_data.get("stories_meeting_300_words", 0) == 0:
            critical_issues.append("CRITICAL: No stories meet 300+ word requirement")
        
        # Check story streaming pipeline (Priority 4)
        streaming_data = self.test_results.get("story_streaming_pipeline", {})
        if streaming_data.get("successful_tests", 0) == 0:
            critical_issues.append("CRITICAL: Story streaming pipeline completely non-functional")
        
        # Check voice processing (Priority 5)
        voice_data = self.test_results.get("voice_processing_integration", {})
        if voice_data.get("successful_tests", 0) == 0:
            critical_issues.append("CRITICAL: Voice processing integration failed")
        
        return {
            "total_testing_time": f"{total_time:.2f}s",
            "overall_success_rate": f"{overall_success_rate:.1f}%",
            "priority_results": priority_results,
            "critical_issues": critical_issues,
            "overall_status": "PASS" if overall_success_rate >= 70 else "PARTIAL" if overall_success_rate >= 40 else "FAIL",
            "recommendations": self.generate_recommendations(priority_results, critical_issues)
        }

    def generate_recommendations(self, priority_results: Dict, critical_issues: List[str]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Story generation recommendations
        story_gen_status = priority_results.get("story_generation_length", {}).get("status", "FAIL")
        if story_gen_status != "PASS":
            recommendations.append("URGENT: Fix story generation to produce 300+ word stories consistently")
        
        # Story streaming recommendations
        streaming_status = priority_results.get("story_streaming_pipeline", {}).get("status", "FAIL")
        if streaming_status != "PASS":
            recommendations.append("HIGH: Implement or fix story streaming pipeline for progressive story delivery")
        
        # Voice processing recommendations
        voice_status = priority_results.get("voice_processing_integration", {}).get("status", "FAIL")
        if voice_status != "PASS":
            recommendations.append("HIGH: Fix voice processing integration and TTS generation")
        
        # Barge-in recommendations
        barge_in_status = priority_results.get("barge_in_integration", {}).get("status", "FAIL")
        if barge_in_status != "PASS":
            recommendations.append("MEDIUM: Implement or enhance barge-in functionality for story interruption")
        
        # Session management recommendations
        session_status = priority_results.get("story_session_management", {}).get("status", "FAIL")
        if session_status != "PASS":
            recommendations.append("MEDIUM: Improve story session management and context persistence")
        
        if not recommendations:
            recommendations.append("All priority areas are functioning well - continue with integration testing")
        
        return recommendations

    def print_detailed_report(self):
        """Print comprehensive test report"""
        print("\n" + "="*80)
        print("🎯 REVIEW PRIORITY BACKEND TESTING REPORT")
        print("="*80)
        
        overall = self.test_results.get("overall_summary", {})
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Success Rate: {overall.get('overall_success_rate', 'N/A')}")
        print(f"   Status: {overall.get('overall_status', 'UNKNOWN')}")
        print(f"   Testing Time: {overall.get('total_testing_time', 'N/A')}")
        
        print(f"\n🎯 PRIORITY RESULTS:")
        priority_results = overall.get("priority_results", {})
        for priority, data in priority_results.items():
            status_emoji = "✅" if data["status"] == "PASS" else "⚠️" if data["status"] == "PARTIAL" else "❌"
            print(f"   {status_emoji} {priority.replace('_', ' ').title()}: {data['success_rate']} ({data['successful_tests']}/{data['total_tests']})")
        
        critical_issues = overall.get("critical_issues", [])
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in critical_issues:
                print(f"   ❌ {issue}")
        
        recommendations = overall.get("recommendations", [])
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "="*80)

async def main():
    """Main testing function"""
    tester = ReviewPriorityBackendTester()
    
    try:
        results = await tester.run_comprehensive_test()
        tester.print_detailed_report()
        
        # Save results to file
        with open('/app/review_priority_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info("📄 Test results saved to review_priority_test_results.json")
        
    except Exception as e:
        logger.error(f"❌ Testing failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())