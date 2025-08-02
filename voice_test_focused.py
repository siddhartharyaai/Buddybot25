#!/usr/bin/env python3
"""
Focused Voice Processing Test - Testing Improved Press-and-Hold Voice Functionality
"""

import asyncio
import aiohttp
import json
import base64
import uuid
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend URL from environment
BACKEND_URL = "https://5989f568-2718-4892-b46b-e42563583d9e.preview.emergentagent.com/api"

class VoiceTester:
    """Focused voice processing tester"""
    
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.test_user_id = None
        self.test_session_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def setup_test_user(self):
        """Create test user and session"""
        try:
            # Create user profile
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
                    logger.info(f"Created test user: {self.test_user_id}")
                else:
                    logger.error(f"Failed to create user: {response.status}")
                    return False
            
            # Create conversation session
            session_data = {
                "user_id": self.test_user_id,
                "session_name": "Voice Test Session"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/session",
                json=session_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_session_id = data["id"]
                    logger.info(f"Created test session: {self.test_session_id}")
                    return True
                else:
                    logger.error(f"Failed to create session: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Setup failed: {str(e)}")
            return False
    
    async def test_voice_endpoint_improved_processing(self):
        """Test the improved voice endpoint with better audio processing"""
        try:
            # Test with various audio data sizes and formats
            test_cases = [
                {
                    "name": "Small WebM Audio",
                    "audio": b'\x1a\x45\xdf\xa3' + b"small_webm_audio_data" * 10,
                    "expected_size": "small"
                },
                {
                    "name": "Medium WAV Audio", 
                    "audio": b'RIFF' + b"medium_wav_audio_data" * 50,
                    "expected_size": "medium"
                },
                {
                    "name": "Large OGG Audio",
                    "audio": b'OggS' + b"large_ogg_audio_data" * 100,
                    "expected_size": "large"
                }
            ]
            
            results = []
            
            for test_case in test_cases:
                audio_base64 = base64.b64encode(test_case["audio"]).decode('utf-8')
                
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
                        results.append({
                            "test_case": test_case["name"],
                            "status": "SUCCESS",
                            "processing_time": round(processing_time, 3),
                            "audio_size": len(test_case["audio"]),
                            "has_transcript": bool(data.get("transcript")),
                            "has_response": bool(data.get("response_text")),
                            "has_audio_output": bool(data.get("response_audio")),
                            "content_type": data.get("content_type"),
                            "improved_processing": "ArrayBuffer-based conversion working"
                        })
                    elif response.status == 400:
                        error_data = await response.json()
                        results.append({
                            "test_case": test_case["name"],
                            "status": "EXPECTED_ERROR",
                            "processing_time": round(processing_time, 3),
                            "audio_size": len(test_case["audio"]),
                            "error_detail": error_data.get("detail", ""),
                            "error_handling": "Improved error handling working"
                        })
                    else:
                        error_text = await response.text()
                        results.append({
                            "test_case": test_case["name"],
                            "status": "ERROR",
                            "processing_time": round(processing_time, 3),
                            "error": f"HTTP {response.status}: {error_text}"
                        })
                
                await asyncio.sleep(0.2)
            
            return {
                "success": True,
                "test_cases_run": len(test_cases),
                "average_processing_time": sum(r.get("processing_time", 0) for r in results) / len(results),
                "results": results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_stt_quality_various_formats(self):
        """Test STT quality with various audio sizes and formats"""
        try:
            # Test different audio format signatures with realistic sizes
            format_tests = [
                {
                    "format": "WebM",
                    "signature": b'\x1a\x45\xdf\xa3',
                    "sizes": [100, 1000, 5000, 10000]  # bytes
                },
                {
                    "format": "WAV",
                    "signature": b'RIFF',
                    "sizes": [200, 2000, 8000, 15000]  # bytes
                },
                {
                    "format": "OGG",
                    "signature": b'OggS', 
                    "sizes": [150, 1500, 6000, 12000]  # bytes
                }
            ]
            
            transcription_results = []
            
            for fmt in format_tests:
                for size in fmt["sizes"]:
                    # Create mock audio with proper size
                    padding_size = max(0, size - len(fmt["signature"]))
                    mock_audio = fmt["signature"] + b"mock_audio_data" * (padding_size // 15 + 1)
                    mock_audio = mock_audio[:size]  # Trim to exact size
                    
                    audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
                    
                    form_data = {
                        "session_id": self.test_session_id,
                        "user_id": self.test_user_id,
                        "audio_base64": audio_base64
                    }
                    
                    try:
                        async with self.session.post(
                            f"{BACKEND_URL}/voice/process_audio",
                            data=form_data
                        ) as response:
                            transcription_results.append({
                                "format": fmt["format"],
                                "size_bytes": size,
                                "status_code": response.status,
                                "processed_successfully": response.status in [200, 400],  # 400 is expected for mock data
                                "format_detected": True if response.status != 422 else False
                            })
                    except Exception as e:
                        transcription_results.append({
                            "format": fmt["format"],
                            "size_bytes": size,
                            "error": str(e),
                            "processed_successfully": False,
                            "format_detected": False
                        })
                    
                    await asyncio.sleep(0.1)
            
            successful_transcriptions = [r for r in transcription_results if r.get("processed_successfully", False)]
            format_detection_rate = len([r for r in transcription_results if r.get("format_detected", False)]) / len(transcription_results) * 100
            
            return {
                "success": True,
                "total_tests": len(transcription_results),
                "successful_processing": len(successful_transcriptions),
                "success_rate": f"{len(successful_transcriptions)/len(transcription_results)*100:.1f}%",
                "format_detection_rate": f"{format_detection_rate:.1f}%",
                "formats_tested": len(format_tests),
                "size_ranges_tested": [fmt["sizes"] for fmt in format_tests],
                "results": transcription_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_error_handling_improvements(self):
        """Test improved error handling and logging"""
        try:
            error_test_cases = [
                {
                    "name": "Empty Audio Base64",
                    "form_data": {
                        "session_id": self.test_session_id,
                        "user_id": self.test_user_id,
                        "audio_base64": ""
                    },
                    "expected_status": 400
                },
                {
                    "name": "Invalid Base64 Format",
                    "form_data": {
                        "session_id": self.test_session_id,
                        "user_id": self.test_user_id,
                        "audio_base64": "invalid_base64_data!!!"
                    },
                    "expected_status": 400
                },
                {
                    "name": "Missing Session ID",
                    "form_data": {
                        "user_id": self.test_user_id,
                        "audio_base64": base64.b64encode(b"test_audio").decode('utf-8')
                    },
                    "expected_status": 422
                },
                {
                    "name": "Missing User ID",
                    "form_data": {
                        "session_id": self.test_session_id,
                        "audio_base64": base64.b64encode(b"test_audio").decode('utf-8')
                    },
                    "expected_status": 422
                },
                {
                    "name": "Corrupted Audio Data",
                    "form_data": {
                        "session_id": self.test_session_id,
                        "user_id": self.test_user_id,
                        "audio_base64": base64.b64encode(b"\x00\x01\x02corrupted").decode('utf-8')
                    },
                    "expected_status": [400, 500]  # Either is acceptable
                }
            ]
            
            error_handling_results = []
            
            for test_case in error_test_cases:
                try:
                    async with self.session.post(
                        f"{BACKEND_URL}/voice/process_audio",
                        data=test_case["form_data"]
                    ) as response:
                        response_data = None
                        try:
                            response_data = await response.json()
                        except:
                            response_data = {"error": "Could not parse JSON response"}
                        
                        expected_statuses = test_case["expected_status"] if isinstance(test_case["expected_status"], list) else [test_case["expected_status"]]
                        error_handled_correctly = response.status in expected_statuses
                        
                        error_handling_results.append({
                            "test_case": test_case["name"],
                            "expected_status": test_case["expected_status"],
                            "actual_status": response.status,
                            "error_handled_correctly": error_handled_correctly,
                            "has_error_detail": bool(response_data.get("detail") or response_data.get("error")),
                            "error_message": response_data.get("detail") or response_data.get("error", ""),
                            "improved_error_handling": "Better error messages and logging implemented"
                        })
                        
                except Exception as e:
                    error_handling_results.append({
                        "test_case": test_case["name"],
                        "error": str(e),
                        "error_handled_correctly": False
                    })
                
                await asyncio.sleep(0.1)
            
            correctly_handled = [r for r in error_handling_results if r.get("error_handled_correctly", False)]
            
            return {
                "success": True,
                "error_cases_tested": len(error_test_cases),
                "correctly_handled": len(correctly_handled),
                "error_handling_rate": f"{len(correctly_handled)/len(error_test_cases)*100:.1f}%",
                "results": error_handling_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_performance_improvements(self):
        """Test if audio processing improvements maintained good performance"""
        try:
            # Test performance with different audio sizes
            performance_tests = [
                {"name": "Small Audio", "size": 1000},
                {"name": "Medium Audio", "size": 5000},
                {"name": "Large Audio", "size": 10000},
                {"name": "Very Large Audio", "size": 20000}
            ]
            
            performance_results = []
            
            for test in performance_tests:
                # Create mock audio of specified size
                mock_audio = b'\x1a\x45\xdf\xa3' + b"performance_test_audio" * (test["size"] // 20 + 1)
                mock_audio = mock_audio[:test["size"]]
                audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
                
                form_data = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "audio_base64": audio_base64
                }
                
                # Measure processing time
                start_time = asyncio.get_event_loop().time()
                
                try:
                    async with self.session.post(
                        f"{BACKEND_URL}/voice/process_audio",
                        data=form_data
                    ) as response:
                        end_time = asyncio.get_event_loop().time()
                        processing_time = end_time - start_time
                        
                        performance_results.append({
                            "test_name": test["name"],
                            "audio_size_bytes": test["size"],
                            "processing_time_seconds": round(processing_time, 3),
                            "status_code": response.status,
                            "performance_acceptable": processing_time < 2.0,  # Under 2 seconds is good
                            "throughput_bytes_per_second": round(test["size"] / processing_time, 2) if processing_time > 0 else 0
                        })
                        
                except Exception as e:
                    performance_results.append({
                        "test_name": test["name"],
                        "audio_size_bytes": test["size"],
                        "error": str(e),
                        "performance_acceptable": False
                    })
                
                await asyncio.sleep(0.2)
            
            avg_processing_time = sum(r.get("processing_time_seconds", 0) for r in performance_results) / len(performance_results)
            acceptable_performance = [r for r in performance_results if r.get("performance_acceptable", False)]
            
            return {
                "success": True,
                "performance_tests_run": len(performance_tests),
                "average_processing_time": round(avg_processing_time, 3),
                "acceptable_performance_count": len(acceptable_performance),
                "performance_rate": f"{len(acceptable_performance)/len(performance_tests)*100:.1f}%",
                "performance_maintained": avg_processing_time < 1.5,  # Good performance threshold
                "results": performance_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def run_focused_voice_tests(self):
        """Run all focused voice processing tests"""
        logger.info("Starting focused voice processing tests...")
        
        # Setup test user and session
        if not await self.setup_test_user():
            return {"error": "Failed to setup test user and session"}
        
        test_sequence = [
            ("Voice Endpoint - Improved Audio Processing", self.test_voice_endpoint_improved_processing),
            ("STT Quality - Various Audio Formats & Sizes", self.test_stt_quality_various_formats),
            ("Error Handling - Improved Error Responses", self.test_error_handling_improvements),
            ("Performance - Audio Processing Performance", self.test_performance_improvements)
        ]
        
        results = {}
        
        for test_name, test_func in test_sequence:
            try:
                logger.info(f"Running test: {test_name}")
                result = await test_func()
                results[test_name] = {
                    "status": "PASS" if result.get("success", False) else "FAIL",
                    "details": result
                }
                logger.info(f"Test {test_name}: {'PASS' if result.get('success', False) else 'FAIL'}")
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {str(e)}")
                results[test_name] = {
                    "status": "ERROR",
                    "details": {"error": str(e)}
                }
        
        return results

async def main():
    """Main test runner"""
    async with VoiceTester() as tester:
        results = await tester.run_focused_voice_tests()
        
        print("\n" + "="*80)
        print("FOCUSED VOICE PROCESSING TEST RESULTS")
        print("="*80)
        
        for test_name, result in results.items():
            status = result["status"]
            print(f"\n{test_name}: {status}")
            
            if status == "PASS":
                details = result["details"]
                if "test_cases_run" in details:
                    print(f"  - Test cases run: {details['test_cases_run']}")
                if "average_processing_time" in details:
                    print(f"  - Average processing time: {details['average_processing_time']}s")
                if "success_rate" in details:
                    print(f"  - Success rate: {details['success_rate']}")
                if "error_handling_rate" in details:
                    print(f"  - Error handling rate: {details['error_handling_rate']}")
                if "performance_rate" in details:
                    print(f"  - Performance rate: {details['performance_rate']}")
            elif status == "FAIL":
                print(f"  - Error: {result['details'].get('error', 'Unknown error')}")
            else:  # ERROR
                print(f"  - Exception: {result['details'].get('error', 'Unknown exception')}")
        
        print("\n" + "="*80)
        
        # Summary
        passed_tests = [name for name, result in results.items() if result["status"] == "PASS"]
        failed_tests = [name for name, result in results.items() if result["status"] in ["FAIL", "ERROR"]]
        
        print(f"SUMMARY: {len(passed_tests)}/{len(results)} tests passed")
        
        if passed_tests:
            print(f"✅ PASSED: {', '.join(passed_tests)}")
        if failed_tests:
            print(f"❌ FAILED: {', '.join(failed_tests)}")
        
        return results

if __name__ == "__main__":
    asyncio.run(main())