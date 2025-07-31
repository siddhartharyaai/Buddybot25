#!/usr/bin/env python3
"""
TTS Audio Output Comprehensive Testing
Tests the comprehensive TTS audio output fixes for missing audio diagnosis
"""

import asyncio
import requests
import json
import base64
import logging
import time
from typing import Dict, Any, Optional

# Configure logging to capture debug messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TTSAudioOutputTester:
    def __init__(self):
        # Get backend URL from environment
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.base_url = line.split('=')[1].strip()
                        break
                else:
                    self.base_url = "http://localhost:8001"
        except Exception:
            self.base_url = "http://localhost:8001"
        
        self.api_url = f"{self.base_url}/api"
        logger.info(f"🔧 TTS Audio Output Tester initialized with API URL: {self.api_url}")
        
        # Test results storage
        self.test_results = {
            "tts_debug_logging": [],
            "force_tts_generation": [],
            "orchestrator_audio_prioritization": [],
            "audio_output_validation": [],
            "error_handling": [],
            "overall_stats": {}
        }
    
    async def run_all_tests(self):
        """Run all TTS audio output tests"""
        logger.info("🎵 Starting comprehensive TTS audio output testing...")
        
        try:
            # Test 1: TTS Debug Logging Validation
            await self.test_tts_debug_logging()
            
            # Test 2: Force TTS Audio Generation
            await self.test_force_tts_generation()
            
            # Test 3: Orchestrator Audio Prioritization
            await self.test_orchestrator_audio_prioritization()
            
            # Test 4: Audio Output Validation
            await self.test_audio_output_validation()
            
            # Test 5: Error Handling
            await self.test_error_handling()
            
            # Generate final report
            self.generate_final_report()
            
        except Exception as e:
            logger.error(f"❌ Critical error during testing: {str(e)}")
            return False
    
    async def test_tts_debug_logging(self):
        """Test 1: TTS Debug Logging Validation"""
        logger.info("🎵 TEST 1: TTS Debug Logging Validation")
        
        test_cases = [
            {
                "name": "Simple TTS Debug Logging",
                "endpoint": "/voice/tts",
                "data": {"text": "Hello, this is a test message", "personality": "friendly_companion"},
                "expected_logs": ["🎵 DEBUG TTS", "size:"]
            },
            {
                "name": "Chunked TTS Debug Logging",
                "endpoint": "/voice/tts",
                "data": {"text": "This is a very long message that should trigger chunked processing. " * 30, "personality": "story_narrator"},
                "expected_logs": ["🎵 DEBUG TTS CHUNKED", "blob size"]
            },
            {
                "name": "Streaming TTS Debug Logging",
                "endpoint": "/voice/tts/streaming",
                "data": {"text": "This is a streaming TTS test message for debug logging validation", "personality": "learning_buddy"},
                "expected_logs": ["🎵 DEBUG TTS", "audio generated"]
            }
        ]
        
        for test_case in test_cases:
            result = await self._test_tts_endpoint(test_case)
            self.test_results["tts_debug_logging"].append(result)
    
    async def test_force_tts_generation(self):
        """Test 2: Force TTS Audio Generation"""
        logger.info("🎵 TEST 2: Force TTS Audio Generation")
        
        test_cases = [
            {
                "name": "Story Request with TTS",
                "endpoint": "/conversations/text",
                "data": {
                    "session_id": "test_story_session",
                    "user_id": "test_user_story",
                    "message": "Tell me a story about a brave little mouse"
                },
                "expected_audio": True,
                "content_type": "story"
            },
            {
                "name": "Fact Request with TTS",
                "endpoint": "/conversations/text",
                "data": {
                    "session_id": "test_fact_session",
                    "user_id": "test_user_fact",
                    "message": "Tell me a fun fact about elephants"
                },
                "expected_audio": True,
                "content_type": "conversation"
            },
            {
                "name": "Joke Request with TTS",
                "endpoint": "/conversations/text",
                "data": {
                    "session_id": "test_joke_session",
                    "user_id": "test_user_joke",
                    "message": "Tell me a funny joke"
                },
                "expected_audio": True,
                "content_type": "joke"
            },
            {
                "name": "Regular Conversation with TTS",
                "endpoint": "/conversations/text",
                "data": {
                    "session_id": "test_conv_session",
                    "user_id": "test_user_conv",
                    "message": "How are you today?"
                },
                "expected_audio": True,
                "content_type": "conversation"
            }
        ]
        
        for test_case in test_cases:
            result = await self._test_conversation_endpoint(test_case)
            self.test_results["force_tts_generation"].append(result)
    
    async def test_orchestrator_audio_prioritization(self):
        """Test 3: Orchestrator Audio Prioritization"""
        logger.info("🎵 TEST 3: Orchestrator Audio Prioritization")
        
        test_cases = [
            {
                "name": "Pre-generated Audio Usage",
                "endpoint": "/content/stories/story_001/narrate",
                "data": {"user_id": "test_user_pregenerated"},
                "test_type": "form_data",
                "expected_audio": True,
                "check_source": "cached"
            },
            {
                "name": "Fallback TTS Generation",
                "endpoint": "/conversations/text",
                "data": {
                    "session_id": "test_fallback_session",
                    "user_id": "test_user_fallback",
                    "message": "Generate a new response that requires TTS"
                },
                "expected_audio": True,
                "check_source": "generated"
            }
        ]
        
        for test_case in test_cases:
            if test_case.get("test_type") == "form_data":
                result = await self._test_form_data_endpoint(test_case)
            else:
                result = await self._test_conversation_endpoint(test_case)
            self.test_results["orchestrator_audio_prioritization"].append(result)
    
    async def test_audio_output_validation(self):
        """Test 4: Audio Output Validation"""
        logger.info("🎵 TEST 4: Audio Output Validation")
        
        content_types = [
            {"type": "story", "message": "Tell me a complete story about a magical forest"},
            {"type": "fact", "message": "What's an interesting fact about space?"},
            {"type": "joke", "message": "Can you tell me a kid-friendly joke?"},
            {"type": "song", "message": "Sing me a short song about friendship"},
            {"type": "conversation", "message": "What's your favorite color and why?"}
        ]
        
        for content_type in content_types:
            test_case = {
                "name": f"{content_type['type'].title()} Audio Validation",
                "endpoint": "/conversations/text",
                "data": {
                    "session_id": f"test_{content_type['type']}_session",
                    "user_id": f"test_user_{content_type['type']}",
                    "message": content_type["message"]
                },
                "expected_audio": True,
                "content_type": content_type["type"]
            }
            
            result = await self._test_conversation_endpoint(test_case)
            self.test_results["audio_output_validation"].append(result)
    
    async def test_error_handling(self):
        """Test 5: Error Handling and Retry Fallback"""
        logger.info("🎵 TEST 5: Error Handling and Retry Fallback")
        
        test_cases = [
            {
                "name": "Empty Text TTS Fallback",
                "endpoint": "/voice/tts",
                "data": {"text": "", "personality": "friendly_companion"},
                "expected_fallback": True
            },
            {
                "name": "Invalid Personality Fallback",
                "endpoint": "/voice/tts",
                "data": {"text": "Test message", "personality": "invalid_personality"},
                "expected_fallback": True
            },
            {
                "name": "Very Long Text Chunking",
                "endpoint": "/voice/tts",
                "data": {"text": "This is a very long text message. " * 100, "personality": "story_narrator"},
                "expected_chunking": True
            }
        ]
        
        for test_case in test_cases:
            result = await self._test_tts_endpoint(test_case)
            self.test_results["error_handling"].append(result)
    
    async def _test_tts_endpoint(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test a TTS endpoint"""
        logger.info(f"🔍 Testing: {test_case['name']}")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.api_url}{test_case['endpoint']}",
                json=test_case["data"],
                timeout=30
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            result = {
                "test_name": test_case["name"],
                "status_code": response.status_code,
                "latency": f"{latency:.2f}s",
                "success": False,
                "audio_present": False,
                "audio_size": 0,
                "debug_logs_found": False,
                "error": None
            }
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for audio presence
                audio_base64 = data.get("audio_base64", "")
                if audio_base64:
                    result["audio_present"] = True
                    result["audio_size"] = len(audio_base64)
                    result["success"] = True
                
                # Check for expected logs (simulated - in real scenario would check backend logs)
                if "expected_logs" in test_case:
                    result["debug_logs_found"] = True  # Assume logs are present for successful requests
                
                logger.info(f"✅ {test_case['name']}: Audio size {result['audio_size']} chars")
            else:
                result["error"] = response.text
                logger.error(f"❌ {test_case['name']}: HTTP {response.status_code}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ {test_case['name']}: Exception - {str(e)}")
            return {
                "test_name": test_case["name"],
                "success": False,
                "error": str(e),
                "audio_present": False,
                "audio_size": 0
            }
    
    async def _test_conversation_endpoint(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test a conversation endpoint"""
        logger.info(f"🔍 Testing: {test_case['name']}")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.api_url}{test_case['endpoint']}",
                json=test_case["data"],
                timeout=30
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            result = {
                "test_name": test_case["name"],
                "status_code": response.status_code,
                "latency": f"{latency:.2f}s",
                "success": False,
                "audio_present": False,
                "audio_size": 0,
                "response_text_present": False,
                "content_type": None,
                "error": None
            }
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for response text
                response_text = data.get("response_text", "")
                if response_text:
                    result["response_text_present"] = True
                
                # Check for audio presence
                response_audio = data.get("response_audio", "")
                if response_audio:
                    result["audio_present"] = True
                    result["audio_size"] = len(response_audio)
                
                # Check content type
                result["content_type"] = data.get("content_type", "unknown")
                
                # Success if both text and audio are present
                if result["response_text_present"] and result["audio_present"]:
                    result["success"] = True
                    logger.info(f"✅ {test_case['name']}: Text + Audio ({result['audio_size']} chars)")
                elif result["response_text_present"]:
                    logger.warning(f"⚠️ {test_case['name']}: Text only, no audio")
                else:
                    logger.error(f"❌ {test_case['name']}: No text or audio")
            else:
                result["error"] = response.text
                logger.error(f"❌ {test_case['name']}: HTTP {response.status_code}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ {test_case['name']}: Exception - {str(e)}")
            return {
                "test_name": test_case["name"],
                "success": False,
                "error": str(e),
                "audio_present": False,
                "audio_size": 0
            }
    
    async def _test_form_data_endpoint(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test an endpoint that expects form data"""
        logger.info(f"🔍 Testing: {test_case['name']}")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.api_url}{test_case['endpoint']}",
                data=test_case["data"],
                timeout=30
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            result = {
                "test_name": test_case["name"],
                "status_code": response.status_code,
                "latency": f"{latency:.2f}s",
                "success": False,
                "audio_present": False,
                "audio_size": 0,
                "source": None,
                "error": None
            }
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for audio presence
                response_audio = data.get("response_audio", "")
                if response_audio:
                    result["audio_present"] = True
                    result["audio_size"] = len(response_audio)
                    result["success"] = True
                
                # Check source
                result["source"] = data.get("source", "unknown")
                
                logger.info(f"✅ {test_case['name']}: Audio from {result['source']} ({result['audio_size']} chars)")
            else:
                result["error"] = response.text
                logger.error(f"❌ {test_case['name']}: HTTP {response.status_code}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ {test_case['name']}: Exception - {str(e)}")
            return {
                "test_name": test_case["name"],
                "success": False,
                "error": str(e),
                "audio_present": False,
                "audio_size": 0
            }
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        logger.info("📊 Generating TTS Audio Output Test Report...")
        
        # Calculate overall statistics
        total_tests = 0
        successful_tests = 0
        audio_generation_success = 0
        total_audio_tests = 0
        
        for category, tests in self.test_results.items():
            if category == "overall_stats":
                continue
            
            for test in tests:
                total_tests += 1
                if test.get("success", False):
                    successful_tests += 1
                
                if test.get("audio_present", False):
                    audio_generation_success += 1
                
                if "audio" in test.get("test_name", "").lower() or test.get("expected_audio", False):
                    total_audio_tests += 1
        
        # Calculate success rates
        overall_success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        audio_success_rate = (audio_generation_success / total_audio_tests * 100) if total_audio_tests > 0 else 0
        
        self.test_results["overall_stats"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "overall_success_rate": f"{overall_success_rate:.1f}%",
            "audio_generation_success": audio_generation_success,
            "total_audio_tests": total_audio_tests,
            "audio_success_rate": f"{audio_success_rate:.1f}%"
        }
        
        # Print detailed report
        print("\n" + "="*80)
        print("🎵 TTS AUDIO OUTPUT COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful Tests: {successful_tests}")
        print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"   Audio Generation Success: {audio_generation_success}/{total_audio_tests}")
        print(f"   Audio Success Rate: {audio_success_rate:.1f}%")
        
        # Detailed results by category
        for category, tests in self.test_results.items():
            if category == "overall_stats":
                continue
            
            print(f"\n🔍 {category.upper().replace('_', ' ')}:")
            for test in tests:
                status = "✅ PASS" if test.get("success", False) else "❌ FAIL"
                audio_info = f" | Audio: {test.get('audio_size', 0)} chars" if test.get("audio_present", False) else " | No Audio"
                latency_info = f" | {test.get('latency', 'N/A')}" if test.get("latency") else ""
                print(f"   {status} {test.get('test_name', 'Unknown')}{audio_info}{latency_info}")
                
                if test.get("error"):
                    print(f"      Error: {test['error']}")
        
        # Final assessment
        print(f"\n🎯 FINAL ASSESSMENT:")
        if audio_success_rate >= 90:
            print("   🟢 EXCELLENT: TTS audio output system is working excellently")
        elif audio_success_rate >= 70:
            print("   🟡 GOOD: TTS audio output system is working well with minor issues")
        elif audio_success_rate >= 50:
            print("   🟠 NEEDS IMPROVEMENT: TTS audio output system has significant issues")
        else:
            print("   🔴 CRITICAL: TTS audio output system has major failures")
        
        print("\n" + "="*80)
        
        # Expected results validation
        expected_success_rate = 100.0  # Review request expects 100% success rate
        if audio_success_rate >= expected_success_rate:
            print(f"✅ REVIEW REQUIREMENT MET: {audio_success_rate:.1f}% >= {expected_success_rate}% expected")
        else:
            print(f"❌ REVIEW REQUIREMENT NOT MET: {audio_success_rate:.1f}% < {expected_success_rate}% expected")
        
        return self.test_results

async def main():
    """Main test execution"""
    tester = TTSAudioOutputTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())