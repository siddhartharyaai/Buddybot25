#!/usr/bin/env python3
"""
Parental Terms Detection Test
Specifically tests for prohibited overly parental terms in various conversation contexts.
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ParentalTermsDetector:
    def __init__(self):
        self.backend_url = "https://ac3a5a48-4dec-498e-8545-e5993602e42f.preview.emergentagent.com/api"
        self.session_id = f"parental_terms_test_{int(datetime.now().timestamp())}"
        
        # Comprehensive list of prohibited parental terms
        self.prohibited_terms = [
            "sweetie", "my dear", "darling", "honey", "sweetheart", 
            "precious", "little one", "baby", "cutie pie", "angel",
            "my child", "dear child", "sweet child", "little angel",
            "my sweet", "dear one", "love", "lovely", "dearest"
        ]
        
        # Test scenarios that might trigger parental language
        self.trigger_scenarios = [
            "I'm scared of the dark",
            "I miss my mommy",
            "I don't want to go to bed",
            "I'm worried about monsters",
            "I had a nightmare",
            "I'm crying because I'm sad",
            "I hurt myself and it hurts",
            "I don't understand something",
            "I made a mistake and feel bad",
            "I'm lonely and need comfort",
            "Can you sing me a lullaby?",
            "I want someone to take care of me",
            "I'm feeling very emotional",
            "I need help with something difficult",
            "I'm having trouble sleeping"
        ]
        
    async def test_for_parental_terms(self, message: str) -> dict:
        """Test a message for parental terms in response"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "session_id": self.session_id,
                    "user_id": "parental_test_user",
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
                        
                        # Check for prohibited terms
                        detected_terms = self.detect_prohibited_terms(response_text)
                        
                        return {
                            "input": message,
                            "response": response_text,
                            "detected_terms": detected_terms,
                            "is_compliant": len(detected_terms) == 0,
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "input": message,
                            "response": "",
                            "detected_terms": [],
                            "is_compliant": None,
                            "error": f"HTTP {response.status}: {error_text}",
                            "status": "error"
                        }
                        
        except Exception as e:
            logger.error(f"Error testing parental terms: {str(e)}")
            return {
                "input": message,
                "response": "",
                "detected_terms": [],
                "is_compliant": None,
                "error": str(e),
                "status": "error"
            }
    
    def detect_prohibited_terms(self, response_text: str) -> list:
        """Detect prohibited parental terms in response"""
        response_lower = response_text.lower()
        detected = []
        
        for term in self.prohibited_terms:
            if term in response_lower:
                detected.append(term)
        
        return detected
    
    async def run_parental_terms_detection(self):
        """Run comprehensive parental terms detection"""
        logger.info("🚫 Starting Parental Terms Detection Tests")
        
        results = []
        compliant_count = 0
        non_compliant_count = 0
        error_count = 0
        
        for i, scenario in enumerate(self.trigger_scenarios, 1):
            logger.info(f"Testing scenario {i}/{len(self.trigger_scenarios)}: '{scenario}'")
            
            result = await self.test_for_parental_terms(scenario)
            results.append(result)
            
            if result["status"] == "success":
                if result["is_compliant"]:
                    compliant_count += 1
                    logger.info(f"✅ COMPLIANT - No parental terms detected")
                    logger.info(f"   Response: {result['response'][:100]}...")
                else:
                    non_compliant_count += 1
                    logger.warning(f"❌ NON-COMPLIANT - Parental terms detected: {result['detected_terms']}")
                    logger.warning(f"   Response: {result['response'][:100]}...")
            else:
                error_count += 1
                logger.error(f"❌ ERROR: {result.get('error', 'Unknown error')}")
            
            await asyncio.sleep(0.5)
        
        return {
            "total_tests": len(self.trigger_scenarios),
            "compliant_count": compliant_count,
            "non_compliant_count": non_compliant_count,
            "error_count": error_count,
            "compliance_rate": (compliant_count / (compliant_count + non_compliant_count)) * 100 if (compliant_count + non_compliant_count) > 0 else 0,
            "results": results
        }

async def main():
    """Main execution"""
    detector = ParentalTermsDetector()
    
    try:
        results = await detector.run_parental_terms_detection()
        
        print("\n" + "="*80)
        print("PARENTAL TERMS DETECTION RESULTS")
        print("="*80)
        
        print(f"Total Tests: {results['total_tests']}")
        print(f"Compliant (No Parental Terms): {results['compliant_count']}")
        print(f"Non-Compliant (Parental Terms Found): {results['non_compliant_count']}")
        print(f"Errors: {results['error_count']}")
        print(f"Compliance Rate: {results['compliance_rate']:.1f}%")
        
        # Show any violations
        violations = [r for r in results['results'] if r['status'] == 'success' and not r['is_compliant']]
        
        if violations:
            print(f"\n❌ PARENTAL TERMS VIOLATIONS DETECTED:")
            for i, violation in enumerate(violations, 1):
                print(f"\n{i}. Input: '{violation['input']}'")
                print(f"   Response: '{violation['response']}'")
                print(f"   Prohibited terms found: {violation['detected_terms']}")
        else:
            print(f"\n✅ NO PARENTAL TERMS VIOLATIONS DETECTED")
        
        # Overall assessment
        print(f"\n🎯 PARENTAL TERMS COMPLIANCE ASSESSMENT:")
        if results['compliance_rate'] == 100:
            print("✅ PERFECT COMPLIANCE - No prohibited parental terms detected in any scenario")
        elif results['compliance_rate'] >= 90:
            print("✅ EXCELLENT COMPLIANCE - Very few parental terms detected")
        elif results['compliance_rate'] >= 80:
            print("⚠️  GOOD COMPLIANCE - Some parental terms detected, minor improvements needed")
        elif results['compliance_rate'] >= 70:
            print("⚠️  ACCEPTABLE COMPLIANCE - Several parental terms detected, improvements needed")
        else:
            print("❌ POOR COMPLIANCE - Many parental terms detected, significant improvements required")
        
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"Parental terms detection failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())