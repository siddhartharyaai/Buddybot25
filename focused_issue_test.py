#!/usr/bin/env python3
"""
FOCUSED ISSUE ANALYSIS TEST
==========================

This test focuses on the specific critical issues identified:
1. STT functionality broken (HTTP 422 errors)
2. Story generation producing only 23-28 words instead of 300+
3. Story narration endpoint failing with HTTP 422
4. Context continuity issues
"""

import asyncio
import aiohttp
import base64
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://0e5dcf5a-4e8d-4074-9227-19f4607bd0be.preview.emergentagent.com/api"
TEST_USER_ID = "focused_test_user"
TEST_SESSION_ID = "focused_session"

async def test_voice_processing_detailed():
    """Detailed analysis of voice processing issues"""
    logger.info("🔍 Analyzing voice processing issues...")
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Check what the voice endpoint expects
        logger.info("Testing voice endpoint with minimal valid data...")
        
        # Create minimal test audio
        test_audio = base64.b64encode(b'\x00' * 100).decode('utf-8')
        
        # Test different payload formats
        test_cases = [
            {
                "name": "Form data format",
                "data": {
                    "session_id": TEST_SESSION_ID,
                    "user_id": TEST_USER_ID,
                    "audio_base64": test_audio
                },
                "content_type": "application/x-www-form-urlencoded"
            },
            {
                "name": "JSON format",
                "data": {
                    "session_id": TEST_SESSION_ID,
                    "user_id": TEST_USER_ID,
                    "audio_base64": test_audio
                },
                "content_type": "application/json"
            }
        ]
        
        for test_case in test_cases:
            try:
                if test_case["content_type"] == "application/json":
                    async with session.post(
                        f"{BASE_URL}/voice/process_audio",
                        json=test_case["data"]
                    ) as response:
                        response_text = await response.text()
                        logger.info(f"{test_case['name']}: HTTP {response.status}")
                        if response.status != 200:
                            logger.info(f"Response: {response_text[:200]}...")
                else:
                    async with session.post(
                        f"{BASE_URL}/voice/process_audio",
                        data=test_case["data"]
                    ) as response:
                        response_text = await response.text()
                        logger.info(f"{test_case['name']}: HTTP {response.status}")
                        if response.status != 200:
                            logger.info(f"Response: {response_text[:200]}...")
                            
            except Exception as e:
                logger.error(f"{test_case['name']} error: {str(e)}")

async def test_story_generation_detailed():
    """Detailed analysis of story generation issues"""
    logger.info("🔍 Analyzing story generation issues...")
    
    async with aiohttp.ClientSession() as session:
        # Test story generation through text conversation
        story_requests = [
            "Tell me a complete story about a brave little mouse. Make it at least 300 words long with a beginning, middle, and end.",
            "I want a full detailed story about magical adventures. Please make it very long and complete.",
            "Create a comprehensive story with lots of details, characters, and a complete plot. Make it as long as possible."
        ]
        
        for i, request in enumerate(story_requests, 1):
            try:
                payload = {
                    "session_id": f"{TEST_SESSION_ID}_{i}",
                    "user_id": TEST_USER_ID,
                    "message": request
                }
                
                logger.info(f"Testing story request {i}: '{request[:50]}...'")
                
                async with session.post(
                    f"{BASE_URL}/conversations/text",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        word_count = len(response_text.split())
                        
                        logger.info(f"Story {i} result: {word_count} words")
                        logger.info(f"Story {i} preview: '{response_text[:100]}...'")
                        
                        # Check for story structure
                        has_beginning = any(word in response_text.lower() for word in ["once", "there was", "long ago", "in a"])
                        has_ending = any(word in response_text.lower() for word in ["the end", "happily", "finally", "and so"])
                        
                        logger.info(f"Story {i} structure: Beginning={has_beginning}, Ending={has_ending}")
                        
                    else:
                        response_text = await response.text()
                        logger.error(f"Story {i} failed: HTTP {response.status}")
                        logger.error(f"Error response: {response_text[:200]}...")
                        
            except Exception as e:
                logger.error(f"Story {i} error: {str(e)}")

async def test_story_narration_detailed():
    """Detailed analysis of story narration issues"""
    logger.info("🔍 Analyzing story narration issues...")
    
    async with aiohttp.ClientSession() as session:
        # First get available stories
        try:
            async with session.get(f"{BASE_URL}/content/stories") as response:
                if response.status == 200:
                    data = await response.json()
                    stories = data.get("stories", [])
                    logger.info(f"Found {len(stories)} stories available")
                    
                    if stories:
                        # Test narration for first story
                        story = stories[0]
                        story_id = story.get("id", "")
                        story_title = story.get("title", "Unknown")
                        
                        logger.info(f"Testing narration for: '{story_title}' (ID: {story_id})")
                        
                        # Test different payload formats for narration
                        test_formats = [
                            {"name": "Form data", "data": {"user_id": TEST_USER_ID}, "use_json": False},
                            {"name": "JSON data", "data": {"user_id": TEST_USER_ID}, "use_json": True}
                        ]
                        
                        for test_format in test_formats:
                            try:
                                if test_format["use_json"]:
                                    async with session.post(
                                        f"{BASE_URL}/content/stories/{story_id}/narrate",
                                        json=test_format["data"]
                                    ) as response:
                                        response_text = await response.text()
                                        logger.info(f"Narration {test_format['name']}: HTTP {response.status}")
                                        if response.status != 200:
                                            logger.info(f"Response: {response_text[:200]}...")
                                else:
                                    async with session.post(
                                        f"{BASE_URL}/content/stories/{story_id}/narrate",
                                        data=test_format["data"]
                                    ) as response:
                                        response_text = await response.text()
                                        logger.info(f"Narration {test_format['name']}: HTTP {response.status}")
                                        if response.status == 200:
                                            data = await response.json()
                                            text_length = len(data.get("response_text", ""))
                                            audio_length = len(str(data.get("response_audio", "")))
                                            logger.info(f"Success: Text={text_length} chars, Audio={audio_length} chars")
                                        else:
                                            logger.info(f"Response: {response_text[:200]}...")
                                            
                            except Exception as e:
                                logger.error(f"Narration {test_format['name']} error: {str(e)}")
                    else:
                        logger.warning("No stories found to test narration")
                else:
                    response_text = await response.text()
                    logger.error(f"Failed to get stories: HTTP {response.status}")
                    logger.error(f"Response: {response_text[:200]}...")
                    
        except Exception as e:
            logger.error(f"Story narration test error: {str(e)}")

async def test_context_detailed():
    """Detailed analysis of context continuity issues"""
    logger.info("🔍 Analyzing context continuity issues...")
    
    async with aiohttp.ClientSession() as session:
        # Test simple context preservation
        session_id = f"{TEST_SESSION_ID}_context"
        
        conversation = [
            {"message": "My name is Alice", "expect": "alice"},
            {"message": "What is my name?", "expect": "alice"},
            {"message": "I like cats", "expect": "cat"},
            {"message": "What do I like?", "expect": "cat"}
        ]
        
        for i, turn in enumerate(conversation, 1):
            try:
                payload = {
                    "session_id": session_id,  # Same session for context
                    "user_id": TEST_USER_ID,
                    "message": turn["message"]
                }
                
                logger.info(f"Context turn {i}: '{turn['message']}'")
                
                async with session.post(
                    f"{BASE_URL}/conversations/text",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "").lower()
                        
                        has_expected = turn["expect"] in response_text
                        logger.info(f"Turn {i} response: '{response_text[:100]}...'")
                        logger.info(f"Turn {i} context check: Expected '{turn['expect']}' - {'Found' if has_expected else 'Missing'}")
                        
                    else:
                        response_text = await response.text()
                        logger.error(f"Turn {i} failed: HTTP {response.status}")
                        logger.error(f"Error: {response_text[:200]}...")
                        
                # Small delay between turns
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Context turn {i} error: {str(e)}")

async def main():
    """Run focused issue analysis"""
    logger.info("🚀 Starting Focused Issue Analysis...")
    
    await test_voice_processing_detailed()
    await test_story_generation_detailed()
    await test_story_narration_detailed()
    await test_context_detailed()
    
    logger.info("✅ Focused Issue Analysis Complete")

if __name__ == "__main__":
    asyncio.run(main())