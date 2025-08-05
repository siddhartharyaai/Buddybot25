#!/usr/bin/env python3
"""
TTS Welcome Message Testing - Focused on Auto-Speaking Welcome Message Feature
Testing the /api/voice/tts endpoint for welcome message functionality
"""

import asyncio
import aiohttp
import json
import base64
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class TTSWelcomeMessageTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name, status, details="", response_time=None):
        """Log test result"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        time_info = f" ({response_time:.2f}s)" if response_time else ""
        print(f"{status_emoji} {test_name}: {status}{time_info}")
        if details:
            print(f"   Details: {details}")
            
    async def test_tts_endpoint_basic(self):
        """Test basic TTS endpoint functionality"""
        try:
            start_time = time.time()
            
            test_data = {
                "text": "Hello! This is a test message.",
                "personality": "friendly_companion"
            }
            
            async with self.session.post(f"{API_BASE}/voice/tts", json=test_data) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success" and data.get("audio_base64"):
                        # Verify base64 audio data
                        audio_data = data.get("audio_base64", "")
                        if len(audio_data) > 100:  # Should have substantial audio data
                            self.log_test("TTS Endpoint Basic Functionality", "PASS", 
                                        f"Generated {len(audio_data)} chars of base64 audio", response_time)
                        else:
                            self.log_test("TTS Endpoint Basic Functionality", "FAIL", 
                                        f"Audio data too short: {len(audio_data)} chars", response_time)
                    else:
                        self.log_test("TTS Endpoint Basic Functionality", "FAIL", 
                                    f"Invalid response format: {data}", response_time)
                else:
                    error_text = await response.text()
                    self.log_test("TTS Endpoint Basic Functionality", "FAIL", 
                                f"HTTP {response.status}: {error_text}", response_time)
                    
        except Exception as e:
            self.log_test("TTS Endpoint Basic Functionality", "FAIL", f"Exception: {str(e)}")
            
    async def test_welcome_message_tts(self):
        """Test TTS with typical welcome message"""
        try:
            start_time = time.time()
            
            # Typical welcome message format
            welcome_text = "Hi Emma! 👋 I'm Buddy, your AI friend. How can I help you today?"
            
            test_data = {
                "text": welcome_text,
                "personality": "friendly_companion"
            }
            
            async with self.session.post(f"{API_BASE}/voice/tts", json=test_data) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success" and data.get("audio_base64"):
                        audio_data = data.get("audio_base64", "")
                        
                        # Verify audio quality indicators
                        try:
                            # Decode base64 to check if it's valid
                            decoded_audio = base64.b64decode(audio_data)
                            audio_size_kb = len(decoded_audio) / 1024
                            
                            if audio_size_kb > 10:  # Should be substantial for welcome message
                                self.log_test("Welcome Message TTS Performance", "PASS", 
                                            f"Generated {audio_size_kb:.1f}KB audio for welcome message", response_time)
                            else:
                                self.log_test("Welcome Message TTS Performance", "FAIL", 
                                            f"Audio too small: {audio_size_kb:.1f}KB", response_time)
                        except Exception as decode_error:
                            self.log_test("Welcome Message TTS Performance", "FAIL", 
                                        f"Invalid base64 audio: {str(decode_error)}", response_time)
                    else:
                        self.log_test("Welcome Message TTS Performance", "FAIL", 
                                    f"Invalid response: {data}", response_time)
                else:
                    error_text = await response.text()
                    self.log_test("Welcome Message TTS Performance", "FAIL", 
                                f"HTTP {response.status}: {error_text}", response_time)
                    
        except Exception as e:
            self.log_test("Welcome Message TTS Performance", "FAIL", f"Exception: {str(e)}")
            
    async def test_voice_personalities(self):
        """Test different voice personalities for welcome messages"""
        personalities = ["friendly_companion", "story_narrator", "learning_buddy"]
        
        for personality in personalities:
            try:
                start_time = time.time()
                
                test_data = {
                    "text": f"Hello! I'm your {personality.replace('_', ' ')} today!",
                    "personality": personality
                }
                
                async with self.session.post(f"{API_BASE}/voice/tts", json=test_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "success" and data.get("audio_base64"):
                            audio_data = data.get("audio_base64", "")
                            if len(audio_data) > 100:
                                self.log_test(f"Voice Personality - {personality}", "PASS", 
                                            f"Generated audio with {personality}", response_time)
                            else:
                                self.log_test(f"Voice Personality - {personality}", "FAIL", 
                                            f"Audio data too short", response_time)
                        else:
                            self.log_test(f"Voice Personality - {personality}", "FAIL", 
                                        f"Invalid response format", response_time)
                    else:
                        error_text = await response.text()
                        self.log_test(f"Voice Personality - {personality}", "FAIL", 
                                    f"HTTP {response.status}: {error_text}", response_time)
                        
            except Exception as e:
                self.log_test(f"Voice Personality - {personality}", "FAIL", f"Exception: {str(e)}")
                
    async def test_tts_error_handling(self):
        """Test TTS endpoint error handling"""
        
        # Test 1: Empty text
        try:
            start_time = time.time()
            
            test_data = {
                "text": "",
                "personality": "friendly_companion"
            }
            
            async with self.session.post(f"{API_BASE}/voice/tts", json=test_data) as response:
                response_time = time.time() - start_time
                
                if response.status == 400:  # Should return bad request for empty text
                    self.log_test("TTS Error Handling - Empty Text", "PASS", 
                                "Correctly rejected empty text", response_time)
                else:
                    self.log_test("TTS Error Handling - Empty Text", "FAIL", 
                                f"Unexpected status: {response.status}", response_time)
                    
        except Exception as e:
            self.log_test("TTS Error Handling - Empty Text", "FAIL", f"Exception: {str(e)}")
            
        # Test 2: Invalid personality
        try:
            start_time = time.time()
            
            test_data = {
                "text": "Hello world!",
                "personality": "invalid_personality"
            }
            
            async with self.session.post(f"{API_BASE}/voice/tts", json=test_data) as response:
                response_time = time.time() - start_time
                
                # Should either work with fallback or return error
                if response.status in [200, 400]:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "success":
                            self.log_test("TTS Error Handling - Invalid Personality", "PASS", 
                                        "Handled invalid personality with fallback", response_time)
                        else:
                            self.log_test("TTS Error Handling - Invalid Personality", "PASS", 
                                        "Correctly rejected invalid personality", response_time)
                    else:
                        self.log_test("TTS Error Handling - Invalid Personality", "PASS", 
                                    "Correctly rejected invalid personality", response_time)
                else:
                    self.log_test("TTS Error Handling - Invalid Personality", "FAIL", 
                                f"Unexpected status: {response.status}", response_time)
                    
        except Exception as e:
            self.log_test("TTS Error Handling - Invalid Personality", "FAIL", f"Exception: {str(e)}")
            
    async def test_audio_format_compatibility(self):
        """Test audio format compatibility with HTML5 Audio API"""
        try:
            start_time = time.time()
            
            test_data = {
                "text": "Testing audio format compatibility for HTML5 playback.",
                "personality": "friendly_companion"
            }
            
            async with self.session.post(f"{API_BASE}/voice/tts", json=test_data) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success" and data.get("audio_base64"):
                        audio_base64 = data.get("audio_base64", "")
                        
                        try:
                            # Decode and check audio format
                            decoded_audio = base64.b64decode(audio_base64)
                            
                            # Check for common audio format headers
                            audio_format = "unknown"
                            if decoded_audio.startswith(b'RIFF'):
                                audio_format = "WAV"
                            elif decoded_audio.startswith(b'ID3') or decoded_audio[0:2] == b'\xff\xfb':
                                audio_format = "MP3"
                            elif decoded_audio.startswith(b'OggS'):
                                audio_format = "OGG"
                            elif decoded_audio.startswith(b'fLaC'):
                                audio_format = "FLAC"
                                
                            # Check if format is HTML5 compatible
                            html5_compatible = audio_format in ["WAV", "MP3", "OGG"]
                            
                            if html5_compatible:
                                self.log_test("Audio Format Compatibility", "PASS", 
                                            f"Generated {audio_format} format ({len(decoded_audio)} bytes)", response_time)
                            else:
                                self.log_test("Audio Format Compatibility", "WARN", 
                                            f"Unknown format, may not be HTML5 compatible ({len(decoded_audio)} bytes)", response_time)
                                
                        except Exception as decode_error:
                            self.log_test("Audio Format Compatibility", "FAIL", 
                                        f"Cannot decode audio: {str(decode_error)}", response_time)
                    else:
                        self.log_test("Audio Format Compatibility", "FAIL", 
                                    f"No audio data in response", response_time)
                else:
                    error_text = await response.text()
                    self.log_test("Audio Format Compatibility", "FAIL", 
                                f"HTTP {response.status}: {error_text}", response_time)
                    
        except Exception as e:
            self.log_test("Audio Format Compatibility", "FAIL", f"Exception: {str(e)}")
            
    async def test_welcome_message_generation(self):
        """Test welcome message generation endpoint"""
        try:
            start_time = time.time()
            
            test_data = {
                "user_id": "test_user_tts_welcome",
                "session_id": "test_session_tts_welcome"
            }
            
            async with self.session.post(f"{API_BASE}/conversations/welcome", json=test_data) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    welcome_message = data.get("message", "")
                    content_type = data.get("content_type", "")
                    
                    if welcome_message and content_type == "welcome":
                        # Now test TTS with the generated welcome message
                        tts_data = {
                            "text": welcome_message,
                            "personality": "friendly_companion"
                        }
                        
                        async with self.session.post(f"{API_BASE}/voice/tts", json=tts_data) as tts_response:
                            if tts_response.status == 200:
                                tts_result = await tts_response.json()
                                if tts_result.get("status") == "success" and tts_result.get("audio_base64"):
                                    self.log_test("Welcome Message + TTS Integration", "PASS", 
                                                f"Generated welcome message and TTS: '{welcome_message[:50]}...'", response_time)
                                else:
                                    self.log_test("Welcome Message + TTS Integration", "FAIL", 
                                                f"TTS failed for welcome message", response_time)
                            else:
                                self.log_test("Welcome Message + TTS Integration", "FAIL", 
                                            f"TTS request failed: {tts_response.status}", response_time)
                    else:
                        self.log_test("Welcome Message + TTS Integration", "FAIL", 
                                    f"Invalid welcome message response: {data}", response_time)
                else:
                    error_text = await response.text()
                    self.log_test("Welcome Message + TTS Integration", "FAIL", 
                                f"Welcome message generation failed: HTTP {response.status}: {error_text}", response_time)
                    
        except Exception as e:
            self.log_test("Welcome Message + TTS Integration", "FAIL", f"Exception: {str(e)}")
            
    async def test_tts_performance_metrics(self):
        """Test TTS performance for welcome messages"""
        try:
            # Test different message lengths
            test_messages = [
                "Hi!",  # Very short
                "Hello there! Welcome to Buddy!",  # Short
                "Hi Emma! 👋 I'm Buddy, your AI friend. How can I help you today?",  # Typical welcome
                "Hello and welcome! I'm Buddy, your friendly AI companion. I'm here to help you learn, play, and explore new things together. What would you like to do today?"  # Long welcome
            ]
            
            for i, message in enumerate(test_messages):
                start_time = time.time()
                
                test_data = {
                    "text": message,
                    "personality": "friendly_companion"
                }
                
                async with self.session.post(f"{API_BASE}/voice/tts", json=test_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "success" and data.get("audio_base64"):
                            audio_data = data.get("audio_base64", "")
                            decoded_size = len(base64.b64decode(audio_data)) if audio_data else 0
                            
                            # Performance criteria: should be under 5 seconds for welcome messages
                            if response_time < 5.0:
                                self.log_test(f"TTS Performance - Message {i+1}", "PASS", 
                                            f"Generated {decoded_size} bytes in {response_time:.2f}s", response_time)
                            else:
                                self.log_test(f"TTS Performance - Message {i+1}", "WARN", 
                                            f"Slow response: {response_time:.2f}s for {len(message)} chars", response_time)
                        else:
                            self.log_test(f"TTS Performance - Message {i+1}", "FAIL", 
                                        f"No audio generated", response_time)
                    else:
                        error_text = await response.text()
                        self.log_test(f"TTS Performance - Message {i+1}", "FAIL", 
                                    f"HTTP {response.status}: {error_text}", response_time)
                        
        except Exception as e:
            self.log_test("TTS Performance Testing", "FAIL", f"Exception: {str(e)}")
            
    async def run_all_tests(self):
        """Run all TTS welcome message tests"""
        print("🎯 STARTING TTS WELCOME MESSAGE TESTING")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Core TTS functionality tests
            await self.test_tts_endpoint_basic()
            await self.test_welcome_message_tts()
            
            # Voice personality tests
            await self.test_voice_personalities()
            
            # Error handling tests
            await self.test_tts_error_handling()
            
            # Audio format compatibility
            await self.test_audio_format_compatibility()
            
            # Integration tests
            await self.test_welcome_message_generation()
            
            # Performance tests
            await self.test_tts_performance_metrics()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 TTS WELCOME MESSAGE TESTING COMPLETE")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 RESULTS: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("✅ EXCELLENT: TTS welcome message system is working well")
        elif success_rate >= 60:
            print("⚠️  GOOD: TTS welcome message system is mostly functional")
        else:
            print("❌ NEEDS ATTENTION: TTS welcome message system has significant issues")
            
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "success_rate": success_rate,
            "test_results": self.test_results
        }

async def main():
    """Main test execution"""
    tester = TTSWelcomeMessageTester()
    results = await tester.run_all_tests()
    
    # Return results for potential integration with other systems
    return results

if __name__ == "__main__":
    asyncio.run(main())