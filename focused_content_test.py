#!/usr/bin/env python3
"""
FOCUSED CONTENT GENERATION TESTING
Testing specific issues found in the comprehensive test
"""

import asyncio
import aiohttp
import json

# Get backend URL from frontend environment
BACKEND_URL = "https://6ddee563-7037-4e87-80ca-83a8a9a9bcae.preview.emergentagent.com/api"

async def test_story_word_count_detailed():
    """Test story word count in detail"""
    async with aiohttp.ClientSession() as session:
        # Create test user
        profile_data = {
            "name": "Story Tester",
            "age": 7,
            "location": "Test City",
            "timezone": "America/New_York",
            "language": "english",
            "voice_personality": "friendly_companion",
            "interests": ["stories", "animals"],
            "learning_goals": ["reading"],
            "parent_email": "test@example.com"
        }
        
        async with session.post(f"{BACKEND_URL}/users/profile", json=profile_data) as response:
            if response.status == 200:
                user_data = await response.json()
                user_id = user_data["id"]
                print(f"✅ Created test user: {user_id}")
            else:
                print(f"❌ Failed to create user: {response.status}")
                return
        
        # Create session
        session_data = {"user_id": user_id, "session_name": "Test Session"}
        async with session.post(f"{BACKEND_URL}/conversations/session", json=session_data) as response:
            if response.status == 200:
                session_data = await response.json()
                session_id = session_data["id"]
                print(f"✅ Created session: {session_id}")
            else:
                print(f"❌ Failed to create session: {response.status}")
                return
        
        # Test different story requests
        story_requests = [
            "Tell me a story about a brave little dog",
            "Please tell me a complete story about a magical forest adventure",
            "Can you tell me a long story about a young explorer discovering treasure?",
            "I want to hear a detailed story about a friendly dragon who helps children"
        ]
        
        print("\n🎯 TESTING STORY WORD COUNTS:")
        print("="*60)
        
        for i, request in enumerate(story_requests, 1):
            text_input = {
                "session_id": session_id,
                "user_id": user_id,
                "message": request
            }
            
            async with session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    word_count = len(response_text.split())
                    content_type = data.get("content_type", "unknown")
                    
                    print(f"\n📖 Story Request {i}:")
                    print(f"   Request: {request[:50]}...")
                    print(f"   Content Type: {content_type}")
                    print(f"   Word Count: {word_count}")
                    print(f"   Character Count: {len(response_text)}")
                    print(f"   Meets 200+ words: {'✅ YES' if word_count >= 200 else '❌ NO'}")
                    print(f"   Story Preview: {response_text[:200]}...")
                    
                    if word_count < 200:
                        print(f"   ⚠️  ISSUE: Story only {word_count} words (should be 200+)")
                else:
                    print(f"❌ Request {i} failed: HTTP {response.status}")
            
            await asyncio.sleep(1)  # Rate limiting

async def test_chat_vs_story_length():
    """Test chat vs story length comparison"""
    async with aiohttp.ClientSession() as session:
        # Use existing user setup (simplified)
        user_id = "test_user_comparison"
        session_id = "test_session_comparison"
        
        print("\n🔍 TESTING CHAT VS STORY LENGTH COMPARISON:")
        print("="*60)
        
        # Test regular chat
        chat_input = {
            "session_id": session_id,
            "user_id": user_id,
            "message": "Hi, how are you today?"
        }
        
        async with session.post(f"{BACKEND_URL}/conversations/text", json=chat_input) as response:
            if response.status == 200:
                chat_data = await response.json()
                chat_text = chat_data.get("response_text", "")
                chat_word_count = len(chat_text.split())
                chat_content_type = chat_data.get("content_type", "unknown")
                
                print(f"\n💬 Regular Chat Response:")
                print(f"   Content Type: {chat_content_type}")
                print(f"   Word Count: {chat_word_count}")
                print(f"   Response: {chat_text}")
            else:
                print(f"❌ Chat request failed: HTTP {response.status}")
                return
        
        await asyncio.sleep(1)
        
        # Test story request
        story_input = {
            "session_id": session_id,
            "user_id": user_id,
            "message": "Tell me a story about a magical unicorn"
        }
        
        async with session.post(f"{BACKEND_URL}/conversations/text", json=story_input) as response:
            if response.status == 200:
                story_data = await response.json()
                story_text = story_data.get("response_text", "")
                story_word_count = len(story_text.split())
                story_content_type = story_data.get("content_type", "unknown")
                
                print(f"\n📚 Story Response:")
                print(f"   Content Type: {story_content_type}")
                print(f"   Word Count: {story_word_count}")
                print(f"   Response Preview: {story_text[:300]}...")
                
                # Compare lengths
                if chat_word_count > 0:
                    length_ratio = story_word_count / chat_word_count
                    print(f"\n📊 COMPARISON RESULTS:")
                    print(f"   Chat Words: {chat_word_count}")
                    print(f"   Story Words: {story_word_count}")
                    print(f"   Length Ratio: {length_ratio:.1f}x")
                    print(f"   Dynamic Length Working: {'✅ YES' if length_ratio >= 3 else '❌ NO'}")
                    
                    if length_ratio < 3:
                        print(f"   ⚠️  ISSUE: Story should be at least 3x longer than chat")
            else:
                print(f"❌ Story request failed: HTTP {response.status}")

async def test_token_limits():
    """Test token limits specifically"""
    async with aiohttp.ClientSession() as session:
        user_id = "test_user_tokens"
        session_id = "test_session_tokens"
        
        print("\n🎯 TESTING TOKEN LIMITS:")
        print("="*60)
        
        # Test very detailed story request
        detailed_request = {
            "session_id": session_id,
            "user_id": user_id,
            "message": "Tell me a very detailed and complete story about a young wizard's first day at magic school, including all the characters they meet, the classes they attend, the spells they learn, the friends they make, the challenges they face, the magical creatures they encounter, the teachers who help them, the dormitory where they sleep, the great hall where they eat, and the adventures they have throughout the entire day from morning until night"
        }
        
        async with session.post(f"{BACKEND_URL}/conversations/text", json=detailed_request) as response:
            if response.status == 200:
                data = await response.json()
                response_text = data.get("response_text", "")
                word_count = len(response_text.split())
                estimated_tokens = int(word_count / 0.75)  # Rough token estimation
                
                print(f"\n📝 DETAILED STORY REQUEST RESULTS:")
                print(f"   Word Count: {word_count}")
                print(f"   Estimated Tokens: {estimated_tokens}")
                print(f"   Exceeds 200 tokens: {'✅ YES' if estimated_tokens > 200 else '❌ NO'}")
                print(f"   Reaches 1500+ tokens: {'✅ YES' if estimated_tokens >= 1500 else '❌ NO'}")
                print(f"   No truncation: {'✅ YES' if not response_text.endswith('...') else '❌ NO'}")
                print(f"   Content Type: {data.get('content_type', 'unknown')}")
                print(f"   Response Preview: {response_text[:400]}...")
                
                if estimated_tokens <= 200:
                    print(f"   ⚠️  ISSUE: Response appears to be limited to ~200 tokens")
                if response_text.endswith('...'):
                    print(f"   ⚠️  ISSUE: Response appears to be artificially truncated")
            else:
                print(f"❌ Detailed request failed: HTTP {response.status}")

async def main():
    """Run focused content tests"""
    print("🎯 FOCUSED CONTENT GENERATION TESTING")
    print("="*60)
    
    await test_story_word_count_detailed()
    await test_chat_vs_story_length()
    await test_token_limits()
    
    print("\n" + "="*60)
    print("🎉 FOCUSED TESTING COMPLETE")

if __name__ == "__main__":
    asyncio.run(main())