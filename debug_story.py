#!/usr/bin/env python3
"""
Debug Story Generation - Detailed Analysis
"""

import asyncio
import aiohttp
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = "https://e73353f9-1d22-4a0f-9deb-0707101e1e70.preview.emergentagent.com/api"

async def debug_story_generation():
    """Debug the story generation process"""
    
    async with aiohttp.ClientSession() as session:
        # Create test user
        profile_data = {
            "name": "Debug Child",
            "age": 7,
            "location": "Test City",
            "timezone": "America/New_York",
            "language": "english",
            "voice_personality": "story_narrator",
            "interests": ["stories", "adventures"],
            "learning_goals": ["reading"],
            "parent_email": "debug@example.com"
        }
        
        async with session.post(f"{BACKEND_URL}/users/profile", json=profile_data) as response:
            if response.status == 200:
                user_data = await response.json()
                user_id = user_data["id"]
                logger.info(f"Created debug user: {user_id}")
            else:
                logger.error(f"Failed to create user: {response.status}")
                return
        
        # Create session
        session_data = {
            "user_id": user_id,
            "session_name": "Debug Story Session"
        }
        
        async with session.post(f"{BACKEND_URL}/conversations/session", json=session_data) as response:
            if response.status == 200:
                session_data = await response.json()
                session_id = session_data["id"]
                logger.info(f"Created debug session: {session_id}")
            else:
                logger.error(f"Failed to create session: {response.status}")
                return
        
        # Test story generation with detailed logging
        story_request = "Tell me a complete story about a brave little mouse who goes on an adventure"
        
        text_input = {
            "session_id": session_id,
            "user_id": user_id,
            "message": story_request
        }
        
        logger.info(f"Sending story request: {story_request}")
        
        async with session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
            if response.status == 200:
                data = await response.json()
                story_text = data.get("response_text", "")
                
                print("\n" + "="*80)
                print("DETAILED STORY GENERATION DEBUG")
                print("="*80)
                print(f"Request: {story_request}")
                print(f"Response Status: {response.status}")
                print(f"Content Type: {data.get('content_type', 'unknown')}")
                print(f"Has Audio: {bool(data.get('response_audio'))}")
                print(f"Character Count: {len(story_text)}")
                print(f"Word Count: {len(story_text.split())}")
                print(f"Metadata: {data.get('metadata', {})}")
                print("\nFull Story Response:")
                print("-" * 40)
                print(story_text)
                print("-" * 40)
                
                # Analyze why it's short
                if len(story_text.split()) < 100:
                    print("\n❌ CRITICAL ISSUE: Story is extremely short!")
                    print("Possible causes:")
                    print("1. System message not being applied correctly")
                    print("2. Iterative generation logic not triggering")
                    print("3. Content type detection failing")
                    print("4. API response being truncated")
                    
                    # Check if it looks like a complete response or truncated
                    if story_text.endswith("...") or not story_text.endswith(('.', '!', '?')):
                        print("5. Response appears to be truncated mid-sentence")
                    else:
                        print("5. Response appears complete but very short")
                
            else:
                error_text = await response.text()
                print(f"Error: HTTP {response.status}: {error_text}")

if __name__ == "__main__":
    asyncio.run(debug_story_generation())