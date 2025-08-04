#!/usr/bin/env python3
"""
FOCUSED VOICE PROCESSING TESTING
Target: Get Voice Processing from 85% to 100% operational

CRITICAL TESTING AREAS:
1. Voice Personalities Endpoint - HTTP 500 errors
2. Ambient Listening Endpoints - 404 errors  
3. Progressive TTS Features - implementation gaps
4. Voice Processing Pipeline - STT → Processing → TTS
5. Audio Format Support - different formats
6. Voice Conversation Endpoint - functionality testing
"""

import asyncio
import aiohttp
import base64
import json
import logging
import time
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get backend URL from frontend .env
def get_backend_url():
    frontend_env_path = Path("/app/frontend/.env")
    if frontend_env_path.exists():
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    return "http://localhost:8001"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

class VoiceProcessingTester:
    def __init__(self):
        self.session = None
        self.test_results = {
            "voice_personalities": {"status": "pending", "details": []},
            "ambient_listening": {"status": "pending", "details": []},
            "progressive_tts": {"status": "pending", "details": []},
            "voice_pipeline": {"status": "pending", "details": []},
            "audio_formats": {"status": "pending", "details": []},
            "voice_conversation": {"status": "pending", "details": []}
        }
        self.test_user_id = "voice_test_user_001"
        self.test_session_id = "voice_session_001"

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def generate_test_audio_base64(self, format_type="wav"):
        """Generate minimal test audio data in base64 format"""
        if format_type == "wav":
            # Minimal WAV header + silence (44 bytes header + 1000 bytes data)
            wav_header = b'RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00'
            silence_data = b'\x80' * 1000  # 1000 bytes of silence
            audio_data = wav_header + silence_data
        elif format_type == "webm":
            # Minimal WebM container with Opus audio
            webm_data = b'\x1a\x45\xdf\xa3' + b'\x00' * 100  # Simplified WebM header
            audio_data = webm_data
        else:
            # Default to raw PCM
            audio_data = b'\x00' * 1000
        
        return base64.b64encode(audio_data).decode('utf-8')

    async def test_voice_personalities_endpoint(self):
        """Test 1: Voice Personalities Endpoint - HTTP 500 errors"""
        logger.info("🎭 TESTING: Voice Personalities Endpoint")
        
        try:
            async with self.session.get(f"{API_BASE}/voice/personalities") as response:
                status_code = response.status
                response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                
                if status_code == 200:
                    self.test_results["voice_personalities"]["status"] = "✅ WORKING"
                    self.test_results["voice_personalities"]["details"].append(f"SUCCESS: Status {status_code}, Response: {response_data}")
                    logger.info(f"✅ Voice personalities endpoint working: {len(response_data) if isinstance(response_data, list) else 'N/A'} personalities")
                elif status_code == 500:
                    self.test_results["voice_personalities"]["status"] = "❌ HTTP 500 ERROR"
                    self.test_results["voice_personalities"]["details"].append(f"CRITICAL: HTTP 500 error - {response_data}")
                    logger.error(f"❌ Voice personalities endpoint returning HTTP 500: {response_data}")
                else:
                    self.test_results["voice_personalities"]["status"] = f"❌ HTTP {status_code}"
                    self.test_results["voice_personalities"]["details"].append(f"ERROR: Status {status_code}, Response: {response_data}")
                    logger.error(f"❌ Voice personalities endpoint error {status_code}: {response_data}")
                    
        except Exception as e:
            self.test_results["voice_personalities"]["status"] = "❌ EXCEPTION"
            self.test_results["voice_personalities"]["details"].append(f"EXCEPTION: {str(e)}")
            logger.error(f"❌ Voice personalities endpoint exception: {str(e)}")

    async def test_ambient_listening_endpoints(self):
        """Test 2: Ambient Listening Endpoints - 404 errors"""
        logger.info("🎧 TESTING: Ambient Listening Endpoints")
        
        endpoints = [
            ("/ambient/start", "POST", {"user_id": self.test_user_id}),
            ("/ambient/stop", "POST", {"session_id": self.test_session_id}),
            ("/ambient/status", "GET", None),
            (f"/ambient/status/{self.test_session_id}", "GET", None)
        ]
        
        ambient_results = []
        
        for endpoint, method, data in endpoints:
            try:
                url = f"{API_BASE}{endpoint}"
                
                if method == "POST":
                    async with self.session.post(url, json=data) as response:
                        status_code = response.status
                        response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                elif method == "GET":
                    async with self.session.get(url) as response:
                        status_code = response.status
                        response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                
                if status_code == 404:
                    ambient_results.append(f"❌ 404 ERROR: {endpoint} - Endpoint not found")
                    logger.error(f"❌ Ambient endpoint 404: {endpoint}")
                elif status_code in [200, 201]:
                    ambient_results.append(f"✅ SUCCESS: {endpoint} - Status {status_code}")
                    logger.info(f"✅ Ambient endpoint working: {endpoint}")
                else:
                    ambient_results.append(f"⚠️ STATUS {status_code}: {endpoint} - {response_data}")
                    logger.warning(f"⚠️ Ambient endpoint status {status_code}: {endpoint}")
                    
            except Exception as e:
                ambient_results.append(f"❌ EXCEPTION: {endpoint} - {str(e)}")
                logger.error(f"❌ Ambient endpoint exception {endpoint}: {str(e)}")
        
        # Determine overall status
        if any("❌ 404 ERROR" in result for result in ambient_results):
            self.test_results["ambient_listening"]["status"] = "❌ 404 ERRORS FOUND"
        elif any("✅ SUCCESS" in result for result in ambient_results):
            self.test_results["ambient_listening"]["status"] = "✅ PARTIALLY WORKING"
        else:
            self.test_results["ambient_listening"]["status"] = "❌ ALL FAILED"
            
        self.test_results["ambient_listening"]["details"] = ambient_results

    async def test_progressive_tts_features(self):
        """Test 3: Progressive TTS Features - implementation gaps"""
        logger.info("🎵 TESTING: Progressive TTS Features")
        
        tts_tests = [
            # Basic TTS
            {
                "endpoint": "/voice/tts",
                "data": {"text": "Hello, this is a basic TTS test.", "personality": "friendly_companion"},
                "test_name": "Basic TTS"
            },
            # Streaming TTS
            {
                "endpoint": "/voice/tts/streaming", 
                "data": {"text": "This is a longer text for streaming TTS testing. It should be processed in chunks for better performance and user experience.", "personality": "friendly_companion"},
                "test_name": "Streaming TTS"
            },
            # Chunk TTS
            {
                "endpoint": "/voice/tts/chunk",
                "data": {"text": "This is a chunk of text for TTS processing.", "personality": "story_narrator"},
                "test_name": "Chunk TTS"
            }
        ]
        
        tts_results = []
        
        for test in tts_tests:
            try:
                url = f"{API_BASE}{test['endpoint']}"
                async with self.session.post(url, json=test["data"]) as response:
                    status_code = response.status
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                    
                    if status_code == 200 and isinstance(response_data, dict):
                        if "audio_base64" in response_data or "status" in response_data:
                            tts_results.append(f"✅ {test['test_name']}: Working - Status {status_code}")
                            logger.info(f"✅ {test['test_name']} working")
                        else:
                            tts_results.append(f"⚠️ {test['test_name']}: Incomplete response - {response_data}")
                            logger.warning(f"⚠️ {test['test_name']} incomplete response")
                    else:
                        tts_results.append(f"❌ {test['test_name']}: Failed - Status {status_code}, Response: {response_data}")
                        logger.error(f"❌ {test['test_name']} failed: {status_code}")
                        
            except Exception as e:
                tts_results.append(f"❌ {test['test_name']}: Exception - {str(e)}")
                logger.error(f"❌ {test['test_name']} exception: {str(e)}")
        
        # Determine overall status
        success_count = sum(1 for result in tts_results if "✅" in result)
        if success_count == len(tts_tests):
            self.test_results["progressive_tts"]["status"] = "✅ ALL WORKING"
        elif success_count > 0:
            self.test_results["progressive_tts"]["status"] = f"⚠️ PARTIAL ({success_count}/{len(tts_tests)})"
        else:
            self.test_results["progressive_tts"]["status"] = "❌ ALL FAILED"
            
        self.test_results["progressive_tts"]["details"] = tts_results

    async def test_voice_processing_pipeline(self):
        """Test 4: Voice Processing Pipeline - STT → Processing → TTS"""
        logger.info("🔄 TESTING: Complete Voice Processing Pipeline")
        
        pipeline_tests = [
            {
                "endpoint": "/voice/process_audio",
                "test_name": "Complete Voice Pipeline",
                "audio_format": "wav"
            },
            {
                "endpoint": "/conversations/voice", 
                "test_name": "Voice Conversation Pipeline",
                "audio_format": "wav"
            }
        ]
        
        pipeline_results = []
        
        for test in pipeline_tests:
            try:
                # Generate test audio
                test_audio = self.generate_test_audio_base64(test["audio_format"])
                
                # Prepare form data
                form_data = aiohttp.FormData()
                form_data.add_field('session_id', self.test_session_id)
                form_data.add_field('user_id', self.test_user_id)
                form_data.add_field('audio_base64', test_audio)
                
                url = f"{API_BASE}{test['endpoint']}"
                async with self.session.post(url, data=form_data) as response:
                    status_code = response.status
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                    
                    if status_code == 200:
                        # Check for complete pipeline response
                        if isinstance(response_data, dict):
                            has_transcript = "transcript" in response_data
                            has_response_text = "response_text" in response_data  
                            has_response_audio = "response_audio" in response_data
                            
                            pipeline_score = sum([has_transcript, has_response_text, has_response_audio])
                            
                            if pipeline_score == 3:
                                pipeline_results.append(f"✅ {test['test_name']}: Complete pipeline working (STT+LLM+TTS)")
                                logger.info(f"✅ {test['test_name']} complete pipeline working")
                            elif pipeline_score >= 2:
                                pipeline_results.append(f"⚠️ {test['test_name']}: Partial pipeline ({pipeline_score}/3 components)")
                                logger.warning(f"⚠️ {test['test_name']} partial pipeline")
                            else:
                                pipeline_results.append(f"❌ {test['test_name']}: Pipeline broken ({pipeline_score}/3 components)")
                                logger.error(f"❌ {test['test_name']} pipeline broken")
                        else:
                            pipeline_results.append(f"❌ {test['test_name']}: Invalid response format")
                            logger.error(f"❌ {test['test_name']} invalid response")
                    else:
                        pipeline_results.append(f"❌ {test['test_name']}: HTTP {status_code} - {response_data}")
                        logger.error(f"❌ {test['test_name']} HTTP {status_code}")
                        
            except Exception as e:
                pipeline_results.append(f"❌ {test['test_name']}: Exception - {str(e)}")
                logger.error(f"❌ {test['test_name']} exception: {str(e)}")
        
        # Determine overall status
        success_count = sum(1 for result in pipeline_results if "✅" in result)
        if success_count == len(pipeline_tests):
            self.test_results["voice_pipeline"]["status"] = "✅ COMPLETE PIPELINE WORKING"
        elif success_count > 0:
            self.test_results["voice_pipeline"]["status"] = f"⚠️ PARTIAL PIPELINE ({success_count}/{len(pipeline_tests)})"
        else:
            self.test_results["voice_pipeline"]["status"] = "❌ PIPELINE BROKEN"
            
        self.test_results["voice_pipeline"]["details"] = pipeline_results

    async def test_audio_format_support(self):
        """Test 5: Audio Format Support - different formats"""
        logger.info("🎧 TESTING: Audio Format Support")
        
        audio_formats = ["wav", "webm", "raw"]
        format_results = []
        
        for audio_format in audio_formats:
            try:
                # Generate test audio in different formats
                test_audio = self.generate_test_audio_base64(audio_format)
                
                # Test with voice processing endpoint
                form_data = aiohttp.FormData()
                form_data.add_field('session_id', self.test_session_id)
                form_data.add_field('user_id', self.test_user_id)
                form_data.add_field('audio_base64', test_audio)
                
                url = f"{API_BASE}/voice/process_audio"
                async with self.session.post(url, data=form_data) as response:
                    status_code = response.status
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                    
                    if status_code == 200:
                        format_results.append(f"✅ {audio_format.upper()}: Supported - Status {status_code}")
                        logger.info(f"✅ Audio format {audio_format} supported")
                    elif status_code == 400:
                        format_results.append(f"❌ {audio_format.upper()}: Not supported - Status {status_code}")
                        logger.warning(f"❌ Audio format {audio_format} not supported")
                    else:
                        format_results.append(f"⚠️ {audio_format.upper()}: Error - Status {status_code}")
                        logger.error(f"⚠️ Audio format {audio_format} error: {status_code}")
                        
            except Exception as e:
                format_results.append(f"❌ {audio_format.upper()}: Exception - {str(e)}")
                logger.error(f"❌ Audio format {audio_format} exception: {str(e)}")
        
        # Determine overall status
        supported_count = sum(1 for result in format_results if "✅" in result)
        if supported_count == len(audio_formats):
            self.test_results["audio_formats"]["status"] = "✅ ALL FORMATS SUPPORTED"
        elif supported_count > 0:
            self.test_results["audio_formats"]["status"] = f"⚠️ PARTIAL SUPPORT ({supported_count}/{len(audio_formats)})"
        else:
            self.test_results["audio_formats"]["status"] = "❌ NO FORMAT SUPPORT"
            
        self.test_results["audio_formats"]["details"] = format_results

    async def test_voice_conversation_endpoint(self):
        """Test 6: Voice Conversation Endpoint - functionality testing"""
        logger.info("💬 TESTING: Voice Conversation Endpoint")
        
        conversation_tests = [
            # Test with JSON payload
            {
                "method": "json",
                "data": {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "audio_base64": self.generate_test_audio_base64("wav")
                },
                "test_name": "JSON Voice Conversation"
            },
            # Test with different audio
            {
                "method": "json", 
                "data": {
                    "session_id": f"{self.test_session_id}_2",
                    "user_id": self.test_user_id,
                    "audio_base64": self.generate_test_audio_base64("webm")
                },
                "test_name": "WebM Voice Conversation"
            }
        ]
        
        conversation_results = []
        
        for test in conversation_tests:
            try:
                url = f"{API_BASE}/conversations/voice"
                
                if test["method"] == "json":
                    async with self.session.post(url, json=test["data"]) as response:
                        status_code = response.status
                        response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                
                if status_code == 200:
                    # Check response completeness
                    if isinstance(response_data, dict):
                        has_status = "status" in response_data
                        has_transcript = "transcript" in response_data
                        has_response = "response_text" in response_data
                        
                        completeness = sum([has_status, has_transcript, has_response])
                        
                        if completeness >= 2:
                            conversation_results.append(f"✅ {test['test_name']}: Working ({completeness}/3 fields)")
                            logger.info(f"✅ {test['test_name']} working")
                        else:
                            conversation_results.append(f"⚠️ {test['test_name']}: Incomplete ({completeness}/3 fields)")
                            logger.warning(f"⚠️ {test['test_name']} incomplete")
                    else:
                        conversation_results.append(f"❌ {test['test_name']}: Invalid response format")
                        logger.error(f"❌ {test['test_name']} invalid response")
                else:
                    conversation_results.append(f"❌ {test['test_name']}: HTTP {status_code} - {response_data}")
                    logger.error(f"❌ {test['test_name']} HTTP {status_code}")
                    
            except Exception as e:
                conversation_results.append(f"❌ {test['test_name']}: Exception - {str(e)}")
                logger.error(f"❌ {test['test_name']} exception: {str(e)}")
        
        # Determine overall status
        success_count = sum(1 for result in conversation_results if "✅" in result)
        if success_count == len(conversation_tests):
            self.test_results["voice_conversation"]["status"] = "✅ FULLY FUNCTIONAL"
        elif success_count > 0:
            self.test_results["voice_conversation"]["status"] = f"⚠️ PARTIAL ({success_count}/{len(conversation_tests)})"
        else:
            self.test_results["voice_conversation"]["status"] = "❌ NOT FUNCTIONAL"
            
        self.test_results["voice_conversation"]["details"] = conversation_results

    async def run_all_tests(self):
        """Run all voice processing tests"""
        logger.info("🚀 STARTING FOCUSED VOICE PROCESSING TESTING")
        logger.info(f"🔗 Backend URL: {BASE_URL}")
        
        # Run all tests
        await self.test_voice_personalities_endpoint()
        await self.test_ambient_listening_endpoints()
        await self.test_progressive_tts_features()
        await self.test_voice_processing_pipeline()
        await self.test_audio_format_support()
        await self.test_voice_conversation_endpoint()
        
        # Generate summary report
        self.generate_summary_report()

    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        logger.info("\n" + "="*80)
        logger.info("🎯 FOCUSED VOICE PROCESSING TEST RESULTS")
        logger.info("="*80)
        
        total_tests = len(self.test_results)
        working_tests = sum(1 for result in self.test_results.values() if "✅" in result["status"])
        partial_tests = sum(1 for result in self.test_results.values() if "⚠️" in result["status"])
        failed_tests = sum(1 for result in self.test_results.values() if "❌" in result["status"])
        
        logger.info(f"📊 OVERALL RESULTS: {working_tests}/{total_tests} fully working, {partial_tests} partial, {failed_tests} failed")
        
        # Detailed results
        for test_name, result in self.test_results.items():
            logger.info(f"\n🔍 {test_name.upper().replace('_', ' ')}: {result['status']}")
            for detail in result["details"]:
                logger.info(f"   • {detail}")
        
        # Calculate operational percentage
        operational_percentage = ((working_tests + (partial_tests * 0.5)) / total_tests) * 100
        logger.info(f"\n🎯 VOICE PROCESSING OPERATIONAL STATUS: {operational_percentage:.1f}%")
        
        # Critical issues summary
        logger.info("\n🚨 CRITICAL ISSUES IDENTIFIED:")
        critical_issues = []
        
        for test_name, result in self.test_results.items():
            if "❌" in result["status"]:
                if "500" in result["status"]:
                    critical_issues.append(f"• {test_name}: HTTP 500 Server Error")
                elif "404" in result["status"]:
                    critical_issues.append(f"• {test_name}: Endpoints Not Found (404)")
                elif "FAILED" in result["status"]:
                    critical_issues.append(f"• {test_name}: Complete Failure")
                else:
                    critical_issues.append(f"• {test_name}: {result['status']}")
        
        if critical_issues:
            for issue in critical_issues:
                logger.info(issue)
        else:
            logger.info("• No critical issues found!")
        
        # Recommendations
        logger.info("\n💡 RECOMMENDED FIXES:")
        recommendations = []
        
        if "❌" in self.test_results["voice_personalities"]["status"]:
            if "500" in self.test_results["voice_personalities"]["status"]:
                recommendations.append("• Fix voice_agent.get_available_voices() method - likely missing implementation or API error")
        
        if "❌" in self.test_results["ambient_listening"]["status"]:
            if "404" in self.test_results["ambient_listening"]["status"]:
                recommendations.append("• Implement missing ambient listening endpoints: /api/ambient/start, /api/ambient/stop, /api/ambient/status")
        
        if "❌" in self.test_results["progressive_tts"]["status"]:
            recommendations.append("• Fix TTS implementation gaps - check text_to_speech methods and audio generation")
        
        if "❌" in self.test_results["voice_pipeline"]["status"]:
            recommendations.append("• Fix voice processing pipeline - ensure STT, LLM, and TTS components are properly integrated")
        
        if "❌" in self.test_results["audio_formats"]["status"]:
            recommendations.append("• Improve audio format support - add proper format detection and conversion")
        
        if "❌" in self.test_results["voice_conversation"]["status"]:
            recommendations.append("• Fix voice conversation endpoint - ensure proper request handling and response format")
        
        if recommendations:
            for rec in recommendations:
                logger.info(rec)
        else:
            logger.info("• All systems operational - no fixes needed!")
        
        logger.info("="*80)

async def main():
    """Main test execution"""
    async with VoiceProcessingTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())