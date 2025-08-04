#!/usr/bin/env python3
"""
ADDITIONAL VALIDATION TESTS
"""

import requests
import json
import time

BACKEND_URL = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com/api"

def test_multiple_story_requests():
    """Test multiple story requests to check consistency"""
    print("🔄 TESTING MULTIPLE STORY REQUESTS")
    
    prompts = [
        "Tell me a complete story about a magical garden",
        "I want a story about two friends who go on an adventure", 
        "Can you tell me a story with a beginning, middle, and end?"
    ]
    
    word_counts = []
    
    for i, prompt in enumerate(prompts, 1):
        try:
            payload = {
                "session_id": f"multi_test_{i}_{int(time.time())}",
                "user_id": "test_user_multi",
                "message": prompt
            }
            
            response = requests.post(f"{BACKEND_URL}/conversations/text", json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                story_text = data.get("response_text", "")
                word_count = len(story_text.split())
                word_counts.append(word_count)
                print(f"   Test {i}: {word_count} words")
            else:
                print(f"   Test {i}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   Test {i}: Exception - {str(e)}")
    
    if word_counts:
        avg_words = sum(word_counts) / len(word_counts)
        meets_requirement = all(wc >= 300 for wc in word_counts)
        print(f"✅ Average word count: {avg_words:.1f}")
        print(f"   All meet 300+ requirement: {'YES' if meets_requirement else 'NO'}")
        return meets_requirement
    else:
        print("❌ No successful tests")
        return False

def test_user_profile_creation():
    """Test user profile creation and retrieval"""
    print("\n👤 TESTING USER PROFILE HANDLING")
    
    try:
        # Create profile
        profile_data = {
            "name": "Test Child",
            "age": 8,
            "language": "english",
            "preferences": {
                "voice_personality": "friendly_companion",
                "learning_goals": ["storytelling"],
                "favorite_topics": ["adventure"]
            }
        }
        
        response = requests.post(f"{BACKEND_URL}/users/profile", json=profile_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            user_id = data.get("id")
            
            if user_id:
                print(f"✅ Profile created with ID: {user_id}")
                
                # Test retrieval
                get_response = requests.get(f"{BACKEND_URL}/users/profile/{user_id}", timeout=30)
                
                if get_response.status_code == 200:
                    print("✅ Profile retrieved successfully")
                    return True
                else:
                    print(f"❌ Profile retrieval failed: HTTP {get_response.status_code}")
                    return False
            else:
                print("❌ No user ID returned")
                return False
        else:
            print(f"❌ Profile creation failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_iterative_story_system():
    """Test if iterative story generation is working"""
    print("\n🔄 TESTING ITERATIVE STORY GENERATION")
    
    try:
        payload = {
            "session_id": f"iterative_{int(time.time())}",
            "user_id": "test_iterative",
            "message": "Please tell me a complete, detailed story with at least 300 words about a young explorer who discovers a hidden magical kingdom. Include a beginning, middle with challenges, and a satisfying ending."
        }
        
        response = requests.post(f"{BACKEND_URL}/conversations/text", json=payload, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            story_text = data.get("response_text", "")
            word_count = len(story_text.split())
            
            # Check story structure
            has_beginning = any(word in story_text.lower() for word in ["once", "long ago", "there was", "in a"])
            has_middle = len(story_text.split('.')) >= 5
            has_ending = any(word in story_text.lower() for word in ["end", "finally", "happily", "conclusion"])
            
            structure_score = sum([has_beginning, has_middle, has_ending])
            
            print(f"✅ Story generated: {word_count} words")
            print(f"   Structure score: {structure_score}/3")
            print(f"   Meets requirements: {'YES' if word_count >= 300 and structure_score >= 2 else 'NO'}")
            
            return word_count >= 300 and structure_score >= 2
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    print("🔍 ADDITIONAL VALIDATION TESTS")
    print("=" * 50)
    
    results = []
    results.append(("Multiple Story Requests", test_multiple_story_requests()))
    results.append(("User Profile Handling", test_user_profile_creation()))
    results.append(("Iterative Story Generation", test_iterative_story_system()))
    
    print("\n" + "=" * 50)
    print("🔍 ADDITIONAL VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 ADDITIONAL TESTS PASSED: {passed}/3")

if __name__ == "__main__":
    main()