#!/usr/bin/env python3
"""
Deep Story Narration Investigation
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://a720410a-cd33-47aa-8dde-f4048df3b4e9.preview.emergentagent.com/api"

async def investigate_story_narration():
    async with aiohttp.ClientSession() as session:
        
        # Create test user
        profile_data = {
            "name": "Story Test Child",
            "age": 8,
            "location": "Test City",
            "timezone": "America/New_York",
            "language": "english",
            "voice_personality": "story_narrator",
            "interests": ["stories", "animals"],
            "learning_goals": ["reading"],
            "parent_email": "test@example.com"
        }
        
        async with session.post(f"{BACKEND_URL}/users/profile", json=profile_data) as response:
            if response.status == 200:
                user_data = await response.json()
                test_user_id = user_data["id"]
                print(f"✅ Created test user: {test_user_id}")
            else:
                print(f"❌ Failed to create user: HTTP {response.status}")
                return
        
        # Get available stories
        print("\n🔍 Investigating available stories...")
        async with session.get(f"{BACKEND_URL}/content/stories") as response:
            if response.status == 200:
                stories_data = await response.json()
                stories = stories_data.get("stories", [])
                print(f"📚 Found {len(stories)} stories")
                
                for i, story in enumerate(stories[:3]):  # Check first 3 stories
                    print(f"\nStory {i+1}: {story.get('title', 'No title')}")
                    print(f"  ID: {story.get('id', 'No ID')}")
                    print(f"  Content length: {len(story.get('content', ''))} chars")
                    print(f"  Content preview: {story.get('content', '')[:100]}...")
                    
                    # Test narration for this story
                    story_id = story.get("id")
                    if story_id:
                        narration_request = {
                            "user_id": test_user_id,
                            "full_narration": True,
                            "voice_personality": "story_narrator"
                        }
                        
                        print(f"\n🎭 Testing narration for story: {story_id}")
                        async with session.post(f"{BACKEND_URL}/content/stories/{story_id}/narrate", json=narration_request) as narrate_response:
                            print(f"  Response status: {narrate_response.status}")
                            
                            if narrate_response.status == 200:
                                narration_data = await narrate_response.json()
                                response_text = narration_data.get("response_text", "")
                                response_audio = narration_data.get("response_audio", "")
                                narration_complete = narration_data.get("narration_complete", False)
                                content_type = narration_data.get("content_type", "")
                                
                                print(f"  Response text length: {len(response_text)} chars")
                                print(f"  Response audio size: {len(response_audio) if response_audio else 0} bytes")
                                print(f"  Narration complete: {narration_complete}")
                                print(f"  Content type: {content_type}")
                                print(f"  Response text: '{response_text}'")
                                
                                if len(response_text) < 100:
                                    print("  ⚠️ WARNING: Response text is very short!")
                                
                                # Check metadata
                                metadata = narration_data.get("metadata", {})
                                if metadata:
                                    print(f"  Metadata: {metadata}")
                                
                            else:
                                error_text = await narrate_response.text()
                                print(f"  ❌ Error: {error_text}")
                    
                    print("-" * 50)
            else:
                print(f"❌ Failed to get stories: HTTP {response.status}")
        
        # Test text conversation for comparison
        print("\n🔍 Testing text conversation for comparison...")
        story_request = {
            "session_id": f"test_session_{test_user_id}",
            "user_id": test_user_id,
            "message": "Please tell me a complete story about a brave little mouse who goes on an adventure. Make it a full story with beginning, middle, and end."
        }
        
        async with session.post(f"{BACKEND_URL}/conversations/text", json=story_request) as response:
            if response.status == 200:
                data = await response.json()
                response_text = data.get("response_text", "")
                response_audio = data.get("response_audio", "")
                content_type = data.get("content_type", "")
                
                print(f"Text conversation response:")
                print(f"  Response text length: {len(response_text)} chars")
                print(f"  Response audio size: {len(response_audio) if response_audio else 0} bytes")
                print(f"  Content type: {content_type}")
                print(f"  Response preview: {response_text[:200]}...")
                
                if len(response_text) > 200:
                    print("  ✅ Text conversation generates longer responses")
                else:
                    print("  ⚠️ Text conversation also generates short responses")
            else:
                error_text = await response.text()
                print(f"❌ Text conversation failed: HTTP {response.status}: {error_text}")

if __name__ == "__main__":
    asyncio.run(investigate_story_narration())