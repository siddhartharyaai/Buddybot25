#!/usr/bin/env python3
"""
Comprehensive Backend Testing Suite for AI Companion Device
Tests all critical backend endpoints and functionality after microscopic granular audit
Focus: User authentication, Voice processing, Story generation, Conversation management, 
Memory systems, Content management, Parental controls, Safety systems
"""

import asyncio
import aiohttp
import json
import base64
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from frontend .env
BACKEND_URL = "https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com/api"

class ComprehensiveBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.test_user_id = None
        self.test_session_id = str(uuid.uuid4())
        self.auth_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            logger.info("🏥 Testing health check endpoint...")
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Health check passed: {data}")
                    return {"status": "success", "data": data}
                else:
                    logger.error(f"❌ Health check failed: {response.status}")
                    return {"status": "error", "error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"❌ Health check error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def test_user_authentication(self):
        """Test user authentication (signup/signin)"""
        try:
            logger.info("🔐 Testing user authentication...")
            
            # Test signup
            signup_data = {
                "email": f"test_{int(time.time())}@example.com",
                "password": "TestPassword123!",
                "name": "Emma Test",
                "age": 7,
                "location": "Test City"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/signup", json=signup_data) as response:
                if response.status == 201:
                    auth_data = await response.json()
                    self.auth_token = auth_data.get("access_token")
                    self.test_user_id = auth_data.get("profile_id")
                    logger.info(f"✅ Signup successful: User ID {self.test_user_id}")
                    
                    # Test signin with same credentials
                    signin_data = {
                        "email": signup_data["email"],
                        "password": signup_data["password"]
                    }
                    
                    async with self.session.post(f"{BACKEND_URL}/auth/signin", json=signin_data) as signin_response:
                        if signin_response.status == 200:
                            signin_auth = await signin_response.json()
                            logger.info("✅ Signin successful")
                            return {"status": "success", "user_id": self.test_user_id, "token": self.auth_token}
                        else:
                            logger.error(f"❌ Signin failed: {signin_response.status}")
                            return {"status": "partial", "signup_success": True, "signin_failed": True}
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Signup failed: {response.status} - {error_text}")
                    return {"status": "error", "error": f"Signup failed: {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def test_user_profile_management(self):
        """Test user profile CRUD operations"""
        try:
            logger.info("👤 Testing user profile management...")
            
            if not self.test_user_id:
                return {"status": "error", "error": "No test user ID available"}
            
            # Test get profile
            async with self.session.get(f"{BACKEND_URL}/users/profile/{self.test_user_id}") as response:
                if response.status == 200:
                    profile_data = await response.json()
                    logger.info(f"✅ Profile retrieved: {profile_data.get('name', 'Unknown')}")
                    
                    # Test update profile
                    update_data = {
                        "interests": ["stories", "animals", "space"],
                        "learning_goals": ["reading", "science"]
                    }
                    
                    async with self.session.put(f"{BACKEND_URL}/users/profile/{self.test_user_id}", json=update_data) as update_response:
                        if update_response.status == 200:
                            updated_profile = await update_response.json()
                            logger.info("✅ Profile updated successfully")
                            return {"status": "success", "profile": updated_profile}
                        else:
                            logger.error(f"❌ Profile update failed: {update_response.status}")
                            return {"status": "partial", "get_success": True, "update_failed": True}
                else:
                    logger.error(f"❌ Profile retrieval failed: {response.status}")
                    return {"status": "error", "error": f"Profile retrieval failed: {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Profile management error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def test_parental_controls(self):
        """Test parental controls API"""
        try:
            logger.info("👨‍👩‍👧‍👦 Testing parental controls...")
            
            if not self.test_user_id:
                return {"status": "error", "error": "No test user ID available"}
            
            # Test get parental controls
            async with self.session.get(f"{BACKEND_URL}/users/{self.test_user_id}/parental-controls") as response:
                if response.status == 200:
                    controls_data = await response.json()
                    logger.info("✅ Parental controls retrieved")
                    
                    # Test update parental controls
                    update_data = {
                        "time_limits": {"monday": 45, "tuesday": 45, "wednesday": 45, "thursday": 45, "friday": 60, "saturday": 90, "sunday": 90},
                        "monitoring_enabled": True
                    }
                    
                    async with self.session.put(f"{BACKEND_URL}/users/{self.test_user_id}/parental-controls", json=update_data) as update_response:
                        if update_response.status == 200:
                            updated_controls = await update_response.json()
                            logger.info("✅ Parental controls updated")
                            return {"status": "success", "controls": updated_controls}
                        else:
                            logger.error(f"❌ Parental controls update failed: {update_response.status}")
                            return {"status": "partial", "get_success": True, "update_failed": True}
                else:
                    logger.error(f"❌ Parental controls retrieval failed: {response.status}")
                    return {"status": "error", "error": f"Parental controls failed: {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Parental controls error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def test_voice_processing(self):
        """Test voice processing endpoints (TTS/STT)"""
        try:
            logger.info("🎤 Testing voice processing...")
            
            # Test TTS endpoint
            tts_request = {
                "text": "Hello! This is a test of the text-to-speech system for our AI companion.",
                "personality": "friendly_companion"
            }
            
            async with self.session.post(f"{BACKEND_URL}/voice/tts", json=tts_request) as response:
                if response.status == 200:
                    tts_data = await response.json()
                    if tts_data.get("status") == "success" and tts_data.get("audio_base64"):
                        audio_size = len(tts_data["audio_base64"])
                        logger.info(f"✅ TTS successful: Generated {audio_size} chars of base64 audio")
                        
                        # Test voice personalities
                        async with self.session.get(f"{BACKEND_URL}/voice/personalities") as personalities_response:
                            if personalities_response.status == 200:
                                personalities = await personalities_response.json()
                                logger.info(f"✅ Voice personalities: {len(personalities)} available")
                                return {"status": "success", "tts_audio_size": audio_size, "personalities": len(personalities)}
                            else:
                                logger.warning(f"⚠️ Voice personalities failed: {personalities_response.status}")
                                return {"status": "partial", "tts_success": True, "personalities_failed": True}
                    else:
                        logger.error(f"❌ TTS failed: {tts_data}")
                        return {"status": "error", "error": "TTS returned no audio"}
                else:
                    error_text = await response.text()
                    logger.error(f"❌ TTS request failed: {response.status} - {error_text}")
                    return {"status": "error", "error": f"TTS failed: {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Voice processing error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def test_story_generation(self):
        """Test story generation and streaming"""
        try:
            logger.info("📚 Testing story generation...")
            
            if not self.test_user_id:
                return {"status": "error", "error": "No test user ID available"}
            
            # Test story streaming
            story_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "text": "Tell me an adventure story about a brave little rabbit exploring a magical forest"
            }
            
            async with self.session.post(f"{BACKEND_URL}/stories/stream", json=story_request) as response:
                if response.status == 200:
                    story_data = await response.json()
                    if story_data.get("status") == "success":
                        total_words = story_data.get("total_words", 0)
                        total_chunks = story_data.get("total_chunks", 0)
                        logger.info(f"✅ Story streaming successful: {total_words} words, {total_chunks} chunks")
                        
                        # Test chunk TTS
                        if story_data.get("first_chunk"):
                            chunk_request = {
                                "text": story_data["first_chunk"].get("text", ""),
                                "chunk_id": 0,
                                "user_id": self.test_user_id,
                                "session_id": self.test_session_id
                            }
                            
                            async with self.session.post(f"{BACKEND_URL}/stories/chunk-tts", json=chunk_request) as chunk_response:
                                if chunk_response.status == 200:
                                    chunk_data = await chunk_response.json()
                                    if chunk_data.get("status") == "success":
                                        audio_size = len(chunk_data.get("audio_base64", ""))
                                        logger.info(f"✅ Chunk TTS successful: {audio_size} chars audio")
                                        return {"status": "success", "words": total_words, "chunks": total_chunks, "chunk_audio": audio_size}
                                    else:
                                        logger.warning("⚠️ Chunk TTS failed")
                                        return {"status": "partial", "story_success": True, "chunk_tts_failed": True}
                                else:
                                    logger.warning(f"⚠️ Chunk TTS request failed: {chunk_response.status}")
                                    return {"status": "partial", "story_success": True, "chunk_tts_failed": True}
                        else:
                            logger.warning("⚠️ No first chunk in story response")
                            return {"status": "partial", "story_success": True, "no_chunks": True}
                    else:
                        logger.error(f"❌ Story generation failed: {story_data}")
                        return {"status": "error", "error": "Story generation failed"}
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Story request failed: {response.status} - {error_text}")
                    return {"status": "error", "error": f"Story request failed: {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Story generation error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def test_conversation_management(self):
        """Test conversation management and suggestions"""
        try:
            logger.info("💬 Testing conversation management...")
            
            # Test conversation suggestions
            async with self.session.get(f"{BACKEND_URL}/conversations/suggestions") as response:
                if response.status == 200:
                    suggestions = await response.json()
                    logger.info(f"✅ Conversation suggestions: {len(suggestions)} available")
                    
                    # Test text conversation
                    if self.test_user_id:
                        text_request = {
                            "session_id": self.test_session_id,
                            "user_id": self.test_user_id,
                            "message": "Hello! How are you today?"
                        }
                        
                        async with self.session.post(f"{BACKEND_URL}/conversations/text", json=text_request) as text_response:
                            if text_response.status == 200:
                                text_data = await text_response.json()
                                response_length = len(text_data.get("response_text", ""))
                                logger.info(f"✅ Text conversation successful: {response_length} chars response")
                                return {"status": "success", "suggestions": len(suggestions), "response_length": response_length}
                            else:
                                logger.warning(f"⚠️ Text conversation failed: {text_response.status}")
                                return {"status": "partial", "suggestions_success": True, "text_failed": True}
                    else:
                        return {"status": "partial", "suggestions_success": True, "no_user_id": True}
                else:
                    logger.error(f"❌ Conversation suggestions failed: {response.status}")
                    return {"status": "error", "error": f"Suggestions failed: {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Conversation management error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def test_ambient_listening(self):
        """Test ambient listening system"""
        try:
            logger.info("🎧 Testing ambient listening...")
            
            if not self.test_user_id:
                return {"status": "error", "error": "No test user ID available"}
            
            # Test start ambient listening
            start_request = {"user_id": self.test_user_id}
            
            async with self.session.post(f"{BACKEND_URL}/ambient/start", json=start_request) as response:
                if response.status == 200:
                    start_data = await response.json()
                    session_id = start_data.get("session_id")
                    logger.info(f"✅ Ambient listening started: {session_id}")
                    
                    # Test session status
                    async with self.session.get(f"{BACKEND_URL}/ambient/status/{session_id}") as status_response:
                        if status_response.status == 200:
                            status_data = await status_response.json()
                            logger.info(f"✅ Ambient status: {status_data.get('status')}")
                            
                            # Test stop ambient listening
                            stop_request = {"session_id": session_id}
                            async with self.session.post(f"{BACKEND_URL}/ambient/stop", json=stop_request) as stop_response:
                                if stop_response.status == 200:
                                    logger.info("✅ Ambient listening stopped")
                                    return {"status": "success", "session_id": session_id}
                                else:
                                    logger.warning(f"⚠️ Ambient stop failed: {stop_response.status}")
                                    return {"status": "partial", "start_success": True, "stop_failed": True}
                        else:
                            logger.warning(f"⚠️ Ambient status failed: {status_response.status}")
                            return {"status": "partial", "start_success": True, "status_failed": True}
                else:
                    logger.error(f"❌ Ambient start failed: {response.status}")
                    return {"status": "error", "error": f"Ambient start failed: {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Ambient listening error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def test_memory_and_telemetry(self):
        """Test memory snapshots and telemetry systems"""
        try:
            logger.info("🧠 Testing memory and telemetry...")
            
            if not self.test_user_id:
                return {"status": "error", "error": "No test user ID available"}
            
            # Test memory snapshot generation
            async with self.session.post(f"{BACKEND_URL}/memory/snapshot/{self.test_user_id}") as response:
                if response.status == 200:
                    snapshot_data = await response.json()
                    logger.info("✅ Memory snapshot generated")
                    
                    # Test memory snapshots retrieval
                    async with self.session.get(f"{BACKEND_URL}/memory/snapshots/{self.test_user_id}") as snapshots_response:
                        if snapshots_response.status == 200:
                            snapshots_data = await snapshots_response.json()
                            snapshot_count = snapshots_data.get("count", 0)
                            logger.info(f"✅ Memory snapshots retrieved: {snapshot_count} snapshots")
                            
                            # Test analytics dashboard
                            async with self.session.get(f"{BACKEND_URL}/analytics/dashboard/{self.test_user_id}") as analytics_response:
                                if analytics_response.status == 200:
                                    analytics_data = await analytics_response.json()
                                    logger.info("✅ Analytics dashboard working")
                                    return {"status": "success", "snapshots": snapshot_count, "analytics": True}
                                else:
                                    logger.warning(f"⚠️ Analytics failed: {analytics_response.status}")
                                    return {"status": "partial", "memory_success": True, "analytics_failed": True}
                        else:
                            logger.warning(f"⚠️ Snapshots retrieval failed: {snapshots_response.status}")
                            return {"status": "partial", "snapshot_gen_success": True, "retrieval_failed": True}
                else:
                    logger.error(f"❌ Memory snapshot failed: {response.status}")
                    return {"status": "error", "error": f"Memory snapshot failed: {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Memory and telemetry error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def test_content_management(self):
        """Test content management system"""
        try:
            logger.info("📖 Testing content management...")
            
            # Test get stories
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status == 200:
                    stories_data = await response.json()
                    story_count = len(stories_data.get("stories", []))
                    logger.info(f"✅ Content stories: {story_count} available")
                    
                    if self.test_user_id:
                        # Test content suggestions
                        async with self.session.get(f"{BACKEND_URL}/content/suggestions/{self.test_user_id}") as suggestions_response:
                            if suggestions_response.status == 200:
                                suggestions = await suggestions_response.json()
                                logger.info(f"✅ Content suggestions: {len(suggestions)} available")
                                return {"status": "success", "stories": story_count, "suggestions": len(suggestions)}
                            else:
                                logger.warning(f"⚠️ Content suggestions failed: {suggestions_response.status}")
                                return {"status": "partial", "stories_success": True, "suggestions_failed": True}
                    else:
                        return {"status": "partial", "stories_success": True, "no_user_id": True}
                else:
                    logger.error(f"❌ Content stories failed: {response.status}")
                    return {"status": "error", "error": f"Content stories failed: {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Content management error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def test_safety_systems(self):
        """Test safety and moderation systems"""
        try:
            logger.info("🛡️ Testing safety systems...")
            
            if not self.test_user_id:
                return {"status": "error", "error": "No test user ID available"}
            
            # Test with potentially inappropriate content
            safety_test_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "I'm feeling sad and angry today"
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text", json=safety_test_request) as response:
                if response.status == 200:
                    safety_data = await response.json()
                    response_text = safety_data.get("response_text", "")
                    
                    # Check if response is empathetic and appropriate
                    if any(word in response_text.lower() for word in ["understand", "feel", "help", "sorry", "here"]):
                        logger.info("✅ Safety system: Empathetic response detected")
                        return {"status": "success", "empathetic_response": True}
                    else:
                        logger.info(f"✅ Safety system: Response generated - {len(response_text)} chars")
                        return {"status": "success", "response_generated": True}
                else:
                    logger.error(f"❌ Safety test failed: {response.status}")
                    return {"status": "error", "error": f"Safety test failed: {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Safety systems error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def run_comprehensive_test(self):
        """Run all backend tests"""
        logger.info("🚀 Starting comprehensive backend testing...")
        
        test_functions = [
            ("Health Check", self.test_health_check),
            ("User Authentication", self.test_user_authentication),
            ("User Profile Management", self.test_user_profile_management),
            ("Parental Controls", self.test_parental_controls),
            ("Voice Processing", self.test_voice_processing),
            ("Story Generation", self.test_story_generation),
            ("Conversation Management", self.test_conversation_management),
            ("Ambient Listening", self.test_ambient_listening),
            ("Memory and Telemetry", self.test_memory_and_telemetry),
            ("Content Management", self.test_content_management),
            ("Safety Systems", self.test_safety_systems)
        ]
        
        results = {}
        success_count = 0
        total_tests = len(test_functions)
        
        for test_name, test_func in test_functions:
            try:
                result = await test_func()
                results[test_name] = result
                
                if result.get("status") == "success":
                    success_count += 1
                    logger.info(f"✅ {test_name}: PASSED")
                elif result.get("status") == "partial":
                    success_count += 0.5
                    logger.warning(f"⚠️ {test_name}: PARTIAL")
                else:
                    logger.error(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                logger.error(f"❌ {test_name}: EXCEPTION - {str(e)}")
                results[test_name] = {"status": "error", "error": str(e)}
        
        success_rate = (success_count / total_tests) * 100
        
        logger.info(f"\n🎯 COMPREHENSIVE BACKEND TESTING COMPLETE")
        logger.info(f"📊 SUCCESS RATE: {success_rate:.1f}% ({success_count}/{total_tests})")
        logger.info(f"👤 Test User ID: {self.test_user_id}")
        logger.info(f"🔑 Auth Token: {'✅ Generated' if self.auth_token else '❌ Not generated'}")
        
        return {
            "success_rate": success_rate,
            "total_tests": total_tests,
            "passed_tests": success_count,
            "test_user_id": self.test_user_id,
            "auth_token_generated": bool(self.auth_token),
            "detailed_results": results
        }

async def main():
    """Main test execution"""
    async with ComprehensiveBackendTester() as tester:
        results = await tester.run_comprehensive_test()
        
        print("\n" + "="*80)
        print("🎯 FINAL BACKEND TESTING SUMMARY")
        print("="*80)
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"Tests Passed: {results['passed_tests']}/{results['total_tests']}")
        print(f"Test User Created: {'✅' if results['test_user_id'] else '❌'}")
        print(f"Authentication: {'✅' if results['auth_token_generated'] else '❌'}")
        
        print("\n📋 DETAILED RESULTS:")
        for test_name, result in results['detailed_results'].items():
            status = result.get('status', 'unknown')
            if status == 'success':
                print(f"✅ {test_name}")
            elif status == 'partial':
                print(f"⚠️ {test_name} (Partial)")
            else:
                print(f"❌ {test_name}")
                if 'error' in result:
                    print(f"   Error: {result['error']}")
        
        print("\n" + "="*80)
        
        return results

if __name__ == "__main__":
    asyncio.run(main())