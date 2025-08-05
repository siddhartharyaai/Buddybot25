#!/usr/bin/env python3
"""
Quick Age-Appropriate Language Post-Processing Test
"""

import asyncio
import aiohttp
import json
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = "https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com/api"

async def test_post_processing():
    async with aiohttp.ClientSession() as session:
        # Test with existing user or create simple one
        test_data = {
            "session_id": "test_session_123",
            "user_id": "test_user_age5",
            "message": "Tell me about a magnificent animal that is extraordinary"
        }
        
        logger.info("Testing age-appropriate language post-processing...")
        logger.info(f"Input: {test_data['message']}")
        
        try:
            async with session.post(f"{BACKEND_URL}/conversations/text", json=test_data) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response_text", "")
                    
                    logger.info(f"Response: {response_text}")
                    
                    # Check for forbidden words
                    forbidden_words = ['magnificent', 'extraordinary', 'tremendous', 'sophisticated']
                    found_forbidden = []
                    
                    for word in forbidden_words:
                        if re.search(r'\b' + word + r'\b', response_text.lower()):
                            found_forbidden.append(word)
                    
                    # Check for expected replacements
                    expected_replacements = ['big and fun', 'super cool', 'really big', 'awesome', 'amazing']
                    found_replacements = []
                    
                    for replacement in expected_replacements:
                        if replacement.lower() in response_text.lower():
                            found_replacements.append(replacement)
                    
                    # Analyze sentence length
                    sentences = re.split(r'(?<=[.!?])\s+', response_text)
                    sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
                    avg_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
                    
                    logger.info("=" * 60)
                    logger.info("POST-PROCESSING ANALYSIS:")
                    logger.info(f"Forbidden words found: {found_forbidden}")
                    logger.info(f"Expected replacements found: {found_replacements}")
                    logger.info(f"Average sentence length: {avg_length:.1f} words")
                    logger.info(f"Sentence lengths: {sentence_lengths}")
                    
                    # Assessment
                    vocab_compliant = len(found_forbidden) == 0
                    sentence_compliant = all(length <= 8 for length in sentence_lengths)  # Age 5 limit
                    
                    logger.info("=" * 60)
                    logger.info("COMPLIANCE ASSESSMENT:")
                    logger.info(f"Vocabulary compliant: {'✅' if vocab_compliant else '❌'}")
                    logger.info(f"Sentence length compliant: {'✅' if sentence_compliant else '❌'}")
                    logger.info(f"Overall compliant: {'✅' if vocab_compliant and sentence_compliant else '❌'}")
                    
                    if vocab_compliant and sentence_compliant:
                        logger.info("🎉 Age-appropriate language post-processing is WORKING!")
                    else:
                        logger.info("❌ Age-appropriate language post-processing has ISSUES!")
                        
                else:
                    error_text = await response.text()
                    logger.error(f"Request failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_post_processing())