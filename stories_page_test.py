#!/usr/bin/env python3
"""
Stories Page Specific Testing
Verify that the Stories page will work correctly with the new content API endpoints
"""

import asyncio
import aiohttp
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend URL from environment
BACKEND_URL = "https://dfc58399-9814-411f-9cc5-6e9560883b27.preview.emergentagent.com/api"

class StoriesPageTester:
    """Stories page specific tester"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_stories_page_data_format(self):
        """Test that stories data matches what StoriesPage.js expects"""
        logger.info("Testing stories data format for StoriesPage.js compatibility...")
        
        try:
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status == 200:
                    data = await response.json()
                    stories = data.get("stories", [])
                    
                    if not stories:
                        return {"success": False, "error": "No stories returned"}
                    
                    # Check each story has the required fields for StoriesPage.js
                    story_checks = []
                    for i, story in enumerate(stories):
                        check = {
                            "story_index": i,
                            "has_id": "id" in story and story["id"],
                            "has_title": "title" in story and story["title"],
                            "has_description": "description" in story,
                            "has_content": "content" in story and len(story["content"]) > 100,
                            "has_category": "category" in story,
                            "has_duration": "duration" in story,
                            "has_age_group": "age_group" in story,
                            "has_tags": "tags" in story and isinstance(story["tags"], list),
                            "content_length": len(story.get("content", "")),
                            "title": story.get("title", ""),
                            "valid_for_stories_page": all([
                                "id" in story and story["id"],
                                "title" in story and story["title"],
                                "content" in story and len(story["content"]) > 50
                            ])
                        }
                        story_checks.append(check)
                    
                    valid_stories = [s for s in story_checks if s["valid_for_stories_page"]]
                    
                    return {
                        "success": True,
                        "total_stories": len(stories),
                        "valid_stories_for_page": len(valid_stories),
                        "all_stories_valid": len(valid_stories) == len(stories),
                        "stories_page_ready": len(valid_stories) >= 5,
                        "story_checks": story_checks,
                        "sample_story_structure": stories[0] if stories else None
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_no_404_errors(self):
        """Test that there are no 404 errors that would cause Stories page to fail"""
        logger.info("Testing for 404 errors that could break Stories page...")
        
        endpoints_to_test = [
            "/content/stories",
            "/content/story",  # Test if this also works
            "/health"  # Basic health check
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            try:
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    results[endpoint] = {
                        "status_code": response.status,
                        "no_404": response.status != 404,
                        "accessible": response.status in [200, 400, 422]  # Any non-404 response
                    }
            except Exception as e:
                results[endpoint] = {
                    "status_code": "error",
                    "no_404": False,
                    "accessible": False,
                    "error": str(e)
                }
        
        critical_endpoints_working = results.get("/content/stories", {}).get("no_404", False)
        
        return {
            "success": True,
            "critical_endpoints_working": critical_endpoints_working,
            "stories_endpoint_accessible": results.get("/content/stories", {}).get("accessible", False),
            "endpoint_results": results,
            "no_critical_404s": critical_endpoints_working
        }
    
    async def test_voice_functionality_data(self):
        """Test that voice functionality has the data it needs"""
        logger.info("Testing voice functionality data availability...")
        
        try:
            # Test voice personalities endpoint
            async with self.session.get(f"{BACKEND_URL}/voice/personalities") as response:
                voice_personalities_available = response.status == 200
                voice_data = await response.json() if response.status == 200 else {}
            
            # Test stories content for voice reading
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status == 200:
                    data = await response.json()
                    stories = data.get("stories", [])
                    
                    # Check if stories have content suitable for voice reading
                    voice_ready_stories = []
                    for story in stories:
                        content = story.get("content", "")
                        if len(content) > 50 and len(content) < 2000:  # Good length for voice
                            voice_ready_stories.append({
                                "title": story.get("title"),
                                "content_length": len(content),
                                "voice_suitable": True
                            })
                    
                    return {
                        "success": True,
                        "voice_personalities_available": voice_personalities_available,
                        "voice_personalities_count": len(voice_data) if isinstance(voice_data, dict) else 0,
                        "stories_available_for_voice": len(voice_ready_stories),
                        "voice_functionality_ready": voice_personalities_available and len(voice_ready_stories) > 0,
                        "voice_ready_stories": voice_ready_stories
                    }
                else:
                    return {"success": False, "error": f"Stories not available: HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def run_stories_page_tests(self):
        """Run all Stories page specific tests"""
        logger.info("Starting Stories Page Regression Testing...")
        
        test_results = {}
        
        # Test 1: Data format compatibility
        test_results["data_format"] = await self.test_stories_page_data_format()
        
        # Test 2: No 404 errors
        test_results["no_404_errors"] = await self.test_no_404_errors()
        
        # Test 3: Voice functionality data
        test_results["voice_functionality"] = await self.test_voice_functionality_data()
        
        return test_results
    
    def print_test_summary(self, results):
        """Print Stories page test summary"""
        print("\n" + "="*80)
        print("STORIES PAGE REGRESSION TEST RESULTS")
        print("="*80)
        
        # Test 1: Data format
        data_format_result = results.get("data_format", {})
        if data_format_result.get("success"):
            print("✅ Stories Data Format - PASS")
            print(f"   - Total stories: {data_format_result.get('total_stories', 0)}")
            print(f"   - Valid stories for page: {data_format_result.get('valid_stories_for_page', 0)}")
            print(f"   - Stories page ready: {data_format_result.get('stories_page_ready', False)}")
            print(f"   - All stories valid: {data_format_result.get('all_stories_valid', False)}")
        else:
            print("❌ Stories Data Format - FAIL")
            print(f"   - Error: {data_format_result.get('error', 'Unknown error')}")
        
        # Test 2: No 404 errors
        no_404_result = results.get("no_404_errors", {})
        if no_404_result.get("success"):
            print("✅ No Critical 404 Errors - PASS")
            print(f"   - Stories endpoint accessible: {no_404_result.get('stories_endpoint_accessible', False)}")
            print(f"   - No critical 404s: {no_404_result.get('no_critical_404s', False)}")
        else:
            print("❌ No Critical 404 Errors - FAIL")
            print(f"   - Error: {no_404_result.get('error', 'Unknown error')}")
        
        # Test 3: Voice functionality
        voice_result = results.get("voice_functionality", {})
        if voice_result.get("success"):
            print("✅ Voice Functionality Data - PASS")
            print(f"   - Voice personalities available: {voice_result.get('voice_personalities_available', False)}")
            print(f"   - Stories available for voice: {voice_result.get('stories_available_for_voice', 0)}")
            print(f"   - Voice functionality ready: {voice_result.get('voice_functionality_ready', False)}")
        else:
            print("❌ Voice Functionality Data - FAIL")
            print(f"   - Error: {voice_result.get('error', 'Unknown error')}")
        
        # Overall status
        all_passed = all(
            results.get(test, {}).get("success", False) 
            for test in ["data_format", "no_404_errors", "voice_functionality"]
        )
        
        stories_page_will_work = (
            data_format_result.get("stories_page_ready", False) and
            no_404_result.get("no_critical_404s", False)
        )
        
        print("\n" + "-"*80)
        print("STORIES PAGE REGRESSION FIX ASSESSMENT:")
        if stories_page_will_work:
            print("🎉 STORIES PAGE REGRESSION SUCCESSFULLY FIXED!")
            print("   - Stories page should now load properly")
            print("   - All required data is available")
            print("   - No critical 404 errors")
        else:
            print("⚠️  STORIES PAGE MAY STILL HAVE ISSUES")
            print("   - Check the failed tests above")
        
        if voice_result.get("voice_functionality_ready", False):
            print("🔊 VOICE FUNCTIONALITY IS READY")
        else:
            print("🔇 VOICE FUNCTIONALITY MAY HAVE ISSUES")
        
        print("="*80)

async def main():
    """Main test execution"""
    async with StoriesPageTester() as tester:
        results = await tester.run_stories_page_tests()
        tester.print_test_summary(results)
        
        # Return success status based on critical functionality
        data_format_ok = results.get("data_format", {}).get("stories_page_ready", False)
        no_404_ok = results.get("no_404_errors", {}).get("no_critical_404s", False)
        
        return data_format_ok and no_404_ok

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)