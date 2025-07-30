#!/usr/bin/env python3
"""
Content API Endpoints Testing - Stories Page Regression Fix
Tests the newly added content API endpoints specifically
"""

import asyncio
import aiohttp
import json
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend URL from environment
BACKEND_URL = "https://dfc58399-9814-411f-9cc5-6e9560883b27.preview.emergentagent.com/api"

class ContentAPITester:
    """Content API specific tester"""
    
    def __init__(self):
        self.session = None
        self.test_user_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def setup_test_user(self):
        """Create a test user for the content API tests"""
        try:
            profile_data = {
                "name": "Emma",
                "age": 7,
                "location": "New York",
                "timezone": "America/New_York",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories", "animals", "music"],
                "learning_goals": ["reading", "counting"],
                "parent_email": "parent@example.com"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/users/profile",
                json=profile_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_user_id = data["id"]
                    logger.info(f"Created test user with ID: {self.test_user_id}")
                    return True
                else:
                    logger.error(f"Failed to create test user: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error creating test user: {str(e)}")
            return False
    
    async def test_content_api_stories(self):
        """Test GET /api/content/stories endpoint - Stories page regression fix"""
        logger.info("Testing GET /api/content/stories endpoint...")
        try:
            async with self.session.get(f"{BACKEND_URL}/content/stories") as response:
                if response.status == 200:
                    data = await response.json()
                    stories = data.get("stories", [])
                    
                    # Verify stories structure and content
                    story_validation = []
                    for story in stories:
                        validation = {
                            "has_id": "id" in story,
                            "has_title": "title" in story,
                            "has_description": "description" in story,
                            "has_content": "content" in story and len(story.get("content", "")) > 50,
                            "has_category": "category" in story,
                            "has_duration": "duration" in story,
                            "has_age_group": "age_group" in story,
                            "has_tags": "tags" in story and isinstance(story.get("tags"), list),
                            "has_moral": "moral" in story
                        }
                        story_validation.append(validation)
                    
                    # Check for expected stories
                    story_titles = [story.get("title", "") for story in stories]
                    expected_stories = ["Clever Rabbit", "Three Little Pigs", "Tortoise", "Goldilocks", "Ugly Duckling"]
                    found_expected = sum(1 for expected in expected_stories 
                                       if any(expected.lower() in title.lower() for title in story_titles))
                    
                    result = {
                        "success": True,
                        "stories_count": len(stories),
                        "has_stories": len(stories) >= 5,
                        "all_stories_have_required_fields": all(
                            all(validation.values()) for validation in story_validation
                        ),
                        "expected_stories_found": found_expected,
                        "story_titles": story_titles,
                        "sample_story": stories[0] if stories else None,
                        "stories_page_compatible": len(stories) >= 5 and all(
                            story.get("title") and story.get("content") and story.get("id")
                            for story in stories
                        )
                    }
                    
                    logger.info(f"Stories endpoint test result: {result}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Stories endpoint failed: HTTP {response.status}: {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            logger.error(f"Stories endpoint test error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_content_api_content_types(self):
        """Test GET /api/content/{content_type} endpoints for all 7 content types"""
        logger.info("Testing GET /api/content/{content_type} endpoints...")
        try:
            content_types = ["jokes", "riddles", "facts", "songs", "rhymes", "stories", "games"]
            content_results = {}
            
            for content_type in content_types:
                logger.info(f"Testing content type: {content_type}")
                async with self.session.get(f"{BACKEND_URL}/content/{content_type}") as response:
                    if response.status == 200:
                        data = await response.json()
                        content_list = data.get("content", [])
                        
                        content_results[content_type] = {
                            "available": True,
                            "count": data.get("count", len(content_list)),
                            "has_content": len(content_list) > 0,
                            "content_structure_valid": data.get("content_type") == content_type,
                            "sample_content": content_list[0] if content_list else None
                        }
                    elif response.status == 404:
                        content_results[content_type] = {
                            "available": False,
                            "error": "Content type not found"
                        }
                    else:
                        error_text = await response.text()
                        content_results[content_type] = {
                            "available": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
            
            # Calculate success metrics
            available_types = [ct for ct, result in content_results.items() if result.get("available", False)]
            types_with_content = [ct for ct, result in content_results.items() 
                                if result.get("available", False) and result.get("has_content", False)]
            
            result = {
                "success": True,
                "total_content_types_tested": len(content_types),
                "available_content_types": len(available_types),
                "content_types_with_data": len(types_with_content),
                "all_7_types_available": len(available_types) == 7,
                "content_results": content_results,
                "available_types_list": available_types,
                "types_with_content_list": types_with_content
            }
            
            logger.info(f"Content types test result: {result}")
            return result
        except Exception as e:
            logger.error(f"Content types test error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_content_api_generate(self):
        """Test POST /api/content/generate endpoint with 3-tier sourcing system"""
        logger.info("Testing POST /api/content/generate endpoint...")
        if not self.test_user_id:
            return {"success": False, "error": "No test user ID available"}
        
        try:
            # Test different content types with the generate endpoint
            test_requests = [
                {
                    "content_type": "story",
                    "user_input": "Tell me a story about a brave little mouse",
                    "user_id": self.test_user_id
                },
                {
                    "content_type": "joke",
                    "user_input": "Tell me a funny joke",
                    "user_id": self.test_user_id
                },
                {
                    "content_type": "riddle",
                    "user_input": "Give me a riddle to solve",
                    "user_id": self.test_user_id
                },
                {
                    "content_type": "song",
                    "user_input": "Sing me a happy song",
                    "user_id": self.test_user_id
                }
            ]
            
            generation_results = []
            
            for request_data in test_requests:
                logger.info(f"Testing generate endpoint for: {request_data['content_type']}")
                async with self.session.post(
                    f"{BACKEND_URL}/content/generate",
                    json=request_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        generation_results.append({
                            "content_type": request_data["content_type"],
                            "generation_successful": True,
                            "has_content": bool(data.get("content")),
                            "has_metadata": bool(data.get("metadata")),
                            "content_length": len(str(data.get("content", ""))),
                            "tier_used": data.get("metadata", {}).get("tier_used", "unknown"),
                            "response_preview": str(data.get("content", ""))[:100]
                        })
                    else:
                        error_text = await response.text()
                        generation_results.append({
                            "content_type": request_data["content_type"],
                            "generation_successful": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        })
                
                await asyncio.sleep(0.2)  # Small delay between requests
            
            # Test invalid requests
            invalid_request = {
                "content_type": "invalid_type",
                "user_input": "test",
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/content/generate",
                json=invalid_request
            ) as response:
                invalid_request_handled = response.status in [400, 404, 422]
            
            # Calculate success metrics
            successful_generations = [r for r in generation_results if r.get("generation_successful", False)]
            generations_with_content = [r for r in generation_results if r.get("has_content", False)]
            
            result = {
                "success": True,
                "total_requests_tested": len(test_requests),
                "successful_generations": len(successful_generations),
                "generations_with_content": len(generations_with_content),
                "all_content_types_working": len(successful_generations) == len(test_requests),
                "invalid_request_handled_correctly": invalid_request_handled,
                "generation_results": generation_results,
                "3_tier_sourcing_active": any(
                    r.get("tier_used") in ["local", "llm", "fallback"] 
                    for r in generation_results
                )
            }
            
            logger.info(f"Generate endpoint test result: {result}")
            return result
        except Exception as e:
            logger.error(f"Generate endpoint test error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def run_content_api_tests(self):
        """Run all content API tests"""
        logger.info("Starting Content API Testing for Stories Page Regression Fix...")
        
        # Setup test user
        if not await self.setup_test_user():
            return {"error": "Failed to setup test user"}
        
        # Run the three critical tests
        test_results = {}
        
        # Test 1: Stories endpoint
        test_results["stories_endpoint"] = await self.test_content_api_stories()
        
        # Test 2: Content type endpoints
        test_results["content_types_endpoints"] = await self.test_content_api_content_types()
        
        # Test 3: Generate endpoint
        test_results["generate_endpoint"] = await self.test_content_api_generate()
        
        return test_results
    
    def print_test_summary(self, results):
        """Print test summary"""
        print("\n" + "="*80)
        print("CONTENT API ENDPOINTS TEST RESULTS - STORIES PAGE REGRESSION FIX")
        print("="*80)
        
        if "error" in results:
            print(f"❌ Test setup failed: {results['error']}")
            return
        
        # Test 1: Stories endpoint
        stories_result = results.get("stories_endpoint", {})
        if stories_result.get("success"):
            print("✅ GET /api/content/stories - PASS")
            print(f"   - Stories count: {stories_result.get('stories_count', 0)}")
            print(f"   - Stories page compatible: {stories_result.get('stories_page_compatible', False)}")
            print(f"   - Expected stories found: {stories_result.get('expected_stories_found', 0)}")
            print(f"   - Story titles: {stories_result.get('story_titles', [])}")
        else:
            print("❌ GET /api/content/stories - FAIL")
            print(f"   - Error: {stories_result.get('error', 'Unknown error')}")
        
        # Test 2: Content types endpoints
        content_types_result = results.get("content_types_endpoints", {})
        if content_types_result.get("success"):
            print("✅ GET /api/content/{content_type} - PASS")
            print(f"   - Available content types: {content_types_result.get('available_content_types', 0)}/7")
            print(f"   - All 7 types available: {content_types_result.get('all_7_types_available', False)}")
            print(f"   - Available types: {content_types_result.get('available_types_list', [])}")
        else:
            print("❌ GET /api/content/{content_type} - FAIL")
            print(f"   - Error: {content_types_result.get('error', 'Unknown error')}")
        
        # Test 3: Generate endpoint
        generate_result = results.get("generate_endpoint", {})
        if generate_result.get("success"):
            print("✅ POST /api/content/generate - PASS")
            print(f"   - Successful generations: {generate_result.get('successful_generations', 0)}/4")
            print(f"   - All content types working: {generate_result.get('all_content_types_working', False)}")
            print(f"   - 3-tier sourcing active: {generate_result.get('3_tier_sourcing_active', False)}")
        else:
            print("❌ POST /api/content/generate - FAIL")
            print(f"   - Error: {generate_result.get('error', 'Unknown error')}")
        
        # Overall status
        all_passed = all(
            results.get(test, {}).get("success", False) 
            for test in ["stories_endpoint", "content_types_endpoints", "generate_endpoint"]
        )
        
        print("\n" + "-"*80)
        if all_passed:
            print("🎉 ALL CONTENT API TESTS PASSED - STORIES PAGE REGRESSION FIX SUCCESSFUL!")
        else:
            print("⚠️  SOME CONTENT API TESTS FAILED - STORIES PAGE MAY STILL HAVE ISSUES")
        print("="*80)

async def main():
    """Main test execution"""
    async with ContentAPITester() as tester:
        results = await tester.run_content_api_tests()
        tester.print_test_summary(results)
        
        # Return success status
        if "error" in results:
            return False
        
        return all(
            results.get(test, {}).get("success", False) 
            for test in ["stories_endpoint", "content_types_endpoints", "generate_endpoint"]
        )

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)