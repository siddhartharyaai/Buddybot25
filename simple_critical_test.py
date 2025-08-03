#!/usr/bin/env python3
"""
Simple Critical Backend Test for Buddy AI
Focus on the most critical issues from review request
"""

import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_backend_url():
    """Get backend URL from frontend .env file"""
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    url = line.split('=', 1)[1].strip()
                    return f"{url}/api"
        return "http://localhost:8001/api"
    except Exception as e:
        logger.warning(f"Could not read frontend .env: {e}")
        return "http://localhost:8001/api"

def test_health_check(backend_url):
    """Test basic health check"""
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', {})
            logger.info(f"✅ Health Check: {response.status_code} - Orchestrator: {agents.get('orchestrator')}, Gemini: {agents.get('gemini_configured')}, Deepgram: {agents.get('deepgram_configured')}")
            return True
        else:
            logger.error(f"❌ Health Check: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Health Check: Exception {str(e)}")
        return False

def test_story_generation(backend_url):
    """Test story generation word count"""
    try:
        test_user_id = f"test_user_{int(time.time())}"
        payload = {
            "session_id": f"test_session_{int(time.time())}",
            "user_id": test_user_id,
            "message": "Tell me a complete story about a brave little mouse adventure"
        }
        
        start_time = time.time()
        response = requests.post(f"{backend_url}/conversations/text", json=payload, timeout=30)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response_text', '')
            word_count = len(response_text.split())
            
            meets_requirement = word_count >= 300
            status = "✅" if meets_requirement else "❌"
            logger.info(f"{status} Story Generation: {word_count} words in {duration:.2f}s. Meets 300+ requirement: {meets_requirement}")
            logger.info(f"   Story preview: {response_text[:150]}...")
            return meets_requirement
        else:
            logger.error(f"❌ Story Generation: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Story Generation: Exception {str(e)}")
        return False

def test_template_system(backend_url):
    """Test template system suggestions"""
    try:
        response = requests.get(f"{backend_url}/conversations/suggestions", timeout=10)
        if response.status_code == 200:
            suggestions = response.json()
            suggestion_count = len(suggestions) if isinstance(suggestions, list) else 0
            
            # Check for template patterns
            patterns_found = []
            expected_patterns = ["story", "song", "joke", "fact", "help"]
            
            for suggestion in suggestions:
                suggestion_lower = suggestion.lower()
                for pattern in expected_patterns:
                    if pattern in suggestion_lower:
                        patterns_found.append(pattern)
            
            unique_patterns = list(set(patterns_found))
            success = len(unique_patterns) >= 3 and suggestion_count >= 5
            
            status = "✅" if success else "❌"
            logger.info(f"{status} Template System: {suggestion_count} suggestions, {len(unique_patterns)} pattern types: {unique_patterns}")
            logger.info(f"   Sample suggestions: {suggestions[:3] if suggestions else 'None'}")
            return success
        else:
            logger.error(f"❌ Template System: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Template System: Exception {str(e)}")
        return False

def test_voice_personalities(backend_url):
    """Test voice personalities endpoint"""
    try:
        response = requests.get(f"{backend_url}/voice/personalities", timeout=10)
        if response.status_code == 200:
            personalities = response.json()
            
            if isinstance(personalities, (list, dict)) and personalities:
                personality_count = len(personalities) if isinstance(personalities, list) else len(personalities.keys())
                success = personality_count >= 3
                status = "✅" if success else "❌"
                logger.info(f"{status} Voice Personalities: {personality_count} personalities available")
                logger.info(f"   Personalities: {personalities}")
                return success
            else:
                logger.error(f"❌ Voice Personalities: Empty response")
                return False
        else:
            logger.error(f"❌ Voice Personalities: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Voice Personalities: Exception {str(e)}")
        return False

def test_latency(backend_url):
    """Test response latency"""
    try:
        test_user_id = f"latency_user_{int(time.time())}"
        payload = {
            "session_id": f"latency_session_{int(time.time())}",
            "user_id": test_user_id,
            "message": "Hello, how are you today?"
        }
        
        start_time = time.time()
        response = requests.post(f"{backend_url}/conversations/text", json=payload, timeout=15)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response_text', '')
            
            if response_text and len(response_text) > 10:
                ultra_fast = duration < 0.5
                acceptable = duration < 1.5
                
                if ultra_fast:
                    status = "✅ ULTRA-FAST"
                elif acceptable:
                    status = "✅ ACCEPTABLE"
                else:
                    status = "❌ SLOW"
                
                logger.info(f"{status} Latency: {duration:.3f}s (Target: <0.5s ultra-fast, <1.5s acceptable)")
                logger.info(f"   Response: {response_text[:100]}...")
                return acceptable
            else:
                logger.error(f"❌ Latency: Invalid response in {duration:.3f}s")
                return False
        else:
            logger.error(f"❌ Latency: HTTP {response.status_code} in {duration:.3f}s")
            return False
    except Exception as e:
        logger.error(f"❌ Latency: Exception {str(e)}")
        return False

def test_user_profile(backend_url):
    """Test user profile functionality"""
    try:
        # Create test user profile
        test_user_data = {
            "name": f"TestUser_{int(time.time())}",
            "age": 7,
            "location": "Test City",
            "timezone": "UTC",
            "language": "english",
            "voice_personality": "friendly_companion",
            "interests": ["stories", "animals"],
            "learning_goals": ["creativity"],
            "gender": "prefer_not_to_say",
            "avatar": "bunny",
            "speech_speed": "normal",
            "energy_level": "balanced"
        }
        
        # Test profile creation
        response = requests.post(f"{backend_url}/users/profile", json=test_user_data, timeout=10)
        if response.status_code == 201:
            profile_data = response.json()
            user_id = profile_data.get('id')
            
            if user_id:
                # Test profile retrieval
                get_response = requests.get(f"{backend_url}/users/profile/{user_id}", timeout=10)
                if get_response.status_code == 200:
                    retrieved_profile = get_response.json()
                    success = retrieved_profile.get('name') == profile_data.get('name')
                    status = "✅" if success else "❌"
                    logger.info(f"{status} User Profile: Created and retrieved. User ID: {user_id}, Name: {retrieved_profile.get('name')}")
                    return success
                else:
                    logger.error(f"❌ User Profile: Retrieval failed HTTP {get_response.status_code}")
                    return False
            else:
                logger.error(f"❌ User Profile: Creation response missing user ID")
                return False
        else:
            logger.error(f"❌ User Profile: Creation failed HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ User Profile: Exception {str(e)}")
        return False

def main():
    """Run critical backend tests"""
    backend_url = get_backend_url()
    logger.info(f"🚀 Starting Critical Backend Tests")
    logger.info(f"Backend URL: {backend_url}")
    logger.info("="*60)
    
    # Run critical tests
    tests = [
        ("Health Check", test_health_check),
        ("Story Generation (300+ words)", test_story_generation),
        ("Template System", test_template_system),
        ("Voice Personalities", test_voice_personalities),
        ("Ultra-Low Latency", test_latency),
        ("User Profile", test_user_profile)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Testing: {test_name}")
        try:
            result = test_func(backend_url)
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name}: Critical error {str(e)}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("🎯 CRITICAL BACKEND TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal Tests: {total}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {total - passed}")
    logger.info(f"Success Rate: {success_rate:.1f}%")
    
    # Critical issues analysis
    critical_failures = []
    for test_name, result in results:
        if not result and any(keyword in test_name for keyword in 
            ['Story Generation', 'Template System', 'Ultra-Low Latency']):
            critical_failures.append(test_name)
    
    if critical_failures:
        logger.error(f"\n🚨 CRITICAL FAILURES DETECTED: {critical_failures}")
    else:
        logger.info(f"\n✅ All critical systems operational")
    
    logger.info("="*60)
    
    return success_rate >= 70

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Critical backend testing completed successfully!")
    else:
        print("\n❌ Critical backend testing revealed major issues!")