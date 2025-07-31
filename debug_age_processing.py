#!/usr/bin/env python3
"""
Debug Age-Appropriate Language Processing
"""

import requests
import json

BACKEND_URL = "https://9c87ad27-55c0-4609-a47c-ef5b9de00cdd.preview.emergentagent.com/api"

def test_debug():
    # Create a simple age 5 user
    user_data = {
        "id": "debug_user_age5",
        "name": "Emma",
        "age": 5,
        "location": "Test Location",
        "interests": ["puppies", "colors"],
        "language": "english"
    }
    
    # Create user
    response = requests.post(f"{BACKEND_URL}/users/profile", json=user_data)
    print(f"User creation: {response.status_code}")
    
    # Test conversation
    payload = {
        "session_id": "debug_session",
        "user_id": "debug_user_age5",
        "message": "Tell me about a magnificent animal that is extraordinary"
    }
    
    response = requests.post(f"{BACKEND_URL}/conversations/text", json=payload)
    print(f"Conversation: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        response_text = data.get("response_text", "")
        content_type = data.get("content_type", "")
        
        print(f"Content type: {content_type}")
        print(f"Response: {response_text[:200]}...")
        
        # Check for forbidden words
        forbidden_words = ["magnificent", "extraordinary", "amazing", "wonderful", "incredible"]
        found_words = [word for word in forbidden_words if word.lower() in response_text.lower()]
        
        print(f"Forbidden words found: {found_words}")
        
        # Check for expected replacements
        expected_words = ["big and fun", "super cool", "really fun", "really nice", "really cool"]
        found_replacements = [word for word in expected_words if word.lower() in response_text.lower()]
        
        print(f"Expected replacements found: {found_replacements}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_debug()