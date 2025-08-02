#!/usr/bin/env python3
"""
Iterative Story Generation Testing Suite
Tests the newly implemented iterative story generation system for 300+ word stories
"""

import asyncio
import aiohttp
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend URL from environment
BACKEND_URL = "https://5989f568-2718-4892-b46b-e42563583d9e.preview.emergentagent.com/api"

class IterativeStoryTester:
    """Test iterative story generation system"""
    
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.test_user_id = None
        self.test_session_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        if not text:
            return 0
        return len(text.split())
    
    def analyze_story_structure(self, story: str) -> Dict[str, Any]:
        """Analyze story structure for completeness"""
        if not story:
            return {"score": 0, "elements": [], "complete": False}
        
        story_lower = story.lower()
        elements = []
        
        # Check for story elements
        if any(phrase in story_lower for phrase in ["once upon a time", "long ago", "there was", "there lived"]):
            elements.append("opening")
        
        if any(phrase in story_lower for phrase in ["decided to", "went on", "journey", "adventure", "set out"]):
            elements.append("rising_action")
        
        if any(phrase in story_lower for phrase in ["suddenly", "then", "but", "however", "challenge", "problem"]):
            elements.append("conflict")
        
        if any(phrase in story_lower for phrase in ["finally", "at last", "in the end", "solved", "overcame"]):
            elements.append("resolution")
        
        if any(phrase in story_lower for phrase in ["happily", "learned", "the end", "ever after", "moral"]):
            elements.append("conclusion")
        
        score = len(elements)
        complete = score >= 3  # At least 3 story elements for a complete story
        
        return {
            "score": score,
            "elements": elements,
            "complete": complete,
            "total_possible": 5
        }
    
    async def test_iterative_story_generation(self):
        """Test the iterative story generation system with multiple story requests"""
        logger.info("🎯 TESTING ITERATIVE STORY GENERATION SYSTEM")
        
        # Test story requests as specified in the review
        story_requests = [
            "Tell me a story about a brave little mouse",
            "Can you tell me a story about a magical garden", 
            "I want a story about two friends who go on an adventure"
        ]
        
        all_results = []
        
        for i, story_request in enumerate(story_requests, 1):
            logger.info(f"Testing story {i}/3: {story_request}")
            
            try:
                # Create test user and session for each story
                await self.create_test_user(f"story_test_user_{i}")
                await self.create_test_session()
                
                # Test the story generation
                result = await self.test_single_story_generation(story_request)
                result["story_number"] = i
                result["request"] = story_request
                all_results.append(result)
                
                logger.info(f"Story {i} result: {result['word_count']} words, Structure: {result['structure']['score']}/5")
                
            except Exception as e:
                logger.error(f"Error testing story {i}: {str(e)}")
                all_results.append({
                    "story_number": i,
                    "request": story_request,
                    "success": False,
                    "error": str(e)
                })
        
        return self.analyze_overall_results(all_results)
    
    async def create_test_user(self, user_name: str):
        """Create a test user for story generation"""
        try:
            profile_data = {
                "name": user_name,
                "age": 7,
                "location": "Test City",
                "timezone": "America/New_York",
                "language": "english",
                "voice_personality": "story_narrator",
                "interests": ["stories", "adventures", "animals"],
                "learning_goals": ["reading", "imagination"],
                "parent_email": "test@example.com"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/users/profile",
                json=profile_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_user_id = data["id"]
                    logger.info(f"Created test user: {self.test_user_id}")
                    return True
                else:
                    logger.error(f"Failed to create user: HTTP {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error creating test user: {str(e)}")
            return False
    
    async def create_test_session(self):
        """Create a test conversation session"""
        try:
            session_data = {
                "user_id": self.test_user_id,
                "session_name": "Story Generation Test"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/session",
                json=session_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_session_id = data["id"]
                    logger.info(f"Created test session: {self.test_session_id}")
                    return True
                else:
                    logger.error(f"Failed to create session: HTTP {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error creating test session: {str(e)}")
            return False
    
    async def test_single_story_generation(self, story_request: str) -> Dict[str, Any]:
        """Test a single story generation request"""
        try:
            text_input = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": story_request
            }
            
            start_time = asyncio.get_event_loop().time()
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=text_input
            ) as response:
                end_time = asyncio.get_event_loop().time()
                processing_time = end_time - start_time
                
                if response.status == 200:
                    data = await response.json()
                    story_text = data.get("response_text", "")
                    
                    # Analyze the story
                    word_count = self.count_words(story_text)
                    structure = self.analyze_story_structure(story_text)
                    
                    return {
                        "success": True,
                        "story_text": story_text,
                        "word_count": word_count,
                        "meets_300_word_target": word_count >= 300,
                        "structure": structure,
                        "content_type": data.get("content_type"),
                        "has_audio": bool(data.get("response_audio")),
                        "processing_time": round(processing_time, 2),
                        "metadata": data.get("metadata", {}),
                        "character_count": len(story_text)
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "word_count": 0,
                        "meets_300_word_target": False
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "word_count": 0,
                "meets_300_word_target": False
            }
    
    def analyze_overall_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall test results"""
        successful_tests = [r for r in results if r.get("success", False)]
        total_tests = len(results)
        
        if not successful_tests:
            return {
                "overall_success": False,
                "success_rate": "0%",
                "total_tests": total_tests,
                "successful_tests": 0,
                "average_word_count": 0,
                "stories_meeting_300_words": 0,
                "average_structure_score": 0,
                "critical_issues": ["All story generation tests failed"],
                "results": results
            }
        
        # Calculate metrics
        word_counts = [r["word_count"] for r in successful_tests]
        structure_scores = [r["structure"]["score"] for r in successful_tests]
        stories_meeting_target = sum(1 for r in successful_tests if r.get("meets_300_word_target", False))
        
        average_word_count = sum(word_counts) / len(word_counts) if word_counts else 0
        average_structure_score = sum(structure_scores) / len(structure_scores) if structure_scores else 0
        
        # Identify critical issues
        critical_issues = []
        if average_word_count < 300:
            critical_issues.append(f"Average word count ({average_word_count:.0f}) below 300-word target")
        
        if stories_meeting_target == 0:
            critical_issues.append("No stories met the 300+ word requirement")
        
        if average_structure_score < 3:
            critical_issues.append(f"Poor story structure (avg {average_structure_score:.1f}/5)")
        
        # Determine overall success
        overall_success = (
            len(successful_tests) == total_tests and
            stories_meeting_target >= 2 and  # At least 2/3 stories should meet target
            average_structure_score >= 3
        )
        
        return {
            "overall_success": overall_success,
            "success_rate": f"{len(successful_tests)}/{total_tests} ({len(successful_tests)/total_tests*100:.1f}%)",
            "total_tests": total_tests,
            "successful_tests": len(successful_tests),
            "average_word_count": round(average_word_count, 1),
            "stories_meeting_300_words": stories_meeting_target,
            "stories_meeting_300_words_rate": f"{stories_meeting_target}/{len(successful_tests)} ({stories_meeting_target/len(successful_tests)*100:.1f}%)" if successful_tests else "0%",
            "average_structure_score": round(average_structure_score, 1),
            "structure_completeness": f"{average_structure_score}/5",
            "critical_issues": critical_issues,
            "individual_results": results,
            "summary": self.generate_summary(results, overall_success, critical_issues)
        }
    
    def generate_summary(self, results: List[Dict[str, Any]], overall_success: bool, critical_issues: List[str]) -> str:
        """Generate a summary of the test results"""
        if overall_success:
            return "✅ ITERATIVE STORY GENERATION SYSTEM WORKING: All tests passed, stories meet 300+ word requirement with complete narrative structure."
        else:
            issues_text = "; ".join(critical_issues)
            return f"❌ ITERATIVE STORY GENERATION SYSTEM FAILING: {issues_text}. System not producing required 300+ word stories with complete narrative structure."

async def main():
    """Run the iterative story generation tests"""
    logger.info("🎯 STARTING ITERATIVE STORY GENERATION VALIDATION")
    
    async with IterativeStoryTester() as tester:
        results = await tester.test_iterative_story_generation()
        
        # Print detailed results
        print("\n" + "="*80)
        print("ITERATIVE STORY GENERATION TEST RESULTS")
        print("="*80)
        
        print(f"Overall Success: {results['overall_success']}")
        print(f"Success Rate: {results['success_rate']}")
        print(f"Average Word Count: {results['average_word_count']}")
        print(f"Stories Meeting 300+ Words: {results['stories_meeting_300_words_rate']}")
        print(f"Average Structure Score: {results['structure_completeness']}")
        
        if results['critical_issues']:
            print(f"\nCritical Issues:")
            for issue in results['critical_issues']:
                print(f"  ❌ {issue}")
        
        print(f"\nSummary: {results['summary']}")
        
        # Print individual story results
        print(f"\nIndividual Story Results:")
        for result in results['individual_results']:
            if result.get('success', False):
                print(f"  Story {result['story_number']}: {result['word_count']} words, Structure: {result['structure']['score']}/5")
                print(f"    Request: {result['request']}")
                print(f"    Meets Target: {'✅' if result['meets_300_word_target'] else '❌'}")
                print(f"    Story Preview: {result['story_text'][:100]}...")
            else:
                print(f"  Story {result['story_number']}: FAILED - {result.get('error', 'Unknown error')}")
            print()
        
        return results

if __name__ == "__main__":
    asyncio.run(main())