#!/usr/bin/env python3
"""
Comprehensive TTS Fixes Validation - With proper timeouts
"""

import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BACKEND_URL = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com/api"

def test_tts_chunked_threshold():
    """Test 1: TTS Threshold Fix - 1500 char chunking with proper timeout"""
    logger.info("🎯 TEST 1: TTS Chunked Threshold (1500+ chars)")
    
    # Create text over 1500 characters
    long_text = "Tell me a story about a brave little mouse who goes on an amazing adventure through the magical forest. " * 20  # ~2000 chars
    
    try:
        logger.info(f"Testing with {len(long_text)} character text (should trigger chunking)")
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/voice/tts",
            json={"text": long_text, "personality": "story_narrator"},
            timeout=60  # Increased timeout for chunked processing
        )
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success" and result.get("audio_base64"):
                audio_size = len(result["audio_base64"])
                logger.info(f"✅ PASS: TTS Chunked - Generated {audio_size} chars of audio in {processing_time:.1f}s")
                return True
            else:
                logger.info(f"❌ FAIL: TTS Chunked - No audio: {result.get('error', 'Unknown error')}")
                return False
        else:
            logger.info(f"❌ FAIL: TTS Chunked - HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.info(f"❌ FAIL: TTS Chunked - Exception: {str(e)}")
        return False

def test_story_narration_simple():
    """Test 2: Story Narration via text conversation (simpler approach)"""
    logger.info("🎯 TEST 2: Story Narration via Text Conversation")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/conversations/text",
            json={
                "session_id": "test_session_narration",
                "user_id": "test_user_narration",
                "message": "Tell me a short story about a brave little mouse"
            },
            timeout=45  # Increased timeout for story generation + TTS
        )
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            has_text = bool(result.get("response_text"))
            has_audio = bool(result.get("response_audio"))
            content_type = result.get("content_type", "")
            
            if has_text and has_audio:
                text_length = len(result["response_text"])
                audio_length = len(result["response_audio"])
                logger.info(f"✅ PASS: Story Narration - Generated story with text ({text_length} chars) and audio ({audio_length} chars) in {processing_time:.1f}s, type: {content_type}")
                return True
            elif has_text:
                logger.info(f"❌ FAIL: Story Narration - Text only ({len(result['response_text'])} chars), no audio generated")
                return False
            else:
                logger.info(f"❌ FAIL: Story Narration - No content generated: {result}")
                return False
        else:
            logger.info(f"❌ FAIL: Story Narration - HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.info(f"❌ FAIL: Story Narration - Exception: {str(e)}")
        return False

def test_text_to_speech_with_prosody():
    """Test 3: text_to_speech_with_prosody Method (via TTS endpoint)"""
    logger.info("🎯 TEST 3: text_to_speech_with_prosody Method")
    
    try:
        # Test with story-like content that should use prosody
        story_text = "Once upon a time, in a magical kingdom far, far away, there lived a brave little princess who loved adventures!"
        
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/voice/tts",
            json={
                "text": story_text,
                "personality": "story_narrator"
            },
            timeout=20
        )
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success" and result.get("audio_base64"):
                audio_size = len(result["audio_base64"])
                logger.info(f"✅ PASS: TTS with Prosody - Generated {audio_size} chars of audio in {processing_time:.1f}s")
                return True
            else:
                logger.info(f"❌ FAIL: TTS with Prosody - No audio: {result.get('error', 'Unknown')}")
                return False
        else:
            logger.info(f"❌ FAIL: TTS with Prosody - HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.info(f"❌ FAIL: TTS with Prosody - Exception: {str(e)}")
        return False

def test_voice_personalities():
    """Test 4: Voice Personalities Endpoint"""
    logger.info("🎯 TEST 4: Voice Personalities Endpoint")
    
    try:
        response = requests.get(f"{BACKEND_URL}/voice/personalities", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            voices = result.get("voices", [])
            if len(voices) >= 3:
                voice_names = [v.get("name", "Unknown") for v in voices]
                logger.info(f"✅ PASS: Voice Personalities - {len(voices)} personalities: {', '.join(voice_names)}")
                return True
            else:
                logger.info(f"❌ FAIL: Voice Personalities - Only {len(voices)} personalities available")
                return False
        else:
            logger.info(f"❌ FAIL: Voice Personalities - HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.info(f"❌ FAIL: Voice Personalities - Exception: {str(e)}")
        return False

def test_basic_health_check():
    """Test 0: Basic health check"""
    logger.info("🎯 TEST 0: Basic Health Check")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "healthy":
                agents = result.get("agents", {})
                logger.info(f"✅ PASS: Health Check - System healthy, orchestrator: {agents.get('orchestrator')}, gemini: {agents.get('gemini_configured')}, deepgram: {agents.get('deepgram_configured')}")
                return True
            else:
                logger.info(f"❌ FAIL: Health Check - System not healthy: {result}")
                return False
        else:
            logger.info(f"❌ FAIL: Health Check - HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.info(f"❌ FAIL: Health Check - Exception: {str(e)}")
        return False

def main():
    """Run all tests with proper sequencing"""
    logger.info("🚀 Starting Comprehensive TTS Fixes Validation")
    logger.info("=" * 60)
    
    # Run tests in order
    test0 = test_basic_health_check()
    test1 = test_tts_chunked_threshold()
    test2 = test_story_narration_simple()
    test3 = test_text_to_speech_with_prosody()
    test4 = test_voice_personalities()
    
    # Summary
    tests = [test0, test1, test2, test3, test4]
    test_names = ["Health Check", "TTS Chunked Threshold", "Story Narration", "TTS with Prosody", "Voice Personalities"]
    
    passed = sum(tests)
    total = len(tests)
    success_rate = (passed / total) * 100
    
    logger.info("=" * 60)
    logger.info("🎯 COMPREHENSIVE TTS FIXES VALIDATION SUMMARY")
    logger.info("=" * 60)
    
    for i, (test_result, test_name) in enumerate(zip(tests, test_names)):
        status = "✅ PASS" if test_result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("=" * 60)
    logger.info(f"📊 OVERALL RESULTS: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    # Critical assessment
    critical_tests = [test1, test2, test3]  # The 3 main TTS fixes
    critical_passed = sum(critical_tests)
    critical_rate = (critical_passed / 3) * 100
    
    logger.info(f"🎯 CRITICAL TTS FIXES: {critical_passed}/3 passed ({critical_rate:.1f}%)")
    
    if critical_rate >= 100:
        logger.info("🎉 TTS FIXES: ALL CRITICAL ISSUES RESOLVED")
    elif critical_rate >= 67:
        logger.info("✅ TTS FIXES: MOSTLY RESOLVED - MINOR ISSUES REMAIN")
    elif critical_rate >= 33:
        logger.info("⚠️ TTS FIXES: PARTIAL SUCCESS - SIGNIFICANT ISSUES REMAIN")
    else:
        logger.info("🚨 TTS FIXES: CRITICAL FAILURES - URGENT ATTENTION NEEDED")
    
    return {
        "total_success_rate": success_rate,
        "critical_success_rate": critical_rate,
        "individual_results": dict(zip(test_names, tests))
    }

if __name__ == "__main__":
    main()