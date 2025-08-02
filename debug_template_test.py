#!/usr/bin/env python3
"""
Debug Template System - Test the template detection directly
"""

import re

# Test the template detection logic
intent_patterns = {
    "story_animal": [r"story.*about.*(cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer)", r"tell.*me.*about.*(animal|pet)", r"(cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer).*story"],
    "story_adventure": [r"adventure.*story", r"story.*adventure", r"quest.*story", r"journey.*story", r"explore.*story"],
    "fact_animal": [r"fact.*about.*(cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer)", r"tell.*me.*about.*(cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer)", r"how.*do.*(cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer)"],
    "fact_space": [r"fact.*about.*(space|planet|star|moon|sun|mars|jupiter|saturn)", r"tell.*me.*about.*(space|planet|star|moon|sun|mars|jupiter|saturn)", r"(space|planet|star|moon|sun|mars|jupiter|saturn).*fact"],
    "joke_animal": [r"joke.*about.*(cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer)", r"funny.*joke", r"make.*me.*laugh", r"tell.*joke"],
    "joke_school": [r"joke.*about.*school", r"school.*joke", r"funny.*about.*learning"]
}

def detect_template_intent(user_input: str):
    """Test template intent detection"""
    user_input_lower = user_input.lower()
    
    for intent_name, patterns in intent_patterns.items():
        for pattern in patterns:
            if re.search(pattern, user_input_lower):
                # Parse intent: "story_animal" -> ("story", "animal")
                parts = intent_name.split('_', 1)
                if len(parts) == 2:
                    return parts[0], parts[1]
    
    return None, None

# Test various inputs
test_inputs = [
    "tell me a story about a cat",
    "story about a brave mouse",
    "tell me a fact about elephants", 
    "joke about animals",
    "tell me about space",
    "fact about planets",
    "hello",
    "how are you",
    "tell me a joke",
    "make me laugh"
]

print("🔍 TESTING TEMPLATE INTENT DETECTION:")
for test_input in test_inputs:
    content_type, category = detect_template_intent(test_input)
    status = "✅ MATCH" if content_type else "❌ NO MATCH"
    print(f"{status} '{test_input}' -> ({content_type}, {category})")

# Test specific regex patterns
print("\n🔍 TESTING SPECIFIC PATTERNS:")
test_pattern = r"story.*about.*(cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer)"
test_text = "tell me a story about a cat"
match = re.search(test_pattern, test_text.lower())
print(f"Pattern: {test_pattern}")
print(f"Text: {test_text}")
print(f"Match: {match is not None}")
if match:
    print(f"Matched: {match.group()}")