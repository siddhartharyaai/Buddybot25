#!/usr/bin/env python3
"""
Simple story generation test
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com/api"

async def test_story_generation():
    async with aiohttp.ClientSession() as session:
        # Test with existing user from previous test
        user_id = "85e4cb04-29dd-4645-89f6-a323e3c1994a"  # From previous test
        session_id = "debug_session_123"
        
        # Test story generation
        story_request = "Tell me a complete story about a brave little mouse who goes on an adventure. Make it a full story with beginning, middle, and end."
        
        text_data = {
            "session_id": session_id,
            "user_id": user_id,
            "message": story_request
        }
        
        print(f"Testing story generation with user: {user_id}")
        print(f"Request: {story_request}")
        
        async with session.post(f"{BACKEND_URL}/conversations/text", json=text_data) as story_response:
            print(f"Response status: {story_response.status}")
            
            if story_response.status == 200:
                story_data = await story_response.json()
                response_text = story_data.get("response_text", "")
                word_count = len(response_text.split())
                
                print(f"\n=== STORY GENERATION RESULTS ===")
                print(f"Response length: {len(response_text)} characters")
                print(f"Word count: {word_count} words")
                print(f"Content type: {story_data.get('content_type')}")
                print(f"Meets 300+ word requirement: {word_count >= 300}")
                print(f"Has response audio: {bool(story_data.get('response_audio'))}")
                
                print(f"\n=== FULL STORY RESPONSE ===")
                print(response_text)
                
                # Check narrative structure
                response_lower = response_text.lower()
                structure_elements = {
                    "opening": any(phrase in response_lower for phrase in [
                        "once upon a time", "long ago", "there was", "there lived",
                        "in a", "one day", "once there was"
                    ]),
                    "character": "mouse" in response_lower,
                    "adventure": "adventure" in response_lower or "journey" in response_lower,
                    "challenge": any(phrase in response_lower for phrase in [
                        "problem", "challenge", "difficulty", "trouble", "lost",
                        "scared", "worried", "needed", "wanted"
                    ]),
                    "resolution": any(phrase in response_lower for phrase in [
                        "finally", "at last", "in the end", "solved", "found",
                        "happy", "safe", "home", "learned", "realized"
                    ])
                }
                
                print(f"\n=== NARRATIVE STRUCTURE ANALYSIS ===")
                for element, found in structure_elements.items():
                    print(f"{element.capitalize()}: {'✅' if found else '❌'}")
                
                structure_score = sum(structure_elements.values())
                print(f"Structure score: {structure_score}/5")
                
            else:
                error_text = await story_response.text()
                print(f"Story generation failed: {story_response.status}")
                print(f"Error: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_story_generation())