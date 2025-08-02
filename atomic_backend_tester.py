#!/usr/bin/env python3
"""
Atomic Backend Testing - Focus on finding and fixing EVERY bug
Tests each endpoint individually with comprehensive edge cases
"""

import asyncio
import aiohttp
import json
import time
import sys
from typing import Dict, Any, List

class AtomicBackendTester:
    def __init__(self):
        self.base_url = "https://5989f568-2718-4892-b46b-e42563583d9e.preview.emergentagent.com/api"
        self.bugs_found = []
        self.tests_passed = 0
        self.tests_failed = 0
        
    async def test_endpoint(self, method: str, endpoint: str, data: Dict = None, 
                           expected_status: int = 200, timeout: int = 30) -> Dict:
        """Test individual endpoint with detailed analysis"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                start_time = time.time()
                
                if method == 'GET':
                    async with session.get(url) as response:
                        duration = time.time() - start_time
                        try:
                            result = await response.json()
                        except:
                            result = await response.text()
                        
                        return {
                            "success": response.status == expected_status,
                            "status": response.status,
                            "data": result,
                            "duration": duration,
                            "method": method,
                            "endpoint": endpoint
                        }
                
                elif method == 'POST':
                    headers = {'Content-Type': 'application/json'}
                    async with session.post(url, json=data, headers=headers) as response:
                        duration = time.time() - start_time
                        try:
                            result = await response.json()
                        except:
                            result = await response.text()
                        
                        return {
                            "success": response.status == expected_status,
                            "status": response.status,
                            "data": result,
                            "duration": duration,
                            "method": method,
                            "endpoint": endpoint
                        }
                        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "status": 408,
                "data": "Timeout",
                "duration": timeout,
                "method": method,
                "endpoint": endpoint,
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "status": 500,
                "data": str(e),
                "duration": 0,
                "method": method,
                "endpoint": endpoint,
                "error": str(e)
            }
    
    def log_result(self, test_name: str, result: Dict):
        """Log test result and track bugs"""
        if result["success"]:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASS ({result['duration']:.3f}s)")
        else:
            self.tests_failed += 1
            print(f"❌ {test_name}: FAIL - Status {result['status']} ({result['duration']:.3f}s)")
            print(f"   Error: {result.get('error', result['data'])}")
            
            self.bugs_found.append({
                "test": test_name,
                "endpoint": result["endpoint"],
                "method": result["method"],
                "status": result["status"],
                "error": result.get("error", result["data"]),
                "duration": result["duration"]
            })
    
    async def test_critical_endpoints(self):
        """Test the most critical endpoints first"""
        print("\n🔥 TESTING CRITICAL ENDPOINTS...")
        
        # Health check
        result = await self.test_endpoint('GET', '/health')
        self.log_result("Health Check", result)
        
        # Basic conversation
        test_data = {
            "session_id": "test_session",
            "user_id": "test_user",
            "message": "Hello"
        }
        result = await self.test_endpoint('POST', '/conversations/text', test_data, timeout=30)
        self.log_result("Basic Conversation", result)
        
        # Story generation (critical for app)
        story_data = {
            "session_id": "test_session",
            "user_id": "test_user", 
            "message": "Tell me a short story"
        }
        result = await self.test_endpoint('POST', '/conversations/text', story_data, timeout=60)
        self.log_result("Story Generation", result)
        
        # Voice personalities
        result = await self.test_endpoint('GET', '/voice/personalities')
        self.log_result("Voice Personalities", result)
        
        # TTS basic
        tts_data = {
            "text": "Hello world",
            "personality": "friendly_companion"
        }
        result = await self.test_endpoint('POST', '/voice/tts', tts_data)
        self.log_result("TTS Basic", result)
        
        # User profile creation
        profile_data = {
            "name": "Test Child",
            "age": 7,
            "interests": ["stories"],
            "voice_personality": "friendly_companion"
        }
        result = await self.test_endpoint('POST', '/users/profile', profile_data, expected_status=201)
        self.log_result("Profile Creation", result)
        
    async def test_edge_cases(self):
        """Test edge cases and error conditions"""
        print("\n⚠️ TESTING EDGE CASES...")
        
        # Empty message
        empty_data = {
            "session_id": "test_session",
            "user_id": "test_user",
            "message": ""
        }
        result = await self.test_endpoint('POST', '/conversations/text', empty_data, expected_status=400)
        self.log_result("Empty Message", result)
        
        # Very long message
        long_data = {
            "session_id": "test_session", 
            "user_id": "test_user",
            "message": "Tell me a story " * 1000  # Very long
        }
        result = await self.test_endpoint('POST', '/conversations/text', long_data, timeout=90)
        self.log_result("Very Long Message", result)
        
        # Invalid user profile
        invalid_profile = {
            "name": "",  # Empty name
            "age": -5,   # Invalid age
            "interests": []
        }
        result = await self.test_endpoint('POST', '/users/profile', invalid_profile, expected_status=400)
        self.log_result("Invalid Profile", result)
        
        # TTS with empty text
        empty_tts = {
            "text": "",
            "personality": "friendly_companion"
        }
        result = await self.test_endpoint('POST', '/voice/tts', empty_tts, expected_status=400)
        self.log_result("Empty TTS", result)
        
    async def run_all_tests(self):
        """Run all atomic tests"""
        print("🚀 STARTING ATOMIC BACKEND TESTING...")
        start_time = time.time()
        
        await self.test_critical_endpoints()
        await self.test_edge_cases()
        
        total_time = time.time() - start_time
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 TEST RESULTS:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Duration: {total_time:.2f}s")
        print(f"Bugs Found: {len(self.bugs_found)}")
        
        if self.bugs_found:
            print(f"\n🐛 BUGS FOUND:")
            for i, bug in enumerate(self.bugs_found, 1):
                print(f"{i}. {bug['test']}: {bug['method']} {bug['endpoint']} -> {bug['status']} ({bug['error']})")
        
        return {
            "total_tests": total_tests,
            "passed": self.tests_passed,
            "failed": self.tests_failed,
            "success_rate": success_rate,
            "bugs": self.bugs_found,
            "duration": total_time
        }

if __name__ == "__main__":
    async def main():
        tester = AtomicBackendTester()
        results = await tester.run_all_tests()
        
        # Save results
        with open('/app/atomic_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n🎯 Results saved to: /app/atomic_test_results.json")
        
        if results['success_rate'] < 100:
            print(f"❌ {results['failed']} BUGS NEED FIXING!")
            sys.exit(1)
        else:
            print("✅ ALL ATOMIC TESTS PASSED!")
    
    asyncio.run(main())