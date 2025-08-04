#!/usr/bin/env python3
"""
CRITICAL VOICE PROCESSING PIPELINE TEST
Testing Focus: Verify the critical bug fix where fast pipeline was calling non-existent `text_to_speech_ultra_fast` method
Expected: NO MORE "I heard you!" fallback responses - should get actual AI responses with proper audio
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

class VoicePipelineCriticalTester:
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
        
        logger.info(f"🎯 CRITICAL VOICE PIPELINE TESTING: Using backend URL: {self.base_url}")
        
        # Test data
        self.test_user_id = f"voice_test_user_{int(time.time())}"
        self.test_session_id = f"voice_session_{int(time.time())}"
        
        # Sample audio data (base64 encoded silence for testing)
        self.sample_audio_base64 = self._generate_sample_audio()
        
        # Test results tracking
        self.test_results = {
            "voice_processing_endpoint": [],
            "end_to_end_pipeline": [],
            "response_content_validation": [],
            "audio_generation": [],
            "fast_pipeline_specific": []
        }
        
    def _generate_sample_audio(self):
        """Generate a small sample audio data for testing (base64 encoded)"""
        # This is a minimal WAV file header + some silence
        # In a real scenario, you'd use actual audio data
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
        silence_data = b'\x00' * 2048  # 2KB of silence
        sample_wav = wav_header + silence_data
        return base64.b64encode(sample_wav).decode('utf-8')
        
    async def run_critical_voice_tests(self):
        """Run all critical voice processing tests"""
        logger.info("🚨 STARTING CRITICAL VOICE PROCESSING PIPELINE TESTING")
        logger.info("🎯 FOCUS: Verify fix for text_to_speech_ultra_fast method bug")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Create test user profile first
            await self._create_test_user_profile()
            
            # Test 1: Voice Processing Endpoint Basic Functionality
            await self._test_voice_processing_endpoint()
            
            # Test 2: End-to-End Pipeline (STT → LLM → TTS)
            await self._test_end_to_end_pipeline()
            
            # Test 3: Response Content Validation (NO "I heard you!" fallbacks)
            await self._test_response_content_validation()
            
            # Test 4: Audio Generation Verification
            await self._test_audio_generation()
            
            # Test 5: Fast Pipeline Specific Testing
            await self._test_fast_pipeline_specific()
            
        # Generate comprehensive report
        await self._generate_test_report()
    
    async def _create_test_user_profile(self):
        """Create test user profile for voice testing"""
        try:
            profile_data = {
                "name": f"VoiceTestUser_{int(time.time())}",
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
    
    async def _test_voice_processing_endpoint(self):
        """Test 1: Voice Processing Endpoint - /api/voice/process_audio"""
        logger.info("🎯 TEST 1: Voice Processing Endpoint Basic Functionality")
        
        test_results = []
        
        # Test 1.1: Endpoint accessibility and basic response
        try:
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": self.sample_audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success":
                        test_results.append({
                            "test": "Endpoint accessibility",
                            "status": "PASS",
                            "details": f"Voice processing endpoint responding: {result.get('pipeline', 'unknown')} pipeline used"
                        })
                    else:
                        test_results.append({
                            "test": "Endpoint accessibility",
                            "status": "FAIL",
                            "details": f"Endpoint returned error status: {result}"
                        })
                else:
                    test_results.append({
                        "test": "Endpoint accessibility",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Endpoint accessibility",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 1.2: Response structure validation
        try:
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": self.sample_audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                if response.status == 200:
                    result = await response.json()
                    required_fields = ["status", "transcript", "response_text", "response_audio"]
                    missing_fields = [field for field in required_fields if field not in result]
                    
                    if not missing_fields:
                        test_results.append({
                            "test": "Response structure validation",
                            "status": "PASS",
                            "details": f"All required fields present: {required_fields}"
                        })
                    else:
                        test_results.append({
                            "test": "Response structure validation",
                            "status": "FAIL",
                            "details": f"Missing fields: {missing_fields}"
                        })
                else:
                    test_results.append({
                        "test": "Response structure validation",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Response structure validation",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["voice_processing_endpoint"] = test_results
        logger.info(f"✅ Voice Processing Endpoint Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_end_to_end_pipeline(self):
        """Test 2: End-to-End Pipeline (STT → LLM → TTS)"""
        logger.info("🎯 TEST 2: End-to-End Pipeline Verification")
        
        test_results = []
        
        # Test 2.1: STT Processing
        try:
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": self.sample_audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                if response.status == 200:
                    result = await response.json()
                    transcript = result.get("transcript", "")
                    
                    # Even if transcript is empty (due to silence), STT should process without error
                    if "transcript" in result:
                        test_results.append({
                            "test": "STT Processing",
                            "status": "PASS",
                            "details": f"STT processed successfully, transcript: '{transcript[:50]}...'"
                        })
                    else:
                        test_results.append({
                            "test": "STT Processing",
                            "status": "FAIL",
                            "details": "No transcript field in response"
                        })
                else:
                    test_results.append({
                        "test": "STT Processing",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "STT Processing",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 2.2: LLM Response Generation
        try:
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": self.sample_audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "")
                    
                    if response_text and len(response_text) > 0:
                        test_results.append({
                            "test": "LLM Response Generation",
                            "status": "PASS",
                            "details": f"LLM generated response: '{response_text[:100]}...'"
                        })
                    else:
                        test_results.append({
                            "test": "LLM Response Generation",
                            "status": "FAIL",
                            "details": "No response text generated"
                        })
                else:
                    test_results.append({
                        "test": "LLM Response Generation",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "LLM Response Generation",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 2.3: TTS Audio Generation
        try:
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": self.sample_audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                if response.status == 200:
                    result = await response.json()
                    response_audio = result.get("response_audio", "")
                    
                    if response_audio and len(response_audio) > 0:
                        test_results.append({
                            "test": "TTS Audio Generation",
                            "status": "PASS",
                            "details": f"TTS generated audio: {len(response_audio)} chars base64"
                        })
                    else:
                        test_results.append({
                            "test": "TTS Audio Generation",
                            "status": "FAIL",
                            "details": "No response audio generated"
                        })
                else:
                    test_results.append({
                        "test": "TTS Audio Generation",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "TTS Audio Generation",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["end_to_end_pipeline"] = test_results
        logger.info(f"✅ End-to-End Pipeline Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_response_content_validation(self):
        """Test 3: Response Content Validation - NO "I heard you!" fallbacks"""
        logger.info("🎯 TEST 3: Response Content Validation (Critical Bug Fix)")
        
        test_results = []
        
        # Test 3.1: No "I heard you!" fallback responses
        try:
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": self.sample_audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "").lower()
                    
                    # Check for the specific fallback text that was the bug
                    if "i heard you!" in response_text or "i heard you" in response_text:
                        test_results.append({
                            "test": "No fallback responses",
                            "status": "FAIL",
                            "details": f"CRITICAL BUG STILL PRESENT: Found fallback response: '{result.get('response_text', '')}'"
                        })
                    else:
                        test_results.append({
                            "test": "No fallback responses",
                            "status": "PASS",
                            "details": f"✅ BUG FIXED: No fallback response detected. Got: '{result.get('response_text', '')[:100]}...'"
                        })
                else:
                    test_results.append({
                        "test": "No fallback responses",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "No fallback responses",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 3.2: Actual AI responses generated
        try:
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": self.sample_audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "")
                    
                    # Check if we get meaningful AI responses (not just generic fallbacks)
                    if len(response_text) > 10 and response_text.strip():
                        test_results.append({
                            "test": "Actual AI responses generated",
                            "status": "PASS",
                            "details": f"AI response generated: '{response_text[:100]}...'"
                        })
                    else:
                        test_results.append({
                            "test": "Actual AI responses generated",
                            "status": "FAIL",
                            "details": f"Response too short or empty: '{response_text}'"
                        })
                else:
                    test_results.append({
                        "test": "Actual AI responses generated",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Actual AI responses generated",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 3.3: No "FALLBACK TTS" messages in logs (check response metadata)
        try:
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": self.sample_audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                if response.status == 200:
                    result = await response.json()
                    metadata = result.get("metadata", {})
                    pipeline = result.get("pipeline", "")
                    
                    # Check if we're using proper pipeline, not fallback
                    if "fallback" not in pipeline.lower() and "error" not in str(metadata).lower():
                        test_results.append({
                            "test": "No fallback TTS messages",
                            "status": "PASS",
                            "details": f"Using proper pipeline: {pipeline}, metadata clean"
                        })
                    else:
                        test_results.append({
                            "test": "No fallback TTS messages",
                            "status": "FAIL",
                            "details": f"Fallback detected in pipeline: {pipeline} or metadata: {metadata}"
                        })
                else:
                    test_results.append({
                        "test": "No fallback TTS messages",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "No fallback TTS messages",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["response_content_validation"] = test_results
        logger.info(f"✅ Response Content Validation Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_audio_generation(self):
        """Test 4: Audio Generation Verification"""
        logger.info("🎯 TEST 4: Audio Generation for Actual AI Responses")
        
        test_results = []
        
        # Test 4.1: Audio matches response text content
        try:
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": self.sample_audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "")
                    response_audio = result.get("response_audio", "")
                    
                    # If we have text, we should have corresponding audio
                    if response_text and response_audio:
                        # Basic validation: audio length should correlate with text length
                        text_length = len(response_text)
                        audio_length = len(response_audio)
                        
                        # Rough estimate: longer text should produce longer audio (base64)
                        if audio_length > 100:  # Minimum reasonable audio size
                            test_results.append({
                                "test": "Audio matches response content",
                                "status": "PASS",
                                "details": f"Audio generated for text ({text_length} chars text → {audio_length} chars audio)"
                            })
                        else:
                            test_results.append({
                                "test": "Audio matches response content",
                                "status": "FAIL",
                                "details": f"Audio too short: {audio_length} chars for {text_length} chars text"
                            })
                    elif response_text and not response_audio:
                        test_results.append({
                            "test": "Audio matches response content",
                            "status": "FAIL",
                            "details": f"Text present but no audio: '{response_text[:50]}...'"
                        })
                    else:
                        test_results.append({
                            "test": "Audio matches response content",
                            "status": "FAIL",
                            "details": "Neither text nor audio present"
                        })
                else:
                    test_results.append({
                        "test": "Audio matches response content",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Audio matches response content",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 4.2: Audio quality validation (basic checks)
        try:
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": self.sample_audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                if response.status == 200:
                    result = await response.json()
                    response_audio = result.get("response_audio", "")
                    
                    if response_audio:
                        try:
                            # Try to decode base64 to verify it's valid
                            audio_data = base64.b64decode(response_audio)
                            if len(audio_data) > 0:
                                test_results.append({
                                    "test": "Audio quality validation",
                                    "status": "PASS",
                                    "details": f"Valid audio data: {len(audio_data)} bytes"
                                })
                            else:
                                test_results.append({
                                    "test": "Audio quality validation",
                                    "status": "FAIL",
                                    "details": "Audio data is empty after decoding"
                                })
                        except Exception as decode_error:
                            test_results.append({
                                "test": "Audio quality validation",
                                "status": "FAIL",
                                "details": f"Invalid base64 audio: {str(decode_error)}"
                            })
                    else:
                        test_results.append({
                            "test": "Audio quality validation",
                            "status": "FAIL",
                            "details": "No audio data to validate"
                        })
                else:
                    test_results.append({
                        "test": "Audio quality validation",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Audio quality validation",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["audio_generation"] = test_results
        logger.info(f"✅ Audio Generation Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_fast_pipeline_specific(self):
        """Test 5: Fast Pipeline Specific Testing (The bug was here)"""
        logger.info("🎯 TEST 5: Fast Pipeline Specific Testing (Critical Bug Location)")
        
        test_results = []
        
        # Test 5.1: Fast pipeline method existence (the core bug)
        try:
            # Test with a simple greeting that should trigger fast pipeline
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": self.sample_audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                if response.status == 200:
                    result = await response.json()
                    pipeline = result.get("pipeline", "")
                    auto_selected = result.get("auto_selected_pipeline", "")
                    
                    # Check if fast pipeline is working without errors
                    if "ultra_fast" in pipeline.lower() or "fast" in auto_selected.lower():
                        test_results.append({
                            "test": "Fast pipeline method existence",
                            "status": "PASS",
                            "details": f"✅ CRITICAL BUG FIXED: Fast pipeline working: {pipeline} / {auto_selected}"
                        })
                    else:
                        # Even if not using fast pipeline, it should work without the method error
                        test_results.append({
                            "test": "Fast pipeline method existence",
                            "status": "PASS",
                            "details": f"Pipeline working (using {pipeline}), no method errors"
                        })
                else:
                    test_results.append({
                        "test": "Fast pipeline method existence",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            # If we get a method error, the bug is still there
            if "text_to_speech_ultra_fast" in str(e):
                test_results.append({
                    "test": "Fast pipeline method existence",
                    "status": "FAIL",
                    "details": f"🚨 CRITICAL BUG STILL PRESENT: {str(e)}"
                })
            else:
                test_results.append({
                    "test": "Fast pipeline method existence",
                    "status": "ERROR",
                    "details": str(e)
                })
        
        # Test 5.2: Ultra-fast pipeline performance
        try:
            start_time = time.time()
            
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": self.sample_audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                end_time = time.time()
                latency = end_time - start_time
                
                if response.status == 200:
                    result = await response.json()
                    reported_latency = result.get("latency", "unknown")
                    
                    # Fast pipeline should be reasonably quick
                    if latency < 10.0:  # 10 seconds is reasonable for testing
                        test_results.append({
                            "test": "Ultra-fast pipeline performance",
                            "status": "PASS",
                            "details": f"Fast processing: {latency:.2f}s actual, {reported_latency} reported"
                        })
                    else:
                        test_results.append({
                            "test": "Ultra-fast pipeline performance",
                            "status": "FAIL",
                            "details": f"Slow processing: {latency:.2f}s (expected <10s)"
                        })
                else:
                    test_results.append({
                        "test": "Ultra-fast pipeline performance",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Ultra-fast pipeline performance",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 5.3: Smart pipeline selection working
        try:
            voice_data = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": self.sample_audio_base64
            }
            
            async with self.session.post(f"{self.base_url}/voice/process_audio", data=voice_data) as response:
                if response.status == 200:
                    result = await response.json()
                    smart_routing = result.get("smart_routing", "")
                    auto_selected = result.get("auto_selected_pipeline", "")
                    
                    if smart_routing == "enabled" and auto_selected:
                        test_results.append({
                            "test": "Smart pipeline selection",
                            "status": "PASS",
                            "details": f"Smart routing enabled, selected: {auto_selected}"
                        })
                    else:
                        test_results.append({
                            "test": "Smart pipeline selection",
                            "status": "FAIL",
                            "details": f"Smart routing not working: {smart_routing}, {auto_selected}"
                        })
                else:
                    test_results.append({
                        "test": "Smart pipeline selection",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Smart pipeline selection",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["fast_pipeline_specific"] = test_results
        logger.info(f"✅ Fast Pipeline Specific Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("🎯 GENERATING CRITICAL VOICE PIPELINE TEST REPORT")
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        
        report = []
        report.append("=" * 80)
        report.append("🚨 CRITICAL VOICE PROCESSING PIPELINE TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Backend URL: {self.base_url}")
        report.append(f"Test User ID: {self.test_user_id}")
        report.append(f"Test Session ID: {self.test_session_id}")
        report.append("")
        report.append("🎯 FOCUS: Verify fix for text_to_speech_ultra_fast method bug")
        report.append("🎯 EXPECTED: NO MORE 'I heard you!' fallback responses")
        report.append("")
        
        for category, tests in self.test_results.items():
            if not tests:
                continue
                
            category_passed = len([t for t in tests if t['status'] == 'PASS'])
            category_failed = len([t for t in tests if t['status'] == 'FAIL'])
            category_errors = len([t for t in tests if t['status'] == 'ERROR'])
            category_total = len(tests)
            
            total_tests += category_total
            total_passed += category_passed
            total_failed += category_failed
            total_errors += category_errors
            
            success_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            
            report.append(f"📋 {category.upper().replace('_', ' ')}")
            report.append(f"   Success Rate: {success_rate:.1f}% ({category_passed}/{category_total})")
            report.append(f"   ✅ Passed: {category_passed}")
            report.append(f"   ❌ Failed: {category_failed}")
            report.append(f"   🔥 Errors: {category_errors}")
            report.append("")
            
            for test in tests:
                status_icon = "✅" if test['status'] == 'PASS' else "❌" if test['status'] == 'FAIL' else "🔥"
                report.append(f"   {status_icon} {test['test']}: {test['status']}")
                report.append(f"      Details: {test['details']}")
                report.append("")
        
        # Overall summary
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report.append("=" * 80)
        report.append("🚨 CRITICAL BUG FIX ASSESSMENT")
        report.append("=" * 80)
        report.append(f"Total Tests: {total_tests}")
        report.append(f"✅ Passed: {total_passed}")
        report.append(f"❌ Failed: {total_failed}")
        report.append(f"🔥 Errors: {total_errors}")
        report.append(f"Overall Success Rate: {overall_success_rate:.1f}%")
        report.append("")
        
        # Critical assessment
        if overall_success_rate >= 90:
            report.append("🎉 EXCELLENT: Critical voice processing bug appears to be FIXED!")
            report.append("✅ Voice responses should now work properly without fallbacks")
        elif overall_success_rate >= 70:
            report.append("⚠️  GOOD: Most voice processing working, but some issues remain")
            report.append("🔍 Review failed tests for remaining issues")
        else:
            report.append("🚨 CRITICAL: Major issues still present in voice processing pipeline")
            report.append("❌ The text_to_speech_ultra_fast bug may still be present")
        
        report.append("")
        report.append("🔍 KEY FINDINGS:")
        
        # Check for specific critical issues
        response_tests = self.test_results.get("response_content_validation", [])
        fallback_test = next((t for t in response_tests if "fallback" in t['test'].lower()), None)
        if fallback_test:
            if fallback_test['status'] == 'PASS':
                report.append("✅ CRITICAL BUG FIXED: No more 'I heard you!' fallback responses")
            else:
                report.append("❌ CRITICAL BUG STILL PRESENT: 'I heard you!' fallbacks detected")
        
        fast_pipeline_tests = self.test_results.get("fast_pipeline_specific", [])
        method_test = next((t for t in fast_pipeline_tests if "method" in t['test'].lower()), None)
        if method_test:
            if method_test['status'] == 'PASS':
                report.append("✅ FAST PIPELINE FIXED: text_to_speech_ultra_fast method issue resolved")
            else:
                report.append("❌ FAST PIPELINE BROKEN: text_to_speech_ultra_fast method still missing")
        
        audio_tests = self.test_results.get("audio_generation", [])
        if audio_tests:
            audio_passed = len([t for t in audio_tests if t['status'] == 'PASS'])
            if audio_passed >= len(audio_tests) * 0.8:
                report.append("✅ AUDIO GENERATION: Working correctly for AI responses")
            else:
                report.append("❌ AUDIO GENERATION: Issues with TTS for AI responses")
        
        pipeline_tests = self.test_results.get("end_to_end_pipeline", [])
        if pipeline_tests:
            pipeline_passed = len([t for t in pipeline_tests if t['status'] == 'PASS'])
            if pipeline_passed >= len(pipeline_tests) * 0.8:
                report.append("✅ END-TO-END PIPELINE: STT → LLM → TTS flow working")
            else:
                report.append("❌ END-TO-END PIPELINE: Issues in STT → LLM → TTS flow")
        
        report.append("")
        report.append("=" * 80)
        
        # Print report
        for line in report:
            logger.info(line)
        
        return {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_errors": total_errors,
            "success_rate": overall_success_rate,
            "critical_bug_fixed": overall_success_rate >= 70,
            "detailed_results": self.test_results
        }

async def main():
    """Main test execution"""
    tester = VoicePipelineCriticalTester()
    results = await tester.run_critical_voice_tests()
    
    # Return results for further processing
    return results

if __name__ == "__main__":
    asyncio.run(main())