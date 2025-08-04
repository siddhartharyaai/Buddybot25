#!/usr/bin/env python3
"""
Comprehensive Age Processing Debug
"""

import requests
import json

BACKEND_URL = "https://6ddee563-7037-4e87-80ca-83a8a9a9bcae.preview.emergentagent.com/api"

def test_comprehensive_debug():
    user_id = "debug_comprehensive_age5"
    
    # Step 1: Create user profile
    user_data = {
        "name": "Emma",
        "age": 5,
        "location": "Test Location",
        "interests": ["puppies", "colors"],
        "language": "english"
    }
    
    print("=== STEP 1: Creating User Profile ===")
    response = requests.post(f"{BACKEND_URL}/users/profile", json=user_data)
    print(f"Profile creation status: {response.status_code}")
    if response.status_code == 200:
        profile_data = response.json()
        actual_user_id = profile_data.get("id")
        print(f"Created profile with ID: {actual_user_id}")
        print(f"Profile age: {profile_data.get('age')}")
        print(f"Profile name: {profile_data.get('name')}")
    else:
        print(f"Profile creation failed: {response.text}")
        return
    
    # Step 2: Retrieve the profile to verify it was stored
    print("\n=== STEP 2: Retrieving User Profile ===")
    response = requests.get(f"{BACKEND_URL}/users/profile/{actual_user_id}")
    print(f"Profile retrieval status: {response.status_code}")
    if response.status_code == 200:
        retrieved_profile = response.json()
        print(f"Retrieved profile age: {retrieved_profile.get('age')}")
        print(f"Retrieved profile name: {retrieved_profile.get('name')}")
    else:
        print(f"Profile retrieval failed: {response.text}")
    
    # Step 3: Test conversation with the actual user ID
    print("\n=== STEP 3: Testing Conversation ===")
    payload = {
        "session_id": "debug_comprehensive_session",
        "user_id": actual_user_id,
        "message": "Tell me about a magnificent animal that is extraordinary"
    }
    
    response = requests.post(f"{BACKEND_URL}/conversations/text", json=payload)
    print(f"Conversation status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        response_text = data.get("response_text", "")
        content_type = data.get("content_type", "")
        
        print(f"Content type: {content_type}")
        print(f"Response length: {len(response_text)} characters")
        print(f"Response preview: {response_text[:200]}...")
        
        # Check for forbidden words (age 5)
        age5_forbidden = ["magnificent", "extraordinary", "amazing", "wonderful", "incredible", "tremendous", "fantastic"]
        found_forbidden = [word for word in age5_forbidden if word.lower() in response_text.lower()]
        
        # Check for expected replacements (age 5)
        age5_replacements = ["big and fun", "super cool", "really fun", "really nice", "really cool", "really big", "super fun"]
        found_replacements = [word for word in age5_replacements if word.lower() in response_text.lower()]
        
        print(f"\nAge 5 Analysis:")
        print(f"Forbidden words found: {found_forbidden}")
        print(f"Expected replacements found: {found_replacements}")
        
        # Analyze sentence length
        sentences = [s.strip() for s in response_text.split('.') if s.strip()]
        long_sentences = [s for s in sentences if len(s.split()) > 8]
        
        print(f"Total sentences: {len(sentences)}")
        print(f"Sentences over 8 words: {len(long_sentences)}")
        if long_sentences:
            print(f"Long sentence example: {long_sentences[0][:100]}...")
        
        # Overall assessment
        post_processing_working = len(found_forbidden) == 0
        age_appropriate = len(found_replacements) > 0 or len(found_forbidden) == 0
        
        print(f"\nAssessment:")
        print(f"Post-processing working: {post_processing_working}")
        print(f"Age-appropriate language: {age_appropriate}")
        
    else:
        print(f"Conversation failed: {response.text}")

if __name__ == "__main__":
    test_comprehensive_debug()