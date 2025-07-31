#!/usr/bin/env python3
"""
Focused TTS Debug Logging Test
Tests specific TTS debug logging and chunked processing
"""

import requests
import json
import time

# Get backend URL
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            base_url = line.split('=')[1].strip()
            break
    else:
        base_url = "http://localhost:8001"

api_url = f"{base_url}/api"

def test_tts_endpoints():
    """Test TTS endpoints with shorter timeouts"""
    print("🎵 FOCUSED TTS DEBUG LOGGING TEST")
    print("="*50)
    
    # Test 1: Simple TTS
    print("\n🔍 Test 1: Simple TTS")
    try:
        response = requests.post(
            f"{api_url}/voice/tts",
            json={"text": "Hello, this is a test message", "personality": "friendly_companion"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            audio_size = len(data.get("audio_base64", ""))
            print(f"✅ Simple TTS: {audio_size} chars audio")
        else:
            print(f"❌ Simple TTS: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Simple TTS: {str(e)}")
    
    # Test 2: Chunked TTS (shorter text)
    print("\n🔍 Test 2: Chunked TTS (shorter)")
    try:
        response = requests.post(
            f"{api_url}/voice/tts",
            json={"text": "This is a moderately long message for chunked processing. " * 10, "personality": "story_narrator"},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            audio_size = len(data.get("audio_base64", ""))
            print(f"✅ Chunked TTS: {audio_size} chars audio")
        else:
            print(f"❌ Chunked TTS: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Chunked TTS: {str(e)}")
    
    # Test 3: Voice personalities
    print("\n🔍 Test 3: Voice Personalities")
    try:
        response = requests.get(f"{api_url}/voice/personalities", timeout=5)
        if response.status_code == 200:
            data = response.json()
            personalities = data.get("personalities", [])
            print(f"✅ Voice Personalities: {len(personalities)} available")
            for p in personalities:
                print(f"   - {p.get('name', 'Unknown')}: {p.get('description', 'No description')}")
        else:
            print(f"❌ Voice Personalities: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Voice Personalities: {str(e)}")
    
    # Test 4: Conversation with TTS
    print("\n🔍 Test 4: Conversation with TTS")
    try:
        response = requests.post(
            f"{api_url}/conversations/text",
            json={
                "session_id": "test_session_focused",
                "user_id": "test_user_focused",
                "message": "Tell me a short joke"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response_text", "")
            response_audio = data.get("response_audio", "")
            content_type = data.get("content_type", "unknown")
            print(f"✅ Conversation TTS: {len(response_text)} chars text, {len(response_audio)} chars audio")
            print(f"   Content Type: {content_type}")
        else:
            print(f"❌ Conversation TTS: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Conversation TTS: {str(e)}")
    
    # Test 5: Story narration
    print("\n🔍 Test 5: Story Narration")
    try:
        response = requests.post(
            f"{api_url}/content/stories/story_001/narrate",
            data={"user_id": "test_user_story"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response_text", "")
            response_audio = data.get("response_audio", "")
            source = data.get("source", "unknown")
            print(f"✅ Story Narration: {len(response_text)} chars text, {len(response_audio)} chars audio")
            print(f"   Source: {source}")
        else:
            print(f"❌ Story Narration: HTTP {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Story Narration: {str(e)}")

if __name__ == "__main__":
    test_tts_endpoints()