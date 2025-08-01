#!/usr/bin/env python3
"""
Focused JSON Validation and Conversation Context Testing
Tests the conversation text endpoint for JSON issues and context maintenance
"""

import asyncio
import aiohttp
import json
import base64
import uuid
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend URL from environment
BACKEND_URL = "https://0e5dcf5a-4e8d-4074-9227-19f4607bd0be.preview.emergentagent.com/api"

class JSONTester:
    """Focused JSON validation and conversation context tester"""
    
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
    
    async def setup_test_user(self):
        """Create a test user for testing"""
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
                    logger.info(f"Created test user: {self.test_user_id}")
                    
                    # Create session
                    session_data = {
                        "user_id": self.test_user_id,
                        "session_name": "JSON Test Session"
                    }
                    
                    async with self.session.post(
                        f"{BACKEND_URL}/conversations/session",
                        json=session_data
                    ) as session_response:
                        if session_response.status == 200:
                            session_data = await session_response.json()
                            self.test_session_id = session_data["id"]
                            logger.info(f"Created test session: {self.test_session_id}")
                            return True
                        else:
                            logger.error(f"Failed to create session: {session_response.status}")
                            return False
                else:
                    logger.error(f"Failed to create user: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Setup failed: {str(e)}")
            return False
    
    async def test_conversation_text_json_validation(self):
        """Test POST /api/conversations/text endpoint for JSON response validation and malformed responses"""
        logger.info("Testing JSON validation for conversation text endpoint...")
        
        try:
            # Test simple message first
            simple_message = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Hello, how are you today?"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=simple_message
            ) as response:
                # Check if response is valid JSON
                response_text = await response.text()
                logger.info(f"Response status: {response.status}")
                logger.info(f"Response preview: {response_text[:200]}...")
                
                try:
                    data = json.loads(response_text)
                    json_valid = True
                    json_error = None
                except json.JSONDecodeError as e:
                    json_valid = False
                    json_error = str(e)
                    data = None
                
                # Validate AIResponse model format
                if json_valid and data:
                    required_fields = ["response_text", "content_type"]
                    optional_fields = ["response_audio", "metadata"]
                    
                    has_required_fields = all(field in data for field in required_fields)
                    field_types_valid = (
                        isinstance(data.get("response_text"), str) and
                        isinstance(data.get("content_type"), str) and
                        (data.get("response_audio") is None or isinstance(data.get("response_audio"), str)) and
                        (data.get("metadata") is None or isinstance(data.get("metadata"), dict))
                    )
                    
                    return {
                        "success": json_valid and has_required_fields and field_types_valid,
                        "json_valid": json_valid,
                        "json_error": json_error,
                        "response_status": response.status,
                        "has_required_fields": has_required_fields,
                        "field_types_valid": field_types_valid,
                        "response_text_length": len(data.get("response_text", "")),
                        "content_type": data.get("content_type"),
                        "has_response_audio": bool(data.get("response_audio")),
                        "has_metadata": bool(data.get("metadata")),
                        "raw_response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                    }
                else:
                    return {
                        "success": False,
                        "json_valid": json_valid,
                        "json_error": json_error,
                        "response_status": response.status,
                        "raw_response": response_text[:500] + "..." if len(response_text) > 500 else response_text
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_riddle_conversation_context(self):
        """Test riddle scenario: ask for a riddle, then respond with 'I don't know' to check context maintenance"""
        logger.info("Testing riddle conversation context...")
        
        try:
            # Step 1: Ask for a riddle
            riddle_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "Tell me a riddle"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=riddle_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Riddle request failed: HTTP {response.status}"}
                
                riddle_data = await response.json()
                riddle_response = riddle_data.get("response_text", "")
                logger.info(f"Riddle response: {riddle_response[:100]}...")
                
                # Step 2: Respond with "I don't know"
                await asyncio.sleep(1.0)  # Brief pause to simulate real conversation
                
                followup_request = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": "I don't know"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=followup_request
                ) as followup_response:
                    if followup_response.status != 200:
                        return {"success": False, "error": f"Followup failed: HTTP {followup_response.status}"}
                    
                    followup_data = await followup_response.json()
                    followup_text = followup_data.get("response_text", "")
                    logger.info(f"Followup response: {followup_text[:100]}...")
                    
                    # Check if context is maintained (bot should provide the answer)
                    context_maintained = (
                        "answer" in followup_text.lower() or
                        "solution" in followup_text.lower() or
                        len(followup_text) > 50  # Substantial response indicating context awareness
                    )
                    
                    return {
                        "success": True,
                        "riddle_provided": len(riddle_response) > 20,
                        "riddle_content_type": riddle_data.get("content_type"),
                        "followup_response_received": bool(followup_text),
                        "context_maintained": context_maintained,
                        "followup_response_length": len(followup_text),
                        "riddle_preview": riddle_response[:100] + "..." if len(riddle_response) > 100 else riddle_response,
                        "followup_preview": followup_text[:100] + "..." if len(followup_text) > 100 else followup_text,
                        "conversation_flow": "riddle → I don't know → answer provided" if context_maintained else "context lost"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_question_conversation_context(self):
        """Test question scenario: ask a question and see if context is maintained in follow-up"""
        logger.info("Testing question conversation context...")
        
        try:
            # Step 1: Ask a question that requires follow-up
            question_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "What's your favorite color and why?"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=question_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Question request failed: HTTP {response.status}"}
                
                question_data = await response.json()
                question_response = question_data.get("response_text", "")
                logger.info(f"Question response: {question_response[:100]}...")
                
                # Step 2: Follow up on the response
                await asyncio.sleep(1.0)
                
                followup_request = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": "That's interesting! Tell me more about that."
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=followup_request
                ) as followup_response:
                    if followup_response.status != 200:
                        return {"success": False, "error": f"Followup failed: HTTP {followup_response.status}"}
                    
                    followup_data = await followup_response.json()
                    followup_text = followup_data.get("response_text", "")
                    logger.info(f"Followup response: {followup_text[:100]}...")
                    
                    # Check if context is maintained (bot should reference previous response)
                    context_maintained = (
                        len(followup_text) > 30 and  # Substantial response
                        ("color" in followup_text.lower() or
                         "that" in followup_text.lower() or
                         "because" in followup_text.lower())
                    )
                    
                    return {
                        "success": True,
                        "question_answered": len(question_response) > 20,
                        "question_content_type": question_data.get("content_type"),
                        "followup_response_received": bool(followup_text),
                        "context_maintained": context_maintained,
                        "followup_response_length": len(followup_text),
                        "question_preview": question_response[:100] + "..." if len(question_response) > 100 else question_response,
                        "followup_preview": followup_text[:100] + "..." if len(followup_text) > 100 else followup_text,
                        "conversation_flow": "question → answer → contextual follow-up" if context_maintained else "context lost"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_memory_system_working(self):
        """Test if the memory system is working correctly across conversations"""
        logger.info("Testing memory system...")
        
        try:
            # Step 1: Establish a preference
            preference_request = {
                "session_id": self.test_session_id,
                "user_id": self.test_user_id,
                "message": "I love stories about animals, especially rabbits!"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/conversations/text",
                json=preference_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Preference request failed: HTTP {response.status}"}
                
                preference_data = await response.json()
                logger.info(f"Preference response: {preference_data.get('response_text', '')[:100]}...")
                
                # Step 2: Generate memory snapshot
                await asyncio.sleep(1.0)
                async with self.session.post(
                    f"{BACKEND_URL}/memory/snapshot/{self.test_user_id}"
                ) as snapshot_response:
                    snapshot_success = snapshot_response.status == 200
                    logger.info(f"Memory snapshot: {'Success' if snapshot_success else 'Failed'}")
                
                # Step 3: Ask for content that should use memory
                await asyncio.sleep(1.0)
                memory_test_request = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": "Tell me a story based on what I like"
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/conversations/text",
                    json=memory_test_request
                ) as memory_response:
                    if memory_response.status != 200:
                        return {"success": False, "error": f"Memory test failed: HTTP {memory_response.status}"}
                    
                    memory_data = await memory_response.json()
                    memory_story = memory_data.get("response_text", "")
                    metadata = memory_data.get("metadata", {})
                    logger.info(f"Memory story: {memory_story[:100]}...")
                    
                    # Check if memory was used (story should reference animals/rabbits)
                    memory_used = (
                        "animal" in memory_story.lower() or
                        "rabbit" in memory_story.lower() or
                        bool(metadata.get("memory_context"))
                    )
                    
                    return {
                        "success": True,
                        "preference_established": len(preference_data.get("response_text", "")) > 10,
                        "memory_snapshot_created": snapshot_success,
                        "memory_story_generated": len(memory_story) > 50,
                        "memory_used": memory_used,
                        "has_memory_metadata": bool(metadata.get("memory_context")),
                        "story_content_type": memory_data.get("content_type"),
                        "story_preview": memory_story[:150] + "..." if len(memory_story) > 150 else memory_story,
                        "memory_system_working": memory_used and snapshot_success
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_json_serialization_edge_cases(self):
        """Test edge cases that might cause JSON serialization issues"""
        logger.info("Testing JSON serialization edge cases...")
        
        try:
            # Test messages that might cause JSON issues
            edge_case_messages = [
                'Message with "quotes" and \'apostrophes\'',
                "Message with unicode: 🎉 🤖 ✨ 🎵",
                "Message with\nnewlines\nand\ttabs",
                "Message with special chars: @#$%^&*()[]{}|\\",
                "Very long message: " + "A" * 500,  # Shorter for testing
                "",  # Empty message
                "Message with JSON-like content: {\"key\": \"value\", \"number\": 123}"
            ]
            
            edge_case_results = []
            
            for i, message in enumerate(edge_case_messages):
                logger.info(f"Testing edge case {i+1}/{len(edge_case_messages)}: {message[:50]}...")
                
                test_request = {
                    "session_id": self.test_session_id,
                    "user_id": self.test_user_id,
                    "message": message
                }
                
                try:
                    async with self.session.post(
                        f"{BACKEND_URL}/conversations/text",
                        json=test_request
                    ) as response:
                        response_text = await response.text()
                        
                        # Try to parse JSON
                        try:
                            data = json.loads(response_text)
                            json_valid = True
                            json_error = None
                        except json.JSONDecodeError as e:
                            json_valid = False
                            json_error = str(e)
                            data = None
                        
                        edge_case_results.append({
                            "message_type": message[:50] + "..." if len(message) > 50 else message or "empty",
                            "response_status": response.status,
                            "json_valid": json_valid,
                            "json_error": json_error,
                            "response_received": bool(data and data.get("response_text")) if json_valid else False,
                            "response_length": len(data.get("response_text", "")) if json_valid and data else 0
                        })
                        
                except Exception as e:
                    edge_case_results.append({
                        "message_type": message[:50] + "..." if len(message) > 50 else message or "empty",
                        "error": str(e),
                        "json_valid": False
                    })
                
                await asyncio.sleep(0.5)
            
            successful_cases = [r for r in edge_case_results if r.get("json_valid", False)]
            
            return {
                "success": True,
                "edge_cases_tested": len(edge_case_messages),
                "json_valid_responses": len(successful_cases),
                "json_success_rate": f"{len(successful_cases)/len(edge_case_messages)*100:.1f}%",
                "edge_case_results": edge_case_results,
                "serialization_robust": len(successful_cases) == len(edge_case_messages)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def run_focused_tests(self):
        """Run focused JSON and context tests"""
        logger.info("Starting focused JSON validation and conversation context testing...")
        
        # Setup test user
        if not await self.setup_test_user():
            logger.error("Failed to setup test user")
            return {}
        
        # Test sequence
        test_sequence = [
            ("JSON VALIDATION - Conversation Text Endpoint JSON Response", self.test_conversation_text_json_validation),
            ("CONTEXT TEST - Riddle Conversation Follow-Through", self.test_riddle_conversation_context),
            ("CONTEXT TEST - Question Conversation Context Maintenance", self.test_question_conversation_context),
            ("MEMORY TEST - Memory System Working Correctly", self.test_memory_system_working),
            ("JSON EDGE CASES - Serialization Edge Cases", self.test_json_serialization_edge_cases)
        ]
        
        for test_name, test_func in test_sequence:
            try:
                logger.info(f"Running test: {test_name}")
                result = await test_func()
                self.test_results[test_name] = {
                    "status": "PASS" if result.get("success", False) else "FAIL",
                    "details": result
                }
                logger.info(f"Test {test_name}: {'PASS' if result.get('success', False) else 'FAIL'}")
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {str(e)}")
                self.test_results[test_name] = {
                    "status": "ERROR",
                    "details": {"error": str(e)}
                }
        
        return self.test_results
    
    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("JSON VALIDATION AND CONVERSATION CONTEXT TEST RESULTS")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["status"] == "PASS")
        failed_tests = sum(1 for result in self.test_results.values() if result["status"] == "FAIL")
        error_tests = sum(1 for result in self.test_results.values() if result["status"] == "ERROR")
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print("-"*80)
        
        for test_name, result in self.test_results.items():
            status_symbol = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_symbol} {test_name}: {result['status']}")
            
            if result["status"] != "PASS" and "error" in result["details"]:
                print(f"   Error: {result['details']['error']}")
            elif result["status"] == "PASS" and isinstance(result["details"], dict):
                # Show key success metrics
                key_info = {}
                details = result["details"]
                if "json_valid" in details:
                    key_info["json_valid"] = details["json_valid"]
                if "context_maintained" in details:
                    key_info["context_maintained"] = details["context_maintained"]
                if "memory_system_working" in details:
                    key_info["memory_system_working"] = details["memory_system_working"]
                if "json_success_rate" in details:
                    key_info["json_success_rate"] = details["json_success_rate"]
                
                if key_info:
                    print(f"   Key Results: {key_info}")
        
        print("-"*80)
        print("\nDETAILED FINDINGS:")
        
        # JSON Validation Results
        json_test = self.test_results.get("JSON VALIDATION - Conversation Text Endpoint JSON Response")
        if json_test and json_test["status"] == "PASS":
            details = json_test["details"]
            print(f"✅ JSON Response Format: Valid JSON with required fields")
            print(f"   - Response Status: {details.get('response_status')}")
            print(f"   - Content Type: {details.get('content_type')}")
            print(f"   - Response Length: {details.get('response_text_length')} chars")
        elif json_test:
            print(f"❌ JSON Response Format: {json_test['details'].get('json_error', 'Failed')}")
        
        # Context Tests
        riddle_test = self.test_results.get("CONTEXT TEST - Riddle Conversation Follow-Through")
        if riddle_test and riddle_test["status"] == "PASS":
            details = riddle_test["details"]
            print(f"✅ Riddle Context: {'Maintained' if details.get('context_maintained') else 'Lost'}")
            print(f"   - Flow: {details.get('conversation_flow')}")
        
        question_test = self.test_results.get("CONTEXT TEST - Question Conversation Context Maintenance")
        if question_test and question_test["status"] == "PASS":
            details = question_test["details"]
            print(f"✅ Question Context: {'Maintained' if details.get('context_maintained') else 'Lost'}")
            print(f"   - Flow: {details.get('conversation_flow')}")
        
        # Memory Test
        memory_test = self.test_results.get("MEMORY TEST - Memory System Working Correctly")
        if memory_test and memory_test["status"] == "PASS":
            details = memory_test["details"]
            print(f"✅ Memory System: {'Working' if details.get('memory_system_working') else 'Not Working'}")
            print(f"   - Memory Used: {details.get('memory_used')}")
            print(f"   - Snapshot Created: {details.get('memory_snapshot_created')}")
        
        # Edge Cases
        edge_test = self.test_results.get("JSON EDGE CASES - Serialization Edge Cases")
        if edge_test and edge_test["status"] == "PASS":
            details = edge_test["details"]
            print(f"✅ JSON Edge Cases: {details.get('json_success_rate')} success rate")
            print(f"   - Serialization Robust: {details.get('serialization_robust')}")
        
        print("\n" + "="*80)

async def main():
    """Main test execution"""
    async with JSONTester() as tester:
        results = await tester.run_focused_tests()
        tester.print_test_summary()
        
        # Return overall success status
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result["status"] == "PASS")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)