#!/usr/bin/env python3
"""
Detailed Tone Analysis Test
Additional validation of specific conversation scenarios to ensure friendly companion tone.
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DetailedToneAnalyzer:
    def __init__(self):
        self.backend_url = "https://9c87ad27-55c0-4609-a47c-ef5b9de00cdd.preview.emergentagent.com/api"
        self.session_id = f"detailed_tone_test_{int(datetime.now().timestamp())}"
        
        # Specific test scenarios from the review request
        self.specific_tests = [
            {
                "input": "Hi Buddy, how are you today?",
                "expected_tone": "friendly_greeting",
                "description": "Basic greeting test"
            },
            {
                "input": "I'm excited about my new toy!",
                "expected_tone": "shared_excitement",
                "description": "Excitement sharing test"
            },
            {
                "input": "I'm feeling sad about something",
                "expected_tone": "supportive_friend",
                "description": "Emotional support test"
            },
            {
                "input": "Can you help me with a problem?",
                "expected_tone": "helpful_companion",
                "description": "Help request test"
            },
            {
                "input": "Tell me something fun!",
                "expected_tone": "enthusiastic_friend",
                "description": "Fun request test"
            }
        ]
        
    async def test_specific_conversation(self, test_case: dict) -> dict:
        """Test a specific conversation scenario"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "session_id": self.session_id,
                    "user_id": "detailed_test_user",
                    "message": test_case["input"]
                }
                
                async with session.post(
                    f"{self.backend_url}/conversations/text",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        
                        # Detailed analysis
                        analysis = self.analyze_response_details(response_text, test_case)
                        
                        return {
                            "test_case": test_case,
                            "response": response_text,
                            "analysis": analysis,
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "test_case": test_case,
                            "response": "",
                            "analysis": {"error": f"HTTP {response.status}: {error_text}"},
                            "status": "error"
                        }
                        
        except Exception as e:
            logger.error(f"Error in detailed test: {str(e)}")
            return {
                "test_case": test_case,
                "response": "",
                "analysis": {"error": str(e)},
                "status": "error"
            }
    
    def analyze_response_details(self, response_text: str, test_case: dict) -> dict:
        """Perform detailed analysis of response tone and content"""
        analysis = {
            "word_count": len(response_text.split()),
            "character_count": len(response_text),
            "tone_indicators": [],
            "problematic_phrases": [],
            "positive_indicators": [],
            "appropriateness_score": 0,
            "detailed_assessment": ""
        }
        
        response_lower = response_text.lower()
        
        # Check for specific tone indicators based on test type
        expected_tone = test_case["expected_tone"]
        
        if expected_tone == "friendly_greeting":
            # Should be warm but not overly affectionate
            positive_patterns = ["hi", "hello", "great", "good", "nice to", "how are", "doing well"]
            negative_patterns = ["sweetie", "dear", "precious", "my child"]
            
            for pattern in positive_patterns:
                if pattern in response_lower:
                    analysis["positive_indicators"].append(f"Friendly greeting: '{pattern}'")
                    analysis["appropriateness_score"] += 1
            
            for pattern in negative_patterns:
                if pattern in response_lower:
                    analysis["problematic_phrases"].append(f"Overly parental: '{pattern}'")
                    analysis["appropriateness_score"] -= 2
                    
        elif expected_tone == "shared_excitement":
            # Should show enthusiasm without being overly sentimental
            positive_patterns = ["that's awesome", "exciting", "cool", "amazing", "wow", "fantastic"]
            negative_patterns = ["so proud", "precious", "my dear", "sweetie"]
            
            for pattern in positive_patterns:
                if pattern in response_lower:
                    analysis["positive_indicators"].append(f"Natural enthusiasm: '{pattern}'")
                    analysis["appropriateness_score"] += 1
            
            for pattern in negative_patterns:
                if pattern in response_lower:
                    analysis["problematic_phrases"].append(f"Overly sentimental: '{pattern}'")
                    analysis["appropriateness_score"] -= 2
                    
        elif expected_tone == "supportive_friend":
            # Should be understanding and supportive like a friend, not parental
            positive_patterns = ["understand", "sorry to hear", "want to talk", "i'm here", "that sounds tough"]
            negative_patterns = ["don't worry", "everything will be okay", "mommy", "daddy", "sweetie"]
            
            for pattern in positive_patterns:
                if pattern in response_lower:
                    analysis["positive_indicators"].append(f"Supportive friend tone: '{pattern}'")
                    analysis["appropriateness_score"] += 1
            
            for pattern in negative_patterns:
                if pattern in response_lower:
                    analysis["problematic_phrases"].append(f"Too parental: '{pattern}'")
                    analysis["appropriateness_score"] -= 2
                    
        elif expected_tone == "helpful_companion":
            # Should offer help in a friendly, collaborative way
            positive_patterns = ["i can help", "let's figure", "what kind of", "tell me more", "we can work"]
            negative_patterns = ["let me take care", "don't worry about", "i'll handle"]
            
            for pattern in positive_patterns:
                if pattern in response_lower:
                    analysis["positive_indicators"].append(f"Collaborative help: '{pattern}'")
                    analysis["appropriateness_score"] += 1
            
            for pattern in negative_patterns:
                if pattern in response_lower:
                    analysis["problematic_phrases"].append(f"Too protective: '{pattern}'")
                    analysis["appropriateness_score"] -= 2
                    
        elif expected_tone == "enthusiastic_friend":
            # Should be fun and engaging like a friend
            positive_patterns = ["fun", "exciting", "cool", "awesome", "let's", "how about", "want to"]
            negative_patterns = ["precious", "sweetie", "my dear", "little one"]
            
            for pattern in positive_patterns:
                if pattern in response_lower:
                    analysis["positive_indicators"].append(f"Friend-like enthusiasm: '{pattern}'")
                    analysis["appropriateness_score"] += 1
            
            for pattern in negative_patterns:
                if pattern in response_lower:
                    analysis["problematic_phrases"].append(f"Overly parental: '{pattern}'")
                    analysis["appropriateness_score"] -= 2
        
        # Check for use of name or appropriate address terms
        if "friend" in response_lower:
            analysis["positive_indicators"].append("Uses 'friend' - appropriate companion term")
            analysis["appropriateness_score"] += 1
        elif "buddy" in response_lower:
            analysis["positive_indicators"].append("Uses 'buddy' - appropriate companion term")
            analysis["appropriateness_score"] += 1
        
        # Overall assessment
        if analysis["appropriateness_score"] >= 3:
            analysis["detailed_assessment"] = "EXCELLENT - Perfect friendly companion tone"
        elif analysis["appropriateness_score"] >= 1:
            analysis["detailed_assessment"] = "GOOD - Appropriate friendly tone"
        elif analysis["appropriateness_score"] >= -1:
            analysis["detailed_assessment"] = "ACCEPTABLE - Generally appropriate"
        else:
            analysis["detailed_assessment"] = "NEEDS IMPROVEMENT - Tone issues detected"
        
        return analysis
    
    async def run_detailed_analysis(self):
        """Run detailed tone analysis tests"""
        logger.info("🔍 Starting Detailed Tone Analysis Tests")
        
        results = []
        
        for i, test_case in enumerate(self.specific_tests, 1):
            logger.info(f"Running test {i}/{len(self.specific_tests)}: {test_case['description']}")
            
            result = await self.test_specific_conversation(test_case)
            results.append(result)
            
            if result["status"] == "success":
                analysis = result["analysis"]
                logger.info(f"✅ Response ({analysis['word_count']} words): {result['response'][:100]}...")
                logger.info(f"   Assessment: {analysis['detailed_assessment']}")
                logger.info(f"   Score: {analysis['appropriateness_score']}")
                
                if analysis["positive_indicators"]:
                    logger.info(f"   👍 Positive: {analysis['positive_indicators']}")
                
                if analysis["problematic_phrases"]:
                    logger.warning(f"   ⚠️  Issues: {analysis['problematic_phrases']}")
            else:
                logger.error(f"❌ Test failed: {result['analysis'].get('error', 'Unknown error')}")
            
            await asyncio.sleep(0.5)
        
        return results

async def main():
    """Main execution"""
    analyzer = DetailedToneAnalyzer()
    
    try:
        results = await analyzer.run_detailed_analysis()
        
        print("\n" + "="*80)
        print("DETAILED TONE ANALYSIS RESULTS")
        print("="*80)
        
        successful_tests = [r for r in results if r["status"] == "success"]
        
        if successful_tests:
            total_score = sum(r["analysis"]["appropriateness_score"] for r in successful_tests)
            avg_score = total_score / len(successful_tests)
            
            print(f"Successful Tests: {len(successful_tests)}/{len(results)}")
            print(f"Average Appropriateness Score: {avg_score:.2f}")
            
            print(f"\nDETAILED TEST RESULTS:")
            for i, result in enumerate(successful_tests, 1):
                test_case = result["test_case"]
                analysis = result["analysis"]
                
                print(f"\n{i}. {test_case['description'].upper()}")
                print(f"   Input: '{test_case['input']}'")
                print(f"   Response: '{result['response']}'")
                print(f"   Assessment: {analysis['detailed_assessment']}")
                print(f"   Score: {analysis['appropriateness_score']}")
                
                if analysis["positive_indicators"]:
                    print(f"   ✅ Positive aspects: {', '.join(analysis['positive_indicators'])}")
                
                if analysis["problematic_phrases"]:
                    print(f"   ❌ Issues found: {', '.join(analysis['problematic_phrases'])}")
            
            # Overall assessment
            print(f"\n🎯 OVERALL DETAILED ASSESSMENT:")
            if avg_score >= 2:
                print("✅ EXCELLENT - AI companion consistently uses perfect friendly tone")
            elif avg_score >= 1:
                print("✅ GOOD - AI companion tone is appropriate with minor variations")
            elif avg_score >= 0:
                print("⚠️  ACCEPTABLE - Generally appropriate but some improvements possible")
            else:
                print("❌ NEEDS IMPROVEMENT - Tone issues need to be addressed")
        
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"Detailed analysis failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())