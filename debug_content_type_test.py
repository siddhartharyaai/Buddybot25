#!/usr/bin/env python3
"""
Debug Content Type Detection Test
"""

import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = "https://0e5dcf5a-4e8d-4074-9227-19f4607bd0be.preview.emergentagent.com/api"

async def test_content_type_detection():
    async with aiohttp.ClientSession() as session:
        test_cases = [
            "Tell me about a magnificent animal that is extraordinary",
            "What colors do you like?",
            "Tell me about puppies",
            "Can you tell me a story?",
            "Tell me a story about animals"
        ]
        
        for test_input in test_cases:
            test_data = {
                "session_id": f"debug_session_{hash(test_input)}",
                "user_id": "debug_user_age5",
                "message": test_input
            }
            
            logger.info(f"Testing input: {test_input}")
            
            try:
                async with session.post(f"{BACKEND_URL}/conversations/text", json=test_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "")
                        content_type = result.get("content_type", "unknown")
                        
                        logger.info(f"Content type detected: {content_type}")
                        logger.info(f"Response length: {len(response_text)} chars")
                        logger.info(f"Response preview: {response_text[:100]}...")
                        
                        # Check for forbidden words
                        forbidden_words = ['magnificent', 'extraordinary']
                        found_forbidden = [word for word in forbidden_words if word.lower() in response_text.lower()]
                        
                        logger.info(f"Forbidden words found: {found_forbidden}")
                        logger.info("-" * 60)
                        
                    else:
                        logger.error(f"Request failed: {response.status}")
                        
            except Exception as e:
                logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_content_type_detection())