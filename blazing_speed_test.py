#!/usr/bin/env python3
"""
Blazing Speed Test - Verify <0.5s latency optimizations
Tests template system, prefetch cache, and parallel TTS
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime

class BlazingSpeedTester:
    def __init__(self):
        self.base_url = "https://6ddee563-7037-4e87-80ca-83a8a9a9bcae.preview.emergentagent.com/api"
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        self.blazing_threshold = 0.5  # <0.5s target
        self.acceptable_threshold = 2.0  # <2s acceptable
        
    async def test_template_system_speed(self):
        """Test template system for blazing speed"""
        print("\n🚀 TESTING TEMPLATE SYSTEM SPEED...")
        
        template_queries = [
            "tell me a story about a cat",
            "story about a brave mouse", 
            "tell me a fact about elephants",
            "joke about animals",
            "tell me about space",
            "fact about planets"
        ]
        
        async with aiohttp.ClientSession() as session:
            for query in template_queries:
                try:
                    data = {
                        "session_id": f"blazing_template_{int(time.time())}",
                        "user_id": "blazing_test_user",
                        "message": query
                    }
                    
                    start_time = time.time()
                    async with session.post(f"{self.base_url}/conversations/text", json=data, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        duration = time.time() - start_time
                        
                        if response.status == 200:
                            result = await response.json()
                            response_text = result.get("response_text", "")
                            word_count = len(response_text.split())
                            
                            # Check if it's blazing fast (<0.5s)
                            if duration < self.blazing_threshold:
                                status = "🚀 BLAZING"
                                self.tests_passed += 1
                            elif duration < self.acceptable_threshold:
                                status = "⚡ FAST"
                                self.tests_passed += 1
                            else:
                                status = "🐌 SLOW"
                                self.tests_failed += 1
                            
                            print(f"{status} Template '{query[:30]}...': {duration:.3f}s ({word_count} words)")
                            
                            self.test_results.append({
                                "test": "Template System",
                                "query": query,
                                "duration": duration,
                                "word_count": word_count,
                                "blazing": duration < self.blazing_threshold,
                                "status": status
                            })
                        else:
                            self.tests_failed += 1
                            print(f"❌ Template '{query[:30]}...': HTTP {response.status}")
                            
                except Exception as e:
                    self.tests_failed += 1
                    print(f"❌ Template '{query[:30]}...': Error - {str(e)}")
    
    async def test_parallel_tts_speed(self):
        """Test parallel TTS processing speed"""
        print("\n⚡ TESTING PARALLEL TTS SPEED...")
        
        tts_tests = [
            "This is a short test sentence for TTS.",
            "This is a longer test sentence that should trigger the parallel processing system for blazing fast text-to-speech generation with multiple chunks working simultaneously.",
            "Once upon a time, there was a brave little mouse who lived in a magical forest. The mouse loved to explore and discover new things every day. One morning, the mouse found a sparkling treasure that would lead to an amazing adventure full of friendship and wonder."
        ]
        
        async with aiohttp.ClientSession() as session:
            for i, text in enumerate(tts_tests):
                try:
                    data = {
                        "text": text,
                        "personality": "friendly_companion"
                    }
                    
                    start_time = time.time()
                    async with session.post(f"{self.base_url}/voice/tts", json=data, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        duration = time.time() - start_time
                        
                        if response.status == 200:
                            result = await response.json()
                            audio_size = len(result.get("audio_base64", ""))
                            text_length = len(text)
                            
                            # TTS speed targets: <1s for short, <2s for long
                            if text_length < 100 and duration < 1.0:
                                status = "🚀 BLAZING"
                                self.tests_passed += 1
                            elif text_length >= 100 and duration < 2.0:
                                status = "⚡ FAST" 
                                self.tests_passed += 1
                            elif duration < 5.0:
                                status = "✅ OK"
                                self.tests_passed += 1
                            else:
                                status = "🐌 SLOW"
                                self.tests_failed += 1
                            
                            print(f"{status} TTS Test {i+1}: {duration:.3f}s ({text_length} chars → {audio_size} audio)")
                            
                            self.test_results.append({
                                "test": "Parallel TTS",
                                "text_length": text_length,
                                "duration": duration,
                                "audio_size": audio_size,
                                "blazing": duration < (1.0 if text_length < 100 else 2.0),
                                "status": status
                            })
                        else:
                            self.tests_failed += 1
                            print(f"❌ TTS Test {i+1}: HTTP {response.status}")
                            
                except Exception as e:
                    self.tests_failed += 1
                    print(f"❌ TTS Test {i+1}: Error - {str(e)}")
    
    async def test_end_to_end_latency(self):
        """Test complete end-to-end latency"""
        print("\n🎯 TESTING END-TO-END LATENCY...")
        
        e2e_queries = [
            "hello",
            "how are you", 
            "tell me a joke",
            "what can you do",
            "story about friendship",
            "fact about cats"
        ]
        
        async with aiohttp.ClientSession() as session:
            for query in e2e_queries:
                try:
                    data = {
                        "session_id": f"blazing_e2e_{int(time.time())}",
                        "user_id": "blazing_test_user", 
                        "message": query
                    }
                    
                    start_time = time.time()
                    async with session.post(f"{self.base_url}/conversations/text", json=data, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        duration = time.time() - start_time
                        
                        if response.status == 200:
                            result = await response.json()
                            response_text = result.get("response_text", "")
                            word_count = len(response_text.split())
                            
                            # End-to-end blazing targets
                            if duration < self.blazing_threshold:
                                status = "🚀 BLAZING"
                                self.tests_passed += 1
                            elif duration < self.acceptable_threshold:
                                status = "⚡ FAST"
                                self.tests_passed += 1
                            else:
                                status = "🐌 SLOW"
                                self.tests_failed += 1
                            
                            print(f"{status} E2E '{query}': {duration:.3f}s ({word_count} words)")
                            
                            self.test_results.append({
                                "test": "End-to-End",
                                "query": query,
                                "duration": duration,
                                "word_count": word_count,
                                "blazing": duration < self.blazing_threshold,
                                "status": status
                            })
                        else:
                            self.tests_failed += 1
                            print(f"❌ E2E '{query}': HTTP {response.status}")
                            
                except Exception as e:
                    self.tests_failed += 1
                    print(f"❌ E2E '{query}': Error - {str(e)}")
    
    async def run_all_blazing_tests(self):
        """Run all blazing speed tests"""
        print("🚀 STARTING BLAZING SPEED TESTING...")
        print(f"🎯 TARGET: <{self.blazing_threshold}s for blazing, <{self.acceptable_threshold}s acceptable")
        start_time = time.time()
        
        await self.test_template_system_speed()
        await self.test_parallel_tts_speed()
        await self.test_end_to_end_latency()
        
        total_time = time.time() - start_time
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Count blazing speed results
        blazing_count = sum(1 for result in self.test_results if result.get("blazing", False))
        blazing_rate = (blazing_count / len(self.test_results) * 100) if self.test_results else 0
        
        print(f"\n🎯 BLAZING SPEED TEST RESULTS:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Blazing Speed Rate: {blazing_rate:.1f}% (<{self.blazing_threshold}s)")
        print(f"Total Duration: {total_time:.2f}s")
        
        # Performance categories
        blazing_results = [r for r in self.test_results if r.get("blazing", False)]
        fast_results = [r for r in self.test_results if r.get("status") == "⚡ FAST"]
        slow_results = [r for r in self.test_results if r.get("status") == "🐌 SLOW"]
        
        print(f"\n📊 PERFORMANCE BREAKDOWN:")
        print(f"🚀 BLAZING (<{self.blazing_threshold}s): {len(blazing_results)} tests")
        print(f"⚡ FAST (<{self.acceptable_threshold}s): {len(fast_results)} tests")  
        print(f"🐌 SLOW (>{self.acceptable_threshold}s): {len(slow_results)} tests")
        
        if blazing_results:
            avg_blazing = sum(r["duration"] for r in blazing_results) / len(blazing_results)
            print(f"🚀 Average blazing speed: {avg_blazing:.3f}s")
        
        # Save results
        results = {
            "total_tests": total_tests,
            "passed": self.tests_passed,
            "failed": self.tests_failed,
            "success_rate": success_rate,
            "blazing_rate": blazing_rate,
            "blazing_threshold": self.blazing_threshold,
            "acceptable_threshold": self.acceptable_threshold,
            "detailed_results": self.test_results,
            "summary": {
                "blazing_count": len(blazing_results),
                "fast_count": len(fast_results),
                "slow_count": len(slow_results)
            }
        }
        
        with open('/app/blazing_speed_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        if blazing_rate >= 50:
            print("\n🚀 BLAZING SPEED: EXCELLENT PERFORMANCE!")
        elif success_rate >= 80:
            print("\n⚡ FAST SPEED: GOOD PERFORMANCE!")
        else:
            print("\n🐌 OPTIMIZATION NEEDED")
        
        return results

if __name__ == "__main__":
    async def main():
        tester = BlazingSpeedTester()
        results = await tester.run_all_blazing_tests()
        print(f"\n🎯 Results saved to: /app/blazing_speed_results.json")
    
    asyncio.run(main())