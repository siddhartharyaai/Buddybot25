#!/usr/bin/env python3
"""
Quick Story Generation Test - Focused on the critical issue
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://5989f568-2718-4892-b46b-e42563583d9e.preview.emergentagent.com/api"

async def test_story_generation():
    """Test story generation length issue"""
    async with aiohttp.ClientSession() as session:
        # Create test user
        profile_data = {
            "name": "Story Test Child",
            "age": 7,
            "location": "Test City",
            "timezone": "America/New_York",
            "language": "english",
            "voice_personality": "friendly_companion",
            "interests": ["stories"],
            "learning_goals": ["reading"],
            "parent_email": "test@example.com"
        }
        
        async with session.post(f"{BACKEND_URL}/users/profile", json=profile_data) as response:
            if response.status == 200:
                user_data = await response.json()
                user_id = user_data["id"]
                
                # Test story generation
                text_input = {
                    "session_id": "story_test_session",
                    "user_id": user_id,
                    "message": "Tell me a complete story about a brave little mouse adventure"
                }
                
                async with session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as story_response:
                    if story_response.status == 200:
                        story_data = await story_response.json()
                        story_text = story_data.get("response_text", "")
                        word_count = len(story_text.split())
                        
                        print(f"🔍 STORY GENERATION TEST RESULTS:")
                        print(f"   Story Word Count: {word_count}")
                        print(f"   Character Count: {len(story_text)}")
                        print(f"   Content Type: {story_data.get('content_type', 'unknown')}")
                        print(f"   Meets 300+ Word Requirement: {'✅ YES' if word_count >= 300 else '❌ NO'}")
                        print(f"   Story Preview: {story_text[:200]}...")
                        
                        return {
                            "word_count": word_count,
                            "meets_requirement": word_count >= 300,
                            "story_text": story_text
                        }
                    else:
                        print(f"❌ Story generation failed: HTTP {story_response.status}")
                        return {"error": f"HTTP {story_response.status}"}
            else:
                print(f"❌ User creation failed: HTTP {response.status}")
                return {"error": f"HTTP {response.status}"}

if __name__ == "__main__":
    result = asyncio.run(test_story_generation())
    print(f"\n📊 Final Result: {result}")