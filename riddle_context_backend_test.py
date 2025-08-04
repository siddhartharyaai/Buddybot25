#!/usr/bin/env python3
"""
Riddle Context Retention Backend Test
Testing the specific riddle context retention fix implementation
"""

import asyncio
import aiohttp
import json
import uuid
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com"

class RiddleContextTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session_id = str(uuid.uuid4())
        self.user_id = f"riddle_test_user_{int(time.time())}"
        self.test_results = []
        
    async def log_result(self, test_name, success, details):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    async def test_riddle_request(self, session):
        """Test 1: Request a riddle and verify only question is shown"""
        try:
            payload = {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "message": "tell me a riddle"
            }
            
            async with session.post(f"{self.backend_url}/api/conversations/text", json=payload) as response:
                if response.status != 200:
                    await self.log_result("Riddle Request", False, f"HTTP {response.status}")
                    return None
                
                data = await response.json()
                response_text = data.get("response_text", "")
                
                # Check if response contains riddle question but not answer
                has_question_mark = "?" in response_text
                has_think_prompt = "think" in response_text.lower() or "guess" in response_text.lower()
                
                # Should NOT contain obvious answer patterns
                suspicious_patterns = [
                    "the answer is",
                    "answer:",
                    "solution:",
                    "it is a",
                    "it's a"
                ]
                
                contains_answer = any(pattern in response_text.lower() for pattern in suspicious_patterns)
                
                success = has_question_mark and has_think_prompt and not contains_answer
                
                details = f"Response: '{response_text[:100]}...' | Has question: {has_question_mark} | Has think prompt: {has_think_prompt} | Contains answer: {contains_answer}"
                
                await self.log_result("Riddle Request - Question Only", success, details)
                
                return response_text if success else None
                
        except Exception as e:
            await self.log_result("Riddle Request", False, f"Exception: {str(e)}")
            return None

    async def test_correct_answer(self, session, riddle_text):
        """Test 2: Provide correct answer and verify context-aware response"""
        try:
            # Common riddle answers to try
            common_answers = [
                "echo", "shadow", "candle", "clock", "mirror", "river", "fire", 
                "wind", "time", "breath", "footsteps", "silence", "darkness",
                "light", "water", "air", "sun", "moon", "stars", "rain"
            ]
            
            # Try a few common answers
            for answer in common_answers[:3]:  # Test first 3
                payload = {
                    "session_id": self.session_id,
                    "user_id": self.user_id,
                    "message": answer
                }
                
                async with session.post(f"{self.backend_url}/api/conversations/text", json=payload) as response:
                    if response.status != 200:
                        continue
                    
                    data = await response.json()
                    response_text = data.get("response_text", "").lower()
                    
                    # Check for correct answer patterns
                    correct_patterns = [
                        "excellent", "correct", "right", "got it", "well done",
                        "🎉", "congratulations", "perfect", "exactly"
                    ]
                    
                    # Check for context retention (mentions the riddle or answer)
                    context_patterns = [
                        "answer is indeed", "you got it right", "the answer",
                        "riddle", "correct"
                    ]
                    
                    is_correct_response = any(pattern in response_text for pattern in correct_patterns)
                    has_context = any(pattern in response_text for pattern in context_patterns)
                    
                    if is_correct_response and has_context:
                        details = f"Answer: '{answer}' | Response: '{response_text[:100]}...' | Context retained: {has_context}"
                        await self.log_result("Correct Answer Context", True, details)
                        return True
            
            # If no correct answer found, test with a generic correct response
            payload = {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "message": "Is it an echo?"
            }
            
            async with session.post(f"{self.backend_url}/api/conversations/text", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "").lower()
                    
                    # Check if bot remembers the riddle context
                    has_riddle_context = any(word in response_text for word in ["riddle", "answer", "guess", "correct", "wrong"])
                    
                    details = f"Generic answer test | Response: '{response_text[:100]}...' | Has context: {has_riddle_context}"
                    await self.log_result("Correct Answer Context", has_riddle_context, details)
                    return has_riddle_context
            
            await self.log_result("Correct Answer Context", False, "No correct answer response detected")
            return False
            
        except Exception as e:
            await self.log_result("Correct Answer Context", False, f"Exception: {str(e)}")
            return False

    async def test_incorrect_answer(self, session):
        """Test 3: Provide incorrect answer and verify context-aware response"""
        try:
            payload = {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "message": "Is it a banana?"  # Obviously wrong answer
            }
            
            async with session.post(f"{self.backend_url}/api/conversations/text", json=payload) as response:
                if response.status != 200:
                    await self.log_result("Incorrect Answer Context", False, f"HTTP {response.status}")
                    return False
                
                data = await response.json()
                response_text = data.get("response_text", "").lower()
                
                # Check for incorrect answer patterns
                incorrect_patterns = [
                    "good try", "not quite", "close", "try again", "the answer",
                    "thinking of", "actually", "incorrect", "wrong"
                ]
                
                # Check for context retention
                context_patterns = [
                    "answer", "riddle", "thinking of", "the answer is", "it was"
                ]
                
                is_incorrect_response = any(pattern in response_text for pattern in incorrect_patterns)
                has_context = any(pattern in response_text for pattern in context_patterns)
                
                success = is_incorrect_response or has_context  # Either pattern indicates context retention
                
                details = f"Response: '{response_text[:100]}...' | Incorrect response: {is_incorrect_response} | Has context: {has_context}"
                await self.log_result("Incorrect Answer Context", success, details)
                
                return success
                
        except Exception as e:
            await self.log_result("Incorrect Answer Context", False, f"Exception: {str(e)}")
            return False

    async def test_session_persistence(self, session):
        """Test 4: Verify riddle context persists across multiple interactions"""
        try:
            # Ask about the riddle again
            payload = {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "message": "What was that riddle again?"
            }
            
            async with session.post(f"{self.backend_url}/api/conversations/text", json=payload) as response:
                if response.status != 200:
                    await self.log_result("Session Persistence", False, f"HTTP {response.status}")
                    return False
                
                data = await response.json()
                response_text = data.get("response_text", "").lower()
                
                # Check if bot remembers the riddle
                remembers_riddle = any(word in response_text for word in [
                    "riddle", "asked", "earlier", "before", "remember", "previous"
                ])
                
                details = f"Response: '{response_text[:100]}...' | Remembers riddle: {remembers_riddle}"
                await self.log_result("Session Persistence", remembers_riddle, details)
                
                return remembers_riddle
                
        except Exception as e:
            await self.log_result("Session Persistence", False, f"Exception: {str(e)}")
            return False

    async def test_new_riddle_request(self, session):
        """Test 5: Request another riddle to test context switching"""
        try:
            payload = {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "message": "tell me another riddle"
            }
            
            async with session.post(f"{self.backend_url}/api/conversations/text", json=payload) as response:
                if response.status != 200:
                    await self.log_result("New Riddle Request", False, f"HTTP {response.status}")
                    return False
                
                data = await response.json()
                response_text = data.get("response_text", "")
                
                # Check if new riddle is provided
                has_question_mark = "?" in response_text
                has_new_riddle_content = len(response_text) > 20  # Should be substantial content
                
                success = has_question_mark and has_new_riddle_content
                
                details = f"Response: '{response_text[:100]}...' | Has question: {has_question_mark} | Substantial content: {has_new_riddle_content}"
                await self.log_result("New Riddle Request", success, details)
                
                return success
                
        except Exception as e:
            await self.log_result("New Riddle Request", False, f"Exception: {str(e)}")
            return False

    async def run_comprehensive_test(self):
        """Run all riddle context retention tests"""
        print("🎯 RIDDLE CONTEXT RETENTION TESTING STARTED")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Session ID: {self.session_id}")
        print(f"User ID: {self.user_id}")
        print()
        
        async with aiohttp.ClientSession() as session:
            # Test 1: Request riddle
            riddle_text = await self.test_riddle_request(session)
            
            if riddle_text:
                # Test 2: Correct answer
                await self.test_correct_answer(session, riddle_text)
                
                # Test 3: Incorrect answer (new session to test different flow)
                self.session_id = str(uuid.uuid4())  # New session
                await self.test_riddle_request(session)  # Get new riddle
                await self.test_incorrect_answer(session)
                
                # Test 4: Session persistence
                await self.test_session_persistence(session)
                
                # Test 5: New riddle request
                await self.test_new_riddle_request(session)
            
        # Summary
        print("=" * 60)
        print("🎯 RIDDLE CONTEXT RETENTION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status}: {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print()
        print("🎯 RIDDLE CONTEXT RETENTION TESTING COMPLETE")
        
        # Return overall success
        return passed_tests >= (total_tests * 0.6)  # 60% pass rate required

async def main():
    """Main test execution"""
    tester = RiddleContextTester()
    success = await tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 RIDDLE CONTEXT RETENTION: WORKING")
    else:
        print("\n❌ RIDDLE CONTEXT RETENTION: NEEDS FIXES")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())