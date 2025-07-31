#!/usr/bin/env python3
"""
TTS Story Narration Fixes Validation Test
Focus on 3 critical issues:
1. TTS Threshold Fix Validation (1500 char chunking)
2. Story Narration Endpoint (POST /api/stories/narrate)
3. text_to_speech_with_prosody Method
"""

import asyncio
import requests
import json
import time
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from environment
BACKEND_URL = "https://9c87ad27-55c0-4609-a47c-ef5b9de00cdd.preview.emergentagent.com/api"

class TTSFixesValidator:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        
    def log_test_result(self, test_name: str, success: bool, details: str):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: {test_name} - {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    async def test_1_tts_chunked_threshold_validation(self):
        """Test 1: Validate text_to_speech_chunked method with 1500+ character texts"""
        logger.info("🎯 TEST 1: TTS Chunked Threshold Validation (1500+ chars)")
        
        try:
            # Create a long story text over 1500 characters
            long_story = """Once upon a time, in a magical forest filled with towering oak trees and sparkling streams, there lived a brave little mouse named Oliver. Oliver was not like other mice - he had a heart full of courage and a spirit of adventure that made him special among all the woodland creatures. Every morning, Oliver would wake up in his cozy burrow beneath the roots of the great oak tree and dream of exploring the vast world beyond his home. One sunny day, Oliver decided it was time for his greatest adventure yet. He packed his tiny backpack with crumbs of cheese, a few berries, and his lucky acorn, then set off into the deep forest. As he walked along the winding path, he met many friendly animals who warned him about the dangers ahead. There was a wise old owl who told him about the dark cave where a sleeping dragon lived, and a family of rabbits who shared stories of the enchanted meadow where flowers sang beautiful songs. But Oliver was determined to see these wonders for himself. His journey took him through thorny bushes, across babbling brooks, and up steep hills covered in morning dew. Along the way, he helped a lost butterfly find her way home and shared his food with a hungry squirrel. When Oliver finally reached the dragon's cave, he discovered that the fearsome beast was actually just lonely and needed a friend. They became the best of companions, and Oliver learned that sometimes the most frightening things turn out to be the most wonderful. From that day forward, Oliver and the dragon would meet every week to share stories and adventures, proving that friendship can bloom in the most unexpected places."""
            
            logger.info(f"Testing with {len(long_story)} character story (should trigger chunking)")
            
            # Test the TTS endpoint with long text
            response = requests.post(
                f"{self.backend_url}/voice/tts",
                json={
                    "text": long_story,
                    "personality": "story_narrator"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success" and result.get("audio_base64"):
                    audio_size = len(result["audio_base64"])
                    self.log_test_result(
                        "TTS Chunked Processing (1500+ chars)",
                        True,
                        f"Successfully processed {len(long_story)} chars, generated {audio_size} chars of audio"
                    )
                    return True
                else:
                    self.log_test_result(
                        "TTS Chunked Processing (1500+ chars)",
                        False,
                        f"No audio generated: {result}"
                    )
                    return False
            else:
                self.log_test_result(
                    "TTS Chunked Processing (1500+ chars)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "TTS Chunked Processing (1500+ chars)",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    async def test_2_story_narration_endpoint(self):
        """Test 2: Story Narration Endpoint - POST /api/stories/narrate"""
        logger.info("🎯 TEST 2: Story Narration Endpoint Validation")
        
        try:
            # First, get available stories
            stories_response = requests.get(f"{self.backend_url}/content/stories", timeout=10)
            
            if stories_response.status_code != 200:
                self.log_test_result(
                    "Story Narration - Get Stories",
                    False,
                    f"Failed to get stories: HTTP {stories_response.status_code}"
                )
                return False
            
            stories_data = stories_response.json()
            stories = stories_data.get("stories", [])
            
            if not stories:
                self.log_test_result(
                    "Story Narration - Get Stories",
                    False,
                    "No stories available for testing"
                )
                return False
            
            # Test narration with first available story
            story = stories[0]
            story_id = story["id"]
            
            logger.info(f"Testing story narration with story: {story['title']} (ID: {story_id})")
            
            # Test the story narration endpoint
            narration_response = requests.post(
                f"{self.backend_url}/content/stories/{story_id}/narrate",
                data={"user_id": "test_user_tts"},
                timeout=30
            )
            
            if narration_response.status_code == 200:
                result = narration_response.json()
                
                # Check if both response_text and response_audio are present
                has_text = bool(result.get("response_text"))
                has_audio = bool(result.get("response_audio"))
                
                if has_text and has_audio:
                    text_length = len(result["response_text"])
                    audio_length = len(result["response_audio"])
                    self.log_test_result(
                        "Story Narration Endpoint",
                        True,
                        f"Success: response_text ({text_length} chars) and response_audio ({audio_length} chars) both present"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Story Narration Endpoint",
                        False,
                        f"Missing data - response_text: {has_text}, response_audio: {has_audio}. Result: {result}"
                    )
                    return False
            else:
                self.log_test_result(
                    "Story Narration Endpoint",
                    False,
                    f"HTTP {narration_response.status_code}: {narration_response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Story Narration Endpoint",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    async def test_3_text_to_speech_with_prosody(self):
        """Test 3: text_to_speech_with_prosody Method Validation"""
        logger.info("🎯 TEST 3: text_to_speech_with_prosody Method Validation")
        
        try:
            # Test with a story request that should use prosody
            story_request = "Tell me a story about a brave little mouse"
            
            # Use the text conversation endpoint which should utilize prosody
            response = requests.post(
                f"{self.backend_url}/conversations/text",
                json={
                    "session_id": "test_session_prosody",
                    "user_id": "test_user_prosody",
                    "message": story_request
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if response includes audio (which would use prosody for stories)
                has_audio = bool(result.get("response_audio"))
                has_text = bool(result.get("response_text"))
                content_type = result.get("content_type", "")
                
                if has_text and has_audio:
                    text_length = len(result["response_text"])
                    audio_length = len(result["response_audio"])
                    self.log_test_result(
                        "text_to_speech_with_prosody Method",
                        True,
                        f"Success: Generated story with prosody - text ({text_length} chars), audio ({audio_length} chars), type: {content_type}"
                    )
                    return True
                elif has_text and not has_audio:
                    self.log_test_result(
                        "text_to_speech_with_prosody Method",
                        False,
                        f"Story generated but no audio (prosody method may not be working): {result.get('response_text', '')[:100]}..."
                    )
                    return False
                else:
                    self.log_test_result(
                        "text_to_speech_with_prosody Method",
                        False,
                        f"No story generated: {result}"
                    )
                    return False
            else:
                self.log_test_result(
                    "text_to_speech_with_prosody Method",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "text_to_speech_with_prosody Method",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    async def test_4_voice_personalities_endpoint(self):
        """Test 4: Voice Personalities Endpoint (mentioned as fixed)"""
        logger.info("🎯 TEST 4: Voice Personalities Endpoint Validation")
        
        try:
            response = requests.get(f"{self.backend_url}/voice/personalities", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                voices = result.get("voices", [])
                
                if len(voices) >= 3:
                    voice_names = [v.get("name", "Unknown") for v in voices]
                    self.log_test_result(
                        "Voice Personalities Endpoint",
                        True,
                        f"Success: {len(voices)} personalities available: {', '.join(voice_names)}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Voice Personalities Endpoint",
                        False,
                        f"Insufficient personalities: {result}"
                    )
                    return False
            else:
                self.log_test_result(
                    "Voice Personalities Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Voice Personalities Endpoint",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    async def run_all_tests(self):
        """Run all TTS validation tests"""
        logger.info("🚀 Starting TTS Fixes Validation Tests")
        logger.info("=" * 60)
        
        # Run all tests
        test_1_result = await self.test_1_tts_chunked_threshold_validation()
        test_2_result = await self.test_2_story_narration_endpoint()
        test_3_result = await self.test_3_text_to_speech_with_prosody()
        test_4_result = await self.test_4_voice_personalities_endpoint()
        
        # Calculate results
        total_tests = 4
        passed_tests = sum([test_1_result, test_2_result, test_3_result, test_4_result])
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info("=" * 60)
        logger.info("🎯 TTS FIXES VALIDATION SUMMARY")
        logger.info("=" * 60)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            logger.info(f"{status} {result['test']}: {result['details']}")
        
        logger.info("=" * 60)
        logger.info(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            logger.info("🎉 TTS FIXES VALIDATION: MOSTLY SUCCESSFUL")
        elif success_rate >= 50:
            logger.info("⚠️ TTS FIXES VALIDATION: PARTIAL SUCCESS - NEEDS ATTENTION")
        else:
            logger.info("🚨 TTS FIXES VALIDATION: CRITICAL FAILURES - URGENT FIXES NEEDED")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "results": self.test_results
        }

async def main():
    """Main test execution"""
    validator = TTSFixesValidator()
    results = await validator.run_all_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())