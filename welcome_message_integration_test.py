#!/usr/bin/env python3
"""
Welcome Message Integration Test - End-to-End Testing
"""

import asyncio
import aiohttp
import json
import base64
import time
import os

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_welcome_message_flow():
    """Test complete welcome message flow with TTS"""
    
    async with aiohttp.ClientSession() as session:
        print("🎯 TESTING WELCOME MESSAGE INTEGRATION FLOW")
        print("=" * 50)
        
        # Step 1: Generate welcome message
        print("1️⃣ Testing welcome message generation...")
        
        welcome_data = {
            "user_id": "test_user_welcome_flow",
            "session_id": "test_session_welcome_flow"
        }
        
        try:
            async with session.post(f"{API_BASE}/conversations/welcome", json=welcome_data) as response:
                if response.status == 200:
                    welcome_result = await response.json()
                    welcome_message = welcome_result.get("message", "")
                    content_type = welcome_result.get("content_type", "")
                    
                    print(f"✅ Welcome message generated: '{welcome_message[:100]}...'")
                    print(f"✅ Content type: {content_type}")
                    
                    if not welcome_message:
                        print("❌ No welcome message generated")
                        return
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Welcome message generation failed: {response.status} - {error_text}")
                    return
                    
        except Exception as e:
            print(f"❌ Welcome message generation error: {str(e)}")
            return
            
        # Step 2: Test TTS with different personalities for the welcome message
        print("\n2️⃣ Testing TTS with different personalities...")
        
        personalities = ["friendly_companion", "story_narrator", "learning_buddy"]
        
        for personality in personalities:
            print(f"\n   Testing {personality}...")
            
            tts_data = {
                "text": welcome_message,
                "personality": personality
            }
            
            try:
                start_time = time.time()
                async with session.post(f"{API_BASE}/voice/tts", json=tts_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        tts_result = await response.json()
                        
                        if tts_result.get("status") == "success" and tts_result.get("audio_base64"):
                            audio_data = tts_result.get("audio_base64", "")
                            decoded_size = len(base64.b64decode(audio_data)) if audio_data else 0
                            
                            print(f"   ✅ {personality}: Generated {decoded_size} bytes in {response_time:.2f}s")
                            
                            # Test audio format
                            try:
                                decoded_audio = base64.b64decode(audio_data)
                                if decoded_audio.startswith(b'RIFF'):
                                    print(f"   ✅ Audio format: WAV (HTML5 compatible)")
                                else:
                                    print(f"   ⚠️  Audio format: Unknown")
                            except:
                                print(f"   ❌ Invalid base64 audio data")
                                
                        else:
                            print(f"   ❌ {personality}: TTS failed - {tts_result}")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ {personality}: HTTP {response.status} - {error_text}")
                        
            except Exception as e:
                print(f"   ❌ {personality}: Exception - {str(e)}")
                
        # Step 3: Test performance with typical welcome messages
        print("\n3️⃣ Testing performance with various welcome message lengths...")
        
        test_messages = [
            "Hi there! 👋",
            "Hello! I'm Buddy, your AI friend.",
            "Hi Emma! 👋 I'm Buddy, your AI friend. How can I help you today?",
            "Hello and welcome! I'm Buddy, your friendly AI companion. I'm here to help you learn, play, and explore new things together. What would you like to do today? 🌟"
        ]
        
        for i, message in enumerate(test_messages):
            print(f"\n   Testing message {i+1} ({len(message)} chars)...")
            
            tts_data = {
                "text": message,
                "personality": "friendly_companion"
            }
            
            try:
                start_time = time.time()
                async with session.post(f"{API_BASE}/voice/tts", json=tts_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        tts_result = await response.json()
                        
                        if tts_result.get("status") == "success" and tts_result.get("audio_base64"):
                            audio_data = tts_result.get("audio_base64", "")
                            decoded_size = len(base64.b64decode(audio_data)) if audio_data else 0
                            
                            # Performance criteria for welcome messages
                            if response_time < 3.0:
                                status = "✅ EXCELLENT"
                            elif response_time < 5.0:
                                status = "✅ GOOD"
                            else:
                                status = "⚠️  SLOW"
                                
                            print(f"   {status}: {decoded_size} bytes in {response_time:.2f}s")
                            
                        else:
                            print(f"   ❌ TTS failed: {tts_result}")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ HTTP {response.status}: {error_text}")
                        
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                
        print("\n" + "=" * 50)
        print("🎉 WELCOME MESSAGE INTEGRATION TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(test_welcome_message_flow())