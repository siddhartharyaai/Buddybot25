#!/usr/bin/env python3
"""
DETAILED INVESTIGATION OF CRITICAL FAILURES
Focus on the two critical failures identified:
1. Story Generation Length (84 words instead of 300+)
2. Story Narration Endpoint (empty response)
"""

import asyncio
import aiohttp
import json
import base64
import time
from datetime import datetime

BACKEND_URL = "https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com/api"

class DetailedInvestigation:
    def __init__(self):
        self.session = None
        self.user_id = "investigation_user"
        self.session_id = f"investigation_{int(time.time())}"
        
    async def setup(self):
        self.session = aiohttp.ClientSession()
        print("🔍 DETAILED INVESTIGATION OF CRITICAL FAILURES")
        print("=" * 60)
        
    async def cleanup(self):
        if self.session:
            await self.session.close()
            
    async def investigate_story_generation_length(self):
        """Deep dive into story generation length issue"""
        print("🔍 INVESTIGATING STORY GENERATION LENGTH ISSUE")
        print("-" * 50)
        
        story_requests = [
            "Tell me a complete story about a brave little mouse",
            "I want a long story about a magical adventure",
            "Can you tell me a detailed story about friendship",
            "Please tell me a story with lots of details about a dragon",
            "Tell me a story that's at least 300 words long"
        ]
        
        for i, request in enumerate(story_requests, 1):
            print(f"\n📖 Test {i}: '{request}'")
            
            payload = {
                "session_id": f"{self.session_id}_{i}",
                "user_id": self.user_id,
                "message": request
            }
            
            try:
                async with self.session.post(f"{BACKEND_URL}/conversations/text", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        word_count = len(response_text.split())
                        char_count = len(response_text)
                        content_type = data.get("content_type", "unknown")
                        
                        print(f"   Word Count: {word_count}")
                        print(f"   Character Count: {char_count}")
                        print(f"   Content Type: {content_type}")
                        print(f"   Meets 300+ requirement: {'✅' if word_count >= 300 else '❌'}")
                        
                        # Show first and last parts to check for truncation
                        if response_text:
                            print(f"   First 100 chars: {response_text[:100]}...")
                            if len(response_text) > 200:
                                print(f"   Last 100 chars: ...{response_text[-100:]}")
                            else:
                                print(f"   Full response: {response_text}")
                        else:
                            print("   ❌ EMPTY RESPONSE")
                            
                    else:
                        print(f"   ❌ HTTP Error: {response.status}")
                        
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                
            await asyncio.sleep(1)  # Delay between requests
            
    async def investigate_story_narration_endpoint(self):
        """Deep dive into story narration endpoint issue"""
        print("\n🔍 INVESTIGATING STORY NARRATION ENDPOINT ISSUE")
        print("-" * 50)
        
        # First, get available stories
        try:
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status == 200:
                    stories_data = await response.json()
                    stories = stories_data.get("stories", [])
                    print(f"📚 Available stories: {len(stories)}")
                    
                    for story in stories[:3]:  # Test first 3 stories
                        story_id = story["id"]
                        story_title = story.get("title", "Unknown")
                        
                        print(f"\n📖 Testing story: {story_title} (ID: {story_id})")
                        
                        # Test story narration
                        form_data = aiohttp.FormData()
                        form_data.add_field('user_id', self.user_id)
                        
                        try:
                            async with self.session.post(f"{BACKEND_URL}/content/stories/{story_id}/narrate", data=form_data) as narrate_response:
                                print(f"   HTTP Status: {narrate_response.status}")
                                
                                if narrate_response.status == 200:
                                    narrate_data = await narrate_response.json()
                                    
                                    response_text = narrate_data.get("response_text", "")
                                    response_audio = narrate_data.get("response_audio", "")
                                    status = narrate_data.get("status", "unknown")
                                    error = narrate_data.get("error", "")
                                    
                                    print(f"   Status: {status}")
                                    print(f"   Has response_text: {'✅' if response_text else '❌'}")
                                    print(f"   Has response_audio: {'✅' if response_audio else '❌'}")
                                    print(f"   Response text length: {len(response_text)} chars")
                                    print(f"   Response audio length: {len(response_audio)} chars")
                                    
                                    if error:
                                        print(f"   ❌ Error: {error}")
                                        
                                    if response_text:
                                        word_count = len(response_text.split())
                                        print(f"   Word count: {word_count}")
                                        print(f"   Preview: {response_text[:200]}...")
                                    else:
                                        print("   ❌ EMPTY RESPONSE TEXT")
                                        
                                    # Check for specific errors
                                    full_response = json.dumps(narrate_data, indent=2)
                                    if "UserProfile object has no attribute" in full_response:
                                        print("   🚨 FOUND UserProfile ERROR!")
                                        print(f"   Error details: {full_response}")
                                        
                                else:
                                    error_text = await narrate_response.text()
                                    print(f"   ❌ HTTP Error Response: {error_text[:500]}")
                                    
                        except Exception as narrate_error:
                            print(f"   ❌ Narration Exception: {str(narrate_error)}")
                            
                        await asyncio.sleep(0.5)
                        
                else:
                    print(f"❌ Could not fetch stories: HTTP {response.status}")
                    
        except Exception as e:
            print(f"❌ Stories fetch exception: {str(e)}")
            
    async def test_user_profile_creation(self):
        """Test if user profile issues are causing problems"""
        print("\n🔍 INVESTIGATING USER PROFILE ISSUES")
        print("-" * 50)
        
        # Try to get user profile
        try:
            async with self.session.get(f"{BACKEND_URL}/users/profile/{self.user_id}") as response:
                print(f"Get profile HTTP status: {response.status}")
                
                if response.status == 404:
                    print("   User profile not found, creating one...")
                    
                    # Create user profile
                    profile_data = {
                        "name": "Investigation User",
                        "age": 8,
                        "language": "english",
                        "location": "Test City",
                        "parent_email": "test@example.com",
                        "preferences": {
                            "voice_personality": "friendly_companion",
                            "learning_goals": ["general_knowledge"],
                            "favorite_topics": ["stories", "adventures"]
                        }
                    }
                    
                    async with self.session.post(f"{BACKEND_URL}/users/profile", json=profile_data) as create_response:
                        print(f"   Create profile HTTP status: {create_response.status}")
                        
                        if create_response.status == 200:
                            created_profile = await create_response.json()
                            print(f"   ✅ Profile created: {created_profile.get('id')}")
                            
                            # Now test story narration with proper profile
                            await self.test_narration_with_profile()
                        else:
                            error_text = await create_response.text()
                            print(f"   ❌ Profile creation failed: {error_text}")
                            
                elif response.status == 200:
                    profile_data = await response.json()
                    print(f"   ✅ Profile exists: {profile_data.get('name')}")
                    await self.test_narration_with_profile()
                else:
                    error_text = await response.text()
                    print(f"   ❌ Profile fetch error: {error_text}")
                    
        except Exception as e:
            print(f"❌ Profile investigation exception: {str(e)}")
            
    async def test_narration_with_profile(self):
        """Test narration after ensuring profile exists"""
        print("\n   🔄 Re-testing narration with proper profile...")
        
        try:
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status == 200:
                    stories_data = await response.json()
                    stories = stories_data.get("stories", [])
                    
                    if stories:
                        story_id = stories[0]["id"]
                        
                        form_data = aiohttp.FormData()
                        form_data.add_field('user_id', self.user_id)
                        
                        async with self.session.post(f"{BACKEND_URL}/content/stories/{story_id}/narrate", data=form_data) as narrate_response:
                            print(f"   Narration HTTP status: {narrate_response.status}")
                            
                            if narrate_response.status == 200:
                                narrate_data = await narrate_response.json()
                                response_text = narrate_data.get("response_text", "")
                                status = narrate_data.get("status", "unknown")
                                
                                print(f"   Status: {status}")
                                print(f"   Has response_text: {'✅' if response_text else '❌'}")
                                print(f"   Response length: {len(response_text)} chars")
                                
                                if response_text:
                                    print(f"   ✅ SUCCESS: Narration working with profile!")
                                else:
                                    print(f"   ❌ STILL EMPTY: {narrate_data}")
                            else:
                                error_text = await narrate_response.text()
                                print(f"   ❌ Still failing: {error_text}")
                                
        except Exception as e:
            print(f"   ❌ Re-test exception: {str(e)}")
            
    async def run_investigation(self):
        """Run full investigation"""
        await self.setup()
        
        try:
            await self.investigate_story_generation_length()
            await self.investigate_story_narration_endpoint()
            await self.test_user_profile_creation()
            
            print("\n" + "=" * 60)
            print("🎯 INVESTIGATION SUMMARY")
            print("=" * 60)
            print("Key findings will help identify root causes of:")
            print("1. Story generation producing only 84 words instead of 300+")
            print("2. Story narration endpoint returning empty responses")
            print("3. Whether UserProfile errors are still occurring")
            
        finally:
            await self.cleanup()

async def main():
    investigator = DetailedInvestigation()
    await investigator.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())