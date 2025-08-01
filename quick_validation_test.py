#!/usr/bin/env python3
"""
QUICK FINAL VALIDATION - Critical Issues Check
Fast validation of the 3 critical fixes
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://0e5dcf5a-4e8d-4074-9227-19f4607bd0be.preview.emergentagent.com/api"

def test_voice_personalities():
    """Test Voice Personalities Endpoint"""
    print("🎯 Testing Voice Personalities Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/voice/personalities", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASS: Voice Personalities - HTTP 200")
            print(f"   Response: {str(data)[:200]}...")
            return True
        else:
            print(f"❌ FAIL: Voice Personalities - HTTP {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Voice Personalities - Exception: {str(e)}")
        return False

def test_story_generation():
    """Test Story Generation Length"""
    print("\n🎯 Testing Story Generation Length...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/conversations/text",
            json={
                "session_id": "quick_test",
                "user_id": "test_user",
                "message": "Tell me a complete story about a brave little mouse"
            },
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            story_text = data.get("response_text", "")
            word_count = len(story_text.split())
            
            if word_count >= 300:
                print(f"✅ PASS: Story Generation - {word_count} words (meets 300+ requirement)")
                return True
            else:
                print(f"❌ FAIL: Story Generation - Only {word_count} words (below 300)")
                print(f"   Preview: {story_text[:150]}...")
                return False
        else:
            print(f"❌ FAIL: Story Generation - HTTP {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Story Generation - Exception: {str(e)}")
        return False

def test_story_narration():
    """Test Story Narration Endpoint"""
    print("\n🎯 Testing Story Narration Endpoint...")
    try:
        # First get stories
        stories_response = requests.get(f"{BACKEND_URL}/content/stories", timeout=10)
        if stories_response.status_code != 200:
            print(f"❌ FAIL: Could not fetch stories - HTTP {stories_response.status_code}")
            return False
            
        stories_data = stories_response.json()
        stories = stories_data.get("stories", [])
        
        if not stories:
            print("❌ FAIL: No stories available")
            return False
            
        # Test narration
        story_id = stories[0]["id"]
        narration_response = requests.post(
            f"{BACKEND_URL}/content/stories/{story_id}/narrate",
            data={"user_id": "test_user"},
            timeout=20
        )
        
        if narration_response.status_code == 200:
            narration_data = narration_response.json()
            response_text = narration_data.get("response_text", "")
            response_audio = narration_data.get("response_audio", "")
            
            if response_text and response_audio:
                word_count = len(response_text.split())
                print(f"✅ PASS: Story Narration - Text: {word_count} words, Audio: {len(response_audio)} chars")
                return True
            else:
                print(f"❌ FAIL: Story Narration - Empty response_text or response_audio")
                print(f"   Text length: {len(response_text)}, Audio length: {len(response_audio)}")
                return False
        else:
            print(f"❌ FAIL: Story Narration - HTTP {narration_response.status_code}")
            print(f"   Error: {narration_response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Story Narration - Exception: {str(e)}")
        return False

def test_health_check():
    """Test Health Check"""
    print("\n🎯 Testing Health Check...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASS: Health Check - System healthy")
            return True
        else:
            print(f"❌ FAIL: Health Check - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Health Check - Exception: {str(e)}")
        return False

def main():
    print("🚀 QUICK FINAL VALIDATION - CRITICAL FIXES")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Start Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Voice Personalities", test_voice_personalities()))
    results.append(("Story Generation", test_story_generation()))
    results.append(("Story Narration", test_story_narration()))
    
    # Summary
    print("\n🎯 QUICK VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    # Critical assessment
    voice_working = results[1][1] if len(results) > 1 else False
    story_gen_working = results[2][1] if len(results) > 2 else False
    story_narration_working = results[3][1] if len(results) > 3 else False
    
    print("CRITICAL ISSUES STATUS:")
    print(f"✅ Voice Personalities Endpoint: {'FIXED' if voice_working else 'STILL BROKEN'}")
    print(f"✅ Story Generation Length (300+ words): {'FIXED' if story_gen_working else 'STILL BROKEN'}")
    print(f"✅ Story Narration UserProfile handling: {'FIXED' if story_narration_working else 'STILL BROKEN'}")
    print()
    
    critical_fixes = sum([voice_working, story_gen_working, story_narration_working])
    
    if critical_fixes == 3:
        print("🎉 ALL CRITICAL FIXES CONFIRMED WORKING!")
    elif critical_fixes >= 2:
        print("⚠️  PARTIAL SUCCESS - Most critical fixes working")
    else:
        print("❌ CRITICAL FAILURES REMAIN")
    
    print("=" * 60)

if __name__ == "__main__":
    main()