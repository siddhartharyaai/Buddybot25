#!/usr/bin/env python3
"""
Focused Voice Processing Test
Testing the specific voice processing endpoint issues
"""

import asyncio
import aiohttp
import json
import base64
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend URL
BACKEND_URL = "https://e73353f9-1d22-4a0f-9deb-0707101e1e70.preview.emergentagent.com/api"

async def test_voice_processing():
    """Test voice processing endpoint"""
    
    async with aiohttp.ClientSession() as session:
        # 1. Test Health Check
        print("🔍 Testing Health Check...")
        try:
            async with session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Health Check: {health_data.get('status')}")
                    print(f"   Orchestrator: {health_data.get('agents', {}).get('orchestrator')}")
                    print(f"   Deepgram: {health_data.get('agents', {}).get('deepgram_configured')}")
                    print(f"   Gemini: {health_data.get('agents', {}).get('gemini_configured')}")
                else:
                    print(f"❌ Health Check Failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ Health Check Error: {e}")
            return
        
        # 2. Create Test User
        print("\n🔍 Creating Test User...")
        test_user_id = None
        try:
            profile_data = {
                "name": "Voice Test User",
                "age": 8,
                "location": "Test City",
                "timezone": "America/New_York",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "music"],
                "learning_goals": ["listening"],
                "parent_email": "test@voice.com"
            }
            
            async with session.post(f"{BACKEND_URL}/users/profile", json=profile_data) as response:
                if response.status == 200:
                    user_data = await response.json()
                    test_user_id = user_data["id"]
                    print(f"✅ Test User Created: {test_user_id}")
                else:
                    print(f"❌ User Creation Failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ User Creation Error: {e}")
            return
        
        # 3. Test Voice Processing Endpoint
        print("\n🔍 Testing Voice Processing Endpoint...")
        test_session_id = f"voice_test_{uuid.uuid4().hex[:8]}"
        
        try:
            # Create mock audio data
            mock_audio = b"test_audio_data_for_voice_processing"
            audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
            
            form_data = {
                "session_id": test_session_id,
                "user_id": test_user_id,
                "audio_base64": audio_base64
            }
            
            print(f"   Session ID: {test_session_id}")
            print(f"   User ID: {test_user_id}")
            print(f"   Audio Size: {len(mock_audio)} bytes")
            print(f"   Base64 Size: {len(audio_base64)} chars")
            
            async with session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
                print(f"   Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ Voice Processing Successful!")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Transcript: {data.get('transcript', 'None')}")
                    print(f"   Response Text: {len(data.get('response_text', ''))} chars")
                    print(f"   Response Audio: {len(data.get('response_audio', ''))} chars")
                    print(f"   Content Type: {data.get('content_type')}")
                    
                elif response.status == 400:
                    error_data = await response.json()
                    print("⚠️ Voice Processing - Expected Error (400):")
                    print(f"   Status: {error_data.get('status')}")
                    print(f"   Detail: {error_data.get('detail')}")
                    print("   Note: This is expected with mock audio data")
                    
                elif response.status == 500:
                    try:
                        error_data = await response.json()
                        error_detail = error_data.get('detail', '')
                        print("❌ Voice Processing - Server Error (500):")
                        print(f"   Detail: {error_detail}")
                        
                        # Check for specific errors
                        if "process_conversation" in error_detail:
                            print("🚨 CRITICAL: Old 'process_conversation' method error still exists!")
                            print("   Fix needed: Update to use 'process_voice_input' method")
                        elif "process_voice_input" in error_detail and "not found" in error_detail:
                            print("🚨 CRITICAL: 'process_voice_input' method not found!")
                            print("   Fix needed: Implement process_voice_input method in orchestrator")
                        else:
                            print("ℹ️ Different server error - method integration may be working")
                    except:
                        error_text = await response.text()
                        print(f"❌ Voice Processing - Server Error: {error_text}")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Voice Processing Failed: {response.status}")
                    print(f"   Error: {error_text}")
                    
        except Exception as e:
            print(f"❌ Voice Processing Exception: {e}")
        
        # 4. Test Voice Personalities
        print("\n🔍 Testing Voice Personalities...")
        try:
            async with session.get(f"{BACKEND_URL}/voice/personalities") as response:
                if response.status == 200:
                    personalities = await response.json()
                    print(f"✅ Voice Personalities: {len(personalities)} available")
                    for name, details in personalities.items():
                        print(f"   - {name}: {details.get('description', 'No description')}")
                else:
                    print(f"❌ Voice Personalities Failed: {response.status}")
        except Exception as e:
            print(f"❌ Voice Personalities Error: {e}")
        
        # 5. Test Text Conversation (for TTS verification)
        print("\n🔍 Testing Text Conversation (TTS verification)...")
        try:
            text_input = {
                "session_id": test_session_id,
                "user_id": test_user_id,
                "message": "Hello, can you say something back to me?"
            }
            
            async with session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Text Conversation Successful!")
                    print(f"   Response Text: {len(data.get('response_text', ''))} chars")
                    print(f"   Response Audio: {len(data.get('response_audio', ''))} chars")
                    print(f"   Content Type: {data.get('content_type')}")
                    
                    if data.get('response_audio'):
                        print("✅ TTS Integration Working - Audio response generated")
                    else:
                        print("⚠️ TTS Integration - No audio response")
                else:
                    error_text = await response.text()
                    print(f"❌ Text Conversation Failed: {response.status}")
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ Text Conversation Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_voice_processing())