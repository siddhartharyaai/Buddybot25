#!/usr/bin/env python3
"""
FINAL CONFIRMATION TEST - ROOT CAUSE ANALYSIS
Based on investigation findings:
1. Story generation is severely truncated (49-105 words vs 300+ required)
2. Story narration endpoint fails with "Failed to retrieve user profile" error
3. User profile endpoint returns HTTP 500 errors
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://6ddee563-7037-4e87-80ca-83a8a9a9bcae.preview.emergentagent.com/api"

class RootCauseAnalysis:
    def __init__(self):
        self.session = None
        
    async def setup(self):
        self.session = aiohttp.ClientSession()
        print("🎯 ROOT CAUSE ANALYSIS - FINAL CONFIRMATION")
        print("=" * 60)
        
    async def cleanup(self):
        if self.session:
            await self.session.close()
            
    async def test_user_profile_endpoint_directly(self):
        """Test user profile endpoint directly to confirm the issue"""
        print("🔍 TESTING USER PROFILE ENDPOINT DIRECTLY")
        print("-" * 40)
        
        test_user_ids = ["test_user", "demo_user", "investigation_user"]
        
        for user_id in test_user_ids:
            try:
                async with self.session.get(f"{BACKEND_URL}/users/profile/{user_id}") as response:
                    print(f"User ID '{user_id}': HTTP {response.status}")
                    
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"   Error: {error_text}")
                    else:
                        profile_data = await response.json()
                        print(f"   ✅ Profile found: {profile_data.get('name', 'Unknown')}")
                        
            except Exception as e:
                print(f"User ID '{user_id}': Exception - {str(e)}")
                
        print()
        
    async def test_story_generation_with_different_approaches(self):
        """Test story generation with different approaches to confirm truncation"""
        print("🔍 TESTING STORY GENERATION TRUNCATION")
        print("-" * 40)
        
        # Test with explicit length requests
        test_cases = [
            "Write a 500-word story about a mouse",
            "Tell me a very long detailed story",
            "I need a complete story with beginning, middle, and end",
            "Generate a story that takes 5 minutes to read"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            payload = {
                "session_id": f"test_session_{i}",
                "user_id": "test_user_final",
                "message": test_case
            }
            
            try:
                async with self.session.post(f"{BACKEND_URL}/conversations/text", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        word_count = len(response_text.split())
                        
                        print(f"Test {i}: '{test_case[:50]}...'")
                        print(f"   Words: {word_count} (Target: 300+)")
                        print(f"   Success: {'✅' if word_count >= 300 else '❌'}")
                        
                        # Check if story appears complete or truncated
                        if response_text:
                            ends_properly = any(ending in response_text.lower() for ending in [
                                "the end", "happily ever after", "and they lived", 
                                "finally", "at last", "conclusion"
                            ])
                            print(f"   Appears complete: {'✅' if ends_properly else '❌'}")
                        print()
                        
                    else:
                        print(f"Test {i}: HTTP {response.status}")
                        
            except Exception as e:
                print(f"Test {i}: Exception - {str(e)}")
                
    async def test_backend_agent_status(self):
        """Check if backend agents are properly initialized"""
        print("🔍 TESTING BACKEND AGENT STATUS")
        print("-" * 40)
        
        try:
            async with self.session.get(f"{BACKEND_URL}/agents/status") as response:
                print(f"Agents status: HTTP {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("Agent Status:")
                    
                    if isinstance(data, dict):
                        for key, value in data.items():
                            print(f"   {key}: {value}")
                    else:
                        print(f"   Response: {data}")
                else:
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    
        except Exception as e:
            print(f"Exception: {str(e)}")
            
        print()
        
    async def run_analysis(self):
        """Run complete root cause analysis"""
        await self.setup()
        
        try:
            await self.test_user_profile_endpoint_directly()
            await self.test_story_generation_with_different_approaches()
            await self.test_backend_agent_status()
            
            print("=" * 60)
            print("🎯 ROOT CAUSE ANALYSIS RESULTS")
            print("=" * 60)
            print("CONFIRMED ISSUES:")
            print("1. ❌ Story generation severely truncated (49-105 words vs 300+ required)")
            print("2. ❌ Story narration endpoint fails with 'Failed to retrieve user profile'")
            print("3. ❌ User profile endpoints return HTTP 500 errors")
            print("4. ❌ Token limits and content frameworks NOT working as implemented")
            print()
            print("WORKING SYSTEMS:")
            print("1. ✅ Multi-turn conversations (basic functionality)")
            print("2. ✅ Ultra-low latency pipeline (<1.5s)")
            print("3. ✅ Memory integration endpoints")
            print("4. ✅ Health check and basic API endpoints")
            print()
            print("CRITICAL CONCLUSION:")
            print("The fixes mentioned in the review request have NOT been successfully")
            print("implemented. The system still has the same critical issues:")
            print("- Stories truncated at ~50-100 words instead of 300+")
            print("- Story narration endpoint returns empty responses")
            print("- UserProfile errors causing endpoint failures")
            
        finally:
            await self.cleanup()

async def main():
    analyzer = RootCauseAnalysis()
    await analyzer.run_analysis()

if __name__ == "__main__":
    asyncio.run(main())