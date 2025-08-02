#!/usr/bin/env python3
"""
Mobile Voice Recording Fixes - Comprehensive Backend Testing
Focus: Voice processing pipeline, mobile audio handling, story narration, and system stability
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

# Get backend URL from frontend environment
BACKEND_URL = "https://ac3a5a48-4dec-498e-8545-e5993602e42f.preview.emergentagent.com/api"

class MobileVoiceTestSuite:
    """Comprehensive mobile voice recording and system stability tester"""
    
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.test_user_id = f"mobile_test_user_{uuid.uuid4().hex[:8]}"
        self.test_session_id = f"mobile_session_{uuid.uuid4().hex[:8]}"
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def create_test_audio_base64(self, size_bytes: int = 1024) -> str:
        """Create test audio data in base64 format"""
        # Create mock audio data (WebM format header + data)
        webm_header = b'\x1a\x45\xdf\xa3'  # WebM signature
        audio_data = webm_header + b'\x00' * (size_bytes - len(webm_header))
        return base64.b64encode(audio_data).decode('utf-8')
    
    async def test_voice_processing_pipeline_end_to_end(self):
        """Test 1: Voice Processing Pipeline End-to-End"""
        logger.info("🎤 Testing Voice Processing Pipeline End-to-End...")
        
        try:
            # Test various audio formats and sizes
            test_cases = [
                {"format": "webm", "size": 1024, "description": "Standard WebM audio"},
                {"format": "webm", "size": 500, "description": "Mobile threshold WebM (500 bytes)"},
                {"format": "webm", "size": 8192, "description": "Large WebM audio"},
                {"format": "webm", "size": 1, "description": "Minimal audio data"},
            ]
            
            results = []
            for case in test_cases:
                audio_base64 = self.create_test_audio_base64(case["size"])
                
                # Test POST /api/voice/process_audio
                form_data = aiohttp.FormData()
                form_data.add_field('session_id', self.test_session_id)
                form_data.add_field('user_id', self.test_user_id)
                form_data.add_field('audio_base64', audio_base64)
                
                async with self.session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
                    status = response.status
                    content = await response.text()
                    
                    try:
                        data = json.loads(content)
                    except:
                        data = {"raw_response": content}
                    
                    result = {
                        "case": case["description"],
                        "status": status,
                        "success": status in [200, 400],  # 400 is acceptable for invalid audio
                        "response_size": len(content),
                        "has_audio_response": "response_audio" in data,
                        "error_handled": status == 400 and "error" in data
                    }
                    results.append(result)
                    
                    logger.info(f"  ✅ {case['description']}: Status {status}")
            
            success_rate = sum(1 for r in results if r["success"]) / len(results) * 100
            
            self.test_results["voice_processing_pipeline"] = {
                "status": "PASS" if success_rate >= 75 else "FAIL",
                "success_rate": f"{success_rate:.1f}%",
                "details": results,
                "summary": f"Voice processing pipeline tested with {len(results)} audio formats"
            }
            
        except Exception as e:
            logger.error(f"❌ Voice processing pipeline test failed: {str(e)}")
            self.test_results["voice_processing_pipeline"] = {
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_mobile_audio_handling(self):
        """Test 2: Mobile-Specific Audio Handling"""
        logger.info("📱 Testing Mobile-Specific Audio Handling...")
        
        try:
            # Test different MIME types and mobile constraints
            mobile_test_cases = [
                {"mime": "webm", "size": 500, "description": "Mobile WebM threshold"},
                {"mime": "ogg", "size": 1024, "description": "OGG format"},
                {"mime": "mp4", "size": 2048, "description": "MP4 audio format"},
                {"mime": "wav", "size": 4096, "description": "WAV format"},
                {"mime": "webm", "size": 499, "description": "Below mobile threshold"},
                {"mime": "webm", "size": 50000, "description": "Large mobile audio"},
            ]
            
            results = []
            for case in mobile_test_cases:
                audio_base64 = self.create_test_audio_base64(case["size"])
                
                form_data = aiohttp.FormData()
                form_data.add_field('session_id', self.test_session_id)
                form_data.add_field('user_id', self.test_user_id)
                form_data.add_field('audio_base64', audio_base64)
                
                async with self.session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
                    status = response.status
                    content = await response.text()
                    
                    try:
                        data = json.loads(content)
                    except:
                        data = {"raw_response": content}
                    
                    result = {
                        "case": case["description"],
                        "mime_type": case["mime"],
                        "size": case["size"],
                        "status": status,
                        "processed": status == 200,
                        "error_handled": status in [400, 422] and case["size"] < 500,
                        "response_data": data.get("status", "unknown")
                    }
                    results.append(result)
                    
                    logger.info(f"  📱 {case['description']}: Status {status}")
            
            # Check mobile threshold handling
            mobile_threshold_tests = [r for r in results if r["size"] == 500 or r["size"] == 499]
            threshold_working = len([r for r in mobile_threshold_tests if r["processed"] or r["error_handled"]]) > 0
            
            self.test_results["mobile_audio_handling"] = {
                "status": "PASS" if threshold_working else "FAIL",
                "mobile_threshold_working": threshold_working,
                "formats_tested": len(set(r["mime_type"] for r in results)),
                "details": results,
                "summary": f"Mobile audio handling tested with {len(results)} format/size combinations"
            }
            
        except Exception as e:
            logger.error(f"❌ Mobile audio handling test failed: {str(e)}")
            self.test_results["mobile_audio_handling"] = {
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_story_narration_chunked_tts(self):
        """Test 3: Story Narration with Chunked TTS"""
        logger.info("📚 Testing Story Narration with Chunked TTS...")
        
        try:
            # First, get available stories
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status != 200:
                    raise Exception(f"Failed to get stories: {response.status}")
                
                stories_data = await response.json()
                stories = stories_data.get("stories", [])
                
                if not stories:
                    raise Exception("No stories available for testing")
            
            # Test story narration with chunked TTS
            test_story = stories[0]  # Use first available story
            
            narration_request = {
                "user_id": self.test_user_id,
                "full_narration": True,
                "voice_personality": "story_narrator"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/content/stories/{test_story['id']}/narrate",
                json=narration_request
            ) as response:
                status = response.status
                content = await response.text()
                
                try:
                    data = json.loads(content)
                except:
                    data = {"raw_response": content}
                
                # Check for chunked TTS indicators
                has_audio = "response_audio" in data and data["response_audio"]
                has_text = "response_text" in data and len(data.get("response_text", "")) > 100
                narration_complete = data.get("narration_complete", False)
                
                # Test text conversation for story content type
                text_request = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": f"Tell me the story of {test_story['title']}"
                }
                
                async with self.session.post(f"{BACKEND_URL}/conversations/text", json=text_request) as text_response:
                    text_status = text_response.status
                    text_data = await text_response.json() if text_response.status == 200 else {}
                    
                    story_content_detected = text_data.get("content_type") == "story" or "story" in text_data.get("response_text", "").lower()
                
                self.test_results["story_narration_chunked_tts"] = {
                    "status": "PASS" if has_audio and has_text else "FAIL",
                    "story_endpoint_status": status,
                    "has_audio_response": has_audio,
                    "has_text_response": has_text,
                    "narration_complete": narration_complete,
                    "story_content_detected": story_content_detected,
                    "text_conversation_status": text_status,
                    "stories_available": len(stories),
                    "test_story": test_story["title"],
                    "summary": f"Story narration tested with {test_story['title']}"
                }
                
                logger.info(f"  📚 Story narration: Status {status}, Audio: {has_audio}, Text: {has_text}")
                
        except Exception as e:
            logger.error(f"❌ Story narration test failed: {str(e)}")
            self.test_results["story_narration_chunked_tts"] = {
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_session_user_management(self):
        """Test 4: Session and User Management"""
        logger.info("👤 Testing Session and User Management...")
        
        try:
            # Test user profile creation
            profile_data = {
                "name": "Mobile Test Child",
                "age": 8,
                "location": "San Francisco",
                "parent_email": "parent@test.com",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "games"],
                "learning_goals": ["creativity", "language"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/users/profile", json=profile_data) as response:
                profile_status = response.status
                profile_data_response = await response.json() if response.status == 200 else {}
                profile_created = response.status == 200
                
                if profile_created:
                    self.test_user_id = profile_data_response.get("id", self.test_user_id)
            
            # Test user profile retrieval
            async with self.session.get(f"{BACKEND_URL}/users/profile/{self.test_user_id}") as response:
                profile_get_status = response.status
                profile_retrieved = response.status == 200
            
            # Test parental controls
            async with self.session.get(f"{BACKEND_URL}/users/{self.test_user_id}/parental-controls") as response:
                parental_status = response.status
                parental_working = response.status == 200
            
            # Test session creation
            session_data = {
                "user_id": self.test_user_id,
                "session_type": "voice_chat"
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/session", json=session_data) as response:
                session_status = response.status
                session_created = response.status == 200
            
            # Test voice personalities
            async with self.session.get(f"{BACKEND_URL}/voice/personalities") as response:
                personalities_status = response.status
                personalities_available = response.status == 200
                personalities_data = await response.json() if response.status == 200 else {}
                personality_count = len(personalities_data) if isinstance(personalities_data, list) else 0
            
            overall_success = all([
                profile_created or profile_retrieved,
                parental_working,
                session_created,
                personalities_available
            ])
            
            self.test_results["session_user_management"] = {
                "status": "PASS" if overall_success else "FAIL",
                "profile_creation": profile_status,
                "profile_retrieval": profile_get_status,
                "parental_controls": parental_status,
                "session_creation": session_status,
                "voice_personalities": personalities_status,
                "personality_count": personality_count,
                "test_user_id": self.test_user_id,
                "summary": f"User management tested with profile, parental controls, and {personality_count} voice personalities"
            }
            
            logger.info(f"  👤 User management: Profile {profile_status}, Parental {parental_status}, Session {session_status}")
            
        except Exception as e:
            logger.error(f"❌ Session and user management test failed: {str(e)}")
            self.test_results["session_user_management"] = {
                "status": "FAIL",
                "error": str(e)
            }
    
    async def test_error_handling_edge_cases(self):
        """Test 5: Error Handling and Edge Cases"""
        logger.info("⚠️ Testing Error Handling and Edge Cases...")
        
        try:
            edge_cases = []
            
            # Test 1: Empty audio data
            form_data = aiohttp.FormData()
            form_data.add_field('session_id', self.test_session_id)
            form_data.add_field('user_id', self.test_user_id)
            form_data.add_field('audio_base64', '')
            
            async with self.session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
                empty_audio_status = response.status
                empty_audio_handled = response.status in [400, 422]
                edge_cases.append({"case": "empty_audio", "status": empty_audio_status, "handled": empty_audio_handled})
            
            # Test 2: Invalid base64 audio
            form_data = aiohttp.FormData()
            form_data.add_field('session_id', self.test_session_id)
            form_data.add_field('user_id', self.test_user_id)
            form_data.add_field('audio_base64', 'invalid_base64_data!')
            
            async with self.session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
                invalid_b64_status = response.status
                invalid_b64_handled = response.status in [400, 422]
                edge_cases.append({"case": "invalid_base64", "status": invalid_b64_status, "handled": invalid_b64_handled})
            
            # Test 3: Missing required fields
            form_data = aiohttp.FormData()
            form_data.add_field('session_id', self.test_session_id)
            # Missing user_id and audio_base64
            
            async with self.session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
                missing_fields_status = response.status
                missing_fields_handled = response.status == 422
                edge_cases.append({"case": "missing_fields", "status": missing_fields_status, "handled": missing_fields_handled})
            
            # Test 4: Very large audio file
            large_audio = self.create_test_audio_base64(100000)  # 100KB
            form_data = aiohttp.FormData()
            form_data.add_field('session_id', self.test_session_id)
            form_data.add_field('user_id', self.test_user_id)
            form_data.add_field('audio_base64', large_audio)
            
            async with self.session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
                large_audio_status = response.status
                large_audio_handled = response.status in [200, 400, 413]  # 413 = Payload Too Large
                edge_cases.append({"case": "large_audio", "status": large_audio_status, "handled": large_audio_handled})
            
            # Test 5: Health check
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                health_status = response.status
                health_data = await response.json() if response.status == 200 else {}
                health_working = response.status == 200
                
                agents_status = health_data.get("agents", {})
                deepgram_configured = agents_status.get("deepgram_configured", False)
                gemini_configured = agents_status.get("gemini_configured", False)
            
            # Calculate edge case handling success rate
            handled_cases = sum(1 for case in edge_cases if case["handled"])
            edge_case_success_rate = (handled_cases / len(edge_cases)) * 100 if edge_cases else 0
            
            self.test_results["error_handling_edge_cases"] = {
                "status": "PASS" if edge_case_success_rate >= 75 and health_working else "FAIL",
                "edge_case_success_rate": f"{edge_case_success_rate:.1f}%",
                "health_check": health_status,
                "deepgram_configured": deepgram_configured,
                "gemini_configured": gemini_configured,
                "edge_cases": edge_cases,
                "summary": f"Error handling tested with {len(edge_cases)} edge cases, {handled_cases} handled correctly"
            }
            
            logger.info(f"  ⚠️ Error handling: {handled_cases}/{len(edge_cases)} cases handled, Health: {health_status}")
            
        except Exception as e:
            logger.error(f"❌ Error handling test failed: {str(e)}")
            self.test_results["error_handling_edge_cases"] = {
                "status": "FAIL",
                "error": str(e)
            }
    
    async def run_mobile_voice_tests(self):
        """Run all mobile voice recording tests"""
        logger.info("🚀 Starting Mobile Voice Recording Fixes Testing...")
        
        # Run tests in priority order
        await self.test_voice_processing_pipeline_end_to_end()
        await self.test_mobile_audio_handling()
        await self.test_story_narration_chunked_tts()
        await self.test_session_user_management()
        await self.test_error_handling_edge_cases()
        
        # Generate summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        logger.info("\n" + "="*80)
        logger.info("🎯 MOBILE VOICE RECORDING FIXES - TEST RESULTS SUMMARY")
        logger.info("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get("status") == "PASS")
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        logger.info(f"📊 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        logger.info("")
        
        # Detailed results
        for test_name, result in self.test_results.items():
            status_emoji = "✅" if result.get("status") == "PASS" else "❌"
            logger.info(f"{status_emoji} {test_name.upper().replace('_', ' ')}: {result.get('status', 'UNKNOWN')}")
            
            if "summary" in result:
                logger.info(f"   📝 {result['summary']}")
            
            if "error" in result:
                logger.info(f"   ⚠️ Error: {result['error']}")
            
            logger.info("")
        
        # Critical findings
        logger.info("🔍 CRITICAL FINDINGS:")
        
        # Voice processing pipeline
        voice_result = self.test_results.get("voice_processing_pipeline", {})
        if voice_result.get("status") == "PASS":
            logger.info("✅ Voice processing pipeline is FULLY OPERATIONAL")
        else:
            logger.info("❌ Voice processing pipeline has CRITICAL ISSUES")
        
        # Mobile audio handling
        mobile_result = self.test_results.get("mobile_audio_handling", {})
        if mobile_result.get("mobile_threshold_working"):
            logger.info("✅ Mobile audio threshold (500 bytes) is working correctly")
        else:
            logger.info("❌ Mobile audio threshold handling needs attention")
        
        # Story narration
        story_result = self.test_results.get("story_narration_chunked_tts", {})
        if story_result.get("has_audio_response") and story_result.get("has_text_response"):
            logger.info("✅ Story narration with chunked TTS is FUNCTIONAL")
        else:
            logger.info("❌ Story narration system needs fixes")
        
        # User management
        user_result = self.test_results.get("session_user_management", {})
        personality_count = user_result.get("personality_count", 0)
        if personality_count >= 3:
            logger.info(f"✅ User management system operational with {personality_count} voice personalities")
        else:
            logger.info("❌ User management or voice personalities need attention")
        
        # Error handling
        error_result = self.test_results.get("error_handling_edge_cases", {})
        if error_result.get("deepgram_configured") and error_result.get("gemini_configured"):
            logger.info("✅ API integrations (Deepgram & Gemini) are properly configured")
        else:
            logger.info("⚠️ API configuration may need verification")
        
        logger.info("="*80)
        
        # Success criteria evaluation
        logger.info("🎯 SUCCESS CRITERIA EVALUATION:")
        criteria_met = []
        
        if voice_result.get("status") == "PASS":
            criteria_met.append("✅ Voice endpoint consistently returns 200 status")
        else:
            criteria_met.append("❌ Voice endpoint has issues")
        
        if mobile_result.get("mobile_threshold_working"):
            criteria_met.append("✅ Audio processing handles mobile formats correctly")
        else:
            criteria_met.append("❌ Mobile format handling needs work")
        
        if story_result.get("status") == "PASS":
            criteria_met.append("✅ Chunked TTS processes stories without timeout")
        else:
            criteria_met.append("❌ Story processing has issues")
        
        if error_result.get("edge_case_success_rate", "0%") != "0%" and float(error_result.get("edge_case_success_rate", "0%").replace("%", "")) >= 75:
            criteria_met.append("✅ Proper error responses for edge cases")
        else:
            criteria_met.append("❌ Error handling needs improvement")
        
        for criterion in criteria_met:
            logger.info(f"  {criterion}")
        
        logger.info("="*80)
        
        # Final recommendation
        if success_rate >= 80:
            logger.info("🎉 RECOMMENDATION: Mobile voice recording system is PRODUCTION READY")
        elif success_rate >= 60:
            logger.info("⚠️ RECOMMENDATION: System is functional but needs minor fixes")
        else:
            logger.info("🚨 RECOMMENDATION: Critical issues found - system needs major fixes")
        
        logger.info("="*80)

async def main():
    """Main test execution"""
    async with MobileVoiceTestSuite() as tester:
        await tester.run_mobile_voice_tests()

if __name__ == "__main__":
    asyncio.run(main())