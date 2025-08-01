#!/usr/bin/env python3
"""
Quick TTS Fixes Test - Focus on the 3 critical issues
"""

import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BACKEND_URL = "https://0e5dcf5a-4e8d-4074-9227-19f4607bd0be.preview.emergentagent.com/api"

def test_tts_chunked_threshold():
    """Test 1: TTS Threshold Fix - 1500 char chunking"""
    logger.info("🎯 TEST 1: TTS Chunked Threshold (1500+ chars)")
    
    # Create text over 1500 characters
    long_text = "Tell me a story about a brave little mouse. " * 40  # ~1760 chars
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/voice/tts",
            json={"text": long_text, "personality": "story_narrator"},
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success" and result.get("audio_base64"):
                logger.info(f"✅ PASS: TTS Chunked - Generated audio for {len(long_text)} chars")
                return True
            else:
                logger.info(f"❌ FAIL: TTS Chunked - No audio: {result.get('error', 'Unknown error')}")
                return False
        else:
            logger.info(f"❌ FAIL: TTS Chunked - HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.info(f"❌ FAIL: TTS Chunked - Exception: {str(e)}")
        return False

def test_story_narration_endpoint():
    """Test 2: Story Narration Endpoint"""
    logger.info("🎯 TEST 2: Story Narration Endpoint")
    
    try:
        # Test with a simple story request using text conversation
        response = requests.post(
            f"{BACKEND_URL}/conversations/text",
            json={
                "session_id": "test_session",
                "user_id": "test_user",
                "message": "Tell me a story about a brave little mouse"
            },
            timeout=25
        )
        
        if response.status_code == 200:
            result = response.json()
            has_text = bool(result.get("response_text"))
            has_audio = bool(result.get("response_audio"))
            
            if has_text and has_audio:
                logger.info(f"✅ PASS: Story Narration - Both text and audio generated")
                return True
            elif has_text:
                logger.info(f"❌ FAIL: Story Narration - Text only, no audio")
                return False
            else:
                logger.info(f"❌ FAIL: Story Narration - No content generated")
                return False
        else:
            logger.info(f"❌ FAIL: Story Narration - HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.info(f"❌ FAIL: Story Narration - Exception: {str(e)}")
        return False

def test_text_to_speech_with_prosody():
    """Test 3: text_to_speech_with_prosody Method"""
    logger.info("🎯 TEST 3: text_to_speech_with_prosody Method")
    
    try:
        # Test simple TTS to verify prosody method works
        response = requests.post(
            f"{BACKEND_URL}/voice/tts",
            json={
                "text": "Once upon a time, there was a magical adventure waiting to unfold!",
                "personality": "story_narrator"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success" and result.get("audio_base64"):
                audio_size = len(result["audio_base64"])
                logger.info(f"✅ PASS: TTS with Prosody - Generated {audio_size} chars of audio")
                return True
            else:
                logger.info(f"❌ FAIL: TTS with Prosody - No audio: {result.get('error', 'Unknown')}")
                return False
        else:
            logger.info(f"❌ FAIL: TTS with Prosody - HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.info(f"❌ FAIL: TTS with Prosody - Exception: {str(e)}")
        return False

def test_voice_personalities():
    """Test 4: Voice Personalities Endpoint (bonus)"""
    logger.info("🎯 TEST 4: Voice Personalities Endpoint")
    
    try:
        response = requests.get(f"{BACKEND_URL}/voice/personalities", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            voices = result.get("voices", [])
            if len(voices) >= 3:
                logger.info(f"✅ PASS: Voice Personalities - {len(voices)} personalities available")
                return True
            else:
                logger.info(f"❌ FAIL: Voice Personalities - Only {len(voices)} personalities")
                return False
        else:
            logger.info(f"❌ FAIL: Voice Personalities - HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.info(f"❌ FAIL: Voice Personalities - Exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting Quick TTS Fixes Validation")
    logger.info("=" * 50)
    
    # Run tests
    test1 = test_tts_chunked_threshold()
    test2 = test_story_narration_endpoint()
    test3 = test_text_to_speech_with_prosody()
    test4 = test_voice_personalities()
    
    # Summary
    passed = sum([test1, test2, test3, test4])
    total = 4
    success_rate = (passed / total) * 100
    
    logger.info("=" * 50)
    logger.info(f"📊 RESULTS: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        logger.info("🎉 TTS FIXES: MOSTLY WORKING")
    elif success_rate >= 50:
        logger.info("⚠️ TTS FIXES: PARTIAL SUCCESS")
    else:
        logger.info("🚨 TTS FIXES: CRITICAL FAILURES")
    
    return success_rate

if __name__ == "__main__":
    main()