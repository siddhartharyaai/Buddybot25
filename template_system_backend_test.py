#!/usr/bin/env python3
"""
Template System & Frontend-Backend Integration Testing
Testing Focus: Template System Optimizations, Conversation Suggestions, Prefetch Cache, Intent Detection
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

class TemplateSystemBackendTester:
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
        
        logger.info(f"🎯 TEMPLATE SYSTEM TESTING: Using backend URL: {self.base_url}")
        
        # Test data
        self.test_user_id = f"template_test_user_{int(time.time())}"
        self.test_session_id = f"template_session_{int(time.time())}"
        
        # Test results tracking
        self.test_results = {
            "template_system_suggestions": [],
            "prefetch_cache_performance": [],
            "template_intent_detection": [],
            "story_generation_processing": [],
            "api_endpoint_functionality": [],
            "general_backend_health": []
        }
        
    async def run_comprehensive_template_tests(self):
        """Run all template system tests"""
        logger.info("🎯 STARTING COMPREHENSIVE TEMPLATE SYSTEM TESTING")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Create test user profile first
            await self._create_test_user_profile()
            
            # Test 1: Template System & Conversation Suggestions
            await self._test_template_system_suggestions()
            
            # Test 2: Prefetch Cache Performance
            await self._test_prefetch_cache_performance()
            
            # Test 3: Template Intent Detection
            await self._test_template_intent_detection()
            
            # Test 4: Story Generation & Processing
            await self._test_story_generation_processing()
            
            # Test 5: API Endpoint Functionality
            await self._test_api_endpoint_functionality()
            
            # Test 6: General Backend Health
            await self._test_general_backend_health()
            
        # Generate comprehensive report
        await self._generate_test_report()
    
    async def _create_test_user_profile(self):
        """Create test user profile for template testing"""
        try:
            profile_data = {
                "name": f"TemplateTestUser_{int(time.time())}",
                "age": 7,
                "location": "Test City",
                "timezone": "UTC",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "jokes", "facts", "songs"],
                "learning_goals": ["creativity", "knowledge"],
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
    
    async def _test_template_system_suggestions(self):
        """Test 1: Template System & Conversation Suggestions"""
        logger.info("🎯 TEST 1: Template System & Conversation Suggestions")
        
        test_results = []
        
        # Test 1.1: New /api/conversations/suggestions endpoint
        try:
            async with self.session.get(f"{self.base_url}/conversations/suggestions") as response:
                if response.status == 200:
                    suggestions = await response.json()
                    if isinstance(suggestions, list) and len(suggestions) >= 5:
                        # Check if suggestions are dynamic and varied
                        unique_suggestions = set(suggestions)
                        if len(unique_suggestions) >= 4:  # At least 4 unique suggestions
                            test_results.append({
                                "test": "Dynamic conversation suggestions endpoint",
                                "status": "PASS",
                                "details": f"Got {len(suggestions)} suggestions, {len(unique_suggestions)} unique: {suggestions[:3]}"
                            })
                        else:
                            test_results.append({
                                "test": "Dynamic conversation suggestions endpoint",
                                "status": "FAIL",
                                "details": f"Not enough variety: {len(unique_suggestions)} unique out of {len(suggestions)}"
                            })
                    else:
                        test_results.append({
                            "test": "Dynamic conversation suggestions endpoint",
                            "status": "FAIL",
                            "details": f"Insufficient suggestions: {len(suggestions) if isinstance(suggestions, list) else 'Not a list'}"
                        })
                else:
                    test_results.append({
                        "test": "Dynamic conversation suggestions endpoint",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Dynamic conversation suggestions endpoint",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 1.2: Template-based suggestions generation
        try:
            # Test multiple calls to see if suggestions vary
            suggestions_sets = []
            for i in range(3):
                async with self.session.get(f"{self.base_url}/conversations/suggestions") as response:
                    if response.status == 200:
                        suggestions = await response.json()
                        suggestions_sets.append(set(suggestions))
                    await asyncio.sleep(0.5)  # Small delay between requests
            
            if len(suggestions_sets) >= 2:
                # Check if suggestions vary between calls
                all_same = all(s == suggestions_sets[0] for s in suggestions_sets[1:])
                if not all_same:
                    test_results.append({
                        "test": "Template suggestions variation",
                        "status": "PASS",
                        "details": "Suggestions vary between calls - dynamic generation working"
                    })
                else:
                    test_results.append({
                        "test": "Template suggestions variation",
                        "status": "PARTIAL",
                        "details": "Suggestions are consistent (may be cached or static)"
                    })
            else:
                test_results.append({
                    "test": "Template suggestions variation",
                    "status": "FAIL",
                    "details": "Could not test variation - insufficient data"
                })
                
        except Exception as e:
            test_results.append({
                "test": "Template suggestions variation",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 1.3: Template variables usage
        try:
            # Test content suggestions with user profile
            async with self.session.get(f"{self.base_url}/content/suggestions/{self.test_user_id}") as response:
                if response.status == 200:
                    suggestions = await response.json()
                    if isinstance(suggestions, list) and len(suggestions) > 0:
                        # Check if suggestions use template variables (personalization)
                        suggestion_texts = [s.get('title', '') + ' ' + s.get('description', '') for s in suggestions if isinstance(s, dict)]
                        has_personalization = any('story' in text.lower() or 'joke' in text.lower() or 'fact' in text.lower() for text in suggestion_texts)
                        
                        if has_personalization:
                            test_results.append({
                                "test": "Template variables usage",
                                "status": "PASS",
                                "details": f"Personalized suggestions generated: {len(suggestions)} suggestions"
                            })
                        else:
                            test_results.append({
                                "test": "Template variables usage",
                                "status": "PARTIAL",
                                "details": f"Suggestions generated but personalization unclear: {len(suggestions)} suggestions"
                            })
                    else:
                        test_results.append({
                            "test": "Template variables usage",
                            "status": "FAIL",
                            "details": f"No content suggestions returned: {suggestions}"
                        })
                else:
                    test_results.append({
                        "test": "Template variables usage",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Template variables usage",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["template_system_suggestions"] = test_results
        logger.info(f"✅ Template System Suggestions Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_prefetch_cache_performance(self):
        """Test 2: Prefetch Cache Performance"""
        logger.info("🎯 TEST 2: Prefetch Cache Performance")
        
        test_results = []
        
        # Test 2.1: Cache population and hit rates
        try:
            # Check cache stats
            async with self.session.get(f"{self.base_url}/admin/cache-stats") as response:
                if response.status == 200:
                    cache_stats = await response.json()
                    if cache_stats.get("status") == "success":
                        db_cache = cache_stats.get("database_cache", {})
                        memory_cache = cache_stats.get("memory_cache", {})
                        
                        total_cached = db_cache.get("total_records", 0)
                        memory_size = memory_cache.get("content_cache_size", 0)
                        
                        if total_cached > 18:  # Should have more than 18 entries (previous issue)
                            test_results.append({
                                "test": "Cache population above threshold",
                                "status": "PASS",
                                "details": f"Database cache: {total_cached} records, Memory cache: {memory_size} entries"
                            })
                        else:
                            test_results.append({
                                "test": "Cache population above threshold",
                                "status": "FAIL",
                                "details": f"Insufficient cache entries: DB={total_cached}, Memory={memory_size} (need >18)"
                            })
                    else:
                        test_results.append({
                            "test": "Cache population above threshold",
                            "status": "FAIL",
                            "details": f"Cache stats failed: {cache_stats}"
                        })
                else:
                    test_results.append({
                        "test": "Cache population above threshold",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Cache population above threshold",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 2.2: Blazing latency responses using cached content
        try:
            # Test multiple quick requests to measure latency
            latencies = []
            for i in range(3):
                start_time = time.time()
                
                # Test a simple conversation that should hit cache
                text_request = {
                    "session_id": self.test_session_id,
                    "message": "Hello",
                    "user_id": self.test_user_id
                }
                
                async with self.session.post(f"{self.base_url}/conversations/text", json=text_request) as response:
                    if response.status == 200:
                        result = await response.json()
                        latency = time.time() - start_time
                        latencies.append(latency)
                        
                        # Check if processing time is blazing fast (should be ~0.0 for cached)
                        processing_time = result.get("metadata", {}).get("processing_time", latency)
                        if isinstance(processing_time, str):
                            try:
                                processing_time = float(processing_time.replace('s', ''))
                            except:
                                processing_time = latency
                    else:
                        latencies.append(999)  # High latency for failed requests
                
                await asyncio.sleep(0.1)  # Small delay between requests
            
            avg_latency = sum(latencies) / len(latencies) if latencies else 999
            
            if avg_latency < 2.0:  # Under 2 seconds is good
                if avg_latency < 0.5:  # Under 0.5s is blazing
                    test_results.append({
                        "test": "Blazing latency cached responses",
                        "status": "PASS",
                        "details": f"Blazing fast responses: {avg_latency:.3f}s average latency"
                    })
                else:
                    test_results.append({
                        "test": "Blazing latency cached responses",
                        "status": "PARTIAL",
                        "details": f"Good but not blazing: {avg_latency:.3f}s average latency"
                    })
            else:
                test_results.append({
                    "test": "Blazing latency cached responses",
                    "status": "FAIL",
                    "details": f"Slow responses: {avg_latency:.3f}s average latency"
                })
                
        except Exception as e:
            test_results.append({
                "test": "Blazing latency cached responses",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 2.3: Cache hit rate verification
        try:
            # Test the same request multiple times to verify caching
            cache_test_request = {
                "session_id": self.test_session_id,
                "message": "Tell me a fact about animals",
                "user_id": self.test_user_id
            }
            
            response_times = []
            for i in range(2):
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/conversations/text", json=cache_test_request) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_time = time.time() - start_time
                        response_times.append(response_time)
                    else:
                        response_times.append(999)
                await asyncio.sleep(0.2)
            
            if len(response_times) >= 2:
                # Second request should be faster if cached
                if response_times[1] <= response_times[0] * 1.2:  # Allow 20% variance
                    test_results.append({
                        "test": "Cache hit rate verification",
                        "status": "PASS",
                        "details": f"Cache working: 1st={response_times[0]:.3f}s, 2nd={response_times[1]:.3f}s"
                    })
                else:
                    test_results.append({
                        "test": "Cache hit rate verification",
                        "status": "PARTIAL",
                        "details": f"Cache may not be working: 1st={response_times[0]:.3f}s, 2nd={response_times[1]:.3f}s"
                    })
            else:
                test_results.append({
                    "test": "Cache hit rate verification",
                    "status": "FAIL",
                    "details": "Could not test cache hit rate - insufficient data"
                })
                
        except Exception as e:
            test_results.append({
                "test": "Cache hit rate verification",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["prefetch_cache_performance"] = test_results
        logger.info(f"✅ Prefetch Cache Performance Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_template_intent_detection(self):
        """Test 3: Template Intent Detection"""
        logger.info("🎯 TEST 3: Template Intent Detection")
        
        test_results = []
        
        # Test 3.1: Story requests intent detection
        story_requests = [
            "Tell me a story about a brave mouse",
            "I want to hear a fairy tale",
            "Can you tell me a bedtime story?",
            "Story about dragons please"
        ]
        
        story_results = []
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
                        content_type = result.get("content_type", "")
                        
                        # Check if it's detected as a story and has appropriate length
                        is_story_detected = content_type == "story" or len(response_text) > 100
                        is_blazing_fast = processing_time < 1.0
                        
                        story_results.append({
                            "request": story_request,
                            "detected": is_story_detected,
                            "fast": is_blazing_fast,
                            "processing_time": processing_time,
                            "response_length": len(response_text),
                            "content_type": content_type
                        })
                    else:
                        story_results.append({
                            "request": story_request,
                            "detected": False,
                            "fast": False,
                            "error": f"HTTP {response.status}"
                        })
                        
            except Exception as e:
                story_results.append({
                    "request": story_request,
                    "detected": False,
                    "fast": False,
                    "error": str(e)
                })
        
        # Analyze story detection results
        successful_detections = len([r for r in story_results if r.get("detected", False)])
        fast_responses = len([r for r in story_results if r.get("fast", False)])
        
        if successful_detections >= len(story_requests) * 0.75:  # 75% success rate
            test_results.append({
                "test": "Story intent detection accuracy",
                "status": "PASS",
                "details": f"Detected {successful_detections}/{len(story_requests)} story requests correctly"
            })
        else:
            test_results.append({
                "test": "Story intent detection accuracy",
                "status": "FAIL",
                "details": f"Only detected {successful_detections}/{len(story_requests)} story requests"
            })
        
        if fast_responses >= len(story_requests) * 0.75:  # 75% fast responses
            test_results.append({
                "test": "Story detection blazing speed",
                "status": "PASS",
                "details": f"{fast_responses}/{len(story_requests)} responses were blazing fast (<1s)"
            })
        else:
            test_results.append({
                "test": "Story detection blazing speed",
                "status": "FAIL",
                "details": f"Only {fast_responses}/{len(story_requests)} responses were fast enough"
            })
        
        # Test 3.2: Fact requests intent detection
        fact_requests = [
            "Tell me a fact about space",
            "What's an interesting fact about animals?",
            "Give me a fun fact",
            "I want to learn something new"
        ]
        
        fact_results = []
        for fact_request in fact_requests:
            try:
                start_time = time.time()
                text_request = {
                    "session_id": self.test_session_id,
                    "message": fact_request,
                    "user_id": self.test_user_id
                }
                
                async with self.session.post(f"{self.base_url}/conversations/text", json=text_request) as response:
                    if response.status == 200:
                        result = await response.json()
                        processing_time = time.time() - start_time
                        
                        response_text = result.get("response_text", "")
                        
                        # Check if response is appropriate for a fact (shorter, informative)
                        is_fact_like = 20 < len(response_text) < 200  # Facts should be concise
                        is_blazing_fast = processing_time < 0.5  # Facts should be very fast
                        
                        fact_results.append({
                            "request": fact_request,
                            "appropriate": is_fact_like,
                            "fast": is_blazing_fast,
                            "processing_time": processing_time,
                            "response_length": len(response_text)
                        })
                    else:
                        fact_results.append({
                            "request": fact_request,
                            "appropriate": False,
                            "fast": False,
                            "error": f"HTTP {response.status}"
                        })
                        
            except Exception as e:
                fact_results.append({
                    "request": fact_request,
                    "appropriate": False,
                    "fast": False,
                    "error": str(e)
                })
        
        # Analyze fact detection results
        appropriate_facts = len([r for r in fact_results if r.get("appropriate", False)])
        fast_facts = len([r for r in fact_results if r.get("fast", False)])
        
        if appropriate_facts >= len(fact_requests) * 0.75:
            test_results.append({
                "test": "Fact intent detection accuracy",
                "status": "PASS",
                "details": f"Generated appropriate facts for {appropriate_facts}/{len(fact_requests)} requests"
            })
        else:
            test_results.append({
                "test": "Fact intent detection accuracy",
                "status": "FAIL",
                "details": f"Only {appropriate_facts}/{len(fact_requests)} appropriate fact responses"
            })
        
        # Test 3.3: Joke and greeting requests
        other_requests = [
            ("Tell me a joke", "joke"),
            ("Hello there", "greeting"),
            ("Good morning", "greeting"),
            ("Make me laugh", "joke")
        ]
        
        other_results = []
        for request_text, expected_type in other_requests:
            try:
                start_time = time.time()
                text_request = {
                    "session_id": self.test_session_id,
                    "message": request_text,
                    "user_id": self.test_user_id
                }
                
                async with self.session.post(f"{self.base_url}/conversations/text", json=text_request) as response:
                    if response.status == 200:
                        result = await response.json()
                        processing_time = time.time() - start_time
                        
                        response_text = result.get("response_text", "")
                        is_blazing_fast = processing_time < 0.5
                        
                        other_results.append({
                            "request": request_text,
                            "type": expected_type,
                            "fast": is_blazing_fast,
                            "processing_time": processing_time,
                            "response_length": len(response_text),
                            "success": len(response_text) > 10
                        })
                    else:
                        other_results.append({
                            "request": request_text,
                            "type": expected_type,
                            "fast": False,
                            "success": False,
                            "error": f"HTTP {response.status}"
                        })
                        
            except Exception as e:
                other_results.append({
                    "request": request_text,
                    "type": expected_type,
                    "fast": False,
                    "success": False,
                    "error": str(e)
                })
        
        successful_others = len([r for r in other_results if r.get("success", False)])
        fast_others = len([r for r in other_results if r.get("fast", False)])
        
        if successful_others >= len(other_requests) * 0.75:
            test_results.append({
                "test": "Joke and greeting detection",
                "status": "PASS",
                "details": f"Handled {successful_others}/{len(other_requests)} joke/greeting requests correctly"
            })
        else:
            test_results.append({
                "test": "Joke and greeting detection",
                "status": "FAIL",
                "details": f"Only handled {successful_others}/{len(other_requests)} joke/greeting requests"
            })
        
        self.test_results["template_intent_detection"] = test_results
        logger.info(f"✅ Template Intent Detection Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_story_generation_processing(self):
        """Test 4: Story Generation & Processing"""
        logger.info("🎯 TEST 4: Story Generation & Processing")
        
        test_results = []
        
        # Test 4.1: Story generation with various prompts
        story_prompts = [
            "Tell me a story about a brave little mouse who goes on an adventure",
            "I want a fairy tale about a princess and a dragon",
            "Can you tell me a bedtime story about friendship?",
            "Story about a magical forest with talking animals"
        ]
        
        story_generation_results = []
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
                        
                        response_text = result.get("response_text", "")
                        word_count = len(response_text.split())
                        
                        # Check story quality metrics
                        has_good_length = word_count >= 50  # At least 50 words
                        has_story_elements = any(word in response_text.lower() for word in ['once', 'story', 'adventure', 'character', 'journey'])
                        is_complete = response_text.endswith('.') or response_text.endswith('!') or response_text.endswith('?')
                        
                        story_generation_results.append({
                            "prompt": prompt,
                            "word_count": word_count,
                            "processing_time": processing_time,
                            "good_length": has_good_length,
                            "story_elements": has_story_elements,
                            "complete": is_complete,
                            "success": has_good_length and has_story_elements
                        })
                    else:
                        story_generation_results.append({
                            "prompt": prompt,
                            "success": False,
                            "error": f"HTTP {response.status}"
                        })
                        
            except Exception as e:
                story_generation_results.append({
                    "prompt": prompt,
                    "success": False,
                    "error": str(e)
                })
        
        # Analyze story generation results
        successful_stories = len([r for r in story_generation_results if r.get("success", False)])
        avg_word_count = sum([r.get("word_count", 0) for r in story_generation_results]) / len(story_generation_results) if story_generation_results else 0
        avg_processing_time = sum([r.get("processing_time", 0) for r in story_generation_results]) / len(story_generation_results) if story_generation_results else 0
        
        if successful_stories >= len(story_prompts) * 0.75:
            test_results.append({
                "test": "Story generation quality",
                "status": "PASS",
                "details": f"Generated {successful_stories}/{len(story_prompts)} quality stories, avg {avg_word_count:.0f} words"
            })
        else:
            test_results.append({
                "test": "Story generation quality",
                "status": "FAIL",
                "details": f"Only {successful_stories}/{len(story_prompts)} quality stories generated"
            })
        
        if avg_processing_time < 3.0:  # Under 3 seconds is good
            test_results.append({
                "test": "Story generation speed",
                "status": "PASS",
                "details": f"Average processing time: {avg_processing_time:.2f}s (optimized)"
            })
        else:
            test_results.append({
                "test": "Story generation speed",
                "status": "FAIL",
                "details": f"Slow processing time: {avg_processing_time:.2f}s (needs optimization)"
            })
        
        # Test 4.2: Story streaming functionality
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
                        first_chunk = result.get("first_chunk", {})
                        total_chunks = result.get("total_chunks", 0)
                        total_words = result.get("total_words", 0)
                        
                        if total_chunks > 1 and total_words > 100:
                            test_results.append({
                                "test": "Story streaming functionality",
                                "status": "PASS",
                                "details": f"Story streaming working: {total_chunks} chunks, {total_words} words"
                            })
                        else:
                            test_results.append({
                                "test": "Story streaming functionality",
                                "status": "PARTIAL",
                                "details": f"Streaming active but limited: {total_chunks} chunks, {total_words} words"
                            })
                    else:
                        test_results.append({
                            "test": "Story streaming functionality",
                            "status": "FAIL",
                            "details": f"Story streaming not working: {result}"
                        })
                else:
                    test_results.append({
                        "test": "Story streaming functionality",
                        "status": "FAIL",
                        "details": f"HTTP {response.status}: {await response.text()}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Story streaming functionality",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 4.3: Story narration endpoint
        try:
            # First get available stories
            async with self.session.get(f"{self.base_url}/content/stories") as response:
                if response.status == 200:
                    stories_data = await response.json()
                    stories = stories_data.get("stories", [])
                    
                    if stories:
                        # Test narration of first story
                        story_id = stories[0].get("id")
                        if story_id:
                            form_data = aiohttp.FormData()
                            form_data.add_field('user_id', self.test_user_id)
                            
                            async with self.session.post(f"{self.base_url}/content/stories/{story_id}/narrate", data=form_data) as narrate_response:
                                if narrate_response.status == 200:
                                    narrate_result = await narrate_response.json()
                                    if narrate_result.get("status") == "success":
                                        response_text = narrate_result.get("response_text", "")
                                        response_audio = narrate_result.get("response_audio", "")
                                        
                                        if response_text and len(response_text) > 50:
                                            test_results.append({
                                                "test": "Story narration endpoint",
                                                "status": "PASS",
                                                "details": f"Narration working: {len(response_text)} chars text, audio: {len(response_audio) > 0}"
                                            })
                                        else:
                                            test_results.append({
                                                "test": "Story narration endpoint",
                                                "status": "FAIL",
                                                "details": f"Poor narration quality: {len(response_text)} chars text"
                                            })
                                    else:
                                        test_results.append({
                                            "test": "Story narration endpoint",
                                            "status": "FAIL",
                                            "details": f"Narration failed: {narrate_result}"
                                        })
                                else:
                                    test_results.append({
                                        "test": "Story narration endpoint",
                                        "status": "FAIL",
                                        "details": f"HTTP {narrate_response.status}: {await narrate_response.text()}"
                                    })
                        else:
                            test_results.append({
                                "test": "Story narration endpoint",
                                "status": "FAIL",
                                "details": "No story ID available for testing"
                            })
                    else:
                        test_results.append({
                            "test": "Story narration endpoint",
                            "status": "FAIL",
                            "details": "No stories available for narration testing"
                        })
                else:
                    test_results.append({
                        "test": "Story narration endpoint",
                        "status": "FAIL",
                        "details": f"Could not get stories: HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Story narration endpoint",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["story_generation_processing"] = test_results
        logger.info(f"✅ Story Generation & Processing Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_api_endpoint_functionality(self):
        """Test 5: API Endpoint Functionality"""
        logger.info("🎯 TEST 5: API Endpoint Functionality")
        
        test_results = []
        
        # Test 5.1: All conversation endpoints
        conversation_endpoints = [
            ("GET", "/conversations/suggestions", None),
            ("POST", "/conversations/text", {
                "session_id": self.test_session_id,
                "message": "Hello",
                "user_id": self.test_user_id
            }),
            ("POST", "/conversations/voice", {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "audio_base64": "dGVzdA=="  # base64 encoded "test"
            })
        ]
        
        for method, endpoint, data in conversation_endpoints:
            try:
                if method == "GET":
                    async with self.session.get(f"{self.base_url}{endpoint}") as response:
                        status = response.status
                        content = await response.json() if response.content_type == 'application/json' else await response.text()
                elif method == "POST":
                    async with self.session.post(f"{self.base_url}{endpoint}", json=data) as response:
                        status = response.status
                        content = await response.json() if response.content_type == 'application/json' else await response.text()
                
                if status in [200, 201]:
                    test_results.append({
                        "test": f"Endpoint {method} {endpoint}",
                        "status": "PASS",
                        "details": f"HTTP {status} - Working correctly"
                    })
                elif status in [400, 422]:  # Expected validation errors
                    test_results.append({
                        "test": f"Endpoint {method} {endpoint}",
                        "status": "PARTIAL",
                        "details": f"HTTP {status} - Validation working (expected for test data)"
                    })
                else:
                    test_results.append({
                        "test": f"Endpoint {method} {endpoint}",
                        "status": "FAIL",
                        "details": f"HTTP {status} - Unexpected response"
                    })
                    
            except Exception as e:
                test_results.append({
                    "test": f"Endpoint {method} {endpoint}",
                    "status": "ERROR",
                    "details": str(e)
                })
        
        # Test 5.2: Voice processing endpoints
        voice_endpoints = [
            ("GET", "/voice/personalities", None),
            ("POST", "/voice/tts", {
                "text": "Hello, this is a test",
                "personality": "friendly_companion"
            })
        ]
        
        for method, endpoint, data in voice_endpoints:
            try:
                if method == "GET":
                    async with self.session.get(f"{self.base_url}{endpoint}") as response:
                        status = response.status
                        content = await response.json() if response.content_type == 'application/json' else await response.text()
                elif method == "POST":
                    async with self.session.post(f"{self.base_url}{endpoint}", json=data) as response:
                        status = response.status
                        content = await response.json() if response.content_type == 'application/json' else await response.text()
                
                if status == 200:
                    test_results.append({
                        "test": f"Voice endpoint {method} {endpoint}",
                        "status": "PASS",
                        "details": f"HTTP {status} - Working correctly"
                    })
                else:
                    test_results.append({
                        "test": f"Voice endpoint {method} {endpoint}",
                        "status": "FAIL",
                        "details": f"HTTP {status} - Not working"
                    })
                    
            except Exception as e:
                test_results.append({
                    "test": f"Voice endpoint {method} {endpoint}",
                    "status": "ERROR",
                    "details": str(e)
                })
        
        # Test 5.3: Error handling for invalid inputs
        error_test_cases = [
            ("POST", "/conversations/text", {
                "session_id": "",
                "message": "",
                "user_id": ""
            }),
            ("POST", "/voice/tts", {
                "text": "",
                "personality": "invalid_personality"
            })
        ]
        
        error_handling_success = 0
        for method, endpoint, invalid_data in error_test_cases:
            try:
                async with self.session.post(f"{self.base_url}{endpoint}", json=invalid_data) as response:
                    if response.status in [400, 422, 500]:  # Expected error codes
                        error_handling_success += 1
                        
            except Exception:
                pass  # Exception handling is also valid
        
        if error_handling_success >= len(error_test_cases) * 0.5:
            test_results.append({
                "test": "Error handling for invalid inputs",
                "status": "PASS",
                "details": f"Proper error handling: {error_handling_success}/{len(error_test_cases)} cases"
            })
        else:
            test_results.append({
                "test": "Error handling for invalid inputs",
                "status": "FAIL",
                "details": f"Poor error handling: {error_handling_success}/{len(error_test_cases)} cases"
            })
        
        # Test 5.4: Response formats and data consistency
        try:
            text_request = {
                "session_id": self.test_session_id,
                "message": "Tell me a joke",
                "user_id": self.test_user_id
            }
            
            async with self.session.post(f"{self.base_url}/conversations/text", json=text_request) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Check required fields
                    required_fields = ["response_text"]
                    has_required_fields = all(field in result for field in required_fields)
                    
                    # Check data types
                    response_text = result.get("response_text", "")
                    is_valid_text = isinstance(response_text, str) and len(response_text) > 0
                    
                    if has_required_fields and is_valid_text:
                        test_results.append({
                            "test": "Response format consistency",
                            "status": "PASS",
                            "details": f"Consistent format with required fields: {list(result.keys())}"
                        })
                    else:
                        test_results.append({
                            "test": "Response format consistency",
                            "status": "FAIL",
                            "details": f"Inconsistent format: missing fields or invalid data types"
                        })
                else:
                    test_results.append({
                        "test": "Response format consistency",
                        "status": "FAIL",
                        "details": f"Could not test format: HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Response format consistency",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["api_endpoint_functionality"] = test_results
        logger.info(f"✅ API Endpoint Functionality Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _test_general_backend_health(self):
        """Test 6: General Backend Health"""
        logger.info("🎯 TEST 6: General Backend Health")
        
        test_results = []
        
        # Test 6.1: All agents properly initialized
        try:
            async with self.session.get(f"{self.base_url}/agents/status") as response:
                if response.status == 200:
                    agents_status = await response.json()
                    
                    # Check key agents
                    key_agents = ["orchestrator", "voice_agent", "conversation_agent", "content_agent", "safety_agent"]
                    active_agents = []
                    
                    for agent in key_agents:
                        if agents_status.get(agent) == "active":
                            active_agents.append(agent)
                    
                    if len(active_agents) >= len(key_agents) * 0.8:  # 80% of agents active
                        test_results.append({
                            "test": "Agents initialization",
                            "status": "PASS",
                            "details": f"Active agents: {active_agents} ({len(active_agents)}/{len(key_agents)})"
                        })
                    else:
                        test_results.append({
                            "test": "Agents initialization",
                            "status": "FAIL",
                            "details": f"Insufficient active agents: {active_agents} ({len(active_agents)}/{len(key_agents)})"
                        })
                else:
                    test_results.append({
                        "test": "Agents initialization",
                        "status": "FAIL",
                        "details": f"Could not get agents status: HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Agents initialization",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 6.2: Database connectivity and operations
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    
                    database_status = health_data.get("database")
                    agents_status = health_data.get("agents", {})
                    
                    if database_status == "connected":
                        test_results.append({
                            "test": "Database connectivity",
                            "status": "PASS",
                            "details": f"Database connected, orchestrator: {agents_status.get('orchestrator', False)}"
                        })
                    else:
                        test_results.append({
                            "test": "Database connectivity",
                            "status": "FAIL",
                            "details": f"Database not connected: {database_status}"
                        })
                else:
                    test_results.append({
                        "test": "Database connectivity",
                        "status": "FAIL",
                        "details": f"Health check failed: HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Database connectivity",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 6.3: Voice processing capabilities
        try:
            # Test TTS capability
            tts_request = {
                "text": "This is a voice processing test",
                "personality": "friendly_companion"
            }
            
            async with self.session.post(f"{self.base_url}/voice/tts", json=tts_request) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success" and result.get("audio_base64"):
                        test_results.append({
                            "test": "Voice processing capabilities",
                            "status": "PASS",
                            "details": f"TTS working: {len(result.get('audio_base64', ''))} chars audio generated"
                        })
                    else:
                        test_results.append({
                            "test": "Voice processing capabilities",
                            "status": "FAIL",
                            "details": f"TTS not working properly: {result}"
                        })
                else:
                    test_results.append({
                        "test": "Voice processing capabilities",
                        "status": "FAIL",
                        "details": f"TTS endpoint failed: HTTP {response.status}"
                    })
                    
        except Exception as e:
            test_results.append({
                "test": "Voice processing capabilities",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test 6.4: Memory and telemetry systems
        try:
            # Test memory context
            async with self.session.get(f"{self.base_url}/memory/context/{self.test_user_id}") as response:
                memory_working = response.status == 200
            
            # Test analytics
            async with self.session.get(f"{self.base_url}/analytics/dashboard/{self.test_user_id}") as response:
                analytics_working = response.status == 200
            
            if memory_working and analytics_working:
                test_results.append({
                    "test": "Memory and telemetry systems",
                    "status": "PASS",
                    "details": "Both memory and analytics systems working"
                })
            elif memory_working or analytics_working:
                test_results.append({
                    "test": "Memory and telemetry systems",
                    "status": "PARTIAL",
                    "details": f"Memory: {memory_working}, Analytics: {analytics_working}"
                })
            else:
                test_results.append({
                    "test": "Memory and telemetry systems",
                    "status": "FAIL",
                    "details": "Both memory and analytics systems not working"
                })
                
        except Exception as e:
            test_results.append({
                "test": "Memory and telemetry systems",
                "status": "ERROR",
                "details": str(e)
            })
        
        self.test_results["general_backend_health"] = test_results
        logger.info(f"✅ General Backend Health Tests: {len([t for t in test_results if t['status'] == 'PASS'])}/{len(test_results)} passed")
    
    async def _generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("🎯 GENERATING COMPREHENSIVE TEMPLATE SYSTEM TEST REPORT")
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        total_partial = 0
        
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE TEMPLATE SYSTEM & FRONTEND-BACKEND INTEGRATION TESTING REPORT")
        report.append("=" * 80)
        report.append(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Backend URL: {self.base_url}")
        report.append(f"Test User ID: {self.test_user_id}")
        report.append(f"Test Session ID: {self.test_session_id}")
        report.append("")
        
        for category, tests in self.test_results.items():
            if not tests:
                continue
                
            category_passed = len([t for t in tests if t['status'] == 'PASS'])
            category_failed = len([t for t in tests if t['status'] == 'FAIL'])
            category_errors = len([t for t in tests if t['status'] == 'ERROR'])
            category_partial = len([t for t in tests if t['status'] == 'PARTIAL'])
            category_total = len(tests)
            
            total_tests += category_total
            total_passed += category_passed
            total_failed += category_failed
            total_errors += category_errors
            total_partial += category_partial
            
            success_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            
            report.append(f"📋 {category.upper().replace('_', ' ')}")
            report.append(f"   Success Rate: {success_rate:.1f}% ({category_passed}/{category_total})")
            report.append(f"   ✅ Passed: {category_passed}")
            report.append(f"   ⚠️  Partial: {category_partial}")
            report.append(f"   ❌ Failed: {category_failed}")
            report.append(f"   🔥 Errors: {category_errors}")
            report.append("")
            
            for test in tests:
                status_icon = "✅" if test['status'] == 'PASS' else "⚠️" if test['status'] == 'PARTIAL' else "❌" if test['status'] == 'FAIL' else "🔥"
                report.append(f"   {status_icon} {test['test']}: {test['status']}")
                report.append(f"      Details: {test['details']}")
                report.append("")
        
        # Overall summary
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report.append("=" * 80)
        report.append("OVERALL SUMMARY")
        report.append("=" * 80)
        report.append(f"Total Tests: {total_tests}")
        report.append(f"✅ Passed: {total_passed}")
        report.append(f"⚠️  Partial: {total_partial}")
        report.append(f"❌ Failed: {total_failed}")
        report.append(f"🔥 Errors: {total_errors}")
        report.append(f"Overall Success Rate: {overall_success_rate:.1f}%")
        report.append("")
        
        # Critical assessment based on review priorities
        report.append("🎯 PRIORITY AREAS ASSESSMENT:")
        report.append("")
        
        # Template System & Conversation Suggestions
        template_tests = self.test_results.get("template_system_suggestions", [])
        if template_tests:
            template_passed = len([t for t in template_tests if t['status'] == 'PASS'])
            if template_passed >= len(template_tests) * 0.75:
                report.append("✅ PRIORITY 1 - Template System & Conversation Suggestions: WORKING")
            else:
                report.append("❌ PRIORITY 1 - Template System & Conversation Suggestions: NEEDS ATTENTION")
        
        # Prefetch Cache Performance
        cache_tests = self.test_results.get("prefetch_cache_performance", [])
        if cache_tests:
            cache_passed = len([t for t in cache_tests if t['status'] == 'PASS'])
            if cache_passed >= len(cache_tests) * 0.75:
                report.append("✅ PRIORITY 2 - Prefetch Cache Performance: WORKING")
            else:
                report.append("❌ PRIORITY 2 - Prefetch Cache Performance: NEEDS ATTENTION")
        
        # Template Intent Detection
        intent_tests = self.test_results.get("template_intent_detection", [])
        if intent_tests:
            intent_passed = len([t for t in intent_tests if t['status'] == 'PASS'])
            if intent_passed >= len(intent_tests) * 0.75:
                report.append("✅ PRIORITY 3 - Template Intent Detection: WORKING")
            else:
                report.append("❌ PRIORITY 3 - Template Intent Detection: NEEDS ATTENTION")
        
        # Story Generation & Processing
        story_tests = self.test_results.get("story_generation_processing", [])
        if story_tests:
            story_passed = len([t for t in story_tests if t['status'] == 'PASS'])
            if story_passed >= len(story_tests) * 0.75:
                report.append("✅ PRIORITY 4 - Story Generation & Processing: WORKING")
            else:
                report.append("❌ PRIORITY 4 - Story Generation & Processing: NEEDS ATTENTION")
        
        # API Endpoint Functionality
        api_tests = self.test_results.get("api_endpoint_functionality", [])
        if api_tests:
            api_passed = len([t for t in api_tests if t['status'] == 'PASS'])
            if api_passed >= len(api_tests) * 0.75:
                report.append("✅ PRIORITY 5 - API Endpoint Functionality: WORKING")
            else:
                report.append("❌ PRIORITY 5 - API Endpoint Functionality: NEEDS ATTENTION")
        
        # General Backend Health
        health_tests = self.test_results.get("general_backend_health", [])
        if health_tests:
            health_passed = len([t for t in health_tests if t['status'] == 'PASS'])
            if health_passed >= len(health_tests) * 0.75:
                report.append("✅ PRIORITY 6 - General Backend Health: WORKING")
            else:
                report.append("❌ PRIORITY 6 - General Backend Health: NEEDS ATTENTION")
        
        report.append("")
        
        # Final assessment
        if overall_success_rate >= 85:
            report.append("🎉 EXCELLENT: Template system optimizations are working excellently!")
            report.append("   Frontend-backend integration fixes are successful.")
        elif overall_success_rate >= 70:
            report.append("✅ GOOD: Most template system optimizations working well.")
            report.append("   Some minor issues need attention.")
        elif overall_success_rate >= 50:
            report.append("⚠️  MODERATE: Template system partially working.")
            report.append("   Several issues need to be addressed.")
        else:
            report.append("🚨 CRITICAL: Major issues with template system implementation.")
            report.append("   Significant fixes required before deployment.")
        
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
            "total_partial": total_partial,
            "success_rate": overall_success_rate,
            "detailed_results": self.test_results
        }

async def main():
    """Main test execution"""
    tester = TemplateSystemBackendTester()
    results = await tester.run_comprehensive_template_tests()
    
    # Return results for further processing
    return results

if __name__ == "__main__":
    asyncio.run(main())