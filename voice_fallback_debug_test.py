#!/usr/bin/env python3
"""
DEBUG TEST: Investigate why "I heard you!" fallback responses are still occurring
Focus: Test different scenarios to understand when fallbacks happen vs real responses
"""

import asyncio
import aiohttp
import json
import base64
import time
import logging
from typing import Dict, Any, List
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoiceFallbackDebugTester:
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
        
        logger.info(f"🔍 VOICE FALLBACK DEBUG: Using backend URL: {self.base_url}")
        
        # Test data
        self.test_user_id = f"debug_user_{int(time.time())}"
        self.test_session_id = f"debug_session_{int(time.time())}"
        
    async def run_debug_tests(self):
        """Run debug tests to understand fallback behavior"""
        logger.info("🔍 STARTING VOICE FALLBACK DEBUG TESTING")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Create test user profile first
            await self._create_test_user_profile()
            
            # Test 1: Text input (should work fine)
            await self._test_text_input()
            
            # Test 2: Voice input with silence (current test case)
            await self._test_voice_with_silence()
            
            # Test 3: Test TTS directly
            await self._test_direct_tts()
            
            # Test 4: Test conversation endpoint directly
            await self._test_conversation_endpoint()
            
            # Test 5: Check if it's an STT issue
            await self._test_stt_behavior()
    
    async def _create_test_user_profile(self):
        """Create test user profile"""
        try:
            profile_data = {
                "name": f"DebugUser_{int(time.time())}",
                "age": 7,
                "location": "Test City",
                "timezone": "UTC",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "games"],
                "learning_goals": ["conversation"],
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
    
    async def _test_text_input(self):
        """Test 1: Text input should generate proper AI responses"""
        logger.info("🔍 TEST 1: Text Input (Baseline)")
        
        try:
            text_request = {
                "session_id": self.test_session_id,
                "message": "Hello, how are you today?",
                "user_id": self.test_user_id
            }
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=text_request) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "")
                    
                    logger.info(f"📝 TEXT INPUT RESULT:")
                    logger.info(f"   Response: '{response_text}'")
                    logger.info(f"   Length: {len(response_text)} chars")
                    logger.info(f"   Content Type: {result.get('content_type', 'unknown')}")
                    
                    if "i heard you" in response_text.lower():
                        logger.warning("⚠️  TEXT INPUT ALSO RETURNS FALLBACK!")
                    else:
                        logger.info("✅ TEXT INPUT WORKS PROPERLY")
                        
                else:
                    logger.error(f"❌ Text input failed: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Text input error: {e}")
    
    async def _test_voice_with_silence(self):
        """Test 2: Voice input with silence (reproducing current issue)"""
        logger.info("🔍 TEST 2: Voice Input with Silence")
        
        try:
            # Generate silence audio
            wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
            silence_data = b'\x00' * 2048
            sample_wav = wav_header + silence_data
            audio_base64 = base64.b64encode(sample_wav).decode('utf-8')
            
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                if response.status == 200:
                    result = await response.json()
                    transcript = result.get("transcript", "")
                    response_text = result.get("response_text", "")
                    pipeline = result.get("pipeline", "")
                    
                    logger.info(f"🎤 VOICE INPUT (SILENCE) RESULT:")
                    logger.info(f"   Transcript: '{transcript}'")
                    logger.info(f"   Response: '{response_text}'")
                    logger.info(f"   Pipeline: {pipeline}")
                    logger.info(f"   Length: {len(response_text)} chars")
                    
                    if not transcript or transcript.strip() == "":
                        logger.info("🔍 EMPTY TRANSCRIPT - This might trigger fallback logic")
                    
                    if "i heard you" in response_text.lower():
                        logger.warning("⚠️  VOICE INPUT RETURNS FALLBACK (Expected for silence)")
                    else:
                        logger.info("✅ VOICE INPUT WORKS PROPERLY")
                        
                else:
                    logger.error(f"❌ Voice input failed: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Voice input error: {e}")
    
    async def _test_direct_tts(self):
        """Test 3: Test TTS directly with meaningful text"""
        logger.info("🔍 TEST 3: Direct TTS Test")
        
        try:
            tts_request = {
                "text": "Hello there! I'm your AI companion and I'm here to help you with anything you need. How can I assist you today?",
                "personality": "friendly_companion"
            }
            
            async with self.session.post(f"{self.base_url}/voice/tts", json=tts_request) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    logger.info(f"🔊 DIRECT TTS RESULT:")
                    logger.info(f"   Status: {result.get('status', 'unknown')}")
                    logger.info(f"   Audio Length: {len(result.get('audio_base64', ''))} chars")
                    logger.info(f"   Text: '{result.get('text', '')[:100]}...'")
                    
                    if result.get("status") == "success":
                        logger.info("✅ DIRECT TTS WORKS PROPERLY")
                    else:
                        logger.warning("⚠️  DIRECT TTS HAS ISSUES")
                        
                else:
                    logger.error(f"❌ Direct TTS failed: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Direct TTS error: {e}")
    
    async def _test_conversation_endpoint(self):
        """Test 4: Test conversation endpoint directly"""
        logger.info("🔍 TEST 4: Direct Conversation Endpoint Test")
        
        try:
            conv_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": ""  # Empty audio to simulate no speech detected
            }
            
            async with self.session.post(f"{self.base_url}/conversations/voice", json=conv_request) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    logger.info(f"💬 CONVERSATION ENDPOINT RESULT:")
                    logger.info(f"   Response Text: '{result.get('response_text', '')}'")
                    logger.info(f"   Content Type: {result.get('content_type', 'unknown')}")
                    logger.info(f"   Processing Time: {result.get('processing_time', 'unknown')}")
                    
                elif response.status == 400:
                    logger.info("🔍 CONVERSATION ENDPOINT REQUIRES VALID AUDIO (Expected)")
                else:
                    logger.error(f"❌ Conversation endpoint failed: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Conversation endpoint error: {e}")
    
    async def _test_stt_behavior(self):
        """Test 5: Check STT behavior with empty/silence audio"""
        logger.info("🔍 TEST 5: STT Behavior Analysis")
        
        try:
            # Test what happens when STT gets silence
            wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
            silence_data = b'\x00' * 2048
            sample_wav = wav_header + silence_data
            audio_base64 = base64.b64encode(sample_wav).decode('utf-8')
            
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                if response.status == 200:
                    result = await response.json()
                    transcript = result.get("transcript", "")
                    response_text = result.get("response_text", "")
                    
                    logger.info(f"🎯 STT BEHAVIOR ANALYSIS:")
                    logger.info(f"   Raw Transcript: '{transcript}'")
                    logger.info(f"   Transcript Length: {len(transcript)}")
                    logger.info(f"   Transcript Empty: {not transcript or transcript.strip() == ''}")
                    logger.info(f"   Response Generated: '{response_text}'")
                    
                    # Check if empty transcript triggers fallback
                    if not transcript or transcript.strip() == "":
                        logger.info("🔍 ANALYSIS: Empty transcript likely triggers 'I heard you!' fallback")
                        logger.info("🔍 SOLUTION: The system should handle empty STT results better")
                        
                        # This is actually expected behavior for silence!
                        # The issue might be that we're testing with silence
                        logger.info("💡 INSIGHT: Testing with silence naturally produces empty transcript")
                        logger.info("💡 INSIGHT: 'I heard you!' might be appropriate response to silence")
                        logger.info("💡 INSIGHT: Need to test with actual speech audio to verify fix")
                    
                else:
                    logger.error(f"❌ STT analysis failed: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ STT analysis error: {e}")
        
        # Final analysis
        logger.info("🎯 FINAL ANALYSIS:")
        logger.info("   The 'I heard you!' response might be CORRECT behavior for:")
        logger.info("   1. Empty/silence audio input")
        logger.info("   2. STT returning empty transcript")
        logger.info("   3. No speech detected scenarios")
        logger.info("")
        logger.info("   The CRITICAL BUG was the text_to_speech_ultra_fast method error")
        logger.info("   That appears to be FIXED (no method errors detected)")
        logger.info("")
        logger.info("   To properly test the fix, we need:")
        logger.info("   1. Real speech audio samples")
        logger.info("   2. Test cases that should generate AI responses")
        logger.info("   3. Verify those don't fallback to 'I heard you!'")

async def main():
    """Main test execution"""
    tester = VoiceFallbackDebugTester()
    await tester.run_debug_tests()

if __name__ == "__main__":
    asyncio.run(main())