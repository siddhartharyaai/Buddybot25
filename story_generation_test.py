#!/usr/bin/env python3
"""
Story Generation Testing - Focus on 300+ Word Story Validation
Testing the critical story generation fix as requested in review
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StoryGenerationTester:
    def __init__(self):
        # Use the backend URL from frontend/.env
        self.base_url = "https://0e5dcf5a-4e8d-4074-9227-19f4607bd0be.preview.emergentagent.com/api"
        self.test_results = []
        self.session = None
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        logger.info("🎯 STORY GENERATION TESTING INITIALIZED")
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    def count_words(self, text: str) -> int:
        """Count words in text"""
        if not text:
            return 0
        return len(text.split())
    
    def analyze_story_structure(self, story: str) -> Dict[str, Any]:
        """Analyze story for narrative structure elements"""
        story_lower = story.lower()
        
        # Check for story structure elements
        structure_elements = {
            "introduction": any(word in story_lower for word in ["once", "there was", "lived", "began", "started"]),
            "rising_action": any(word in story_lower for word in ["then", "suddenly", "but", "however", "decided", "wanted"]),
            "climax": any(word in story_lower for word in ["finally", "at last", "suddenly", "realized", "discovered"]),
            "falling_action": any(word in story_lower for word in ["after", "then", "so", "because", "as a result"]),
            "resolution": any(word in story_lower for word in ["end", "finally", "happily", "learned", "never forgot"])
        }
        
        structure_score = sum(structure_elements.values())
        
        return {
            "elements": structure_elements,
            "score": structure_score,
            "total_possible": 5,
            "percentage": (structure_score / 5) * 100
        }
    
    async def test_health_check(self) -> bool:
        """Test if backend is accessible"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Backend health check passed: {data}")
                    return True
                else:
                    logger.error(f"❌ Backend health check failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Backend connection failed: {str(e)}")
            return False
    
    async def test_story_generation_via_text_conversation(self, story_request: str, test_name: str) -> Dict[str, Any]:
        """Test story generation through text conversation endpoint"""
        try:
            logger.info(f"🎭 Testing story generation: {test_name}")
            logger.info(f"📝 Story request: '{story_request}'")
            
            # Create test payload
            payload = {
                "session_id": f"story_test_{int(time.time())}",
                "user_id": "story_test_user",
                "message": story_request
            }
            
            # Send request
            async with self.session.post(
                f"{self.base_url}/conversations/text",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"❌ Request failed with status {response.status}: {error_text}")
                    return {
                        "test_name": test_name,
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "word_count": 0,
                        "meets_300_words": False,
                        "structure_analysis": {"score": 0, "percentage": 0}
                    }
                
                data = await response.json()
                story_text = data.get("response_text", "")
                content_type = data.get("content_type", "unknown")
                
                # Analyze the story
                word_count = self.count_words(story_text)
                meets_300_words = word_count >= 300
                structure_analysis = self.analyze_story_structure(story_text)
                
                # Log results
                logger.info(f"📊 STORY ANALYSIS RESULTS:")
                logger.info(f"   📝 Word Count: {word_count} words")
                logger.info(f"   ✅ Meets 300+ requirement: {meets_300_words}")
                logger.info(f"   🏗️ Structure Score: {structure_analysis['score']}/5 ({structure_analysis['percentage']:.1f}%)")
                logger.info(f"   🎭 Content Type: {content_type}")
                logger.info(f"   📖 Story Preview: {story_text[:200]}...")
                
                if meets_300_words and structure_analysis['score'] >= 3:
                    logger.info(f"✅ {test_name}: PASSED - Complete story with good structure")
                elif meets_300_words:
                    logger.info(f"⚠️ {test_name}: PARTIAL - Good length but weak structure")
                else:
                    logger.error(f"❌ {test_name}: FAILED - Story too short ({word_count} words)")
                
                return {
                    "test_name": test_name,
                    "success": meets_300_words and structure_analysis['score'] >= 3,
                    "story_text": story_text,
                    "word_count": word_count,
                    "meets_300_words": meets_300_words,
                    "structure_analysis": structure_analysis,
                    "content_type": content_type,
                    "response_metadata": data.get("metadata", {})
                }
                
        except Exception as e:
            logger.error(f"❌ Story generation test failed: {str(e)}")
            return {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "word_count": 0,
                "meets_300_words": False,
                "structure_analysis": {"score": 0, "percentage": 0}
            }
    
    async def test_story_continuation_logic(self) -> Dict[str, Any]:
        """Test if story continuation logic works for short stories"""
        try:
            logger.info("🔄 Testing story continuation logic...")
            
            # Test with a request that might generate a short response initially
            story_request = "Tell me a very short story about a cat"
            
            result = await self.test_story_generation_via_text_conversation(
                story_request, "Story Continuation Logic Test"
            )
            
            # Check if continuation logic was triggered (should still meet 300+ words)
            if result["word_count"] >= 300:
                logger.info("✅ Story continuation logic working - even 'short' request generated 300+ words")
                result["continuation_logic_working"] = True
            else:
                logger.error("❌ Story continuation logic failed - short story request stayed short")
                result["continuation_logic_working"] = False
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Story continuation test failed: {str(e)}")
            return {
                "test_name": "Story Continuation Logic Test",
                "success": False,
                "error": str(e),
                "continuation_logic_working": False
            }
    
    async def run_comprehensive_story_tests(self) -> Dict[str, Any]:
        """Run comprehensive story generation tests"""
        logger.info("🎯 STARTING COMPREHENSIVE STORY GENERATION TESTING")
        
        # Test cases from the review request
        test_cases = [
            ("Tell me a story about a brave little mouse", "Brave Little Mouse Story"),
            ("Can you tell me a story about friendship", "Friendship Story"),
            ("I want a story about a magic forest", "Magic Forest Story"),
            ("Please tell me a complete story about a dragon and a princess", "Dragon Princess Story"),
            ("Create a story about a child who discovers something amazing", "Amazing Discovery Story")
        ]
        
        all_results = []
        
        # Run each test case
        for story_request, test_name in test_cases:
            result = await self.test_story_generation_via_text_conversation(story_request, test_name)
            all_results.append(result)
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        # Test story continuation logic
        continuation_result = await self.test_story_continuation_logic()
        all_results.append(continuation_result)
        
        # Calculate overall statistics
        total_tests = len(all_results)
        successful_tests = sum(1 for r in all_results if r.get("success", False))
        tests_meeting_300_words = sum(1 for r in all_results if r.get("meets_300_words", False))
        
        avg_word_count = sum(r.get("word_count", 0) for r in all_results) / total_tests if total_tests > 0 else 0
        avg_structure_score = sum(r.get("structure_analysis", {}).get("score", 0) for r in all_results) / total_tests if total_tests > 0 else 0
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / total_tests) * 100 if total_tests > 0 else 0,
            "tests_meeting_300_words": tests_meeting_300_words,
            "word_count_compliance_rate": (tests_meeting_300_words / total_tests) * 100 if total_tests > 0 else 0,
            "average_word_count": avg_word_count,
            "average_structure_score": avg_structure_score,
            "detailed_results": all_results
        }
        
        return summary
    
    async def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("🎯 STORY GENERATION TESTING REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Overall statistics
        report.append("📊 OVERALL RESULTS:")
        report.append(f"   Total Tests: {results['total_tests']}")
        report.append(f"   Successful Tests: {results['successful_tests']}")
        report.append(f"   Success Rate: {results['success_rate']:.1f}%")
        report.append(f"   Tests Meeting 300+ Words: {results['tests_meeting_300_words']}")
        report.append(f"   Word Count Compliance: {results['word_count_compliance_rate']:.1f}%")
        report.append(f"   Average Word Count: {results['average_word_count']:.1f} words")
        report.append(f"   Average Structure Score: {results['average_structure_score']:.1f}/5")
        report.append("")
        
        # Critical assessment
        if results['word_count_compliance_rate'] >= 80:
            report.append("✅ CRITICAL ASSESSMENT: Story length validation WORKING")
        else:
            report.append("❌ CRITICAL ASSESSMENT: Story length validation FAILING")
        
        if results['average_structure_score'] >= 3:
            report.append("✅ NARRATIVE STRUCTURE: Complete story structure WORKING")
        else:
            report.append("❌ NARRATIVE STRUCTURE: Story structure INCOMPLETE")
        
        report.append("")
        
        # Detailed results
        report.append("📝 DETAILED TEST RESULTS:")
        for i, result in enumerate(results['detailed_results'], 1):
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            report.append(f"{i}. {result['test_name']}: {status}")
            report.append(f"   Words: {result.get('word_count', 0)} | Structure: {result.get('structure_analysis', {}).get('score', 0)}/5")
            
            if result.get("error"):
                report.append(f"   Error: {result['error']}")
            report.append("")
        
        # Recommendations
        report.append("🔧 RECOMMENDATIONS:")
        if results['word_count_compliance_rate'] < 80:
            report.append("❌ URGENT: Story generation is not meeting 300+ word requirement")
            report.append("   - Check conversation_agent.py story continuation logic")
            report.append("   - Verify token limits are completely removed")
            report.append("   - Test story framework implementation")
        
        if results['average_structure_score'] < 3:
            report.append("⚠️ Story structure needs improvement")
            report.append("   - Review story framework guidelines")
            report.append("   - Enhance narrative structure prompts")
        
        if results['success_rate'] >= 80:
            report.append("✅ Story generation system is working well overall")
        
        return "\n".join(report)

async def main():
    """Main test execution"""
    tester = StoryGenerationTester()
    
    try:
        await tester.setup()
        
        # Check backend connectivity
        if not await tester.test_health_check():
            logger.error("❌ Cannot connect to backend - aborting tests")
            return
        
        # Run comprehensive story tests
        results = await tester.run_comprehensive_story_tests()
        
        # Generate and display report
        report = await tester.generate_test_report(results)
        print("\n" + report)
        
        # Save results to file
        with open("/app/story_generation_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info("📄 Test results saved to story_generation_test_results.json")
        
        # Return exit code based on results
        if results['word_count_compliance_rate'] >= 80 and results['average_structure_score'] >= 3:
            logger.info("🎉 STORY GENERATION TESTS PASSED")
            return 0
        else:
            logger.error("❌ STORY GENERATION TESTS FAILED")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Test execution failed: {str(e)}")
        return 1
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)