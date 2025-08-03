#!/usr/bin/env python3
"""
Companion Tone Validation Test
Tests the AI companion's tone to ensure friendly companion language rather than overly parental terms.
"""

import asyncio
import aiohttp
import json
import logging
import re
from typing import Dict, List, Any
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompanionToneValidator:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = "https://754f72e7-5d73-488b-8ab4-20151131dc19.preview.emergentagent.com/api"
        
        # Define overly parental terms that should NOT be used
        self.overly_parental_terms = [
            "sweetie", "my dear", "darling", "honey", "sweetheart", 
            "precious", "little one", "baby", "cutie pie", "angel",
            "my child", "dear child", "sweet child"
        ]
        
        # Define appropriate friendly companion terms that SHOULD be used
        self.friendly_companion_terms = [
            "friend", "buddy", "pal", "mate", "dude", "kiddo" # kiddo is borderline but acceptable
        ]
        
        # Test conversations to validate tone
        self.test_conversations = [
            "Hi Buddy, how are you today?",
            "I'm excited about my new toy!",
            "I'm feeling sad about something",
            "Can you help me with a problem?",
            "Tell me something fun!",
            "What should we do today?",
            "I had a great day at school!",
            "I'm worried about my test tomorrow",
            "Can you tell me a story?",
            "I want to play a game"
        ]
        
        self.test_results = []
        self.session_id = f"tone_test_{int(datetime.now().timestamp())}"
        
    async def test_conversation_tone(self, message: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single conversation for tone validation"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "session_id": self.session_id,
                    "user_id": user_profile["id"],
                    "message": message
                }
                
                async with session.post(
                    f"{self.backend_url}/conversations/text",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response_text", "")
                        
                        # Analyze tone
                        tone_analysis = self.analyze_tone(response_text)
                        
                        return {
                            "input": message,
                            "response": response_text,
                            "tone_analysis": tone_analysis,
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "input": message,
                            "response": "",
                            "tone_analysis": {"error": f"HTTP {response.status}: {error_text}"},
                            "status": "error"
                        }
                        
        except Exception as e:
            logger.error(f"Error testing conversation '{message}': {str(e)}")
            return {
                "input": message,
                "response": "",
                "tone_analysis": {"error": str(e)},
                "status": "error"
            }
    
    def analyze_tone(self, response_text: str) -> Dict[str, Any]:
        """Analyze the tone of a response"""
        analysis = {
            "overly_parental_terms_found": [],
            "friendly_companion_terms_found": [],
            "tone_score": 0,
            "tone_assessment": "",
            "specific_issues": [],
            "positive_aspects": []
        }
        
        response_lower = response_text.lower()
        
        # Check for overly parental terms (negative)
        for term in self.overly_parental_terms:
            if term in response_lower:
                analysis["overly_parental_terms_found"].append(term)
                analysis["tone_score"] -= 2  # Penalty for parental terms
                analysis["specific_issues"].append(f"Uses overly parental term: '{term}'")
        
        # Check for friendly companion terms (positive)
        for term in self.friendly_companion_terms:
            if term in response_lower:
                analysis["friendly_companion_terms_found"].append(term)
                analysis["tone_score"] += 1  # Bonus for friendly terms
                analysis["positive_aspects"].append(f"Uses appropriate friendly term: '{term}'")
        
        # Check for natural enthusiasm without being overly sentimental
        enthusiasm_indicators = [
            "that's awesome", "that's cool", "that sounds great", "wow", "amazing",
            "fantastic", "wonderful", "excellent", "nice", "good job"
        ]
        
        overly_sentimental_indicators = [
            "my precious", "so proud of you", "you're such a special", 
            "mommy/daddy loves", "you're the best little"
        ]
        
        # Check enthusiasm
        enthusiasm_count = 0
        for indicator in enthusiasm_indicators:
            if indicator in response_lower:
                enthusiasm_count += 1
                analysis["positive_aspects"].append(f"Shows natural enthusiasm: '{indicator}'")
        
        if enthusiasm_count > 0:
            analysis["tone_score"] += 1
        
        # Check for overly sentimental language
        for indicator in overly_sentimental_indicators:
            if indicator in response_lower:
                analysis["tone_score"] -= 2
                analysis["specific_issues"].append(f"Overly sentimental language: '{indicator}'")
        
        # Check for supportive but not overly protective tone
        supportive_indicators = [
            "i understand", "that sounds", "i can help", "let's try", "want to talk about",
            "i'm here", "that's okay", "it's alright"
        ]
        
        overly_protective_indicators = [
            "don't worry about", "i'll protect you", "let me take care of", 
            "you don't need to", "i won't let anything"
        ]
        
        for indicator in supportive_indicators:
            if indicator in response_lower:
                analysis["tone_score"] += 0.5
                analysis["positive_aspects"].append(f"Supportive tone: '{indicator}'")
        
        for indicator in overly_protective_indicators:
            if indicator in response_lower:
                analysis["tone_score"] -= 1
                analysis["specific_issues"].append(f"Overly protective: '{indicator}'")
        
        # Check for age-appropriate friend-like language
        friend_like_indicators = [
            "want to", "let's", "how about", "what do you think", "that's interesting",
            "tell me more", "sounds like fun", "i'd love to", "we could"
        ]
        
        for indicator in friend_like_indicators:
            if indicator in response_lower:
                analysis["tone_score"] += 0.5
                analysis["positive_aspects"].append(f"Friend-like language: '{indicator}'")
        
        # Determine overall tone assessment
        if analysis["tone_score"] >= 3:
            analysis["tone_assessment"] = "EXCELLENT - Perfect friendly companion tone"
        elif analysis["tone_score"] >= 1:
            analysis["tone_assessment"] = "GOOD - Appropriate friendly tone with minor areas for improvement"
        elif analysis["tone_score"] >= -1:
            analysis["tone_assessment"] = "ACCEPTABLE - Generally appropriate but could be more friend-like"
        else:
            analysis["tone_assessment"] = "NEEDS IMPROVEMENT - Too parental or inappropriate tone"
        
        return analysis
    
    async def run_comprehensive_tone_validation(self) -> Dict[str, Any]:
        """Run comprehensive tone validation tests"""
        logger.info("🎯 Starting Companion Tone Validation Tests")
        
        # Create test user profile
        test_user = {
            "id": "tone_test_user",
            "name": "Emma",
            "age": 7,
            "preferences": {
                "voice_personality": "friendly_companion"
            }
        }
        
        # Test all conversations
        all_results = []
        successful_tests = 0
        failed_tests = 0
        
        for i, conversation in enumerate(self.test_conversations, 1):
            logger.info(f"Testing conversation {i}/{len(self.test_conversations)}: '{conversation}'")
            
            result = await self.test_conversation_tone(conversation, test_user)
            all_results.append(result)
            
            if result["status"] == "success":
                successful_tests += 1
                tone_analysis = result["tone_analysis"]
                logger.info(f"✅ Response: {result['response'][:100]}...")
                logger.info(f"   Tone Score: {tone_analysis['tone_score']}")
                logger.info(f"   Assessment: {tone_analysis['tone_assessment']}")
                
                if tone_analysis["overly_parental_terms_found"]:
                    logger.warning(f"   ⚠️  Parental terms found: {tone_analysis['overly_parental_terms_found']}")
                
                if tone_analysis["friendly_companion_terms_found"]:
                    logger.info(f"   👍 Friendly terms found: {tone_analysis['friendly_companion_terms_found']}")
                    
            else:
                failed_tests += 1
                logger.error(f"❌ Test failed: {result['tone_analysis'].get('error', 'Unknown error')}")
            
            # Small delay between requests
            await asyncio.sleep(0.5)
        
        # Calculate overall results
        total_tests = len(self.test_conversations)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Analyze overall tone patterns
        overall_analysis = self.analyze_overall_patterns(all_results)
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "overall_analysis": overall_analysis,
            "detailed_results": all_results,
            "test_timestamp": datetime.now().isoformat()
        }
        
        return summary
    
    def analyze_overall_patterns(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall tone patterns across all tests"""
        successful_results = [r for r in results if r["status"] == "success"]
        
        if not successful_results:
            return {"error": "No successful tests to analyze"}
        
        # Aggregate statistics
        total_parental_terms = []
        total_friendly_terms = []
        total_issues = []
        total_positive_aspects = []
        tone_scores = []
        
        for result in successful_results:
            analysis = result["tone_analysis"]
            total_parental_terms.extend(analysis["overly_parental_terms_found"])
            total_friendly_terms.extend(analysis["friendly_companion_terms_found"])
            total_issues.extend(analysis["specific_issues"])
            total_positive_aspects.extend(analysis["positive_aspects"])
            tone_scores.append(analysis["tone_score"])
        
        # Calculate averages and patterns
        avg_tone_score = sum(tone_scores) / len(tone_scores) if tone_scores else 0
        
        # Count unique terms
        unique_parental_terms = list(set(total_parental_terms))
        unique_friendly_terms = list(set(total_friendly_terms))
        
        # Determine overall compliance
        parental_term_violations = len(total_parental_terms)
        friendly_term_usage = len(total_friendly_terms)
        
        compliance_score = 100
        if parental_term_violations > 0:
            compliance_score -= (parental_term_violations * 20)  # -20 points per violation
        
        if friendly_term_usage > 0:
            compliance_score += min(friendly_term_usage * 5, 20)  # +5 points per friendly term, max +20
        
        compliance_score = max(0, min(100, compliance_score))  # Keep between 0-100
        
        # Overall assessment
        if compliance_score >= 90 and parental_term_violations == 0:
            overall_assessment = "EXCELLENT - Perfect friendly companion tone"
        elif compliance_score >= 70 and parental_term_violations <= 1:
            overall_assessment = "GOOD - Generally appropriate tone with minor issues"
        elif compliance_score >= 50:
            overall_assessment = "ACCEPTABLE - Some improvements needed"
        else:
            overall_assessment = "NEEDS IMPROVEMENT - Significant tone issues detected"
        
        return {
            "average_tone_score": round(avg_tone_score, 2),
            "compliance_score": compliance_score,
            "overall_assessment": overall_assessment,
            "parental_term_violations": parental_term_violations,
            "unique_parental_terms_found": unique_parental_terms,
            "friendly_term_usage": friendly_term_usage,
            "unique_friendly_terms_found": unique_friendly_terms,
            "total_issues": len(total_issues),
            "total_positive_aspects": len(total_positive_aspects),
            "success_criteria_met": {
                "no_overly_parental_terms": parental_term_violations == 0,
                "uses_friendly_language": friendly_term_usage > 0,
                "natural_enthusiasm": avg_tone_score > 0,
                "supportive_not_protective": compliance_score >= 70,
                "age_appropriate_friend_like": avg_tone_score >= 1
            }
        }

async def main():
    """Main test execution"""
    validator = CompanionToneValidator()
    
    try:
        logger.info("🚀 Starting Companion Tone Validation Test Suite")
        
        # Run comprehensive validation
        results = await validator.run_comprehensive_tone_validation()
        
        # Print summary
        print("\n" + "="*80)
        print("COMPANION TONE VALIDATION RESULTS")
        print("="*80)
        
        print(f"Total Tests: {results['total_tests']}")
        print(f"Successful Tests: {results['successful_tests']}")
        print(f"Failed Tests: {results['failed_tests']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        
        if results['successful_tests'] > 0:
            overall = results['overall_analysis']
            print(f"\nOVERALL TONE ANALYSIS:")
            print(f"Average Tone Score: {overall['average_tone_score']}")
            print(f"Compliance Score: {overall['compliance_score']}/100")
            print(f"Assessment: {overall['overall_assessment']}")
            
            print(f"\nTONE VALIDATION CRITERIA:")
            criteria = overall['success_criteria_met']
            for criterion, met in criteria.items():
                status = "✅ PASS" if met else "❌ FAIL"
                print(f"  {criterion.replace('_', ' ').title()}: {status}")
            
            if overall['parental_term_violations'] > 0:
                print(f"\n⚠️  PARENTAL TERM VIOLATIONS: {overall['parental_term_violations']}")
                print(f"   Terms found: {overall['unique_parental_terms_found']}")
            
            if overall['friendly_term_usage'] > 0:
                print(f"\n👍 FRIENDLY TERMS USED: {overall['friendly_term_usage']}")
                print(f"   Terms found: {overall['unique_friendly_terms_found']}")
            
            # Overall compliance assessment
            print(f"\n🎯 COMPANION TONE COMPLIANCE:")
            if overall['compliance_score'] >= 90 and overall['parental_term_violations'] == 0:
                print("✅ EXCELLENT - AI companion uses perfect friendly tone")
            elif overall['compliance_score'] >= 70:
                print("✅ GOOD - AI companion tone is generally appropriate")
            elif overall['compliance_score'] >= 50:
                print("⚠️  ACCEPTABLE - Some tone improvements needed")
            else:
                print("❌ NEEDS IMPROVEMENT - Significant tone issues detected")
        
        print("\n" + "="*80)
        
        return results
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())