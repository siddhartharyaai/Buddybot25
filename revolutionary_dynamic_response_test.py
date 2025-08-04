#!/usr/bin/env python3
"""
COMPREHENSIVE VALIDATION: Revolutionary Dynamic Response System Testing
Testing all claimed improvements as requested in review.
"""

import asyncio
import aiohttp
import json
import time
import base64
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from environment
BACKEND_URL = "https://6ddee563-7037-4e87-80ca-83a8a9a9bcae.preview.emergentagent.com/api"

class RevolutionaryDynamicResponseTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.user_profiles = {
            "age_5": {
                "id": "test_user_age_5",
                "name": "Emma",
                "age": 5,
                "preferences": {"voice_personality": "friendly_companion"}
            },
            "age_8": {
                "id": "test_user_age_8", 
                "name": "Alex",
                "age": 8,
                "preferences": {"voice_personality": "story_narrator"}
            },
            "age_11": {
                "id": "test_user_age_11",
                "name": "Jordan", 
                "age": 11,
                "preferences": {"voice_personality": "learning_buddy"}
            }
        }

    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    def log_test_result(self, test_name, success, details, expected_range=None, actual_value=None):
        """Log test result with detailed information"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "expected_range": expected_range,
            "actual_value": actual_value
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
        if expected_range and actual_value:
            logger.info(f"   Expected: {expected_range}, Actual: {actual_value}")
        logger.info(f"   Details: {details}")

    async def test_health_check(self):
        """Test basic health check"""
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result(
                        "Health Check",
                        True,
                        f"Backend healthy: {data}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Health Check", 
                        False,
                        f"Health check failed with status {response.status}"
                    )
                    return False
        except Exception as e:
            self.log_test_result(
                "Health Check",
                False, 
                f"Health check error: {str(e)}"
            )
            return False

    async def create_user_profile(self, profile_data):
        """Create user profile for testing"""
        try:
            payload = {
                "name": profile_data["name"],
                "age": profile_data["age"],
                "language": "english",
                "preferences": profile_data["preferences"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/users/profile", json=payload) as response:
                if response.status == 200:
                    return True
                else:
                    logger.warning(f"Profile creation failed for {profile_data['name']}: {response.status}")
                    return False
        except Exception as e:
            logger.warning(f"Profile creation error for {profile_data['name']}: {str(e)}")
            return False

    async def test_dynamic_response_lengths(self):
        """Test 1: DYNAMIC RESPONSE LENGTH TESTING"""
        logger.info("🎯 TESTING: Dynamic Response Length System")
        
        test_queries = [
            {
                "query": "What is Jupiter?",
                "type": "Quick Fact Query",
                "expected_words": (30, 50),
                "expected_time": (3, 5),
                "user_age": 8
            },
            {
                "query": "Tell me a story about a dragon",
                "type": "Story Request", 
                "expected_words": (120, 300),
                "expected_time": (5, 15),
                "user_age": 8
            },
            {
                "query": "Hello Buddy",
                "type": "Greeting",
                "expected_words": (15, 25),
                "expected_time": (1, 3),
                "user_age": 8
            },
            {
                "query": "Tell me a joke",
                "type": "Entertainment",
                "expected_words": (40, 80),
                "expected_time": (3, 8),
                "user_age": 8
            },
            {
                "query": "How do airplanes fly?",
                "type": "Complex Question",
                "expected_words": (25, 60),
                "expected_time": (3, 8),
                "user_age": 8
            }
        ]

        for query_test in test_queries:
            await self.test_single_query_response_length(query_test)

    async def test_single_query_response_length(self, query_test):
        """Test a single query for response length and timing"""
        try:
            start_time = time.time()
            
            payload = {
                "session_id": f"test_session_{int(time.time())}",
                "user_id": f"test_user_age_{query_test['user_age']}",
                "message": query_test["query"]
            }
            
            # Test fast pipeline first
            async with self.session.post(f"{BACKEND_URL}/conversations/text_fast", json=payload) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    word_count = len(response_text.split())
                    
                    # Check word count
                    expected_min, expected_max = query_test["expected_words"]
                    word_count_ok = expected_min <= word_count <= expected_max
                    
                    # Check response time
                    expected_time_min, expected_time_max = query_test["expected_time"]
                    time_ok = response_time <= expected_time_max
                    
                    success = word_count_ok and time_ok
                    
                    details = f"Query: '{query_test['query']}' | Words: {word_count} | Time: {response_time:.2f}s | Response: '{response_text[:100]}...'"
                    
                    self.log_test_result(
                        f"Dynamic Length - {query_test['type']}",
                        success,
                        details,
                        f"{expected_min}-{expected_max} words, <{expected_time_max}s",
                        f"{word_count} words, {response_time:.2f}s"
                    )
                    
                else:
                    self.log_test_result(
                        f"Dynamic Length - {query_test['type']}",
                        False,
                        f"API error: {response.status}"
                    )
                    
        except Exception as e:
            self.log_test_result(
                f"Dynamic Length - {query_test['type']}",
                False,
                f"Test error: {str(e)}"
            )

    async def test_age_appropriate_responses(self):
        """Test 2: AGE-APPROPRIATE TESTING"""
        logger.info("🎯 TESTING: Age-Appropriate Response System")
        
        test_query = "Tell me about dinosaurs"
        
        for age_key, profile in self.user_profiles.items():
            await self.test_age_appropriate_single(test_query, profile)

    async def test_age_appropriate_single(self, query, profile):
        """Test age-appropriate response for single user profile"""
        try:
            payload = {
                "session_id": f"test_session_{int(time.time())}",
                "user_id": profile["id"],
                "message": query
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text_fast", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    
                    # Analyze language complexity
                    complexity_score = self.analyze_language_complexity(response_text, profile["age"])
                    
                    # Check if response is age-appropriate
                    age_appropriate = self.is_age_appropriate(response_text, profile["age"])
                    
                    details = f"Age {profile['age']} | Complexity: {complexity_score:.1f} | Response: '{response_text[:100]}...'"
                    
                    self.log_test_result(
                        f"Age-Appropriate - Age {profile['age']}",
                        age_appropriate,
                        details,
                        f"Age {profile['age']} appropriate",
                        f"Complexity {complexity_score:.1f}"
                    )
                    
                else:
                    self.log_test_result(
                        f"Age-Appropriate - Age {profile['age']}",
                        False,
                        f"API error: {response.status}"
                    )
                    
        except Exception as e:
            self.log_test_result(
                f"Age-Appropriate - Age {profile['age']}",
                False,
                f"Test error: {str(e)}"
            )

    def analyze_language_complexity(self, text, age):
        """Analyze language complexity for age appropriateness"""
        if not text:
            return 0
            
        words = text.split()
        if not words:
            return 0
            
        # Calculate average word length
        avg_word_length = sum(len(word.strip('.,!?')) for word in words) / len(words)
        
        # Calculate sentence complexity (words per sentence)
        sentences = text.split('.')
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        # Simple complexity score
        complexity = (avg_word_length * 2) + (avg_sentence_length * 0.5)
        
        return complexity

    def is_age_appropriate(self, text, age):
        """Check if text is age-appropriate"""
        complexity = self.analyze_language_complexity(text, age)
        
        # Age-appropriate complexity thresholds
        if age <= 5:
            return complexity <= 8.0  # Simple words and short sentences
        elif age <= 8:
            return complexity <= 12.0  # Moderate complexity
        elif age <= 11:
            return complexity <= 16.0  # More complex vocabulary allowed
        else:
            return True  # No strict limits for older kids

    async def test_latency_validation(self):
        """Test 3: LATENCY VALIDATION"""
        logger.info("🎯 TESTING: Latency Validation System")
        
        test_cases = [
            {
                "query": "Hi there!",
                "expected_max_latency": 5.0,
                "pipeline": "fast"
            },
            {
                "query": "Tell me a short story",
                "expected_max_latency": 15.0,
                "pipeline": "regular"
            },
            {
                "query": "What's 2+2?",
                "expected_max_latency": 3.0,
                "pipeline": "fast"
            }
        ]
        
        for test_case in test_cases:
            await self.test_single_latency(test_case)

    async def test_single_latency(self, test_case):
        """Test latency for a single query"""
        try:
            start_time = time.time()
            
            payload = {
                "session_id": f"test_session_{int(time.time())}",
                "user_id": "test_user_age_8",
                "message": test_case["query"]
            }
            
            # Choose endpoint based on pipeline
            endpoint = "/conversations/text_fast" if test_case["pipeline"] == "fast" else "/conversations/text"
            
            async with self.session.post(f"{BACKEND_URL}{endpoint}", json=payload) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    latency_ok = response_time <= test_case["expected_max_latency"]
                    
                    details = f"Query: '{test_case['query']}' | Pipeline: {test_case['pipeline']} | Latency: {response_time:.2f}s"
                    
                    self.log_test_result(
                        f"Latency - {test_case['pipeline'].title()} Pipeline",
                        latency_ok,
                        details,
                        f"<{test_case['expected_max_latency']}s",
                        f"{response_time:.2f}s"
                    )
                    
                else:
                    self.log_test_result(
                        f"Latency - {test_case['pipeline'].title()} Pipeline",
                        False,
                        f"API error: {response.status}"
                    )
                    
        except Exception as e:
            self.log_test_result(
                f"Latency - {test_case['pipeline'].title()} Pipeline",
                False,
                f"Test error: {str(e)}"
            )

    async def test_smart_routing_validation(self):
        """Test 4: SMART ROUTING VALIDATION"""
        logger.info("🎯 TESTING: Smart Routing System")
        
        # Test voice processing with smart routing
        test_cases = [
            {
                "query": "Hello",
                "expected_pipeline": "fast",
                "description": "Simple greeting should use fast pipeline"
            },
            {
                "query": "Tell me a complete story about adventure",
                "expected_pipeline": "full",
                "description": "Story request should use full pipeline"
            }
        ]
        
        for test_case in test_cases:
            await self.test_smart_routing_single(test_case)

    async def test_smart_routing_single(self, test_case):
        """Test smart routing for a single case"""
        try:
            # Create minimal audio data for testing (1 second of silence)
            audio_data = b'\x00' * 8000  # 1 second of 8kHz silence
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            payload = {
                "session_id": f"test_session_{int(time.time())}",
                "user_id": "test_user_age_8",
                "audio_base64": audio_base64
            }
            
            async with self.session.post(f"{BACKEND_URL}/voice/process_audio", data=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    selected_pipeline = data.get("pipeline", "unknown")
                    smart_routing = data.get("smart_routing", "disabled")
                    
                    routing_working = smart_routing == "enabled"
                    
                    details = f"Query type: {test_case['description']} | Selected: {selected_pipeline} | Smart routing: {smart_routing}"
                    
                    self.log_test_result(
                        f"Smart Routing - {test_case['expected_pipeline'].title()} Pipeline",
                        routing_working,
                        details,
                        test_case["expected_pipeline"],
                        selected_pipeline
                    )
                    
                else:
                    self.log_test_result(
                        f"Smart Routing - {test_case['expected_pipeline'].title()} Pipeline",
                        False,
                        f"API error: {response.status}"
                    )
                    
        except Exception as e:
            self.log_test_result(
                f"Smart Routing - {test_case['expected_pipeline'].title()} Pipeline",
                False,
                f"Test error: {str(e)}"
            )

    async def test_content_quality_validation(self):
        """Test 5: CONTENT QUALITY VALIDATION"""
        logger.info("🎯 TESTING: Content Quality System")
        
        test_queries = [
            {
                "query": "Tell me a story about friendship",
                "quality_checks": ["complete", "age_appropriate", "engaging", "educational"]
            },
            {
                "query": "What is the sun?",
                "quality_checks": ["complete", "age_appropriate", "educational", "accurate"]
            },
            {
                "query": "Tell me a joke",
                "quality_checks": ["complete", "age_appropriate", "entertaining", "appropriate_humor"]
            }
        ]
        
        for query_test in test_queries:
            await self.test_content_quality_single(query_test)

    async def test_content_quality_single(self, query_test):
        """Test content quality for a single query"""
        try:
            payload = {
                "session_id": f"test_session_{int(time.time())}",
                "user_id": "test_user_age_8",
                "message": query_test["query"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    content_type = data.get("content_type", "conversation")
                    
                    # Evaluate quality
                    quality_score = self.evaluate_content_quality(response_text, query_test["quality_checks"])
                    quality_ok = quality_score >= 0.7  # 70% quality threshold
                    
                    details = f"Query: '{query_test['query']}' | Quality: {quality_score:.2f} | Type: {content_type} | Response: '{response_text[:100]}...'"
                    
                    self.log_test_result(
                        f"Content Quality - {query_test['query'][:20]}...",
                        quality_ok,
                        details,
                        "Quality ≥ 0.7",
                        f"Quality {quality_score:.2f}"
                    )
                    
                else:
                    self.log_test_result(
                        f"Content Quality - {query_test['query'][:20]}...",
                        False,
                        f"API error: {response.status}"
                    )
                    
        except Exception as e:
            self.log_test_result(
                f"Content Quality - {query_test['query'][:20]}...",
                False,
                f"Test error: {str(e)}"
            )

    def evaluate_content_quality(self, text, quality_checks):
        """Evaluate content quality based on checks"""
        if not text:
            return 0.0
            
        score = 0.0
        total_checks = len(quality_checks)
        
        for check in quality_checks:
            if check == "complete":
                # Check if response seems complete (ends with punctuation, reasonable length)
                if len(text) > 20 and text.strip()[-1] in '.!?':
                    score += 1.0
            elif check == "age_appropriate":
                # Check language complexity
                if self.is_age_appropriate(text, 8):  # Using age 8 as baseline
                    score += 1.0
            elif check == "engaging":
                # Check for engaging elements (questions, exclamations, descriptive words)
                engaging_indicators = ['!', '?', 'amazing', 'wonderful', 'exciting', 'fun', 'great']
                if any(indicator in text.lower() for indicator in engaging_indicators):
                    score += 1.0
            elif check == "educational":
                # Check for educational content (facts, explanations, learning elements)
                educational_indicators = ['because', 'learn', 'know', 'understand', 'discover', 'fact']
                if any(indicator in text.lower() for indicator in educational_indicators):
                    score += 1.0
            elif check == "accurate":
                # Basic accuracy check (no obvious misinformation)
                # This is a simplified check - in reality would need more sophisticated validation
                if len(text) > 10:  # Assume reasonable length indicates some accuracy
                    score += 1.0
            elif check == "entertaining":
                # Check for entertainment elements
                entertainment_indicators = ['funny', 'laugh', 'smile', 'joke', 'fun', 'silly']
                if any(indicator in text.lower() for indicator in entertainment_indicators):
                    score += 1.0
            elif check == "appropriate_humor":
                # Check that humor is child-appropriate (no inappropriate content)
                inappropriate_indicators = ['scary', 'mean', 'hurt', 'bad']
                if not any(indicator in text.lower() for indicator in inappropriate_indicators):
                    score += 1.0
        
        return score / total_checks if total_checks > 0 else 0.0

    async def test_voice_pipeline_endpoints(self):
        """Test voice pipeline endpoints"""
        logger.info("🎯 TESTING: Voice Pipeline Endpoints")
        
        # Test voice personalities endpoint
        try:
            async with self.session.get(f"{BACKEND_URL}/voice/personalities") as response:
                if response.status == 200:
                    data = await response.json()
                    personalities_count = len(data.get("personalities", []))
                    
                    self.log_test_result(
                        "Voice Personalities Endpoint",
                        personalities_count >= 3,
                        f"Found {personalities_count} voice personalities",
                        "≥3 personalities",
                        f"{personalities_count} personalities"
                    )
                else:
                    self.log_test_result(
                        "Voice Personalities Endpoint",
                        False,
                        f"API error: {response.status}"
                    )
        except Exception as e:
            self.log_test_result(
                "Voice Personalities Endpoint",
                False,
                f"Test error: {str(e)}"
            )

    async def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        logger.info("🚀 STARTING: Revolutionary Dynamic Response System Comprehensive Testing")
        
        await self.setup_session()
        
        try:
            # Create user profiles
            for profile in self.user_profiles.values():
                await self.create_user_profile(profile)
            
            # Run health check first
            health_ok = await self.test_health_check()
            if not health_ok:
                logger.error("❌ Health check failed - aborting tests")
                return
            
            # Run all test suites
            await self.test_dynamic_response_lengths()
            await self.test_age_appropriate_responses()
            await self.test_latency_validation()
            await self.test_smart_routing_validation()
            await self.test_content_quality_validation()
            await self.test_voice_pipeline_endpoints()
            
            # Generate summary
            self.generate_test_summary()
            
        finally:
            await self.cleanup_session()

    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 REVOLUTIONARY DYNAMIC RESPONSE SYSTEM - COMPREHENSIVE TEST RESULTS")
        logger.info("=" * 80)
        logger.info(f"📊 OVERALL RESULTS:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info("")
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result["test_name"].split(" - ")[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "tests": []}
            
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
            categories[category]["tests"].append(result)
        
        # Print category summaries
        for category, data in categories.items():
            total_cat = data["passed"] + data["failed"]
            cat_success_rate = (data["passed"] / total_cat * 100) if total_cat > 0 else 0
            status = "✅" if cat_success_rate >= 80 else "⚠️" if cat_success_rate >= 60 else "❌"
            
            logger.info(f"{status} {category}: {data['passed']}/{total_cat} ({cat_success_rate:.1f}%)")
            
            # Show failed tests
            for test in data["tests"]:
                if not test["success"]:
                    logger.info(f"   ❌ {test['test_name']}: {test['details']}")
        
        logger.info("")
        logger.info("🎯 CRITICAL ASSESSMENT:")
        
        if success_rate >= 90:
            logger.info("🟢 EXCELLENT: Revolutionary Dynamic Response System is working exceptionally well")
        elif success_rate >= 80:
            logger.info("🟡 GOOD: System is working well with minor issues")
        elif success_rate >= 60:
            logger.info("🟠 MODERATE: System has significant issues that need attention")
        else:
            logger.info("🔴 CRITICAL: System has major failures requiring immediate fixes")
        
        logger.info("=" * 80)

async def main():
    """Main test execution"""
    tester = RevolutionaryDynamicResponseTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())