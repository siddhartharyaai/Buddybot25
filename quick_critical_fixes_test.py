#!/usr/bin/env python3
"""
Quick Critical Fixes Test
========================
Focused test for the three critical fixes mentioned in the review request.
"""

import asyncio
import aiohttp
import json
import time
import base64
import uuid
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BACKEND_URL = "https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com/api"

async def test_critical_fixes():
    """Test the three critical fixes"""
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
        test_user_id = f"test_user_{int(time.time())}"
        test_session_id = str(uuid.uuid4())
        
        logger.info("🚀 TESTING CRITICAL FIXES")
        logger.info("=" * 50)
        
        # Create test user
        user_data = {
            "name": "Test Child",
            "age": 8,
            "location": "Test City",
            "interests": ["stories", "animals"]
        }
        
        async with session.post(f"{BACKEND_URL}/users/profile", json=user_data) as response:
            if response.status == 201:
                profile = await response.json()
                test_user_id = profile["id"]
                logger.info(f"✅ Created test user: {test_user_id}")
            else:
                logger.error(f"❌ Failed to create test user: {response.status}")
                return
        
        # TEST 1: Welcome Message System
        logger.info("\n🎯 TEST 1: Welcome Message System")
        welcome_request = {
            "user_id": test_user_id,
            "session_id": test_session_id
        }
        
        try:
            async with session.post(f"{BACKEND_URL}/conversations/welcome", json=welcome_request) as response:
                if response.status == 200:
                    welcome_data = await response.json()
                    message = welcome_data.get("message", "")
                    content_type = welcome_data.get("content_type", "")
                    
                    if message and len(message) > 10:
                        logger.info(f"✅ Welcome message generated: '{message[:80]}...'")
                        logger.info(f"✅ Content type: {content_type}")
                    else:
                        logger.error("❌ Welcome message too short or empty")
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Welcome message failed: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"❌ Welcome message error: {str(e)}")
        
        # TEST 2: Content Deduplication (simplified)
        logger.info("\n🔄 TEST 2: Content Deduplication")
        
        # Send same request twice
        request_text = "Tell me about cats"
        responses = []
        
        for i in range(2):
            try:
                text_input = {
                    "session_id": test_session_id,
                    "user_id": test_user_id,
                    "message": request_text
                }
                
                async with session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        response_text = response_data.get("response_text", "")
                        responses.append(response_text)
                        logger.info(f"Response {i+1}: '{response_text[:60]}...'")
                    else:
                        logger.error(f"❌ Text conversation failed: {response.status}")
                        break
                
                await asyncio.sleep(1)  # Small delay
            except Exception as e:
                logger.error(f"❌ Content deduplication error: {str(e)}")
                break
        
        if len(responses) == 2:
            if responses[0] != responses[1]:
                logger.info("✅ Content deduplication working - responses are different")
            else:
                logger.info("⚠️ Responses are identical - deduplication may not be active")
        
        # TEST 3: Ultra-Low Latency Pipeline (TTS only)
        logger.info("\n⚡ TEST 3: Ultra-Low Latency Pipeline")
        
        # Test TTS latency
        tts_request = {
            "text": "Hello, this is a quick test message.",
            "personality": "friendly_companion"
        }
        
        try:
            start_time = time.time()
            async with session.post(f"{BACKEND_URL}/voice/tts", json=tts_request) as response:
                tts_time = time.time() - start_time
                
                if response.status == 200:
                    tts_data = await response.json()
                    audio_base64 = tts_data.get("audio_base64", "")
                    
                    if tts_time < 3.0 and audio_base64:
                        logger.info(f"✅ TTS latency: {tts_time:.2f}s (target <3s)")
                        logger.info(f"✅ Audio generated: {len(audio_base64)} chars")
                    else:
                        logger.error(f"❌ TTS too slow or failed: {tts_time:.2f}s")
                else:
                    error_text = await response.text()
                    logger.error(f"❌ TTS failed: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"❌ TTS error: {str(e)}")
        
        # Test text conversation latency
        try:
            start_time = time.time()
            text_request = {
                "session_id": test_session_id,
                "user_id": test_user_id,
                "message": "What's 2 plus 2?"
            }
            
            async with session.post(f"{BACKEND_URL}/conversations/text", json=text_request) as response:
                text_time = time.time() - start_time
                
                if response.status == 200:
                    response_data = await response.json()
                    response_text = response_data.get("response_text", "")
                    
                    if text_time < 5.0 and response_text:
                        logger.info(f"✅ Text conversation: {text_time:.2f}s")
                        logger.info(f"✅ Response: '{response_text[:60]}...'")
                    else:
                        logger.error(f"❌ Text conversation too slow: {text_time:.2f}s")
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Text conversation failed: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"❌ Text conversation error: {str(e)}")
        
        # REGRESSION TESTS
        logger.info("\n🔍 REGRESSION TESTS")
        
        # Health check
        try:
            async with session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    if health_data.get("status") == "healthy":
                        logger.info("✅ Health check: System healthy")
                    else:
                        logger.error("❌ Health check: System not healthy")
                else:
                    logger.error(f"❌ Health check failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Health check error: {str(e)}")
        
        # Conversation suggestions
        try:
            async with session.get(f"{BACKEND_URL}/conversations/suggestions") as response:
                if response.status == 200:
                    suggestions = await response.json()
                    if isinstance(suggestions, list) and len(suggestions) > 0:
                        logger.info(f"✅ Conversation suggestions: {len(suggestions)} available")
                    else:
                        logger.error("❌ No conversation suggestions available")
                else:
                    logger.error(f"❌ Conversation suggestions failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Conversation suggestions error: {str(e)}")
        
        logger.info("\n" + "=" * 50)
        logger.info("🏁 CRITICAL FIXES TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(test_critical_fixes())