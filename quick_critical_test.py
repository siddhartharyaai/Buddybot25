#!/usr/bin/env python3
"""
QUICK CRITICAL TESTING - Focus on the 3 main issues
"""

import requests
import json
import time

BACKEND_URL = "https://0e5dcf5a-4e8d-4074-9227-19f4607bd0be.preview.emergentagent.com/api"

def test_story_generation():
    """Test story generation length"""
    print("🎯 TESTING STORY GENERATION LENGTH")
    
    payload = {
        "session_id": f"test_{int(time.time())}",
        "user_id": "test_user",
        "message": "Tell me a story about a brave little mouse"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/conversations/text", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            story_text = data.get("response_text", "")
            word_count = len(story_text.split())
            print(f"✅ Story generated: {word_count} words")
            print(f"   Meets 300+ requirement: {'YES' if word_count >= 300 else 'NO'}")
            print(f"   Preview: {story_text[:200]}...")
            return word_count >= 300
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_story_narration():
    """Test story narration endpoint"""
    print("\n🎯 TESTING STORY NARRATION ENDPOINT")
    
    try:
        # Get stories first
        stories_response = requests.get(f"{BACKEND_URL}/content/stories", timeout=30)
        if stories_response.status_code != 200:
            print(f"❌ Cannot get stories: HTTP {stories_response.status_code}")
            return False
            
        stories = stories_response.json().get("stories", [])
        if not stories:
            print("❌ No stories available")
            return False
            
        print(f"✅ Found {len(stories)} stories")
        
        # Test narration for first story
        story = stories[0]
        story_id = story.get("id")
        
        narration_data = {"user_id": "test_user"}
        response = requests.post(f"{BACKEND_URL}/content/stories/{story_id}/narrate", 
                               data=narration_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response_text", "")
            response_audio = data.get("response_audio", "")
            
            if response_text and response_audio:
                print(f"✅ Narration successful: {len(response_text.split())} words, audio: {len(response_audio)} chars")
                return True
            else:
                print(f"❌ Empty response - text: '{response_text}', audio: '{response_audio}'")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_voice_personalities():
    """Test voice personalities endpoint"""
    print("\n🎯 TESTING VOICE PERSONALITIES ENDPOINT")
    
    try:
        response = requests.get(f"{BACKEND_URL}/voice/personalities", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"✅ Retrieved voice personalities: {json.dumps(data, indent=2)}")
                return True
            else:
                print("❌ Empty personality data")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    print("🚨 QUICK CRITICAL TESTING")
    print("=" * 50)
    
    # Test health first
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if health.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {health.status_code}")
            return
    except:
        print("❌ Cannot reach backend")
        return
    
    # Run critical tests
    results = []
    results.append(("Story Generation Length", test_story_generation()))
    results.append(("Story Narration Endpoint", test_story_narration()))
    results.append(("Voice Personalities Endpoint", test_voice_personalities()))
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 CRITICAL ISSUES SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    
    for test_name, result in results:
        status = "✅ RESOLVED" if result else "❌ FAILING"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 CRITICAL ISSUES RESOLVED: {passed}/3")
    
    if passed == 0:
        print("🚨 ALL CRITICAL ISSUES ARE FAILING")
    elif passed < 3:
        print("⚠️ SOME CRITICAL ISSUES REMAIN")
    else:
        print("🎉 ALL CRITICAL ISSUES RESOLVED")

if __name__ == "__main__":
    main()