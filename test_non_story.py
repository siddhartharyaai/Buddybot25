#!/usr/bin/env python3
"""
Test Non-Story Content Post-Processing
"""

import requests
import json

BACKEND_URL = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com/api"

def test_non_story_content():
    # Use existing user profile
    user_id = "dd18fbca-beb7-4d02-bfe4-e40d6ef38cd4"  # Emma, age 5
    
    test_cases = [
        {
            "message": "What is a magnificent and extraordinary animal?",
            "expected_type": "conversation"
        },
        {
            "message": "Can you tell me a joke about a magnificent animal?",
            "expected_type": "joke"
        },
        {
            "message": "Sing me a song about something magnificent",
            "expected_type": "song"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== TEST {i}: {test_case['expected_type'].upper()} ===")
        
        payload = {
            "session_id": f"non_story_test_{i}",
            "user_id": user_id,
            "message": test_case["message"]
        }
        
        response = requests.post(f"{BACKEND_URL}/conversations/text", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response_text", "")
            content_type = data.get("content_type", "")
            
            print(f"Content type: {content_type}")
            print(f"Response: {response_text[:150]}...")
            
            # Check for forbidden words (age 5)
            forbidden_words = ["magnificent", "extraordinary"]
            found_forbidden = [word for word in forbidden_words if word.lower() in response_text.lower()]
            
            # Check for expected replacements (age 5)
            expected_replacements = ["big and fun", "super cool"]
            found_replacements = [word for word in expected_replacements if word.lower() in response_text.lower()]
            
            print(f"Forbidden words found: {found_forbidden}")
            print(f"Expected replacements found: {found_replacements}")
            
            # Check sentence length for non-story content
            sentences = [s.strip() for s in response_text.split('.') if s.strip()]
            long_sentences = [s for s in sentences if len(s.split()) > 8]
            
            print(f"Sentences over 8 words: {len(long_sentences)}/{len(sentences)}")
            
            # Assessment
            word_processing_ok = len(found_forbidden) == 0
            sentence_processing_ok = len(long_sentences) == 0
            
            print(f"Word processing OK: {word_processing_ok}")
            print(f"Sentence processing OK: {sentence_processing_ok}")
            print(f"Overall: {'✅ PASS' if word_processing_ok and sentence_processing_ok else '❌ FAIL'}")
        else:
            print(f"Failed: {response.text}")

if __name__ == "__main__":
    test_non_story_content()