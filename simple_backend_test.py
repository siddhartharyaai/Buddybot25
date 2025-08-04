#!/usr/bin/env python3
"""
Simple Backend Test for Voice Processing
"""

import asyncio
import aiohttp
import json
import base64
import uuid

BACKEND_URL = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com/api"

async def test_backend():
    """Test key backend functionality"""
    
    print("🔍 BACKEND TESTING - VOICE PROCESSING FOCUS")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Health Check
        print("\n1. Health Check")
        try:
            async with session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Status: {data.get('status')}")
                    print(f"   ✅ Orchestrator: {data.get('agents', {}).get('orchestrator')}")
                    print(f"   ✅ Deepgram: {data.get('agents', {}).get('deepgram_configured')}")
                    print(f"   ✅ Gemini: {data.get('agents', {}).get('gemini_configured')}")
                else:
                    print(f"   ❌ Failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 2. Create User Profile
        print("\n2. User Profile Creation")
        test_user_id = None
        try:
            profile_data = {
                "name": "Test User",
                "age": 7,
                "location": "Test City",
                "timezone": "America/New_York",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories"],
                "learning_goals": ["listening"],
                "parent_email": "test@example.com"
            }
            
            async with session.post(f"{BACKEND_URL}/users/profile", json=profile_data) as response:
                if response.status == 200:
                    data = await response.json()
                    test_user_id = data["id"]
                    print(f"   ✅ User created: {test_user_id}")
                else:
                    print(f"   ❌ Failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        if not test_user_id:
            print("❌ Cannot continue without user ID")
            return
        
        # 3. Voice Processing Endpoint
        print("\n3. Voice Processing Endpoint")
        test_session_id = f"test_{uuid.uuid4().hex[:8]}"
        try:
            mock_audio = b"test_audio_data"
            audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
            
            form_data = {
                "session_id": test_session_id,
                "user_id": test_user_id,
                "audio_base64": audio_base64
            }
            
            async with session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Success: {data.get('status')}")
                elif response.status == 400:
                    data = await response.json()
                    print(f"   ✅ Expected error: {data.get('detail')}")
                else:
                    print(f"   ❌ Unexpected status: {response.status}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 4. Text Conversation
        print("\n4. Text Conversation")
        try:
            text_input = {
                "session_id": test_session_id,
                "user_id": test_user_id,
                "message": "Hello, can you tell me a short story?"
            }
            
            async with session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Response: {len(data.get('response_text', ''))} chars")
                    print(f"   ✅ Audio: {'YES' if data.get('response_audio') else 'NO'}")
                    print(f"   ✅ Type: {data.get('content_type')}")
                else:
                    print(f"   ❌ Failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 5. Voice Personalities
        print("\n5. Voice Personalities")
        try:
            async with session.get(f"{BACKEND_URL}/voice/personalities") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Available: {len(data)} personalities")
                    for name in data.keys():
                        print(f"      - {name}")
                else:
                    print(f"   ❌ Failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 6. Content Stories
        print("\n6. Content Stories")
        try:
            async with session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status == 200:
                    data = await response.json()
                    stories = data.get('stories', [])
                    print(f"   ✅ Stories available: {len(stories)}")
                    for story in stories[:3]:  # Show first 3
                        print(f"      - {story.get('title')}")
                else:
                    print(f"   ❌ Failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 50)
        print("✅ BACKEND TESTING COMPLETE")

if __name__ == "__main__":
    asyncio.run(test_backend())