#!/usr/bin/env python3
"""
Priority Backend Testing for Template System Optimizations
Focus: Template System, Prefetch Cache, Intent Detection, Story Generation
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PriorityBackendTester:
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
        
        logger.info(f"🎯 PRIORITY TESTING: Using backend URL: {self.base_url}")
        
        # Test data
        self.test_user_id = f"priority_test_{int(time.time())}"
        self.test_session_id = f"priority_session_{int(time.time())}"
        
        # Results tracking
        self.results = []
        
    async def run_priority_tests(self):
        """Run priority tests"""
        logger.info("🎯 STARTING PRIORITY BACKEND TESTING")
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            self.session = session
            
            # Create test user
            await self._create_test_user()
            
            # Priority Test 1: Template System & Conversation Suggestions
            await self._test_conversation_suggestions()
            
            # Priority Test 2: Prefetch Cache Performance  
            await self._test_cache_performance()
            
            # Priority Test 3: Template Intent Detection
            await self._test_intent_detection()
            
            # Priority Test 4: Story Generation & Processing
            await self._test_story_generation()
            
            # Priority Test 5: API Endpoint Health
            await self._test_api_health()
            
        # Generate report
        await self._generate_report()
    
    async def _create_test_user(self):
        """Create test user profile"""
        try:
            profile_data = {
                "name": f"PriorityTestUser_{int(time.time())}",
                "age": 7,
                "location": "Test City",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "jokes", "facts"]
            }
            
            async with self.session.post(f"{self.base_url}/users/profile", json=profile_data) as response:
                if response.status == 201:
                    result = await response.json()
                    self.test_user_id = result["id"]
                    logger.info(f"✅ Created test user: {self.test_user_id}")
                    return True
                else:
                    logger.error(f"❌ Failed to create user: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ User creation error: {e}")
            return False
    
    async def _test_conversation_suggestions(self):
        """Priority Test 1: Template System & Conversation Suggestions"""
        logger.info("🎯 PRIORITY TEST 1: Template System & Conversation Suggestions")
        
        try:
            # Test new /api/conversations/suggestions endpoint
            async with self.session.get(f"{self.base_url}/conversations/suggestions") as response:
                if response.status == 200:
                    suggestions = await response.json()
                    if isinstance(suggestions, list) and len(suggestions) >= 5:
                        unique_suggestions = set(suggestions)
                        if len(unique_suggestions) >= 4:
                            self.results.append({
                                "test": "✅ Template System - Conversation Suggestions Endpoint",
                                "status": "PASS",
                                "details": f"Dynamic suggestions working: {len(suggestions)} total, {len(unique_suggestions)} unique"
                            })
                        else:
                            self.results.append({
                                "test": "⚠️ Template System - Conversation Suggestions Endpoint", 
                                "status": "PARTIAL",
                                "details": f"Limited variety: {len(unique_suggestions)} unique out of {len(suggestions)}"
                            })
                    else:
                        self.results.append({
                            "test": "❌ Template System - Conversation Suggestions Endpoint",
                            "status": "FAIL", 
                            "details": f"Insufficient suggestions: {len(suggestions) if isinstance(suggestions, list) else 'Not a list'}"
                        })
                else:
                    self.results.append({
                        "test": "❌ Template System - Conversation Suggestions Endpoint",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            self.results.append({
                "test": "🔥 Template System - Conversation Suggestions Endpoint",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test template variables usage
        try:
            async with self.session.get(f"{self.base_url}/content/suggestions/{self.test_user_id}") as response:
                if response.status == 200:
                    suggestions = await response.json()
                    if isinstance(suggestions, list) and len(suggestions) > 0:
                        self.results.append({
                            "test": "✅ Template Variables Usage",
                            "status": "PASS",
                            "details": f"Personalized suggestions: {len(suggestions)} suggestions generated"
                        })
                    else:
                        self.results.append({
                            "test": "❌ Template Variables Usage",
                            "status": "FAIL",
                            "details": "No personalized suggestions returned"
                        })
                else:
                    self.results.append({
                        "test": "❌ Template Variables Usage",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            self.results.append({
                "test": "🔥 Template Variables Usage",
                "status": "ERROR",
                "details": str(e)
            })
    
    async def _test_cache_performance(self):
        """Priority Test 2: Prefetch Cache Performance"""
        logger.info("🎯 PRIORITY TEST 2: Prefetch Cache Performance")
        
        try:
            # Check cache stats
            async with self.session.get(f"{self.base_url}/admin/cache-stats") as response:
                if response.status == 200:
                    cache_stats = await response.json()
                    if cache_stats.get("status") == "success":
                        total_cached = cache_stats.get("database_cache", {}).get("total_records", 0)
                        memory_size = cache_stats.get("memory_cache", {}).get("content_cache_size", 0)
                        
                        if total_cached > 18:  # Should have more than 18 entries
                            self.results.append({
                                "test": "✅ Prefetch Cache Population",
                                "status": "PASS",
                                "details": f"Cache above threshold: DB={total_cached}, Memory={memory_size} (>18 required)"
                            })
                        else:
                            self.results.append({
                                "test": "❌ Prefetch Cache Population",
                                "status": "FAIL",
                                "details": f"Cache below threshold: DB={total_cached}, Memory={memory_size} (need >18)"
                            })
                    else:
                        self.results.append({
                            "test": "❌ Prefetch Cache Population",
                            "status": "FAIL",
                            "details": f"Cache stats failed: {cache_stats}"
                        })
                else:
                    self.results.append({
                        "test": "❌ Prefetch Cache Population",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            self.results.append({
                "test": "🔥 Prefetch Cache Population",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test blazing latency responses
        try:
            latencies = []
            for i in range(3):
                start_time = time.time()
                
                text_request = {
                    "session_id": self.test_session_id,
                    "message": "Hello",
                    "user_id": self.test_user_id
                }
                
                async with self.session.post(f"{self.base_url}/conversations/text", json=text_request) as response:
                    if response.status == 200:
                        latency = time.time() - start_time
                        latencies.append(latency)
                    else:
                        latencies.append(999)
                
                await asyncio.sleep(0.1)
            
            avg_latency = sum(latencies) / len(latencies) if latencies else 999
            
            if avg_latency < 0.5:  # Blazing fast
                self.results.append({
                    "test": "✅ Blazing Latency Cached Responses",
                    "status": "PASS",
                    "details": f"Blazing fast: {avg_latency:.3f}s average latency"
                })
            elif avg_latency < 2.0:  # Good
                self.results.append({
                    "test": "⚠️ Blazing Latency Cached Responses",
                    "status": "PARTIAL",
                    "details": f"Good but not blazing: {avg_latency:.3f}s average latency"
                })
            else:
                self.results.append({
                    "test": "❌ Blazing Latency Cached Responses",
                    "status": "FAIL",
                    "details": f"Slow responses: {avg_latency:.3f}s average latency"
                })
                
        except Exception as e:
            self.results.append({
                "test": "🔥 Blazing Latency Cached Responses",
                "status": "ERROR",
                "details": str(e)
            })
    
    async def _test_intent_detection(self):
        """Priority Test 3: Template Intent Detection"""
        logger.info("🎯 PRIORITY TEST 3: Template Intent Detection")
        
        # Test story intent detection
        story_requests = [
            "Tell me a story about a brave mouse",
            "I want a fairy tale",
            "Can you tell me a bedtime story?"
        ]
        
        story_success = 0
        blazing_responses = 0
        
        for story_request in story_requests:
            try:
                start_time = time.time()
                text_request = {
                    "session_id": self.test_session_id,
                    "message": story_request,
                    "user_id": self.test_user_id
                }
                
                async with self.session.post(f"{self.base_url}/conversations/text", json=text_request) as response:
                    if response.status == 200:
                        result = await response.json()
                        processing_time = time.time() - start_time
                        
                        response_text = result.get("response_text", "")
                        
                        # Check if story detected (longer response)
                        if len(response_text) > 100:
                            story_success += 1
                        
                        # Check if blazing fast
                        if processing_time < 1.0:
                            blazing_responses += 1
                            
            except Exception:
                pass
        
        if story_success >= len(story_requests) * 0.75:
            self.results.append({
                "test": "✅ Story Intent Detection",
                "status": "PASS",
                "details": f"Detected {story_success}/{len(story_requests)} story requests correctly"
            })
        else:
            self.results.append({
                "test": "❌ Story Intent Detection",
                "status": "FAIL",
                "details": f"Only detected {story_success}/{len(story_requests)} story requests"
            })
        
        if blazing_responses >= len(story_requests) * 0.75:
            self.results.append({
                "test": "✅ Blazing Speed Intent Processing",
                "status": "PASS",
                "details": f"{blazing_responses}/{len(story_requests)} responses were blazing fast (<1s)"
            })
        else:
            self.results.append({
                "test": "❌ Blazing Speed Intent Processing",
                "status": "FAIL",
                "details": f"Only {blazing_responses}/{len(story_requests)} responses were fast enough"
            })
        
        # Test fact intent detection
        fact_requests = [
            "Tell me a fact about animals",
            "What's interesting about space?",
            "Give me a fun fact"
        ]
        
        fact_success = 0
        for fact_request in fact_requests:
            try:
                text_request = {
                    "session_id": self.test_session_id,
                    "message": fact_request,
                    "user_id": self.test_user_id
                }
                
                async with self.session.post(f"{self.base_url}/conversations/text", json=text_request) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "")
                        
                        # Facts should be concise but informative
                        if 20 < len(response_text) < 300:
                            fact_success += 1
                            
            except Exception:
                pass
        
        if fact_success >= len(fact_requests) * 0.75:
            self.results.append({
                "test": "✅ Fact Intent Detection",
                "status": "PASS",
                "details": f"Generated appropriate facts for {fact_success}/{len(fact_requests)} requests"
            })
        else:
            self.results.append({
                "test": "❌ Fact Intent Detection",
                "status": "FAIL",
                "details": f"Only {fact_success}/{len(fact_requests)} appropriate fact responses"
            })
    
    async def _test_story_generation(self):
        """Priority Test 4: Story Generation & Processing"""
        logger.info("🎯 PRIORITY TEST 4: Story Generation & Processing")
        
        # Test story generation quality
        story_prompts = [
            "Tell me a story about a brave little mouse",
            "I want a fairy tale about a princess",
            "Can you tell me a bedtime story about friendship?"
        ]
        
        story_quality_success = 0
        processing_times = []
        
        for prompt in story_prompts:
            try:
                start_time = time.time()
                text_request = {
                    "session_id": self.test_session_id,
                    "message": prompt,
                    "user_id": self.test_user_id
                }
                
                async with self.session.post(f"{self.base_url}/conversations/text", json=text_request) as response:
                    if response.status == 200:
                        result = await response.json()
                        processing_time = time.time() - start_time
                        processing_times.append(processing_time)
                        
                        response_text = result.get("response_text", "")
                        word_count = len(response_text.split())
                        
                        # Check story quality
                        has_good_length = word_count >= 50
                        has_story_elements = any(word in response_text.lower() for word in ['once', 'story', 'adventure', 'character'])
                        
                        if has_good_length and has_story_elements:
                            story_quality_success += 1
                            
            except Exception:
                pass
        
        if story_quality_success >= len(story_prompts) * 0.75:
            avg_word_count = sum([len(r.split()) for r in [""]*story_quality_success]) / max(story_quality_success, 1)
            self.results.append({
                "test": "✅ Story Generation Quality",
                "status": "PASS",
                "details": f"Generated {story_quality_success}/{len(story_prompts)} quality stories"
            })
        else:
            self.results.append({
                "test": "❌ Story Generation Quality",
                "status": "FAIL",
                "details": f"Only {story_quality_success}/{len(story_prompts)} quality stories generated"
            })
        
        # Check processing speed
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 999
        
        if avg_processing_time < 3.0:
            self.results.append({
                "test": "✅ Story Generation Speed",
                "status": "PASS",
                "details": f"Optimized processing: {avg_processing_time:.2f}s average"
            })
        else:
            self.results.append({
                "test": "❌ Story Generation Speed",
                "status": "FAIL",
                "details": f"Slow processing: {avg_processing_time:.2f}s average (needs optimization)"
            })
        
        # Test story streaming
        try:
            story_stream_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "text": "Tell me a complete story about a magical adventure"
            }
            
            async with self.session.post(f"{self.base_url}/stories/stream", json=story_stream_request) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success" and result.get("story_mode"):
                        total_chunks = result.get("total_chunks", 0)
                        total_words = result.get("total_words", 0)
                        
                        if total_chunks > 1 and total_words > 100:
                            self.results.append({
                                "test": "✅ Story Streaming Functionality",
                                "status": "PASS",
                                "details": f"Streaming working: {total_chunks} chunks, {total_words} words"
                            })
                        else:
                            self.results.append({
                                "test": "⚠️ Story Streaming Functionality",
                                "status": "PARTIAL",
                                "details": f"Limited streaming: {total_chunks} chunks, {total_words} words"
                            })
                    else:
                        self.results.append({
                            "test": "❌ Story Streaming Functionality",
                            "status": "FAIL",
                            "details": f"Streaming not working: {result}"
                        })
                else:
                    self.results.append({
                        "test": "❌ Story Streaming Functionality",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            self.results.append({
                "test": "🔥 Story Streaming Functionality",
                "status": "ERROR",
                "details": str(e)
            })
    
    async def _test_api_health(self):
        """Priority Test 5: API Endpoint Health"""
        logger.info("🎯 PRIORITY TEST 5: API Endpoint Health")
        
        # Test key endpoints
        endpoints = [
            ("GET", "/health", None),
            ("GET", "/agents/status", None),
            ("GET", "/voice/personalities", None)
        ]
        
        working_endpoints = 0
        
        for method, endpoint, data in endpoints:
            try:
                if method == "GET":
                    async with self.session.get(f"{self.base_url}{endpoint}") as response:
                        if response.status == 200:
                            working_endpoints += 1
                            
            except Exception:
                pass
        
        if working_endpoints >= len(endpoints) * 0.75:
            self.results.append({
                "test": "✅ Core API Endpoints Health",
                "status": "PASS",
                "details": f"Working endpoints: {working_endpoints}/{len(endpoints)}"
            })
        else:
            self.results.append({
                "test": "❌ Core API Endpoints Health",
                "status": "FAIL",
                "details": f"Failed endpoints: {len(endpoints) - working_endpoints}/{len(endpoints)}"
            })
        
        # Test database connectivity
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    if health_data.get("database") == "connected":
                        self.results.append({
                            "test": "✅ Database Connectivity",
                            "status": "PASS",
                            "details": "Database connected and operational"
                        })
                    else:
                        self.results.append({
                            "test": "❌ Database Connectivity",
                            "status": "FAIL",
                            "details": f"Database not connected: {health_data.get('database')}"
                        })
                else:
                    self.results.append({
                        "test": "❌ Database Connectivity",
                        "status": "FAIL",
                        "details": f"Health check failed: HTTP {response.status}"
                    })
                    
        except Exception as e:
            self.results.append({
                "test": "🔥 Database Connectivity",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test voice processing
        try:
            tts_request = {
                "text": "This is a voice processing test",
                "personality": "friendly_companion"
            }
            
            async with self.session.post(f"{self.base_url}/voice/tts", json=tts_request) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success" and result.get("audio_base64"):
                        self.results.append({
                            "test": "✅ Voice Processing Capabilities",
                            "status": "PASS",
                            "details": f"TTS working: {len(result.get('audio_base64', ''))} chars audio"
                        })
                    else:
                        self.results.append({
                            "test": "❌ Voice Processing Capabilities",
                            "status": "FAIL",
                            "details": f"TTS not working: {result}"
                        })
                else:
                    self.results.append({
                        "test": "❌ Voice Processing Capabilities",
                        "status": "FAIL",
                        "details": f"TTS failed: HTTP {response.status}"
                    })
                    
        except Exception as e:
            self.results.append({
                "test": "🔥 Voice Processing Capabilities",
                "status": "ERROR",
                "details": str(e)
            })
    
    async def _generate_report(self):
        """Generate test report"""
        logger.info("🎯 GENERATING PRIORITY BACKEND TEST REPORT")
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASS'])
        partial_tests = len([r for r in self.results if r['status'] == 'PARTIAL'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.results if r['status'] == 'ERROR'])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("PRIORITY BACKEND TESTING REPORT - TEMPLATE SYSTEM OPTIMIZATIONS")
        print("=" * 80)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Backend URL: {self.base_url}")
        print(f"Test User ID: {self.test_user_id}")
        print("")
        
        print("📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ⚠️  Partial: {partial_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   🔥 Errors: {error_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print("")
        
        print("🎯 DETAILED TEST RESULTS:")
        for result in self.results:
            print(f"   {result['test']}")
            print(f"      Status: {result['status']}")
            print(f"      Details: {result['details']}")
            print("")
        
        print("🎯 PRIORITY AREAS ASSESSMENT:")
        print("")
        
        # Analyze by priority areas
        template_tests = [r for r in self.results if 'Template' in r['test']]
        cache_tests = [r for r in self.results if 'Cache' in r['test'] or 'Latency' in r['test']]
        intent_tests = [r for r in self.results if 'Intent' in r['test'] or 'Detection' in r['test']]
        story_tests = [r for r in self.results if 'Story' in r['test']]
        api_tests = [r for r in self.results if 'API' in r['test'] or 'Database' in r['test'] or 'Voice' in r['test']]
        
        def assess_area(tests, area_name):
            if not tests:
                return f"❓ {area_name}: NO TESTS"
            
            passed = len([t for t in tests if t['status'] == 'PASS'])
            total = len(tests)
            rate = (passed / total * 100) if total > 0 else 0
            
            if rate >= 75:
                return f"✅ {area_name}: WORKING ({passed}/{total} passed)"
            elif rate >= 50:
                return f"⚠️ {area_name}: PARTIAL ({passed}/{total} passed)"
            else:
                return f"❌ {area_name}: NEEDS ATTENTION ({passed}/{total} passed)"
        
        print(assess_area(template_tests, "PRIORITY 1 - Template System & Conversation Suggestions"))
        print(assess_area(cache_tests, "PRIORITY 2 - Prefetch Cache Performance"))
        print(assess_area(intent_tests, "PRIORITY 3 - Template Intent Detection"))
        print(assess_area(story_tests, "PRIORITY 4 - Story Generation & Processing"))
        print(assess_area(api_tests, "PRIORITY 5 - API Endpoint Functionality & Backend Health"))
        print("")
        
        # Final assessment
        if success_rate >= 85:
            print("🎉 EXCELLENT: Template system optimizations working excellently!")
            print("   Ready for production deployment.")
        elif success_rate >= 70:
            print("✅ GOOD: Most optimizations working well.")
            print("   Minor issues need attention before deployment.")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Template system partially working.")
            print("   Several issues need to be addressed.")
        else:
            print("🚨 CRITICAL: Major issues with template system implementation.")
            print("   Significant fixes required before deployment.")
        
        print("")
        print("=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "results": self.results
        }

async def main():
    """Main test execution"""
    tester = PriorityBackendTester()
    results = await tester.run_priority_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())